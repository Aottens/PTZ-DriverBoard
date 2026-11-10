#!/usr/bin/env python3
"""Build the board from the schematic's netlist and the placement in placement.py.

Run with KiCad's Python, from hardware/:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 tools/board.py place

  place   new board: outline, holes, every footprint with its nets, placed; no copper yet
Big parts sit where placement.py says. Small parts are put as close as they fit to the pad they belong to:
a hint in placement.py, or else a pad of a part that shares one of their signal nets.
"""
import json
import math
import os
import re
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import netlist  # noqa: E402
import placement as P  # noqa: E402
import project  # noqa: E402

HW = os.path.dirname(HERE)
PCB = os.path.join(HW, "ptz-driver.kicad_pcb")
KICAD_FP = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
OX, OY = 100.0, 100.0          # board origin on the KiCad sheet, mm
W, H = P.BOARD_W, P.BOARD_H
GLOBAL = {"GND", "+3V3", "+5V", "VM", "VSYS", "3V3A"}


def mm(v):
    return pcbnew.FromMM(float(v))


def vec(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))


def load_footprint(fpid):
    lib, name = fpid.split(":")
    path = os.path.join(HW, "ptz.pretty") if lib == "ptz" else f"{KICAD_FP}/{lib}.pretty"
    fp = pcbnew.FootprintLoad(path, name)
    assert fp, f"footprint not found: {fpid}"
    return fp


class Item:
    """A footprint with its courtyard box and pads, in footprint coordinates (mm, y down, rotation 0)."""

    def __init__(self, ref, comp, pins):
        self.ref, self.comp = ref, comp
        self.fp = load_footprint(comp["footprint"])
        cy = self.fp.GetCourtyard(pcbnew.F_CrtYd)
        bb = cy.BBox() if cy.OutlineCount() else self.fp.GetBoundingBox(False)
        self.box = (bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6)
        self.pads = {}
        for pad in self.fp.Pads():
            if pad.GetNumber():
                self.pads.setdefault(pad.GetNumber(), []).append((pad.GetPosition().x / 1e6, pad.GetPosition().y / 1e6))
        self.pads = {n: (sum(p[0] for p in v) / len(v), sum(p[1] for p in v) / len(v)) for n, v in self.pads.items()}
        self.nets = {n: pins.get((ref, n)) for n in self.pads}
        self.pos = None  # (x, y, rot) of the footprint origin on the board

    @staticmethod
    def turn(x, y, rot):
        """Rotate counter-clockwise as seen on screen (y down), as KiCad does."""
        c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
        return x * c + y * s, -x * s + y * c

    def rect(self, x, y, rot, grow=0.0):
        a = self.turn(self.box[0], self.box[1], rot)
        b = self.turn(self.box[2], self.box[3], rot)
        return (x + min(a[0], b[0]) - grow, y + min(a[1], b[1]) - grow, x + max(a[0], b[0]) + grow, y + max(a[1], b[1]) + grow)

    def origin_for_centre(self, cx, cy, rot):
        r = self.rect(0, 0, rot)
        return cx - (r[0] + r[2]) / 2, cy - (r[1] + r[3]) / 2

    def pad_at(self, n, pos=None):
        x, y, rot = pos or self.pos
        px, py = self.turn(*self.pads[n], rot)
        return x + px, y + py


def overlap(a, b):
    return a[0] < b[2] - 1e-6 and b[0] < a[2] - 1e-6 and a[1] < b[3] - 1e-6 and b[1] < a[3] - 1e-6


def place(items):
    """Fill item.pos for every item. Returns the items that found no place."""
    taken = [(x - 3.5, y - 3.5, x + 3.5, y + 3.5) for x, y in P.HOLES]   # hole keep-outs
    for ref, (cx, cy, rot) in P.FIXED.items():
        it = items[ref]
        x, y = it.origin_for_centre(cx, cy, rot)
        it.pos = (x, y, rot)
        r = it.rect(x, y, rot)
        for other in taken:
            assert not overlap(r, other) or ref in P.MAY_OVERLAP, f"{ref} overlaps a placed part or keep-out: {r} / {other}"
        taken.append(r)

    taken += list(P.KEEPOUT)   # keep-outs bind the small parts only

    labels = {}

    def label_of(it):
        if it.ref.startswith("TP"):
            return P.TP_NAMES.get(it.comp["value"], it.comp["value"])
        return P.PART_LABELS.get(it.ref)

    def free(it, x, y, rot, grow):
        """The room the part takes at this spot, with its silkscreen name beside it, or None when it does not fit."""
        r = it.rect(x, y, rot, grow)
        name = label_of(it)
        for side in ((1, -1) if name else (0,)):
            c = r
            if side:
                w = len(name) * P.TEXT_H_SMALL * 0.92 + 0.2
                lx, ly = (r[2] + w / 2 if side > 0 else r[0] - w / 2), (r[1] + r[3]) / 2
                tb = P.text_box(name, lx, ly, P.TEXT_H_SMALL)
                c = (min(r[0], tb[0]), min(r[1], tb[1]), max(r[2], tb[2]), max(r[3], tb[3]))
                it.label = (name, round(lx, 3), round(ly, 3), 0)
            if c[0] < P.EDGE or c[1] < P.EDGE or c[2] > W - P.EDGE or c[3] > H - P.EDGE:
                continue
            if not any(overlap(c, t) for t in taken):
                return c
        return None

    def target(it):
        """(x, y, my pad) to sit next to, or None while the part it belongs to is not placed yet."""
        hint = P.NEAR.get(it.ref)
        if hint:
            other = items[hint[0]]
            if not other.pos:
                return None
            tx, ty = other.pad_at(hint[1])
            mine = [n for n, net in it.nets.items() if net == other.nets[hint[1]]]
            return tx, ty, (mine[0] if mine else sorted(it.pads)[0])
        best = None
        for n, net in it.nets.items():
            if not net or net in GLOBAL:
                continue
            for o in items.values():
                if o is it or not o.pos:
                    continue
                for m, onet in o.nets.items():
                    if onet == net:
                        rank = (0 if len(o.pads) > 2 else 1, len(o.pads))
                        if best is None or rank < best[0]:
                            best = (rank, *o.pad_at(m), n)
        return best[1:] if best else None

    todo = [it for it in items.values() if not it.pos]
    todo.sort(key=lambda it: (it.ref not in P.NEAR, -(it.box[2] - it.box[0]) * (it.box[3] - it.box[1]), it.ref))
    failed, progress = [], True
    while todo and progress:
        progress = False
        for it in list(todo):
            t = target(it)
            if t is None:
                continue
            tx, ty, mine = t
            best = None
            for grow in (P.HALO, 0.05):
                for ring in range(0, int(P.REACH / P.STEP)):
                    radius = ring * P.STEP
                    steps = max(1, int(2 * math.pi * radius / P.STEP))
                    for k in range(steps):
                        ang = 2 * math.pi * k / steps
                        for rot in (0, 90, 180, 270):
                            # put my own pad on the ring around the target pad
                            px, py = it.turn(*it.pads[mine], rot)
                            x = round((tx + radius * math.cos(ang) - px) / 0.05) * 0.05
                            y = round((ty + radius * math.sin(ang) - py) / 0.05) * 0.05
                            if free(it, x, y, rot, grow):
                                d = math.dist(it.pad_at(mine, (x, y, rot)), (tx, ty))
                                if best is None or d < best[0]:
                                    best = (d, x, y, rot)
                    if best and radius > best[0] + 1.0:
                        break
                if best:
                    break
            if best:
                it.pos = best[1:]
                taken.append(free(it, *it.pos, 0.0) or it.rect(*it.pos, 0.0))   # also settles which side the name is on
                if label_of(it):
                    labels[it.ref] = it.label
                todo.remove(it)
                progress = True
            else:
                failed.append(it)
                todo.remove(it)
    json.dump(labels, open(os.path.join(HW, "tools", "tp_labels.json"), "w"), indent=0, sort_keys=True)
    return failed + todo


def zone(board, net, layer, pts, clearance=0.2):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetLocalClearance(mm(clearance))
    z.SetMinThickness(mm(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    outline = z.Outline()
    outline.NewOutline()
    for x, y in pts:
        outline.Append(mm(OX + x), mm(OY + y))
    board.Add(z)
    return z


def keepout(board, layers, pts, pour, vias=False):
    """A rule area without tracks; pour and vias say whether zone copper and vias may still be in it."""
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    ls = pcbnew.LSET()
    for layer in layers:
        ls.AddLayer(layer)
    z.SetLayerSet(ls)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(not vias)
    z.SetDoNotAllowZoneFills(not pour)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    outline = z.Outline()
    outline.NewOutline()
    for x, y in pts:
        outline.Append(mm(OX + x), mm(OY + y))
    board.Add(z)
    return z


def via(board, net, x, y, size=0.6, drill=0.3):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(vec(x, y))
    v.SetDrill(mm(drill))
    v.SetWidth(pcbnew.F_Cu, mm(size))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net)
    board.Add(v)
    return v


def save(board):
    pcbnew.SaveBoard(PCB, board)
    project.patch()   # KiCad writes the project file too, with whatever the board object holds


def build():
    tree = netlist.export(os.path.join(HW, "ptz-driver.kicad_sch"))
    comps, pins = netlist.components(tree), netlist.pin_nets(tree)
    items = {ref: Item(ref, c, pins) for ref, c in comps.items() if c["footprint"]}
    lost = place(items)

    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)
    for layer in (pcbnew.In1_Cu, pcbnew.In2_Cu):     # planes: the router must not put tracks here (BRD-03)
        board.SetLayerType(layer, pcbnew.LT_POWER)
    nets = {}
    for name in sorted(set(pins.values())):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        nets[name] = ni
    for it in items.values():
        fp = it.fp
        lib, name = it.comp["footprint"].split(":")
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetLocalClearance(None)       # some library footprints carry their own; the net classes decide here
        fp.SetReference(it.ref)
        fp.SetValue(it.comp["value"])
        fp.SetPath(pcbnew.KIID_PATH(f"{it.comp['path']}{it.comp['uuid']}"))
        for key, value in it.comp["fields"].items():      # every symbol field, so schematic parity holds
            if key not in ("Footprint", "Datasheet", "Description"):
                fp.SetField(key, value)
        for field in fp.GetFields():
            if field.GetName() not in ("Reference", "Value"):
                field.SetVisible(False)
        for pad in fp.Pads():
            net = pins.get((it.ref, pad.GetNumber()))
            if net:
                pad.SetNet(nets[net])
        board.Add(fp)
        x, y, rot = it.pos or (W + 10 + 4 * (lost.index(it) % 8), 4 * (lost.index(it) // 8), 0)
        fp.SetPosition(vec(x, y))
        fp.SetOrientationDegrees(rot)
    for ref, (dx, dy) in P.SHIFT.items():
        fp = items[ref].fp
        fp.SetPosition(fp.GetPosition() + pcbnew.VECTOR2I(mm(dx), mm(dy)))
    for ra, rb in P.SWAP:
        fa, fb = items[ra].fp, items[rb].fp
        pa, oa = fa.GetPosition(), fa.GetOrientationDegrees()
        fa.SetPosition(fb.GetPosition())
        fa.SetOrientationDegrees(fb.GetOrientationDegrees())
        fb.SetPosition(pa)
        fb.SetOrientationDegrees(oa)
    pts = [(0, 0), (W, 0), (W, H), (0, H)]
    for i in range(4):
        seg = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(vec(*pts[i]))
        seg.SetEnd(vec(*pts[(i + 1) % 4]))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.1))
        board.Add(seg)
    # inner planes: an unbroken ground plane, and the supply plane split into the motor supply and 3.3 V (BRD-03)
    zone(board, nets["GND"], pcbnew.In1_Cu, [(0, 0), (W, 0), (W, H), (0, H)])
    for net, pts in P.PLANES:
        zone(board, nets[net], pcbnew.In2_Cu, pts)
    keepout(board, [pcbnew.In2_Cu], dict(P.PLANES)["VM"], pour=True, vias=True)    # the motor supply plane stays whole
    for net, pts in P.POURS:
        z = zone(board, nets[net], pcbnew.F_Cu, pts)
        z.SetAssignedPriority(10)
    for x, y in P.VM_VIAS:
        via(board, nets["VM"], x, y, 0.8, 0.4)
    # nine vias under each driver into the ground planes, and no other copper under it on the bottom (BRD-11)
    for it in items.values():
        if it.comp["value"].startswith("TMC5240"):
            x, y = it.pos[:2]
            for dx in (-1.03, 0, 1.03):
                for dy in (-1.03, 0, 1.03):
                    via(board, nets["GND"], x + dx, y + dy)
            keepout(board, [pcbnew.B_Cu], [(x - 2.9, y - 2.9), (x + 2.9, y - 2.9), (x + 2.9, y + 2.9), (x - 2.9, y + 2.9)], pour=True, vias=True)
    # nothing but bare board within 3.5 mm of a mounting hole's centre, top and bottom (BRD-01)
    for hx, hy in P.HOLES:
        ring = [(hx + 3.5 * math.cos(math.radians(a)), hy + 3.5 * math.sin(math.radians(a))) for a in range(0, 360, 15)]
        keepout(board, [pcbnew.F_Cu, pcbnew.B_Cu], ring, pour=False)
    save(board)
    area = sum((i.box[2] - i.box[0]) * (i.box[3] - i.box[1]) for i in items.values() if i.pos)
    print(f"{len(items)} footprints, {len(lost)} without a place: {' '.join(sorted(i.ref for i in lost))}")
    print(f"courtyard area {area:.0f} mm2 of {W * H:.0f} = {100 * area / (W * H):.0f} %")
    return not lost


# ---------------------------------------------------------------- after routing

def _pt(v):
    return (v.x / 1e6 - OX, v.y / 1e6 - OY)


def _d_point_seg(p, a, b):
    ax, ay, bx, by = *a, *b
    dx, dy = bx - ax, by - ay
    t = 0 if dx == dy == 0 else max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


def _cross(a, b, c, d):
    def side(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return side(a, b, c) * side(a, b, d) < 0 and side(c, d, a) * side(c, d, b) < 0


def _d_seg_seg(a, b, c, d):
    if _cross(a, b, c, d):
        return 0.0
    return min(_d_point_seg(a, c, d), _d_point_seg(b, c, d), _d_point_seg(c, a, b), _d_point_seg(d, a, b))


def _d_seg_rect(a, b, r):
    x0, y0, x1, y1 = r
    if x0 <= a[0] <= x1 and y0 <= a[1] <= y1:
        return 0.0
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return min(_d_seg_seg(a, b, c[i], c[(i + 1) % 4]) for i in range(4))


def widen(board):
    """Give every track the width of its net class where its surroundings allow, motor outputs up to 0.8 mm (BRD-06).

    The router necks tracks down at fine-pitch pins and leaves them narrow; this widens each segment as far as the
    0.2 mm gap to other nets' tracks, vias and pads lets it.
    """
    target = {"Motor": 0.8, "Supply": 0.6, "Power": 0.5, "Default": 0.2}
    tracks = [t for t in board.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
    vias = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    pads = [(p, p.GetBoundingBox()) for fp in board.GetFootprints() for p in fp.Pads()]
    pads = [(p, (bb.GetLeft() / 1e6 - OX, bb.GetTop() / 1e6 - OY, bb.GetRight() / 1e6 - OX, bb.GetBottom() / 1e6 - OY)) for p, bb in pads]
    for t in list(tracks):                   # a long narrow segment is cut up first, so each piece gets the width its own spot allows
        want = target.get(t.GetNetClassName(), 0.2)
        a, b = _pt(t.GetStart()), _pt(t.GetEnd())
        n = math.ceil(math.hypot(b[0] - a[0], b[1] - a[1]) / 0.5)
        if want > 0.2 and t.GetWidth() / 1e6 < want and n > 1:
            for k in range(1, n):
                piece = pcbnew.PCB_TRACK(board)
                piece.SetStart(vec(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
                piece.SetEnd(vec(a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n))
                piece.SetWidth(t.GetWidth())
                piece.SetLayer(t.GetLayer())
                piece.SetNetCode(t.GetNetCode())
                board.Add(piece)
                tracks.append(piece)
            t.SetEnd(vec(a[0] + (b[0] - a[0]) / n, a[1] + (b[1] - a[1]) / n))
    changed = 0
    for cap in (0.6, 9.9):                   # first every track to 0.6 mm, then what is left to the widest: neighbours share the room
        for t in tracks:
            want = min(cap, target.get(t.GetNetClassName(), 0))
            if not want or t.GetWidth() / 1e6 >= want:
                continue
            a, b, layer, net = _pt(t.GetStart()), _pt(t.GetEnd()), t.GetLayer(), t.GetNetCode()
            room = min(a[0], a[1], b[0], b[1], W - a[0], W - b[0], H - a[1], H - b[1]) - 0.3
            for o in tracks:
                if o.GetLayer() == layer and o.GetNetCode() != net:
                    room = min(room, _d_seg_seg(a, b, _pt(o.GetStart()), _pt(o.GetEnd())) - o.GetWidth() / 2e6 - 0.2)
            for v in vias:
                if v.GetNetCode() != net:
                    room = min(room, _d_point_seg(_pt(v.GetPosition()), a, b) - v.GetWidth(pcbnew.F_Cu) / 2e6 - 0.2)
            for p, r in pads:
                if p.GetNetCode() != net and (p.IsOnLayer(layer) or p.GetDrillSize().x):
                    room = min(room, _d_seg_rect(a, b, r) - (0.3 if p.GetDrillSize().x >= p.GetSizeX() > 0 else 0.2))   # unplated hole: 0.25 mm
            width = min(want, math.floor(2 * (room - 0.01) / 0.05 + 1e-6) * 0.05)
            if width > t.GetWidth() / 1e6 + 1e-6:
                t.SetWidth(mm(width))
                changed += 1
    thin = sorted({t.GetNetname() for t in tracks if t.GetWidth() / 1e6 < 0.15 - 1e-6})
    print(f"widened {changed} track segments" + (f"; still under 0.15 mm: {thin}" if thin else ""))


KEEP = []


def finish():
    board = pcbnew.LoadBoard(PCB)
    widen(board)
    nets = board.GetNetsByName()
    gnd = nets["GND"]
    for z in list(board.Zones()):      # a rerun replaces the outer ground pours
        if not z.GetIsRuleArea() and z.GetNetname() == "GND" and z.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu):
            board.Remove(z)
            KEEP.append(z)             # not freed while we run: KiCad's Python breaks the board when it deletes a removed item
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = zone(board, gnd, layer, [(0, 0), (W, 0), (W, H), (0, H)], clearance=0.25)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(0.25))
        z.SetThermalReliefSpokeWidth(mm(0.3))
        z.SetMinThickness(mm(0.25))
    for d in list(board.GetDrawings()):  # a rerun replaces what this function drew
        if d.GetLayer() in (pcbnew.B_Mask, pcbnew.F_SilkS, pcbnew.B_SilkS):
            board.Remove(d)
            KEEP.append(d)
    for fp in board.GetFootprints():
        if fp.GetValue().startswith("TMC5240"):     # bare window under each driver for a heat spreader (BRD-11)
            x, y = _pt(fp.GetPosition())
            r = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_RECTANGLE)
            r.SetStart(vec(x - 2.8, y - 2.8))
            r.SetEnd(vec(x + 2.8, y + 2.8))
            r.SetLayer(pcbnew.B_Mask)
            r.SetFilled(True)
            r.SetWidth(0)
            board.Add(r)
    import silk
    silk.draw(board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    save(board)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "place"
    if cmd == "place":
        sys.exit(0 if build() else 1)
    elif cmd == "dsn":
        board = pcbnew.LoadBoard(PCB)
        assert pcbnew.ExportSpecctraDSN(board, sys.argv[2]), "DSN export failed"
        text = open(sys.argv[2]).read()
        # the ground plane is a power layer to the router whatever KiCad wrote; inner layer 2 stays open for the
        # signals that do not fit on the outer layers, outside the keep-out over the VM plane
        # both inner layers are power layers to Freerouting: given inner layer 2 it cut the +3V3 plane into some twenty
        # pieces. tools/complete.py uses that layer afterwards, sparingly, for what the outer layers cannot hold.
        for name in ("In1.Cu", "In2.Cu"):
            text = re.sub(r"(\(layer %s\n\s+\(type )\w+" % re.escape(name), r"\g<1>power", text)
        assert text.count("(type power)") == 2 and text.count("(type signal)") == 2, "layer types in the DSN are not as meant"
        text = text.replace("(type route)", "(type protect)")     # what is on the board already (plane vias and their stubs) stays
        open(sys.argv[2], "w").write(text)
    elif cmd == "ses":
        board = pcbnew.LoadBoard(PCB)
        assert pcbnew.ImportSpecctraSES(board, sys.argv[2]), "SES import failed"
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        save(board)
    elif cmd == "finish":
        finish()
