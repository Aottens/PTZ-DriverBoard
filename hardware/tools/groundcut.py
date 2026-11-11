#!/usr/bin/env python3
"""How much ground copper joins two groups of pads: the narrowest total cross-section, in mm (BRD-13).

The filled ground pours, ground tracks and ground pads of both layers are put on a 0.25 mm raster. Every step from
one cell to its neighbour carries one unit; a via joins the layers with two units (0.5 mm), a plated hole with
one unit per cell of its drill. The largest flow from one group of pads to the other, times the cell size, is the width of copper that
any cut between them must go through (max-flow = min-cut). It counts steps along the axes, so a slanted neck reads
up to 1.4 times too wide: a comparison between layouts, not a current rating.

Run from hardware/ with KiCad's Python:  tools/groundcut.py            prints the figures check_board.py uses
"""
import os
import sys
from array import array
from collections import deque

import pcbnew

STEP = 0.25
OX = OY = 100.0
W, H = 400, 320                      # cells: 100 x 80 mm
VIA_UNITS = 2
BIG = 10 ** 6


def raster(board):
    """copper[layer] as bytearrays, and link[cell] = units between the layers at that cell."""
    copper = [bytearray(W * H), bytearray(W * H)]
    link = array("i", [0]) * (W * H)
    for li, layer in enumerate((pcbnew.F_Cu, pcbnew.B_Cu)):
        fills = [z.GetFilledPolysList(layer) for z in board.Zones()
                 if not z.GetIsRuleArea() and z.GetNetname() == "GND" and z.GetLayer() == layer]
        for j in range(H):
            y = int((OY + (j + 0.5) * STEP) * 1e6)
            for i in range(W):
                pt = pcbnew.VECTOR2I(int((OX + (i + 0.5) * STEP) * 1e6), y)
                if any(f.Contains(pt) for f in fills):
                    copper[li][j * W + i] = 1
    for t in board.GetTracks():
        if t.GetNetname() != "GND":
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            k = cell(p)
            link[k] = max(link[k], VIA_UNITS)
            copper[0][k] = copper[1][k] = 1
        else:                                            # a track: the cells along its centre line
            li = 0 if t.GetLayer() == pcbnew.F_Cu else 1
            a, b = t.GetStart(), t.GetEnd()
            n = max(1, int(t.GetLength() / 1e6 / (STEP / 2)))
            for s in range(n + 1):
                copper[li][cell(pcbnew.VECTOR2I(a.x + (b.x - a.x) * s // n, a.y + (b.y - a.y) * s // n))] = 1
    add_pads(board, copper, link)
    return copper, link


def cell(p):
    i = min(W - 1, max(0, int((p.x / 1e6 - OX) / STEP)))
    j = min(H - 1, max(0, int((p.y / 1e6 - OY) / STEP)))
    return j * W + i


def covered(p):
    """The cells under a pad, and those inside its drill."""
    c, r = p.GetPosition(), p.GetBoundingBox()
    drill = p.GetDrillSize().x / 2
    pad, hole = [], []
    for j in range(max(0, int((r.GetTop() / 1e6 - OY) / STEP)), min(H, int((r.GetBottom() / 1e6 - OY) / STEP) + 1)):
        for i in range(max(0, int((r.GetLeft() / 1e6 - OX) / STEP)), min(W, int((r.GetRight() / 1e6 - OX) / STEP) + 1)):
            x, y = int((OX + (i + 0.5) * STEP) * 1e6), int((OY + (j + 0.5) * STEP) * 1e6)
            if p.HitTest(pcbnew.VECTOR2I(x, y)):
                pad.append(j * W + i)
                if drill and (x - c.x) ** 2 + (y - c.y) ** 2 <= drill ** 2:
                    hole.append(j * W + i)
    return pad, hole


def pad_cells(board, names):
    """Every cell under the named pads ("J101.2"), on the layers the pad is on."""
    out = []
    for name in names:
        ref, num = name.split(".")
        for p in board.FindFootprintByReference(ref).Pads():
            if p.GetNumber() == num:
                assert p.GetNetname() == "GND", f"{name} is on {p.GetNetname()}"
                layers = [0, 1] if p.GetDrillSize().x else [0 if p.IsOnLayer(pcbnew.F_Cu) else 1]
                out += [li * W * H + k for li in layers for k in covered(p)[0]]
    return out


def add_pads(board, copper, link):
    """Ground pads are copper; a plated hole joins the layers with one unit per cell of its drill (its barrel)."""
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == "GND":
                pad, hole = covered(p)
                for li in ([0, 1] if p.GetDrillSize().x else [0 if p.IsOnLayer(pcbnew.F_Cu) else 1]):
                    for k in pad:
                        copper[li][k] = 1
                for k in hole:
                    link[k] = max(link[k], 1)


def max_flow(copper, link, sources, sinks):
    n = W * H
    flow = {}                                            # (u, v) -> units sent from u to v, net
    src, snk = set(sources), set(sinks)

    def edges(u):
        li, k = divmod(u, n)
        i = k % W
        c = copper[li]
        if i and c[k - 1]:
            yield u - 1, 1
        if i < W - 1 and c[k + 1]:
            yield u + 1, 1
        if k >= W and c[k - W]:
            yield u - W, 1
        if k < n - W and c[k + W]:
            yield u + W, 1
        if link[k]:
            yield (1 - li) * n + k, link[k]

    total = 0
    while True:
        parent = {s: -1 for s in src}
        queue = deque(src)
        end = -1
        while queue and end < 0:
            u = queue.popleft()
            for v, cap in edges(u):
                if v not in parent and cap - flow.get((u, v), 0) > 0:
                    parent[v] = u
                    if v in snk:
                        end = v
                        break
                    queue.append(v)
        if end < 0:
            return total
        v = end
        while parent[v] != -1:                           # one unit along the path found
            u = parent[v]
            flow[(u, v)] = flow.get((u, v), 0) + 1
            flow[(v, u)] = flow.get((v, u), 0) - 1
            v = u
        total += 1


def width(board, a, b, rastered=None):
    """Millimetres of ground copper between pad groups a and b."""
    copper, link = rastered or raster(board)
    return max_flow(copper, link, pad_cells(board, a), pad_cells(board, b)) * STEP


DRIVER_GND = [f"A{n}01.{p}" for n in (3, 4, 5, 6) for p in ("10", "16")]     # GND beside VM, and GND beside VIO
PAIRS = (("the supply connector's minus (J101.2) and the eight ground pins of the driver sockets", ["J101.2"], DRIVER_GND),
         ("the MCU module's ground pins and the eight ground pins of the driver sockets", ["A201.22", "A201.23", "A201.43", "A201.44"], DRIVER_GND))

if __name__ == "__main__":
    board = pcbnew.LoadBoard(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ptz-driver.kicad_pcb"))
    r = raster(board)
    for text, a, b in PAIRS:
        print(f"{width(board, a, b, r):5.1f} mm between {text}")
