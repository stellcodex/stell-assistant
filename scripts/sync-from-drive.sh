#!/usr/bin/env bash
# Stell — Drive → Git sync script
# Kullanım: bash scripts/sync-from-drive.sh

set -euo pipefail

DRIVE_REMOTE="gdrive:stellcodex-genois"
STELL_DIR="/root/stell"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")

echo "[stell-sync] $TIMESTAMP başlatılıyor..."

# 1. Drive'daki onaylı knowledge'ı indir
echo "[stell-sync] Drive'dan github-seed indiriliyor..."
rclone sync "${DRIVE_REMOTE}/02_approved/github-seed/" "${STELL_DIR}/" \
  --exclude ".git/**" \
  --exclude "scripts/**" \
  --exclude "handoff/**"

# 2. Değişiklik var mı?
cd "${STELL_DIR}"
if git diff --quiet && git diff --cached --quiet; then
  echo "[stell-sync] Değişiklik yok, commit atlanıyor."
else
  git add .
  git commit -m "chore: drive sync ${TIMESTAMP}

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
  echo "[stell-sync] Commit tamamlandı."
fi

echo "[stell-sync] Bitti."
