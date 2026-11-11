# Build notes

What has to survive a long run. One lesson per entry, newest at the bottom. Entries 1 to 25 are from Rev A (the
four-layer board, git tag `rev-a`); they stay because the tools and the habits are the same. From 26 on: Rev B.

## From Rev A

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
24. **A plane tie has no length limit, and that bit.** A round tied a 3.3 V pin to its plane with a 7 mm track between the crystal's pads, because the near spots were taken; it also laid the same track once per open end. A round now removes doubled tracks. Look at every long supply track after routing; a plane tie longer than a few millimetres is a sign that a via spot is missing.
25. **Review the routing of the two crystal pins by eye before the blind review does.** The router closed them last and worst.

## From Rev B

26. **Count the cost before the parts, and count JLC's three libraries.** JLC has 351 Basic parts and about 1 200
    flagged Preferred; neither carries the $3.07 loading fee on Economic PCBA. `sourcing/jlc_api.py` reads the same
    JSON the parts page uses (`.../smtGood/selectSmtComponentList`), with `componentLibraryType: "base"` or
    `preferredComponentFlag: true` as a filter, so the whole fee-free list can be pulled once and searched. No
    fuse, electrolytic, power inductor, thermistor or P-channel power FET is on it: decide early which of those the
    owner solders as a through-hole part.
27. **A part JLC assembles is bought five times, a part the owner solders once.** Moving the regulator, the fuses
    and the bulk capacitors off the JLC order saved their Extended fees and four of every five parts.
28. **The PCBA Type is not in the parts API.** It is only on `jlcpcb.com/partdetail/<number>`, which WebFetch reads.
29. **The N8 DevKitC is end of life.** Espressif's user guide marks it so; the N16R8 is what shops sell, and its
    octal memory takes GPIO35 to 37. A pin table that avoids them fits both. Read the ordering table of a dev
    board before trusting the PRD's variant.
30. **A module is a footprint with a drawing behind it.** Rows, spacing, which end is pin 1 and which way the
    jack opens came from the makers' drawings (Espressif's DXF, WIZnet's page 10, BIGTREETECH's size drawing), and
    an agent's summary of a drawing was wrong once (the jack's direction): look at the drawing yourself.
31. **Give a socket courtyards around its pin rows only.** Then low parts can stand under the module and the DRC
    still catches a part on a pin row; the height under the module is `check_board.py`'s job (BRD-11).
32. **A router treats a pour as a plane it may cut.** Freerouting ran signal tracks through the VIN pour and cut it
    in two. The supply path is now laid as tracks of the wanted width (`placement.TRACKS`), which a router leaves
    whole, with the pour only as extra copper on the bottom.
33. **Pre-route the pins a router cannot reach, and it routes the rest in a minute.** On two layers with 2.54 mm
    headers Freerouting needs under a minute and leaves about ten connections open, always around the same spots:
    a supply pin of a SOT-23-6 shut in by its neighbours, a jumper pad in a crowded corner. A via and a track for
    each in `placement.py` cost less than any router round.
34. **A grid router that never moves a track is enough on two layers.** `tools/complete.py` is a third of Rev A's:
    A* on a 0.1 mm grid, one grid per track width and gap, no pushing. It runs each round in its own process (16).
35. **Stitch the pours, then look for loose pieces.** A ground pour cut up by tracks leaves pieces that hang on one
    pad. `complete.py` puts vias on a 2.5 mm raster where both layers carry ground, then gives every remaining
    piece a via of its own or a track to the main body. A second stitching pass must skip the vias of the first:
    it once drilled 199 holes twice.
36. **Solid pour connections on a board the owner solders.** Thermal spokes left ground pins of the driver sockets
    on one spoke or on a loose piece of pour; the pours now connect solid. Ground pins need a second longer with
    the iron.
37. **Freerouting necks tracks down at fine-pitch pads** (0.19 mm at a SOT-23-6, 0.38 mm on a 0.5 mm net) and once
    paired a 0.4 mm drill with a 0.6 mm pad. `board.py` repairs the via; the necks are allowed in BRD-05 and
    BRD-06 and counted by `check_board.py`.
38. **Let an independent check be independent.** `check_netlist.py` was written by a fresh agent from the specs
    alone. It found ten places where the specs did not say enough to write a check; each was a spec defect, fixed
    in the spec, never in the check alone.
39. **JLC's own symbol tells the pin order of its footprint.** `fab/jlc_pins.py` prints what JLC's library calls
    each numbered pin (G, S, D; C and A; the plus of a tantalum is drawn at pin 1). That settles a rotation
    question before the preview does.
40. **A calculation should be allowed to overturn a part.** The first sensor-supply regulator limited a short to
    100 mA, which looked fine until the product with 4.6 V was set against its 0.25 W package. Three SOT-23 FETs in
    parallel looked fine until the fuse's let-through was set against them. Both are in `calc/power.py` now.
41. **A module that is soldered in has no room under it.** A module on 8.5 mm sockets leaves 2.1 mm for parts
    under it; the Ethernet module, soldered in for its height, leaves none. The first placement had ten parts
    there. `check_board.py` now holds a rule per module: how high a part under it may be, and for this one, none.
42. **An option nobody asked for is a liability.** The fan jumper to the motor supply looked like a free knob; it
    put an output on a 5 A fuse behind a 0.5 mm track. The blind review found it, and the PRD had never asked.
43. **Sum the capacitance a small regulator module must charge.** These modules name a largest capacitive load
    (220 to 680 µF here), and a board collects 22 µF and 100 µF parts quickly. The sum is in `calc/power.py`; it
    ruled one module out.
44. **Keep the fault line off the strapping pins.** A pin that must be low to enter download mode may carry a
    direction signal, not a line that a plugged-in module can hold high.
45. **A router that necks a supply track keeps the neck.** Freerouting and `complete.py` both lay the whole
    connection at the width that passed the tightest spot. `tools/widen.py` sets every such piece to full width,
    lets DRC name the ones that do not fit, and steps only those down.
46. **Show the output of every step in a build script.** `run.sh` once sent `board.py finish` to `/dev/null`, so a
    silkscreen that could not place a name stopped the build with nothing on the screen.
47. **Write the pin table to a file, and filter it by footprint, not by value.** `fab/jlc_pins.py` chose polar
    capacitors by the text "100 µF"; when the tantalums became 10 µF they dropped out of the table unnoticed.
48. **On two layers, lay the ground before the signals.** A router sees a pour as space it may cut, and a bus
    between two rows of modules cuts both pours from edge to edge: the first two routings left 4 mm of ground
    between the drivers and everything else, and DRC cannot see that. The ground that must stay whole is now a set
    of tracks in `placement.py`, and `tools/groundcut.py` measures what joins two groups of pads (max-flow on a
    raster of the copper).
49. **A wide track ends in a half circle.** A 3 mm bridge that stopped 2 mm from a pin row shorted to a pin with
    its round end. Count half the width beyond every end point.
50. **Protect each branch behind its own fuse.** A TVS behind the motor fuse does nothing for the logic branch
    while that fuse is out, which is exactly how a careful first power-up is done.
51. **Empty the zip before filling it.** `zip -r` adds to an archive that exists, so two files the script no
    longer made stayed in the Gerber zip.
52. **A second blind review finds different things.** The first reviewer read parts and heights, the second
    measured copper. Neither repeated the other.

## How the routed board was made (2026-11-11)

From `hardware/`, with `KP` the KiCad Python from `CLAUDE.md`. Freerouting is not repeatable, so a rerun gives
another board; the steps are.

1. `sh route/run.sh 20`: `board.py place` (the log must say "186 footprints placed"), `board.py dsn`, Freerouting
   headless with 20 passes (about a minute), `board.py ses`, `board.py finish`, `complete.py 4`, `widen.py`. The
   board in this repository is the third routing: each blind review moved parts or added copper.
2. `$KP check_board.py` and `$KP check_fit.py`.

Done by hand on this board afterwards, with a few lines of pcbnew, and not in any script:
- three signal tracks (`SPI_MISO`, `SPI_SCK`, `STEP2`) that Freerouting laid 0.0025 mm too close to a jumper pad
  were made 0.24 mm wide instead of 0.25 mm.
