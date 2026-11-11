#!/usr/bin/env python3
"""Check the Rev B board in its working envelope, with every module, heat sink, connector, mating plug and cable
bend as a box (BRD-07).

Run with KiCad's Python:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 hardware/check_fit.py

The envelope is the owner's brief (specs/modules/board.md): a base of 160 mm inner diameter, a 42 x 42 mm pan motor
centred 55.7 mm from the pan axis, the board flat beside it with its south edge 1 mm from the motor's face, 25 mm of
height above the board. The head itself does not exist yet, so this is all that can be checked.
Every height below names where it comes from, so it can be corrected; heights are above the board's top face.
"""
import math
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
R_WALL = 80.0                    # mm, inner radius of the base
MOTOR = (-21.0, -76.7, 21.0, -34.7)   # x0, y0, x1, y1 in base coordinates: 42 mm square centred at (0, -55.7)
GAP_TO_MOTOR = 1.0
HEIGHT_MAX = 25.0
EDGE_TO_WALL_MIN = 10.0
OX, OY = 100.0, 100.0            # board origin on the KiCad sheet (tools/board.py)

SOCKET = 8.5                     # an ordinary 2.54 mm female header
SPACER = 2.54                    # the plastic of the module's own pin header, between socket and module
PCB = 1.6
# module footprint -> (how it is mounted, what stands on its board, that height, source)
MODULES = {
    "StepStick_Socket": ("socket", "heat sink", 12.0, "assumption: BIGTREETECH gives no heat-sink height; the tall ones sold with these modules are about 12 mm"),
    "ESP32-S3-DevKitC-1": ("socket", "module can and USB sockets", 3.3, "ESP32-S3-WROOM-1U is 3.2 mm tall (datasheet v1.8, figure 10-1); USB-C sockets about 3.3 mm"),
    "WIZ850io": ("soldered", "RJ45 jack with its tab", 15.61, "WIZnet datasheet V1.0 p10: jack 13.61 mm plus a 2.0 mm tab"),
}
# footprint name starts with -> (height of part with its plug and cable bend, source)
PARTS = {
    "JST_XH_B": (9.8 + 8.0, "JST XH: 9.8 mm mounted with its housing (eXH.pdf), plus 8 mm for the wires to bend over"),
    "JST_VH_B2P": (16.5 + 8.0, "JST VH: 16.5 mm mounted (eVH.pdf), plus 8 mm bend"),
    "JST_PH_B": (8.0 + 6.0, "JST PH: 8 mm mounted (ePH.pdf), plus 6 mm bend"),
    "PinHeader_1x": (2.5 + 14.0 + 6.0, "2.54 mm header: 2.5 mm base, a 14 mm crimp housing, 6 mm bend"),
    "CP_Radial_D6.3": (11.5, "100 uF 35 V, 6.3 x 11 mm"),
    "Fuseholder_TR5": (10.5, "TR5 fuse, 8 mm, in a holder; 8 mm soldered in"),
    "SIP3_DCDC": (17.5, "Mornsun K7805-1000R3, the taller of the two named: 17.5 mm; Traco TSR 1-2450 10.2 mm"),
    "TO-252": (2.4, ""), "D_SMB": (2.5, ""), "D_SMA": (2.4, ""),
}
ANTENNA = (22.86 / 2, -1.0)      # the U.FL connector on the module, from the footprint's pad 1: near the antenna end, mid-width (estimate)


def main():
    board = pcbnew.LoadBoard(os.path.join(HERE, "ptz-driver.kicad_pcb"))
    edge = [p for d in board.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts for p in (d.GetStart(), d.GetEnd())]
    w = (max(p.x for p in edge) - min(p.x for p in edge)) / 1e6      # centre lines of the outline, not its stroke
    h = (max(p.y for p in edge) - min(p.y for p in edge)) / 1e6
    fails, boxes = [], []         # box: (ref, x0, y0, x1, y1, z0, z1, kind)

    def base(x, y):
        """Board coordinates (origin top-left, y south) to base coordinates (origin on the pan axis, y away from the motor)."""
        return x - w / 2, (MOTOR[3] + GAP_TO_MOTOR + h) - y

    def check(ok, text):
        print(("ok    " if ok else "FAIL  ") + text)
        if not ok:
            fails.append(text)

    def rect(b):
        return (b.GetLeft() / 1e6 - OX, b.GetTop() / 1e6 - OY, b.GetRight() / 1e6 - OX, b.GetBottom() / 1e6 - OY)

    check(w <= 100.0 + 1e-6 and h <= 80.0 + 1e-6, f"outline {w:.1f} x {h:.1f} mm, at most 100 x 80 (BRD-04)")
    corners = [base(0, 0), base(w, 0), base(w, h), base(0, h)]
    check(all(math.hypot(*c) < R_WALL for c in corners), f"board corners inside the base, farthest at {max(math.hypot(*c) for c in corners):.1f} of {R_WALL} mm")
    free = min(R_WALL - math.hypot(*c) for c in corners)
    check(free >= EDGE_TO_WALL_MIN, f"nearest board corner to the wall: {free:.1f} mm, at least {EDGE_TO_WALL_MIN}")

    usb = jack = antenna = None
    for fp in board.GetFootprints():
        name, ref = fp.GetFPID().GetLibItemName().wx_str(), fp.GetReference()
        if name in MODULES:
            how, what, top, _ = MODULES[name]
            fab = [rect(g.GetBoundingBox()) for g in fp.GraphicalItems() if g.GetLayer() == pcbnew.F_Fab and g.GetClass() == "PCB_SHAPE"]
            b = (min(r[0] for r in fab), min(r[1] for r in fab), max(r[2] for r in fab), max(r[3] for r in fab))
            z0 = (SOCKET if how == "socket" else 0.0) + SPACER
            boxes.append((ref, *b, z0, z0 + PCB + top, f"module, {how}, with its {what}"))
            if name == "WIZ850io":
                jack = (ref, b, z0 + PCB + top, SOCKET + SPACER + PCB + top)
            if name == "ESP32-S3-DevKitC-1":
                usb = (ref, b)
                p1 = [p for p in fp.Pads() if p.GetNumber() == "1"][0].GetPosition()
                rot = round(fp.GetOrientationDegrees()) % 360
                c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
                antenna = (p1.x / 1e6 - OX + ANTENNA[0] * c + ANTENNA[1] * s, p1.y / 1e6 - OY - ANTENNA[0] * s + ANTENNA[1] * c, z0 + PCB + top)
            continue
        for key, (top, _) in PARTS.items():
            if name.startswith(key):
                boxes.append((ref, *rect(fp.GetCourtyard(pcbnew.F_CrtYd).BBox()), 0.0, top, "part with its plug" if "JST" in key or "Header" in key else "part"))

    for ref, x0, y0, x1, y1, z0, z1, kind in boxes:
        pts = [base(x0, y0), base(x1, y0), base(x1, y1), base(x0, y1)]
        r = max(math.hypot(*p) for p in pts)
        in_motor = any(MOTOR[0] < p[0] < MOTOR[2] and MOTOR[1] < p[1] < MOTOR[3] for p in pts)
        if z1 > 14.0 or r >= R_WALL or in_motor:
            check(r < R_WALL and z1 <= HEIGHT_MAX and not in_motor,
                  f"{ref}: {kind}: top at {z1:.1f} of {HEIGHT_MAX} mm, radius {r:.1f} of {R_WALL} mm, clear of the motor")
    print(f"      ({len([b for b in boxes if b[6] <= 14.0])} lower boxes are inside the base and under 14 mm)")
    clash = [(a[0], b[0]) for i, a in enumerate(boxes) for b in boxes[i + 1:]
             if a[1] < b[3] - 0.01 and b[1] < a[3] - 0.01 and a[2] < b[4] - 0.01 and b[2] < a[4] - 0.01 and a[5] < b[6] and b[5] < a[6]]
    check(not clash, "no two boxes share space" + (": " + ", ".join(f"{a}/{b}" for a, b in clash) if clash else ""))

    # a screwdriver must come straight down onto each mounting screw: nothing tall inside the 7 mm circle, and a
    # 6 mm wide shaft free above it
    for fp in board.GetFootprints():
        if "MountingHole" in fp.GetFPID().GetLibItemName().wx_str():
            hx, hy = fp.GetPosition().x / 1e6 - OX, fp.GetPosition().y / 1e6 - OY
            close = [b[0] for b in boxes if b[6] > 3.0 and math.hypot(min(max(hx, b[1]), b[3]) - hx, min(max(hy, b[2]), b[4]) - hy) < 3.0]
            check(not close, f"{fp.GetReference()}: a driver reaches the screw from above" + (f"; in the way: {close}" if close else ""))

    if usb:
        ref, b = usb
        mouth = base(b[0], (b[1] + b[3]) / 2)
        to_wall = math.sqrt(R_WALL ** 2 - mouth[1] ** 2) - abs(mouth[0])
        blocked = [x[0] for x in boxes if x[0] != ref and x[3] <= b[0] + 0.5 and x[2] < b[3] and b[1] < x[4] and x[6] > 8.0]
        check(b[0] < 1.0 and not blocked, f"{ref}: the USB sockets are at the west edge with a free way out; the wall is {to_wall:.0f} mm from them"
              + (f"; blocked by {blocked}" if blocked else ""))
    if jack:
        ref, b, top, top_socketed = jack
        mouth = base(b[2], (b[1] + b[3]) / 2)
        to_wall = math.sqrt(R_WALL ** 2 - mouth[1] ** 2) - abs(mouth[0])
        check(b[2] > w - 1.0, f"{ref}: the RJ45 jack opens at the east edge; the wall is {to_wall:.0f} mm from its face")
        check(top <= HEIGHT_MAX < top_socketed, f"{ref}: soldered in, the jack's tab is at {top:.1f} mm; on 8.5 mm sockets it would be at {top_socketed:.1f} mm, over the {HEIGHT_MAX} mm")
    if antenna:
        ax, ay, az = antenna
        over = [b[0] for b in boxes if b[5] > az and b[1] - 3 < ax < b[3] + 3 and b[2] - 3 < ay < b[4] + 3]
        bx, by = base(ax, ay)
        check(not over and az + 6.0 <= HEIGHT_MAX, f"antenna connector at ({ax:.1f}, {ay:.1f}) on the board, {az:.1f} mm up: free above, {R_WALL - math.hypot(bx, by):.0f} mm from the wall"
              + (f"; under {over}" if over else ""))

    print(f"\n{len(boxes)} boxes checked, {len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
