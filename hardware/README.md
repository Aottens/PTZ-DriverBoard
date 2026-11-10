# hardware/

The driver board, Rev A. The specs in `specs/modules/` say what each part is for; this says how the files are made.

## What is where

| File | What |
| --- | --- |
| `ptz-driver.kicad_pro`, `.kicad_sch`, `.kicad_pcb` and the sheet files | The KiCad 10 project. Open it in KiCad to look; change it through the scripts |
| `tools/circuit.py` | The circuit as data: every part, net, footprint and LCSC number. Writes the schematic |
| `../firmware/include/pins.h` | The one place MCU and expander pins are assigned |
| `tools/placement.py`, `tools/board.py`, `tools/silk.py` | Where parts sit, the board build, the silkscreen |
| `tools/complete.py` | Pre-routes before Freerouting (`fanout`), the rounds that close what it leaves open, `prune` |
| `tools/project.py` | Design rules and net classes (KiCad rewrites the project file, so they live here) |
| `check_netlist.py` | Expected pin-to-net table per criterion, written from specs and datasheets without the schematic |
| `check_board.py` | Every number `specs/modules/board.md` states, plus ERC and DRC |
| `check_fit.py` | The board with its plugs in the working envelope |
| `calc/power.py`, `calc/thermal.py` | The calculations, with every input and its source |
| `fab/make_jlc.py`, `fab/jlc/`, `fab/gerbers/` | BOM and CPL fitted on JLC's own footprints, and the Gerbers |
| `sourcing/` | What JLC's part pages said, and the check table per BOM line |
| `review/` | The blind review and what was done with it |
| `ASSEMBLY.md`, `BUILD_NOTES.md`, `datasheets/README.md` | Fitting it in the base; lessons; datasheet sources and revisions |

## Rebuilding from scratch

`KP` is KiCad's Python: `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`.
Run from `hardware/`.

1. `python3 tools/make_libs.py`: project footprints, library tables, project rules.
2. `python3 tools/circuit.py`: the schematic. It reads the netlist back through KiCad and stops if it differs.
3. `python3 check_netlist.py`
4. `$KP tools/board.py place`: a fresh board with every part placed, planes, pours and keep-outs. **This discards the routing.**
5. `$KP tools/complete.py fanout`, then the DSN export, Freerouting and the session import, then `$KP tools/complete.py`
   until nothing is open and `$KP tools/complete.py prune`. The exact commands, and what was done by hand on the
   board in this repository, are in `BUILD_NOTES.md` under *How the routed board was made*. Routing is not repeatable.
6. `$KP tools/board.py finish`: widens motor and supply tracks, pours ground on both outer layers, opens the heat
   windows, draws the silkscreen.
7. `$KP check_board.py` and `$KP check_fit.py`
8. `$KP fab/make_jlc.py`, `python3 sourcing/jlc_read.py`, and the Gerbers with `sh fab/make_gerbers.sh`.

A change that keeps the placement (a value, an LCSC number) needs only steps 2, 3 and 8, but the footprint fields on
the board then lag the schematic until step 4: `check_board.py` reports that as a parity issue.
