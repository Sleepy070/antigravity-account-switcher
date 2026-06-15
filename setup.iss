[Setup]
AppName=Antigravity Account Switcher
AppVersion=1.0
DefaultDirName={autopf}\Antigravity Account Switcher
DefaultGroupName=Antigravity Account Switcher
OutputDir=Output
OutputBaseFilename=AntigravityAccountSwitcher_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\AntigravityAccountSwitcher.exe
PrivilegesRequired=admin

[Files]
Source: "dist\AntigravityAccountSwitcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Antigravity Account Switcher"; Filename: "{app}\AntigravityAccountSwitcher.exe"; IconFilename: "{app}\icon.ico"
Name: "{group}\Uninstall Antigravity Account Switcher"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Antigravity Account Switcher"; Filename: "{app}\AntigravityAccountSwitcher.exe"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加快捷方式:"; Flags: unchecked
