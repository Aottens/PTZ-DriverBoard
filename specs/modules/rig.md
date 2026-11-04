# Module spec: test rig (RIG)

Status: **approved by the owner (2026-11-04).** Built by R-TR, run by R-T1 and R-T2.

One real pan axis, carrying the real camera, before any board exists. It exists to answer questions, so it stays a test tool:
it is allowed to be ugly, and nothing here is a design for the final head. It answers R-02 (motor), R-03 (driver), R-05 (sensor),
R-07 (voltage) and R-08 (reduction) in `docs/research/README.md`.

## What it answers

| Question | Measured by | Target |
| --- | --- | --- |
| Is the slowest move clean on screen? | R-T1, video | TGT-02 |
| Is the fastest move quiet? | R-T1, by ear and phone meter | TGT-03, TGT-04 |
| Does the head wobble after a stop? | R-T1, video | Owner's judgement, then a number |
| Does a preset land the same every time? | R-T1, video and logged position | TGT-05 |
| 12 or 24 V, 6.25:1 without idlers or 7.5:1 with, and which motor: which is quieter and cleaner? | R-T1, compared side by side | R-07, R-08 |
| Does a sensor survive a long cable next to a motor? | R-T2, read errors | ENC-04 |
| How repeatable is a sensor at standstill? | R-T2, logged noise | Input for R-05 |

## Acceptance criteria

### Mechanics
- **RIG-01** A printed frame holds a vertical output shaft on two 6806-2RS bearings, with the camera on top, at the axis, and stands on a tripod or is bolted to a bench.
- **RIG-02** Two drive set-ups fit one frame without reprinting it, each a single belt stage within the head's real base limit of Ø165 mm: 6.25:1 without idlers (16T to 100T) and 7.5:1 with two idlers (16T to 120T). The motor sits under the pulley, as in the real head, and one slot serves both and sets the belt tension.
- **RIG-03** A diametric magnet sits on the output axis centre in a printed holder, with no steel within 5 mm, and the sensor on a bracket above it with an adjustable gap.
- **RIG-04** The output turns at least ±170°, and the camera's own cables do not snag. A printed stop limits the range, so a software error cannot wind up a cable.

### Electronics
- **RIG-05** A TMC5240-BOB on SPI to an ESP32 dev board drives one motor, wired on a breadboard or with loose wires, from the owner's lab supply. Pinout and wiring are drawn in `tests/hardware/rig-wiring.md`.
- **RIG-06** The first power-up follows a current-limited checklist, with the motor disconnected first.
- **RIG-07** The AS5047P (SPI) and AS5600 (I2C) can both be read from the same firmware, by cables of 15, 30 and 60 cm, tied to the motor wires over that length.

### Firmware
Kept in `firmware/rig/`, separate from the final firmware. Written against this spec, not a start of the final design.

- **RIG-08** From serial, set at runtime: velocity in °/s, target position in °, run current, hold current, chopper mode, microsteps setting and reduction.
- **RIG-09** Conversion from output °/s to TMC5240 velocity units is pure code with a host test: at 7.5:1 and 256 microsteps, 0.08°/s is 85.3 microsteps/s and 60°/s is 64,000 microsteps/s, and the units follow datasheet p50.
- **RIG-10** A preset move always lands from the same side, with the overshoot distance configurable (FW-11).
- **RIG-11** Motion stops by itself: on a stop key, when the host goes silent for 2 s during a jog, and on any driver fault flag. Position limits are enforced in the driver's own limits or the ramp target, not only in the host script.
- **RIG-12** Logs a CSV over serial with time, commanded position, driver position, sensor angle, sensor read errors and driver status, and a host script saves it per run.

## Geometry

Belts and centres from `mechanica/belts.py`. One belt stage (owner, 2026-11-04), and the base at most Ø165 mm (owner, 2026-11-04).

| Set-up | Pulleys | Belt | Centres | Teeth in mesh on the 16T | Base |
| --- | --- | --- | --- | --- | --- |
| 6.25:1 | 16T to 100T, no idlers | 240 mm | 55.6 mm | 5.5, under the usual 6 | Ø165 |
| 7.5:1 | 16T to 120T, two idlers at x = ±12.2, y = -48.6 | 270 mm | 55.7 mm | 6.9 | Ø165 |

The motor's distance sets the base: at 55.7 mm its corner reaches the Ø165 limit. 9:1 (144T) reaches it too, with no margin at all: 1 mm from the 16T and only 6.1 teeth at best, so it is left out.

**Layout, top view:** the output shaft is the origin, the motor is on the line x = 0 at y = -55.65, ±2 mm. The rig's plates are 136 × 156 and 136 × 136 mm: square, not round, since the rig has no need for a round base.

**Stack, from the top:** camera plate on the output flange; bearing housing with two 6806-2RS on a top plate; the belt plane at z = 13 with the pulley and the idlers; a bottom plate with the motor in a pocket underneath it; the magnet on the end of the output shaft, with the sensor tray below it, on four legs bolted to the bottom plate. Shims between legs and plate set the gap to the magnet. Two plates on four pillars, on four feet.

**The pulley on the output** is carried by a hexagon on the shaft, held in a stack by the magnet holder and three M3 bolts into the shaft end. It has no flange: the 16T and the idlers keep the belt in line.

**The idlers** are two F623 back to back on an M3 bolt per idler, from the top plate down through printed spacers, into the 3 mm under it. They come out for 6.25:1.

**Model:** `mechanica/rig/build_rig.py` builds everything in Fusion. Fit is checked there: no overlap in either set-up. Belts are not modelled, and bought parts other than the motor are drawn from estimated sizes (see Printing).

## Printing

STL files in `mechanica/rig/export/`, plus `rig.f3d`. Print orientation is the owner's call; below is the proposal.

| Part | Qty | Lay it |
| --- | --- | --- |
| `bottom_plate`, `top_plate` | 1 each | Flat |
| `pillar`, `foot` | 4 each | Standing |
| `bearing_housing` | 1 | Flange down |
| `output_shaft` | 1 | Flange down, 100 % infill |
| `camera_plate` | 1 | Slot side up |
| `magnet_holder`, `sensor_tray`, `spacer` | 1 each | Flat |
| `idler_spacer_top`, `idler_spacer_low` | 2 each | Standing |
| `pulley_100T`, `pulley_120T` | 1 each | Flat, 0.12 mm layers |

**Before printing the lot:**
1. **Print the 120T first and try it on a belt.** A 144T already printed for the tooth test is just as good for that. The tooth shape is simplified and untested; `GROOVE_W` and `GROOVE_D` in the script adjust it.
2. **Check the bearing and hexagon fits** on that same print and on the housing; `BEARING_FIT` and `HEX_FIT` adjust them.
3. **Wait with `sensor_tray`** until the sensor boards are in: the tray is a placeholder until the boards are measured.
4. **Check the 16T pulley on arrival.** Its height and hub are estimated, and they set the belt plane.

**Also needed:** 29 M3 heat-set inserts and M3 bolts, including two M3 × 30 for the idlers. Stainless bolts near the magnet.

## Parts

Prices are ex VAT and shipping. Checked in the shop on 2026-11-04 where marked; estimates are from memory. To be rechecked when ordering.

| Part | Qty | Price | Source |
| --- | --- | --- | --- |
| TMC5240-BOB breakout | 1 | €27.05 | DigiKey NL, 17 in stock, checked |
| AS5047P adapter board | 1 | €17.22 | DigiKey NL, 199 in stock, checked; being discontinued there |
| Motor 17HE12-1204S: 26 Ncm, 1.2 A, 2.5 Ω, 3.3 mH, 30 mm | 1 | €4.13 | StepperOnline, checked; €2.55 more from Germany |
| Motor 17HE15-1504S: 42 Ncm, 1.5 A, 2.3 Ω, 4 mH, 38 mm | 1 | €4.30 | StepperOnline, checked; €1.27 more from Germany |
| AS5600 breakout with magnet | 1 | €3 | Estimate |
| Diametric magnet, D6×2.5, in case the AS5047P board comes without | 1 | €2 | Estimate |
| GT2 pulley, 16T, 5 mm bore | 2 | €4 | Estimate |
| GT2 closed belts, 6 mm wide: 240 and 270 mm | 2 | €6 | Estimate; check that 270 mm is on sale, or the idlers move |
| Bearings: 2× 6806-2RS | 2 | €8 | Estimate |
| Idler bearings: F623 (3 × 10 × 4 mm, flange 11.5 mm) | 4 | €4 | Estimate |

**About €80, plus shipping, VAT and filament.** Both motors go on the rig to compare noise. Worst-case tilt at 7.5:1 needs about 0.22 Nm, so the 42 Ncm is the likely choice for the real tilt.

**The owner already has, to confirm:** an ESP32 dev board, a lab supply reaching 24 V, the camera and lens, a Bambu printer, M3 inserts and bolts, and a 1/4" camera bolt.
Printed: see Printing.

## Out of scope

Tilt, zoom and focus. WiFi, OSC or any control source. Reprogramming the microstep table: a later refinement if R-T1 asks for it. Any design decision for the real head, except through its evidence.
