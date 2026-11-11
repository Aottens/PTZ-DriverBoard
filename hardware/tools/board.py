#!/usr/bin/env python3
"""Build the Rev B board from the schematic's netlist and the placement in placement.py.

Run with KiCad's Python, from hardware/:
  KP=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
  $KP tools/board.py place          new board: outline, holes, every footprint placed, supply pours, motor tracks.
                                    This discards the routing.
  $KP tools/board.py dsn out.dsn    Specctra export for Freerouting; what is on the board already is protected
  $KP tools/board.py ses in.ses     import the routed session
  $KP tools/board.py finish         ground pours on both layers, stitching vias, silkscreen
"""
import math
import os
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
LAYER = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}
KEEP = []                      # removed items stay referenced: KiCad's Python breaks the board when it frees them


def mm(v):
    return pcbnew.FromMM(float(v))


def vec(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))


def xy(v):
    return v.x / 1e6 - OX, v.y / 1e6 - OY


def load_footprint(fpid):
    lib, name = fpid.split(":")
    path = os.path.join(HW, "ptz.pretty") if lib == "ptz" else f"{KICAD_FP}/{lib}.pretty"
    fp = pcbnew.FootprintLoad(path, name)
    assert fp, f"footprint not found: {fpid}"
    return fp


def turn(x, y, rot):
    """Rotate counter-clockwise as seen on screen (y down), as KiCad does."""
    c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
    return x * c + y * s, -x * s + y * c


def origin_for(fp, x, y, rot, anchor):
    """Where the footprint's origin goes so that its anchor lands on (x, y)."""
    if anchor == "o":
        return x, y
    if anchor == "c":
        bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
        ax, ay = (bb.GetLeft() + bb.GetRight()) / 2e6, (bb.GetTop() + bb.GetBottom()) / 2e6
    else:
        pad = [p for p in fp.Pads() if p.GetNumber() == anchor][0]
        ax, ay = pad.GetPosition().x / 1e6, pad.GetPosition().y / 1e6
    dx, dy = turn(ax, ay, rot)
    return x - dx, y - dy


def zone(board, net, layer, pts, clearance=0.25, priority=0, thermal=False):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetLocalClearance(mm(clearance))
    z.SetMinThickness(mm(0.25))
    z.SetAssignedPriority(priority)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal else pcbnew.ZONE_CONNECTION_FULL)
    if thermal:
        z.SetThermalReliefGap(mm(0.25))
        z.SetThermalReliefSpokeWidth(mm(0.4))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    outline = z.Outline()
    outline.NewOutline()
    for x, y in pts:
        outline.Append(mm(OX + x), mm(OY + y))
    board.Add(z)
    return z


def keepout(board, layers, pts):
    """A rule area without tracks, vias or pour."""
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    ls = pcbnew.LSET()
    for layer in layers:
        ls.AddLayer(layer)
    z.SetLayerSet(ls)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    outline = z.Outline()
    outline.NewOutline()
    for x, y in pts:
        outline.Append(mm(OX + x), mm(OY + y))
    board.Add(z)
    return z


def via(board, net, x, y, size=0.8, drill=0.4):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(vec(x, y))
    v.SetDrill(mm(drill))
    v.SetWidth(pcbnew.F_Cu, mm(size))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net)
    board.Add(v)
    return v


def track(board, net, layer, width, a, b):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(vec(*a))
    t.SetEnd(vec(*b))
    t.SetWidth(mm(width))
    t.SetLayer(layer)
    t.SetNet(net)
    board.Add(t)
    return t


def save(board):
    pcbnew.SaveBoard(PCB, board)
    project.patch()   # KiCad writes the project file too, with whatever the board object holds


def build():
    tree = netlist.export(os.path.join(HW, "ptz-driver.kicad_sch"))
    comps, pins = netlist.components(tree), netlist.pin_nets(tree)
    comps = {r: c for r, c in comps.items() if c["footprint"]}
    missing, extra = sorted(set(comps) - set(P.POS)), sorted(set(P.POS) - set(comps))
    assert not missing and not extra, f"placement.py: no place for {missing}; placed but not in the schematic: {extra}"

    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    nets = {}
    for name in sorted(set(pins.values())):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        nets[name] = ni
    for ref, comp in comps.items():
        fp = load_footprint(comp["footprint"])
        lib, name = comp["footprint"].split(":")
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(ref)
        fp.SetValue(comp["value"])
        fp.SetPath(pcbnew.KIID_PATH(f"{comp['path']}{comp['uuid']}"))
        for key, value in comp["fields"].items():      # every symbol field, so schematic parity holds
            if key not in ("Footprint", "Datasheet", "Description"):
                fp.SetField(key, value)
        for field in fp.GetFields():
            if field.GetName() not in ("Reference", "Value"):
                field.SetVisible(False)
        for pad in fp.Pads():
            net = pins.get((ref, pad.GetNumber()))
            if net:
                pad.SetNet(nets[net])
        x, y, rot, anchor = P.POS[ref]
        board.Add(fp)
        fp.SetPosition(vec(*origin_for(fp, x, y, rot, anchor)))
        fp.SetOrientationDegrees(rot)
    pts = [(0, 0), (W, 0), (W, H), (0, H)]
    for i in range(4):
        seg = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(vec(*pts[i]))
        seg.SetEnd(vec(*pts[(i + 1) % 4]))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.1))
        board.Add(seg)
    # supply pours with a known width (BRD-06), over the ground pour of the bottom layer
    for net, layer, poly in P.ZONES:
        zone(board, nets[net], LAYER[layer], poly, priority=10)
    zone(board, nets["GND"], pcbnew.B_Cu, [(0, 0), (W, 0), (W, H), (0, H)])
    for net, layer, width, line in P.TRACKS:
        for a, b in zip(line, line[1:]):
            track(board, nets[net], LAYER[layer], width, a, b)
    for net, x, y in P.VIAS:
        via(board, nets[net], x, y, *((0.8, 0.4) if net == "VM" else (0.6, 0.3)))
    # nothing but bare board within 3.5 mm of a mounting hole's centre, top and bottom (BRD-01)
    for hx, hy in P.HOLES:
        ring = [(hx + 3.5 * math.cos(math.radians(a)), hy + 3.5 * math.sin(math.radians(a))) for a in range(0, 360, 15)]
        keepout(board, [pcbnew.F_Cu, pcbnew.B_Cu], ring)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    save(board)
    print(f"{len(comps)} footprints placed")
    return True


def tidy(board):
    """The router pairs a 0.4 mm drill with a 0.6 mm pad now and then, and necks a track below 0.15 mm."""
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T and t.GetWidth(pcbnew.F_Cu) - t.GetDrill() < mm(0.3):
            t.SetDrill(t.GetWidth(pcbnew.F_Cu) - mm(0.3))
        elif t.Type() != pcbnew.PCB_VIA_T and t.GetWidth() < mm(0.15):
            t.SetWidth(mm(0.15))


def finish():
    board = pcbnew.LoadBoard(PCB)
    tidy(board)
    gnd = board.GetNetsByName()["GND"]
    for z in list(board.Zones()):      # a rerun replaces the top ground pour
        if not z.GetIsRuleArea() and z.GetNetname() == "GND" and z.GetLayer() == pcbnew.F_Cu:
            board.Remove(z)
            KEEP.append(z)
    zone(board, gnd, pcbnew.F_Cu, [(0, 0), (W, 0), (W, H), (0, H)])
    for d in list(board.GetDrawings()):  # a rerun replaces what this function drew
        if d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            board.Remove(d)
            KEEP.append(d)
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
        assert text.count("(type signal)") == 2, "layer types in the DSN are not as meant"
        text = text.replace("(type route)", "(type protect)")     # what is on the board already stays
        open(sys.argv[2], "w").write(text)
    elif cmd == "ses":
        board = pcbnew.LoadBoard(PCB)
        assert pcbnew.ImportSpecctraSES(board, sys.argv[2]), "SES import failed"
        tidy(board)
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        save(board)
    elif cmd == "finish":
        finish()
