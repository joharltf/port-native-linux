# portkit-bootstrap

Setup awal OpenCode (model **Zen gratis**) untuk proyek port game (Wii, lalu
Xbox/Xbox 360) ke PC (SDL2) dan Android. Satu perintah ke OpenCode: ia
mengambil repo ini, menjalankan `install.sh`, lalu mengerjakan sisanya sendiri.

## Pakai (3 langkah)

**0. Sekali, di terminal:**

```bash
mkdir -p ~/port && cd ~/port && opencode
```

Di OpenCode ketik `/models`, pilih satu model berlabel *free*. Jika diminta
izin menjalankan perintah, pilih *allow always*.

**1. PERINTAH 1 (tempel satu kali).** Ganti `<USERNAME>/<REPO>`:

```
Ambil repo https://github.com/<USERNAME>/<REPO> ke ~/port-bootstrap
(git clone; jika git tidak ada, unduh zip dari GitHub lalu ekstrak).
Baca README.md-nya, lalu jalankan: bash ~/port-bootstrap/install.sh
Jangan menjalankan sudo. Laporkan hasil <= 8 baris dan ikuti bagian
"LANGKAH BERIKUT" dari output-nya.
```

**2. Dua hal manual (AI tidak boleh sudo):**

```bash
bash ~/port/setup_sudo.sh      # sekali, minta password sudo
source ~/.bashrc
```

Tutup OpenCode, lalu `cd ~/port && opencode`.

**3. PERINTAH 2 (kirim berulang sampai semua `[x]`):**

```
Baca ~/port/state/BOOTSTRAP.md. Kerjakan item "[ ]" berurutan mulai dari
yang pertama sesuai AGENTS (baca bagiannya dengan pdoc: Fase 0, Fase 1,
P-WII). Tiap item: tes, komit, ubah jadi "[x]". Berhenti saat ada yang
gagal atau butuh sudo (tulis ke setup_sudo.sh dan minta user).
Laporan <= 5 baris.
```

Aman dikirim ulang setelah limit habis, model berganti, atau OpenCode dibuka
lagi: kemajuan ada di `BOOTSTRAP.md`, Git, dan memori (`pmem`).

## Setelah semua `[x]`

Taruh disc **milik sendiri** di `~/port/dumps`, lalu di OpenCode:

```
Game baru: <nama game>. Jalankan urutan game baru.
```

Kerja harian (di folder game): `port resume, lalu port loop 3. Berhenti setelah 3.`
Konsol lain: `Jalankan Fase P-XBOX saja.` atau `Jalankan Fase P-X360 saja.`

## Yang dipasang `install.sh` (tanpa sudo, aman diulang)

| Item | Lokasi |
|---|---|
| `AGENTS.md` (otak ringan ± 4,5 KB, dimuat tiap sesi) | `~/.config/opencode/AGENTS.md` |
| `FASE.md` (panduan detail, dibaca per bagian) | `~/.config/opencode/FASE.md` |
| `zen_free_sync.py` -> perintah `zensync` | config model gratis, fallback otomatis, izin edit |
| `port_mem.py` -> perintah `pmem` | memori permanen (global + per game) |
| `port_doc.py` -> perintah `pdoc` | baca panduan per bagian |
| `~/port` | git, `.gitignore`, `memory/`, `state/BOOTSTRAP.md`, `setup_sudo.sh` |

File yang sudah ada dicadangkan (`.bak-waktu`) sebelum ditimpa. Progres
`BOOTSTRAP.md` tidak pernah ditimpa.

## Perawatan

```bash
zensync                                   # daftar model gratis berganti: segarkan
cd ~/port-bootstrap && git pull && bash install.sh   # perbarui otak/tool
pmem show                                 # lihat memori
pdoc list                                 # lihat daftar panduan
```

## Catatan penting

- **Privasi:** selama masa gratis, prompt bisa dipakai tim model untuk
  memperbaiki model. Jangan kirim password, API key, atau data pribadi.
- **Legal:** hanya dump disc milik sendiri. Jangan unggah ISO, dump, atau aset
  game ke repo mana pun. Hanya kode port yang boleh dibagikan.
- **Repo ini harus publik** (atau AI tidak bisa meng-clone tanpa kredensial).
  Jangan menaruh token/API key di repo atau di perintah.
- **Keamanan:** `install.sh` dijalankan AI dari repo Anda sendiri. Tinjau
  perubahan sebelum `git pull`, dan pertimbangkan menyematkan tag/commit.
- Plugin ganti-model otomatis (`@renjfk/opencode-model-fallback`) adalah plugin
  komunitas; cek README-nya jika perilakunya berubah.
- Model gratis lebih lemah dan kuotanya dipakai bersama. Bagian tersulit
  (lifter PowerPC/x86, GX -> Vulkan) bisa memerlukan model lebih kuat.

## Struktur repo

```
install.sh   AGENTS.md   VERSION   README.md
docs/        FASE.md  LANGKAH_MANUAL.txt
tools/       zen_free_sync.py  port_mem.py  port_doc.py
templates/   BOOTSTRAP.md  setup_sudo.sh  gitignore
```
