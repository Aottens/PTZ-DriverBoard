# Module spec: motor drive (DRV)

Status: **written in the Rev A one-run build (2026-11-10); gate 1 is the owner's approval of `docs/prompts/fable-board-rev-a.md`.**
Grows out of DRV-01..06 in `specs/PRD.md`.

Four identical axis cells. Axis n = 1 to 4; its parts carry references in the hundreds a = 3, 4, 5, 6 (axis 1 = 3xx, axis 4 = 6xx). The board does not know which axis is pan: that is configuration (CORE-01).

## Parts and datasheets

| Ref | Part | LCSC | Datasheet read |
| --- | --- | --- | --- |
| U301, U401, U501, U601 | TMC5240ATJ+T, TQFN-32 5 × 5 mm | C7494373 | Analog Devices 19-101625C, Rev 1, 4/24; pin table p15-18 |
| J301, J401, J501, J601 | JST S4B-XH-A, 4 pins, 2.5 mm, through-hole, side entry | C157925 | JST XH series |
| J303, J403, J503, J603 | JST SM04B-GHS-TB, 4 pins, 1.25 mm, SMD, side entry, with latch | C189895 | JST GH series |
| U703 | SN74AHCT244PWR, octal buffer, TSSOP-20 | C484743 | TI SCLS228O, July 2024 |
| F702 | 0.2 A PTC, 0603 | C20785 | SMD0603P020TF |

TMC5240 pins used here, TQFN-32 (datasheet p16-18): 1 IREF, 2 AIN, 3 VDD1V8, 4 AGND, 5 VCC_IO, 6 ENCN, 7 ENCB, 8 ENCA, 9 DRV_ENN, 10 UART_EN, 11 DIAG0, 12 DIAG1/SW, 13 OV, 14 CPI, 15 CPO, 16 VCP, 17 VS, 18 OUT1B, 19 OUT2B, 20 VS, 21 VS, 22 OUT2A, 23 OUT1A, 24 VS, 25 SLEEPN, 26 CSN, 27 SCK, 28 SDI, 29 SDO, 30 CLK, 31 REFL, 32 REFR, exposed pad GND.

## Acceptance criteria

- **DRV-01** Four axes, each a TMC5240 with its own motor connector. Motor connector pin 1 = OUT1A, 2 = OUT2A (coil A), 3 = OUT1B, 4 = OUT2B (coil B).
- **DRV-02** Each driver is set up from firmware over SPI: UART_EN and CLK are tied to `GND` (SPI, internal clock), SCK, SDI and SDO are on the shared bus, and each CSN has its own decoder output `CS_DRVn`. SDO is three-state (datasheet p16), so the four share `SPI_MISO` directly.
- **DRV-03** No trimmers. IREF has 12 kΩ 1 % to `GND`, which gives the full 3 A peak range; firmware picks the range and scales the current (datasheet p46-47).
- **DRV-04** DIAG0 and DIAG1 of every axis reach the MCU: each has a 10 kΩ pull-up to `+3V3` and goes to the I/O expander, whose interrupt `XINT_N` is on a direct MCU pin (`specs/modules/control.md`, CTL-09). The driver stops the motor itself on a stall or a home input; the MCU's own stop is DRV-07.
- **DRV-05** Thermal, by calculation in `hardware/calc/thermal.py` with its assumptions written down: junction temperature with all four axes at 1.5 A RMS in still air stays below the 125 °C operating limit with margin, and the board temperature is stated, since the housing softens first (MEC-06). The exposed pad has at least 9 vias to the ground planes, checked in `hardware/check_board.py`.
- **DRV-06** Each axis has an external driver port: pin 1 = `+5V_EXT`, 2 = STEP, 3 = DIR, 4 = `GND`. STEP and DIR are the driver's DIAG0 and DIAG1 (datasheet p60-61), buffered to 5 V by U703 through 220 Ω. U703's outputs are enabled by `DRV_ENN`, so the direct stop pin also stops an external driver's steps.
- **DRV-07** `DRV_ENN` is one direct MCU pin to all four drivers and to U703, pulled up to `+3V3` by R701 (10 kΩ), so the bridges are off until firmware drives it low.
- **DRV-08** Supply decoupling as the datasheet's application circuit (p20, p166): per driver two 100 nF and one 10 µF, all 50 V, from `VM` to `GND`; 1 µF from VCP to `VM`; 22 nF 50 V between CPI and CPO; 2.2 µF from VDD1V8 to `GND`; 100 nF on VCC_IO. The 440 µF bulk is shared (POW).
- **DRV-09** Unused pins are tied off: AIN, ENCA, ENCB, ENCN and REFR to `GND`; OV left open. SLEEPN goes to `VM` through 100 kΩ, because it may not exceed VS + 0.3 V (datasheet p10) and `+3V3` is present on USB power when `VM` is not.
- **DRV-10** Each motor output has 470 pF 50 V to `GND` against ESD from a belt drive in a plastic housing (datasheet p167).

## Connections, per axis

n = axis 1 to 4, a = 3 to 6.

| Ref | Value | Connections |
| --- | --- | --- |
| Ua01 | TMC5240ATJ | VS (4 pins) = `VM`; VCC_IO = `+3V3`; AGND and exposed pad = `GND`; VDD1V8 = `An_1V8`; VCP = `An_VCP`; CPO = `An_CPO`; CPI = `An_CPI`; IREF = `An_IREF`; SLEEPN = `An_SLEEPN`; AIN, CLK, UART_EN, ENCA, ENCB, ENCN, REFR = `GND`; OV = not connected; CSN = `CS_DRVn`; SCK = `SPI_SCK`; SDI = `SPI_MOSI`; SDO = `SPI_MISO`; DRV_ENN = `DRV_ENN`; DIAG0 = `DIAG0_n`; DIAG1/SW = `DIAG1_n`; REFL = `HOMEn`; OUT1A = `Mn_A1`; OUT2A = `Mn_A2`; OUT1B = `Mn_B1`; OUT2B = `Mn_B2` |
| Ja01 | S4B-XH-A | 1 = `Mn_A1`, 2 = `Mn_A2`, 3 = `Mn_B1`, 4 = `Mn_B2` |
| Ja03 | SM04B-GHS-TB | 1 = `+5V_EXT`, 2 = `STEPn_O`, 3 = `DIRn_O`, 4 = `GND`; mounting pads = `GND` |
| Ca01, Ca02 | 100 nF 50 V | `VM`, `GND` |
| Ca03 | 10 µF 50 V | `VM`, `GND` |
| Ca04 | 1 µF 50 V | `An_VCP`, `VM` |
| Ca05 | 22 nF 50 V | `An_CPI`, `An_CPO` |
| Ca06 | 2.2 µF | `An_1V8`, `GND` |
| Ca07 | 100 nF | `+3V3`, `GND` |
| Ca08, Ca09, Ca10, Ca11 | 470 pF 50 V | `Mn_A1`, `Mn_A2`, `Mn_B1`, `Mn_B2` to `GND`, in that order |
| Ra01 | 12k | `An_IREF`, `GND` |
| Ra02 | 100k | `An_SLEEPN`, `VM` |
| Ra03 | 10k | `DIAG0_n`, `+3V3` |
| Ra04 | 10k | `DIAG1_n`, `+3V3` |
| Ra14 | 220R | `STEPn_B`, `STEPn_O` |
| Ra15 | 220R | `DIRn_B`, `DIRn_O` |

## Connections, shared

| Ref | Value | Connections |
| --- | --- | --- |
| U703 | SN74AHCT244 | VCC = `+5V`; GND = `GND`; 1OE and 2OE = `DRV_ENN`; 1A1..1A4 = `DIAG0_1`..`DIAG0_4`; 1Y1..1Y4 = `STEP1_B`..`STEP4_B`; 2A1..2A4 = `DIAG1_1`..`DIAG1_4`; 2Y1..2Y4 = `DIR1_B`..`DIR4_B` |
| C703 | 100 nF | `+5V`, `GND` |
| F702 | 0.2 A PTC | `+5V`, `+5V_EXT` |
| C705 | 1 µF | `+5V_EXT`, `GND` |
| R701 | 10k | `DRV_ENN`, `+3V3` |

## Not verified in this build

Motion, noise, StealthChop tuning, stall detection and the real driver temperature need the board and a motor: `tests/hardware/bringup-rev-a.md`. Whether a given external driver accepts 5 V signals through 220 Ω depends on that driver.
