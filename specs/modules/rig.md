# Module spec: test rig (RIG)

Status: **draft, waiting for owner approval (gate 1).** Built by R-TR, run by R-T1 and R-T2.

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

## Parts

Prices are first-tier, ex shipping, and checked on 2026-11-04 where marked. To be rechecked when ordering.

| Part | Qty | About | Source |
| --- | --- | --- | --- |
| TMC5240-BOB breakout | 1 | €23 ex VAT | DigiKey listing, undated |
| Motor 17HE08-1004S, 17 Ncm, 23 mm, for 30:1 | 1 | €4 | StepperOnline, checked |
| Motor 17HE12-1204S, 26 Ncm, for 9:1, where the 17 Ncm has too little reserve | 1 | €4 | StepperOnline, checked |
| AS5047P-TS_EK_AB adapter board, with D6×2.5 magnet | 1 | €15 ex VAT | DigiKey and RS listings, undated |
| AS5600 breakout with magnet | 1 | €3 | Estimate |
| GT2 pulley, 16T, 5 mm bore | 2 | €4 | Estimate |
| GT2 pulley, 16T, 8 mm bore, for the middle shaft | 1 | €2 | Estimate |
| GT2 closed belts, 6 mm wide, lengths from CAD | 3 | €9 | Estimate |
| Bearings: 2× 6806-2RS, 2× 608 | 4 | €12 | Estimate |
| 8 mm steel shaft, 100 mm | 1 | €3 | Estimate |

**About €80, plus shipping, VAT and filament.** Motors from the EU warehouse cost about €2 more each.

**The owner already has, to confirm:** an ESP32 dev board, a lab supply reaching 24 V, the camera and lens, a Bambu printer, M3 inserts and bolts, and a 1/4" camera bolt.
Printed: frame, 80T, 96T and 144T pulleys, motor plates, magnet holder, sensor bracket, camera plate.

## Out of scope

Tilt, zoom and focus. WiFi, OSC or any control source. Reprogramming the microstep table: a later refinement if R-T1 asks for it. Any design decision for the real head, except through its evidence.
