"""Where the parts sit. All numbers in mm, origin at the board's top-left corner, y down.

The bottom edge (y = BOARD_H) faces the pan motor: no connectors there.
FIXED gives the centre of a part's courtyard and its rotation; everything else is placed by board.py
next to the pad named in NEAR, or next to a pad it shares a signal net with.
"""
BOARD_W, BOARD_H = 85.0, 65.0
HOLES = [(4.0, 4.0), (81.0, 4.0), (4.0, 61.0), (81.0, 61.0)]
EDGE = 0.4      # small parts keep this far from the board edge
HALO = 0.15     # room left around a small part where it fits, so tracks and vias can pass
STEP = 0.25
REACH = 25.0
KEEPOUT = [(4.4, 22.6, 11.3, 25.8)]   # the VM pour between TVS and fuse, with its vias
# supply plane on inner layer 2: the motor supply under the drivers and bulk capacitors, 3.3 V under the logic
# VM covers the input corner and the strip under the drivers' VS pins; +3V3 starts under their logic side
PLANES = [("VM", [(0, 0), (85, 0), (85, 13.2), (64.6, 13.2), (64.6, 29.0), (58.2, 29.0), (58.2, 13.2), (51.1, 13.2), (51.1, 29.0),
                  (44.9, 29.0), (44.9, 13.2), (24.5, 13.2), (24.5, 25.9), (0, 25.9)]),     # two tongues reach the bulk capacitors
          ("+3V3", [(0, 26.4), (25.0, 26.4), (25.0, 13.7), (44.4, 13.7), (44.4, 29.5), (51.6, 29.5), (51.6, 13.7), (57.7, 13.7),
                    (57.7, 29.5), (65.1, 29.5), (65.1, 13.7), (85, 13.7), (85, 65), (0, 65)])]
# pours on the top layer that carry the input current (BRD-06): connector to FET, FET to fuse, fuse to bulk capacitor
POURS = [("VIN_RAW", [(10.1, 2.6), (13.7, 2.6), (13.7, 9.6), (18.0, 9.6), (18.0, 17.4), (11.8, 17.4), (11.8, 9.6), (10.1, 9.6)]),
         ("VIN", [(16.2, 19.2), (18.6, 19.2), (18.6, 25.9), (16.2, 25.9)]),
         ("VM", [(1.8, 22.6), (13.6, 22.6), (13.6, 25.8), (1.8, 25.8)])]
# vias from the VM pour down to the VM plane, 0.8/0.4 mm
VM_VIAS = [(x, y) for x in (5.2, 6.5, 7.8, 9.1, 10.4) for y in (23.4, 25.0)]
MAY_OVERLAP = {"H1", "H2", "H3", "H4"}

AXIS_X = {1: 26.0, 2: 39.6, 3: 53.2, 4: 66.8}   # centre line of each driver cell
DRIVER_Y = 12.05

FIXED = {
    "H1": (4, 4, 0), "H2": (81, 4, 0), "H3": (4, 61, 0), "H4": (81, 61, 0),
    # top-left corner: power in, with the reverse-polarity FET, the motor fuse and the TVS below it
    "J101": (13.9, 5.3, 0), "Q101": (14.9, 16.15, 90), "F101": (14.9, 24.2, 180), "D102": (3.1, 21.7, 90),
    # left edge, top to bottom: camera, Ethernet header, USB-C, spare I2C
    "J901": (3.4, 13.0, 270), "J801": (3.4, 32.1, 270), "J201": (4.26, 44.15, 270), "J202": (3.4, 53.5, 270),
    # right edge: external driver ports, RS-485
    "J303": (81.75, 13.0, 90), "J403": (81.75, 22.6, 90), "J503": (81.75, 32.2, 90), "J603": (81.75, 41.8, 90),
    "J802": (81.75, 51.4, 90),
    # power
    "C101": (52.6, 27.1, 0), "C102": (66.1, 27.1, 0), "U101": (31.0, 24.6, 0), "L101": (40.6, 26.4, 0),
    "U204": (42.9, 19.7, 0),
    # logic
    "U801": (15.2, 32.0, 0), "U201": (17.2, 49.0, 0), "U202": (30.0, 45.0, 0), "U203": (30.5, 53.5, 0),
    "U701": (41.0, 45.2, 0), "U702": (52.0, 44.5, 0), "U703": (73.5, 46.0, 0), "U802": (71.5, 54.5, 0),
    "U803": (52.0, 60.8, 0), "J803": (62.0, 60.5, 0), "J902": (72.0, 61.0, 0), "U102": (27.0, 61.5, 0),
    "SW201": (38.0, 61.5, 0),
}
NEAR = {
    "C103": ("U101", "2"), "C104": ("U101", "2"), "C105": ("U101", "2"), "C106": ("U101", "1"), "R102": ("U101", "3"),
    "R103": ("U101", "3"), "R104": ("U101", "4"), "R105": ("U101", "6"), "C107": ("R105", "2"), "C108": ("U101", "6"),
    "R107": ("U101", "5"), "R112": ("U101", "5"), "R106": ("R112", "1"), "D103": ("U101", "8"), "C109": ("L101", "2"),
    "C110": ("L101", "2"), "D104": ("L101", "2"), "C111": ("U102", "4"), "L102": ("U102", "3"), "C112": ("L102", "2"),
    "C113": ("L102", "2"), "R108": ("U102", "5"), "R109": ("U102", "5"), "C115": ("U102", "5"), "D105": ("U102", "4"),
    "F102": ("F101", "1"), "D101": ("Q101", "1"), "R101": ("Q101", "1"),
    "C201": ("U201", "3"), "C202": ("U201", "3"), "R201": ("U201", "8"), "C203": ("U201", "8"), "C204": ("U202", "16"),
    "C205": ("U203", "24"), "C206": ("U204", "8"), "C207": ("J201", "A4"), "F201": ("J202", "2"), "C208": ("J202", "2"),
    "C701": ("U701", "20"), "C702": ("U702", "14"), "C703": ("U703", "20"), "F701": ("J402", "1"), "C704": ("J402", "1"),
    "F702": ("J403", "1"), "C705": ("J403", "1"), "C801": ("U801", "4"), "C802": ("U801", "8"), "C803": ("U801", "15"),
    "C804": ("U801", "21"), "C805": ("U801", "11"), "FB801": ("U801", "17"), "C806": ("U801", "28"), "C807": ("U801", "28"),
    "D802": ("SW201", "1"), "D803": ("SW201", "1"), "C816": ("U802", "8"), "C817": ("U803", "3"), "D201": ("SW201", "1"),
    "TP901": ("F102", "1"), "TP902": ("D102", "1"), "TP903": ("L101", "2"), "TP904": ("U102", "4"), "TP905": ("U201", "3"),
    "TP906": ("SW201", "2"), "TP907": ("C102", "2"), "Q901": ("U203", "18"), "Q902": ("U203", "19"), "U205": ("J201", "A6"),
}
# One driver cell, relative to the driver's centre. The chip is turned so its motor side faces the connector above it:
# top = VS and the four outputs, right = charge pump, DIAG, enable, left = SLEEPN, SPI, REFL, bottom = IREF, 1V8, VCC_IO.
CELL = {  # ref suffix: (dx, dy, rotation)
    "C04": (3.30, -3.95, 180),   # VCP to VM, above the corner: VM pad over pin 17, VCP pad reached from pin 16
    "C02": (5.85, -3.60, 0),     # 100 nF on the right-hand VS pin
    "C05": (3.75, -0.95, 90),    # charge pump capacitor straight out of pins 14 and 15; DIAG and enable pass below it
    "R04": (5.60, 0.20, 0), "R03": (5.60, 1.30, 0),      # DIAG pull-ups
    "R02": (-3.75, -2.30, 90),   # SLEEPN to VM, at the corner between pin 25 and pin 24
    "C01": (-5.30, -3.30, 180),  # 100 nF on the left-hand VS pin
    "C03": (-5.85, 4.90, 270),   # 10 uF, low on the left so the SPI pins have room for their vias
    "R01": (-1.82, 4.20, 270), "C06": (-0.75, 4.20, 270), "C07": (0.32, 4.20, 270),   # under pins 1, 3 and 5
}
for n, x in AXIS_X.items():
    a = n + 2
    FIXED[f"J{a}01"] = (x, 3.9, 0)
    FIXED[f"U{a}01"] = (x, DRIVER_Y, 90)
    FIXED[f"J{a}02"] = (30.5 + 13.4 * (n - 1), 37.45, 0)
    for part, (dx, dy, rot) in CELL.items():
        FIXED[f"{part[0]}{a}{part[1:]}"] = (x + dx, DRIVER_Y + dy, rot)
    u, s, e = f"U{a}01", f"J{a}02", f"J{a}03"
    NEAR.update({
        f"D{a}01": (u, "31"), f"C{a}12": (u, "31"), f"R{a}06": (f"D{a}01", "3"), f"R{a}05": (s, "7"),
        f"R{a}07": (s, "3"), f"R{a}08": (s, "4"), f"R{a}09": (s, "6"), f"R{a}10": (s, "5"), f"R{a}11": (s, "3"),
        f"R{a}12": (s, "4"), f"R{a}13": (f"R{a}10", "2"), f"R{a}14": (e, "2"), f"R{a}15": (e, "3"),
    })

# Silkscreen texts with a fixed place: (text, x, y, angle). The small parts keep clear of them.
# Everything else on the silkscreen finds its own free spot (tools/silk.py).
LABELS = {"J101": ("12-24V", 8.3, 4.7, 90), "J901": ("CAM", 7.5, 13.0, 90), "J801": ("ETH", 8.0, 32.1, 90), "J202": ("I2C", 7.7, 53.5, 90)}
LABELS.update({"SW201": ("BOOT", 38.0, 58.0, 0), "J201": ("USB", 9.68, 44.15, 90), "J802": ("RS485", 77.8, 51.4, 90),
               "J803": ("CAN", 62.0, 56.5, 0), "J902": ("FAN", 72.0, 56.9, 0)})
for n, y in enumerate((13.0, 22.6, 32.2, 41.8), 1):
    LABELS[f"J{n + 2}03"] = (f"X{n}", 77.8, y, 90)
for n, x in AXIS_X.items():
    LABELS[f"J{n + 2}01"] = (f"M{n}", x, 8.05, 0)
for n in AXIS_X:
    LABELS[f"J{n + 2}02"] = (f"S{n}", 24.9 + 13.4 * (n - 1), 33.4, 0)
# Small parts that carry a name: board.py places part and name as one piece, the name left or right of it.
PART_LABELS = {"JP801": "T485", "JP802": "TCAN", "D802": "LINK", "D803": "ACT", "D201": "STAT"}
# Test points carry their name the same way.
TP_NAMES = {"+5V": "5V", "+3V3": "3V3", "SPI_SCK": "SCK", "SPI_MOSI": "MOSI", "SPI_MISO": "MISO", "I2C_SDA": "SDA",
            "I2C_SCL": "SCL", "DRV_ENN": "ENN", "XINT_N": "XINT", "CS_DRV_EN_N": "CSD", "CS_SNS_EN_N": "CSS",
            "CAN_TX": "CTX", "CAN_RX": "CRX", "RS485_TX": "RTX", "RS485_RX": "RRX", "SPARE": "XP15"}
TEXT_H, TEXT_H_SMALL = 0.9, 0.8


def text_box(text, x, y, h, angle=0):
    """The room a silkscreen text takes, as (x0, y0, x1, y1)."""
    w, t = len(text) * h * 0.92 + 0.2, h * 1.25
    if angle in (90, 270):
        w, t = t, w
    return (x - w / 2, y - t / 2, x + w / 2, y + t / 2)


KEEPOUT += [text_box(t, x, y, TEXT_H, a) for t, x, y, a in LABELS.values()]
