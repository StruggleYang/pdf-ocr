; Inno Setup 安装程序脚本
; 保险单识别系统 - Windows 安装包

#define AppName "保险单识别系统"
#define AppVersion "1.0.0"
#define AppPublisher "StruggleYang"
#define AppExeName "保险单识别系统.exe"

[Setup]
; 安装程序基本信息
AppId={{A1B2C3D4-E5F6-4A5B-8C7D-9E0F1A2B3C4D}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename={#AppName}-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; 管理员权限安装（可选，改为 no 则普通用户权限）
PrivilegesRequired=admin
; 卸载信息
UninstallDisplayIcon={app}\{#AppExeName}
UninstallFilesDir={app}\uninstall

; 安装程序图标（可选）
; SetupIconFile=source\appicon1.ico

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"; Flags: unchecked

[Files]
; 主程序
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; 数据文件（如果需要）
Source: "source\*"; DestDir: "{app}\source"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 开始菜单快捷方式
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\卸载 {#AppName}"; Filename: "{uninstallexe}"
; 桌面快捷方式
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; 安装完成后运行程序
Filename: "{app}\{#AppExeName}"; Description: "启动 {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时删除用户数据（可选）
; Type: filesandordirs; Name: "{userappdata}\{#AppName}"
