#define MyAppName "Playitfy"
#define MyAppVersion "1.3"
#define MyAppPublisher "gantarugavr.me"
#define MyAppURL "https://github.com/gantarugavr/Playitfy"
#define MyAppExeName "Playitfy.exe"

[Setup]
; ── Identity ──────────────────────────────────────────────────────────────────
AppName={#MyAppName}
AppVersion={#MyAppVersion} - Open Source
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases

; ── Install Path ──────────────────────────────────────────────────────────────
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; ── Output ────────────────────────────────────────────────────────────────────
OutputDir=D:\Coding\Playitfy\Output
OutputBaseFilename=Playitfy - Music Player Setup v1.3
SetupIconFile=D:\Coding\Playitfy\icon.ico

; ── Compression ───────────────────────────────────────────────────────────────
Compression=lzma2/ultra64
SolidCompression=yes

; ── Architecture ──────────────────────────────────────────────────────────────
ArchitecturesInstallIn64BitMode=x64

; ── Privileges ────────────────────────────────────────────────────────────────
PrivilegesRequired=admin

; ── Appearance ────────────────────────────────────────────────────────────────
WizardStyle=modern
WizardResizable=no

; ── License Page ──────────────────────────────────────────────────────────────
LicenseFile=D:\Coding\Playitfy\LICENSE

; ── Uninstall ─────────────────────────────────────────────────────────────────
UninstallDisplayName={#MyAppName} {#MyAppVersion}
UninstallDisplayIcon={app}\icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Mengambil app.exe dari dist, dan mengganti namanya menjadi Playtify.exe saat instalasi
Source: "D:\Coding\Playitfy\dist\Playitfy.exe"; DestDir: "{app}"; DestName: "Playitfy.exe"; Flags: ignoreversion
Source: "D:\Coding\Playitfy\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\Coding\Playitfy\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent