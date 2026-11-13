=====================================================================
AGENTS v7 - OTAK RINGAN (selalu dimuat; detail dibaca hanya bila perlu)
Linux -> PC (SDL2) -> Android ARM64
Dipasang otomatis oleh install.sh ke ~/.config/opencode/AGENTS.md
=====================================================================
TUJUAN: toolkit `port` per konsol (wii, xbox, x360): CORE sekali,
MODULE platform sekali per konsol, lalu tiap game cukup `port new`.
Disc user disebut NAMANYA saja; ada di $PORT_DUMPS (~/port/dumps).
Xbox One tidak didukung.

DETAIL: jangan baca utuh. Sebelum mengerjakan fase/konsol/tool:
  pdoc list | pdoc <BAGIAN> | pdoc FASE-1 C3 | pdoc find <kata>
  BAGIAN: STRUKTUR FASE-0 FASE-1 P-WII P-XBOX P-X360 GAME-BARU LOOP
          CATATAN
  (jika pdoc tidak ada: python3 ~/.config/opencode/port_doc.py ...)

PERINTAH port (spesifikasi: pdoc FASE-1 <C#>)
  doctor platforms dumps new analyze next ctx check commit skip note
  status assets platform build run apk loop resume models mem
  Game baru : port new "<nama>" --track A|B, analyze, assets scan,
              platform scaffold, build pc, run   (pdoc GAME-BARU)
  Loop      : resume -> next 3 -> kerjakan SATU fungsi -> check
              (maks 3x lalu skip) -> commit      (pdoc LOOP)

--- LEGAL ---
 L1 Hanya dump disc milik user di $PORT_DUMPS; jangan unduh
    ISO/ROM/aset atau cari disc di luar folder itu.
 L2 Jangan commit .iso .rvz .wbfs .ciso .gcm .dol .rel .xbe .xex
    dan aset.
 L3 Tanpa bypass proteksi/lisensi. Scope: decomp, port, modding.
 L4 Hanya kode port yang boleh dibagikan.

--- KEAMANAN ---
 S1 Tulis hanya di ~/port, ~/.bashrc, ~/.config/opencode,
    ~/.local/bin. Jangan sentuh folder lain.
 S2 Jangan pernah menjalankan sudo. Butuh sudo = tulis ke
    ~/port/setup_sudo.sh, minta user menjalankannya, lalu berhenti.
 S3 Unduh tool hanya dari rilis resmi proyek; cocokkan checksum bila
    ada; jangan menebak URL. rm -rf hanya untuk build/ dan cache.

--- HEMAT TOKEN ---
 T1 Jangan `cat` file > 80 baris; pakai head/rg/sed -n.
 T2 Output tool <= 60 baris; detail ke file, cetak ringkasan+path.
 T3 Balasan ke user <= 5 baris kecuali diminta.
 T4 Mulai sesi: `port resume` (atau `pmem show` bila belum ada).
    Akhiri: `port note "<1 kalimat>"` + `pmem add` bila ada pelajaran.
 T5 Tanya tool dulu (`port next`, `port ctx`), jangan eksplorasi.
 T6 Langkah manual berulang > 2x = jadikan subcommand `port`.
 T7 Kriteria selesai dari tool (persen match, exit code).
 T8 Cache di state/; jangan ulang perintah mahal.
 T9 Buntu 3 percobaan -> `port skip <id> "<alasan>"`.

--- MODEL BERGANTI / LIMIT (model bisa berubah otomatis) ---
 M1 Jangan andalkan ingatan percakapan: status ada di file
    (state/NOTES.md, BOOTSTRAP.md, git log, memori).
 M2 Satu pesan = satu tugas kecil (satu tool / satu fungsi).
 M3 Semua tool idempotent; pesan terakhir boleh diulang model lain.
 M4 Komit tiap tool/fungsi setelah tes hijau.
 M5 Jangan mengarang hasil; "selesai" hanya bila tool mendukung.
 M6 Model default = GRATIS Zen (opencode/*-free) lewat zensync.
    "model not found"/rate limit terus -> minta user `zensync`.
    Jangan menulis ulang opencode.json sendiri.
 M7 Selama masa gratis prompt bisa dipakai memperbaiki model: jangan
    taruh password/API key/data pribadi di prompt, catatan, output.

--- MEMORI PERMANEN (global: ~/port/memory; game: state/memory.jsonl) ---
 pmem show | add "<teks>" --cat pref|fakta|keputusan|masalah|pelajaran
 [--pin] [--global] | search <kata> | pin|unpin|forget <id> | compact
 P1 Awal sesi baca memori SEBELUM bertindak; bila bertentangan dengan
    hasil tool, percaya tool lalu perbarui memori.
 P2 Simpan (1 kalimat, spesifik): preferensi/koreksi user (pref,
    --pin); keputusan+alasan; path/versi/flag tool yang berhasil
    (fakta); jalan buntu > 3 percobaan (masalah); solusi terbukti
    (pelajaran).
 P3 Jangan simpan rahasia, isi file besar, log, atau yang mudah
    dibaca ulang dari kode/Git.
 P4 --pin <= 10 entri; bila `pmem show` > ~45 baris: `pmem compact`.
 P5 Simpan tiap ~15 pesan dan sebelum berhenti; jangan tunggu akhir.
 P6 Sebelum menebak hal yang mungkin pernah diputuskan: `pmem search`.

--- BOOTSTRAP ---
 B1 Jika ~/port/state/BOOTSTRAP.md punya item "[ ]", itu tugas
    default: kerjakan "[ ]" pertama berurutan, tes, komit, ubah "[x]".
    (`port resume` belum ada sebelum C13 selesai.)
 B2 Sebelum tiap fase, baca bagiannya dengan `pdoc` (bukan menebak).
=====================================================================
