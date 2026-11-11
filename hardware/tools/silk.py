"""Silkscreen for the PTZ driver board (BRD-09). Called by board.py finish.

Top side: a name at every connector, jumper, LED, button and test point, plus and minus at the supply input.
Each text goes to the free spot nearest its part: clear of pads, of every part's body and of other texts.
Bottom side: the board's name, revision and date, and the pin order of every port, since the top has no room for it.
Pin 1 marks and polarity marks come with the footprints themselves.
"""
import math

import pcbnew

OX = OY = 100.0
H_NAME, H_SMALL = 0.9, 0.8          # text heights, mm; JLC wants at least 0.8 mm high and 0.15 mm stroke
BOARD = "PTZ DRIVER  REV A  2026-11-10"

NAMES = {  # reference -> text beside it
    "J101": "12-24V", "J301": "M1", "J401": "M2", "J501": "M3", "J601": "M4", "J302": "S1", "J402": "S2", "J502": "S3",
    "J602": "S4", "J303": "X1", "J403": "X2", "J503": "X3", "J603": "X4", "J801": "ETH", "J802": "RS485", "J803": "CAN",
    "J901": "CAM", "J902": "FAN", "J201": "USB", "J202": "I2C", "JP801": "T485", "JP802": "TCAN", "SW201": "BOOT",
    "D201": "STAT", "D802": "LINK", "D803": "ACT",
}
PAD_MARKS = [("J101", "1", "+"), ("J101", "2", "-"), ("JP901", "1", "5V"), ("JP901", "3", "VM")]
KEEP_REF = ("U", "Q", "L", "F", "Y")        # references that stay on the silkscreen if they find room
LEGEND = [
    BOARD,
    "J101 SUPPLY 12-24V: 1 PLUS  2 GND",
    "M1-M4 MOTOR: 1 A1  2 A2  3 B2  4 B1",
    "S1-S4 SENSOR 3V3: 1 3V3  2 GND  3 SCK  4 MOSI  5 MISO  6 CS  7 HOME",
    "X1-X4 EXT DRIVER 5V: 1 5V  2 STEP  3 DIR  4 GND",
    "ETH TO MAGJACK: 1 TCT  2 GND  3 TD+  4 TD-  5 RD+  6 RD-  7 RCT",
    "RS485: 1 A  2 B  3 GND  4 GND     CAN: 1 H  2 L  3 GND  4 GND",
    "CAM OPEN DRAIN: 1 TALLY  2 REC  3 GND  4 GND",
    "FAN: 1 PLUS  2 SWITCHED MINUS     I2C 3V3: 1 GND  2 3V3  3 SDA  4 SCL",
    "TP: ENN MOTORS OFF WHEN HIGH   CSD CSS SELECT STROBES   XINT EXPANDER IRQ",
    "T485 TCAN: 120R TERMINATORS   ANTENNA PLUG: W.FL / MHF3, NOT U.FL",
]


def _mm(v):
    return pcbnew.FromMM(float(v))


def _text(board, s, x, y, h, layer=pcbnew.F_SilkS, angle=0, mirror=False, left=False):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(_mm(h), _mm(h)))
    t.SetTextThickness(_mm(0.16 if h >= 0.9 else 0.15))
    t.SetPosition(pcbnew.VECTOR2I(_mm(OX + x), _mm(OY + y)))
    t.SetTextAngleDegrees(angle)
    t.SetMirrored(mirror)
    if left:
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(t)
    return t


def _box(s, x, y, h, angle):
    w = len(s) * h * 0.92 + 0.2
    hh = h * 1.25
    if angle in (90, 270):
        w, hh = hh, w
    return (x - w / 2, y - hh / 2, x + w / 2, y + hh / 2)


def _hit(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def draw(board):
    bb = board.GetBoardEdgesBoundingBox()
    w, h = bb.GetWidth() / 1e6 - 0.1, bb.GetHeight() / 1e6 - 0.1
    solid = []     # where a text may not go: pads with their mask opening, part bodies, holes
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}

    def rect(b, grow=0.0):
        return (b.GetLeft() / 1e6 - OX - grow, b.GetTop() / 1e6 - OY - grow, b.GetRight() / 1e6 - OX + grow, b.GetBottom() / 1e6 - OY + grow)

    for fp in fps.values():
        cy = fp.GetCourtyard(pcbnew.F_CrtYd)
        if cy.OutlineCount():
            solid.append(rect(cy.BBox()))
        for p in fp.Pads():
            solid.append(rect(p.GetBoundingBox(), 0.2))
    placed, missed = [], []

    def put(s, cx, cy, h_text, reach=6.0, ref=""):
        """Place s as near (cx, cy) as it fits; the anchor itself is usually inside a part."""
        best = None
        for angle, bias in ((0, 0.0), (90, 0.5)):       # upright text is preferred; turned text must be clearly nearer
            for ring in range(int(reach / 0.25) + 1):
                r = ring * 0.25
                if best and r + bias >= best[0]:
                    break
                n = max(1, int(2 * math.pi * r / 0.3))
                spot = None
                for k in range(n):
                    x, y = cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)
                    b = _box(s, x, y, h_text, angle)
                    if b[0] < 0.4 or b[1] < 0.4 or b[2] > w - 0.4 or b[3] > h - 0.4:
                        continue
                    if any(_hit(b, o) for o in solid) or any(_hit(b, o) for o in placed):
                        continue
                    spot = (r + bias, x, y, angle, b)
                    break
                if spot:
                    best = spot
                    break
        if not best:
            missed.append(f"{ref}:{s}")
            return None
        _, x, y, angle, b = best
        placed.append(b)
        return _text(board, s, x, y, h_text, angle=angle)

    def centre(fp):
        c = fp.GetCourtyard(pcbnew.F_CrtYd).BBox().GetCenter()
        return c.x / 1e6 - OX, c.y / 1e6 - OY

    import json
    import os
    import placement as P
    tp_fixed = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tp_labels.json")))
    for ref, (s, x, y, angle) in list(P.LABELS.items()) + list(tp_fixed.items()):     # texts with a reserved place
        hh = H_SMALL if ref.startswith("TP") else H_NAME
        placed.append(_box(s, x, y, hh, angle))
        _text(board, s, x, y, hh, angle=angle)
    for ref, name in NAMES.items():
        if ref not in P.LABELS and ref not in tp_fixed:
            put(name, *centre(fps[ref]), H_NAME, ref=ref)
    for ref, pad, s in PAD_MARKS:
        p = [q for q in fps[ref].Pads() if q.GetNumber() == pad][0].GetPosition()
        put(s, p.x / 1e6 - OX, p.y / 1e6 - OY, H_NAME, ref=ref)
    for ref, fp in sorted(fps.items()):
        fp.Reference().SetVisible(False)
    for ref, fp in sorted(fps.items()):
        if ref.rstrip("0123456789") in KEEP_REF:
            put(ref, *centre(fp), H_SMALL, reach=max(fp.GetCourtyard(pcbnew.F_CrtYd).BBox().GetWidth(), fp.GetCourtyard(pcbnew.F_CrtYd).BBox().GetHeight()) / 2e6 + 2.0, ref=ref)
    # bottom side: mirrored, so it reads normally when the board is turned over about its long axis
    for i, line in enumerate(LEGEND):
        _text(board, line, w - 6.0, 22.0 + 2.1 * i, 1.0 if i else 1.3, layer=pcbnew.B_SilkS, mirror=True, left=True)
    must = [m for m in missed if not m.split(":")[0].rstrip("0123456789") in KEEP_REF]
    print(f"silkscreen: {len(placed)} texts placed" + (f"; no room for {', '.join(missed)}" if missed else ""))
    assert not must, f"no room on the silkscreen for: {must}"
