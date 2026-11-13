#!/usr/bin/env python3
"""
zen_free_sync.py - konfigurasi OTOMATIS model GRATIS OpenCode Zen.

Yang dilakukan:
  1. Ambil daftar model publik dari https://opencode.ai/zen/v1/models
  2. Pilih yang gratis (akhiran "-free", "big-pickle", atau harga semua 0)
  3. Urutkan (heuristik, bisa diatur dengan --prefer)
  4. Tulis ~/.config/opencode/opencode.json:
       - model        = model gratis terbaik
       - small_model  = model gratis kedua
       - permission   = edit + bash otomatis (isi yang sudah ada tidak ditimpa)
       - plugin       = ganti model otomatis (rantai A -> B -> C -> D)
  5. Simpan cadangan config lama (.bak-<waktu>) sebelum menulis.

Hanya library bawaan Python. Daftar model gratis berganti-ganti,
jadi jalankan ulang skrip ini kapan saja (aman diulang).

Contoh:
  python3 zen_free_sync.py --dry-run       # lihat hasil, tidak menulis
  python3 zen_free_sync.py                  # tulis config global
  python3 zen_free_sync.py --project        # tulis ./opencode.json
  python3 zen_free_sync.py --from-file m.json   # uji offline
"""
import argparse, json, os, shutil, sys, time, urllib.request

URL = "https://opencode.ai/zen/v1/models"
PLUGIN = "@renjfk/opencode-model-fallback"
PREFER = ["glm", "kimi", "deepseek", "nemotron", "minimax", "mimo", "big-pickle"]
DEFAULT_PERMISSION = {
    "edit": "allow",
    "bash": {"*": "allow", "rm -rf *": "deny", "sudo *": "ask", "git push *": "ask"},
}


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "zen-free-sync/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def items_of(data):
    """Terima beberapa bentuk JSON: {"data":[...]}, {"models":[...]}, [...]"""
    if isinstance(data, dict):
        for k in ("data", "models", "items"):
            if isinstance(data.get(k), list):
                data = data[k]
                break
        else:
            data = [dict(v, id=k) if isinstance(v, dict) else {"id": k}
                    for k, v in data.items()]
    out = []
    for it in data if isinstance(data, list) else []:
        if isinstance(it, str):
            out.append({"id": it})
        elif isinstance(it, dict) and isinstance(it.get("id"), str):
            out.append(it)
    return out


def numbers(obj):
    if isinstance(obj, bool):
        return []
    if isinstance(obj, (int, float)):
        return [obj]
    if isinstance(obj, str):
        try:
            return [float(obj.replace("$", ""))]
        except ValueError:
            return []
    if isinstance(obj, dict):
        return [n for v in obj.values() for n in numbers(v)]
    if isinstance(obj, list):
        return [n for v in obj for n in numbers(v)]
    return []


def is_free(it):
    mid = it["id"].lower()
    if mid.endswith("-free") or mid == "big-pickle":
        return True
    for key in ("pricing", "cost", "price"):
        if key in it:
            nums = numbers(it[key])
            if nums and all(n == 0 for n in nums):
                return True
    return False


def rank(mid, prefer):
    m = mid.lower()
    for i, p in enumerate(prefer):
        if p in m:
            return i
    return len(prefer)


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)  # gagal = berhenti, file TIDAK ditimpa


def build(cfg, models, use_plugin):
    ids = ["opencode/" + m for m in models]
    cfg["$schema"] = cfg.get("$schema", "https://opencode.ai/config.json")
    cfg["model"] = ids[0]
    cfg["small_model"] = ids[1] if len(ids) > 1 else ids[0]
    perm = cfg.get("permission")
    if not isinstance(perm, dict):
        perm = {}
    perm.setdefault("edit", DEFAULT_PERMISSION["edit"])
    perm.setdefault("bash", DEFAULT_PERMISSION["bash"])
    cfg["permission"] = perm
    if use_plugin and len(ids) > 1:
        mappings = {ids[i]: ids[i + 1] for i in range(len(ids) - 1)}
        entry = [PLUGIN, {
            "retry_on_errors": [429, 503],
            "retryable_error_patterns": ["rate.?limit", "usage.?limit"],
            "mappings": mappings,
        }]
        keep = []
        for p in cfg.get("plugin", []):
            name = p[0] if isinstance(p, list) and p else p
            if name != PLUGIN:
                keep.append(p)
        cfg["plugin"] = keep + [entry]
    return cfg


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", help="path opencode.json (default global)")
    ap.add_argument("--project", action="store_true", help="tulis ./opencode.json")
    ap.add_argument("--max", type=int, default=4, help="maks model dalam rantai (default 4)")
    ap.add_argument("--prefer", help="urutan kata kunci, dipisah koma")
    ap.add_argument("--no-plugin", action="store_true", help="jangan tulis blok plugin")
    ap.add_argument("--dry-run", action="store_true", help="tampilkan saja")
    ap.add_argument("--from-file", help="baca daftar model dari file (uji offline)")
    a = ap.parse_args()

    prefer = [p.strip().lower() for p in a.prefer.split(",")] if a.prefer else PREFER
    path = a.config or ("./opencode.json" if a.project else
                        os.path.expanduser("~/.config/opencode/opencode.json"))
    try:
        if a.from_file:
            with open(a.from_file, encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = fetch(URL)
    except Exception as e:
        print("GAGAL ambil daftar model: %s" % e)
        print("Config TIDAK diubah. Cek internet, lalu ulangi.")
        return 1

    free = sorted({it["id"] for it in items_of(data) if is_free(it)},
                  key=lambda m: (rank(m, prefer), m))[:max(1, a.max)]
    if not free:
        print("Tidak ada model gratis terdeteksi. Config TIDAK diubah.")
        print("Pilih manual lewat /models di OpenCode.")
        return 1

    try:
        cfg = load_json(path)
    except Exception as e:
        print("GAGAL baca %s (bukan JSON valid?): %s" % (path, e))
        print("Config TIDAK diubah. Perbaiki atau pindahkan file itu dulu.")
        return 1
    new = build(cfg, free, not a.no_plugin)

    print("Model gratis terpilih (urut prioritas):")
    for i, m in enumerate(free, 1):
        print("  %d. opencode/%s" % (i, m))
    if a.dry_run:
        print("\n--dry-run, tidak menulis. Hasil:\n")
        print(json.dumps(new, indent=2, ensure_ascii=False))
        return 0

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    try:
        if os.path.exists(path) and load_json(path) == new:
            print("Tidak ada perubahan: " + path)
            return 0
    except Exception:
        pass
    if os.path.exists(path):
        bak = "%s.bak-%s" % (path, time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(path, bak)
        print("Cadangan: " + bak)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Tertulis: " + path)
    print("Tutup lalu buka lagi OpenCode agar config terbaca.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
