#!/usr/bin/env python3
"""Check the board in its working envelope, with every connector's mating plug and cable bend (BRD-07).

Run with KiCad's Python:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 hardware/check_fit.py

The envelope is the owner's brief (specs/modules/board.md): a base of 160 mm inner diameter, a 42 x 42 mm pan motor
centred 55.7 mm from the pan axis, the board flat beside it with its bottom long edge 1 mm from the motor's face,
25 mm of height above the board. The head itself does not exist yet, so this is all that can be checked.
Plug sizes are from the makers' drawings as far as I know them; each is written out below so it can be corrected.
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

# footprint name contains -> (kind, mated height or plug reach, cable bend, plug height for side entry)
PLUGS = {
    "JST_XH_B": ("top", 10.3, 8.0, 0),      # XHP housing seated in a B*B-XH-A header, then the wires bend over
    "JST_VH_B2P": ("top", 15.5, 8.0, 0),    # VHR housing on B2P-VH
    "JST_GH_BM": ("top", 6.0, 6.0, 0),      # GHR housing on a top-entry header
    "JST_GH_SM": ("side", 5.0, 8.0, 4.5),   # GHR housing sticks 5 mm out of a side-entry header
    "JST_SH_SM": ("side", 3.5, 6.0, 3.0),
    "USB_C_Receptacle": ("usb", 0, 0, 7.0),  # checked as a free corridor to the wall
}
TALL = {"CP_Elec_10x10": 10.5, "L_7.3x7.3": 4.5, "TO-252": 2.4, "ESP32-C6-MINI-1U": 2.4}
OUTWARD = {0: (0, 1), 90: (1, 0), 180: (0, -1), 270: (-1, 0)}   # mating direction of a side-entry part at each rotation
ANTENNA = (-4.9, -5.35)          # connector on the module, from its pad centre (datasheet v1.5 figure 10-2)


def main():
    board = pcbnew.LoadBoard(os.path.join(HERE, "ptz-driver.kicad_pcb"))
    edge = [p for d in board.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts for p in (d.GetStart(), d.GetEnd())]
    w = (max(p.x for p in edge) - min(p.x for p in edge)) / 1e6      # centre lines of the outline, not its stroke
    h = (max(p.y for p in edge) - min(p.y for p in edge)) / 1e6
    fails, boxes = [], []

    def base(x, y):
        """Board coordinates (origin top-left, y down) to base coordinates (origin on the pan axis, y away from the motor)."""
        return x - w / 2, (MOTOR[3] + GAP_TO_MOTOR + h) - y

    def check(ok, text):
        print(("ok    " if ok else "FAIL  ") + text)
        if not ok:
            fails.append(text)

    check(w <= 100.0 + 1e-6 and h <= 80.0 + 1e-6, f"outline {w:.1f} x {h:.1f} mm, at most 100 x 80 (BRD-04)")
    corners = [base(0, 0), base(w, 0), base(w, h), base(0, h)]
    check(all(math.hypot(*c) < R_WALL for c in corners), f"board corners inside the base, farthest at {max(math.hypot(*c) for c in corners):.1f} of {R_WALL} mm")
    left = min(math.sqrt(R_WALL ** 2 - y ** 2) - abs(base(0, 0)[0]) for y in (corners[0][1], corners[3][1]))
    top = min(math.sqrt(R_WALL ** 2 - x ** 2) - corners[0][1] for x in (corners[0][0], corners[1][0]))
    check(left >= EDGE_TO_WALL_MIN and top >= EDGE_TO_WALL_MIN, f"free edges to the wall: short edges {left:.1f} mm, far long edge {top:.1f} mm, at least {EDGE_TO_WALL_MIN}")

    usb = antenna = None
    for fp in board.GetFootprints():
        name, ref = fp.GetFPID().GetLibItemName().wx_str(), fp.GetReference()
        rot = round(fp.GetOrientationDegrees()) % 360
        cy = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
        x0, y0, x1, y1 = (cy.GetLeft() / 1e6 - OX, cy.GetTop() / 1e6 - OY, cy.GetRight() / 1e6 - OX, cy.GetBottom() / 1e6 - OY)
        for key, height in TALL.items():
            if key in name:
                boxes.append((ref, x0, y0, x1, y1, 0, height, "part"))
        if "ESP32" in name:
            px, py = fp.GetPosition().x / 1e6 - OX, fp.GetPosition().y / 1e6 - OY
            c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
            antenna = (px + ANTENNA[0] * c + ANTENNA[1] * s, py - ANTENNA[0] * s + ANTENNA[1] * c)
        for key, (kind, reach, bend, ph) in PLUGS.items():
            if key not in name:
                continue
            if kind == "top":
                boxes.append((ref, x0, y0, x1, y1, 0, reach + bend, "plug"))
            else:
                dx, dy = OUTWARD[rot]
                near_edge = (dx < 0 and x0 < 3) or (dx > 0 and x1 > w - 3) or (dy < 0 and y0 < 3) or (dy > 0 and y1 > h - 3)
                check(near_edge and dy <= 0, f"{ref}: side-entry connector faces a free edge and not the motor side (BRD-02)")
                if kind == "usb":
                    usb = (ref, x0, y0, x1, y1, dx, dy, ph)
                    continue
                out = reach + bend
                bx = (x0 + min(dx, 0) * out, y0 + min(dy, 0) * out, x1 + max(dx, 0) * out, y1 + max(dy, 0) * out)
                boxes.append((ref, *bx, 0, max(ph, 3.0), "plug"))

    def lifted(z):
        return z + 1.6    # heights are from the board's top face; nothing below it is modelled

    for ref, x0, y0, x1, y1, z0, z1, kind in boxes:
        pts = [base(x0, y0), base(x1, y0), base(x1, y1), base(x0, y1)]
        r = max(math.hypot(*p) for p in pts)
        in_motor = any(MOTOR[0] < p[0] < MOTOR[2] and MOTOR[1] < p[1] < MOTOR[3] for p in pts)
        if kind == "plug" or r >= R_WALL or z1 > HEIGHT_MAX or in_motor:
            check(r < R_WALL and z1 <= HEIGHT_MAX and not in_motor,
                  f"{ref}: {kind} box reaches radius {r:.1f} of {R_WALL} mm and height {z1:.1f} of {HEIGHT_MAX} mm, clear of the motor")
    plugs = [b for b in boxes if b[7] == "plug"]
    clash = [(a[0], b[0]) for i, a in enumerate(plugs) for b in plugs[i + 1:]
             if a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4] and a[5] < b[6] and b[5] < a[6]]
    check(not clash, "no two plugs share space" + (": " + ", ".join(f"{a}/{b}" for a, b in clash) if clash else ""))

    # a screwdriver must come straight down onto each mounting screw: nothing tall within 4 mm of a hole's centre
    for fp in board.GetFootprints():
        if "MountingHole" in fp.GetFPID().GetLibItemName().wx_str():
            hx, hy = fp.GetPosition().x / 1e6 - OX, fp.GetPosition().y / 1e6 - OY
            close = [b[0] for b in boxes if b[6] > 3.0 and b[1] - 4.0 < hx < b[3] + 4.0 and b[2] - 4.0 < hy < b[4] + 4.0]
            check(not close, f"{fp.GetReference()}: a driver reaches the screw from above" + (f"; in the way: {close}" if close else ""))

    if usb:
        ref, x0, y0, x1, y1, dx, dy, ph = usb
        cx, cyy = (x0 + x1) / 2, (y0 + y1) / 2
        half = 6.5   # half the width of a USB-C plug's overmould
        # corridor from the socket to the wall, straight along the plug axis
        cor = (min(cx, cx + dx * 100) - half * abs(dy), min(cyy, cyy + dy * 100) - half * abs(dx),
               max(cx, cx + dx * 100) + half * abs(dy), max(cyy, cyy + dy * 100) + half * abs(dx))
        blocked = [b[0] for b in boxes if b[0] != ref and b[1] < cor[2] and cor[0] < b[3] and b[2] < cor[3] and cor[1] < b[4]
                   and ((dx < 0 and b[3] <= x0) or (dx > 0 and b[1] >= x1) or (dy < 0 and b[4] <= y0))]
        mouth = base(x0 if dx < 0 else x1, cyy) if dx else base(cx, y0)
        to_wall = math.sqrt(R_WALL ** 2 - (mouth[1] if dx else mouth[0]) ** 2) - abs(mouth[0] if dx else mouth[1])
        check(not blocked, f"{ref}: USB-C has a free straight path to the wall, {to_wall:.0f} mm away" + (f"; blocked by {blocked}" if blocked else ""))
    if antenna:
        ax, ay = antenna
        over = [b[0] for b in boxes if b[7] == "plug" and b[1] - 3 < ax < b[3] + 3 and b[2] - 3 < ay < b[4] + 3]
        bx, by = base(ax, ay)
        check(not over, f"antenna connector at ({ax:.1f}, {ay:.1f}) on the board is free above, {R_WALL - math.hypot(bx, by):.0f} mm from the wall" + (f"; under {over}" if over else ""))

    print(f"\n{len(boxes)} boxes checked, {len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
