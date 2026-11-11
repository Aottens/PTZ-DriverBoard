#!/usr/bin/env python3
"""Widen the logic supply tracks that the routers left thinner than 0.5 mm (BRD-06).

Freerouting and complete.py neck a supply track down where it passes fine-pitch pads, and then keep that
width for the rest of the connection. This sets every such piece to 0.5 mm, lets DRC say which pieces do not
fit, and steps only those down: 0.45, 0.4, 0.35 mm, and last the width the router gave.

Run from hardware/ with KiCad's Python:  tools/widen.py
"""
import json
import os
import subprocess
import sys
import tempfile

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.join(HERE, "..", "ptz-driver.kicad_pcb")
CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
NETS = ("VIN_L", "+5V_REG", "+5V", "+3V3", "+3V3_SNS", "V_SNS", "FAN_N")
STEPS = (0.5, 0.45, 0.4, 0.35)
STATE = os.path.join(tempfile.gettempdir(), "ptz_widen.json")


def one_round():
    """Apply the widths in STATE, ask DRC, step the offenders down. Returns how many were stepped down."""
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    board = pcbnew.LoadBoard(PCB)
    tracks = {t.m_Uuid.AsString(): t for t in board.GetTracks()
              if t.Type() != pcbnew.PCB_VIA_T and t.GetNetname() in NETS}
    for u, t in tracks.items():
        if u not in state and t.GetWidth() < 0.5e6 - 1:
            state[u] = [0, t.GetWidth()]          # step, the router's own width
    for u, (step, own) in state.items():
        if u in tracks:
            tracks[u].SetWidth(int(STEPS[step] * 1e6) if step < len(STEPS) and STEPS[step] * 1e6 > own else own)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(PCB)
    out = os.path.join(tempfile.mkdtemp(), "drc.json")
    subprocess.run([CLI, "pcb", "drc", "--format", "json", "--severity-all", "-o", out, PCB], capture_output=True)
    hit = {i.get("uuid") for v in json.load(open(out)).get("violations", []) for i in v.get("items", [])}
    down = [u for u in state if u in hit and state[u][0] < len(STEPS)]
    for u in down:
        state[u][0] += 1
    json.dump(state, open(STATE, "w"))
    widths = sorted(tracks[u].GetWidth() / 1e6 for u in state if u in tracks)
    print(f"  {len(state)} pieces, {len(down)} stepped down; narrowest now {widths[0] if widths else 0.5:.2f} mm")
    return len(down)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--round"]:              # one round per process, as in complete.py
        sys.exit(min(one_round(), 250))
    if os.path.exists(STATE):
        os.remove(STATE)
    for _ in range(len(STEPS) + 2):
        if not subprocess.run([sys.executable, os.path.abspath(__file__), "--round"]).returncode:
            break
