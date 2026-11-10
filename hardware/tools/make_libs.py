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

# --- project file: design rules inside JLC's limits (specs/modules/board.md, BRD-05) and net classes (BRD-06)
import json  # noqa: E402


def netclass(name, track, clearance, via, drill, priority):
    return dict(name=name, track_width=track, clearance=clearance, via_diameter=via, via_drill=drill, priority=priority,
                bus_width=12, wire_width=6, line_style=0, diff_pair_gap=0.2, diff_pair_via_gap=0.25, diff_pair_width=0.2,
                microvia_diameter=0.3, microvia_drill=0.1, pcb_color="rgba(0, 0, 0, 0.000)",
                schematic_color="rgba(0, 0, 0, 0.000)", tuning_profile="")


POWER = ["GND", "VM", "VIN", "VIN_RAW", "VIN_L", "+5V", "+5V_EXT", "VSYS", "VBUS", "+3V3", "+3V3_SNS", "+3V3_I2C", "3V3A",
         "BUCK_SW", "SW3V3", "FAN_V", "FAN_N", "FAN_SRC"]
pro = dict(
    board=dict(design_settings=dict(rules=dict(
        min_clearance=0.15, min_track_width=0.15, min_via_diameter=0.6, min_through_hole_diameter=0.3,
        min_via_annular_width=0.13, min_copper_edge_clearance=0.3, min_hole_clearance=0.25, min_hole_to_hole=0.25,
        min_silk_clearance=0.0, min_text_height=0.7, min_text_thickness=0.08, min_connection=0.0, max_error=0.005,
        min_microvia_diameter=0.2, min_microvia_drill=0.1, min_resolved_spokes=1, min_groove_width=0.0,
        solder_mask_to_copper_clearance=0.0, use_height_for_length_calcs=True))),
    meta=dict(filename="ptz-driver.kicad_pro", version=3),
    net_settings=dict(
        classes=[netclass("Default", 0.2, 0.15, 0.6, 0.3, 2147483647), netclass("Power", 0.5, 0.2, 0.8, 0.4, 0),
                 netclass("Motor", 0.8, 0.2, 0.8, 0.4, 1)],
        meta=dict(version=5), net_colors=None, netclass_assignments=None,
        netclass_patterns=[dict(netclass="Power", pattern=n) for n in POWER] + [dict(netclass="Motor", pattern="M?_??")]),
    erc=dict(rule_severities=dict(lib_symbol_issues="warning", lib_symbol_mismatch="warning", footprint_link_issues="warning")),
    libraries=dict(pinned_footprint_libs=[], pinned_symbol_libs=[]), sheets=[], text_variables={})
open(f"{HW}/ptz-driver.kicad_pro", "w").write(json.dumps(pro, indent=2) + "\n")
print("ptz-driver.kicad_pro written")
