# What was done with the blind review of Rev A

The review is `BLIND_REVIEW.md`, as the reviewer wrote it on 2026-11-11. Reasons for each accepted BELANGRIJK finding
are in `DECISIONS.md` (2026-11-11). `BLIND_REVIEW_2.md` is the second look, after the changes below.

| Finding | Class | Done | Where |
| --- | --- | --- | --- |
| B1 3.3 V output on one thin track and one via | BELANGRIJK | Fixed: six vias, 0.5 mm tracks | `tools/placement.py` `MORE_VIAS`, `tools/board.py` `WIDE_NETS` |
| B2 crystal tracks of the W5500 | BELANGRIJK | XI fixed (top layer only, 2.4 mm). XO shortened from 36 mm and five vias to 22 mm and three; the rest accepted | `DECISIONS.md`; bring-up 7.1b |
| B3 TVS D102 rotation not verifiable | BELANGRIJK | Accepted with two checks | JLC preview checklist in the pull request; bring-up 0.3b |
| B4 sensor ports: clock must rest low | BELANGRIJK | Accepted as a stated limit | `specs/modules/sensing.md` ENC-05; bring-up 5.2b |
| B5 four axes at 1.5 A RMS run hot | BELANGRIJK | Accepted; heat windows, fan output and firmware current reduction exist | `calc/thermal.py`; bring-up 4.4 and 4.8 |
| K1 driver decoupling through the plane; one via per 220 µF capacitor | KLEIN | Bulk capacitors: three vias per pad now. Decoupling through the plane left as is: 3 to 4 mm of plane, and the motor outputs own the top layer there | `MORE_VIAS` |
| K2 TVS margin to 41 V | KLEIN | Left: the margin is real for a supply set to 24 V; a supply above 26 V is outside POW-01 | `specs/modules/power.md` |
| K3 5 V regulator: no vias under the pad, loop through the plane | KLEIN | Left: the 5 V load is low (`calc/power.py`) | |
| K4 USB wins over the 5 V rail | KLEIN | Left: intended, USB alone must run the logic (POW-05) | |
| K5 short on a sensor chip select exceeds the decoder's 50 mA; J801 pin 1 beside ground | KLEIN | Chip select fixed: 100 Ω instead of 33 Ω (ENC-06). J801 left: it follows WIZnet's reference, and the lead is wired once inside the base | `tools/circuit.py`, `check_netlist.py` |
| K6 one PTC for four sensor ports | KLEIN | Left: stated in ENC-07 | |
| K7 GPIO4 and GPIO5 float during reset | KLEIN | Left: both are strapping pins, so they get no resistors; the decoder's strobes are high and nothing is selected | |
| K8 no ESD clamps on sensor SPI, CAN, I2C, camera, BOOT | KLEIN | Left for Rev A: internal cables in a closed base; noted for Rev B | |
| K9 connectors on both long edges, parts near H3 | KLEIN | Left: all upright, plugged before the board goes in (`ASSEMBLY.md` step 2); `check_fit.py` checks the screw's reach | |
| K10 test points and silkscreen | KLEIN | Left: passives carry no reference by choice at this density; the legend is on the back | |
| K11 bus routing: USB pair, long SPI clock, tracks through the 3.3 V plane | KLEIN | Left: full-speed USB tolerates it by the reviewer's own figure; the SPI clock rate is a firmware setting, to be raised step by step at bring-up | |
| K12 eight DRC checks ignored | KLEIN | Left: each has its reason in `tools/project.py`; the reviewer found nothing harmful with them on | |
| K13 HASL, X-ray for the module, lowest stock | KLEIN | For the owner at the order: ENIG costs more and is not needed at 0.5 mm pitch; the X-ray charge is JLC's | pull request |
| K14 green and blue LED dim | KLEIN | Left: a status light; the resistor values can change on a later revision | |
| K15 fuse F101 breaks 50 A | KLEIN | Left: the board is for a current-limited supply, not a battery (POW-01) | |
