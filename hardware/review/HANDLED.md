# What was done with the blind review of Rev B

The review is `BLIND_REVIEW.md`, as the reviewer wrote it on 2026-11-11 from `BRIEF.md`, the design files and the
datasheets: no KRITIEK finding, three BELANGRIJK, fourteen KLEIN. The reason for each accepted finding is in
`DECISIONS.md` (2026-11-11, *Rev B: what was done with the blind review*). `BLIND_REVIEW_2.md` is the second
review, by a fresh reviewer, of the board after the changes below; its findings are in the second table.

## First review

| Finding | Class | Done | Where |
| --- | --- | --- | --- |
| B1 ten parts under the Ethernet module, which sits 2.54 mm above the board | BELANGRIJK | Fixed: nothing stands under the module now; port 4's parts moved west of it | `tools/placement.py`; BRD-11 in `check_board.py` |
| B2 the fan output does not survive a short when set to VM | BELANGRIJK | Fixed: the VM option and its jumper are gone; the fan runs from 5 V only, behind the 5 V module's own protection | AUX-03 in `specs/modules/io.md`; `check_netlist.py` |
| B3 the board does not fix the 5 V module, and the R-78E falls outside its data sheet | BELANGRIJK | Fixed: capacitance on the 5 V and 3.3 V rails cut to 113 µF (C201 and C203 gone, 10 µF where 22 µF stood, 3 × 10 µF tantalum per regulator); the two modules that take the load are named in the spec, in `ASSEMBLY.md` and on the bottom silkscreen; the R-78E is ruled out | POW-07; `calc/power.py` section 5 |
| K1 +3V3 has little headroom above the AMS1117 | KLEIN | Accepted | `DECISIONS.md`; bring-up 1.3, 3.2, 6.1 |
| K2 DIAG_OR on strapping pin GPIO46 | KLEIN | Fixed: DIAG_OR is on GPIO3, GPIO46 carries DIR2 | `firmware/include/pins.h`; CTL-08; bring-up 4.6 |
| K3 the TMC2240's DIAG0 is open drain, active low, by default | KLEIN | Accepted as a firmware condition | DRV-05; bring-up 7.3 |
| K4 10 nF on HOME4 (GPIO43, the ROM's serial output) | KLEIN | Fixed: C603 is 1 nF | ENC-03; `check_netlist.py` |
| K5 the STEP lines float during reset | KLEIN | Fixed: 100 kΩ to ground on each (R310, R410, R510, R610) | DRV-02 |
| K6 multiplexer and Ethernet module reset only together with the MCU | KLEIN | Accepted: no pin is left | `DECISIONS.md` |
| K7 the minus sign at J101 is not beside pin 2 | KLEIN | Fixed: "+" beside pin 1, "-" beside pin 2 | `tools/silk.py`; looked at in the render |
| K8 all ground pins sit solid in the copper | KLEIN | Accepted | `ASSEMBLY.md`; `BUILD_NOTES.md` lesson 36 |
| K9 0.4 mm of height to spare above the drivers | KLEIN | Accepted: the heat sink's 12 mm is an assumption; a lower one or lower sockets give room | `ASSEMBLY.md`; bring-up 9.2 |
| K10 only the DevKitC-1U fits beside U101 | KLEIN | Accepted: the 1U is the module the PRD names | `ASSEMBLY.md` |
| K11 the RJ45 points to the east edge, 29 mm from the wall | KLEIN | Accepted: a hole in the wall or a short patch lead | `ASSEMBLY.md`, *What the base must provide* |
| K12 SMD parts close to the board edge | KLEIN | Accepted: 1.45 mm and 2.0 mm; to look at in JLC's order page | manufacturability flags in the pull request |
| K13 five BOM lines are probably Extended | KLEIN | Not so: JLC's parts API and part pages give three; the SMBJ18A and SRV05-4 are Preferred, free of the fee | `sourcing/jlc_check.md` |
| K14 a shorted sensor or home cable takes all logic down | KLEIN | Accepted: nothing is damaged, which is the requirement | `DECISIONS.md`; bring-up 5.7 |

## Second review

`BLIND_REVIEW_2.md`: no KRITIEK finding, three BELANGRIJK, fifteen KLEIN. The reviewer saw the board of commit
5dbc536. The two findings on the board itself are fixed and the board was routed once more; that last board is
the one the third review saw, in the third table.

| Finding | Class | Done | Where |
| --- | --- | --- | --- |
| B1 the ground of the motor half hangs on about 4 mm of copper | BELANGRIJK | Fixed: a ground spine and four bridges laid as tracks before routing; the VM test point moved off the east edge. Measured by `tools/groundcut.py`: 14.0 mm to the supply connector and 10.0 mm to the MCU module, from 4.2 mm for both | BRD-13; `tools/placement.py`; `check_board.py` |
| B2 no surge clamp on the logic branch while F101 is out; the FET's gate gets 0.6 × the input | BELANGRIJK | Fixed: D103, a second SMBJ18A, on `VIN_L`; R101 is 100 kΩ, so the gate gets half the input | POW-02; `calc/power.py` section 4; bring-up 0.3 |
| B3 26 to 32 mm between the RJ45 jack and the wall | BELANGRIJK | Accepted: no board change; a requirement on the base | `DECISIONS.md`; `ASSEMBLY.md`; RB-05 |
| K1 DIAG works only after firmware sets `diag0_pushpull` | KLEIN | Noted where firmware reads it | `firmware/include/pins.h`; bring-up 7.3 |
| K2 the DIAG pin of a BIGTREETECH TMC2209 V1.3 points up | KLEIN | Noted | `ASSEMBLY.md` |
| K3 the AMS1117 behind a Schottky has no headroom to spare | KLEIN | Accepted, as K1 of the first review | `DECISIONS.md` |
| K4 the 5 V budget is close to 1 A | KLEIN | Accepted: 0.86 A peak of 1 A with a 0.2 A fan, which is the stated limit for the fan | POW-09; `ASSEMBLY.md` |
| K5 a short on `V_SNS` or the fan pin pulls the 5 V rail down; on USB only the host limits it | KLEIN | Accepted, as K14 of the first review | `DECISIONS.md` |
| K6 reverse polarity is not covered with a grounded supply and USB to a grounded computer | KLEIN | Noted as a warning | `ASSEMBLY.md` |
| K7 the TVS clamp is at the TMC2209's operating limit | KLEIN | Accepted: below its absolute maximum, and the board's own sources do not reach the clamp current | `calc/power.py` sections 1 to 3 |
| K8 a DevKitC-1 of version 1.0 has its LED on GPIO48 | KLEIN | Noted: version 1.1 is the one to buy | `ASSEMBLY.md`; `pins.h` |
| K9 no firmware reset for multiplexer and Ethernet | KLEIN | Accepted, as K6 of the first review | `DECISIONS.md` |
| K10 all ground pads sit solid in the pour | KLEIN | Accepted, as K8 of the first review | `ASSEMBLY.md` |
| K11 tight fits between modules; the heat sink's height is an assumption | KLEIN | Accepted | `ASSEMBLY.md`; bring-up 9.2 |
| K12 `VIN_L`, `+5V_REG` and `+3V3_SNS` have no test point | KLEIN | Accepted: each is on a through-hole pin or a jumper pad a probe reaches (F102, U101 `IN` and `OUT`, JP101 `3V3`) | AUX-05 |
| K13 silkscreen: pin functions only on the bottom; texts at JP101 touch; the minus at J101 between the pads | KLEIN | The minus moved towards pin 2; the rest left: the top has no room for pin functions | `tools/silk.py` |
| K14 drill maps in the Gerber zip | KLEIN | Fixed: no drill maps are made | `fab/make_gerbers.sh` |
| K15 five lines are probably Extended | KLEIN | Not so: three, as K13 of the first review | `sourcing/jlc_check.md` |

## Third review

`BLIND_REVIEW_3.md`, of 2026-11-12, by a fresh reviewer who saw the board as it is ordered (the file of
2026-11-11 12:06, SHA-256 `7f8679c4…`): verdict *bestellen*, no KRITIEK finding, one BELANGRIJK, nine KLEIN.
Nothing on the board or in the JLC files changed. The reasons are in `DECISIONS.md` (2026-11-12).

| Finding | Class | Done | Where |
| --- | --- | --- | --- |
| B1 about 29 mm between the RJ45 jack and the wall | BELANGRIJK | Accepted before, as B3 of the second review: a requirement on the base | `DECISIONS.md` (2026-11-11); `ASSEMBLY.md`; RB-05 |
| K1 0.4 mm of height to spare above the driver heat sinks | KLEIN | Accepted before, as K9 and K11 | `ASSEMBLY.md`; bring-up 9.2 |
| K2 `+3V3` has little headroom above the AMS1117 | KLEIN | Accepted before, as K1 and K3 | `DECISIONS.md` (2026-11-11) |
| K3 multiplexer and Ethernet module reset only with the MCU module's EN pin | KLEIN | Accepted before, as K6 and K9 | `DECISIONS.md` (2026-11-11) |
| K4 only a genuine DevKitC-1U fits, version 1.1 for the LED; clones may have rows 25.4 mm apart | KLEIN | Noted: the row spacing is in the parts table now. The shopping list names Espressif's own board | `ASSEMBLY.md` |
| K5 JLC's placement point of an asymmetric part may lie up to 1.5 mm from the point in the CPL | KLEIN | Not so, by calculation: the CPL gives the origin of JLC's own footprint, and for Q101, U102, U103, Q801 and D302 that origin is the middle of JLC's pads, within 0.1 mm of the middle of ours. The preview still shows it | `fab/make_jlc.py`; preview checklist, last line |
| K6 on USB alone, SLEEPN of each TMC2240 module sits above VS + 0.3 V | KLEIN | Accepted: the module's own 4.7 kΩ limits it to about 0.6 mA. New bring-up step: the four modules may lift `VM` to under 3 V with no supply | `DECISIONS.md` (2026-11-12); bring-up 7.9 |
| K7 `VIN_L`, `+5V_REG` and `+3V3_SNS` have no test point | KLEIN | Accepted before, as K12 | AUX-05 |
| K8 the home inputs have no TVS array | KLEIN | Accepted: 10 kΩ in series and a BAV99 clamp protect the MCU pin, which is what ENC-03 asks | `DECISIONS.md` (2026-11-12); ENC-03 |
| K9 the sensor and home plugs stand 3.4 mm from the south edge, behind the motor | KLEIN | Covered: they are plugged before the board goes in, and the board comes out with its cables | `ASSEMBLY.md`, mounting steps 2 and 3 |

The reviewer's four notes for firmware (DIAG0 push-pull, the console off UART0 because of `HOME4`, SPI mode 3 at
10 MHz at most, the TMC2209's one-wire UART) were known: they are in `firmware/include/pins.h` and bring-up 7.3
and 7.8. His guess of five Extended lines is the one of both earlier reviews: JLC's API gives three
(`sourcing/jlc_check.md`), and the order page shows it.
