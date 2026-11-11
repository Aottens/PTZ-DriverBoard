# hardware/

The driver board, Rev B: a two-layer carrier for plug-in modules. The specs in `specs/modules/` say what each part
is for; this says how the files are made. Rev A, the four-layer board with its drivers on board, is under the git
tag `rev-a` (`git show rev-a:hardware/README.md`).

## What is where

| File | What |
| --- | --- |
| `ptz-driver.kicad_pro`, `.kicad_sch`, `.kicad_pcb` and the sheet files | The KiCad 10 project. Open it in KiCad to look; change it through the scripts |
| `tools/circuit.py` | The circuit as data: every part, net, footprint and LCSC number. Writes the schematic |
| `../firmware/include/pins.h` | The one place MCU pins are assigned |
| `tools/make_libs.py`, `ptz.pretty/` | The project's footprints: the three module sockets, the 5 V regulator, the test point |
| `tools/placement.py` | Where every part sits, and the copper laid before routing: the supply path, the motor outputs |
| `tools/board.py`, `tools/silk.py` | The board build (place, dsn, ses, finish) and the silkscreen |
| `route/run.sh`, `tools/complete.py`, `tools/widen.py` | Routing from scratch: Freerouting, then the grid router that closes what it leaves open and stitches the ground pours, then supply tracks widened where the routers necked them |
| `tools/project.py` | Design rules and net classes (KiCad rewrites the project file, so they live here) |
| `check_netlist.py` | Expected pin-to-net table per criterion, written from the specs without the schematic |
| `check_board.py` | Every number `specs/modules/board.md` states, plus ERC and DRC |
| `tools/groundcut.py` | The narrowest cross-section of ground copper between two groups of pads (BRD-13), used by `check_board.py` |
| `check_fit.py` | The board with its modules, heat sinks and plugs in the working envelope |
| `calc/power.py`, `calc/cost.py` | The calculations, with every input and its source |
| `fab/make_jlc.py`, `fab/jlc/`, `fab/gerbers/` | BOM and placement file fitted on JLC's own footprints, and the Gerbers |
| `fab/jlc_pins.py`, `fab/jlc_pins.md` | What JLC's own library calls each pin of every polar part, against the board's nets |
| `sourcing/` | JLC's parts API (`jlc_api.py`) and the check table per BOM line (`jlc_check.md`) |
| `review/` | The blind review and what was done with it |
| `ASSEMBLY.md`, `BUILD_NOTES.md`, `datasheets/README.md` | What the owner buys, solders and plugs; lessons; datasheet sources and revisions |

## Rebuilding from scratch

`KP` is KiCad's Python: `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`.
Run from `hardware/`.

1. `python3 tools/make_libs.py`: project footprints, library tables, project rules.
2. `python3 tools/circuit.py`: the schematic. It reads the netlist back through KiCad and stops if it differs.
3. `python3 check_netlist.py`
4. `sh route/run.sh`: places every part, routes, finishes the board and widens its supply tracks, about five minutes. **This discards the
   routing**, and Freerouting is not repeatable: a rerun gives another board. What was done by hand on the board
   in this repository afterwards is in `BUILD_NOTES.md` under *How the routed board was made*.
5. `$KP check_board.py` and `$KP check_fit.py`
6. `$KP fab/make_jlc.py`, `python3 sourcing/jlc_read.py`, `python3 fab/jlc_pins.py > fab/jlc_pins.md`,
   `python3 calc/cost.py`, and the Gerbers with `sh fab/make_gerbers.sh`.

A change that keeps the placement and the nets (a value, an LCSC number) needs only steps 2, 3 and 6, but the
footprint fields on the board then lag the schematic until step 4: `check_board.py` reports that as a parity
issue. `$KP tools/board.py finish` alone redraws the silkscreen and the top ground pour on the routed board.
