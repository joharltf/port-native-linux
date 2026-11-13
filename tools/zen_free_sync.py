#!/usr/bin/env python3
"""
zen_free_sync.py - konfigurasi OTOMATIS model utama Big Pickle + Fallback Ollama Lokal.

Yang dilakukan:
  1. Setel opencode/big-pickle sebagai model utama (tanpa perlu fetch API)
  2. Daftarkan provider Ollama lokal (default: ollama/qwen2.5-coder:3b)
  3. Tulis ~/.config/opencode/opencode.json:
       - model        = opencode/big-pickle
       - small_model  = ollama/qwen2.5-coder:3b (atau opencode/big-pickle jika --no-ollama)
       - provider     = registrasi endpoint Ollama lokal
       - permission   = edit + bash otomatis (isi yang sudah ada tidak ditimpa)
       - plugin       = ganti model otomatis (opencode/big-pickle -> ollama/qwen2.5-coder:3b)
  4. Simpan cadangan config lama (.bak-<waktu>) sebelum menulis.

Contoh:
  python3 zen_free_sync.py --dry-run                        # lihat hasil, tidak menulis
  python3 zen_free_sync.py                                  # tulis config global
  python3 zen_free_sync.py --ollama-model qwen2.5-coder:1.5b # ganti model lokal
"""
import argparse, json, os, shutil, sys, time

PLUGIN = "@renjfk/opencode-model-fallback"
PRIMARY_MODEL = "opencode/big-pickle"
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder:3b"
DEFAULT_OLLAMA_URL = "http://localhost:11434/v1"
DEFAULT_PERMISSION = {
    "edit": "allow",
    "bash": {"*": "allow", "rm -rf *": "deny", "sudo *": "ask", "git push *": "ask"},
}


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def ensure_ollama_provider(cfg, ollama_model, ollama_url, num_ctx):
    """Daftarkan provider ollama lokal sesuai skema OpenCode."""
    providers = cfg.get("provider")
    if not isinstance(providers, dict):
        providers = {}

    ollama_cfg = providers.get("ollama")
    if not isinstance(ollama_cfg, dict):
        ollama_cfg = {}

    ollama_cfg["npm"] = "@ai-sdk/openai-compatible"
    ollama_cfg["name"] = "Ollama Lokal"

    opts = ollama_cfg.get("options")
    if not isinstance(opts, dict):
        opts = {}
    opts["baseURL"] = ollama_url
    opts.setdefault("apiKey", "ollama")
    ollama_cfg["options"] = opts

    models_map = ollama_cfg.get("models")
    if not isinstance(models_map, dict):
        models_map = {}

    models_map[ollama_model] = {
        "name": f"{ollama_model} (Lokal)",
        "tools": True,
        "options": {
            "num_ctx": num_ctx
        }
    }
    ollama_cfg["models"] = models_map
    providers["ollama"] = ollama_cfg
    cfg["provider"] = providers


def build(cfg, primary_model, use_plugin, ollama_model=None, ollama_url=DEFAULT_OLLAMA_URL, num_ctx=8192):
    ids = [primary_model]

    if ollama_model:
        ensure_ollama_provider(cfg, ollama_model, ollama_url, num_ctx)
        local_id = "ollama/" + ollama_model
        if local_id not in ids:
            ids.append(local_id)

    cfg["$schema"] = cfg.get("$schema", "https://opencode.ai")
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
            "retry_on_errors":,
            "retryable_error_patterns": [
                "rate.?limit",
                "usage.?limit",
                "quota",
                "too many requests",
                "overloaded",
                "timeout",
                "fetch failed",
            ],
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
    ap.add_argument("--primary", default=PRIMARY_MODEL,
                    help="model utama (default: opencode/big-pickle)")
    ap.add_argument("--ollama-model", default=DEFAULT_OLLAMA_MODEL,
                    help="nama model Ollama lokal untuk fallback (default: qwen2.5-coder:3b)")
    ap.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL,
                    help="endpoint API Ollama (default: http://localhost:11434/v1)")
    ap.add_argument("--ollama-ctx", type=int, default=8192,
                    help="batas context window Ollama lokal agar hemat RAM/CPU (default: 8192)")
    ap.add_argument("--no-ollama", action="store_true",
                    help="jangan tambahkan fallback ke Ollama lokal")
    ap.add_argument("--no-plugin", action="store_true", help="jangan tulis blok plugin")
    ap.add_argument("--dry-run", action="store_true", help="tampilkan saja")
    a = ap.parse_args()

    path = a.config or ("./opencode.json" if a.project else
                        os.path.expanduser("~/.config/opencode/opencode.json"))

    try:
        cfg = load_json(path)
    except Exception as e:
        print("GAGAL baca %s (bukan JSON valid?): %s" % (path, e))
        print("Config TIDAK diubah. Perbaiki atau pindahkan file itu dulu.")
        return 1

    ollama_target = None if a.no_ollama else a.ollama_model
    new = build(
        cfg,
        a.primary,
        not a.no_plugin,
        ollama_model=ollama_target,
        ollama_url=a.ollama_url,
        num_ctx=a.ollama_ctx,
    )

    print("Rantai model terpilih:")
    print("  1. %s (Utama)" % a.primary)
    if ollama_target:
        print("  2. ollama/%s (Fallback Lokal)" % ollama_target)

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
