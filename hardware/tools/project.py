#!/usr/bin/env python3
"""Design rules and net classes of the project, kept here because KiCad rewrites ptz-driver.kicad_pro on every save.

patch() merges them into the project file. tools/board.py calls it after each save; run this file to do it by hand.
Rules stay inside JLC's limits (specs/modules/board.md, BRD-05).
"""
import json
import os

HW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRO = os.path.join(HW, "ptz-driver.kicad_pro")

RULES = dict(min_clearance=0.2, min_track_width=0.15, min_via_diameter=0.6, min_through_hole_diameter=0.3,
             min_via_annular_width=0.13, min_copper_edge_clearance=0.3, min_hole_clearance=0.25, min_hole_to_hole=0.25,
             min_text_height=0.7, min_text_thickness=0.08)
# Track widths the router works with (BRD-05, BRD-06). The input path and the VM bus are pours laid by tools/board.py;
# the Supply class is for the short tracks that hang small parts on them.
CLASSES = {  # name: (track, clearance, via, drill, priority)
    "Default": (0.25, 0.2, 0.6, 0.3, 2147483647),
    "Supply": (0.8, 0.25, 0.8, 0.4, 0),
    "Motor": (1.0, 0.25, 0.8, 0.4, 1),
    "Power": (0.5, 0.2, 0.8, 0.4, 2),
}
PATTERNS = [("Supply", n) for n in ("VIN_RAW", "VIN", "VM")] + [("Motor", "M?_?")]
PATTERNS += [("Power", n) for n in ("VIN_L", "+5V_REG", "+5V", "+3V3", "+3V3_SNS", "V_SNS", "FAN_N")]
# DRC checks switched off, each with its reason. Everything else stays at KiCad's default and must come out at zero.
DRC_OFF = {
    "silk_edge_clearance": "the Ethernet module's outline runs off the board on purpose (its jack overhangs); the fab clips it",
    "silk_overlap": "outlines of neighbouring footprints touch; no text is involved (tools/silk.py keeps texts apart)",
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
