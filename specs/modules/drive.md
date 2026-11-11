# Module spec: motor drive (DRV), Rev B

Status: **written in the Rev B one-run build (2026-11-11); gate 1 is the owner's approval of `docs/prompts/fable-board-rev-b.md`.**
Grows out of DRV-01..06 in `specs/PRD.md`. Nets and references here are the contract that `hardware/check_netlist.py` checks.
Rev A's version of this file is under the git tag `rev-a`.

## What it does

Four sockets, one per axis, each for a driver module in StepStick format that the owner buys and plugs in. The board
gives each module its motor supply, 3.3 V for its logic, a motor connector, step and direction from the MCU, and a
place on the driver bus. Axis n = 1 pan, 2 tilt, 3 zoom, 4 focus; its references are in the hundreds a = n + 2
(axis 1 = 3xx … axis 4 = 6xx).

## The socket, and the modules it is drawn for

A StepStick is 15.24 × 20.32 mm with two rows of eight pins, 2.54 mm pitch, the rows 12.7 mm apart. Seen from the
top with the motor supply pin at the top right, the left row is L1 to L8 from the top and the right row R1 to R8.
The modules this board is drawn for carry two more pins in the top row, between L1 and R1: X1 one pitch from L1 and
X2 two pitches from L1.

| Socket pad | Position | BIGTREETECH TMC2240 V1.0 (default) | BIGTREETECH TMC2209 V1.3 | FYSETC TMC2209 V3.1 | Net on the board |
| --- | --- | --- | --- | --- | --- |
| 1 | L1 | EN | EN | EN | `DRV_ENN` |
| 2 | L2 | MOSI | MS1 | MS1 | `DRVn_SDI` |
| 3 | L3 | CLK (the SPI clock) | MS2 | MS2 | `DRVn_SCK` |
| 4 | L4 | CS | RX (PDN_UART) | TX (1 kΩ to PDN_UART) | `DRVn_CSP` |
| 5 | L5 | MISO | TX (not connected) | RX (PDN_UART) | `DRVn_SDO` |
| 6 | L6 | CLK (clock input, 10 kΩ to ground on the module) | CLK (20 kΩ to ground) | CLK (not connected) | not connected |
| 7 | L7 | STEP | STEP | STEP | `STEPn` |
| 8 | L8 | DIR | DIR | DIR | `DIRn` |
| 9 | R1 | VM | VM | VM | `VM` |
| 10 | R2 | GND | GND | GND | `GND` |
| 11 | R3 | B1 | A2 | A2 | `Mn_1` |
| 12 | R4 | B2 | A1 | A1 | `Mn_2` |
| 13 | R5 | A2 | B1 | B1 | `Mn_3` |
| 14 | R6 | A1 | B2 | B2 | `Mn_4` |
| 15 | R7 | VIO | VIO | VIO | `+3V3` |
| 16 | R8 | GND | GND | GND | `GND` |
| 17 | X1 | AIN | INDEX | INDEX | not connected |
| 18 | X2 | DIAG0 | DIAG | DIAG | `DIAGn` |

Sources, all in `hardware/datasheets/README.md`: BIGTREETECH's TMC2240 V1.0 manual (pin drawing p5, size drawing p4)
and schematic; BIGTREETECH's TMC2209 V1.3 schematic and size drawing; FYSETC's TMC2209 V3.1 schematic and readme;
TMC2240 datasheet Rev 2 (11/23); TMC2209 datasheet Rev 1.09. A FYSETC S2240 V2.0 has the same sixteen pins except
L6 (`TYPE`, 10 kΩ to VIO there) and its DIAG0 on a four-pad header whose order could not be read: it works in the
socket without its DIAG signal.

## Parts

| Ref | Part | LCSC | Fitted by |
| --- | --- | --- | --- |
| A301, A401, A501, A601 | Socket for the driver module: 2 × 1×8 and 1×2 female header, 2.54 mm | none | owner |
| J301, J401, J501, J601 | JST B4B-XH-A, 4 pins, 2.5 mm, top entry | none | owner |
| C301 … C601 | 100 nF 50 V 0603 | C14663 | JLC |
| C302 … C602 | 100 nF 50 V 0603 | C14663 | JLC |
| R301 … R601 | 1 kΩ 0603 | C21190 | JLC |
| D301 … D601 | B5819W Schottky, SOD-123 | C8598 | JLC |
| JP301 … JP303, and so on to JP601 … JP603 | Solder jumper, two pads, closed by a copper bridge; two nets in the netlist | none | bare copper |

## Acceptance criteria

- **DRV-01** Four sockets A301, A401, A501 and A601, wired per pad as in the table above. Pad 9 is `VM`, pads 10 and
  16 are `GND`, pad 15 is `+3V3`. Nothing else on the board is powered from a socket.
- **DRV-02 Driver bus.** The default module, a TMC2240, is on the SPI bus through three solder jumpers per socket,
  closed as delivered: JPa01 joins `DRVn_SDI` to `SPI_MOSI`, JPa02 joins `DRVn_SCK` to `SPI_SCK`, JPa03 joins
  `DRVn_SDO` to `SPI_MISO`. Each socket has its own select line from the MCU: `DRVn_CS` reaches `DRVn_CSP` through
  Ra01 (1 kΩ). For a TMC2209 module the owner cuts the three jumpers of that socket; its MS1 and MS2 are then pulled
  low inside the chip (UART address 0) and `DRVn_CS` is its one-wire UART line, with Ra01 as the series resistor the
  TMC2209 datasheet asks for (Rev 1.09, p20). TMC2240 and TMC2209 modules can be mixed.
- **DRV-03** No trimmer and no current-setting part is on the board: current, microsteps and chopper mode go over
  the driver bus (the modules carry their own reference resistor).
- **DRV-04 Enable.** `DRV_ENN` goes from the MCU to pad 1 of all four sockets and has R203 (10 kΩ) to `+3V3`, so
  the bridges are off while the MCU is in reset. High = off (TMC2240 datasheet p16, TMC2209 datasheet p9).
- **DRV-05 Stall and fault.** Pad 18 of each socket (`DIAGn`) goes through Da01 (anode at `DIAGn`) to the shared
  line `DIAG_OR`, which has R205 (10 kΩ) to `GND` and goes to the MCU. Firmware sets the TMC2240's DIAG0 to
  push-pull, active high (`diag0_pushpull`, datasheet p57); the TMC2209's DIAG is active high as it comes (p9). A
  TMC2240 that has not been configured holds DIAG0 low, which the diode blocks. Firmware finds the axis over the
  driver bus. *(PRD DRV-04, proposal: one shared line.)*
- **DRV-06 Step and direction.** `STEPn` and `DIRn` go straight from the MCU to pads 7 and 8.
- **DRV-07 Motor connector.** Ja01 pins 1 to 4 are `Mn_1` to `Mn_4`, in the order of socket pads 11 to 14. Pins 1
  and 2 are one coil and pins 3 and 4 the other, on every module in the table; which coil is called A differs per
  module, and only decides the direction of rotation, which is a firmware setting.
- **DRV-08 Decoupling.** Ca01 (100 nF) from `VM` to `GND` at pad 9, Ca02 (100 nF) from `+3V3` to `GND` at pad 15.
  One bulk capacitor per socket is in `specs/modules/power.md` (POW-04).
- **DRV-09 Limits.** `VM` stays inside both drivers' ratings, by the calculation in `hardware/calc/power.py`:
  TMC2240 4.5 to 36 V, absolute maximum 41 V (datasheet p9); TMC2209 5.5 to 29 V, absolute maximum 32 V
  (datasheet p75). `+3V3` is inside both drivers' VCC_IO range (2.2 to 5.5 V and 3.0 to 5.25 V).
- **DRV-10 Thermal.** The modules carry their own heat sinks. The sockets stand in one row with the modules 0.68 mm
  apart, so air can pass along the row from the fan (AUX-03); nothing taller than 2 mm stands under a module. The
  height of module and heat sink is checked in `hardware/check_fit.py` (BRD-07).

## Not verified in this build

- No module was at hand: the pad table is from the makers' drawings and schematics, read on 2026-11-11.
- Neither datasheet says whether VCC_IO may be present while VS is absent, which is the state on USB power alone.
  Printer boards with these modules are used that way; the bring-up checklist reads the currents in that state first.
- The TMC2240 datasheet calls SDO a three-state output and shows the release time after CSN; it does not state in
  words that SDO is high-impedance while CSN is high. Four drivers and the W5500 share `SPI_MISO` on that reading.
- Heat-sink height is not in BIGTREETECH's documents; `check_fit.py` assumes 12 mm.
