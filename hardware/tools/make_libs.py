#!/usr/bin/env python3
"""Write the project's own footprints (ptz.pretty) and the library tables. Run once, and again after a change here.

The three module footprints are sockets: rows of 1.0 mm holes on a 2.54 mm grid, with the module's outline.
Every dimension below names the drawing it was read from (hardware/datasheets/README.md).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sexp import Q, dump  # noqa: E402

HW = os.path.dirname(HERE)
os.makedirs(f"{HW}/ptz.pretty", exist_ok=True)
for old in os.listdir(f"{HW}/ptz.pretty"):
    os.remove(f"{HW}/ptz.pretty/{old}")
P = 2.54


def line(x1, y1, x2, y2, layer, w):
    return ["fp_line", ["start", x1, y1], ["end", x2, y2], ["stroke", ["width", w], ["type", "solid"]], ["layer", Q(layer)]]


def rect(x1, y1, x2, y2, layer, w):
    return [line(x1, y1, x2, y1, layer, w), line(x2, y1, x2, y2, layer, w), line(x2, y2, x1, y2, layer, w), line(x1, y2, x1, y1, layer, w)]


def text(kind, value, x, y, layer, hide=False):
    p = ["property", Q(kind), Q(value), ["at", x, y, 0], ["layer", Q(layer)],
         ["effects", ["font", ["size", 0.8, 0.8], ["thickness", 0.12]]]]
    if hide:
        p.insert(5, ["hide", "yes"])
    return p


def tht(n, x, y, drill=1.0, size=1.7, square=False):
    return ["pad", Q(str(n)), "thru_hole", "rect" if square else "circle", ["at", x, y], ["size", size, size], ["drill", drill],
            ["layers", Q("*.Cu"), Q("*.Mask")]]


def poly(pts, layer, w):
    return [line(*pts[i], *pts[(i + 1) % len(pts)], layer, w) for i in range(len(pts))]


def strip(x0, y0, x1, y1, m=1.52):
    """Courtyard around a row of pins from (x0, y0) to (x1, y1): the pads plus 0.25 mm."""
    return [(x0 - m, y0 - m), (x1 + m, y0 - m), (x1 + m, y1 + m), (x0 - m, y1 + m)]


def footprint(name, descr, body, pads, extra=(), attr="through_hole", ref_at=None, courtyards=None):
    """body = (x0, y0, x1, y1): the part's outline, drawn on the fab layer and, 0.25 mm larger, as the courtyard.

    A module on a socket gets courtyards around its pin rows only: low parts may stand under it (BRD-11), and
    hardware/check_board.py checks their height against the outline on the fab layer."""
    x0, y0, x1, y1 = body
    rx, ry = ref_at or ((x0 + x1) / 2, y0 - 1.0)
    fp = ["footprint", Q(name), ["version", 20241229], ["generator", Q("make_libs")], ["layer", Q("F.Cu")], ["descr", Q(descr)],
          text("Reference", "REF**", rx, ry, "F.SilkS"), text("Value", name, (x0 + x1) / 2, y1 + 1.0, "F.Fab"),
          text("Datasheet", "", 0, 0, "F.Fab", True), text("Description", "", 0, 0, "F.Fab", True), ["attr"] + attr.split()]
    fp += rect(x0, y0, x1, y1, "F.Fab", 0.1)
    for c in courtyards or [[(x0 - 0.25, y0 - 0.25), (x1 + 0.25, y0 - 0.25), (x1 + 0.25, y1 + 0.25), (x0 - 0.25, y1 + 0.25)]]:
        fp += poly(c, "F.CrtYd", 0.05)
    fp += list(extra) + pads + [["embedded_fonts", "no"]]
    open(f"{HW}/ptz.pretty/{name}.kicad_mod", "w").write(dump(fp) + "\n")


def corners(x0, y0, x1, y1, n=1.5, w=0.15):
    """Silkscreen corner marks of a module's outline: the outline itself would run through its own pads."""
    out = []
    for cx, cy, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x1, y1, -1, -1), (x0, y1, 1, -1)):
        out += [line(cx, cy, cx + dx * n, cy, "F.SilkS", w), line(cx, cy, cx, cy + dy * n, "F.SilkS", w)]
    return out


def dot(x, y, r=0.3):
    return ["fp_circle", ["center", x, y], ["end", x + r, y], ["stroke", ["width", 0.15], ["type", "solid"]], ["fill", "yes"], ["layer", Q("F.SilkS")]]


# --- StepStick driver module: BIGTREETECH TMC2240 V1.0 manual p4 (15.24 x 20.32 mm) and p5 (pin drawing).
# Pads 1-8 = left row L1-L8 (EN ... DIR), 9-16 = right row R1-R8 (VM ... GND), 12.7 mm apart;
# 17 and 18 = the two extra pins in the top row, one and two pitches from L1 (AIN/INDEX and DIAG).
pads = [tht(i + 1, 0, i * P, square=(i == 0)) for i in range(8)] + [tht(i + 9, 5 * P, i * P) for i in range(8)]
pads += [tht(17, P, 0), tht(18, 2 * P, 0)]
body = (-P / 2, -P / 2, 5.5 * P, 7.5 * P)
footprint("StepStick_Socket", "Socket for a StepStick stepper driver module, 2 x 8 pins and 2 extra pins in the top row "
          "(BIGTREETECH TMC2240 V1.0 / TMC2209 V1.3). 1 = EN, 9 = VM, 18 = DIAG", body, pads,
          corners(*body) + [dot(-1.9, 0)], ref_at=(6.35, 8.9),
          courtyards=[[(-1.52, -1.52), (2 * P + 1.52, -1.52), (2 * P + 1.52, 1.52), (1.52, 1.52), (1.52, 7 * P + 1.52), (-1.52, 7 * P + 1.52)],
                      strip(5 * P, 0, 5 * P, 7 * P)])

# --- ESP32-S3-DevKitC-1: Espressif's drawing DXF_ESP32-S3-DevKitC-1_V1.1_20220429: 25.4 x 62.87 mm, rows at 1.27 and
# 24.13 mm from the left edge, 22 pins each; pin 1 is 1.565 mm from the antenna end, pin 22 is 7.96 mm from the USB end.
# Pads 1-22 = J1 pins 1-22 (3V3 ... G), 23-44 = J3 pins 1-22 (G, TX ... G). Origin at J1 pin 1, USB end at +y.
pads = [tht(i + 1, 0, i * P, square=(i == 0)) for i in range(22)] + [tht(i + 23, 9 * P, i * P) for i in range(22)]
body = (-1.27, -1.565, 24.13, 21 * P + 7.96)
usb = [line(3.4, body[3], 3.4, body[3] - 6.5, "F.SilkS", 0.15), line(19.46, body[3], 19.46, body[3] - 6.5, "F.SilkS", 0.15),
       line(3.4, body[3] - 6.5, 19.46, body[3] - 6.5, "F.SilkS", 0.15)]
footprint("ESP32-S3-DevKitC-1", "Socket for an ESP32-S3-DevKitC-1 / -1U, 2 x 22 pins, rows 22.86 mm apart. "
          "1-22 = J1 (pin 1 = 3V3, antenna end), 23-44 = J3; the USB sockets are at the pin 22 end", body, pads,
          corners(*body, n=2.5) + usb + [dot(-2.0, 0)], ref_at=(11.43, 20.0),
          courtyards=[strip(0, 0, 0, 21 * P), strip(9 * P, 0, 9 * P, 21 * P)])

# --- WIZ850io: WIZnet datasheet V1.0 p10: 23.0 x 25.0 mm, rows 20.32 mm apart, pin 1 is 6.4 mm from the end where the
# RJ45 jack overhangs by 2.7 mm; the jack is 16.1 mm wide. Pads 1-6 = J1 (GND GND MOSI SCLK SCNn INTn),
# 7-12 = J2 (GND 3.3V 3.3V NC RSTn MISO). Origin at J1 pin 1, the jack opens towards -y.
pads = [tht(i + 1, 0, i * P, square=(i == 0)) for i in range(6)] + [tht(i + 7, 8 * P, i * P) for i in range(6)]
body = (-1.34, -6.4 - 2.7, 21.66, 5 * P + 5.9)
jack = rect(2.11, -9.1, 18.21, 12.0, "F.Fab", 0.1) + [line(2.11, -6.4, 18.21, -6.4, "F.SilkS", 0.15),
                                                       line(2.11, -6.4, 2.11, -9.1, "F.SilkS", 0.15),
                                                       line(18.21, -6.4, 18.21, -9.1, "F.SilkS", 0.15)]
footprint("WIZ850io", "WIZnet WIZ850io or compatible W5500 module, 2 x 6 pins, rows 20.32 mm apart. "
          "1-6 = J1 (pin 1 = GND), 7-12 = J2; the RJ45 jack opens at the pin 1 end", body, pads,
          corners(-1.34, -6.4, 21.66, 18.6, n=0.8) + jack + [dot(-2.0, 0)], ref_at=(10.16, 6.35),
          courtyards=[strip(0, 0, 0, 5 * P), strip(8 * P, 0, 8 * P, 5 * P)])

# --- 5 V switching regulator, SIP-3 in the 7805 pin order (1 in, 2 ground, 3 out), pitch 2.54 mm.
# The body is the envelope of the RECOM R-78K (11.5 x 7.55), R-78E (11.6 x 8.5), Traco TSR 1 (11.7 x 7.6) and
# Mornsun K7805-1000R3 (11.5 x 9.0): 11.7 mm wide, 9.1 mm deep, the pins 2.0 mm from the front face.
body = (2.54 - 5.85, -7.1, 2.54 + 5.85, 2.0)
footprint("SIP3_DCDC_7805", "Three-pin switching regulator in the 7805 pin order: 1 = in, 2 = ground, 3 = out "
          "(RECOM R-78K/R-78E, Traco TSR 1, Mornsun K7805)", body, [tht(1, 0, 0, square=True), tht(2, P, 0), tht(3, 2 * P, 0)],
          rect(body[0], body[1], body[2], body[3], "F.SilkS", 0.15) + [dot(-1.6, 2.9)], ref_at=(2.54, -3.5))

# --- TO-252 (DPAK) with the land pattern JLC uses for the AOD4185 (C400894): KiCad's own is 0.65 mm shorter
dpak = [["pad", Q(n), "smd", "roundrect", ["at", x, y], ["size", w, h], ["layers", Q("F.Cu"), Q("F.Mask"), Q("F.Paste")],
         ["roundrect_rratio", 0.08]] for n, x, y, w, h in (("1", -3.475, -2.286, 2.5, 1.2), ("3", -3.475, 2.286, 2.5, 1.2), ("2", 3.475, 0, 6.5, 6.0))]
footprint("TO-252_JLC", "TO-252 / DPAK, pads as JLC's TO-252-3_L6.6-W6.1-P4.57-LS9.9: 1 and 3 the leads, 2 the tab",
          (-4.73, -3.15, 6.73, 3.15), dpak,
          [line(-2.4, -3.4, 0.0, -3.4, "F.SilkS", 0.12), line(-2.4, 3.4, 0.0, 3.4, "F.SilkS", 0.12),
           line(-2.4, -3.4, -2.4, -3.1, "F.SilkS", 0.12), line(-2.4, 3.4, -2.4, 3.1, "F.SilkS", 0.12),
           line(-4.7, -3.2, -2.4, -3.2, "F.SilkS", 0.12)], attr="smd", ref_at=(0, -4.3))

# --- a test point: a bare 1.5 mm pad, big enough for a probe tip or a soldered wire
tp = ["footprint", Q("TestPoint_D1.5"), ["version", 20241229], ["generator", Q("make_libs")], ["layer", Q("F.Cu")],
      ["descr", Q("Test point, 1.5 mm round pad")], text("Reference", "REF**", 0, -1.6, "F.SilkS"), text("Value", "TP", 0, 1.6, "F.Fab"),
      text("Datasheet", "", 0, 0, "F.Fab", True), text("Description", "", 0, 0, "F.Fab", True), ["attr", "exclude_from_pos_files", "exclude_from_bom"],
      ["fp_circle", ["center", 0, 0], ["end", 1.0, 0], ["stroke", ["width", 0.05], ["type", "solid"]], ["fill", "no"], ["layer", Q("F.CrtYd")]],
      ["pad", Q("1"), "smd", "circle", ["at", 0, 0], ["size", 1.5, 1.5], ["layers", Q("F.Cu"), Q("F.Mask")]], ["embedded_fonts", "no"]]
open(f"{HW}/ptz.pretty/TestPoint_D1.5.kicad_mod", "w").write(dump(tp) + "\n")

for name, kind, uri in (("sym-lib-table", "sym_lib_table", "${KIPRJMOD}/ptz.kicad_sym"), ("fp-lib-table", "fp_lib_table", "${KIPRJMOD}/ptz.pretty")):
    open(f"{HW}/{name}", "w").write(dump([kind, ["version", 7], ["lib", ["name", Q("ptz")], ["type", Q("KiCad")], ["uri", Q(uri)],
                                                                 ["options", Q("")], ["descr", Q("PTZ driver board")]]]) + "\n")
print("ptz.pretty, sym-lib-table and fp-lib-table written")

import project  # noqa: E402

project.patch()
print("ptz-driver.kicad_pro patched")
