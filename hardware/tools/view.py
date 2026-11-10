#!/usr/bin/env python3
"""Draw a region of the board as a PNG, to look at placement, copper and silkscreen up close.

Run with KiCad's Python, from hardware/:
  .../python3 tools/view.py out.png [x0 y0 x1 y1] [--layers F,B,silk,refs,zones] [--size 2000]
Coordinates are board millimetres from the top-left corner. Uses macOS qlmanage to turn the SVG into a PNG.
"""
import os
import subprocess
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
OX = OY = 100.0
COLOUR = {"GND": "#888", "VM": "#d60", "VIN": "#d60", "VIN_RAW": "#d60", "+3V3": "#b0b", "+5V": "#b80"}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(a[2:].split("=") for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    layers = set(opts.get("layers", "F,B,refs").split(","))
    size = int(opts.get("size", 2000))
    out = args[0]
    board = pcbnew.LoadBoard(opts.get("board", os.path.join(os.path.dirname(HERE), "ptz-driver.kicad_pcb")))
    x0, y0, x1, y1 = [float(v) for v in args[1:5]] if len(args) >= 5 else (-1, -1, 86, 66)
    side = max(x1 - x0, y1 - y0)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {side} {side}" width="{size}" height="{size}">',
         f'<rect x="{x0}" y="{y0}" width="{side}" height="{side}" fill="white"/>']

    def u(v, o):
        return v / 1e6 - o

    if "zones" in layers:
        for z in board.Zones():
            col = COLOUR.get(z.GetNetname(), "#0a0")
            poly = z.Outline()
            pts = " ".join(f"{u(poly.CVertex(i).x, OX):.2f},{u(poly.CVertex(i).y, OY):.2f}" for i in range(poly.TotalVertices()))
            s.append(f'<polygon points="{pts}" fill="{col}" fill-opacity="0.08" stroke="{col}" stroke-width="0.08" stroke-dasharray="0.4 0.3"/>')
    for layer, name, col in ((pcbnew.B_Cu, "B", "#36c"), (pcbnew.F_Cu, "F", "#c22")):
        if name not in layers:
            continue
        for t in board.GetTracks():
            if t.Type() == pcbnew.PCB_VIA_T or t.GetLayer() != layer:
                continue
            s.append(f'<line x1="{u(t.GetStart().x, OX):.3f}" y1="{u(t.GetStart().y, OY):.3f}" x2="{u(t.GetEnd().x, OX):.3f}" '
                     f'y2="{u(t.GetEnd().y, OY):.3f}" stroke="{col}" stroke-width="{t.GetWidth() / 1e6:.3f}" stroke-linecap="round" stroke-opacity="0.75"/>')
    for fp in board.GetFootprints():
        cy = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
        if cy.GetWidth():
            s.append(f'<rect x="{u(cy.GetLeft(), OX):.2f}" y="{u(cy.GetTop(), OY):.2f}" width="{cy.GetWidth() / 1e6:.2f}" '
                     f'height="{cy.GetHeight() / 1e6:.2f}" fill="none" stroke="#999" stroke-width="0.04"/>')
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            col = COLOUR.get(p.GetNetname(), "#226" if p.GetNetname() else "#bbb")
            s.append(f'<rect x="{u(bb.GetLeft(), OX):.3f}" y="{u(bb.GetTop(), OY):.3f}" width="{bb.GetWidth() / 1e6:.3f}" '
                     f'height="{bb.GetHeight() / 1e6:.3f}" fill="{col}" fill-opacity="0.8"/>')
            if p.GetDrillSize().x:
                s.append(f'<circle cx="{u(p.GetPosition().x, OX):.3f}" cy="{u(p.GetPosition().y, OY):.3f}" r="{p.GetDrillSize().x / 2e6:.3f}" fill="white"/>')
        if "refs" in layers and cy.GetWidth():
            small = cy.GetWidth() * cy.GetHeight() < 4e12
            s.append(f'<text x="{u(cy.GetCenter().x, OX):.2f}" y="{u(cy.GetCenter().y, OY) + 0.2:.2f}" font-size="{0.55 if small else 1.0}" '
                     f'text-anchor="middle" font-family="Helvetica" fill="#060">{fp.GetReference()}</text>')
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            col = COLOUR.get(t.GetNetname(), "#080")
            s.append(f'<circle cx="{u(t.GetPosition().x, OX):.3f}" cy="{u(t.GetPosition().y, OY):.3f}" r="{t.GetWidth(pcbnew.F_Cu) / 2e6:.3f}" fill="{col}"/>')
            s.append(f'<circle cx="{u(t.GetPosition().x, OX):.3f}" cy="{u(t.GetPosition().y, OY):.3f}" r="{t.GetDrill() / 2e6:.3f}" fill="white"/>')
    if "silk" in layers:
        for d in list(board.GetDrawings()) + [g for fp in board.GetFootprints() for g in fp.GraphicalItems()]:
            if d.GetLayer() != pcbnew.F_SilkS:
                continue
            if d.GetClass() in ("PCB_TEXT", "PCB_FIELD"):
                s.append(f'<text x="{u(d.GetPosition().x, OX):.2f}" y="{u(d.GetPosition().y, OY) + d.GetTextHeight() / 2.6e6:.2f}" font-size="{d.GetTextHeight() / 1e6 * 1.2:.2f}" '
                         f'text-anchor="middle" font-family="Helvetica" fill="#000" transform="rotate({-d.GetTextAngleDegrees():.0f} {u(d.GetPosition().x, OX):.2f} {u(d.GetPosition().y, OY):.2f})">{d.GetText()}</text>')
            elif d.GetClass() == "PCB_SHAPE" and d.GetShape() == pcbnew.SHAPE_T_SEGMENT:
                s.append(f'<line x1="{u(d.GetStart().x, OX):.2f}" y1="{u(d.GetStart().y, OY):.2f}" x2="{u(d.GetEnd().x, OX):.2f}" y2="{u(d.GetEnd().y, OY):.2f}" stroke="#000" stroke-width="0.12"/>')
        for fp in board.GetFootprints():
            r = fp.Reference()
            if r.IsVisible() and r.GetLayer() == pcbnew.F_SilkS:
                s.append(f'<text x="{u(r.GetPosition().x, OX):.2f}" y="{u(r.GetPosition().y, OY) + r.GetTextHeight() / 2.6e6:.2f}" font-size="{r.GetTextHeight() / 1e6 * 1.2:.2f}" '
                         f'text-anchor="middle" font-family="Helvetica" fill="#000" transform="rotate({-r.GetTextAngleDegrees():.0f} {u(r.GetPosition().x, OX):.2f} {u(r.GetPosition().y, OY):.2f})">{r.GetText()}</text>')
    s.append(f'<rect x="0" y="0" width="{u(board.GetBoardEdgesBoundingBox().GetRight(), OX):.2f}" height="{u(board.GetBoardEdgesBoundingBox().GetBottom(), OY):.2f}" fill="none" stroke="#000" stroke-width="0.1"/>')
    s.append("</svg>")
    svg = out[:-4] + ".svg"
    open(svg, "w").write("\n".join(s))
    subprocess.run(["qlmanage", "-t", "-s", str(size), "-o", os.path.dirname(os.path.abspath(out)), svg], capture_output=True)
    os.replace(svg + ".png", out)


if __name__ == "__main__":
    main()
