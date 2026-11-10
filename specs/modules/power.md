# Module spec: power (POW)

Status: **written in the Rev A one-run build (2026-11-10); gate 1 is the owner's approval of `docs/prompts/fable-board-rev-a.md`.**
Grows out of POW-01..06 in `specs/PRD.md`. Nets and references here are the contract that `hardware/check_netlist.py` checks.

## What it does

```
J101 ─ VIN_RAW ─ Q101 (reverse polarity) ─ VIN ─┬─ F101 7 A ─ VM ── drivers, bulk capacitors, TVS, VM_SENSE
                                               └─ F102 1.5 A ─ VIN_L ─ U101 buck ─ +5V ─┬─ CAN, external driver ports, fan
                                                                                       └─ D104 ─┐
                                                              USB-C VBUS ─────────────── D105 ─┴─ VSYS ─ U102 buck ─ +3V3
```

## Parts and datasheets

| Ref | Part | LCSC | Datasheet read |
| --- | --- | --- | --- |
| J101 | JST B2P-VH, 2 pins, 3.96 mm, through-hole, with latch | C160315 | JST VH series; pin 1 marked on the housing |
| Q101 | AOD4185, P-channel, -40 V, 15 mΩ at -10 V, TO-252 | C400894 | Alpha & Omega, Rev 4.2, June 2024 |
| D101 | BZT52C12 class zener, 12 V, SOD-123 | C12747 | LRC LBZT52C12T1G |
| D102 | SMBJ24A, unidirectional TVS, 600 W | C7470946 | Stand-off 24 V, breakdown 26.7 to 29.5 V, clamp 38.9 V at 15.4 A |
| F101 | Littelfuse 0452007.MRL, 7 A slow, 2410 | C72975 | Littelfuse 452 series |
| F102 | Littelfuse 046601.5NRHF, 1.5 A fast, 1206, 63 V | C187598 | Littelfuse 466 series |
| C101, C102 | 220 µF 50 V aluminium electrolytic, 10 × 10.2 mm | C970698 | Chosen for its ESR, which damps a hot-plug (POW-02) |
| U101 | TPS54360DDAR, 60 V 3.5 A buck, HSOP-8 | C44377 | TI SLVSBB4G, June 2018 |
| D103 | SS36 class Schottky, 60 V 3 A, SMA | see BOM | Catch diode of U101 |
| L101 | 22 µH shielded, about 7 × 7 mm, Isat ≥ 3 A | C128694 | SMMS0630-220M |
| U102 | TLV62569DBVR, 5.5 V 2 A buck, SOT-23-5 | C141836 | TI SLVSDM0, revised October 2017 |
| L102 | 2.2 µH shielded, 4 × 4 mm, Isat ≥ 2.5 A | C408335 | Sunlord MWSA0402S-2R2MT |
| D104, D105 | B5819W, 40 V 1 A Schottky, SOD-123 | C8598 | |

## Acceptance criteria

- **POW-01** One DC input on J101, a locking JST VH header: pin 1 = `VIN_RAW` (plus), pin 2 = `GND`. Nominal 12 to 24 V; the board runs from 10.8 to 25.2 V (24 V + 5 %). The upper limit keeps the supply below D102's lowest breakdown voltage of 26.7 V.
- **POW-02** The board survives:
  - **a. Reverse polarity** to -30 V: Q101 sits in the plus line with its drain at `VIN_RAW` and its source at `VIN`, its gate at `RP_GATE`, pulled to `GND` by R101 (100 kΩ) and clamped to the source by D101 (cathode at `VIN`).
  - **b. A hot-plug spike:** C101 and C102 damp the ring of the supply cable, and D102 clamps `VM` (cathode at `VM`, anode at `GND`). `hardware/calc/power.py` shows the peak.
  - **c. A short on any output connector** to `GND` or to its neighbour pin, per connector in the table under *Outputs and what limits them*.
- **POW-03** Motor and logic supply are fused separately: F101 between `VIN` and `VM`, F102 between `VIN` and `VIN_L`. Nothing but F101, F102, Q101, D101 and the test point TP901 connects to `VIN`.
- **POW-04** The margin from the highest voltage `VM` can reach to the TMC5240's 41 V absolute maximum is calculated in `hardware/calc/power.py` for: the TVS clamp at its rated pulse, a hot-plug, and a motor driven by hand or decelerating. Every part on `VM`, `VIN` and `VIN_L` is rated for at least 50 V, except D102.
- **POW-05** USB alone powers logic only. `VBUS` reaches `VSYS` through D105 (anode at `VBUS`) and nothing else; `+5V` reaches `VSYS` through D104 (anode at `+5V`). So USB cannot feed `+5V`, `VM` or the host.
- **POW-06** Firmware reads the motor supply: `VM_SENSE` is `VM` divided by 11 (R110 100 kΩ from `VM`, R111 10 kΩ and C114 100 nF to `GND`) on an ADC pin. A blown F101 reads as 0 V.
- **POW-07** `+5V` is 4.97 V ± 4 % from U101 (R106 + R112 over R107), sized for 1.5 A. Its under-voltage lock-out starts the converter above about 9.2 V and stops it below about 8.1 V (R102, R103), by calculation.
- **POW-08** `+3V3` is 3.3 V ± 3 % from U102, fed from `VSYS`. The budget is 0.8 A peak; D104 and D105 limit the feed to 1 A.
- **POW-09** The supply current is budgeted in `hardware/calc/power.py` for each rail and for the input at 12 V and 24 V, and the fuses, connector and copper are rated above it.
- **POW-10** Every rail has a test point (AUX-05) and its nominal voltage on the silkscreen.

## Connections

Pins by name, as the datasheet names them.

| Ref | Value | Connections |
| --- | --- | --- |
| J101 | B2P-VH | 1 = `VIN_RAW`, 2 = `GND` |
| Q101 | AOD4185 | D = `VIN_RAW`, S = `VIN`, G = `RP_GATE` |
| D101 | 12 V zener | K = `VIN`, A = `RP_GATE` |
| R101 | 100k | `RP_GATE`, `GND` |
| F101 | 7 A | `VIN`, `VM` |
| F102 | 1.5 A | `VIN`, `VIN_L` |
| D102 | SMBJ24A | K = `VM`, A = `GND` |
| C101, C102 | 220 µF 50 V | + = `VM`, - = `GND` |
| U101 | TPS54360 | VIN = `VIN_L`, EN = `BUCK_EN`, RT/CLK = `BUCK_RT`, FB = `BUCK_FB`, COMP = `BUCK_COMP`, GND and thermal pad = `GND`, SW = `BUCK_SW`, BOOT = `BUCK_BOOT` |
| C103, C104 | 4.7 µF 50 V | `VIN_L`, `GND` |
| C105 | 100 nF 50 V | `VIN_L`, `GND` |
| C106 | 100 nF 50 V | `BUCK_BOOT`, `BUCK_SW` |
| R102 | 330k | `VIN_L`, `BUCK_EN` |
| R103 | 47k | `BUCK_EN`, `GND` |
| R104 | 220k | `BUCK_RT`, `GND` |
| R105 | 4.7k | `BUCK_COMP`, `BUCK_COMP_RC` |
| C107 | 22 nF | `BUCK_COMP_RC`, `GND` |
| C108 | 100 pF | `BUCK_COMP`, `GND` |
| D103 | 60 V 3 A Schottky | K = `BUCK_SW`, A = `GND` |
| L101 | 22 µH | `BUCK_SW`, `+5V` |
| C109, C110 | 22 µF 25 V | `+5V`, `GND` |
| R106 | 47k | `+5V`, `BUCK_FB_MID` |
| R112 | 5.1k | `BUCK_FB_MID`, `BUCK_FB` |
| R107 | 10k | `BUCK_FB`, `GND` |
| D104 | B5819W | A = `+5V`, K = `VSYS` |
| D105 | B5819W | A = `VBUS`, K = `VSYS` |
| U102 | TLV62569 | VIN = `VSYS`, EN = `VSYS`, GND = `GND`, SW = `SW3V3`, FB = `FB3V3` |
| C111 | 4.7 µF 16 V | `VSYS`, `GND` |
| L102 | 2.2 µH | `SW3V3`, `+3V3` |
| C112, C113 | 10 µF 10 V | `+3V3`, `GND` |
| R108 | 100k | `+3V3`, `FB3V3` |
| R109 | 22k | `FB3V3`, `GND` |
| C115 | 22 pF | `+3V3`, `FB3V3` |
| R110 | 100k | `VM`, `VM_SENSE` |
| R111 | 10k | `VM_SENSE`, `GND` |
| C114 | 100 nF | `VM_SENSE`, `GND` |

The values around U101 (R102 to R107, R112, C107, C108, L101) come from the datasheet equations worked out in `hardware/calc/power.py`.

`VM_SENSE` goes to the MCU pin that `firmware/include/pins.h` names `PIN_VM_SENSE`.

## Outputs and what limits them

| Connector pin | Source | A short to GND gives |
| --- | --- | --- |
| Motor outputs J301 to J601 | TMC5240 bridges | The driver's own over-current protection switches the bridge off (datasheet p79, p81) |
| `+3V3_SNS` on J302 to J602 | `+3V3` through F701, 0.2 A PTC | The PTC trips; `+3V3` may dip and reset the MCU, nothing is damaged |
| `+3V3_I2C` on J202 | `+3V3` through F201, 0.2 A PTC | The same |
| `+5V_EXT` on J303 to J603 | `+5V` through F702, 0.2 A PTC | The PTC trips |
| `FAN_V` on J902 | `+5V` or `VM` through F901, 0.5 A 30 V PTC | The PTC trips |
| Signal outputs to sensor and external driver ports | 74LVC244, 74AHCT244 through 33 Ω and 220 Ω | The series resistor limits the current to below the buffer's rating |
| RS-485 and CAN lines | Transceivers | Their own short-circuit limit (SP3485, TJA1051 datasheets) |
| Tally, record, fan switch | Open drain | No current: these only sink |

## Not verified in this build

Everything here is by calculation and datasheet. The rails, the reverse-polarity path, the fuses and the ride-through of a short are checked by the owner in `tests/hardware/bringup-rev-a.md`.
