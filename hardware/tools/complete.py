#!/usr/bin/env python3
"""What Freerouting does not do well on this board: a small grid router around it.

Run with KiCad's Python, from hardware/:
  .../python3 tools/complete.py fanout     before routing, on the placed board: a via to its plane for every supply pad
  .../python3 tools/complete.py [rounds]   after `board.py ses` and `board.py finish`: close what the router left open

A round after routing:
  1. run DRC through kicad-cli;
  2. delete the router's mistakes it names: tracks and vias that short or crowd another net, tracks under 0.15 mm,
     vias and tracks that hang loose, anything of another net in a driver's bottom window;
  3. for every unconnected pair, route a 0.2 mm track on the top or bottom layer with A* on a 0.05 mm grid; for a net
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
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)
PLANE_NETS = {"GND": None, "+3V3": "+3V3", "VM": "VM"}    # net -> name of its In2 zone polygon in placement.PLANES
VIA_KEEP = {(round(x, 3), round(y, 3)) for x, y in P.VM_VIAS}


def mm(v):
    return pcbnew.FromMM(float(v))


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

    def __init__(self, board):
        self.wide = {n.GetNetCode() for name, n in board.GetNetsByName().items()
                     if any(fnmatch.fnmatchcase(str(name), pat) for cls, pat in project.PATTERNS)}
        new = lambda: array("i", [FREE]) * (NX * NY)  # noqa: E731
        self.tracks = [{layer: new() for layer in LAYERS} for _ in range(2)]     # [0]: 0.15 mm nets, [1]: 0.2 mm nets
        self.vias = [new(), new()]
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

    def shape(self, layers, box, dist, half, net, vias=True):
        """Copper of `net` on `layers`: every point within `half` of dist() == 0, inside `box`."""
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
                    if d <= rt[n]:
                        for layer in layers:
                            self._put(self.tracks[n][layer], k, net)

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
        elif t.GetLayer() in LAYERS:
            a, b = xy(t.GetStart()), xy(t.GetEnd())
            box = (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
            self.shape([t.GetLayer()], box, lambda px, py: dseg(px, py, a, b), t.GetWidth() / 2e6, t.GetNetCode())

    def use(self, net):
        self.k = 1 if net in self.wide else 0

    def ok(self, layer, i, j, net):
        if not (0 <= i < NX and 0 <= j < NY):
            return False
        o = self.tracks[self.k][layer][j * NX + i]
        return o == FREE or o == net

    def via_ok(self, i, j, net, gnd):
        k = j * NX + i
        o = self.vias[self.k][k]
        return (o == FREE or o == net) and not self.nopad[k] and (gnd or not self.novia[k])

    def clear(self, layer, a, b, net, first):
        """Is the straight line between two cells free for this net? `first` is the cell in the starting pad."""
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
        for s in range(n + 1):
            c = (int(round(a[0] + (b[0] - a[0]) * s / n)), int(round(a[1] + (b[1] - a[1]) * s / n)))
            if c != first and not self.ok(layer, c[0], c[1], net):
                return False
        return True


def search(grid, net, start, goal=None, plane=None, gnd=False, limit=600000, anchors=()):
    """A* from (layer index, i, j). To the goal cell on its layer, or, with plane set, to the nearest spot for a plane
    via or to a via that is already there for this net (anchors).

    Returns the path as [(layer index, i, j)], with a layer change marking a via.
    """
    def h(i, j):
        return 0 if goal is None else 1.3 * math.hypot(i - goal[1], j - goal[2])

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
            if grid.ok(LAYERS[li], n[1], n[2], net) and (c == 1 or (grid.ok(LAYERS[li], i + di, j, net) and grid.ok(LAYERS[li], i, j + dj, net))):
                nd = d + c
                if nd < dist.get(n, 1e18):
                    dist[n], prev[n] = nd, cur
                    heapq.heappush(heap, (nd + h(n[1], n[2]), nd, n))
        if goal is not None and grid.via_ok(i, j, net, gnd):
            n = (1 - li, i, j)
            nd = d + 2.5 / STEP
            if nd < dist.get(n, 1e18):
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


def lay(board, grid, net, path, end_via=False):
    """Turn a cell path into straight tracks and vias, on the board and in the grid."""
    code = net.GetNetCode()
    grid.use(code)
    first = (path[0][1], path[0][2])

    def via_at(i, j):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(mm(OX + i * STEP), mm(OY + j * STEP)))
        v.SetDrill(mm(DRILL))
        v.SetWidth(pcbnew.F_Cu, mm(VIA))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(net)
        board.Add(v)
        grid.add(v)

    def tracks(li, run):
        k = 0
        while k < len(run) - 1:                 # pull the staircase straight: jump as far as a clear line allows
            s = 1
            while k + 2 * s < len(run) and grid.clear(LAYERS[li], run[k], run[k + 2 * s], code, first):
                s *= 2
            if grid.clear(LAYERS[li], run[k], run[-1], code, first):
                s = len(run) - 1 - k
            p, q = run[k], run[k + s]
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(mm(OX + p[0] * STEP), mm(OY + p[1] * STEP)))
            t.SetEnd(pcbnew.VECTOR2I(mm(OX + q[0] * STEP), mm(OY + q[1] * STEP)))
            t.SetWidth(mm(TRACK))
            t.SetLayer(LAYERS[li])
            t.SetNet(net)
            board.Add(t)
            grid.add(t)
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


def over_plane(name):
    """Test for a spot where a via reaches the plane of this net, a little inside its outline."""
    zone = PLANE_NETS[name]
    if zone is None:
        return lambda x, y: True
    pts = dict(P.PLANES)[zone]
    return lambda x, y: inside(pts, x, y) and all(inside(pts, x + dx, y + dy) for dx, dy in ((0.6, 0), (-0.6, 0), (0, 0.6), (0, -0.6)))


def plane_vias(board):
    anchors = {}
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() in PLANE_NETS and over_plane(t.GetNetname())(*xy(t.GetPosition())):
            anchors.setdefault(t.GetNetCode(), set()).add(cell(*xy(t.GetPosition())))
    return anchors


def fanout():
    """On the placed, unrouted board: tie every SMD pad of a plane net to its plane with a short track and a via.

    Smallest pads first, so fine-pitch pins get out before the capacitors beside them take the room. A pad joins a
    via that is already there for its net when that is within reach.
    """
    board = pcbnew.LoadBoard(PCB)
    grid = Grid(board)
    nets = board.GetNetsByName()
    anchors = plane_vias(board)
    pads = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() in PLANE_NETS and not p.GetDrillSize().x and p.IsOnLayer(pcbnew.F_Cu):
                b = p.GetBoundingBox()
                r = (b.GetLeft() / 1e6 - OX, b.GetTop() / 1e6 - OY, b.GetRight() / 1e6 - OX, b.GetBottom() / 1e6 - OY)
                x, y = xy(p.GetPosition())
                if any(r[0] <= i * STEP <= r[2] and r[1] <= j * STEP <= r[3] for i, j in anchors.get(p.GetNetCode(), ())):
                    continue                                  # an exposed pad that has its vias already
                if any(net == p.GetNetname() and inside(pts, x, y) for net, pts in P.POURS):
                    continue                                  # sits in its own pour on the top layer
                pads.append(((r[2] - r[0]) * (r[3] - r[1]), fp.GetReference(), p.GetNumber(), p.GetNetname(), x, y))
    done, far, failed = 0, [], []
    for _, ref, num, name, x, y in sorted(pads):
        net = nets[name]
        code = net.GetNetCode()
        mine = anchors.setdefault(code, set())
        path = search(grid, code, (0,) + cell(x, y), plane=over_plane(name), gnd=name == "GND", limit=3000000, anchors=mine)
        if not path:
            failed.append(f"{ref}.{num} {name}")
            continue
        if len(path) * STEP > 6:                         # far from its plane: a job for the router, not for a stub
            far.append(f"{ref}.{num} {name}")
            continue
        end = (path[-1][1], path[-1][2])
        lay(board, grid, net, path, end_via=end not in mine)
        mine.add(end)
        done += 1
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    project.patch()
    print(f"fanout: {done} pads tied to their plane, {sum(len(a) for a in anchors.values())} plane vias in all")
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
    layer = None if d.startswith("Via") or "F.Cu - B.Cu" in d or "PTH" in d else (1 if " on B.Cu" in d else 0)
    return (net.group(1) if net else None, layer, item["pos"]["x"] - OX, item["pos"]["y"] - OY, d)


def one_round(n):
    board = pcbnew.LoadBoard(PCB)
    report = drc(PCB)
    by_uuid = {t.m_Uuid.AsString(): t for t in board.GetTracks()}
    doomed = set()
    for v in report["violations"]:
        if v["type"] in ("shorting_items", "clearance", "track_width", "via_dangling", "track_dangling", "items_not_allowed",
                         "tracks_crossing", "annular_width", "hole_clearance", "copper_edge_clearance"):
            items = [by_uuid[i["uuid"]] for i in v["items"] if i.get("uuid") in by_uuid]
            if v["type"] in ("shorting_items", "clearance", "tracks_crossing") and len(items) > 1:
                items = sorted(items, key=lambda t: (t.Type() == pcbnew.PCB_VIA_T, t.GetLength()))[:1]    # drop the smaller offender
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
    if doomed:                                             # the picture changed: look again before routing
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        pcbnew.SaveBoard(PCB, board)
        project.patch()
        report = drc(PCB)
        board = pcbnew.LoadBoard(PCB)
    grid = Grid(board)
    nets = board.GetNetsByName()
    anchors = plane_vias(board)
    done = failed = 0
    notes = []
    for u in report["unconnected_items"]:
        a, b = end_of(u["items"][0]), end_of(u["items"][1])
        name = a[0]
        if name is None or name not in nets:
            continue
        net = nets[name]
        code = net.GetNetCode()
        if name in PLANE_NETS:
            mine = anchors.setdefault(code, set())
            for e in (a, b):
                if e[4].startswith("Zone") or e[4].startswith("Via"):
                    continue
                path = search(grid, code, (e[1] or 0,) + cell(e[2], e[3]), plane=over_plane(name), gnd=name == "GND", anchors=mine)
                if path:
                    end = (path[-1][1], path[-1][2])
                    lay(board, grid, net, path, end_via=end not in mine)
                    mine.add(end)
                    done += 1
                else:
                    failed += 1
                    notes.append(f"{name} at ({e[2]:.1f}, {e[3]:.1f}): no way to its plane")
            continue
        if a[4].startswith("Zone") or b[4].startswith("Zone"):
            continue
        best = None
        for la in ((a[1],) if a[1] is not None else (0, 1)):
            for lb in ((b[1],) if b[1] is not None else (0, 1)):
                path = search(grid, code, (la,) + cell(a[2], a[3]), goal=(lb,) + cell(b[2], b[3]))
                if path and (best is None or len(path) < len(best)):
                    best = path
        if best:
            lay(board, grid, net, best)
            done += 1
        else:
            failed += 1
            notes.append(f"{name}: no path from ({a[2]:.1f}, {a[3]:.1f}) to ({b[2]:.1f}, {b[3]:.1f})")
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    project.patch()
    print(f"round {n}: removed {len(doomed)} bad items, routed {done}, could not route {failed}", flush=True)
    for line in notes[:20]:
        print("   " + line, flush=True)
    return len(doomed) + done


if __name__ == "__main__":
    if sys.argv[1:] == ["fanout"]:
        fanout()
        sys.exit()
    for n in range(1, (int(sys.argv[1]) if len(sys.argv) > 1 else 6) + 1):
        if not one_round(n):
            break
    final = drc(PCB)
    kinds = {}
    for v in final["violations"]:
        kinds[v["type"]] = kinds.get(v["type"], 0) + 1
    print(f"DRC now: {len(final['unconnected_items'])} unconnected, violations {kinds}")
