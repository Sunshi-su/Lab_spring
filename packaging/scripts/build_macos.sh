#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

python3 -m venv .venv-build
source .venv-build/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python -m PyInstaller --clean --noconfirm packaging/pyinstaller/macos.spec

mkdir -p release_artifacts/macos
rm -f release_artifacts/macos/SpringLab-macOS.zip
rm -f release_artifacts/macos/SpringLab-macOS.dmg

ditto -c -k --sequesterRsrc --keepParent dist/SpringLab.app release_artifacts/macos/SpringLab-macOS.zip
hdiutil create \
  -volname "SpringLab" \
  -srcfolder dist/SpringLab.app \
  -ov \
  -format UDZO \
  release_artifacts/macos/SpringLab-macOS.dmg

echo "Готово:"
echo "  release_artifacts/macos/SpringLab-macOS.dmg"
echo "  release_artifacts/macos/SpringLab-macOS.zip"
