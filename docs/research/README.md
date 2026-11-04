# Research phase

The owner and Claude work through these questions together before the hardware is fixed. Each ends in an entry in
`DECISIONS.md` and a change to `specs/PRD.md`. No schematic work starts before they are closed.

**Confidence tags:** `[zeker]` = from the JLC parts search on 2026-11-04 or a calculation shown here.
`[bron]` = from a secondary source listed at the bottom; check against the datasheet. `[geheugen]` = from Claude's
memory, no source yet; treat as a question. The Analog Devices site and LCSC datasheet links did not load in this round, so
**no driver claim below has been checked against a datasheet yet.**

| Id | Question | Who first | Status |
| --- | --- | --- | --- |
| R-01 | What must the head do, in numbers? | Owner | open |
| R-02 | Which motor technology? | Claude + bench test | first round |
| R-03 | Which driver, and where does motion happen? | Claude + datasheets | first round |
| R-04 | Which MCU? | Claude | first round, depends on R-03 |
| R-05 | Which position sensor, over which bus? | Claude + bench test | first round |
| R-06 | How small can the board get? | Claude + 3D design | first round |
| R-07 | Which supply voltage? | Claude, after R-01 | open |

## R-01 — What must the head do, in numbers?

Every other question leans on this one. Needed from the owner: camera and lens (mass, zoom range), which axes really need a
motor (a camera with LANC or IP zoom needs no zoom motor), slowest and fastest move, what counts as too loud, and how exactly a
preset must land.

Why slowest speed and landing matter: at a narrow field of view of 3° on 1080p, one pixel is about 0.0016° (3 / 1920) `[zeker]`.
That sets what "smooth" and "exact" mean, far beyond what the old brief assumed.

## R-02 — Which motor technology?

| | Stepper with reduction | Brushless with FOC |
| --- | --- | --- |
| Holding still | Holds with current, no control loop `[geheugen]` | Needs a running control loop and encoder `[bron]` |
| Smoothness | Depends on driver and reduction; low speed is the known weak point `[bron]` | Lower torque ripple and quieter `[bron]` |
| On the board | One driver IC per axis | Three-phase stage, fast encoder and a real-time loop per axis, four times over `[geheugen]` |
| Tuning | Almost none | Per axis `[bron]` |

The search found **no measured comparison** of the two in a camera head, so this is reasoning, not evidence.

**Leading candidate: stepper with belt reduction.** It keeps the board small and simple, which is the owner's goal.
**What would overturn it:** bench test T-1 below shows jitter we cannot accept.

## R-03 — Which driver, and where does motion happen?

| | TMC2209 | TMC2240 | TMC5240 |
| --- | --- | --- | --- |
| Motion | MCU makes step pulses | MCU makes step pulses | **Ramp generator in the chip**, position and velocity modes `[bron]` |
| Bus | UART `[bron]` | SPI or UART, plus step/dir `[bron]` | SPI `[bron]` |
| Voltage | 29 V max `[bron]` | 36 V `[bron]` | 36 V `[bron]` |
| Current | 2 A RMS `[bron]` | 2 A RMS+ `[bron]` | 2 A RMS `[bron]` |
| Sense resistors | External, 2 per driver `[geheugen]` | Internal `[geheugen]` | Internal `[geheugen]` |
| Encoder and home inputs | None | None `[geheugen]` | ABN encoder `[bron]`; home inputs that stop the motor in the chip `[geheugen]` |
| Package | QFN-28, 5×5 `[zeker]` | TQFN-32, 5×5 `[zeker]` | TQFN-32, 5×5 `[zeker]` |
| JLC stock, price | 22,495, $2.83 `[zeker]` | 4,150, $7.52 `[zeker]` | 3,348, $7.24 `[zeker]` |
| Four on a board | $11.32 | $30.08 | $28.96 `[zeker]` |

Left out: TMC5160 needs eight external MOSFETs, which works against a small board `[geheugen]`. TMC5272 is a two-axis chip
on one small die, but JLC has 1 in stock `[zeker]`.

**Leading candidate: TMC5240**, for three reasons:
1. **Fewer pins and parts.** Eight STEP/DIR pins and the driver UART become one SPI bus with four chip selects. Home inputs land on
   the driver, not the MCU. That probably removes the I/O expander (R-04).
2. **Safer.** A home input that stops the motor in the chip works even when firmware hangs `[geheugen]`.
3. **Simpler firmware.** The chip runs the ramp, so WiFi load cannot touch step timing, and velocity mode suits a joystick.

Costs: about $18 more per board, which matters little for one head. Fewer open-source examples than the TMC2209 `[geheugen]`.

**Check first, these can overturn it:**
- Can a TMC5240 drive an **external driver** (DRV-06), or does that port need other wiring? If not, the "alles kan" port costs extra pins.
- Is its low-speed smoothness the same as the TMC2209 at equal microstepping? Same chopper family, but unverified.
- Do internal sensing and thermal limits really allow the current our motors need, on a small board?

## R-04 — Which MCU?

| | ESP32-S3-MINI-1U | ESP32-S3-WROOM-1U-N16R8 | ESP32 WROOM-32E | ESP32-C6-MINI-1 |
| --- | --- | --- | --- | --- |
| JLC stock, price | 2,172, $4.77 (N8) `[zeker]` | 33,286, $5.19 `[zeker]` | 27,915, $5.10 `[zeker]` | 3,366, $4.10 `[zeker]` |
| Size | 15.4×15.4 mm `[zeker]` | 19.2×18 mm `[zeker]` | 25.5×18 mm `[zeker]` | 16.6×13.2 mm (H4 listing) `[zeker]` |
| USB without converter | Yes `[geheugen]` | Yes `[geheugen]` | No `[geheugen]` | Yes `[geheugen]` |
| Enough pins | More than the WROOM, no octal PSRAM in the way `[geheugen]` | About 33 | To check | Probably not `[geheugen]` |

Outside the ESP32 family: STM32 parts have almost no JLC stock (STM32G474RET6: 19) `[zeker]`, and an RP2350 ($1.30) `[zeker]` needs a
separate radio. Both add a chip and lose the radio-on-board simplicity.

**Leading candidate: ESP32-S3-MINI-1U-N8**, with an external antenna: smaller than the WROOM and probably more pins. The firmware has no clear need for PSRAM `[geheugen]`.
Pin budget with TMC5240, without RS-232, expander or UART0 logs: **about 32, or about 35 if the sensors get their own SPI bus**, which a long cable argues for. This is a sum; the module's real pin count is still to check.
The C6-MINI-1U ($4.20, 13.2×12.5 mm, 3,869 in stock `[zeker]`) is smaller still, but only an option if ports drop.

## R-05 — Which position sensor, over which bus?

| | AS5600 | AS5047P | MT6701 | TLE5012B |
| --- | --- | --- | --- | --- |
| Bus | I2C `[bron]` | SPI `[bron]` | I2C or SSI `[geheugen]` | Synchronous serial `[geheugen]` |
| Resolution | 12 bit `[bron]` | 14 bit `[bron]` | 14 bit `[geheugen]` | 15 bit `[geheugen]` |
| Accuracy (INL max) | ±1° `[bron]` | ±1° `[bron]` | To check | To check |
| JLC stock, price | 401, $1.71 `[zeker]` | 5,054, $6.05 `[zeker]` | 1,219, $2.03 (QFN) `[zeker]` | 20,449, $3.56 `[zeker]` |

**Two findings that change the question:**
1. **±1° is about 640 pixels at 3° field of view**, a third of the frame (1 / 0.0016) `[zeker]`. No cheap sensor gives "exact" on its own, and it does not have to:
   the sensor says roughly where the head is at boot, the motor's step count does the fine work, and presets lean on repeatability rather than absolute
   accuracy. So the number to find is **repeatability and noise**, which the search did not give.
2. **SPI may remove the mux.** One shared bus with a chip select per sensor needs no TCA9548A and cuts wires: 5 shared plus 3 chip selects is 8 through the shaft
   for tilt, zoom and focus, against 12 for separate I2C. SPI's driven lines should also cope better with a long cable than open-drain I2C `[geheugen]`; T-2 tests that.

**Leading candidate: an SPI sensor.** Which one follows from repeatability data and T-2.

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

**The limit is probably heat, not parts.** Four drivers at 1 A or more in 50×50 mm need a way out: the base design has to take heat from the board, for example through a metal plate.
That is the first thing the board and the 3D design must decide together, and R-07 and the current per axis feed into it.

Options to explore with the 3D design: smaller connectors, parts on both sides (at the cost of the bottom-side CPL risk from the scoreboard), a ring-shaped board around the pan shaft, and a remote node (IDEA-02) that
moves heat and wires out of the base.

## R-07 — Which supply voltage?

24 V gives more torque at speed; 12 V is simpler and easier to power. With a reduction, the motors may never turn fast enough for the difference to matter, so R-01 decides it. With a 36 V driver, 24 V has real margin; with the
TMC2209's 29 V it has little.

## Bench tests (owner)

- **T-1 Smoothness baseline.** Old head with TMC2209, camera fully zoomed in: record the slowest clean pan. What is visible, at what speed? Answers R-02 and sets a target for R-03. Needs the old head to still run.
- **T-2 Sensor cable.** A sensor on the longest cable next to a running stepper, I2C against SPI: count read errors. Answers R-05.

## Sources

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
