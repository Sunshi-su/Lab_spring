[Setup]
AppId={{E06CBE6A-9F94-4BC5-BD87-7F1D9E6A0101}
AppName=SpringLab
AppVersion=1.0.0
AppPublisher=KIPFIN
DefaultDirName={autopf}\SpringLab
DefaultGroupName=SpringLab
DisableProgramGroupPage=yes
OutputDir=..\..\..\release_artifacts\windows
OutputBaseFilename=SpringLab-Windows-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\..\..\dist\SpringLab.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SpringLab"; Filename: "{app}\SpringLab.exe"
Name: "{autodesktop}\SpringLab"; Filename: "{app}\SpringLab.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SpringLab.exe"; Description: "{cm:LaunchProgram,SpringLab}"; Flags: nowait postinstall skipifsilent
