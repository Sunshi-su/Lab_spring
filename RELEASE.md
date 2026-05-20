# Сборка релизов

Эти файлы нужны только для подготовки готовых приложений. Исходный код остаётся отдельно в `Main.py` и `pins/`, а собранные файлы складываются в `release_artifacts/`.

## Важно

PyInstaller обычно собирает приложение под ту систему, на которой запущен. Поэтому:

- macOS-версию собирайте на Mac.
- Windows-версию собирайте на Windows.
- Готовые файлы не добавляйте в исходники репозитория: папка `release_artifacts/` уже добавлена в `.gitignore`.

## macOS

В терминале из корня проекта:

```bash
bash packaging/scripts/build_macos.sh
```

На выходе появятся:

- `release_artifacts/macos/SpringLab-macOS.dmg`
- `release_artifacts/macos/SpringLab-macOS.zip`

Для GitHub Release обычно прикладывайте `.dmg`, а `.zip` можно оставить как запасной вариант.

## Windows

На Windows откройте PowerShell в корне проекта и выполните:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\packaging\scripts\build_windows.ps1
```

Если установлен Inno Setup 6, появится установщик:

- `release_artifacts/windows/SpringLab-Windows-Setup.exe`

Если Inno Setup не установлен, скрипт создаст portable-файл:

- `release_artifacts/windows/SpringLab-Windows-Portable.exe`

Чтобы получить именно установщик, установите Inno Setup 6 и запустите скрипт ещё раз.

## Как оформить GitHub Release вручную

1. Соберите macOS-версию на Mac и Windows-версию на Windows.
2. Откройте репозиторий на GitHub.
3. Перейдите в `Releases`.
4. Нажмите `Draft a new release`.
5. Создайте тег, например `v1.0.0`.
6. Название релиза: `SpringLab 1.0.0`.
7. В описание добавьте кратко:
   - что это лабораторная работа по силе упругости;
   - что добавлены готовые сборки для macOS и Windows;
   - что пользователю не нужно ставить Python и библиотеки.
8. В `Assets` прикрепите:
   - `SpringLab-macOS.dmg`;
   - `SpringLab-Windows-Setup.exe`.
9. Нажмите `Publish release`.

После этого пользователи будут скачивать готовые приложения из блока `Assets`, а исходный код останется отдельно в репозитории.
