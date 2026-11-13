=====================================================================
FASE v7 - PANDUAN DETAIL (dibaca per bagian lewat `pdoc`, BUKAN utuh)
Dipasang otomatis oleh install.sh ke ~/.config/opencode/FASE.md
Pakai : pdoc list | pdoc <BAGIAN> | pdoc FASE-1 C3
Isi sama dengan bagian 2-9 dan 11 pada AGENTS v6; hanya dipindah agar
tidak dimuat di setiap sesi.
=====================================================================

## STRUKTUR - STRUKTUR (PISAH CORE / PLATFORM / GAME)
$WORKSPACE/ (default ~/port)
  portkit/                      <- dikomit ke Git, dibuat sekali
    bin/port                    <- CLI utama
    env.sh                      <- env (PORT_DUMPS, ANDROID_*, PATH)
    core/                       <- SHARED semua konsol:
      cli, state, queue, check, build, git, notes,
      assets registry, android+sdl2 scaffold, tes
    platforms/{wii,xbox,x360}/  <- dibuat sekali per konsol
    formats/<developer-or-engine>/  <- parser aset lintas game
    templates/                  <- skeleton per platform
    tests/
  dumps/                        <- $PORT_DUMPS (git-ignored)
  tools/                        <- binary pihak ketiga (git-ignored)
  games/<platform>/<GAME_ID>/   <- DATA per game saja
    orig/ extract/ assets/ build/   (git-ignored)
    src/ include/ platform/ notes/ state/

INTERFACE PLATFORM MODULE (wajib untuk semua konsol)
  detect(disc)      -> disc/format ini milik platform ini?
  extract(disc,out) -> ekstrak isi disc, temukan executable utama
  analyze(exe)      -> functions.csv (id, addr, size, kind, callees,
                       callers, depth, difficulty, status, percent)
  brief(id)         -> disasm + konteks ringkas untuk `port next`
  check(id)         -> compile + diff, cetak persen match
  lift(exe)         -> (opsional, TRACK B) terjemah ke C
  gfx_template      -> skeleton backend GPU (GX / NV2A / Xenos)
  notes             -> daftar batasan platform
Core memanggil modul lewat interface ini; perintah `port` sama untuk
semua konsol.

## FASE-0 - FASE 0 - SISTEM DASAR (SEKALI, SEMUA KONSOL)
0.1 Cek: lsb_release -a; uname -m; free -h; df -h $HOME; nproc
    Syarat: Ubuntu/Debian x86_64, RAM >= 16 GB, disk >= 150 GB.
0.2 Paket apt dipasang manual oleh user (Langkah 1). Cek saja dengan
    `port doctor`; jika kurang, minta user menjalankan sudo apt.
0.3 Android: cmdline-tools ke $HOME/Android, lalu
    sdkmanager --licenses
    sdkmanager "platform-tools" "platforms;android-34"
      "build-tools;34.0.0" "ndk;26.1.10909125" "cmake;3.22.1"
    export ANDROID_HOME=$HOME/Android
    export ANDROID_NDK_HOME=$ANDROID_HOME/ndk/26.1.10909125
0.4 Ghidra (ke tools/ghidra, rilis terbaru dari GitHub resmi, JDK 17+)
0.5 Python venv (~/port/.venv) + pip: capstone pyelftools construct
    pillow numpy pytest
0.6 Tulis env ke ~/.bashrc dan portkit/env.sh, termasuk
    export PORT_DUMPS="$HOME/port/dumps" (mkdir -p $PORT_DUMPS).
    PATH harus memuat ~/.local/bin (pmem, pdoc, zensync) dan
    ~/port/portkit/bin. Alias TIDAK berfungsi di shell agent;
    gunakan skrip wrapper, bukan alias.
Jika URL gagal: cari rilis resmi di halaman proyek, jangan menebak.

## FASE-1 - FASE 1 - CORE `port` (SEKALI, SEMUA KONSOL)
Syarat tiap tool: --help, output <= 60 baris, idempotent, ada tes
dengan sampel sintetis (bukan disc asli), komit setelah tes hijau.
Boleh dikerjakan per potongan (C1-C4, C5-C8, C9-C15).

C1.  port doctor     cek semua binary/env, tabel OK/GAGAL.
C2.  port platforms  daftar platform module terpasang.
C2b. port dumps      daftar isi $PORT_DUMPS (rekursif): nama file,
                     platform terdeteksi, ID game & judul dari header
                     disc, ukuran. Maks 30 baris. Ekstensi: .iso
                     .wbfs .rvz .gcm .ciso .xiso .xbe (folder) dan
                     folder GOD Xbox 360.
C3.  port new "<nama game>" [--track A|B] [--pick N]
                     [--platform auto|wii|xbox|x360]
                     User hanya menyebut NAMA GAME. Tool mencari disc
                     di $PORT_DUMPS:
                      1. Normalisasi nama (huruf kecil, buang tanda
                         baca/spasi ganda), cocokkan ke NAMA FILE dan
                         JUDUL header disc (fuzzy: semua kata kunci
                         harus ada).
                      2. Tepat 1 cocok -> pakai.
                      3. > 1 -> daftar bernomor (maks 10), berhenti;
                         ulangi dengan --pick N.
                      4. Tidak ada -> cetak isi $PORT_DUMPS, berhenti.
                         Jangan mencari ke folder lain.
                     Setelah ketemu: detect() platform, ambil GAME_ID,
                     buat games/<platform>/<id>/ + .gitignore +
                     git init, extract(), simpan hash, tulis
                     notes/overview.md (<= 15 baris). Idempotent
                     (tidak menimpa pekerjaan). Path penuh diterima
                     sebagai cadangan.
C4.  port analyze    panggil analyze() platform -> functions.csv.
C5.  port next [N]   leaf & difficulty terkecil dulu; brief <= 150
                     baris disasm; buat stub src/.
C6.  port ctx <id>   caller, string, konstanta (<= 60 baris).
C7.  port check <id> compile + diff; persen + 20 baris beda pertama.
C8.  port commit|skip|note|status  state & git.
C9.  port assets scan|unpack
                     registry lintas game di portkit/formats/.
                     Format baru -> parser Python + tes, daftarkan.
                     Cek dulu tool komunitas yang sudah ada.
C10. port platform scaffold
                     salin templates/<platform> + SDL2/CMake + Android
                     Gradle ke games/<platform>/<id>/platform/.
C11. port build pc|android | port run | port apk
                     log penuh ke build/*.log, tampil ringkasan.
C12. port loop <N>   cetak tugas berikutnya setelah tugas selesai
                     (tidak memanggil AI sendiri).
C13. port resume     cetak <= 25 baris: game aktif, 5 catatan
                     terakhir, tugas berikutnya, status git
                     (bersih/kotor), lalu `pmem show --n 12`. Dipakai
                     di awal sesi dan setelah model berganti.
C14. port models [sync|show]
                     sync: jalankan ~/.config/opencode/zen_free_sync.py
                     (salin juga ke portkit/core/ agar ikut Git).
                     show: cetak model, small_model, dan rantai
                     fallback dari opencode.json (<= 10 baris).
                     Tidak pernah menimpa config jika skrip gagal.
C15. port mem ...    pembungkus tipis ke port_mem.py (salin ke
                     portkit/core/). Argumen diteruskan apa adanya.
Selesai: portkit/README.md (<= 60 baris) + `git tag core-v1`.

## P-WII - FASE P-WII - MODULE WII (SEKALI; SAAT BUTUH WII)
Binary/tool: devkitPro (dkp-pacman -S wii-dev), decomp-toolkit (dtk),
objdiff + objdiff-cli, wit (wit.wiimm.de), Dolphin (flatpak
org.DolphinEmu.dolphin-emu). Ambil rilis terbaru dari halaman resmi.
Kerjakan berurutan, satu fitur per pesan:
  detect     : header disc Wii (ID game, magic Wii).
  extract    : wit extract -> main.dol.
  analyze    : dtk dol info/split, tandai library SDK/RVL/GX/OS.
  check      : compile (devkitPPC atau mwcc via skrip template dtk)
               + objdiff-cli.
  lift (B)   : lifter Gekko/PowerPC -> C (capstone), integer ->
               float/paired-single -> CR/FPSCR; tes per instruksi.
  gfx_template : GX (TEV, tekstur, EFB copy) -> Vulkan/GLES; rujuk
               kode Dolphin.
  input      : Wii Remote pointer -> sentuh/analog; tombol virtual.
Tes: sampel .dol sintetis kecil. Selesai: `git tag wii-v1`.

## P-XBOX - FASE P-XBOX - MODULE XBOX ORIGINAL (SEKALI; SAAT BUTUH XBOX)
Arsitektur: x86 (Pentium III), executable .xbe, GPU NV2A.
Tool: extract-xiso, nxdk, xemu (referensi). Cari parser .xbe yang
sudah ada sebelum menulis.
  detect     : struktur XISO / header .xbe.
  extract    : extract-xiso -x -> default.xbe + aset.
  analyze    : parser .xbe (section, import kernel), disasm x86 via
               capstone, functions.csv. Import kernel ditandai
               "library".
  check      : TRACK A butuh compiler asli (MSVC era 2001) -> hanya
               jika user menyediakan sendiri; jika tidak, TRACK B.
  lift (B)   : lifter x86 -> C (flag, segment, FPU x87), tes sintetis.
               Lebih sulit dari PowerPC; bertahap.
  gfx_template : NV2A (register combiner, pushbuffer) -> Vulkan/GLES;
               rujuk xemu.
  kernel     : tabel pengganti panggilan kernel Xbox (file, thread,
               memori, audio).
Selesai: `git tag xbox-v1`.

## P-X360 - FASE P-X360 - MODULE XBOX 360 (SEKALI; SAAT BUTUH X360)
Arsitektur: PowerPC (Xenon), executable .xex, GPU Xenos.
Tool: extractor XISO/GOD yang tersedia, XenonRecomp (basis static
recomp), Xenia (referensi). .xex sering terkompresi/terenkripsi:
gunakan hanya dump dan kunci milik user lewat alat yang sah; jangan
membantu mengakali proteksi.
Fitur: seperti P-WII untuk PowerPC (lifter bisa berbagi kode dengan
Gekko), ditambah VMX128, kernel Xbox 360, gfx_template Xenos ->
Vulkan/GLES.
Selesai: `git tag x360-v1`.

## GAME-BARU - GAME BARU (SETELAH MODULE PLATFORM ADA)
  port doctor
  # taruh disc milik sendiri di $PORT_DUMPS, lalu:
  port dumps                              (opsional)
  port new "<nama game>" --track A|B      (disc & platform otomatis)
  port analyze
  port assets scan
  port platform scaffold
  port build pc && port run               # test pattern
Hanya jika `port assets scan` menemukan format tak dikenal: tulis
parser di portkit/formats/<developer>/ dengan tes, komit. Game
berikutnya dari developer/engine sama otomatis memakainya.

## LOOP - LOOP KERJA (SEMUA KONSOL, SAMA)
TRACK A (decomp):
  1. port resume
  2. port next 3 -> kerjakan SATU fungsi
  3. tulis kode di src/
  4. port check <id> (maks 3 kali, lalu skip)
  5. port commit <id> -> ulang dari 2
TRACK B (recomp):
  1. port lift -> src/lifted/
  2. port build pc -> perbaiki di lifter (tool), bukan tambal output
  3. isi stub platform (gfx/audio/input/kernel)
  4. port run -> catat bug ke NOTES.md
Android: port build android && port apk
  adb logcat | rg -i "<nama_app>" | head -50

## CATATAN - CATATAN REALISTIS
- Tool menghilangkan eksplorasi dan kerja mekanis; menulis ulang
  kode game tetap dikerjakan AI per fungsi.
- Model gratis lebih lemah dan sering kena rate limit: kecilkan tugas,
  perbanyak komit. Untuk lifter/analisis yang rumit, pertimbangkan
  model berbayar (/connect) bila model gratis terus gagal.
- Game besar tetap lama. Latih alur di game kecil dulu.
- Compiler proprietary (mwcc, MSVC) jangan diunduh dari sumber tidak
  jelas; pakai skrip template resmi atau milik user sendiri.
- Jika tujuan hanya main di HP: Dolphin (Wii) jauh lebih cepat.
- Kode turunan Dolphin/xemu/Xenia mengikuti lisensi masing-masing.
=====================================================================
