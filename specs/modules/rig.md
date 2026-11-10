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
- **RIG-01** A printed frame holds a vertical output shaft on two 6806-2RS bearings, with the camera on top, at the axis, and stands on four feet, clamped to a bench by the edge of its bottom plate.
- **RIG-02** Two drive set-ups fit one frame without reprinting it, each a single belt stage within the head's real base limit of Ø165 mm: 6.25:1 without idlers (16T to 100T) and 7.5:1 with two idlers (16T to 120T). The motor sits under the pulley, as in the real head, and one slot serves both and sets the belt tension.
- **RIG-03** A diametric magnet sits on the output axis centre in a printed holder, with no steel within 5 mm, and the sensor on a tray below it, with shims to set the gap.
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

**Stack, from the top:** camera plate on the output flange; bearing housing with two 6806-2RS on a top plate; the belt plane at z = 13 with the pulley and the idlers; a bottom plate with the motor in a pocket underneath it; the magnet on the end of the output shaft, with the sensor tray below it, on four legs bolted to the bottom plate. Shims between legs and plate set the gap to the magnet.

**The end stop** is a rib on the housing and a tab on the shaft's flange: about ±171°. Two plates on four pillars, on four feet.

**The pulley on the output** is carried by a hexagon on the shaft, held in a stack by the magnet holder and three M3 bolts into the shaft end. It has no flange: the 16T and the idlers keep the belt in line.

**The idlers** are two F623 back to back, with a 0.5 mm shim between their inner rings, on an M3 bolt per idler: from the top plate down through printed spacers into a thin nut held in the lower spacer. They come out for 6.25:1.

**Model:** `mechanica/rig/build_rig.py` builds everything in Fusion. Fit is checked there: no overlap in either set-up. Printability is checked by `mechanica/rig/check_print.py`. Bolts and belts are not modelled, and bought parts other than the motor are drawn from estimated sizes (see Printing).

## Printing

STL files in `mechanica/rig/export/`, plus `rig.f3d`. The STL files lie as in the assembly, so four must be turned over in the slicer. No part needs support.

| Part | Qty | On the bed |
| --- | --- | --- |
| `fit_seat`, `fit_shaft` | 1 each | As exported: **print these first** |
| `pulley_120T`, `pulley_100T` | 1 each | As exported, 0.12 mm layers |
| `bottom_plate` | 1 | **Turn over:** top face on the bed, pockets up |
| `top_plate` | 1 | As exported |
| `pillar`, `foot` | 4 each | As exported, standing |
| `bearing_housing` | 1 | As exported, flange on the bed |
| `output_shaft` | 1 | **Turn over:** flange on the bed, 100 % infill |
| `camera_plate` | 1 | **Turn over:** top face on the bed, channel up |
| `magnet_holder` | 1 | **Turn over:** pockets up |
| `sensor_tray` | 1 | As exported; wait for the boards |
| `spacer` | 1 | As exported |
| `idler_spacer_top` | 2 | **Turn over:** small boss up |
| `idler_spacer_low` | 2 | As exported; a small part, so use a brim |

**Before printing the lot:**
1. **Print `pulley_120T` and try it on a belt.** A 144T already printed is just as good for that. The tooth land is 0.66 mm, one extrusion line. `GROOVE_W` and `GROOVE_D` adjust it.
2. **Print `fit_seat` and `fit_shaft`, and try them on a 6806 and the pulley.** The seat should take the bearing by hand or a light press, the round end should slide through the bearing, and the hexagon should slide into the pulley. `BEARING_FIT`, `SHAFT_D` and `HEX_FIT` adjust them.
3. **Wait with `sensor_tray`** until the boards are in: the tray is a placeholder, with no mounting for a board yet.
4. **Check the 16T pulley on arrival.** Its height, hub and flange are estimated. At the tightest belt setting its flange has about 0.5 mm to the idler.

## Assembly

Hardware: 27 M3 × 4 heat-set inserts (short ones: some holes are 5 mm deep). M3 bolts: 16 × 10, 4 × 12, 4 × 8 button head with washers, 3 × 8 button head in stainless, 2 × 30. Two thin M3 nuts (DIN 439). Two 0.5 mm M3 shims. Calculated from the model, not yet built.

1. Press all inserts. Try the pulley on the shaft after the shaft's three: the wall to the hexagon's flat is about 1.8 mm.
2. Press the lower bearing into the housing from below, the upper from the top. Bolt the housing to the top plate from below (M3 × 10).
3. Bolt the feet to the bottom plate (M3 × 10 from the top). Bolt the pillars to the top plate (M3 × 10 from the top).
4. Slide the shaft in from the top, with the tab away from the rib. Turn the assembly over.
5. Slide on the spacer, then the pulley with its belt looped on. Bolt on the magnet holder (M3 × 8). Tighten gently until the shaft has no axial play and still turns freely: these three bolts set the bearing load.
6. Turn it back and bolt the bottom plate to the pillars, from below (M3 × 10).
7. Set the 16T on the motor off the rig, hub up, with its lower edge 5.5 mm above the motor's face. Raise the motor from below, inside the belt loop. Fit its bolts with washers, with the motor forward. The inner two are reached through the top plate's holes; push the belt aside with the key if needed.
8. For 7.5:1, fit the idlers with the belt slack: bolt from the top through spacer, bearing, shim, bearing and lower spacer into the nut, with the parts outside the belt loop.
9. Pull the motor back by hand to tension the belt, and tighten.
10. Fit the tray with shims when its boards are in (M3 × 12).
11. **Bolt the camera to the plate first,** off the rig, with the head of the 1/4" bolt in the channel. A rubber pad stops it twisting. Then bolt the plate to the flange from below (M3 × 10), with a ball-end key between the housing and the flange. Turn the shaft to reach each bolt.

**Swapping the pulley:** take off the camera and tray, and the magnet holder's bolts. Lift the shaft 11 mm, holding the spacer. Lift the belt over the motor's shaft into the top plate's opening with the motor loosened, and take the pulley out sideways. Reverse, with the idlers fitted or removed.

**Clamping:** clamp the bottom plate's rear edge to a bench. Lenses over about 66 mm in diameter hit the camera plate's end, so check it before fitting one.

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
| M3 × 4 inserts, bolts, thin nuts and shims: see Assembly | | | Check what you have |

**About €80, plus shipping, VAT and filament.** Both motors go on the rig to compare noise. Worst-case tilt at 7.5:1 needs about 0.22 Nm, so the 42 Ncm is the likely choice for the real tilt.

**The owner already has, to confirm:** an ESP32 dev board, a lab supply reaching 24 V, the camera and lens, a Bambu printer, a 1/4" camera bolt, and a ball-end hex key.
Printed: see Printing.

## Out of scope

Tilt, zoom and focus. WiFi, OSC or any control source. Reprogramming the microstep table: a later refinement if R-T1 asks for it. Any design decision for the real head, except through its evidence.
