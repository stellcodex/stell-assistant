#!/usr/bin/env bash
# Stell — Git → Drive push script (knowledge güncellendikten sonra Drive'ı güncelle)
# Kullanım: bash scripts/push-to-drive.sh

set -euo pipefail

DRIVE_REMOTE="gdrive:stellcodex-genois"
STELL_DIR="/root/stell"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")

echo "[stell-push] $TIMESTAMP başlatılıyor..."

rclone sync "${STELL_DIR}/" "${DRIVE_REMOTE}/02_approved/github-seed/" \
  --exclude ".git/**" \
  --exclude "scripts/**"

echo "[stell-push] Drive güncellendi: ${DRIVE_REMOTE}/02_approved/github-seed/"
echo "[stell-push] Bitti."
