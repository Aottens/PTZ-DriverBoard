"""Silkscreen for the PTZ driver board, Rev B (BRD-09). Called by board.py finish.

Top side: a name at every connector, socket, fuse, jumper and test point, plus and minus and the voltage range at the
supply input. Each text goes to the free spot nearest its part: clear of pads, of every part's courtyard and of other
texts; a name that belongs inside a module's outline (the module covers it) is given its place in INSIDE.
Bottom side: the board's name, revision and date, and the pin order of every connector, since the top has no room.
Pin 1 marks and polarity marks come with the footprints themselves.
"""
import math

import pcbnew

OX = OY = 100.0
H_NAME, H_SMALL = 1.0, 0.8          # text heights, mm; JLC wants at least 0.8 mm high and 0.15 mm stroke
BOARD = "PTZ DRIVER  REV B  2026-11-11"

NAMES = {  # reference -> text beside it
    "J101": "11-17V", "F101": "F1 T5A", "F102": "F2 T1A", "U101": "5V REG", "J801": "FAN", "J701": "I2C",
    "JP101": "VSNS", "JP701": "PU", "D101": "TVS", "D103": "TVS", "RT801": "NTC",
}
for n in (1, 2, 3, 4):
    a = n + 2
    NAMES.update({f"J{a}01": f"M{n}", f"J{a}02": f"H{n}", f"J{a}03": f"S{n}", f"JP{a}04": "PU", f"JP{a}02": "SPI"})
# (reference, pad, text): a mark at one pad
PAD_MARKS = [("JP101", "1", "3V3"), ("JP101", "3", "5V"), ("U101", "1", "IN"), ("U101", "3", "OUT"), ("J801", "1", "+5V")]
# texts with a fixed place, inside a module's outline or along an edge: (text, x, y, angle, height)
INSIDE = [("ESP32-S3-DEVKITC-1", 30.0, 46.3, 0, 1.2), ("USB", 3.4, 52.0, 90, 1.2), ("ANT", 58.0, 45.0, 0, 1.0),
          ("WIZ850IO", 84.0, 58.0, 0, 1.2), ("RJ45", 95.3, 60.0, 90, 1.2), ("3V3", 61.3, 43.4, 90, 0.8), ("5V", 10.5, 47.4, 90, 0.8),
          ("+", 89.1, 45.5, 0, 1.2), ("-", 89.1, 41.9, 0, 1.2)]      # the last two: beside pin 1 and pin 2 of the supply connector
LEGEND = [      # at most 52 characters a line: it has to fit between the MCU module's pin rows
    BOARD,
    "SUPPLY 11-17V: 1 PLUS  2 GND",
    "FUSES TR5 5.08MM: F1 MOTORS T5A  F2 LOGIC T1A",
    "M1-M4 MOTOR: 1-2 ONE COIL  3-4 THE OTHER",
    "S1-S4 AND I2C: 1 VSNS  2 GND  3 SDA  4 SCL",
    "H1-H4 HOME: 1 VSNS  2 GND  3 SWITCH TO GND",
    "FAN, 5V ONLY: 1 PLUS 5V  2 SWITCHED MINUS",
    "VSNS: 3V3 OR 5V FOR ALL SENSOR AND HOME PLUGS",
    "PU: I2C PULL-UPS. CLOSED JUMPER 4K7, OPEN ONE 2K2",
    "5V REG: TSR 1-2450 OR K7805-1000R3. NOT A 7805",
]
LEGEND_2 = [    # under the row of drivers
    "DRIVER SOCKETS: TMC2240 ON SPI = THE 3 SPI JUMPERS CLOSED.  TMC2209 ON UART = CUT THE 3 OF THAT SOCKET",
    "ANTENNA PLUG ON THE ESP32 MODULE: U.FL        ETHERNET MODULE: SOLDER IT IN, NO TALL SOCKET",
]


def _mm(v):
    return pcbnew.FromMM(float(v))


def _text(board, s, x, y, h, layer=pcbnew.F_SilkS, angle=0, mirror=False, left=False):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(_mm(h), _mm(h)))
    t.SetTextThickness(_mm(0.15 if h < 1.0 else 0.17))
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
    import placement as P
    bb = board.GetBoardEdgesBoundingBox()
    w, h = bb.GetWidth() / 1e6 - 0.1, bb.GetHeight() / 1e6 - 0.1
    solid = []     # where a text may not go: pads with their mask opening, courtyards, vias, holes
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}

    def rect(b, grow=0.0):
        return (b.GetLeft() / 1e6 - OX - grow, b.GetTop() / 1e6 - OY - grow, b.GetRight() / 1e6 - OX + grow, b.GetBottom() / 1e6 - OY + grow)

    for fp in fps.values():
        cy = fp.GetCourtyard(pcbnew.F_CrtYd)
        for i in range(cy.OutlineCount()):
            solid.append(rect(cy.Outline(i).BBox()))
        for p in fp.Pads():
            solid.append(rect(p.GetBoundingBox(), 0.2))
        for g in fp.GraphicalItems():                      # the footprints' own silkscreen
            if g.GetLayer() == pcbnew.F_SilkS:
                solid.append(rect(g.GetBoundingBox(), 0.05))
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            solid.append(rect(t.GetBoundingBox(), 0.1))
    placed, missed = [], []

    def put(s, cx, cy, h_text, reach=14.0, ref=""):
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

    for fp in fps.values():
        fp.Reference().SetVisible(False)
    for s, x, y, angle, hh in INSIDE:
        placed.append(_box(s, x, y, hh, angle))
        _text(board, s, x, y, hh, angle=angle)
    for k, x in enumerate(P.XK):                       # inside each driver socket: its name and which corner is which
        for s, tx, ty, hh in ((f"DRIVER {k + 1}", x + 9.0, 19.3, 1.2), ("VM", x + 0.3, 16.6, 0.8), ("EN", x + 3.0, 23.6, 0.8),
                              ("DIR", x + 17.3, 23.6, 0.8), ("GND", x + 17.2, 17.2, 0.8)):
            placed.append(_box(s, tx, ty, hh, 0))
            _text(board, s, tx, ty, hh)
    for ref, name in NAMES.items():
        if not put(name, *centre(fps[ref]), H_NAME, ref=ref):       # a smaller text finds room where the larger does not
            missed.pop()
            put(name, *centre(fps[ref]), H_SMALL, ref=ref)
    for ref, pad, s in PAD_MARKS:
        p = [q for q in fps[ref].Pads() if q.GetNumber() == pad][0].GetPosition()
        put(s, p.x / 1e6 - OX, p.y / 1e6 - OY, H_SMALL, ref=ref)
    for ref, fp in sorted(fps.items()):                # test points carry their net's name
        if ref.startswith("TP"):
            net = fp.Pads()[0].GetNetname()
            put(P.TP_NAMES.get(net, net), *centre(fp), H_SMALL, ref=ref)
    put(BOARD, 50.0, 35.0, H_NAME, reach=30.0, ref="board")
    # bottom side: mirrored, so it reads normally when the board is turned over about its long axis
    for i, line in enumerate(LEGEND):
        _text(board, line, 59.5, 43.6 + 1.85 * i, 1.0, layer=pcbnew.B_SilkS, mirror=True, left=True)
    for i, line in enumerate(LEGEND_2):
        _text(board, line, 93.0, 16.2 + 1.9 * i, 0.8, layer=pcbnew.B_SilkS, mirror=True, left=True)
    print(f"silkscreen: {len(placed)} texts placed" + (f"; no room for {', '.join(missed)}" if missed else ""))
    assert not missed, f"no room on the silkscreen for: {missed}"
