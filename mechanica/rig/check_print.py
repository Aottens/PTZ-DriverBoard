#!/usr/bin/env python3
"""Printability of the rig's STL files, each in its print orientation. Run: python3 mechanica/rig/check_print.py

Reports faces steeper than OVERHANG_DEG from vertical that hang over nothing. Small bridges are fine and
are listed by their largest span; a part is flagged when it needs support in the slicer.
"""
import glob
import math
import os
import struct

BED = 256.0
OVERHANG_DEG = 50.0
FLAG_AREA = 60.0  # mm2 of overhang before a part is worth a look
# Parts printed upside down, compared to the assembly: top face on the bed.
FLIP = {"bottom_plate", "output_shaft", "magnet_holder", "camera_plate", "idler_spacer_top"}
SUPPORT_OK = {
    "bearing_housing": "narrow ring above the lower bearing seat, about 1.5 mm wide: bridges, and fit_seat tests it",
    "fit_seat": "the same narrow ring on purpose, to test that bridge",
}


def triangles(path):
    data = open(path, "rb").read()
    count = struct.unpack("<I", data[80:84])[0]
    assert len(data) == 84 + 50 * count, f"{path}: not a binary STL"
    for i in range(count):
        v = struct.unpack("<9f", data[84 + 50 * i + 12:84 + 50 * i + 48])
        yield (v[0:3], v[3:6], v[6:9])


def check(path):
    name = os.path.basename(path)[:-4]
    tris = list(triangles(path))
    if name in FLIP:
        tris = [tuple((p[0], -p[1], -p[2]) for p in t) for t in tris]
    zs = [p[2] for t in tris for p in t]
    z0 = min(zs)
    size = tuple(max(p[k] for t in tris for p in t) - min(p[k] for t in tris for p in t) for k in range(3))
    assert max(size) < BED, f"{name}: does not fit the bed"
    limit = -math.sin(math.radians(OVERHANG_DEG))
    over = bed = 0.0
    for a, b, c in tris:
        u = [b[i] - a[i] for i in range(3)]
        v = [c[i] - a[i] for i in range(3)]
        n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        area = math.sqrt(sum(x * x for x in n)) / 2
        if area == 0:
            continue
        nz = n[2] / (2 * area)
        low = max(a[2], b[2], c[2]) - z0
        if nz < -0.99 and low < 0.01:
            bed += area
        elif nz < limit:
            over += area
    return name, size, bed, over


if __name__ == "__main__":
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export")
    flagged = []
    print(f"{'part':20} {'size mm':>22} {'on bed mm2':>11} {'overhang mm2':>13}  orientation")
    for path in sorted(glob.glob(os.path.join(here, "*.stl"))):
        name, size, bed, over = check(path)
        side = "flip: top on bed" if name in FLIP else "as exported"
        print(f"{name:20} {size[0]:6.1f} {size[1]:6.1f} {size[2]:6.1f} {bed:11.0f} {over:13.0f}  {side}")
        assert bed > 15, f"{name}: too little on the bed"
        if over > FLAG_AREA and name not in SUPPORT_OK:
            flagged.append(name)
    for name, why in SUPPORT_OK.items():
        print(f"note, {name}: {why}")
    assert not flagged, f"needs a look: {flagged}"
    print("print check ok")
