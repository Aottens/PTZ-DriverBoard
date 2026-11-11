#!/usr/bin/env python3
"""Close what Freerouting leaves open on the two-layer Rev B board: a small grid router and ground stitching.

Run with KiCad's Python, from hardware/, after `board.py ses` and `board.py finish`:
  .../python3 tools/complete.py [rounds]

A round:
  1. run DRC through kicad-cli and read its unconnected items;
  2. tie the ground pours of the two layers together with vias on a 2.5 mm raster, wherever both layers carry ground
     and nothing is in the way (first round only);
  3. for every unconnected pair, find a way with A* on a 0.1 mm grid, on either layer with vias, in the track width
     and clearance of the net's class, and lay it; a ground pad that the pour does not reach is led to the nearest
     spot where the pour's main body lies;
  4. refill the zones and save.
It stops when a round has nothing left to do or changes nothing. Nothing here is trusted: check_board.py runs the
DRC again afterwards. Unlike Rev A's version it never moves a track that is already there.
"""
import fnmatch
import heapq
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from array import array

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import placement as P  # noqa: E402
import project  # noqa: E402

HW = os.path.dirname(HERE)
PCB = os.path.join(HW, "ptz-driver.kicad_pcb")
CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
OX = OY = 100.0
STEP = 0.1
NX, NY = int(P.BOARD_W / STEP) + 1, int(P.BOARD_H / STEP) + 1
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)
VIA, DRILL = 0.6, 0.3
MARGIN = 0.08                    # grid rounding of a track drawn at any angle, and a little air
PAD_VIA = 0.45                   # a via centre stays this far from any pad's edge: no via in or against a pad
FREE, SHARED = -1, -2
GREED = 2.0
VIA_COST = 30                    # in grid steps
KINDS = {"Default": (0.25, 0.2), "Power": (0.5, 0.2), "Supply": (0.5, 0.25), "Motor": (1.0, 0.25)}   # class: track, gap
KEEP = []


def mm(v):
    return pcbnew.FromMM(float(v))


def xy(v):
    return v.x / 1e6 - OX, v.y / 1e6 - OY


def cell(x, y):
    return int(round(x / STEP)), int(round(y / STEP))


def net_class(name):
    for cls, pat in project.PATTERNS:
        if fnmatch.fnmatchcase(name, pat):
            return cls
    return "Default"


class Grid:
    """For one track width and gap: which net owns each cell of each layer (its copper plus the band that keeps
    another net's track centre away), FREE or SHARED; and the same at via size, where both layers count."""

    def __init__(self, board, width, gap):
        self.width, self.gap = width, gap
        self.tracks = {layer: array("i", [FREE]) * (NX * NY) for layer in LAYERS}
        self.vias = array("i", [FREE]) * (NX * NY)
        self.nopad = bytearray(NX * NY)
        self.at_via = {}
        for fp in board.GetFootprints():
            for p in fp.Pads():
                b = p.GetBoundingBox()
                r = (b.GetLeft() / 1e6 - OX, b.GetTop() / 1e6 - OY, b.GetRight() / 1e6 - OX, b.GetBottom() / 1e6 - OY)
                both = bool(p.GetDrillSize().x)
                bare = both and p.GetNetCode() <= 0 and p.GetSizeX() <= p.GetDrillSize().x      # a mounting hole
                net = p.GetNetCode() if p.GetNetCode() > 0 else SHARED
                self.box([l for l in LAYERS if both or p.IsOnLayer(l)], r, 0.1 if bare else 0.0, net)
                self.stamp_box(self.nopad, r, PAD_VIA)
        for t in board.GetTracks():
            self.add(t)
        for hx, hy in P.HOLES:                           # bare circle around each mounting hole (BRD-01)
            self.disc(LAYERS, hx, hy, 3.5, SHARED)
        for z in board.Zones():                          # supply pours keep their place; ground pours give way and refill
            if not z.GetIsRuleArea() and z.GetNetname() != "GND":
                poly = z.Outline()
                pts = [(poly.CVertex(i).x / 1e6 - OX, poly.CVertex(i).y / 1e6 - OY) for i in range(poly.TotalVertices())]
                self.polygon([z.GetLayer()], pts, z.GetNetCode())
        e = 0.3 - gap                                    # 0.3 mm from the board edge
        for r in ((0, 0, P.BOARD_W, 0), (0, P.BOARD_H, P.BOARD_W, P.BOARD_H), (0, 0, 0, P.BOARD_H), (P.BOARD_W, 0, P.BOARD_W, P.BOARD_H)):
            self.box(LAYERS, r, e, SHARED)

    @staticmethod
    def _put(a, k, net):
        cur = a[k]
        if cur == FREE:
            a[k] = net
        elif cur != net:
            a[k] = SHARED

    def _mark(self, layers, i, j, d, half, net):
        k = j * NX + i
        if d <= half + self.gap + self.width / 2 + MARGIN:
            for layer in layers:
                self._put(self.tracks[layer], k, net)
        if d <= half + self.gap + VIA / 2 + MARGIN:
            self._put(self.vias, k, net)

    def box(self, layers, r, half, net):
        reach = half + self.gap + max(self.width, VIA) / 2 + MARGIN
        for j in range(max(0, int((r[1] - reach) / STEP)), min(NY, int((r[3] + reach) / STEP) + 2)):
            y = j * STEP
            dy = max(r[1] - y, 0, y - r[3])
            for i in range(max(0, int((r[0] - reach) / STEP)), min(NX, int((r[2] + reach) / STEP) + 2)):
                x = i * STEP
                self._mark(layers, i, j, math.hypot(max(r[0] - x, 0, x - r[2]), dy), half, net)

    def disc(self, layers, cx, cy, half, net):
        self.box(layers, (cx, cy, cx, cy), half, net)

    def segment(self, layers, a, b, half, net):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / (STEP * 0.7)))
        for s in range(n + 1):
            self.disc(layers, a[0] + (b[0] - a[0]) * s / n, a[1] + (b[1] - a[1]) * s / n, half, net)

    def polygon(self, layers, pts, net):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        for j in range(max(0, int(min(ys) / STEP)), min(NY, int(max(ys) / STEP) + 2)):
            y = j * STEP
            cuts = sorted(x1 + (y - y1) * (x2 - x1) / (y2 - y1) for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]) if (y1 > y) != (y2 > y))
            for x0, x1 in zip(cuts[0::2], cuts[1::2]):
                for i in range(max(0, int(x0 / STEP)), min(NX, int(x1 / STEP) + 2)):
                    self._mark(layers, i, j, 0.0, 0.0, net)
        for a, b in zip(pts, pts[1:] + pts[:1]):
            self.segment(layers, a, b, 0.0, net)

    @staticmethod
    def stamp_box(bits, r, reach):
        for j in range(max(0, int((r[1] - reach) / STEP)), min(NY, int((r[3] + reach) / STEP) + 2)):
            for i in range(max(0, int((r[0] - reach) / STEP)), min(NX, int((r[2] + reach) / STEP) + 2)):
                bits[j * NX + i] = 1

    def add(self, t):
        if t.Type() == pcbnew.PCB_VIA_T:
            x, y = xy(t.GetPosition())
            self.at_via[cell(x, y)] = t.GetNetCode()
            self.disc(LAYERS, x, y, t.GetWidth(pcbnew.F_Cu) / 2e6, t.GetNetCode())
            self.stamp_box(self.nopad, (x, y, x, y), 0.65)    # no second via in or against it
        elif t.GetLayer() in LAYERS:
            self.segment([t.GetLayer()], xy(t.GetStart()), xy(t.GetEnd()), t.GetWidth() / 2e6, t.GetNetCode())

    def ok(self, layer, i, j, net):
        if not (0 <= i < NX and 0 <= j < NY):
            return False
        o = self.tracks[layer][j * NX + i]
        return o == FREE or o == net

    def via_ok(self, i, j, net):
        if self.at_via.get((i, j)) == net:
            return True
        k = j * NX + i
        return (self.vias[k] == FREE or self.vias[k] == net) and not self.nopad[k]

    def clear(self, layer, a, b, net, free):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
        for s in range(n + 1):
            c = (int(round(a[0] + (b[0] - a[0]) * s / n)), int(round(a[1] + (b[1] - a[1]) * s / n)))
            if c not in free and not self.ok(layer, c[0], c[1], net):
                return False
        return True


def search(grid, net, starts, goals=None, goal=None, done=None, limit=3000000):
    """A* from any of the start cells (layer index, i, j) to any goal cell, or until done(cell) says so.
    Start and goal cells count as free: they lie in the net's own pads. Returns the path, or None."""
    free = set(starts) | set(goals or ())
    gx, gy = (goal[1], goal[2]) if goal else (None, None)

    def h(i, j):
        return 0 if goal is None else GREED * math.hypot(i - gx, j - gy)

    dist, prev = {c: 0.0 for c in starts}, {}
    heap = [(h(c[1], c[2]), 0.0, c) for c in starts]
    heapq.heapify(heap)
    seen, end = 0, None
    while heap:
        _, d, cur = heapq.heappop(heap)
        if d > dist.get(cur, 1e18):
            continue
        seen += 1
        if seen > limit:
            return None
        if (goals and cur in goals) or (done and d > 3 and done(cur)):
            end = cur
            break
        li, i, j = cur
        for di, dj, c in ((1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, 1.42), (1, -1, 1.42), (-1, 1, 1.42), (-1, -1, 1.42)):
            n = (li, i + di, j + dj)
            if n in free or (grid.ok(LAYERS[li], n[1], n[2], net) and
                             (c == 1 or (grid.ok(LAYERS[li], i + di, j, net) and grid.ok(LAYERS[li], i, j + dj, net)))):
                nd = d + c
                if nd < dist.get(n, 1e18):
                    dist[n], prev[n] = nd, cur
                    heapq.heappush(heap, (nd + h(n[1], n[2]), nd, n))
        if grid.via_ok(i, j, net):
            n = (1 - li, i, j)
            nd = d + VIA_COST
            if nd < dist.get(n, 1e18):
                dist[n], prev[n] = nd, cur
                heapq.heappush(heap, (nd + h(i, j), nd, n))
    if end is None:
        return None
    path, cur = [end], end
    while cur in prev:
        cur = prev[cur]
        path.append(cur)
    return path[::-1], free


def lay(board, grids, grid, code, path, free):
    """Turn a cell path into straight tracks and vias, on the board and in every grid."""
    made = []

    def note(item):
        board.Add(item)
        made.append(item)
        for g in grids.values():
            g.add(item)

    def via_at(i, j):
        if grid.at_via.get((i, j)) == code:
            return
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(mm(OX + i * STEP), mm(OY + j * STEP)))
        v.SetDrill(mm(DRILL))
        v.SetWidth(pcbnew.F_Cu, mm(VIA))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNetCode(code)
        note(v)

    def tracks(li, run):
        k = 0
        while k < len(run) - 1:                 # pull the staircase straight: jump as far as a clear line allows
            s = 1
            while k + 2 * s < len(run) and grid.clear(LAYERS[li], run[k], run[k + 2 * s], code, free):
                s *= 2
            if grid.clear(LAYERS[li], run[k], run[-1], code, free):
                s = len(run) - 1 - k
            p, q = run[k], run[k + s]
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(mm(OX + p[0] * STEP), mm(OY + p[1] * STEP)))
            t.SetEnd(pcbnew.VECTOR2I(mm(OX + q[0] * STEP), mm(OY + q[1] * STEP)))
            t.SetWidth(mm(grid.width))
            t.SetLayer(LAYERS[li])
            t.SetNetCode(code)
            note(t)
            k += s

    run = [(path[0][1], path[0][2])]
    for a, b in zip(path, path[1:] + [None]):
        if b is not None and b[0] == a[0]:
            run.append((b[1], b[2]))
            continue
        tracks(a[0], run)
        if b is not None:
            via_at(a[1], a[2])
            run = [(b[1], b[2])]
    return made


def drc():
    out = os.path.join(tempfile.mkdtemp(), "drc.json")
    subprocess.run([CLI, "pcb", "drc", "--format", "json", "--severity-all", "-o", out, PCB], capture_output=True)
    return json.load(open(out))


def end_of(item):
    """(net name, layer indexes, x, y, is a zone) of one end of an unconnected pair."""
    d = item["description"]
    net = re.search(r"\[([^\]]+)\]", d).group(1)
    if d.startswith("Zone"):
        return net, None, None, None, True
    layers = [0, 1] if d.startswith(("PTH", "Via")) else [1 if " on B.Cu" in d else 0]
    return net, layers, item["pos"]["x"] - OX, item["pos"]["y"] - OY, False


def main_body(board, layer):
    """The largest piece of the filled ground pour on a layer, as a point test."""
    best = None
    for z in board.Zones():
        if not z.GetIsRuleArea() and z.GetNetname() == "GND" and z.GetLayer() == layer:
            polys = z.GetFilledPolysList(layer)
            for i in range(polys.OutlineCount()):
                area = abs(polys.Outline(i).Area())
                if best is None or area > best[0]:
                    best = (area, polys, i)
    if best is None:
        return lambda x, y: False
    _, polys, idx = best
    return lambda x, y: polys.Contains(pcbnew.VECTOR2I(mm(OX + x), mm(OY + y)), idx, mm(-0.4))    # 0.4 mm inside the edge


def stitch(board, grid, code):
    """Ground vias on a 2.5 mm raster wherever both layers carry the pour's main body."""
    top, bottom = main_body(board, pcbnew.F_Cu), main_body(board, pcbnew.B_Cu)
    anywhere = [z.GetFilledPolysList(z.GetLayer()) for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname() == "GND"]
    n = 0
    for jy in range(1, int(P.BOARD_H / 2.5)):
        for ix in range(1, int(P.BOARD_W / 2.5)):
            x, y = ix * 2.5, jy * 2.5
            i, j = cell(x, y)
            pt = pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))
            on_both = sum(1 for polys in anywhere if polys.Contains(pt, -1, mm(-0.45))) >= 2
            if ((i, j) not in grid.at_via and on_both and (top(x, y) or bottom(x, y)) and grid.via_ok(i, j, code)
                    and grid.ok(LAYERS[0], i, j, code) and grid.ok(LAYERS[1], i, j, code)):
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(pt)
                v.SetDrill(mm(DRILL))
                v.SetWidth(pcbnew.F_Cu, mm(VIA))
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                v.SetNetCode(code)
                board.Add(v)
                grid.add(v)
                n += 1
    # a piece of pour that hangs on a pad but not on the main body: one via of its own, wherever the other layer has
    # ground; where there is no room for one, a spot inside the piece is handed back, for a track to the main body
    loose = []
    for z in board.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != "GND":
            continue
        polys, other = z.GetFilledPolysList(z.GetLayer()), (bottom if z.GetLayer() == pcbnew.F_Cu else top)
        areas = [abs(polys.Outline(i).Area()) for i in range(polys.OutlineCount())]
        for idx in range(polys.OutlineCount()):
            if areas[idx] == max(areas):
                continue
            bb = polys.Outline(idx).BBox()
            done = False
            for jy in range(int((bb.GetTop() / 1e6 - OY) / 0.3), int((bb.GetBottom() / 1e6 - OY) / 0.3) + 1):
                for ix in range(int((bb.GetLeft() / 1e6 - OX) / 0.3), int((bb.GetRight() / 1e6 - OX) / 0.3) + 1):
                    x, y = ix * 0.3, jy * 0.3
                    i, j = cell(x, y)
                    pt = pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))
                    if (not done and (i, j) not in grid.at_via and polys.Contains(pt, idx, mm(-0.35)) and other(x, y) and grid.via_ok(i, j, code)
                            and grid.ok(LAYERS[0], i, j, code) and grid.ok(LAYERS[1], i, j, code)):
                        v = pcbnew.PCB_VIA(board)
                        v.SetPosition(pt)
                        v.SetDrill(mm(DRILL))
                        v.SetWidth(pcbnew.F_Cu, mm(VIA))
                        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                        v.SetNetCode(code)
                        board.Add(v)
                        grid.add(v)
                        n += 1
                        done = True
            if not done:
                li = 0 if z.GetLayer() == pcbnew.F_Cu else 1
                spots = [(ix * STEP, jy * STEP) for jy in range(int((bb.GetTop() / 1e6 - OY) / STEP), int((bb.GetBottom() / 1e6 - OY) / STEP) + 1)
                         for ix in range(int((bb.GetLeft() / 1e6 - OX) / STEP), int((bb.GetRight() / 1e6 - OX) / STEP) + 1)
                         if polys.Contains(pcbnew.VECTOR2I(mm(OX + ix * STEP), mm(OY + jy * STEP)), idx, mm(-0.14))]
                if spots:
                    loose.append((li, *spots[len(spots) // 2]))
    return n, loose


def one_round(n):
    report = drc()
    todo = report.get("unconnected_items", [])
    print(f"round {n}: {len(todo)} unconnected, {len(report.get('violations', []))} violations")
    if not todo and n > 1:
        return 0
    board = pcbnew.LoadBoard(PCB)
    codes = {str(name): net.GetNetCode() for name, net in board.GetNetsByName().items()}
    grids = {}

    def grid_for(name):
        kind = KINDS[net_class(name)]
        if kind not in grids:
            grids[kind] = Grid(board, *kind)
            for item in made_all:                 # what this round laid before the grid existed
                grids[kind].add(item)
        return grids[kind]

    made_all, changed = [], 0
    k, loose = stitch(board, grid_for("GND"), codes["GND"])
    changed += k
    print(f"  {k} stitching vias, {len(loose)} loose pieces of pour")
    body = {0: main_body(board, pcbnew.F_Cu), 1: main_body(board, pcbnew.B_Cu)}
    for u in todo:
        a, b = (end_of(i) for i in u["items"])
        if a[4] and b[4]:
            continue                              # two pieces of pour: the stitching vias are the cure
        if a[4]:
            a, b = b, a
        name, grid, code = a[0], grid_for(a[0]), codes[a[0]]
        starts = [(li, *cell(a[2], a[3])) for li in a[1]]
        if b[4]:                                  # to the pour: any spot in its main body will do
            found = search(grid, code, starts, done=lambda c: body[c[0]](c[1] * STEP, c[2] * STEP))
        else:
            goals = [(li, *cell(b[2], b[3])) for li in b[1]]
            found = search(grid, code, starts, goals=set(goals), goal=goals[0])
        if not found:
            print(f"  no way: {name} ({a[2]:.1f}, {a[3]:.1f}) to " + ("the pour" if b[4] else f"({b[2]:.1f}, {b[3]:.1f})"))
            continue
        made = lay(board, grids, grid, code, *found)
        made_all += made
        changed += 1
        print(f"  {name}: {len(made)} pieces from ({a[2]:.1f}, {a[3]:.1f})")
    grid, code = grid_for("GND"), codes["GND"]
    for li, x, y in loose:                        # a track from inside the loose piece to the pour's main body
        found = search(grid, code, [(li, *cell(x, y))], done=lambda c: body[c[0]](c[1] * STEP, c[2] * STEP))
        if found:
            made_all += lay(board, grids, grid, code, *found)
            changed += 1
        else:
            print(f"  no way: GND pour piece at ({x:.1f}, {y:.1f})")
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    project.patch()
    return changed


if __name__ == "__main__":
    if sys.argv[1:2] == ["--round"]:              # one round per process: KiCad's Python does not survive loading a board twice
        sys.exit(min(one_round(int(sys.argv[2])), 250))
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    for n in range(1, rounds + 1):
        if not subprocess.run([sys.executable, os.path.abspath(__file__), "--round", str(n)]).returncode:
            break
    r = drc()
    print(f"left: {len(r.get('unconnected_items', []))} unconnected, {len(r.get('violations', []))} violations")
