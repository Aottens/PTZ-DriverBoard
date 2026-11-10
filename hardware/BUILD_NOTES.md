# Build notes, Rev A

What has to survive a long run. One lesson per entry, newest at the bottom.

1. **analog.com datasheets** do not load through curl or WebFetch. In the built-in browser they do, and pdf.js from cdnjs can be imported in the page to pull text per page (`import('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.mjs')`, then `getDocument({data})`).
2. **JLC part pages:** WebFetch on `jlcpcb.com/partdetail/C<nr>` gives the PCBA Type but no stock. The same page in the built-in browser shows "In Stock" in its text after about 2 s.
3. **jlcsearch.tscircuit.com** misses many parts (TMC5240, most JST originals) and its database overloads under bursts. Pace requests and never read "no result" as "does not exist".
4. **Schematic generation:** every pin gets a global label, so a net is its name. `circuit.py` reads the netlist back through kicad-cli after writing and refuses to pass if KiCad reads a different one.
5. **UUIDs are uuid5 of sheet and reference**, so regenerating the schematic keeps the board's links.
6. **The ESP32-C6-MINI-1U antenna connector is a third-generation part** (W.FL, MHF III, AMMC), not U.FL (datasheet v1.5 p42). The pigtail must match.
7. **TMC5240 SLEEPN may not exceed VS + 0.3 V** (p10), so it is tied to VM, not to 3.3 V, which is alive on USB power when VM is not.
8. **Area count before layout:** all features on 85 x 65 mm, top side only, came to about 76 % courtyard fill. The RJ45 jack went first (CTL-03 order). Count area per region before choosing connectors next time.
9. **The motor side of the TMC5240 TQFN is one edge** (pins 17 to 24). OUT1B and OUT2B come out in the opposite order to OUT1A and OUT2A, so a planar route to a 4-pin connector needs the order A1 A2 B2 B1.
10. **Freerouting runs headless only** (`-Djava.awt.headless=true ... --gui.enabled=false`). With the GUI it throws exceptions in its paint thread and once wrote an empty session file. It stops improving after about 13 passes on this board (2 minutes each); `-mp 14` is enough.
11. **Freerouting's own "unrouted" count is not KiCad's.** It reported 250 to 340 open where KiCad's DRC, after import, found 45 to 55. Only the DRC count after `board.py ses` means anything.
12. **Freerouting does not tie supply pads to inner planes once the top layer is full**, and it does not finish the drivers' SPI pins. `tools/complete.py fanout` lays these on the placed board before routing, and the DSN export marks them `(type protect)`.
13. **KiCad writes an inner layer set to "power" as `(type power)` in the DSN**, and Freerouting then leaves it alone. `board.py dsn` sets both inner layers to power: given inner layer 2 as a signal layer, Freerouting cut the +3V3 plane into about twenty pieces. Only `complete.py` lays tracks there, and sparingly. Check the printed layer types after every export: a failed assert there once left an unpatched DSN behind that the router then used.
14. **A shell pipeline hides a failed step.** `board.py place | tail` returns tail's status; a failed placement then let the next step run on the old board. Write the log to a file and test it.
15. **Tracks on inner layer 2 cut pieces off the +3V3 plane.** A via on such a piece reaches nothing. After routing, `complete.py` tests against the largest filled piece (`filled_plane`), not the plane's outline.

16. **KiCad's Python frees what you remove from a board, and the board breaks.** A track taken off with `board.Remove()` and then garbage-collected left the net list in a state where `GetNetCode` failed on unrelated items. Keep every removed item in a list for the life of the script (`GRAVE` in `complete.py`, `KEEP` in `board.py`), and do not load the same board twice in one process.
17. **My own pre-routes fenced pins in.** Local tracks from pin to pin and from capacitor to capacitor ran along a pin row and shut the pins behind them; long escape stubs did the same. What works: before routing, connect only an IC pin with its own passive, tie every supply pad to its plane first, keep escape stubs short (1.6 mm outside the drivers), and keep unused escape vias until the very end (`complete.py prune`).
18. **A grid router must be allowed to stand on its own copper.** Three rules cost most of the last open connections: a via of the same net counted as an obstacle for a layer change; a search ran from one point to one point, while any copper of the two pieces would do; and a track laid legally 0.154 mm from a neighbour was "blocked" in the grid, so a search starting on it went nowhere. `complete.py` now changes layer on its own vias, searches from every cell of one piece to any cell of the other, and as a last try may move pushed nets and pre-routed stubs.
19. **Placement order around a fine-pitch row decides whether it routes.** Three adjacent W5500 pins went to three capacitors standing in another order, which cannot be done on one layer; swapping two equal capacitors solved it (`placement.SWAP`). A supply via put in front of a crystal pin sent the crystal track under the chip and shut the next pin in. Look at such rows before routing, not after.
20. **Size is the cheapest routing tool.** On 85 x 65 mm (73 % courtyard fill) the board stopped at 39 open connections after days of router work. On 100 x 80 mm (50 %) Freerouting alone left 32 and the completion rounds closed them. Ask early whether the envelope is really fixed: it was not, the board moved from the head to the base.
21. **Widening needs pieces.** A single long segment from a 0.25 mm pad to a connector can only be as wide as its narrowest spot. `board.py finish` cuts supply and motor segments into 0.5 mm pieces first and widens in two passes (to 0.6 mm, then to the class width), so neighbours share the room.
22. **A footprint's silkscreen cannot be moved on the board** without a library mismatch in the DRC. When a neighbour's pad lies on a pin 1 mark, move the neighbour (`placement.SHIFT`).
23. **An unplated hole wants 0.25 mm to copper**, not the 0.15 mm of a pad. Both the router grid and the widening needed the larger figure for the USB-C socket's locating holes.

## How the routed board was made (2026-11-10)

From `hardware/`, with `KP` the KiCad Python from `CLAUDE.md`. Freerouting is not repeatable, so a rerun gives another board; the steps are.

1. `$KP tools/board.py place > place.log 2>&1`; the log must say "0 without a place".
2. `$KP tools/complete.py fanout`: motor outputs, the drivers' bus, plane ties, pin-to-passive tracks and escape vias. Expect no "not routed" and no "no way out".
3. `cp ptz-driver.kicad_pcb route/rev-a_input.kicad_pcb`, `$KP tools/board.py dsn route/rev-a.dsn`: two `(type power)` layers, the pre-routes as `(type protect)`.
4. In `route/`: `java -Djava.awt.headless=true -jar ~/.kicad-mcp/freerouting.jar -de rev-a.dsn -do rev-a.ses -mp 14 --gui.enabled=false`, about half an hour, as a background job.
5. `cp route/rev-a_input.kicad_pcb ptz-driver.kicad_pcb`, `$KP tools/board.py ses route/rev-a.ses`, `$KP tools/board.py finish`.
6. `$KP tools/complete.py 6`, again until "0 unconnected" with no bad items left; then `$KP tools/complete.py prune` and two more rounds.
7. `$KP tools/board.py finish`, then `$KP check_board.py` and `$KP check_fit.py`.

Done by hand on this board, between steps 6 and 7, and not in any script: the +3V3 via in front of U801's crystal pin and ETH_XI's detour under the chip were taken out and routed again by step 6; each driver's B1 output was moved 0.1 mm away from the VCP capacitor, and the +5V track on inner layer 2 0.1 mm away from a via, so both reach their width. C804/C808 and the small shifts of C201 and the IREF resistors were also made on the routed board; these are in `placement.py`, so a new placement has them from the start.
