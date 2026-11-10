#!/usr/bin/env python3
"""What Freerouting does not do well on this board: a small grid router around it.

Run with KiCad's Python, from hardware/:
  .../python3 tools/complete.py fanout     before routing, on the placed board: a via to its plane for every supply pad
  .../python3 tools/complete.py [rounds]   after `board.py ses` and `board.py finish`: close what the router left open
  .../python3 tools/complete.py prune      last: remove the escape stubs and other loose ends that nothing uses

A round after routing:
  1. run DRC through kicad-cli;
  2. delete the router's mistakes it names: tracks and vias that short or crowd another net, tracks under 0.15 mm,
     vias and tracks that hang loose, anything of another net in a driver's bottom window;
  3. for every unconnected pair, route a 0.2 mm track with A* on a 0.05 mm grid; where no free way exists, lay it
     through other signal tracks, take those out up to their next pad, via or branch, and let a later round lay them
     again (a net laid this way is fixed afterwards, so the pushing ends). The track runs on the top or bottom layer, or on
     inner layer 2 outside the VM plane where those two are full; for a net
     that has a plane (GND, +3V3, VM) instead walk to the nearest free spot over the plane and drop a via;
  4. refill the zones and save.
It stops when a round changes nothing. Nothing here is trusted: check_board.py runs the DRC again afterwards.
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
STEP = 0.05                      # grid, mm: fine enough to leave a 0.5 mm pitch pad between its neighbours
NX, NY = int(P.BOARD_W / STEP) + 1, int(P.BOARD_H / STEP) + 1
TRACK, VIA, DRILL = 0.2, 0.6, 0.3
MARGIN = 0.047                   # grid rounding of a track drawn at any angle (0.036) and a little air
PAD_VIA = 0.4                    # a via centre stays this far from any pad's edge: no via in or against a pad
FREE, SHARED = -1, -2
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In2_Cu)   # In2 only outside the VM plane, and only for what fits nowhere else
PUSH_COST = 6                    # a step through a track that must then move costs this much more
GREED = 2.5                      # weight of the distance still to go: finds a way sooner, not the shortest one
IN2_COST = 1.2                   # a step on In2 costs this much more: it cuts into the +3V3 plane
PLANE_NETS = {"GND": None, "+3V3": "+3V3", "VM": "VM"}    # net -> name of its In2 zone polygon in placement.PLANES
GRAVE = []                       # items taken off the board, kept so Python does not delete them under KiCad
PUSHED = os.path.join(HW, "route", "pushed.json")     # nets laid by pushing others out: these stay, so the pushing ends
VIA_KEEP = {(round(x, 3), round(y, 3)) for x, y in P.VM_VIAS}


def mm(v):
    return pcbnew.FromMM(float(v))


def key(t):
    """A track's place, to recognise it again after the router's session has been read in."""
    a, b = (t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)
    return (t.GetLayer(), min(a, b), max(a, b))


PRE_VIAS = set()


def preroutes():
    """The tracks laid before routing (motor outputs, bus, local connections, plane and escape stubs), read from the
    board the DSN was made of. They stay: pushing one out would cut a fine-pitch pin off behind its neighbours' vias."""
    path = os.path.join(HW, "route", "rev-a_input.kicad_pcb")
    if not os.path.exists(path):
        return set()
    global _PRE_BOARD
    _PRE_BOARD = pcbnew.LoadBoard(path)          # kept alive: freeing a second board under KiCad's Python is not safe
    PRE_VIAS.update((t.GetPosition().x, t.GetPosition().y) for t in _PRE_BOARD.GetTracks() if t.Type() == pcbnew.PCB_VIA_T)
    return {key(t) for t in _PRE_BOARD.GetTracks() if t.Type() != pcbnew.PCB_VIA_T}


def xy(v):
    return v.x / 1e6 - OX, v.y / 1e6 - OY


def cell(x, y):
    return int(round(x / STEP)), int(round(y / STEP))


def inside(poly, x, y):
    hit = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def dseg(x, y, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = 0 if dx == dy == 0 else max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - a[0] - t * dx, y - a[1] - t * dy)


class Grid:
    """Which net owns each cell, FREE or SHARED: its copper plus the band that keeps another net's track away.

    Kept twice, for a new track of a net with 0.15 mm clearance and of one with 0.2 mm (the supply and motor classes),
    and once more at via size, where both layers count.
    """

    def __init__(self, board, fixed=(), pre=()):
        self.pre = pre
        # nets whose tracks stay where they are: supplies, motor outputs, the drivers' bus, and whatever was laid by
        # pushing another track out earlier (fixed). Every other track may be pushed out and routed again.
        self.firm = {n.GetNetCode() for name, n in board.GetNetsByName().items()
                     if str(name) in PLANE_NETS or str(name) in BUS or str(name) in fixed or fnmatch.fnmatchcase(str(name), "M?_??")}
        self.wide = {n.GetNetCode() for name, n in board.GetNetsByName().items()
                     if any(fnmatch.fnmatchcase(str(name), pat) for cls, pat in project.PATTERNS)}
        new = lambda: array("i", [FREE]) * (NX * NY)  # noqa: E731
        self.tracks = [{layer: new() for layer in LAYERS} for _ in range(2)]     # [0]: 0.15 mm nets, [1]: 0.2 mm nets
        self.vias = [new(), new()]
        self.solid = [{layer: new() for layer in LAYERS} for _ in range(2)]      # the same, without the tracks that may move
        self.vsolid = [new(), new()]
        self.nopad = bytearray(NX * NY)          # 1 where a via would sit in or against a pad
        self.novia = bytearray(NX * NY)          # 1 where only a GND via may go (under a driver)
        self.k = 0
        for fp in board.GetFootprints():
            for p in fp.Pads():
                b = p.GetBoundingBox()
                r = (b.GetLeft() / 1e6 - OX, b.GetTop() / 1e6 - OY, b.GetRight() / 1e6 - OX, b.GetBottom() / 1e6 - OY)
                dist = lambda x, y, r=r: math.hypot(max(r[0] - x, 0, x - r[2]), max(r[1] - y, 0, y - r[3]))  # noqa: E731
                both = bool(p.GetDrillSize().x)
                self.shape([l for l in LAYERS if both or p.IsOnLayer(l)], r, dist, 0.0, p.GetNetCode() if p.GetNetCode() > 0 else SHARED)
                self.stamp(self.nopad, r, dist, PAD_VIA)
            if fp.GetValue().startswith("TMC5240"):      # the bare window under a driver: ground only (BRD-11)
                x, y = xy(fp.GetPosition())
                r = (x - 2.9, y - 2.9, x + 2.9, y + 2.9)
                dist = lambda px, py, r=r: math.hypot(max(r[0] - px, 0, px - r[2]), max(r[1] - py, 0, py - r[3]))  # noqa: E731
                self.shape([pcbnew.B_Cu], r, dist, -0.2, SHARED, vias=False)
                self.stamp(self.novia, r, dist, 0.3)
        for t in board.GetTracks():
            self.add(t)
        for hx, hy in P.HOLES:                           # bare circle around each mounting hole (BRD-01)
            self.shape(LAYERS, (hx, hy, hx, hy), lambda x, y, hx=hx, hy=hy: math.hypot(x - hx, y - hy), 3.35, SHARED)
        for net, pts in P.POURS:                         # the input pours on the top layer keep their place
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            dist = lambda x, y, pts=pts: 0 if inside(pts, x, y) else min(dseg(x, y, pts[k], pts[(k + 1) % len(pts)]) for k in range(len(pts)))  # noqa: E731
            self.shape([pcbnew.F_Cu], (min(xs), min(ys), max(xs), max(ys)), dist, 0.0, board.GetNetcodeFromNetname(net))
        vm = dict(P.PLANES)["VM"]                        # the motor supply plane stays whole: no signal tracks in it
        xs, ys = [p[0] for p in vm], [p[1] for p in vm]
        dist = lambda x, y: 0 if inside(vm, x, y) else min(dseg(x, y, vm[k], vm[(k + 1) % len(vm)]) for k in range(len(vm)))  # noqa: E731
        self.shape([pcbnew.In2_Cu], (min(xs), min(ys), max(xs), max(ys)), dist, 0.3, SHARED, vias=False)
        for r in ((0, 0, P.BOARD_W, 0), (0, P.BOARD_H, P.BOARD_W, P.BOARD_H), (0, 0, 0, P.BOARD_H), (P.BOARD_W, 0, P.BOARD_W, P.BOARD_H)):
            dist = lambda x, y, r=r: math.hypot(max(r[0] - x, 0, x - r[2]), max(r[1] - y, 0, y - r[3]))  # noqa: E731
            self.shape(LAYERS, r, dist, 0.15, SHARED)    # 0.3 mm from the edge with the 0.15 mm gap on top

    @staticmethod
    def _put(a, k, net):
        cur = a[k]
        if cur == FREE:
            a[k] = net
        elif cur != net:
            a[k] = SHARED

    def shape(self, layers, box, dist, half, net, vias=True, soft=False):
        """Copper of `net` on `layers`: every point within `half` of dist() == 0, inside `box`. soft: may be pushed out."""
        gap = [0.2 if net in self.wide else 0.15, 0.2]
        rt = [half + g + TRACK / 2 + MARGIN for g in gap]
        rv = [half + g + VIA / 2 + MARGIN for g in gap]
        reach = max(rv)
        for j in range(max(0, int((box[1] - reach) / STEP)), min(NY, int((box[3] + reach) / STEP) + 2)):
            for i in range(max(0, int((box[0] - reach) / STEP)), min(NX, int((box[2] + reach) / STEP) + 2)):
                d = dist(i * STEP, j * STEP)
                if d > reach:
                    continue
                k = j * NX + i
                for n in (0, 1):
                    if vias and d <= rv[n]:
                        self._put(self.vias[n], k, net)
                        if not soft:
                            self._put(self.vsolid[n], k, net)
                    if d <= rt[n]:
                        for layer in layers:
                            self._put(self.tracks[n][layer], k, net)
                            if not soft:
                                self._put(self.solid[n][layer], k, net)

    @staticmethod
    def stamp(bits, box, dist, reach):
        for j in range(max(0, int((box[1] - reach) / STEP)), min(NY, int((box[3] + reach) / STEP) + 2)):
            for i in range(max(0, int((box[0] - reach) / STEP)), min(NX, int((box[2] + reach) / STEP) + 2)):
                if dist(i * STEP, j * STEP) <= reach:
                    bits[j * NX + i] = 1

    def add(self, t):
        if t.Type() == pcbnew.PCB_VIA_T:
            x, y = xy(t.GetPosition())
            self.shape(LAYERS, (x, y, x, y), lambda px, py: math.hypot(px - x, py - y), t.GetWidth(pcbnew.F_Cu) / 2e6, t.GetNetCode())
            self.stamp(self.nopad, (x, y, x, y), lambda px, py: math.hypot(px - x, py - y), 0.62)    # no second via in or against it
        elif t.GetLayer() in LAYERS:
            a, b = xy(t.GetStart()), xy(t.GetEnd())
            box = (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
            self.shape([t.GetLayer()], box, lambda px, py: dseg(px, py, a, b), t.GetWidth() / 2e6, t.GetNetCode(),
                       soft=t.GetNetCode() not in self.firm and key(t) not in self.pre)

    def use(self, net):
        self.k = 1 if net in self.wide else 0

    def ok(self, layer, i, j, net, push=False):
        if not (0 <= i < NX and 0 <= j < NY):
            return False
        o = (self.solid if push else self.tracks)[self.k][layer][j * NX + i]
        return o == FREE or o == net

    def via_ok(self, i, j, net, gnd, push=False):
        k = j * NX + i
        o = (self.vsolid if push else self.vias)[self.k][k]
        return (o == FREE or o == net) and not self.nopad[k] and (gnd or not self.novia[k])

    def clear(self, layer, a, b, net, first, push=False):
        """Is the straight line between two cells free for this net? `first` is the cell in the starting pad."""
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
        for s in range(n + 1):
            c = (int(round(a[0] + (b[0] - a[0]) * s / n)), int(round(a[1] + (b[1] - a[1]) * s / n)))
            if c != first and not self.ok(layer, c[0], c[1], net, push):
                return False
        return True


def search(grid, net, start, goal=None, plane=None, gnd=False, limit=2000000, anchors=(), flat=False, push=False):
    """A* from (layer index, i, j). To the goal cell on its layer, or, with plane set, to the nearest spot for a plane
    via or to a via that is already there for this net (anchors).

    Returns the path as [(layer index, i, j)], with a layer change marking a via.
    """
    def h(i, j):
        return 0 if goal is None else GREED * math.hypot(i - goal[1], j - goal[2])

    grid.use(net)
    dist, prev = {start: 0.0}, {}
    heap = [(h(start[1], start[2]), 0.0, start)]
    seen, found = 0, None
    while heap:
        _, d, cur = heapq.heappop(heap)
        if d > dist.get(cur, 1e18):
            continue
        li, i, j = cur
        seen += 1
        if seen > limit:
            return None
        if goal is not None and cur == goal:
            break
        if goal is None:                     # plane search: a via already there for this net beats a new one within 1.2 mm
            if found and d >= found[0]:
                goal = found[1]
                break
            if d > 0 and (i, j) in anchors:
                goal = cur
                break
            if not found and d * STEP > 0.3 and grid.via_ok(i, j, net, gnd) and plane(i * STEP, j * STEP):
                found = (d + 1.2 / STEP, cur)
        for di, dj, c in ((1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, 1.42), (1, -1, 1.42), (-1, 1, 1.42), (-1, -1, 1.42)):
            n = (li, i + di, j + dj)
            if grid.ok(LAYERS[li], n[1], n[2], net, push) and (c == 1 or (grid.ok(LAYERS[li], i + di, j, net, push) and grid.ok(LAYERS[li], i, j + dj, net, push))):
                if push and not grid.ok(LAYERS[li], n[1], n[2], net):
                    c *= PUSH_COST               # through a track that will have to move
                nd = d + (c * IN2_COST if li == 2 else c)
                if nd < dist.get(n, 1e18):
                    dist[n], prev[n] = nd, cur
                    heapq.heappush(heap, (nd + h(n[1], n[2]), nd, n))
        if not flat and grid.via_ok(i, j, net, gnd, push):
            for lj in range(len(LAYERS)):
                n = (lj, i, j)
                nd = d + (2.5 if grid.via_ok(i, j, net, gnd) else 2.5 * PUSH_COST) / STEP
                if lj != li and nd < dist.get(n, 1e18):
                    dist[n], prev[n] = nd, cur
                    heapq.heappush(heap, (nd + h(i, j), nd, n))
    else:
        if not found:
            return None
        goal = found[1]
    path, cur = [goal], goal
    while cur != start:
        cur = prev[cur]
        path.append(cur)
    return path[::-1]


def lay(board, grid, net, path, end_via=False, push=False):
    """Turn a cell path into straight tracks and vias, on the board and in the grid."""
    code = net if isinstance(net, int) else net.GetNetCode()     # set by code below: a net object looked up twice came back broken
    grid.use(code)
    first = (path[0][1], path[0][2])
    made = []

    def via_at(i, j):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(mm(OX + i * STEP), mm(OY + j * STEP)))
        v.SetDrill(mm(DRILL))
        v.SetWidth(pcbnew.F_Cu, mm(VIA))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNetCode(code)
        board.Add(v)
        grid.add(v)
        made.append(v)

    def tracks(li, run):
        k = 0
        while k < len(run) - 1:                 # pull the staircase straight: jump as far as a clear line allows
            s = 1
            while k + 2 * s < len(run) and grid.clear(LAYERS[li], run[k], run[k + 2 * s], code, first, push):
                s *= 2
            if grid.clear(LAYERS[li], run[k], run[-1], code, first, push):
                s = len(run) - 1 - k
            p, q = run[k], run[k + s]
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(mm(OX + p[0] * STEP), mm(OY + p[1] * STEP)))
            t.SetEnd(pcbnew.VECTOR2I(mm(OX + q[0] * STEP), mm(OY + q[1] * STEP)))
            t.SetWidth(mm(TRACK))
            t.SetLayer(LAYERS[li])
            t.SetNetCode(code)
            board.Add(t)
            grid.add(t)
            made.append(t)
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
    if end_via:
        via_at(path[-1][1], path[-1][2])
    return made


def segdist(a, b, c, d):
    def side(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    if side(a, b, c) * side(a, b, d) < 0 and side(c, d, a) * side(c, d, b) < 0:
        return 0.0
    return min(dseg(a[0], a[1], c, d), dseg(b[0], b[1], c, d), dseg(c[0], c[1], a, b), dseg(d[0], d[1], a, b))


def rip(board, grid, made):
    """Remove the movable tracks of other nets that the new tracks and vias in `made` run into, each with the whole
    stretch it belongs to, up to the next pad, via or branch. Returns the names of the nets that lost a stretch."""
    tracks = [t for t in board.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
    hit = set()
    for n in made:
        for t in tracks:
            if t.GetNetCode() == n.GetNetCode() or t.GetNetCode() in grid.firm or key(t) in grid.pre:
                continue
            a, b = xy(t.GetStart()), xy(t.GetEnd())
            if n.Type() == pcbnew.PCB_VIA_T:
                c = xy(n.GetPosition())
                near = dseg(c[0], c[1], a, b) < VIA / 2 + t.GetWidth() / 2e6 + 0.21
            else:
                near = t.GetLayer() == n.GetLayer() and segdist(xy(n.GetStart()), xy(n.GetEnd()), a, b) < (n.GetWidth() + t.GetWidth()) / 2e6 + 0.21
            if near:
                hit.add(t.m_Uuid.AsString())
    if not hit:
        return set()
    by_id = {t.m_Uuid.AsString(): t for t in tracks}
    ends, stops = {}, set()
    for t in tracks:
        for pt in (t.GetStart(), t.GetEnd()):
            ends.setdefault((t.GetNetCode(), t.GetLayer(), pt.x, pt.y), []).append(t.m_Uuid.AsString())
    for v in board.GetTracks():
        if v.Type() == pcbnew.PCB_VIA_T:
            stops.add((v.GetNetCode(), v.GetPosition().x, v.GetPosition().y))
    pads = {}
    for fp in board.GetFootprints():
        for p in fp.Pads():
            pads.setdefault(p.GetNetCode(), []).append(p.GetBoundingBox())
    gone, todo = set(), list(hit)
    while todo:
        u = todo.pop()
        if u in gone:
            continue
        gone.add(u)
        t = by_id[u]
        for pt in (t.GetStart(), t.GetEnd()):
            there = ends[(t.GetNetCode(), t.GetLayer(), pt.x, pt.y)]
            if (len(there) == 2 and (t.GetNetCode(), pt.x, pt.y) not in stops
                    and not any(b.Contains(pt) for b in pads.get(t.GetNetCode(), ()))):
                todo += [w for w in there if w not in gone]
    names = {by_id[u].GetNetname() for u in gone}
    for u in gone:
        board.Remove(by_id[u])
        GRAVE.append(by_id[u])      # never freed while we run: deleting a removed track broke the board's net list
    return names


def over_plane(name):
    """Test for a spot where a via reaches the plane of this net, a little inside its outline."""
    zone = PLANE_NETS[name]
    if zone is None:
        return lambda x, y: True
    pts = dict(P.PLANES)[zone]
    return lambda x, y: inside(pts, x, y) and all(inside(pts, x + dx, y + dy) for dx, dy in ((0.6, 0), (-0.6, 0), (0, 0.6), (0, -0.6)))


def filled_plane(board, name):
    """The same test on the routed board: is this spot over the largest piece of the net's filled plane? Tracks on
    inner layer 2 cut pieces off the +3V3 plane; a via on such a piece reaches nothing."""
    if PLANE_NETS[name] is None:
        return lambda x, y: True
    zone = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetLayer() == pcbnew.In2_Cu and z.GetNetname() == name][0]
    fill = zone.GetFilledPolysList(pcbnew.In2_Cu)
    main = max(range(fill.OutlineCount()), key=lambda k: fill.Outline(k).Area())
    return lambda x, y: all(fill.Contains(pcbnew.VECTOR2I(mm(OX + x + dx), mm(OY + y + dy)), main)
                            for dx, dy in ((0, 0), (0.6, 0), (-0.6, 0), (0, 0.6), (0, -0.6)))


def plane_vias(board, test=over_plane):
    anchors = {}
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() in PLANE_NETS and test(t.GetNetname())(*xy(t.GetPosition())):
            anchors.setdefault(t.GetNetCode(), set()).add(cell(*xy(t.GetPosition())))
    return anchors


BUS = ("SPI_MISO", "SPI_MOSI", "SPI_SCK")     # the drivers' pins 29, 28, 27: the lowest pin gets the nearest bus line


def fanout():
    """On the placed, unrouted board, the hard nets first (CLAUDE.md): the motor outputs; every pair of pads of one
    net within 3 mm of each other; the bus the four drivers share; then a short track and a via to its plane for
    every SMD supply pad.

    Smallest supply pads first, so fine-pitch pins get out before the capacitors beside them take the room. A pad
    joins a via that is already there for its net when that is within reach.
    """
    if os.path.exists(PUSHED):
        os.remove(PUSHED)                        # a new placement starts with nothing fixed
    board = pcbnew.LoadBoard(PCB)
    grid = Grid(board)
    nets = board.GetNetsByName()
    drivers = sorted((fp for fp in board.GetFootprints() if fp.GetValue().startswith("TMC5240")), key=lambda fp: fp.GetPosition().x)
    motor, lost = [], []
    for fp in drivers:      # each motor output straight from its driver pin to its connector pin, on the top layer
        for p in fp.Pads():
            if fnmatch.fnmatchcase(p.GetNetname(), "M?_??"):
                far = [q for f in board.GetFootprints() if f.GetReference() != fp.GetReference()
                       for q in f.Pads() if q.GetNetCode() == p.GetNetCode()]
                path = search(grid, p.GetNetCode(), (0,) + cell(*xy(p.GetPosition())), goal=(0,) + cell(*xy(far[0].GetPosition())), flat=True)
                if path:
                    motor += [(t, xy(fp.GetPosition())) for t in lay(board, grid, p.GetNet(), path)]
                else:
                    lost.append(p.GetNetname())
    for t, c in motor:        # keep room beside them where they must be 0.6 mm wide: beyond 5 mm from the driver (BRD-06)
        a, b = xy(t.GetStart()), xy(t.GetEnd())
        grid.shape([pcbnew.F_Cu], (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])),
                   lambda px, py, a=a, b=b, c=c: dseg(px, py, a, b) if math.hypot(px - c[0], py - c[1]) > 4.5 else 9, 0.3, t.GetNetCode())
    print(f"motor outputs: {len(motor)} segments on the top layer; not routed: {', '.join(lost) or 'none'}")

    lines = {}              # the drivers' bus lines keep their place on the bottom layer before anything else takes it
    for k, name in enumerate(BUS):
        y = P.DRIVER_Y + 3.35 + 0.8 * k
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(mm(OX + P.AXIS_X[1] - 5.2), mm(OY + y)))
        t.SetEnd(pcbnew.VECTOR2I(mm(OX + P.AXIS_X[4] - 2.5), mm(OY + y)))
        t.SetWidth(mm(TRACK))
        t.SetLayer(pcbnew.B_Cu)
        t.SetNet(nets[name])
        board.Add(t)
        grid.add(t)
        lines[name] = t
    done, far, failed, tied = [], [], [], set()

    def is_ic(fp):
        return len([p for p in fp.Pads() if min(p.GetSize().x, p.GetSize().y) <= 450000]) >= 8

    def is_driver(fp):
        return fp.GetValue().startswith("TMC5240")

    def tie(names, want=lambda fp: True):
        anchors = plane_vias(board)
        pads = []
        for fp in board.GetFootprints():
            for p in fp.Pads():
                if (p.GetNetname() in names and not p.GetDrillSize().x and p.IsOnLayer(pcbnew.F_Cu) and want(fp)
                        and fp.GetReference() + "." + p.GetNumber() not in tied):
                    b = p.GetBoundingBox()
                    r = (b.GetLeft() / 1e6 - OX, b.GetTop() / 1e6 - OY, b.GetRight() / 1e6 - OX, b.GetBottom() / 1e6 - OY)
                    x, y = xy(p.GetPosition())
                    if any(r[0] <= i * STEP <= r[2] and r[1] <= j * STEP <= r[3] for i, j in anchors.get(p.GetNetCode(), ())):
                        continue                                  # an exposed pad that has its vias already
                    if any(net == p.GetNetname() and inside(pts, x, y) for net, pts in P.POURS):
                        continue                                  # sits in its own pour on the top layer
                    pads.append(((r[2] - r[0]) * (r[3] - r[1]), fp.GetReference(), p.GetNumber(), p.GetNetname(), x, y))
        for _, ref, num, name, x, y in sorted(pads):
            net = nets[name]
            code = net.GetNetCode()
            mine = anchors.setdefault(code, set())
            path = search(grid, code, (0,) + cell(x, y), plane=over_plane(name), gnd=name == "GND", limit=3000000, anchors=mine, flat=True)
            if not path:
                failed.append(f"{ref}.{num} {name}")
                continue
            if len(path) * STEP > 6:                         # far from its plane: a job for the router, not for a stub
                far.append(f"{ref}.{num} {name}")
                continue
            end = (path[-1][1], path[-1][2])
            lay(board, grid, net, path, end_via=end not in mine)
            mine.add(end)
            tied.add(f"{ref}.{num}")
            done.append(ref)


    by_net = {}             # what belongs together: a capacitor reaches its pin before anything passes between them
    for fp in board.GetFootprints():
        for p in fp.Pads():
            name = p.GetNetname()
            if name and name not in PLANE_NETS and not fnmatch.fnmatchcase(name, "M?_??") and p.IsOnLayer(pcbnew.F_Cu):
                by_net.setdefault(name, []).append((fp.GetReference() + "." + p.GetNumber(), xy(p.GetPosition())))
    tie({"GND", "+3V3"}, lambda fp: not is_driver(fp))    # before local tracks fence these pads in; the drivers' own pins follow their capacitors
    pairs = sorted((math.dist(a[1], b[1]), name, a, b) for name, pads in by_net.items()
                   for i, a in enumerate(pads) for b in pads[i + 1:] if math.dist(a[1], b[1]) <= 3.0)
    group = {}

    def root(k):
        while group.setdefault(k, k) != k:
            k = group[k]
        return k

    ics = {fp.GetReference() for fp in board.GetFootprints() if is_ic(fp)}
    local, wired = 0, set()
    for d, name, a, b in pairs:
        if root(a[0]) == root(b[0]):
            continue
        ra, rb = a[0].split(".")[0], b[0].split(".")[0]
        if ra == rb or (ra in ics) == (rb in ics):
            continue        # only an IC pin to the part that belongs to it: two pins of one IC, or two capacitors on
                            # one net, joined along a row of pins fence in the pins between them
        path = search(grid, nets[name].GetNetCode(), (0,) + cell(*a[1]), goal=(0,) + cell(*b[1]), limit=40000, flat=True)
        if path and len(path) * STEP <= 2 * d + 1:
            lay(board, grid, nets[name], path)
            group[root(a[0])] = root(b[0])
            wired.update((a[0], b[0]))
            local += 1

    print(f"local connections: {local} of {len(pairs)} pad pairs within 3 mm")

    touched = set(wired)                        # pads that have a track already

    def escape(want, where=lambda x, y: True, reach=4.0, bare=True):
        """A short track on the top layer and a via for IC pins that have no track yet (bare), or whose net is not
        complete yet, so the router finds them from the bottom layer or inner layer 2 instead of having to dig them
        out. `where` says where the via may land."""
        pins = []
        for fp in board.GetFootprints():
            small = [p for p in fp.Pads() if min(p.GetSize().x, p.GetSize().y) <= 450000]
            if len(small) < 8:
                continue
            for p in small:
                name, key = p.GetNetname(), fp.GetReference() + "." + p.GetNumber()
                if (name and name not in PLANE_NETS and not (name in BUS and is_driver(fp)) and not fnmatch.fnmatchcase(name, "M?_??")
                        and (key not in touched if bare else len({root(k) for k, _ in by_net.get(name, ())}) > 1)
                        and len(by_net.get(name, ())) > 1 and not p.GetDrillSize().x and want(fp, p)):
                    pins.append((not fp.GetValue().startswith("TMC5240"), min(p.GetSize().x, p.GetSize().y), fp.GetReference(),
                                 int(p.GetNumber()) if p.GetNumber().isdigit() else 0, p))
        made = 0
        for _, _, ref, num, p in sorted(pins, key=lambda t: t[:4]):
            path = search(grid, p.GetNetCode(), (0,) + cell(*xy(p.GetPosition())), plane=where, limit=400000, flat=True)
            if path and len(path) * STEP <= reach:
                lay(board, grid, p.GetNet(), path, end_via=True)
                touched.add(f"{ref}.{num}")
                made += 1
        return made

    tie({"VM"})     # the motor supply before the bus, whose tracks would otherwise fence in the 10 uF capacitors

    # the drivers' bus: three straight lines on the bottom layer just below the row of drivers, 0.8 mm apart so a via
    # fits on each, and from every driver pin a track on the top layer to a via on its line
    lost, taps = [], {}
    for fp in drivers:
        cx = xy(fp.GetPosition())[0]
        for k, name in enumerate(BUS):
            yl = P.DRIVER_Y + 3.35 + 0.8 * k
            pin = [xy(p.GetPosition()) for p in fp.Pads() if p.GetNetname() == name][0]
            path = search(grid, nets[name].GetNetCode(), (0,) + cell(*pin), limit=400000, flat=True,
                          plane=lambda x, y, yl=yl, cx=cx: abs(y - yl) < 0.6 * STEP and cx - 5.2 < x < cx - 2.5)
            if path:
                lay(board, grid, nets[name], path, end_via=True)
                taps.setdefault(name, []).append(path[-1][1:])
                touched.add(fp.GetReference() + "." + [p.GetNumber() for p in fp.Pads() if p.GetNetname() == name][0])
            else:
                lost.append(f"{name} at {fp.GetReference()}")
    for name, t in lines.items():       # trim each line to its outer taps
        ends = taps.get(name, [])
        if len(ends) < 2:
            lost.append(f"{name} line")
            continue
        t.SetStart(pcbnew.VECTOR2I(mm(OX + min(ends)[0] * STEP), mm(OY + min(ends)[1] * STEP)))
        t.SetEnd(pcbnew.VECTOR2I(mm(OX + max(ends)[0] * STEP), mm(OY + max(ends)[1] * STEP)))
    print(f"driver bus: {sum(len(e) for e in taps.values())} pins on {len(taps)} lines; not routed: {', '.join(lost) or 'none'}")

    # the drivers' own signals (chip select, enable, DIAG0, DIAG1): the bus lines wall off the bottom layer below the
    # drivers, so their vias land where inner layer 2 is free to carry them south, over the +3V3 plane
    tie({"GND", "+3V3"})        # supply pads before signal escapes: a supply pad must reach its plane, a signal has other ways
    first = escape(lambda fp, p: fp.GetValue().startswith("TMC5240"), where=over_plane("+3V3"), reach=9.0, bare=False)
    rest = escape(lambda fp, p: True, reach=1.6)      # short: a longer stub runs along the pins and shuts the others in
    print(f"escape vias: {first} driver pins, {rest} other fine-pitch signal pins")
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    project.patch()
    print(f"fanout: {len(done)} pads tied to their plane, {sum(len(a) for a in plane_vias(board).values())} plane vias in all")
    print("   left to the router, over 6 mm from their plane:", ", ".join(far) or "none")
    print("   no way out:", ", ".join(failed) or "none")


def drc(path):
    out = os.path.join(tempfile.mkdtemp(), "drc.json")
    subprocess.run([CLI, "pcb", "drc", "--format", "json", "--severity-all", "-o", out, path], capture_output=True)
    return json.load(open(out))


def end_of(item):
    """(net name, layer index or None for both, x, y, description) of a DRC item."""
    d = item["description"]
    net = re.search(r"\[([^\]]+)\]", d)
    layer = None if d.startswith("Via") or "F.Cu - B.Cu" in d or "PTH" in d else (1 if " on B.Cu" in d else 2 if " on In2.Cu" in d else 0)
    return (net.group(1) if net else None, layer, item["pos"]["x"] - OX, item["pos"]["y"] - OY, d)


def one_round(n, prune=False):
    """One round of cleaning and routing. With prune, only cleaning, and the escape stubs nobody used go too."""
    board = pcbnew.LoadBoard(PCB)
    report = drc(PCB)
    by_uuid = {t.m_Uuid.AsString(): t for t in board.GetTracks()}
    fixed = set(json.load(open(PUSHED))) if os.path.exists(PUSHED) else set()

    pre = preroutes()

    def firm(t):
        n = t.GetNetname()
        return (n in PLANE_NETS or n in BUS or n in fixed or fnmatch.fnmatchcase(n, "M?_??")
                or (t.Type() != pcbnew.PCB_VIA_T and key(t) in pre))

    doomed = set()
    for v in report["violations"]:
        if v["type"] in ("shorting_items", "clearance", "track_width", "via_dangling", "track_dangling", "items_not_allowed",
                         "tracks_crossing", "annular_width", "hole_clearance", "copper_edge_clearance"):
            items = [by_uuid[i["uuid"]] for i in v["items"] if i.get("uuid") in by_uuid]
            if v["type"] in ("via_dangling", "track_dangling") and not prune:     # a pin's way out, not used yet: it stays
                items = [t for t in items if not ((t.GetPosition().x, t.GetPosition().y) in PRE_VIAS
                                                  if t.Type() == pcbnew.PCB_VIA_T else key(t) in pre)]
            if v["type"] in ("shorting_items", "clearance", "tracks_crossing") and len(items) > 1:
                # drop one offender: a movable track before a fixed one, a track before a via, the shorter first
                items = sorted(items, key=lambda t: (firm(t), t.Type() == pcbnew.PCB_VIA_T, t.GetLength()))[:1]
            doomed.update(t.m_Uuid.AsString() for t in items
                          if not (t.Type() == pcbnew.PCB_VIA_T and tuple(round(c, 3) for c in xy(t.GetPosition())) in VIA_KEEP))
    for fp in board.GetFootprints():                      # other nets in a driver's bottom window
        if fp.GetValue().startswith("TMC5240"):
            x, y = xy(fp.GetPosition())
            for t in board.GetTracks():
                if t.GetNetname() == "GND":
                    continue
                if t.Type() == pcbnew.PCB_VIA_T:
                    px, py = xy(t.GetPosition())
                    if abs(px - x) < 3.2 and abs(py - y) < 3.2:
                        doomed.add(t.m_Uuid.AsString())
                elif t.GetLayer() == pcbnew.B_Cu:
                    (ax, ay), (bx, by) = xy(t.GetStart()), xy(t.GetEnd())
                    if min(ax, bx) < x + 2.9 and max(ax, bx) > x - 2.9 and min(ay, by) < y + 2.9 and max(ay, by) > y - 2.9:
                        doomed.add(t.m_Uuid.AsString())
    for u in doomed:
        board.Remove(by_uuid[u])
        GRAVE.append(by_uuid[u])
    if doomed:                                             # the picture changed: look again before routing
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        pcbnew.SaveBoard(PCB, board)
        project.patch()
        report = drc(PCB)        # the board in memory is what was just saved: no second load, KiCad's Python does not take it well
    if prune:
        print(f"prune: removed {len(doomed)} loose tracks and vias", flush=True)
        return len(doomed)
    grid = Grid(board, fixed, pre)
    nets = board.GetNetsByName()
    pushed = 0
    tests = {name: filled_plane(board, name) for name in PLANE_NETS}
    anchors = plane_vias(board, lambda name: tests[name])
    done = failed = 0
    notes = []
    for u in report["unconnected_items"]:
        a, b = end_of(u["items"][0]), end_of(u["items"][1])
        name = a[0]
        code = board.GetNetcodeFromNetname(name) if name else 0
        if code <= 0:
            continue
        net = code
        if name in PLANE_NETS:
            mine = anchors.setdefault(code, set())
            for e in (a, b):
                if e[4].startswith("Zone") or e[4].startswith("Via"):
                    continue
                path = search(grid, code, (e[1] or 0,) + cell(e[2], e[3]), plane=tests[name], gnd=name == "GND", anchors=mine)
                if path and (path[-1][1], path[-1][2]) in mine:
                    continue                             # this end has its via on the plane already; the other end is the loose one
                if path:
                    lay(board, grid, net, path, end_via=True)
                    mine.add((path[-1][1], path[-1][2]))
                    done += 1
                    continue
                path = search(grid, code, (e[1] or 0,) + cell(e[2], e[3]), plane=tests[name], gnd=name == "GND", anchors=mine, push=True)
                if path:
                    end = (path[-1][1], path[-1][2])
                    out = rip(board, grid, lay(board, grid, net, path, end_via=end not in mine, push=True))
                    mine.add(end)
                    done += 1
                    pushed += 1
                    notes.append(f"{name} at ({e[2]:.1f}, {e[3]:.1f}): tied to its plane by pushing out {', '.join(sorted(out)) or 'nothing'}")
                else:
                    failed += 1
                    notes.append(f"{name} at ({e[2]:.1f}, {e[3]:.1f}): no way to its plane")
            continue
        if a[4].startswith("Zone") or b[4].startswith("Zone"):
            continue
        best = None
        for la in ((a[1],) if a[1] is not None else (0, 1)):
            for lb in ((b[1],) if b[1] is not None else (0, 1)):
                best = best or search(grid, code, (la,) + cell(a[2], a[3]), goal=(lb,) + cell(b[2], b[3]))
        if best:
            lay(board, grid, net, best)
            done += 1
            continue
        for la in ((a[1],) if a[1] is not None else (0, 1)):          # no free way: push other tracks out of it
            for lb in ((b[1],) if b[1] is not None else (0, 1)):
                best = best or search(grid, code, (la,) + cell(a[2], a[3]), goal=(lb,) + cell(b[2], b[3]), push=True)
        if best:
            fixed.add(name)
            grid.firm.add(code)          # before its tracks go into the grid: nothing later in this round may cross them
            out = rip(board, grid, lay(board, grid, net, best, push=True))
            done += 1
            pushed += 1
            notes.append(f"{name}: laid by pushing out {', '.join(sorted(out)) or 'nothing'}")
        else:
            failed += 1
            notes.append(f"{name}: no path from ({a[2]:.1f}, {a[3]:.1f}) to ({b[2]:.1f}, {b[3]:.1f})")
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    project.patch()
    json.dump(sorted(fixed), open(PUSHED, "w"))
    print(f"round {n}: removed {len(doomed)} bad items, routed {done} ({pushed} by pushing), could not route {failed}", flush=True)
    for line in notes[:20]:
        print("   " + line, flush=True)
    return len(doomed) + done


if __name__ == "__main__":
    if sys.argv[1:] == ["fanout"]:
        fanout()
        sys.exit()
    if sys.argv[1:] == ["prune"]:               # at the very end: take out what hangs loose, until nothing does
        while one_round(0, prune=True):
            pass
        sys.exit()
    for n in range(1, (int(sys.argv[1]) if len(sys.argv) > 1 else 6) + 1):
        if not one_round(n):
            break
    final = drc(PCB)
    kinds = {}
    for v in final["violations"]:
        kinds[v["type"]] = kinds.get(v["type"], 0) + 1
    print(f"DRC now: {len(final['unconnected_items'])} unconnected, violations {kinds}")
