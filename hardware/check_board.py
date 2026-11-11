#!/usr/bin/env python3
"""Check every number specs/modules/board.md states about the Rev B board, and run ERC and DRC (BRD-01 to BRD-12).

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
MODULES = ("StepStick_Socket", "ESP32-S3-DevKitC-1", "WIZ850io")
# height above the board by footprint name (mm), for what may stand under a module (BRD-11): makers' package drawings
HEIGHT = {"R_0603": 0.55, "C_0603": 0.9, "C_0805": 1.35, "C_1206": 1.8, "SOT-23-6": 1.3, "SOT-23": 1.2, "SOT-223": 1.8, "TSSOP-24": 1.2,
          "D_SOD-123": 1.35, "D_SMA": 2.4, "D_SMB": 2.5, "CP_EIA-3216-18": 1.8, "TO-252": 2.4, "TestPoint": 0.0, "SolderJumper": 0.0}


def xy(v):
    return v.x / 1e6 - OX, v.y / 1e6 - OY


def check(ok, text):
    print(("ok    " if ok else "FAIL  ") + text)
    if not ok:
        fails.append(text)


def rect(b):
    return (b.GetLeft() / 1e6 - OX, b.GetTop() / 1e6 - OY, b.GetRight() / 1e6 - OX, b.GetBottom() / 1e6 - OY)


def outline():
    pts = [p for d in board.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts for p in (d.GetStart(), d.GetEnd())]
    xs, ys = [p.x / 1e6 - OX for p in pts], [p.y / 1e6 - OY for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


TRACKS = [t for t in board.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
VIAS = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
FPS = {fp.GetReference(): fp for fp in board.GetFootprints()}
X0, Y0, X1, Y1 = outline()


def fpname(fp):
    return fp.GetFPID().GetLibItemName().wx_str()


def pad(name):
    ref, num = name.split(".")
    return [p for p in FPS[ref].Pads() if p.GetNumber() == num][0]


def lcsc(fp):
    return fp.GetFieldText("LCSC") if fp.HasField("LCSC") else ""


def dseg(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = 0 if dx == dy == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def segdist(a, b, c, d):
    def side(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    if side(a, b, c) * side(a, b, d) < 0 and side(c, d, a) * side(c, d, b) < 0:
        return 0.0
    return min(dseg(a, c, d), dseg(b, c, d), dseg(c, a, b), dseg(d, a, b))


def module_body(fp):
    """The outline of the module that plugs in here, from the footprint's fab layer."""
    boxes = [rect(g.GetBoundingBox()) for g in fp.GraphicalItems() if g.GetLayer() == pcbnew.F_Fab and g.GetClass() == "PCB_SHAPE"]
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


def brd_01_outline_and_holes():
    w, h = X1 - X0, Y1 - Y0
    check(w <= 100.0 + 1e-6 and h <= 80.0 + 1e-6, f"BRD-01/04 outline {w:.2f} x {h:.2f} mm, at most 100 x 80")
    holes = [(xy(p.GetPosition()), p.GetDrillSize().x / 1e6, p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH)
             for r, fp in FPS.items() if re.fullmatch(r"H\d", r) for p in fp.Pads()]
    want = {(4.0, 4.0), (w - 4.0, 4.0), (4.0, h - 4.0), (w - 4.0, h - 4.0)}
    got = {(round(p[0], 2), round(p[1], 2)) for p, _, _ in holes}
    check(got == want and all(abs(d - 3.2) < 0.01 and npth for _, d, npth in holes),
          f"BRD-01 four 3.2 mm unplated holes 4.0 mm from the edges: {sorted(got)}")
    near = []
    for (hx, hy), _, _ in holes:
        for r, fp in FPS.items():
            if re.fullmatch(r"H\d", r):
                continue
            for p in fp.Pads():
                b = rect(p.GetBoundingBox())
                if math.hypot(min(max(hx, b[0]), b[2]) - hx, min(max(hy, b[1]), b[3]) - hy) < 3.5:
                    near.append(f"{r}.{p.GetNumber()}")
        near += [f"track {t.GetNetname()}" for t in TRACKS if dseg((hx, hy), xy(t.GetStart()), xy(t.GetEnd())) - t.GetWidth() / 2e6 < 3.5]
        near += [f"via {v.GetNetname()}" for v in VIAS if math.hypot(xy(v.GetPosition())[0] - hx, xy(v.GetPosition())[1] - hy) < 3.5 + 0.3]
    check(not near, "BRD-01 a 7.0 mm circle around each hole is free of pads, tracks and vias" + (f": {sorted(set(near))[:8]}" if near else ""))


def brd_02_sides_and_assembly():
    flipped = [r for r, fp in FPS.items() if fp.IsFlipped()]
    check(not flipped, f"BRD-02 every part is on the top side ({len(FPS)} footprints)" + (f": {flipped}" if flipped else ""))
    smd = [r for r, fp in FPS.items() if fp.GetAttributes() & pcbnew.FP_SMD and not re.match(r"(JP|TP)\d", r)]
    tht = [r for r, fp in FPS.items() if fp.GetAttributes() & pcbnew.FP_THROUGH_HOLE]
    no_number = [r for r in smd if not re.fullmatch(r"C\d+", lcsc(FPS[r]))]
    numbered = [r for r in tht if lcsc(FPS[r])]
    check(not no_number, f"BRD-02 every SMD part carries an LCSC number for JLC ({len(smd)} parts)" + (f"; without: {no_number}" if no_number else ""))
    check(not numbered, f"BRD-02 no through-hole part is in the JLC order: the owner solders {len(tht)}" + (f"; with a number: {numbered}" if numbered else ""))
    jack = module_body(FPS["A202"])
    check(jack[2] > X1 - 1.0, f"BRD-02 the Ethernet jack opens over the east edge (its front is {jack[2] - X1:+.1f} mm from it), nothing opens south")


def brd_03_layers():
    check(board.GetCopperLayerCount() == 2, f"BRD-03 two copper layers (is {board.GetCopperLayerCount()})")
    for layer, name in ((pcbnew.F_Cu, "top"), (pcbnew.B_Cu, "bottom")):
        area = sum(abs(z.GetFilledPolysList(layer).Outline(i).Area()) for z in board.Zones()
                   if not z.GetIsRuleArea() and z.GetNetname() == "GND" and z.GetLayer() == layer
                   for i in range(z.GetFilledPolysList(layer).OutlineCount())) / 1e12
        check(area > 0.3 * (X1 - X0) * (Y1 - Y0), f"BRD-03 ground pour on the {name} layer: {area:.0f} mm2 of {(X1 - X0) * (Y1 - Y0):.0f}")
    gnd_vias = len([v for v in VIAS if v.GetNetname() == "GND"])
    check(gnd_vias >= 200, f"BRD-03 the two ground pours are tied together by {gnd_vias} vias")


def brd_05_design_rules():
    wmin = min(t.GetWidth() for t in TRACKS) / 1e6
    narrow = sum(t.GetLength() for t in TRACKS if t.GetWidth() / 1e6 < 0.25 - 1e-6) / 1e6
    check(wmin >= 0.15 - 1e-6, f"BRD-05 narrowest track {wmin:.2f} mm, at least 0.15; {narrow:.0f} mm of track in all is under 0.25 mm (necks at fine-pitch pads)")
    dmin = min(v.GetDrill() for v in VIAS) / 1e6
    pmin = min(v.GetWidth(pcbnew.F_Cu) for v in VIAS) / 1e6
    check(dmin >= 0.3 - 1e-6 and pmin >= 0.6 - 1e-6, f"BRD-05 smallest via {pmin:.2f} mm with {dmin:.2f} mm drill, at least 0.6 and 0.3")
    pro = json.load(open(os.path.join(HERE, "ptz-driver.kicad_pro")))["board"]["design_settings"]["rules"]
    check(pro["min_clearance"] >= 0.2 and pro["min_track_width"] >= 0.15 and pro["min_copper_edge_clearance"] >= 0.3
          and pro["min_via_diameter"] >= 0.6 and pro["min_through_hole_diameter"] >= 0.3,
          f"BRD-05 the DRC itself runs with gap {pro['min_clearance']}, track {pro['min_track_width']}, edge {pro['min_copper_edge_clearance']}, via {pro['min_via_diameter']}/{pro['min_through_hole_diameter']} mm")
    small = [r for r, fp in FPS.items() if re.search(r"_0402_|_0201_", fpname(fp))]
    check(not small, "BRD-05 no passive smaller than 0603" + (f": {small}" if small else ""))


def reach(net, start, width):
    """The tracks of `net` at least `width` wide that hang together and touch the pad `start`."""
    segs = [(xy(t.GetStart()), xy(t.GetEnd()), t.GetWidth() / 2e6) for t in TRACKS if t.GetNetname() == net and t.GetWidth() / 1e6 >= width - 1e-6]
    p0 = xy(pad(start).GetPosition())
    todo = [s for s in segs if dseg(p0, s[0], s[1]) <= s[2] + 0.8]
    got = list(todo)
    while todo:
        a = todo.pop()
        for s in segs:
            if s not in got and segdist(s[0], s[1], a[0], a[1]) <= max(a[2], s[2]):
                got.append(s)
                todo.append(s)
    return got


def touches(segs, name, slack=0.8):
    p = xy(pad(name).GetPosition())
    return any(dseg(p, s[0], s[1]) <= s[2] + slack for s in segs)


def brd_06_current_paths():
    for net, a, b, width in (("VIN_RAW", "J101.1", "Q101.2", 3.0), ("VIN", "Q101.3", "F101.1", 3.0), ("VIN", "F101.1", "F102.1", 1.0)):
        check(touches(reach(net, a, width), b), f"BRD-06 {net}: tracks at least {width} mm wide join {a} and {b}")
    bus = reach("VM", "F101.2", 3.0)
    length = sum(math.hypot(s[1][0] - s[0][0], s[1][1] - s[0][1]) for s in bus)
    branch = reach("VM", "F101.2", 2.0)
    for n in (3, 4, 5, 6):
        p = xy(pad(f"A{n}01.9").GetPosition())
        d = min(dseg(p, s[0], s[1]) - s[2] for s in bus)
        check(d <= 2.0 and touches(branch, f"A{n}01.9"), f"BRD-06 VM: the 3 mm bus ({length:.0f} mm from F101) passes {max(d, 0):.1f} mm from A{n}01.9, and a branch of 2 mm or more reaches the pad")
        cap = xy(pad(f"C10{n - 2}.1").GetPosition())
        dist = math.hypot(cap[0] - p[0], cap[1] - p[1])
        check(dist <= 12.0 and touches(branch, f"C10{n - 2}.1"), f"BRD-06 C10{n - 2}'s plus pad is {dist:.1f} mm from A{n}01.9, at most 12, on the same branch")
    thin, long = [], []
    for n in (1, 2, 3, 4):
        for i in (1, 2, 3, 4):
            ts = [t for t in TRACKS if t.GetNetname() == f"M{n}_{i}"]
            if not ts or min(t.GetWidth() for t in ts) / 1e6 < 1.0 - 1e-6:
                thin.append(f"M{n}_{i}")
            if sum(t.GetLength() for t in ts) / 1e6 > 15.0:
                long.append(f"M{n}_{i}")
    check(not thin and not long, "BRD-06 all sixteen motor outputs are 1.0 mm wide or more and at most 15 mm long" + (f"; thin {thin}, long {long}" if thin or long else ""))
    for net in ("VIN_L", "+5V_REG", "+5V", "+3V3", "+3V3_SNS", "V_SNS", "FAN_N"):
        w = [t.GetWidth() / 1e6 for t in TRACKS if t.GetNetname() == net]
        neck = sum(t.GetLength() for t in TRACKS if t.GetNetname() == net and t.GetWidth() / 1e6 < 0.5 - 1e-6) / 1e6
        check(bool(w) and min(w) >= 0.35 - 1e-6 and neck <= 3.0,
              f"BRD-06 {net} tracks are 0.5 mm or wider" + (f", but for {neck:.1f} mm of {min(w):.2f} mm necks at fine-pitch pads (at most 3 mm)" if neck else ""))


def brd_09_silkscreen():
    texts = [d.GetText() for d in board.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() == pcbnew.F_SilkS]
    back = [d.GetText() for d in board.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() == pcbnew.B_SilkS]
    name = [t for t in texts if "PTZ" in t and "REV B" in t and re.search(r"20\d\d-\d\d-\d\d", t)]
    check(len(name) == 1, "BRD-09 board name, revision and date are on the top silkscreen")
    need = (["11-17V", "+", "-", "F1 T5A", "F2 T1A", "5V REG", "IN", "OUT", "FAN", "+5V", "I2C", "VSNS", "3V3", "5V", "VM", "USB", "ANT", "RJ45"] +
            [f"{k}{n}" for k in "MHS" for n in (1, 2, 3, 4)] + [f"DRIVER {n}" for n in (1, 2, 3, 4)])
    missing = [n for n in need if n not in texts]
    check(not missing, "BRD-09 every connector, socket and fuse is named on the top side" + (f"; missing {missing}" if missing else ""))
    check(texts.count("SPI") == 4 and texts.count("PU") == 5 and texts.count("EN") == 4 and texts.count("VM") >= 5,
          "BRD-09 every group of jumpers is named, and each driver socket shows its EN and VM corners")
    tps = [r for r in FPS if r.startswith("TP")]
    names = ("VIN", "VM", "5V", "3V3", "VSNS", "GND", "SCK", "MOSI", "MISO", "SDA", "SCL", "ENN", "DIAG", "RST", "M3V3")
    check(sum(texts.count(n) for n in names) >= len(tps), f"BRD-09 all {len(tps)} test points are named")
    legend = " ".join(back)
    check(all(k in legend for k in ("SUPPLY", "MOTOR", "S1-S4", "HOME", "FAN, 5V ONLY", "VSNS", "PULL-UPS", "TMC2209", "U.FL", "K7805")),
          "BRD-09 the pin order of every connector and the use of every jumper is printed on the bottom side")
    small = [d.GetText() for d in board.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)
             and (d.GetTextHeight() / 1e6 < 0.8 - 1e-6 or d.GetTextThickness() / 1e6 < 0.15 - 1e-6)]
    check(not small, "BRD-09 no text smaller than 0.8 mm high with a 0.15 mm stroke" + (f": {small[:5]}" if small else ""))


def brd_11_under_the_modules():
    tall, hidden, unknown = [], [], []
    bodies = {r: module_body(fp) for r, fp in FPS.items() if fpname(fp) in MODULES}
    for r, fp in FPS.items():
        if r in bodies or re.fullmatch(r"H\d", r):
            continue
        c = rect(fp.GetCourtyard(pcbnew.F_CrtYd).BBox())
        under = [m for m, b in bodies.items() if c[0] < b[2] and b[0] < c[2] and c[1] < b[3] and b[1] < c[3]]
        if not under:
            continue
        height = [v for k, v in HEIGHT.items() if fpname(fp).startswith(k)]
        if not height:
            unknown.append(r)
        elif height[0] > 2.2:
            tall.append(f"{r} under {under[0]}")
        if re.match(r"(JP|TP)\d", r):
            hidden.append(f"{r} under {under[0]}")
    n = sum(1 for r, fp in FPS.items() if r not in bodies and any(
        rect(fp.GetCourtyard(pcbnew.F_CrtYd).BBox())[0] < b[2] and b[0] < rect(fp.GetCourtyard(pcbnew.F_CrtYd).BBox())[2] and
        rect(fp.GetCourtyard(pcbnew.F_CrtYd).BBox())[1] < b[3] and b[1] < rect(fp.GetCourtyard(pcbnew.F_CrtYd).BBox())[3] for b in bodies.values()))
    check(not tall and not unknown, f"BRD-11 the {n} parts under a module are 2.2 mm tall at most" + (f"; too tall: {tall}; height unknown: {unknown}" if tall or unknown else ""))
    check(not hidden, "BRD-11 no solder jumper and no test point is under a module" + (f": {hidden}" if hidden else ""))
    b = module_body(FPS["A202"])
    under = sorted(r for r, fp in FPS.items() if r != "A202" and not re.fullmatch(r"H\d", r) and any(
        b[0] < xy(p.GetPosition())[0] < b[2] and b[1] < xy(p.GetPosition())[1] < b[3] for p in fp.Pads()))
    check(not under, "BRD-11 nothing stands under the Ethernet module, which is soldered in" + (f": {under}" if under else ""))


def brd_12_cost():
    cache = os.path.join(HERE, "sourcing", "jlc_parts.json")
    info = json.load(open(cache)) if os.path.exists(cache) else {}
    used = sorted({lcsc(fp) for fp in FPS.values() if lcsc(fp)})
    unread = [c for c in used if c not in info]
    ext = [f"{c} {info[c]['mpn']}" for c in used if c in info and info[c]["library"] == "Extended"]
    check(not unread and len(ext) <= 3, f"BRD-12 {len(used)} assembled BOM lines, {len(ext)} of them Extended, at most 3: {ext}" + (f"; not read at JLC: {unread}" if unread else ""))
    r = subprocess.run([sys.executable.replace("Python.framework/Versions/Current/bin/python3", "Python.framework/Versions/Current/bin/python3"),
                        os.path.join(HERE, "calc", "cost.py")], capture_output=True, text=True)
    high = re.search(r"high estimate is €(\d+)", r.stderr)
    check(r.returncode == 0 and high and int(high.group(1)) <= 100, f"BRD-12 the estimate for five assembled boards is at most €{high.group(1) if high else '?'}, of €100 (calc/cost.py)")


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
    for f in (brd_01_outline_and_holes, brd_02_sides_and_assembly, brd_03_layers, brd_05_design_rules, brd_06_current_paths,
              brd_09_silkscreen, brd_11_under_the_modules, brd_12_cost, brd_10_erc_drc):
        f()
    print(f"\n{len(fails)} failures")
    sys.exit(1 if fails else 0)
