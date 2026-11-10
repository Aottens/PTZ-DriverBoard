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
