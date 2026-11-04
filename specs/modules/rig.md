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
| 12 or 24 V, 9:1 or 12.5:1, and which motor: which is quieter and cleaner? | R-T1, compared side by side | R-07, R-08 |
| Does a sensor survive a long cable next to a motor? | R-T2, read errors | ENC-04 |
| How repeatable is a sensor at standstill? | R-T2, logged noise | Input for R-05 |

## Acceptance criteria

### Mechanics
- **RIG-01** A printed frame holds a vertical output shaft on two 6806-2RS bearings, with the camera on top, at the axis, and stands on a tripod or is bolted to a bench.
- **RIG-02** Two drive set-ups fit one frame without reprinting it, both a single belt stage: 9:1 (16T to 144T) and 12.5:1 (16T to 200T). One motor slot serves both, and it sets the belt tension.
- **RIG-03** A diametric magnet sits on the output axis centre in a printed holder, with no steel within 5 mm, and the sensor on a bracket above it with an adjustable gap.
- **RIG-04** The output turns at least ±170°, and the camera's own cables do not snag. A printed stop limits the range, so a software error cannot wind up a cable.

### Electronics
- **RIG-05** A TMC5240-BOB on SPI to an ESP32 dev board drives one motor, wired on a breadboard or with loose wires, from the owner's lab supply. Pinout and wiring are drawn in `tests/hardware/rig-wiring.md`.
- **RIG-06** The first power-up follows a current-limited checklist, with the motor disconnected first.
- **RIG-07** The AS5047P (SPI) and AS5600 (I2C) can both be read from the same firmware, by cables of 15, 30 and 60 cm, tied to the motor wires over that length.

### Firmware
Kept in `firmware/rig/`, separate from the final firmware. Written against this spec, not a start of the final design.

- **RIG-08** From serial, set at runtime: velocity in °/s, target position in °, run current, hold current, chopper mode, microsteps setting and reduction.
- **RIG-09** Conversion from output °/s to TMC5240 velocity units is pure code with a host test: at 12.5:1 and 256 microsteps, 0.08°/s is 142.2 microsteps/s and 60°/s is 106,667 microsteps/s, and the units follow datasheet p50.
- **RIG-10** A preset move always lands from the same side, with the overshoot distance configurable (FW-11).
- **RIG-11** Motion stops by itself: on a stop key, when the host goes silent for 2 s during a jog, and on any driver fault flag. Position limits are enforced in the driver's own limits or the ramp target, not only in the host script.
- **RIG-12** Logs a CSV over serial with time, commanded position, driver position, sensor angle, sensor read errors and driver status, and a host script saves it per run.

## Geometry

Belts and centres from `mechanica/belts.py`. A single stage is the owner's decision (2026-11-04): no double belt.

| Set-up | Pulleys | Belt | Centres | Teeth in mesh on the 16T |
| --- | --- | --- | --- | --- |
| 9:1 | 16T to 144T | 400 mm | 112.6 mm | 6.2 |
| 12.5:1 | 16T to 200T | 500 mm | 128.7 mm | 5.7, a little under the usual 6; a 550 mm belt reaches 6 but no longer fits the printer's bed |

**Layout, top view:** the output shaft is the origin. The motor sits on the line x = 0, in one slot from y = -108.6 to y = -132.7. The bottom plate is 136 × 233 mm, which fits the printer's 256 mm bed.

**Stack, from the top:** camera plate on the output flange; bearing housing with two 6806-2RS on a top plate; the belt plane at z = 13 with the pulley; a bottom plate with the motor in a pocket underneath it; the magnet on the end of the output shaft, with the sensor tray below it. Two plates on four pillars, on four feet.

**The pulley on the output** is carried by a hexagon on the shaft, held in a stack by the magnet holder and three M3 bolts into the shaft end.

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
| `pulley_144T`, `pulley_200T` | 1 each | Flange down, 0.12 mm layers |

**Before printing the lot:**
1. **Print the 144T first and try it on a belt.** The tooth shape is simplified and untested; `GROOVE_W` and `GROOVE_D` in the script adjust it.
2. **Check the bearing and hexagon fits** on that same print and on the housing; `BEARING_FIT` and `HEX_FIT` adjust them.
3. **Wait with `sensor_tray`** until the sensor boards are in: the tray is a placeholder until the boards are measured.
4. **Check the 16T pulley on arrival.** Its height and hub are estimated, and they set the belt plane.

**Also needed:** 29 M3 heat-set inserts and M3 bolts. Stainless bolts near the magnet.

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
| GT2 closed belts, 6 mm wide: 400 and 500 mm | 2 | €6 | Estimate |
| Bearings: 2× 6806-2RS | 2 | €8 | Estimate |

**About €75, plus shipping, VAT and filament.** Both motors go on the rig to compare noise: at 9:1 the worst-case tilt needs about 0.18 Nm, which the final head may need the 42 Ncm for.

**The owner already has, to confirm:** an ESP32 dev board, a lab supply reaching 24 V, the camera and lens, a Bambu printer, M3 inserts and bolts, and a 1/4" camera bolt.
Printed: see Printing.

## Out of scope

Tilt, zoom and focus. WiFi, OSC or any control source. Reprogramming the microstep table: a later refinement if R-T1 asks for it. Any design decision for the real head, except through its evidence.
