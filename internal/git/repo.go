package git

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"
)

// Repo 管理单部小说的 Git 仓库，提供文件读写和版本控制。
type Repo struct {
	dir    string
	gitBin string
}

// CommitInfo 是 git log 的单条记录。
type CommitInfo struct {
	Hash    string
	Message string
	Time    time.Time
}

// New 打开已有仓库，不存在则 git init + 首次空 commit。
// gitBin 为 git 可执行文件路径，为空时从 PATH 查找。
func New(novelDir, gitBin string) (*Repo, error) {
	if gitBin == "" {
		gitBin = "git"
	}

	r := &Repo{dir: novelDir, gitBin: gitBin}

	if _, err := os.Stat(filepath.Join(novelDir, ".git")); err != nil {
		if !os.IsNotExist(err) {
			return nil, fmt.Errorf("git: stat .git: %w", err)
		}
		if err := os.MkdirAll(novelDir, 0755); err != nil {
			return nil, fmt.Errorf("git: create novel dir: %w", err)
		}
		if _, stderr, err := r.runInDir("init", novelDir); err != nil {
			return nil, fmt.Errorf("git: init: %s: %w", stderr, err)
		}
		gitkeep := filepath.Join(novelDir, "chapters", ".gitkeep")
		if err := os.MkdirAll(filepath.Dir(gitkeep), 0755); err != nil {
			return nil, fmt.Errorf("git: create chapters dir: %w", err)
		}
		if err := os.WriteFile(gitkeep, nil, 0644); err != nil {
			return nil, fmt.Errorf("git: write .gitkeep: %w", err)
		}
		if _, _, err := r.runInDir("add", "chapters/.gitkeep"); err != nil {
			return nil, fmt.Errorf("git: stage .gitkeep: %w", err)
		}
		if _, _, err := r.runInDir("commit", "-m", "initial commit"); err != nil {
			return nil, fmt.Errorf("git: initial commit: %w", err)
		}
	}

	return r, nil
}

// ── 文件路径 ──────────────────────────────────────────────

func (r *Repo) ChapterPath(num int) string {
	return fmt.Sprintf("chapters/%03d.md", num)
}

func (r *Repo) GoinkPath() string {
	return "goink.md"
}

// ── 文件读写 ──────────────────────────────────────────────
// 文件不存在的时候返回错误，调用方可以针对文件不存在返回空内容，底层工具保持通用，不直接返回空

func (r *Repo) ReadChapter(num int) (string, error) {
	return r.readFile(r.ChapterPath(num))
}

func (r *Repo) WriteChapter(num int, content string) error {
	return r.writeFile(r.ChapterPath(num), content)
}

func (r *Repo) ReadGoink() (string, error) {
	return r.readFile(r.GoinkPath())
}

func (r *Repo) WriteGoink(content string) error {
	return r.writeFile(r.GoinkPath(), content)
}

func (r *Repo) readFile(relPath string) (string, error) {
	data, err := os.ReadFile(filepath.Join(r.dir, relPath))
	if err != nil {
		if os.IsNotExist(err) {
			return "", fmt.Errorf("%w: %s", os.ErrNotExist, relPath)
		}
		return "", fmt.Errorf("git: read %s: %w", relPath, err)
	}
	return string(data), nil
}

func (r *Repo) writeFile(relPath, content string) error {
	fullPath := filepath.Join(r.dir, relPath)
	if err := os.MkdirAll(filepath.Dir(fullPath), 0755); err != nil {
		return fmt.Errorf("git: mkdir for %s: %w", relPath, err)
	}
	if err := os.WriteFile(fullPath, []byte(content), 0644); err != nil {
		return fmt.Errorf("git: write %s: %w", relPath, err)
	}
	return nil
}

// ── Diff ──────────────────────────────────────────────────

// DiffContent 对比当前工作区文件与 proposed 内容，返回 unified diff。
// 文件不存在时以空内容为基准。用临时文件 + git diff --no-index 实现。
func (r *Repo) DiffContent(relPath, proposed string) (string, error) {
	fromPath := relPath
	fullPath := filepath.Join(r.dir, relPath)

	if _, err := os.Stat(fullPath); os.IsNotExist(err) {
		empty, err := os.CreateTemp("", "git-diff-empty-*")
		if err != nil {
			return "", fmt.Errorf("git: diff: create empty temp: %w", err)
		}
		empty.Close()
		defer os.Remove(empty.Name())
		fromPath = empty.Name()
	}

	tmp, err := os.CreateTemp("", "git-diff-*"+filepath.Ext(relPath))
	if err != nil {
		return "", fmt.Errorf("git: diff: create temp: %w", err)
	}
	defer os.Remove(tmp.Name())

	if _, err := tmp.WriteString(proposed); err != nil {
		tmp.Close()
		return "", fmt.Errorf("git: diff: write temp: %w", err)
	}
	tmp.Close()

	stdout, stderr, err := r.runInDir("diff", "--no-index", "--", fromPath, tmp.Name())
	// git diff 有差异时 exit 1，stdout 有内容；exit >1 才是真正的错误
	if err != nil && stdout == "" {
		return "", fmt.Errorf("git: diff: %s: %w", stderr, err)
	}
	stdout = strings.ReplaceAll(stdout, filepath.ToSlash(tmp.Name()), "/"+relPath)
	if fromPath != relPath {
		stdout = strings.ReplaceAll(stdout, filepath.ToSlash(fromPath), "/dev/null")
	}
	return stdout, nil
}

// ── Git 操作 ──────────────────────────────────────────────

func (r *Repo) StageAll() error {
	_, stderr, err := r.runInDir("add", "-A")
	if err != nil {
		return fmt.Errorf("git: stage all: %s: %w", stderr, err)
	}
	return nil
}

func (r *Repo) Commit(msg string) (string, error) {
	_, stderr, err := r.runInDir("commit", "-m", msg)
	if err != nil {
		return "", fmt.Errorf("git: commit: %s: %w", stderr, err)
	}
	hash, _, err := r.runInDir("rev-parse", "HEAD")
	if err != nil {
		return "", fmt.Errorf("git: rev-parse after commit: %s: %w", stderr, err)
	}
	return strings.TrimSpace(hash), nil
}

func (r *Repo) HasUncommitted() (bool, error) {
	out, _, err := r.runInDir("status", "--porcelain")
	if err != nil {
		return false, fmt.Errorf("git: status: %w", err)
	}
	return strings.TrimSpace(out) != "", nil
}

func (r *Repo) Revert(hashes []string) error {
	// 逆序使用 --no-commit，全部成功后再统一 commit，保证原子性。
	// 某步冲突则 --abort 丢弃所有暂存的 revert。
	//未来可实现冲突处理
	for i := len(hashes) - 1; i >= 0; i-- {
		_, stderr, err := r.runInDir("revert", "--no-commit", hashes[i])
		if err != nil {
			r.runInDir("revert", "--abort")
			return fmt.Errorf("git: revert %s: %s: %w", hashes[i], stderr, err)
		}
	}
	_, stderr, err := r.runInDir("commit", "-m", "revert turns")
	if err != nil {
		return fmt.Errorf("git: commit revert: %s: %w", stderr, err)
	}
	return nil
}

func (r *Repo) Log(relPath string, n int) ([]CommitInfo, error) {
	args := []string{"log", "--format=%H%x00%s%x00%ct"}
	if n > 0 {
		args = append(args, "-n", strconv.Itoa(n))
	}
	if relPath != "" {
		args = append(args, "--", relPath)
	}

	stdout, stderr, err := r.runInDir(args...)
	if err != nil {
		return nil, fmt.Errorf("git: log: %s: %w", stderr, err)
	}
	return parseLog(stdout), nil
}

func parseLog(out string) []CommitInfo {
	if strings.TrimSpace(out) == "" {
		return nil
	}
	lines := strings.Split(strings.TrimSpace(out), "\n")
	var commits []CommitInfo
	for _, line := range lines {
		parts := strings.SplitN(line, "\x00", 3)
		if len(parts) < 3 {
			continue
		}
		ts, err := strconv.ParseInt(parts[2], 10, 64)
		if err != nil {
			continue
		}
		commits = append(commits, CommitInfo{
			Hash:    parts[0],
			Message: strings.SplitN(parts[1], "\n", 2)[0],
			Time:    time.Unix(ts, 0),
		})
	}
	sort.Slice(commits, func(i, j int) bool {
		return commits[i].Time.Before(commits[j].Time)
	})
	return commits
}

// ── CLI ───────────────────────────────────────────────────

func (r *Repo) runInDir(args ...string) (stdout, stderr string, err error) {
	return runCmd(r.gitBin, r.dir, args...)
}

func runCmd(gitBin, dir string, args ...string) (stdout, stderr string, err error) {
	cmd := exec.Command(gitBin, args...)
	cmd.Dir = dir
	var outBuf, errBuf bytes.Buffer
	cmd.Stdout = &outBuf
	cmd.Stderr = &errBuf
	err = cmd.Run()
	return outBuf.String(), errBuf.String(), err
}
