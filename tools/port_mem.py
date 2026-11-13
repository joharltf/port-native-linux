#!/usr/bin/env python3
"""
port_mem.py - MEMORI PERMANEN untuk AI (berbasis file, ikut Git).

Dua lapis memori:
  - GLOBAL : ~/port/memory/global.jsonl   (preferensi, versi tool, pelajaran)
  - GAME   : games/<platform>/<id>/state/memory.jsonl  (otomatis dipilih
             jika perintah dijalankan di dalam folder game)

Perintah (alias disarankan: pmem):
  add "<teks>" [--cat fakta|keputusan|masalah|pref|pelajaran]
               [--pin] [--global]      simpan (idempotent, tanpa duplikat)
  show [--n 16]                        ringkasan untuk awal sesi (<= ~45 baris)
  search <kata> [<kata>...]            cari di kedua lapis
  pin|unpin <id>                       sematkan / lepas
  forget <id>                          hapus satu memori
  compact [--keep 200]                 buang duplikat + yang tertua (non-pin)
  export                               tulis MEMORY.md yang bisa dibaca manusia

Aturan: JANGAN simpan rahasia. Teks yang mirip API key/password ditolak.
Folder memori global bisa diganti dengan env PORT_MEM_DIR.
"""
import argparse, hashlib, json, os, re, sys, time

CATS = ["fakta", "keputusan", "masalah", "pref", "pelajaran"]
SECRET = re.compile(
    r"(sk-[A-Za-z0-9_\-]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{12,}"
    r"|(?i:passw(or)?d|passwd|secret|api[_ -]?key|token)\s*[:=]\s*\S+"
    r"|[A-Za-z0-9+/=_\-]{40,})")


def gdir():
    return os.environ.get("PORT_MEM_DIR") or os.path.expanduser("~/port/memory")


def game_dir():
    parts = os.path.abspath(os.getcwd()).split(os.sep)
    for i, p in enumerate(parts):
        if p == "games" and i + 2 < len(parts):
            return os.sep.join(parts[:i + 3]), "%s/%s" % (parts[i + 1], parts[i + 2])
    return None, None


def paths(force_global=False):
    g = os.path.join(gdir(), "global.jsonl")
    gd, name = game_dir()
    if gd and not force_global:
        return g, os.path.join(gd, "state", "memory.jsonl"), name
    return g, None, None


def norm(t):
    return re.sub(r"\s+", " ", t.strip().lower())


def mid(t):
    return hashlib.sha1(norm(t).encode()).hexdigest()[:6]


def load(p):
    if not p or not os.path.exists(p):
        return []
    out = []
    with open(p, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass  # baris rusak dilewati, tidak merusak yang lain
    return out


def save(p, rows):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, p)


def target(a):
    g, gm, name = paths(getattr(a, "glob", False))
    return (gm, "game " + name) if gm else (g, "global")


def cmd_add(a):
    text = " ".join(a.text).strip()
    if not text:
        print("Teks kosong."); return 1
    if SECRET.search(text):
        print("DITOLAK: teks mirip rahasia (key/password/token). Tidak disimpan.")
        return 1
    p, label = target(a)
    rows = load(p)
    i = mid(text)
    for r in rows:
        if r["id"] == i:
            r["ts"] = int(time.time())
            r["pin"] = r.get("pin") or a.pin
            save(p, rows)
            print("sudah ada, diperbarui: %s (%s)" % (i, label)); return 0
    rows.append({"id": i, "ts": int(time.time()), "cat": a.cat,
                 "text": text, "pin": bool(a.pin)})
    save(p, rows)
    print("tersimpan: %s [%s] (%s)" % (i, a.cat, label))
    return 0


def fmt(r, w=150):
    t = r["text"]
    t = t if len(t) <= w else t[:w - 1] + "…"
    return " %s%s [%s] %s" % ("*" if r.get("pin") else " ", r["id"], r["cat"], t)


def cmd_show(a):
    g, gm, name = paths()
    layers = [("GLOBAL", load(g))]
    if gm:
        layers.append(("GAME " + name, load(gm)))
    budget = max(5, a.n)
    printed = 0
    for label, rows in layers:
        rows = sorted(rows, key=lambda r: (not r.get("pin"), -r["ts"]))
        share = budget if len(layers) == 1 else budget // 2
        print("[MEMORI %s] %d entri" % (label, len(rows)))
        for r in rows[:share]:
            print(fmt(r)); printed += 1
        if len(rows) > share:
            print("  ... +%d lagi (pmem search <kata>)" % (len(rows) - share))
    if not printed:
        print("(memori kosong)")
    return 0


def cmd_search(a):
    g, gm, _ = paths()
    words = [w.lower() for w in a.words]
    hits = 0
    for label, p in (("global", g), ("game", gm)):
        for r in load(p):
            blob = (r["text"] + " " + r["cat"]).lower()
            if all(w in blob for w in words):
                print("%s%s" % (fmt(r, 200), "  <%s>" % label)); hits += 1
                if hits >= 30:
                    print("... dipotong 30"); return 0
    if not hits:
        print("tidak ada hasil")
    return 0


def edit(a, fn):
    g, gm, _ = paths()
    for p in (g, gm):
        rows = load(p)
        new = fn(rows)
        if new is not None and (len(new) != len(rows) or new != rows):
            save(p, new); return True
    return False


def cmd_pin(a, val):
    def fn(rows):
        hit = False
        for r in rows:
            if r["id"] == a.id:
                r["pin"] = val; hit = True
        return rows if hit else None
    print(("ok" if edit(a, fn) else "id tidak ditemukan")); return 0


def cmd_forget(a):
    def fn(rows):
        new = [r for r in rows if r["id"] != a.id]
        return new if len(new) != len(rows) else None
    print(("dihapus" if edit(a, fn) else "id tidak ditemukan")); return 0


def cmd_compact(a):
    g, gm, _ = paths()
    for p in (g, gm):
        rows = load(p)
        if not rows:
            continue
        seen, out = set(), []
        for r in sorted(rows, key=lambda r: -r["ts"]):
            k = norm(r["text"])
            if k not in seen:
                seen.add(k); out.append(r)
        pins = [r for r in out if r.get("pin")]
        rest = [r for r in out if not r.get("pin")][:max(0, a.keep - len(pins))]
        new = sorted(pins + rest, key=lambda r: r["ts"])
        save(p, new)
        print("%s: %d -> %d" % (p, len(rows), len(new)))
    return 0


def cmd_export(a):
    g, gm, name = paths()
    for label, p in (("global", g), ("game " + (name or ""), gm)):
        if not p:
            continue
        rows = sorted(load(p), key=lambda r: (r["cat"], -r["ts"]))
        md = os.path.join(os.path.dirname(p), "MEMORY.md")
        with open(md, "w", encoding="utf-8") as f:
            f.write("# MEMORI %s\n" % label)
            cur = None
            for r in rows:
                if r["cat"] != cur:
                    cur = r["cat"]; f.write("\n## %s\n" % cur)
                f.write("- %s%s (%s)\n" % ("**[pin]** " if r.get("pin") else "",
                                         r["text"], r["id"]))
        print("ditulis: " + md)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="c", required=True)
    s = sp.add_parser("add"); s.add_argument("text", nargs="+")
    s.add_argument("--cat", choices=CATS, default="fakta")
    s.add_argument("--pin", action="store_true")
    s.add_argument("--global", dest="glob", action="store_true")
    s = sp.add_parser("show"); s.add_argument("--n", type=int, default=16)
    s = sp.add_parser("search"); s.add_argument("words", nargs="+")
    for n in ("pin", "unpin", "forget"):
        s = sp.add_parser(n); s.add_argument("id")
    s = sp.add_parser("compact"); s.add_argument("--keep", type=int, default=200)
    sp.add_parser("export")
    a = ap.parse_args()
    return {"add": cmd_add, "show": cmd_show, "search": cmd_search,
            "pin": lambda x: cmd_pin(x, True), "unpin": lambda x: cmd_pin(x, False),
            "forget": cmd_forget, "compact": cmd_compact,
            "export": cmd_export}[a.c](a)


if __name__ == "__main__":
    sys.exit(main())
