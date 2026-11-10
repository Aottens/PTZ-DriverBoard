#!/usr/bin/env python3
"""Write the project's own footprints (ptz.pretty) and the library tables. Run once, and again after a change here.

- ESP32-C6-MINI-1U: KiCad's ESP32-C6-MINI-1 pads, with the body of the 1U (13.2 x 12.5 mm, datasheet v1.5
  figure 11-2: bottom edge 5.6 mm below the pad centre, so the top edge is 6.9 mm above it) and no antenna keep-out.
- LED_RGB_1616: Everlight 19-237, pads as in JLC's own footprint for C60105 (read from the EasyEDA library).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sexp import Q, dump, find, parse  # noqa: E402

HW = os.path.dirname(HERE)
KICAD_FP = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
os.makedirs(f"{HW}/ptz.pretty", exist_ok=True)


def line(x1, y1, x2, y2, layer, w):
    return ["fp_line", ["start", x1, y1], ["end", x2, y2], ["stroke", ["width", w], ["type", "solid"]], ["layer", Q(layer)]]


def rect(x1, y1, x2, y2, layer, w):
    return [line(x1, y1, x2, y1, layer, w), line(x2, y1, x2, y2, layer, w), line(x2, y2, x1, y2, layer, w), line(x1, y2, x1, y1, layer, w)]


def text(kind, value, y, layer, hide=False):
    p = ["property", Q(kind), Q(value), ["at", 0, y, 0], ["layer", Q(layer)],
         ["effects", ["font", ["size", 0.8, 0.8], ["thickness", 0.12]]]]
    if hide:
        p.insert(5, ["hide", "yes"])
    return p


# --- ESP32-C6-MINI-1U
fp = parse(open(f"{KICAD_FP}/RF_Module.pretty/ESP32-C6-MINI-1.kicad_mod").read())
keep = []
for x in fp:
    if isinstance(x, list):
        if x[0] in ("zone", "model"):
            continue
        if x[0] in ("fp_line", "fp_poly", "fp_rect") and find(x, "layer")[1] in ("F.CrtYd", "F.Fab", "F.SilkS"):
            continue
    keep.append(x)
fp = keep
fp[1] = Q("ESP32-C6-MINI-1U")
tail = [x for x in fp if isinstance(x, list) and x[0] == "embedded_fonts"]
fp = [x for x in fp if x not in tail]
fp += rect(-6.6, -6.9, 6.6, 5.6, "F.Fab", 0.1) + rect(-6.85, -7.15, 6.85, 5.85, "F.CrtYd", 0.05)
for x1, y1, x2, y2 in ((-6.75, -7.05, 6.75, -7.05), (-6.75, -7.05, -6.75, -4.6), (6.75, -7.05, 6.75, -4.6),
                       (-6.75, 5.75, -5.6, 5.75), (6.75, 5.75, 5.6, 5.75), (-6.75, 4.6, -6.75, 5.75), (6.75, 4.6, 6.75, 5.75)):
    fp.append(line(x1, y1, x2, y2, "F.SilkS", 0.12))
fp.append(["fp_circle", ["center", -7.4, -4.0], ["end", -7.2, -4.0], ["stroke", ["width", 0.2], ["type", "solid"]],
           ["fill", "yes"], ["layer", Q("F.SilkS")]])
open(f"{HW}/ptz.pretty/ESP32-C6-MINI-1U.kicad_mod", "w").write(dump(fp + tail) + "\n")

# --- LED_RGB_1616: pads 1 R, 2 G, 3 B cathodes, 4 common anode
pads = {"1": (-0.8, 0.45), "2": (-0.8, -0.45), "3": (0.8, -0.45), "4": (0.8, 0.45)}
led = ["footprint", Q("LED_RGB_1616"), ["version", 20241229], ["generator", Q("make_libs")], ["layer", Q("F.Cu")],
       ["descr", Q("RGB LED 1.6x1.6 mm, Everlight 19-237, 1 R- 2 G- 3 B- 4 common anode")],
       text("Reference", "REF**", -1.7, "F.SilkS"), text("Value", "LED_RGB_1616", 1.7, "F.Fab"),
       text("Datasheet", "", 0, "F.Fab", True), text("Description", "", 0, "F.Fab", True), ["attr", "smd"]]
led += rect(-0.8, -0.8, 0.8, 0.8, "F.Fab", 0.1) + rect(-1.45, -1.0, 1.45, 1.0, "F.CrtYd", 0.05)
led += [line(-1.4, 1.1, 1.4, 1.1, "F.SilkS", 0.12), line(-1.4, -1.1, 1.4, -1.1, "F.SilkS", 0.12),
        ["fp_circle", ["center", 1.75, 0.45], ["end", 1.85, 0.45], ["stroke", ["width", 0.15], ["type", "solid"]],
         ["fill", "yes"], ["layer", Q("F.SilkS")]]]
for n, (x, y) in pads.items():
    led.append(["pad", Q(n), "smd", "roundrect", ["at", x, y], ["size", 0.8, 0.55], ["layers", Q("F.Cu"), Q("F.Mask"), Q("F.Paste")],
                ["roundrect_rratio", 0.2]])
open(f"{HW}/ptz.pretty/LED_RGB_1616.kicad_mod", "w").write(dump(led + [["embedded_fonts", "no"]]) + "\n")

# --- TO-252 (DPAK) with the land pattern JLC uses for the AOD4185 (C400894): KiCad's own is 0.65 mm shorter
dpak = ["footprint", Q("TO-252_JLC"), ["version", 20241229], ["generator", Q("make_libs")], ["layer", Q("F.Cu")],
        ["descr", Q("TO-252 / DPAK, pads as JLC's TO-252-3_L6.6-W6.1-P4.57-LS9.9: 1 and 3 the leads, 2 the tab")],
        text("Reference", "REF**", -4.3, "F.SilkS"), text("Value", "TO-252", 4.3, "F.Fab"),
        text("Datasheet", "", 0, "F.Fab", True), text("Description", "", 0, "F.Fab", True), ["attr", "smd"]]
dpak += rect(-2.3, -3.3, 4.3, 3.3, "F.Fab", 0.1) + rect(-4.98, -3.4, 6.98, 3.4, "F.CrtYd", 0.05)
dpak += [line(-2.4, -3.4, 0.0, -3.4, "F.SilkS", 0.12), line(-2.4, 3.4, 0.0, 3.4, "F.SilkS", 0.12),
         line(-2.4, -3.4, -2.4, -3.1, "F.SilkS", 0.12), line(-2.4, 3.4, -2.4, 3.1, "F.SilkS", 0.12),
         line(-4.7, -3.2, -2.4, -3.2, "F.SilkS", 0.12)]
for n, x, y, w, h in (("1", -3.475, -2.286, 2.5, 1.2), ("3", -3.475, 2.286, 2.5, 1.2), ("2", 3.475, 0, 6.5, 6.0)):
    dpak.append(["pad", Q(n), "smd", "roundrect", ["at", x, y], ["size", w, h], ["layers", Q("F.Cu"), Q("F.Mask"), Q("F.Paste")],
                 ["roundrect_rratio", 0.08]])
open(f"{HW}/ptz.pretty/TO-252_JLC.kicad_mod", "w").write(dump(dpak + [["embedded_fonts", "no"]]) + "\n")

# --- a test point with a tight courtyard: a bare 1.0 mm pad
tp = ["footprint", Q("TestPoint_D1.0"), ["version", 20241229], ["generator", Q("make_libs")], ["layer", Q("F.Cu")],
      ["descr", Q("Test point, 1.0 mm round pad")], text("Reference", "REF**", -1.3, "F.SilkS"), text("Value", "TP", 1.3, "F.Fab"),
      text("Datasheet", "", 0, "F.Fab", True), text("Description", "", 0, "F.Fab", True), ["attr", "exclude_from_pos_files", "exclude_from_bom"],
      ["fp_circle", ["center", 0, 0], ["end", 0.75, 0], ["stroke", ["width", 0.05], ["type", "solid"]], ["fill", "no"], ["layer", Q("F.CrtYd")]],
      ["pad", Q("1"), "smd", "circle", ["at", 0, 0], ["size", 1.0, 1.0], ["layers", Q("F.Cu"), Q("F.Mask")]], ["embedded_fonts", "no"]]
open(f"{HW}/ptz.pretty/TestPoint_D1.0.kicad_mod", "w").write(dump(tp) + "\n")

for name, kind, uri in (("sym-lib-table", "sym_lib_table", "${KIPRJMOD}/ptz.kicad_sym"), ("fp-lib-table", "fp_lib_table", "${KIPRJMOD}/ptz.pretty")):
    open(f"{HW}/{name}", "w").write(dump([kind, ["version", 7], ["lib", ["name", Q("ptz")], ["type", Q("KiCad")], ["uri", Q(uri)],
                                                                 ["options", Q("")], ["descr", Q("PTZ driver board")]]]) + "\n")
print("ptz.pretty, sym-lib-table and fp-lib-table written")

import project  # noqa: E402

project.patch()
print("ptz-driver.kicad_pro patched")
