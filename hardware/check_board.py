#!/usr/bin/env python3
"""Check every number specs/modules/board.md states about the board, and run ERC and DRC (BRD-01 to BRD-11).

Run with KiCad's Python:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 hardware/check_board.py
Each function is named after its criterion. Exit code 0 only when all pass.
"""
import json
import math
import os
import re
import subprocess
import sys
import tempfile

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.join(HERE, "ptz-driver.kicad_pcb")
SCH = os.path.join(HERE, "ptz-driver.kicad_sch")
CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
OX = OY = 100.0
board = pcbnew.LoadBoard(PCB)
fails = []


def xy(v):
    return v.x / 1e6 - OX, v.y / 1e6 - OY


def check(ok, text):
    print(("ok    " if ok else "FAIL  ") + text)
    if not ok:
        fails.append(text)


def outline():
    pts = [p for d in board.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts for p in (d.GetStart(), d.GetEnd())]
    xs, ys = [p.x / 1e6 - OX for p in pts], [p.y / 1e6 - OY for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


TRACKS = [t for t in board.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
VIAS = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
FPS = {fp.GetReference(): fp for fp in board.GetFootprints()}
X0, Y0, X1, Y1 = outline()


def brd_01_outline_and_holes():
    w, h = X1 - X0, Y1 - Y0
    check(w <= 85.0 + 1e-6 and h <= 65.0 + 1e-6, f"BRD-01/04 outline {w:.2f} x {h:.2f} mm, at most 85 x 65")
    holes = [(xy(p.GetPosition()), p.GetDrillSize().x / 1e6, p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH)
             for fp in FPS.values() if fp.GetReference().startswith("H") for p in fp.Pads()]
    want = {(4.0, 4.0), (w - 4.0, 4.0), (4.0, h - 4.0), (w - 4.0, h - 4.0)}
    got = {(round(p[0], 2), round(p[1], 2)) for p, _, _ in holes}
    check(got == want and all(abs(d - 3.2) < 0.01 and npth for _, d, npth in holes),
          f"BRD-01 four 3.2 mm unplated holes 4.0 mm from the edges: {sorted(got)}")
    near = []
    for (hx, hy), _, _ in holes:
        for fp in FPS.values():
            if fp.GetReference().startswith("H"):
                continue
            for p in fp.Pads():
                b = p.GetBoundingBox()
                cx = min(max(hx, b.GetLeft() / 1e6 - OX), b.GetRight() / 1e6 - OX)
                cy = min(max(hy, b.GetTop() / 1e6 - OY), b.GetBottom() / 1e6 - OY)
                if math.hypot(cx - hx, cy - hy) < 3.5:
                    near.append(f"{fp.GetReference()}.{p.GetNumber()}")
        for t in TRACKS:
            if t.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu):
                (ax, ay), (bx, by) = xy(t.GetStart()), xy(t.GetEnd())
                dx, dy = bx - ax, by - ay
                k = 0 if dx == dy == 0 else max(0, min(1, ((hx - ax) * dx + (hy - ay) * dy) / (dx * dx + dy * dy)))
                if math.hypot(hx - ax - k * dx, hy - ay - k * dy) - t.GetWidth() / 2e6 < 3.5:
                    near.append(f"track {t.GetNetname()}")
        near += [f"via {v.GetNetname()}" for v in VIAS if math.hypot(xy(v.GetPosition())[0] - hx, xy(v.GetPosition())[1] - hy) < 3.5 + 0.3]
    check(not near, "BRD-01 a 7.0 mm circle around each hole is free of pads, tracks and vias" + (f": {sorted(set(near))[:8]}" if near else ""))


def brd_02_all_parts_on_top():
    flipped = [r for r, fp in FPS.items() if fp.IsFlipped()]
    check(not flipped, f"BRD-02 every part is on the top side ({len(FPS)} footprints)" + (f": {flipped}" if flipped else ""))
    bad = []
    for r, fp in FPS.items():
        name = fp.GetFPID().GetLibItemName().wx_str()
        if "Horizontal" in name or "USB_C" in name:
            c = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
            edge = min(c.GetLeft() / 1e6 - OX - X0, X1 - (c.GetRight() / 1e6 - OX), c.GetTop() / 1e6 - OY - Y0)
            bottom = Y1 - (c.GetBottom() / 1e6 - OY)
            if edge > 1.0 or bottom < 1.0:
                bad.append(r)
    check(not bad, "BRD-02 side-entry connectors sit on the left, top or right edge, none on the motor side" + (f": {bad}" if bad else ""))


def brd_03_layers():
    check(board.GetCopperLayerCount() == 4, f"BRD-03 four copper layers (is {board.GetCopperLayerCount()})")
    zones = [(z.GetLayer(), z.GetNetname(), z.Outline().BBox()) for z in board.Zones() if not z.GetIsRuleArea()]
    gnd = [b for layer, net, b in zones if layer == pcbnew.In1_Cu and net == "GND"]
    check(len(gnd) == 1 and gnd[0].GetWidth() / 1e6 >= X1 - X0 - 0.01 and gnd[0].GetHeight() / 1e6 >= Y1 - Y0 - 0.01
          and not [1 for layer, net, _ in zones if layer == pcbnew.In1_Cu and net != "GND"]
          and not [t for t in TRACKS if t.GetLayer() == pcbnew.In1_Cu],
          "BRD-03 inner layer 1 is one ground plane over the whole board, with no tracks in it")
    in2 = sorted({net for layer, net, _ in zones if layer == pcbnew.In2_Cu})
    check(set(in2) <= {"VM", "+3V3", "+5V"} and "VM" in in2 and "+3V3" in in2, f"BRD-03 inner layer 2 holds supply planes only: {in2}")


def brd_05_design_rules():
    wmin = min(t.GetWidth() for t in TRACKS) / 1e6 if TRACKS else 0
    check(wmin >= 0.15 - 1e-6, f"BRD-05 narrowest track {wmin:.2f} mm, at least 0.15")
    dmin = min(v.GetDrill() for v in VIAS) / 1e6
    pmin = min(v.GetWidth(pcbnew.F_Cu) for v in VIAS) / 1e6
    check(dmin >= 0.3 - 1e-6 and pmin >= 0.6 - 1e-6, f"BRD-05 smallest via {pmin:.2f} mm with {dmin:.2f} mm drill, at least 0.6 and 0.3")
    pro = json.load(open(os.path.join(HERE, "ptz-driver.kicad_pro")))["board"]["design_settings"]["rules"]
    check(pro["min_clearance"] >= 0.15 and pro["min_track_width"] >= 0.15 and pro["min_copper_edge_clearance"] >= 0.3
          and pro["min_via_diameter"] >= 0.6 and pro["min_through_hole_diameter"] >= 0.3,
          f"BRD-05 the DRC itself runs with gap {pro['min_clearance']}, track {pro['min_track_width']}, edge {pro['min_copper_edge_clearance']}, via {pro['min_via_diameter']}/{pro['min_through_hole_diameter']} mm")


def brd_06_current_paths():
    # motor outputs: 0.6 mm or more, except the neck where a track leaves the driver's 0.25 mm pads
    thin = []
    for t in TRACKS:
        m = re.fullmatch(r"M(\d)_[AB][12]", t.GetNetname())
        if m and t.GetWidth() / 1e6 < 0.6 - 1e-6:
            u = FPS[f"U{int(m.group(1)) + 2}01"]
            ux, uy = xy(u.GetPosition())
            far = max(math.hypot(p[0] - ux, p[1] - uy) for p in (xy(t.GetStart()), xy(t.GetEnd())))
            if far > 5.0:
                thin.append(f"{t.GetNetname()} {t.GetWidth() / 1e6:.2f} mm at {xy(t.GetStart())}")
    check(not thin, "BRD-06 motor outputs are 0.6 mm or wider beyond 5 mm from the driver's centre" + (f": {thin[:6]}" if thin else ""))
    # input current path: a pour per net on the top layer that still joins its pads after shrinking by 1.5 mm
    for net, pads in (("VIN_RAW", ("J101.1", "Q101.2")), ("VIN", ("Q101.3", "F101.1")), ("VM", ("F101.2", "D102.1"))):
        zones = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname() == net and z.GetLayer() == pcbnew.F_Cu]
        ok = False
        if zones:
            poly = pcbnew.SHAPE_POLY_SET(zones[0].GetFilledPolysList(pcbnew.F_Cu))
            pos = []
            for name in pads:
                ref, num = name.split(".")
                pos.append([p for p in FPS[ref].Pads() if p.GetNumber() == num][0].GetPosition())
            ok = all(poly.Contains(p, -1, pcbnew.FromMM(0.5)) for p in pos)
        check(ok, f"BRD-06 {net}: a top-layer pour joins {pads[0]} and {pads[1]}")
    vm_vias = [v for v in VIAS if v.GetNetname() == "VM" and v.GetDrill() / 1e6 >= 0.4 - 1e-6]
    check(len(vm_vias) >= 6, f"BRD-06 VM goes from its pour to the plane through {len(vm_vias)} vias of 0.4 mm drill, at least 6 (about 2 A each)")
    for net in ("+5V", "VSYS", "VIN_L", "+5V_EXT", "+3V3_SNS"):
        w = [t.GetWidth() / 1e6 for t in TRACKS if t.GetNetname() == net]
        check(bool(w) and min(w) >= 0.4 - 1e-6, f"BRD-06 {net} tracks are {min(w) if w else 0:.2f} mm or wider, at least 0.4")


def brd_09_silkscreen():
    texts = [d.GetText() for d in board.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() == pcbnew.F_SilkS]
    back = [d.GetText() for d in board.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() == pcbnew.B_SilkS]
    name = [t for t in texts + back if "PTZ" in t and "REV A" in t and re.search(r"20\d\d-\d\d-\d\d", t)]
    check(len(name) >= 1, "BRD-09 board name, revision and date are on the silkscreen")
    need = ["12-24V", "+", "-", "M1", "M2", "M3", "M4", "S1", "S2", "S3", "S4", "X1", "X2", "X3", "X4", "ETH", "RS485", "CAN",
            "CAM", "FAN", "USB", "I2C", "T485", "TCAN", "5V", "VM", "BOOT", "LINK", "ACT", "STAT"]
    missing = [n for n in need if n not in texts]
    check(not missing, "BRD-09 every connector, jumper, LED and button is named on the top side" + (f"; missing {missing}" if missing else ""))
    tps = [fp for r, fp in FPS.items() if r.startswith("TP")]
    check(len([t for t in texts if t in ("VIN", "VM", "5V", "VSYS", "3V3", "GND", "SCK", "MOSI", "MISO", "SDA", "SCL", "ENN", "XINT",
                                         "CSD", "CSS", "XP15", "CTX", "CRX", "RTX", "RRX", "EN")]) >= len(tps),
          f"BRD-09 all {len(tps)} test points are named")
    legend = " ".join(back)
    check(all(k in legend for k in ("MOTOR", "SENSOR", "EXT DRIVER", "ETH", "RS485", "CAN", "CAM", "FAN", "I2C", "HOME", "STEP")),
          "BRD-09 the pin order of every port is printed on the bottom side")
    small = [d.GetText() for d in board.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)
             and (d.GetTextHeight() / 1e6 < 0.8 - 1e-6 or d.GetTextThickness() / 1e6 < 0.15 - 1e-6)]
    check(not small, "BRD-09 no text smaller than 0.8 mm high with a 0.15 mm stroke" + (f": {small[:5]}" if small else ""))


def brd_11_driver_heat_path():
    for ref, fp in sorted(FPS.items()):
        if not fp.GetValue().startswith("TMC5240"):
            continue
        x, y = xy(fp.GetPosition())
        inside = [v for v in VIAS if abs(xy(v.GetPosition())[0] - x) <= 1.6 and abs(xy(v.GetPosition())[1] - y) <= 1.6]
        check(len(inside) >= 9 and all(v.GetNetname() == "GND" for v in inside), f"BRD-11 {ref}: {len(inside)} ground vias under the exposed pad, at least 9")
        window = [d for d in board.GetDrawings() if d.GetLayer() == pcbnew.B_Mask and d.GetBoundingBox().Contains(fp.GetPosition())]
        size = min(window[0].GetBoundingBox().GetWidth(), window[0].GetBoundingBox().GetHeight()) / 1e6 if window else 0
        foreign = [v.GetNetname() for v in VIAS if v.GetNetname() != "GND" and abs(xy(v.GetPosition())[0] - x) < 2.8 + 0.3 and abs(xy(v.GetPosition())[1] - y) < 2.8 + 0.3]
        foreign += [t.GetNetname() for t in TRACKS if t.GetLayer() == pcbnew.B_Cu and t.GetNetname() != "GND"
                    and min(abs(xy(p)[0] - x) for p in (t.GetStart(), t.GetEnd())) < 2.8 and min(abs(xy(p)[1] - y) for p in (t.GetStart(), t.GetEnd())) < 2.8]
        check(size >= 5.5 and not foreign, f"BRD-11 {ref}: bare bottom window {size:.1f} mm square with ground copper only" + (f"; other nets {sorted(set(foreign))}" if foreign else ""))


def brd_10_erc_drc():
    tmp = tempfile.mkdtemp()
    subprocess.run([CLI, "sch", "erc", "--format", "json", "--severity-all", "-o", f"{tmp}/erc.json", SCH], capture_output=True)
    erc = json.load(open(f"{tmp}/erc.json"))
    n = sum(len(s.get("violations", [])) for s in erc.get("sheets", []))
    check(n == 0, f"BRD-10 ERC: {n} violations")
    subprocess.run([CLI, "pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity", "-o", f"{tmp}/drc.json", PCB], capture_output=True)
    drc = json.load(open(f"{tmp}/drc.json"))
    for key, label in (("violations", "violations"), ("unconnected_items", "unconnected items"), ("schematic_parity", "schematic parity issues")):
        items = drc.get(key, [])
        kinds = {}
        for v in items:
            kinds[v["type"]] = kinds.get(v["type"], 0) + 1
        check(not items, f"BRD-10 DRC: {len(items)} {label}" + (f" {kinds}" if kinds else ""))
    print("      DRC checks switched off in the project, each with its reason in tools/project.py: " +
          ", ".join(sorted(c["key"] if isinstance(c, dict) else str(c) for c in drc.get("ignored_checks", []))))


if __name__ == "__main__":
    for f in (brd_01_outline_and_holes, brd_02_all_parts_on_top, brd_03_layers, brd_05_design_rules, brd_06_current_paths,
              brd_09_silkscreen, brd_11_driver_heat_path, brd_10_erc_drc):
        f()
    print(f"\n{len(fails)} failures")
    sys.exit(1 if fails else 0)
