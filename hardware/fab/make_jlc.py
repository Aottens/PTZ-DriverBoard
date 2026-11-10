#!/usr/bin/env python3
"""JLC BOM and CPL for the PTZ driver board. Rerun after every board change.

Run with KiCad's Python, from hardware/:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 fab/make_jlc.py

Every footprint that carries an LCSC number goes into the BOM and the CPL; the number is a field copied from the
schematic symbol, so there is no parts table here. Rotation and centre are fitted per part onto the pads of the
EasyEDA footprint that JLC itself uses (source: the EasyEDA library, https://easyeda.com), so JLC's preview is right
however the KiCad footprint is drawn. A part whose pads do not land on JLC's within FIT_MAX stops the script:
that is a wrong footprint, not a rotation.
"""
import csv
import json
import math
import os
import subprocess
import sys
import time

import pcbnew

HW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HW, "fab", "jlc")
CACHE = os.path.join(HW, "fab", "easyeda_cache.json")
FIT_MAX = 0.35      # mm, largest pad-centre distance accepted
_cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}


def mean(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def eda_pads(lcsc):
    """Pad centres (mm, y down) of JLC's footprint per pad number, or None when JLC's library has no part for it."""
    if lcsc not in _cache:
        url = f"https://easyeda.com/api/products/{lcsc}/components?version=6.4.19.5"
        for attempt in range(5):
            time.sleep(1.5 if attempt == 0 else 40)     # the API answers with an HTML page when asked too fast
            raw = subprocess.run(["curl", "-s", "-m", "30", url], capture_output=True, text=True).stdout
            if raw.lstrip().startswith("{"):
                break
        else:
            raise SystemExit(f"{lcsc}: the EasyEDA API does not answer, try again later")
        data = json.loads(raw)
        if not data.get("success", True) or "result" not in data:
            _cache[lcsc] = None
        else:
            ds = data["result"]["packageDetail"]["dataStr"]
            hx, hy = float(ds["head"]["x"]), float(ds["head"]["y"])
            pads = {}
            for s in ds["shape"]:
                if s.startswith("PAD"):
                    f = s.split("~")
                    pads.setdefault(f[8], []).append(((float(f[2]) - hx) * 0.254, (float(f[3]) - hy) * 0.254))
            _cache[lcsc] = {"title": data["result"]["packageDetail"]["title"], "pads": {n: mean(v) for n, v in pads.items()}}
        json.dump(_cache, open(CACHE, "w"), indent=0, sort_keys=True)
    return {n: tuple(p) for n, p in _cache[lcsc]["pads"].items()} if _cache[lcsc] else None


def rot(p, a):  # counter-clockwise as seen, y down
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return (p[0] * c + p[1] * s, -p[0] * s + p[1] * c)


def fit(fp, lcsc):
    """JLC rotation and centre that put JLC's footprint onto the KiCad pads. Returns (rotation, centre, error, how)."""
    eda = eda_pads(lcsc)
    if eda is None:
        return fp.GetOrientationDegrees() % 360, (fp.GetPosition().x / 1e6, fp.GetPosition().y / 1e6), 0.0, "KiCad"
    allpads = [(p.GetPosition().x / 1e6, p.GetPosition().y / 1e6) for p in fp.Pads() if p.GetNumber()]
    mine = {}
    for p in fp.Pads():
        if p.GetNumber():
            mine.setdefault(p.GetNumber(), []).append((p.GetPosition().x / 1e6, p.GetPosition().y / 1e6))
    mine = {n: mean(v) for n, v in mine.items()}
    common = [n for n in mine if n in eda]
    plugin = fp.GetOrientationDegrees() % 360
    best = None
    for by_number in (True, False):   # by pad number first; if the numbering differs, by geometry
        if by_number and len(common) < max(2, min(len(mine), len(eda)) - 2):
            continue
        for r in (0, 90, 180, 270):
            if by_number:
                t = {n: rot(eda[n], r) for n in common}
                m = mean([(mine[n][0] - t[n][0], mine[n][1] - t[n][1]) for n in common])
                err = max(math.dist(mine[n], (t[n][0] + m[0], t[n][1] + m[1])) for n in common)
            else:
                t = [rot(e, r) for e in eda.values()]
                m = tuple(a - b for a, b in zip(mean(allpads), mean(t)))
                err = max(min(math.dist((q[0] + m[0], q[1] + m[1]), p) for p in allpads) for q in t)
            key = (round(err, 2), r != round(plugin) % 360)   # on a tie (symmetric part) keep KiCad's own angle
            if best is None or key < best[0]:
                best = (key, r, m, err, "number" if by_number else "geometry")
        if best and best[3] < FIT_MAX:
            break
    return best[1:]


def main():
    board = pcbnew.LoadBoard(os.path.join(HW, "ptz-driver.kicad_pcb"))
    rows, groups, bad = [], {}, []
    for fp in sorted(board.GetFootprints(), key=lambda f: (f.GetReference().rstrip("0123456789"), int("".join(c for c in f.GetReference() if c.isdigit()) or 0))):
        lcsc = fp.GetFieldText("LCSC") if fp.HasField("LCSC") else ""
        if not lcsc:
            continue
        assert not fp.IsFlipped(), f"{fp.GetReference()} is on the bottom: Economic assembly is top side only"
        r, m, err, how = fit(fp, lcsc)
        title = _cache[lcsc]["title"] if _cache[lcsc] else "NOT IN JLC'S FOOTPRINT LIBRARY: check this part in the preview"
        if err >= FIT_MAX:
            bad.append(f"{fp.GetReference()} {lcsc}: JLC's footprint ({title}) is {err:.2f} mm off")
        ref = fp.GetReference()
        rows.append((ref, f"{m[0]:.3f}mm", f"{-m[1]:.3f}mm", "Top", r))
        g = groups.setdefault(lcsc, ([], fp.GetFPID().GetLibItemName().wx_str(), []))      # one line per part number
        g[0].append(fp.GetValue()) if fp.GetValue() not in g[0] else None
        g[2].append(ref)
        print(f"{ref:6} {lcsc:10} rot {r:3.0f}  fit {err:.2f} mm by {how:8}  {title}")
    if bad:
        raise SystemExit("\n".join(bad))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "ptz-driver_cpl.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        w.writerows(rows)
    with open(os.path.join(OUT, "ptz-driver_bom.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for lcsc, (values, name, refs) in groups.items():
            w.writerow([" / ".join(values), ",".join(refs), name, lcsc])
    print(f"{len(rows)} parts, {len(groups)} BOM lines")


if __name__ == "__main__":
    sys.exit(main())
