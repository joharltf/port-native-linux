#!/usr/bin/env bash
# install.sh - pasang portkit-bootstrap. TANPA sudo. Aman dijalankan ulang.
#
# Yang dilakukan:
#   - salin AGENTS.md, FASE.md, dan tools ke ~/.config/opencode
#   - buat wrapper pmem / pdoc / zensync di ~/.local/bin (bukan alias)
#   - buat ~/port (git, .gitignore, memory, state/BOOTSTRAP.md, setup_sudo.sh)
#   - jalankan zen_free_sync.py (config model gratis + fallback + izin)
#   - isi memori awal
# Pembaruan: git pull && bash install.sh  (progres BOOTSTRAP.md tidak ditimpa)
# Opsi: --no-sync (lewati config model)   env PORTKIT_ZEN_ARGS="--dry-run"
#       PORTKIT_ALLOW_ROOT=1 hanya untuk kontainer uji
set -eu
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CFG="$HOME/.config/opencode"; BIN="$HOME/.local/bin"; WS="$HOME/port"
NO_SYNC=0
for a in "$@"; do
  case "$a" in
    --no-sync) NO_SYNC=1 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
  esac
done
warn() { printf 'PERINGATAN: %s\n' "$*" >&2; }
die()  { printf 'GAGAL: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -ne 0 ] || [ "${PORTKIT_ALLOW_ROOT:-0}" = "1" ] || die "Jangan jalankan sebagai root/sudo."
[ "$(uname -s)" = "Linux" ] || die "Hanya Linux."
[ "$(uname -m)" = "x86_64" ] || warn "Arsitektur $(uname -m); target resmi x86_64."
command -v python3 >/dev/null 2>&1 || die "python3 tidak ada. Minta user: sudo apt install -y python3"
for f in AGENTS.md docs/FASE.md tools/zen_free_sync.py tools/port_mem.py \
         tools/port_doc.py templates/gitignore templates/setup_sudo.sh \
         templates/BOOTSTRAP.md VERSION; do
  [ -f "$SRC/$f" ] || die "File repo hilang: $f"
done

put() {  # put SUMBER TUJUAN : cadangkan tujuan jika isinya beda
  if [ -f "$2" ] && ! cmp -s "$1" "$2"; then
    cp "$2" "$2.bak-$(date +%Y%m%d-%H%M%S)"
  fi
  cp "$1" "$2"
}
wrap() {  # wrap NAMA SKRIP
  printf '#!/bin/sh\nexec python3 "$HOME/.config/opencode/%s" "$@"\n' "$2" > "$BIN/$1"
  chmod +x "$BIN/$1"
}

mkdir -p "$CFG" "$BIN" "$WS/dumps" "$WS/state" "$WS/memory"

put "$SRC/AGENTS.md"                "$CFG/AGENTS.md"
put "$SRC/docs/FASE.md"             "$CFG/FASE.md"
put "$SRC/tools/zen_free_sync.py"   "$CFG/zen_free_sync.py"
put "$SRC/tools/port_mem.py"        "$CFG/port_mem.py"
put "$SRC/tools/port_doc.py"        "$CFG/port_doc.py"
cp "$SRC/VERSION" "$CFG/portkit.version"
wrap pmem port_mem.py; wrap pdoc port_doc.py; wrap zensync zen_free_sync.py

if ! grep -qF "# >>> portkit >>>" "$HOME/.bashrc" 2>/dev/null; then
  cat >> "$HOME/.bashrc" << 'RC'

# >>> portkit >>>
export PATH="$HOME/.local/bin:$HOME/port/portkit/bin:$PATH"
export PORT_DUMPS="$HOME/port/dumps"
# <<< portkit <<<
RC
fi
export PATH="$BIN:$PATH"

# workspace
if command -v git >/dev/null 2>&1; then
  [ -d "$WS/.git" ] || git init -q "$WS"
else
  warn "git belum ada (akan terpasang oleh setup_sudo.sh)."
fi
if [ -f "$WS/.gitignore" ]; then
  while IFS= read -r l; do
    grep -qxF "$l" "$WS/.gitignore" || printf '%s\n' "$l" >> "$WS/.gitignore"
  done < "$SRC/templates/gitignore"
else
  cp "$SRC/templates/gitignore" "$WS/.gitignore"
fi
put "$SRC/templates/setup_sudo.sh" "$WS/setup_sudo.sh"; chmod +x "$WS/setup_sudo.sh"
[ -f "$WS/state/BOOTSTRAP.md" ] || cp "$SRC/templates/BOOTSTRAP.md" "$WS/state/BOOTSTRAP.md"

# memori awal (idempotent)
PM="python3 $CFG/port_mem.py"
export PORT_MEM_DIR="$WS/memory"
$PM add "Balas dalam bahasa Indonesia, ringkas" --cat pref --pin --global >/dev/null || true
$PM add "Hanya disc milik user di ~/port/dumps; jangan unduh ISO" --cat pref --pin --global >/dev/null || true
$PM add "Workspace ~/port; agen tanpa sudo, pakai ~/port/setup_sudo.sh" --cat fakta --pin --global >/dev/null || true
$PM add "Config model dibuat zen_free_sync.py (perintah zensync)" --cat fakta --global >/dev/null || true

# config model gratis + fallback + izin
SYNC="dilewati (--no-sync)"
if [ "$NO_SYNC" -eq 0 ]; then
  # shellcheck disable=SC2086
  if python3 "$CFG/zen_free_sync.py" ${PORTKIT_ZEN_ARGS:-}; then
    SYNC="berhasil"
  else
    SYNC="GAGAL (config tidak diubah; pilih model manual lewat /models, ulangi: zensync)"
  fi
fi

# komit workspace
if command -v git >/dev/null 2>&1; then
  (
    cd "$WS"
    git add .gitignore memory state/BOOTSTRAP.md >/dev/null 2>&1 || true
    G=git
    [ -n "$(git config user.name 2>/dev/null || true)" ] || G="git -c user.name=portkit -c user.email=portkit@localhost"
    $G commit -q -m "portkit: setup awal ($(cat "$SRC/VERSION"))" >/dev/null 2>&1 || true
  )
fi

MISSING=""
for c in gcc cmake java rg jq git; do command -v "$c" >/dev/null 2>&1 || MISSING="$MISSING $c"; done
command -v opencode >/dev/null 2>&1 || warn "opencode tidak ditemukan di PATH."

echo "== portkit $(cat "$SRC/VERSION") terpasang =="
echo "Config model : $SYNC"
echo "Workspace    : $WS"
echo "Perintah     : pmem, pdoc, zensync (di ~/.local/bin)"
if [ -n "$MISSING" ]; then
  echo "Paket kurang :$MISSING"
fi
echo
echo "LANGKAH BERIKUT (untuk user, bukan agen):"
[ -z "$MISSING" ] || echo "  1. Di terminal biasa: bash ~/port/setup_sudo.sh"
echo "  2. source ~/.bashrc"
echo "  3. Tutup OpenCode, lalu: cd ~/port && opencode"
echo "  4. Kirim PERINTAH 2 dari README.md"
