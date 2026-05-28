export default function BookCover({ title }: { title: string }) {
  // 根据书名生成不同的渐变色
  const hue = title.split('').reduce((a, c) => a + c.charCodeAt(0), 0) % 360

  return (
    <div
      className="w-full aspect-[3/4] rounded-md flex items-center justify-center shadow-sm"
      style={{
        background: `linear-gradient(135deg, hsl(${hue}, 60%, 75%), hsl(${hue + 30}, 55%, 55%))`,
      }}
    >
      <span className="text-white/90 text-sm font-medium text-center px-2 leading-tight">
        {title}
      </span>
    </div>
  )
}
