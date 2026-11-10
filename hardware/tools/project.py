#!/usr/bin/env python3
"""Design rules and net classes of the project, kept here because KiCad rewrites ptz-driver.kicad_pro on every save.

patch() merges them into the project file. tools/board.py calls it after each save; run this file to do it by hand.
Rules stay inside JLC's limits (specs/modules/board.md, BRD-05).
"""
import json
import os

HW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRO = os.path.join(HW, "ptz-driver.kicad_pro")

RULES = dict(min_clearance=0.15, min_track_width=0.15, min_via_diameter=0.6, min_through_hole_diameter=0.3,
             min_via_annular_width=0.13, min_copper_edge_clearance=0.3, min_hole_clearance=0.25, min_hole_to_hole=0.25,
             min_text_height=0.7, min_text_thickness=0.08)
# Track widths the router works with. Ground, 3.3 V and the motor supply reach their planes through short stubs from
# fine-pitch pins, so they route narrow; the copper that carries current is planes and pours (BRD-06).
# Motor outputs leave the driver's 0.5 mm pitch pins at 0.3 mm and are widened afterwards by tools/board.py.
CLASSES = {  # name: (track, clearance, via, drill, priority)
    "Default": (0.2, 0.15, 0.6, 0.3, 2147483647),
    "Power": (0.5, 0.2, 0.8, 0.4, 0),
    "Motor": (0.3, 0.2, 0.8, 0.4, 1),
    "Supply": (0.3, 0.2, 0.6, 0.3, 2),
}
PATTERNS = [("Power", n) for n in ("VIN_L", "+5V", "+5V_EXT", "VSYS", "VBUS", "+3V3_SNS", "+3V3_I2C", "BUCK_SW", "SW3V3",
                                   "FAN_V", "FAN_N", "FAN_SRC")]
PATTERNS += [("Motor", "M?_??")] + [("Supply", n) for n in ("VM", "VIN", "VIN_RAW")]
# DRC checks switched off, each with its reason. Everything else stays at KiCad's default and must come out at zero.
DRC_OFF = {
    "silk_edge_clearance": "outlines of edge connectors run off the board on purpose; the fab clips them",
    "starved_thermal": "ground pads sit in the outer pours with thermal spokes where they fit; each also has its own track or via to the plane",
    "silk_overlap": "outlines of neighbouring footprints touch at this density; no text is involved (tools/silk.py keeps texts apart)",
}
ERC = dict(lib_symbol_issues="warning", lib_symbol_mismatch="warning", footprint_link_issues="warning")


def patch():
    d = json.load(open(PRO)) if os.path.exists(PRO) else {}
    d.setdefault("meta", dict(filename="ptz-driver.kicad_pro", version=3))
    rules = d.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rules", {})
    rules.update(RULES)
    d["board"]["design_settings"].setdefault("rule_severities", {}).update({k: "ignore" for k in DRC_OFF})
    ns = d.setdefault("net_settings", {})
    base = dict(bus_width=12, wire_width=6, line_style=0, diff_pair_gap=0.2, diff_pair_via_gap=0.25, diff_pair_width=0.2,
                microvia_diameter=0.3, microvia_drill=0.1, pcb_color="rgba(0, 0, 0, 0.000)",
                schematic_color="rgba(0, 0, 0, 0.000)", tuning_profile="")
    ns["classes"] = [dict(base, name=n, track_width=t, clearance=c, via_diameter=v, via_drill=dr, priority=p)
                     for n, (t, c, v, dr, p) in CLASSES.items()]
    ns["netclass_patterns"] = [dict(netclass=c, pattern=p) for c, p in PATTERNS]
    ns.setdefault("meta", dict(version=5))
    ns.setdefault("net_colors", None)
    ns.setdefault("netclass_assignments", None)
    d.setdefault("erc", {}).setdefault("rule_severities", {}).update(ERC)
    open(PRO, "w").write(json.dumps(d, indent=2) + "\n")


if __name__ == "__main__":
    patch()
    print("ptz-driver.kicad_pro patched")
