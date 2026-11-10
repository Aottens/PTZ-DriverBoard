#!/usr/bin/env python3
"""Build the board from the schematic's netlist and the placement in placement.py.

Run with KiCad's Python, from hardware/:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 tools/board.py place

  place   new board: outline, holes, every footprint with its nets, placed; no copper yet
Big parts sit where placement.py says. Small parts are put as close as they fit to the pad they belong to:
a hint in placement.py, or else a pad of a part that shares one of their signal nets.
"""
import math
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import netlist  # noqa: E402
import placement as P  # noqa: E402

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
    taken += [k for k in P.KEEPOUT]
    for ref, (cx, cy, rot) in P.FIXED.items():
        it = items[ref]
        x, y = it.origin_for_centre(cx, cy, rot)
        it.pos = (x, y, rot)
        r = it.rect(x, y, rot)
        for other in taken:
            assert not overlap(r, other) or ref in P.MAY_OVERLAP, f"{ref} overlaps a placed part or keep-out: {r} / {other}"
        taken.append(r)

    def free(it, x, y, rot, grow):
        r = it.rect(x, y, rot, grow)
        if r[0] < P.EDGE or r[1] < P.EDGE or r[2] > W - P.EDGE or r[3] > H - P.EDGE:
            return False
        return not any(overlap(r, t) for t in taken)

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
                taken.append(it.rect(*it.pos, 0.0))
                todo.remove(it)
                progress = True
            else:
                failed.append(it)
                todo.remove(it)
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


def via(board, net, x, y, size=0.6, drill=0.3):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(vec(x, y))
    v.SetDrill(mm(drill))
    v.SetWidth(pcbnew.F_Cu, mm(size))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net)
    board.Add(v)
    return v


def build():
    tree = netlist.export(os.path.join(HW, "ptz-driver.kicad_sch"))
    comps, pins = netlist.components(tree), netlist.pin_nets(tree)
    items = {ref: Item(ref, c, pins) for ref, c in comps.items() if c["footprint"]}
    lost = place(items)

    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)
    nets = {}
    for name in sorted(set(pins.values())):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        nets[name] = ni
    for it in items.values():
        fp = it.fp
        lib, name = it.comp["footprint"].split(":")
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(it.ref)
        fp.SetValue(it.comp["value"])
        fp.SetPath(pcbnew.KIID_PATH(f"{it.comp['path']}{it.comp['uuid']}"))
        for key in ("LCSC", "MPN"):
            if it.comp["fields"].get(key):
                fp.SetField(key, it.comp["fields"][key])
        for pad in fp.Pads():
            net = pins.get((it.ref, pad.GetNumber()))
            if net:
                pad.SetNet(nets[net])
        board.Add(fp)
        x, y, rot = it.pos or (W + 10 + 4 * (lost.index(it) % 8), 4 * (lost.index(it) // 8), 0)
        fp.SetPosition(vec(x, y))
        fp.SetOrientationDegrees(rot)
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
    # nine vias under each driver into the ground planes (BRD-11)
    for it in items.values():
        if it.comp["value"].startswith("TMC5240"):
            for dx in (-1.03, 0, 1.03):
                for dy in (-1.03, 0, 1.03):
                    via(board, nets["GND"], it.pos[0] + dx, it.pos[1] + dy)
    pcbnew.SaveBoard(PCB, board)
    area = sum((i.box[2] - i.box[0]) * (i.box[3] - i.box[1]) for i in items.values() if i.pos)
    print(f"{len(items)} footprints, {len(lost)} without a place: {' '.join(sorted(i.ref for i in lost))}")
    print(f"courtyard area {area:.0f} mm2 of {W * H:.0f} = {100 * area / (W * H):.0f} %")
    return not lost


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "place"
    if cmd == "place":
        sys.exit(0 if build() else 1)
    elif cmd == "dsn":
        board = pcbnew.LoadBoard(PCB)
        assert pcbnew.ExportSpecctraDSN(board, sys.argv[2]), "DSN export failed"
    elif cmd == "ses":
        board = pcbnew.LoadBoard(PCB)
        assert pcbnew.ImportSpecctraSES(board, sys.argv[2]), "SES import failed"
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        pcbnew.SaveBoard(PCB, board)
