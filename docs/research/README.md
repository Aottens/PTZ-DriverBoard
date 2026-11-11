# Research phase

The owner and Claude work through these questions together before the hardware is fixed. Each ends in an entry in
`DECISIONS.md` and a change to `specs/PRD.md`. No schematic work starts before they are closed, except the one-run board builds (Rev A, Rev B; `DECISIONS.md`), which use the choices in `specs/PRD.md`.

**Confidence tags:** `[datasheet]` = read in the manufacturer's datasheet, page given. `[zeker]` = from the JLC parts search on
2026-11-04 or a calculation shown here. `[bron]` = from a secondary source listed at the bottom. `[geheugen]` = from Claude's memory, no
source yet; treat as a question.

| Id | Question | Who first | Status |
| --- | --- | --- | --- |
| R-01 | What must the head do, in numbers? | Owner | closed: targets approved 2026-11-04 |
| R-02 | Which motor technology? | Claude + test rig | leading candidate |
| R-03 | Which driver, and where does motion happen? | Claude + test rig | Rev B: plug-in StepStick modules, TMC2240 default, steps from the MCU (owner, 2026-11-11); rig left |
| R-04 | Which MCU? | Claude | Rev B: plug-in ESP32-S3-DevKitC-1U (owner, 2026-11-11); the C6 drives only two steppers from hardware |
| R-05 | Which position sensor, over which bus? | Claude + test rig | Rev B: AS5600 or MT6701 on I2C behind a multiplexer (owner, 2026-11-11); cable test R-T2 left |
| R-06 | How small can the board get? | Claude + 3D design | first round |
| R-07 | Which supply voltage? | Claude + test rig | 11 to 17 V: 12 V supply or D-Tap (owner, 2026-11-11) |
| R-08 | Which reduction? | Claude + test rig | one belt stage in Ø165 (owner), 6.25:1 or 7.5:1 on the rig |

## R-01 — What must the head do, in numbers?

**From the owner (2026-11-04):** usually a DSLR or mirrorless, 1.5 to 2 kg at most. The camera has no LANC or IP zoom, so a zoom motor is
needed. Used in theatres among the audience, so fairly quiet. As exact as possible within DIY means. Speeds not known yet. The old head stays out of it.

**Targets, approved by the owner on 2026-11-04.** Taken from a professional head: the Panasonic AW-UE150 runs from 0.08°/s up, and is rated NC35 or less up to 60°/s, its normal mode `[bron]`.

| Id | Target | Value |
| --- | --- | --- |
| TGT-01 | Payload, including plate | 2.5 kg |
| TGT-02 | Slowest clean pan and tilt | 0.08°/s |
| TGT-03 | Fastest quiet pan and tilt | 60°/s |
| TGT-04 | Noise while moving | No louder than NC35 up to 60°/s. Slow moves inaudible at 2 m in a quiet room, judged by the owner |
| TGT-05 | Preset landing, always from the same side | Within about 0.005° |

**First camera:** a Panasonic G7 with a 14-140 mm, Micro Four Thirds (owner, 2026-11-04). Lens 265 g `[bron]`; the older F4.0-5.8 version is 460 g `[bron]`, so check which one it is. With the body it stays well under the 2 kg payload, which remains the design limit. Keep the lens stabiliser off on the head `[geheugen]`.

**What a pixel is worth** (horizontal field of view, `[zeker]`). The G7 at 140 mm is the reference from here on:

| Lens | Field of view | Pixel at 1080p | Pixel at 4K |
| --- | --- | --- | --- |
| G7 at 14 mm | 63.4° | 0.033° | 0.017° |
| **G7 at 140 mm** | **7.1°** | **0.0037°** | **0.0018°** |
| 200 mm on full frame | 10.3° | 0.0054° | 0.0027° |
| 600 mm on full frame | 3.4° | 0.0018° | 0.0009° |

At 140 mm, TGT-05 is about 3 pixels at 4K and 1.4 at 1080p. The G7 may crop further in 4K `[geheugen]`, which would make a pixel slightly smaller.

## R-02 — Which motor technology?

| | Stepper with reduction | Brushless with FOC |
| --- | --- | --- |
| Holding still | Holds with current, no control loop `[geheugen]` | Needs a running control loop and encoder `[bron]` |
| Smoothness | Depends on driver and reduction; low speed is the known weak point `[bron]` | Lower torque ripple and quieter `[bron]` |
| On the board | One driver IC per axis | Three-phase stage, fast encoder and a real-time loop per axis, four times over `[geheugen]` |
| Tuning | Almost none | Per axis `[bron]` |

The search found **no measured comparison** of the two in a camera head, so this is reasoning, not evidence.

**Leading candidate: stepper with belt reduction.** It keeps the board small and simple, which is the owner's goal, and the TMC5240 is built for this: StealthChop2 is
specified as noiseless at standstill and low speed `[datasheet p29]`, and its microstep table can be reprogrammed per motor for smoother motion `[datasheet p74]`.
**What would overturn it:** the test rig (R-T1) shows noise or jitter we cannot accept.

## R-03 — Which driver, and where does motion happen?

| | TMC2209 | TMC2240 | TMC5240 |
| --- | --- | --- | --- |
| Motion | MCU makes step pulses | MCU makes step pulses | **Ramp generator in the chip**, position and velocity modes `[datasheet p1]` |
| Bus | UART `[bron]` | SPI or UART, plus step/dir `[bron]` | SPI `[bron]` |
| Voltage | 29 V max `[bron]` | 36 V `[bron]` | 36 V, 41 V absolute `[datasheet p10]` |
| Current | 2 A RMS `[bron]` | 2 A RMS+ `[bron]` | 2.1 A RMS `[datasheet p1]` |
| Sense resistors | External, 2 per driver `[geheugen]` | Internal `[geheugen]` | None `[datasheet p1]` |
| Encoder and home inputs | None | None `[geheugen]` | ABN encoder, home inputs that stop the motor in the chip `[datasheet p1, p58]` |
| Package | QFN-28, 5×5 `[zeker]` | TQFN-32, 5×5 `[zeker]` | TQFN-32, 5×5 `[zeker]` |
| JLC stock, price | 22,495, $2.83 `[zeker]` | 4,150, $7.52 `[zeker]` | 3,348, $7.24 `[zeker]` |
| Four on a board | $11.32 | $30.08 | $28.96 `[zeker]` |

Left out: TMC5160 needs eight external MOSFETs, which works against a small board `[geheugen]`. TMC5272 is a two-axis chip
on one small die, but JLC has 1 in stock `[zeker]`.

**Leading candidate: TMC5240**, now checked against its datasheet (19-101625C, Rev 1, 4/24):

| Claim | Result |
| --- | --- |
| **External driver port (DRV-06)** | **Yes.** DIAG0 and DIAG1 can output STEP and DIR from the internal ramp generator, for an external driver `[datasheet p17, p60-61]`. No extra pins |
| Home inputs stop the motor in the chip | **Yes.** REFL and REFR, hard or soft stop, and they latch the exact position `[datasheet p58]` |
| Supply | 4.5 to 36 V, absolute maximum **41 V** `[datasheet p1, p10]` |
| Current | 2.1 A RMS at 25 °C on four layers; real limit is thermal `[datasheet p1]` |
| No sense resistors | **Yes**, integrated current sensing `[datasheet p1]` |
| Reprogrammable microstep table | **Yes**, for smoother motion with a given motor `[datasheet p74]` |
| Encoder input | ABN, which is incremental, so it does not replace an absolute sensor `[datasheet p1, p77]` |
| Daisy chain on SPI | **Yes**; all commands take effect when CSN goes high `[datasheet p25]` |

**The daisy chain may be the best part.** One chip select for all four drivers, so **a preset move can start on all axes at the same instant**. That follows from the datasheet's description
and is still to prove on a real chain.

**Limits to design for:**
- Automatic StealthChop tuning has a lower current limit that rises with supply voltage, or set `pwm_meas_sd_enable` `[datasheet p33-34]`. To work out once the motors are chosen.
- Fewer open-source examples than the TMC2209 `[geheugen]`.

Costs: about $18 more per board than TMC2209, which matters little for one head.

**Heat, by calculation** `[zeker, with these assumptions]`. Losses in the bridges only, RDS(on) 0.23 Ω, two bridges per motor, so `2 × I² × 0.23`. θJA 29 °C/W is for a JEDEC four-layer board `[datasheet p10]`, larger than ours.

| Current per motor | Per driver | Junction rise |
| --- | --- | --- |
| 0.4 A | 0.07 W | 2 °C |
| 1.0 A | 0.46 W | 13 °C |
| 1.5 A | 1.04 W | 30 °C |

Far below the 125 °C operating limit `[datasheet p10]`. A 50×50 mm board in still air (10 W/m²K, both sides) rises about 37 °C with all four at 1 A, and these motors need that much only near their limit. **So the chip is not the limit; the
3D print is**: PETG softens around 80 °C and PLA well below that `[geheugen]`. Keep the board off the plastic.

## R-04 — Which MCU?

| | ESP32-S3-MINI-1U | ESP32-S3-WROOM-1U-N16R8 | ESP32 WROOM-32E | ESP32-C6-MINI-1 |
| --- | --- | --- | --- | --- |
| JLC stock, price | 2,172, $4.77 (N8) `[zeker]` | 33,286, $5.19 `[zeker]` | 27,915, $5.10 `[zeker]` | 3,366, $4.10 `[zeker]` |
| Size | 15.4×15.4 mm `[zeker]` | 19.2×18 mm `[zeker]` | 25.5×18 mm `[zeker]` | 16.6×13.2 mm (H4 listing) `[zeker]` |
| USB without converter | Yes `[geheugen]` | Yes `[geheugen]` | No `[geheugen]` | Yes `[geheugen]` |
| Enough pins | More than the WROOM, no octal PSRAM in the way `[geheugen]` | About 33 | To check | Probably not `[geheugen]` |

Outside the ESP32 family: STM32 parts have almost no JLC stock (STM32G474RET6: 19) `[zeker]`, and an RP2350 ($1.30) `[zeker]` needs a
separate radio. Both add a chip and lose the radio-on-board simplicity.

**Chosen for Rev A: ESP32-C6-MINI-1U-H4 (owner, 2026-11-10).** JLC's part pages, read that day, list the ESP32-S3-MINI-1U and WROOM-1U modules as "Standard Only", and the C6-MINI-1U as "Economic and Standard" `[zeker]`. The module has 22 GPIOs including USB, one core at 160 MHz, 4 MB flash and one user SPI bus `[datasheet v1.5]`. About 27 signals are needed, so it takes an I2C expander and a chip-select decoder `[zeker, as a sum]`. Whether one core is enough is untested; the TMC5240 generates the motion itself `[datasheet p1]`.

**Earlier leading candidate: ESP32-S3-MINI-1U-N8**, with an external antenna: smaller than the WROOM and probably more pins. The firmware has no clear need for PSRAM `[geheugen]`.
Pin budget with a TMC5240 chain and no RS-232, LANC or expander, with the fan output: **about 30** `[zeker, as a sum]`, which fits. The module's real pin count is still to check, and with it the strapping pins.
The C6-MINI-1U ($4.20, 13.2×12.5 mm, 3,869 in stock `[zeker]`) is smaller still and could become an option at 30 pins; its pin count is the first thing to check.

## R-05 — Which position sensor, over which bus?

| | AS5600 | AS5047P | MT6701 | TLE5012B |
| --- | --- | --- | --- | --- |
| Bus | I2C `[bron]` | SPI `[bron]` | I2C or SSI `[geheugen]` | Synchronous serial `[geheugen]` |
| Resolution | 12 bit `[bron]` | 14 bit `[bron]` | 14 bit `[geheugen]` | 15 bit `[geheugen]` |
| Accuracy (INL max) | ±1° `[bron]` | ±1° `[bron]` | To check | To check |
| JLC stock, price | 401, $1.71 `[zeker]` | 5,054, $6.05 `[zeker]` | 1,219, $2.03 (QFN) `[zeker]` | 20,449, $3.56 `[zeker]` |

**Two findings that change the question:**
1. **±1° is about 540 pixels on the G7 at 140 mm in 4K** (1 / 0.0018) `[zeker]`. No cheap sensor gives "exact" on its own, and it does not have to:
   the sensor says roughly where the head is at boot, the motor's step count does the fine work, and presets lean on repeatability rather than absolute
   accuracy. So the number to find is **repeatability and noise**, which the search did not give.
2. **SPI may remove the mux.** One shared bus with a chip select per sensor needs no TCA9548A and cuts wires: 5 shared plus 3 chip selects is 8 through the shaft
   for tilt, zoom and focus, against 12 for separate I2C. SPI's driven lines should also cope better with a long cable than open-drain I2C `[geheugen]`; R-T2 tests that.

**Leading candidate: an SPI sensor.** Which one follows from repeatability data and R-T2.

**Wire count (MEC-04) drops.** With an absolute sensor on each output axis, home switches are redundant. Motors 12 + sensors 8 = **20 wires**, against 33 in the first draft `[zeker]`.

## R-06 — How small can the board get?

A first estimate from rough block areas, not a layout `[geheugen]`:

| Block | mm² |
| --- | --- |
| MCU module | 240 |
| Four driver cells, about 12×12 each | 580 |
| Power (input protection, buck, inductor, bulk capacitors) | 375 |
| Connectors and ports | 400 |
| **Parts** | **about 1,600** |
| With routing and edges, times 1.5 | **about 2,400, so roughly 50×50 mm** |

**Heat looks manageable without a fan** (R-03), which is what a theatre needs. The optional fan output (AUX-03) is a reserve, not part of the plan. The limit is keeping warmth away from the plastic, and that is the first thing the board and the 3D design agree on.

Options to explore with the 3D design: smaller connectors, parts on both sides (at the cost of the bottom-side CPL risk from the scoreboard), a ring-shaped board around the pan shaft, and a remote node (IDEA-02) that
moves heat and wires out of the base.

## R-07 — Which supply voltage?

**Open.** The motor decides it. Voltage needed at full current, from `sqrt((I·R + E)² + (ω·L·I)²)` with StepperOnline's figures, at the 75 rpm that 7.5:1 needs for 60°/s `[zeker, as a calculation]`:

| Motor | Rated | R, L | Holding | Length | Volts needed | Price |
| --- | --- | --- | --- | --- | --- | --- |
| 17HS13-0404S1 (July design) | 0.4 A | 30 Ω, 37 mH | 26 Ncm | 34 mm | 16.7 V | €7.72 |
| 17HE12-1204S | 1.2 A | 2.5 Ω, 3.3 mH | 26 Ncm | 30 mm | 4.5 V | €4.13 |
| 17HE15-1504S | 1.5 A | 2.3 Ω, 4 mH | 42 Ncm | 38 mm | 5.5 V | €4.30 |

**The low-resistance motors run comfortably on 12 V**, and that might also be quieter: the lowest current StealthChop can tune rises with supply voltage `[datasheet p34]`. Nothing here measures the noise. **The rig tests both, and the board accepts 12 to 24 V either way.**

## R-08 — Which reduction?

**One belt stage, in a base of at most Ø165 mm: the owner's limits (2026-11-04).** The first draft here advised about 30:1 in two stages. That was too strong: it counted the stepper's absolute error, while a preset landing from the same side mostly repeats that error, so 30:1 is not needed for TGT-05. A later draft used a 200T and long belts, which fixed tooth grip but made the base far too big.

**What sets the base is the motor's distance from the axis.** The motor can sit under the pulley, so its corner is the limit: at Ø165, the centres are at most 55.7 mm. Tooth grip then needs idlers above a certain pulley size. They press on the belt's back between the pulley and the 16T, so a larger pulley leaves them less room, and that sets the top end.

On the G7 at 140 mm in 4K (one pixel 0.0018°), taking a stepper's full-step error as ±5 % of 1.8° `[geheugen]`, and 90 % efficiency `[geheugen]`:

| Reduction | Large pulley | Idlers | Teeth on the 16T | Wave in the picture, at most | One step at 0.08°/s | Motor at 60°/s | Worst-case tilt torque at the motor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 6.25:1 | 100T, Ø64 mm | no | 5.5 | ±7.8 pixels | 3.6 s | 62 rpm | 0.26 Nm |
| **7.5:1** | **120T, Ø76 mm** | **yes** | **6.9** | **±6.5 pixels** | **3.0 s** | **75 rpm** | **0.22 Nm** |
| 9:1 | 144T, Ø92 mm | yes, with no margin | 6.1 at best | ±5.4 pixels | 2.5 s | 90 rpm | 0.18 Nm |

**The rig compares 6.25:1 and 7.5:1:** do idlers cost more in noise than they gain in tooth grip and smoothness? A balanced G7 needs far less than this worst case.

**What can shrink the wave:** the TMC5240's reprogrammable microstep table `[datasheet p74]`. How much is for the rig to show. A capstan drive (IDEA-04) is the fallback if the wave stays too large: about 18:1 and ±2.7 pixels in the same Ø165 `[zeker, as a calculation; the drive itself is unresearched]`.

**The other half of exact is firmware:** always landing a preset from the same side takes out backlash and hysteresis, for no hardware at all (FW-11).

## Zoom axis

The G7's 14-140 mm zooms by a ring, so the zoom motor drives a gear on that ring. Its focus ring may be by-wire, with no end stops `[geheugen]`, so focus needs checking on the real lens. This is its own small design: how much torque the ring needs, how to mount it per lens, and how to home it.
A ring turning less than once allows an absolute sensor on a matching gear; otherwise soft stall homing against the ring's end `[datasheet p58]`. To do with the 3D design.

## Test rig

A one-axis rig answers R-02, R-03, R-05, R-07 and R-08 on real hardware before any board exists. Its spec, parts and tests are in `specs/modules/rig.md`.

## Sources

- [StepperOnline 17HE12-1204S](https://www.omc-stepperonline.com/e-series-nema-17-bipolar-26ncm-36-82oz-in-1-2a-42x42x30mm-4-wires-w-1m-cable-connector-17he12-1204s)
- [StepperOnline 17HE15-1504S](https://www.omc-stepperonline.com/e-series-nema-17-bipolar-42ncm-59-49oz-in-1-5a-42x42x38mm-4-wires-w-1m-cable-connector-17he15-1504s)
- [StepperOnline 17HS13-0404S1](https://www.omc-stepperonline.com/nema-17-bipolar-1-8deg-26ncm-36-8oz-in-0-4a-12v-42x42x34mm-4-wires-17hs13-0404s1)
- [Panasonic 14-140 mm II, DXOMARK](https://www.dxomark.com/Lenses/Panasonic/Panasonic-LUMIX-G-VARIO-14-140mm-F35-56-ASPH-POWER-OIS-mounted-on-Olympus-PEN-E-PL7---Specifications__972)
- [Panasonic 14-140 mm F4.0-5.8, PhotographyBlog](https://www.photographyblog.com/reviews/panasonic_lumix_g_vario_14_140mm_f4_58_asph_mega_ois_review/specifications)
- [TMC5240-BOB, DigiKey](https://www.digikey.nl/en/products/detail/analog-devices-inc-maxim-integrated/TMC5240-BOB/21292888)
- [AS5047P adapter board, DigiKey](https://www.digikey.at/en/products/detail/ams-osram-usa-inc/AS5047P-ADAPTERBOARD/5452344)
- [TMC5240 datasheet, Rev 1, Analog Devices](https://www.analog.com/media/en/technical-documentation/data-sheets/tmc5240.pdf)
- [Panasonic AW-UE150 specifications](https://latam.connect.panasonic.com/pa/en/download-specifications/134)
- [TMC5240-BOB, Analog Devices](https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/tmc5240-bob.html)
- [TMC5240-BOB and TMC2240-BOB, Mouser](https://www.mouser.se/adi-tmc2240-bob-tmc5240-bob-boards)

- [Analog Devices TMC5240 no-OS driver](https://analogdevicesinc.github.io/no-OS/drivers/motor/tmc5240.html)
- [TMC5240 evaluation board](https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/tmc5240-eval.html)
- [DigiKey: TMC5240 product highlight](https://www.digikey.co.uk/en/product-highlight/a/analog-devices/tmc5240-stepper-motor-controller-and-driver-ic)
- [Analog Devices TMC2240](https://analog.com/en/products/TMC2240.html)
- [Analog Devices TMC2209](https://analog.com/jp/products/TMC2209.html)
- [ams OSRAM position sensor overview](https://ams.com:443/documents/20143/4421878/Position_Sensors_FS001005_2-00.pdf/e30afae2-cbd2-ffc5-f00a-db4ff9fced8c)
- [Duet3D forum on StealthChop](https://forum.duet3d.com/post/176278)
- [DigiKey: surveillance-camera PTZ ICs](https://www.digikey.be/en/articles/how-to-design-for-a-safer-world-using-energy-efficient-surveillance-camera-ptz-ics)
- [Zbotic: gimbal motors and FOC](https://zbotic.in/gimbal-stabilizer-motor-how-brushless-motors-work-in-2-axis-gimbals/)
- [FastAccelStepper ESP32 notes](https://github.com/gin66/FastAccelStepper/blob/master/extras/doc/platforms/esp32.md)
