#!/usr/bin/env bash
# Builds a .deb package from an already-built dist/AutoClicker binary.
# Usage: build_deb.sh VERSION
set -euo pipefail

VERSION="${1:?Usage: build_deb.sh VERSION}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAGE="$ROOT_DIR/packaging/linux/AutoClicker"
OUT_DIR="$ROOT_DIR/installer_output"

rm -rf "$STAGE"
mkdir -p "$STAGE/DEBIAN"
mkdir -p "$STAGE/opt/autoclicker"
mkdir -p "$STAGE/usr/share/applications"
mkdir -p "$STAGE/usr/share/icons/hicolor/256x256/apps"

cp "$ROOT_DIR/dist/AutoClicker" "$STAGE/opt/autoclicker/AutoClicker"
chmod 755 "$STAGE/opt/autoclicker/AutoClicker"

cp "$ROOT_DIR/packaging/linux/autoclicker.desktop" "$STAGE/usr/share/applications/autoclicker.desktop"
cp "$ROOT_DIR/assets/AutoClicker.png" "$STAGE/usr/share/icons/hicolor/256x256/apps/autoclicker.png"

cat > "$STAGE/DEBIAN/control" <<EOF
Package: autoclicker
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Maintainer: to0-young <71845331+to0-young@users.noreply.github.com>
Description: Simple auto clicker with configurable interval, hotkey, and UA/RU/EN interface
EOF

mkdir -p "$OUT_DIR"
dpkg-deb --build --root-owner-group "$STAGE" "$OUT_DIR/AutoClicker.deb"

echo "Built $OUT_DIR/AutoClicker.deb"
