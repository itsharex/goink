#define MyAppName "Goink"
#define MyAppVersion GetEnv("VERSION")
#define MyAppExeName "goink.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Goink
DefaultDirName={code:GetDefaultDir}
DefaultGroupName={#MyAppName}
OutputDir=..\..\dist
OutputBaseFilename=goink-v{#MyAppVersion}-windows-amd64
Compression=lzma2
SolidCompression=yes
UninstallDisplayName={#MyAppName}
ArchitecturesInstallIn64BitMode=x64compatible
DirExistsWarning=no

[Files]
Source: "..\..\bin\goink.exe"; DestDir: "{app}"
Source: "..\..\runtime\*"; DestDir: "{app}\runtime"; Flags: recursesubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName}卸载 Goink"; Filename: "{uninstallexe}"

[Code]
function GetDefaultDir(Param: string): string;
begin
  if DirExists('D:\') then Result := 'D:\Goink'
  else if DirExists('E:\') then Result := 'E:\Goink'
  else Result := 'C:\Goink';
end;
