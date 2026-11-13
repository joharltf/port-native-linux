#!/usr/bin/env python3
"""
port_doc.py (pdoc) - baca panduan detail per BAGIAN, hemat token.

  pdoc list                 daftar bagian + baris pertama
  pdoc <BAGIAN>             cetak satu bagian (mis. FASE-1, P-WII)
  pdoc <BAGIAN> <ITEM>      cetak satu butir (mis. pdoc FASE-1 C3)
  pdoc find <kata>          cari kata di panduan (maks 20 baris)

File panduan: $PORT_DOC atau ~/.config/opencode/FASE.md
"""
import os, re, sys

DOC = os.environ.get("PORT_DOC") or os.path.expanduser("~/.config/opencode/FASE.md")
ITEM = re.compile(r"^[A-Z]\d+[a-z]?\.\s")


def sections(lines):
    out, cur = {}, None
    for ln in lines:
        m = re.match(r"^## (\S+)", ln)
        if m:
            cur = m.group(1); out[cur] = [ln]
        elif cur:
            out[cur].append(ln)
    return out


def main(argv):
    try:
        lines = open(DOC, encoding="utf-8").read().splitlines()
    except OSError as e:
        print("Panduan tidak ditemukan: %s (%s)" % (DOC, e)); return 1
    secs = sections(lines)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    cmd = argv[0]
    if cmd == "list":
        for k, v in secs.items():
            print("%-10s %s" % (k, v[0][3:].split(" - ", 1)[-1][:60]) + "  (%d baris)" % len(v))
        return 0
    if cmd == "find":
        w = " ".join(argv[1:]).lower(); n = 0
        cur = ""
        for ln in lines:
            m = re.match(r"^## (\S+)", ln)
            if m: cur = m.group(1)
            if w and w in ln.lower():
                print("[%s] %s" % (cur, ln.strip()[:120])); n += 1
                if n >= 20: print("... dipotong"); break
        if not n: print("tidak ada hasil")
        return 0
    key = next((k for k in secs if k.lower() == cmd.lower()), None)
    if not key:
        print("Bagian tidak ada. Pilihan: " + " ".join(secs)); return 1
    body = secs[key]
    if len(argv) == 1:
        print("\n".join(body)); return 0
    item = argv[1]
    pat = re.compile(r"^%s\.?\s" % re.escape(item))
    on, out = False, []
    for ln in body:
        if pat.match(ln): on = True
        elif on and (ITEM.match(ln) or ln.startswith("Selesai")): break
        if on: out.append(ln)
    print("\n".join(out) if out else "Butir '%s' tidak ada di %s." % (item, key))
    return 0 if out else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
