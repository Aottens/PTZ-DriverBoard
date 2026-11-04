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
| 12 or 24 V, 9:1 or 30:1: which is quieter and cleaner? | R-T1, compared side by side | R-07, R-08 |
| Does a sensor survive a long cable next to a motor? | R-T2, read errors | ENC-04 |
| How repeatable is a sensor at standstill? | R-T2, logged noise | Input for R-05 |

## Acceptance criteria

### Mechanics
- **RIG-01** A printed frame holds a vertical output shaft on two 6806-2RS bearings, with the camera on top, at the axis, and stands on a tripod or is bolted to a bench.
- **RIG-02** Two drive set-ups fit one frame without reprinting it: 30:1 in two belt stages (16T to 80T, then 16T to 96T) and 9:1 in one stage (16T to 144T). Each belt's tension is adjustable by slotted holes.
- **RIG-03** A diametric magnet sits on the output axis centre in a printed holder, with no steel within 5 mm, and the sensor on a bracket above it with an adjustable gap.
- **RIG-04** The output turns at least ±170°, and the camera's own cables do not snag. A printed stop limits the range, so a software error cannot wind up a cable.

### Electronics
- **RIG-05** A TMC5240-BOB on SPI to an ESP32 dev board drives one motor, wired on a breadboard or with loose wires, from the owner's lab supply. Pinout and wiring are drawn in `tests/hardware/rig-wiring.md`.
- **RIG-06** The first power-up follows a current-limited checklist, with the motor disconnected first.
- **RIG-07** The AS5047P (SPI) and AS5600 (I2C) can both be read from the same firmware, by cables of 15, 30 and 60 cm, tied to the motor wires over that length.

### Firmware
Kept in `firmware/rig/`, separate from the final firmware. Written against this spec, not a start of the final design.

- **RIG-08** From serial, set at runtime: velocity in °/s, target position in °, run current, hold current, chopper mode, microsteps setting and reduction.
- **RIG-09** Conversion from output °/s to TMC5240 velocity units is pure code with a host test: at 30:1 and 256 microsteps, 0.08°/s is 341 microsteps/s and 60°/s is 256,000 microsteps/s, and the units follow datasheet p50.
- **RIG-10** A preset move always lands from the same side, with the overshoot distance configurable (FW-11).
- **RIG-11** Motion stops by itself: on a stop key, when the host goes silent for 2 s during a jog, and on any driver fault flag. Position limits are enforced in the driver's own limits or the ramp target, not only in the host script.
- **RIG-12** Logs a CSV over serial with time, commanded position, driver position, sensor angle, sensor read errors and driver status, and a host script saves it per run.

## Geometry

Belts and centres from `mechanica/belts.py`, which checks at least 6 teeth in mesh on each small pulley. The output shaft is the origin.

| Belt | Pulleys | Length | Centres |
| --- | --- | --- | --- |
| A, motor to middle shaft | 16T to 80T | 240 mm | 69.0 mm |
| B, middle shaft to output | 16T to 96T | 280 mm | 79.9 mm |
| 9:1, motor to output | 16T to 144T | 400 mm | 112.6 mm |

**Layout, top view:** middle shaft at x = -79.9; 30:1 motor at x = -79.9, y = -69; 9:1 motor at x = +112.6. Everything falls within about 240 × 140 mm, which fits the printer's 256 mm bed.

**Stack, from the top:** camera plate on the output flange; bearing housing with two 6806-2RS on a top plate; belt plane B with the 96T; belt plane A with the 144T, for the 9:1 set-up only; a bottom plate carrying the motors underneath it; the magnet on the end of the output shaft, with the sensor bracket below it. Two plates on four pillars, each printed flat.

**Tension:** the middle shaft's bearing holders slide in slots along x for belt B. Then each motor slides in slots along its own belt. 8 mm of travel.

## Parts

Prices are ex VAT and shipping. Checked in the shop on 2026-11-04 where marked; estimates are from memory. To be rechecked when ordering.

| Part | Qty | Price | Source |
| --- | --- | --- | --- |
| TMC5240-BOB breakout | 1 | €27.05 | DigiKey NL, 17 in stock, checked |
| AS5047P adapter board | 1 | €17.22 | DigiKey NL, 199 in stock, checked; being discontinued there |
| Motor 17HE08-1004S: 17 Ncm, 1 A, 3.6 Ω, 4 mH, 23 mm, for 30:1 | 1 | €4.03 | StepperOnline, checked; €2.20 more from Germany |
| Motor 17HE12-1204S: 26 Ncm, 1.2 A, 2.5 Ω, 3.3 mH, 30 mm, for 9:1 | 1 | €4.13 | StepperOnline, checked; €2.55 more from Germany |
| AS5600 breakout with magnet | 1 | €3 | Estimate |
| Diametric magnet, D6×2.5, in case the AS5047P board comes without | 1 | €2 | Estimate |
| GT2 pulley, 16T, 5 mm bore | 2 | €4 | Estimate |
| GT2 pulley, 16T, 8 mm bore, for the middle shaft | 1 | €2 | Estimate |
| GT2 closed belts, 6 mm wide: 240, 280 and 400 mm | 3 | €9 | Estimate |
| Bearings: 2× 6806-2RS, 2× 608 | 4 | €12 | Estimate |
| 8 mm steel shaft, 100 mm | 1 | €3 | Estimate |

**About €90, plus shipping, VAT and filament.** The 17HE12 needs 10 V at 300 rpm by the same calculation as R-07.

**The owner already has, to confirm:** an ESP32 dev board, a lab supply reaching 24 V, the camera and lens, a Bambu printer, M3 inserts and bolts, and a 1/4" camera bolt.
Printed: plates, pillars, output shaft and flange, 80T, 96T and 144T pulleys, motor brackets, magnet holder, sensor bracket, camera plate.

## Out of scope

Tilt, zoom and focus. WiFi, OSC or any control source. Reprogramming the microstep table: a later refinement if R-T1 asks for it. Any design decision for the real head, except through its evidence.
