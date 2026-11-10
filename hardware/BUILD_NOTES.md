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

## Paused on 2026-11-10, at the owner's request (token use)

Done and committed: module specs, `pins.h`, schematic (ERC 0), `check_netlist.py` by a separate agent (39 criteria,
963 pins, 0 mismatches), calculations, fit check (0 failures on the placed board), placement, board tools, silkscreen
script, JLC footprint fit, JLC part readings, bring-up checklist, ASSEMBLY, DECISIONS, ARCHITECTURE.

Running when paused: Freerouting on `hardware/route/rev-a.dsn`, started detached, writing `hardware/route/rev-a.ses`
and `freerouting.log`. `rev-a_input.kicad_pcb` is the placed board that DSN belongs to. Nothing watches it.

To resume, in this order:
1. Check `route/freerouting.log` for the last "Auto-routing pass" line and whether `route/rev-a.ses` exists.
2. `cp route/rev-a_input.kicad_pcb ptz-driver.kicad_pcb`, then `$KP tools/board.py ses route/rev-a.ses`, then
   `$KP tools/board.py finish`. Neither `ses` nor `finish` has run on a routed board yet: expect fixes.
3. `$KP check_board.py` (untested on a routed board), DRC to zero, route leftovers by hand or with a small router.
4. Look at copper and silkscreen with `tools/view.py`, cropped and zoomed.
5. `fab/make_jlc.py`, `sourcing/jlc_read.py`, Gerbers (no `fab/make_gerbers.sh` yet), JLC preview checklist.
6. Blind review by a fresh agent into `hardware/review/`, handle findings, review again after real changes.
7. STATE, BACKLOG (RA-01), README, push, one PR with `## Tracking`, final report in Dutch.
