# Module spec: power (POW), Rev B

Status: **written in the Rev B one-run build (2026-11-11); gate 1 is the owner's approval of `docs/prompts/fable-board-rev-b.md`.**
Grows out of POW-01..06 in `specs/PRD.md`. Nets and references here are the contract that `hardware/check_netlist.py` checks.
Rev A's version of this file is under the git tag `rev-a`.

## What it does

```
J101 ─ VIN_RAW ─ Q101 (reverse polarity) ─ VIN ─┬─ F101 T 5 A ─ VM ── four driver sockets, C101..C104, TVS D101, VM_SENSE
                                               └─ F102 T 1 A ─ VIN_L ─ U101 5 V module ─ +5V_REG ─ D102 ─ +5V
+5V ─┬─ MCU module (its 5V pin; USB feeds the same net through the module's own diodes)
     ├─ U102 ─ +3V3      multiplexer, Ethernet module, VIO of the drivers, pull-ups
     ├─ U103 ─ +3V3_SNS ─ JP101 ─ V_SNS   the five cabled I2C ports and the home connectors
     └─ JP801 ─ fan
```

The 5 V regulator is a plug-in part like the other modules: a three-pin switching regulator in the 7805 pin order,
soldered by the owner. An on-board buck would need an inductor that JLC only has as an Extended part, and a layout
of its own that nobody can measure in this build; the module is certified by its maker and costs about as much as
that Extended line.

## Parts

| Ref | Part | LCSC | Fitted by | Datasheet read |
| --- | --- | --- | --- | --- |
| J101 | JST B2P-VH, 2 pins, 3.96 mm, with latch, 10 A | none | owner | JST VH series |
| Q101 | AOD4185, P-channel, −40 V, 20 mΩ at −4.5 V, TO-252 | C400894 (Extended) | JLC | Alpha & Omega Rev 4.2, June 2024; 1 gate, 2 (tab) drain, 3 source |
| R101 | 150 kΩ 0603 | C22807 | JLC | |
| R102 | 100 kΩ 0603 | C25803 | JLC | |
| F101 | Radial fuse 5.08 mm (TR5 type), time-lag 5 A, or its holder | none | owner | Schurter MST 250: 250 V AC, 63 V DC |
| F102 | Radial fuse 5.08 mm, time-lag 1 A, or its holder | none | owner | same |
| D101 | SMBJ18A, unidirectional TVS, 600 W, SMB | C19077573 (Preferred) | JLC | Hongjiacheng Rev 1.1: stand-off 18 V, breakdown 20.0 to 22.1 V, clamp 29.2 V at 20.55 A; band = cathode |
| C101 … C104 | 220 µF 35 V aluminium electrolytic, radial, Ø 8 mm, 3.5 mm pitch | none | owner | chosen for its ESR, which damps a hot-plug |
| C105 | 10 µF 50 V 1206 | C13585 | JLC | |
| C106, C109, C112 | 100 nF 50 V 0603 | C14663 | JLC | |
| U101 | 5 V, 1 A switching regulator, SIP-3, pins 1 = in, 2 = ground, 3 = out | none | owner | RECOM R-78K5.0-1.0 (Rev 6-2025), Mornsun K7805-1000R3, Traco TSR 1-2450 |
| D102 | SS34 Schottky, 40 V 3 A, SMA | C8678 | JLC | MDD Rev 2024A5; band = cathode |
| C107, C108 | 22 µF 25 V 0805 | C45783 | JLC | |
| U102 | AMS1117-3.3, SOT-223 | C6186 | JLC | Advanced Monolithic Systems: 1 ground, 2 and tab out, 3 in |
| C110 | 10 µF 25 V 0805 | C15850 | JLC | |
| C111 | 100 µF 6.3 V tantalum, case B | C16133 | JLC | AVX TAJB107K006RNJ; the AMS1117 sheet asks for tantalum of 22 µF or more |
| U103 | XC6206P332MR, 3.3 V 200 mA, SOT-23 | C5446 | JLC | Torex ETR0305_004b: 1 ground, 2 out, 3 in |
| C113, C114 | 1 µF 50 V 0603 | C15849 | JLC | |
| JP101 | Solder jumper, three pads, 1-2 closed by a copper bridge | none | bare copper | |
| R103 | 100 kΩ 0603 | C25803 | JLC | |
| R104 | 10 kΩ 0603 | C25804 | JLC | |
| C115 | 100 nF 50 V 0603 | C14663 | JLC | |

## Acceptance criteria

- **POW-01** One DC input on J101: pin 1 = `VIN_RAW` (plus), pin 2 = `GND`. The board runs from 11 to 17 V: a 12 V
  supply, or a D-Tap lead from a V-mount battery, 16.8 V when full. 17 V stays 3 V below D101's lowest breakdown
  voltage of 20.0 V.
- **POW-02** The board survives:
  - **a. Reverse polarity** to −30 V: Q101 is in the plus line with its drain at `VIN_RAW` and its source at
    `VIN`, its gate at `RP_GATE`. R101 (150 kΩ) from `RP_GATE` to `VIN` and R102 (100 kΩ) from `RP_GATE` to `GND`
    give it 0.6 × the input as gate drive: 6.6 V at 11 V, 10.2 V at 17 V, and 17.5 V at the TVS clamp, inside
    its ±20 V. Reversed, the gate sits at the source and the FET blocks.
  - **b. A hot-plug spike:** C101 to C104 damp the ring of the supply lead and D101 clamps `VM` (cathode `VM`,
    anode `GND`). `hardware/calc/power.py` gives the peak.
  - **c. A short on any output connector** to `GND` or to its neighbour pin, per connector in the table below.
- **POW-03** Motor and logic supply are fused separately: F101 between `VIN` and `VM`, F102 between `VIN` and
  `VIN_L`. Nothing but Q101, R101, F101, F102 and test point TP801 connects to `VIN`. Both fuses are plug-in parts.
- **POW-04 Margin at 17 V**, in `hardware/calc/power.py`: the TVS clamp at its rated pulse, a hot-plug, and the
  energy a decelerating or hand-turned head returns, against the limits in DRV-09 (TMC2209: 29 V operating, 32 V
  absolute; TMC2240: 36 V and 41 V). One bulk capacitor per driver socket, C101 to C104, from `VM` to `GND`,
  each within 12 mm of its socket's pad 9 (BRD-06). Every part on `VIN_RAW`, `VIN`, `VM` and `VIN_L` is rated for
  at least 35 V, except D101.
- **POW-05 USB alone** powers the logic and never the motors. The MCU module feeds USB power to its `5V` pin
  through its own Schottky diodes D1 and D7 (Espressif schematic V1.1), so with USB alone `+5V` carries about
  4.6 V and both 3.3 V regulators run. D102 (anode `+5V_REG`, cathode `+5V`) keeps that voltage out of U101, as
  RECOM asks ("add a blocking diode to Vout if current can flow backwards into the output"), and so out of
  `VIN_L`, `VIN` and `VM`. The same two diodes on the module keep `+5V` from the USB host.
- **POW-06** Firmware reads the motor supply: `VM_SENSE` is `VM` divided by 11 (R103 100 kΩ from `VM`, R104
  10 kΩ and C115 100 nF to `GND`) on an ADC1 pin: 1.00 V at 11 V, 1.55 V at 17 V. A blown F101 reads 0 V.
- **POW-07** `+5V_REG` is 5 V from U101: pin 1 `VIN_L`, pin 2 `GND`, pin 3 `+5V_REG`. C105 and C106 from `VIN_L`
  to `GND`; C107 from `+5V_REG` to `GND`; C108 and C109 from `+5V` to `GND`. `+5V` is `+5V_REG` less D102's
  drop, about 4.6 V at full load by calculation; the budget is 0.85 A peak of the regulator's 1 A.
- **POW-08** `+3V3` is 3.3 V from U102 (pin 3 `+5V`, pin 1 `GND`, pin 2 and tab `+3V3`), with C110 at its input
  and C111 (plus on `+3V3`) and C112 at its output. It feeds the multiplexer, the Ethernet module, the drivers'
  VIO and the pull-ups, not the MCU: the MCU module has its own regulator.
  `+3V3_SNS` is 3.3 V from U103 (pin 3 `+5V`, pin 1 `GND`, pin 2 `+3V3_SNS`), with C113 at its input and C114
  at its output. JP101 chooses `V_SNS`, the supply of every cabled sensor and home connector: pad 2 is `V_SNS`,
  pad 1 is `+3V3_SNS` (closed as delivered), pad 3 is `+5V`.
- **POW-09 Budget**, in `hardware/calc/power.py`: `+3V3` at most 0.25 A, `+3V3_SNS` at most 0.12 A of 0.2 A,
  `+5V` at most 0.85 A, and the input current with four axes at 1.5 A below F101's 5 A.

## Outputs and what limits them (POW-02c)

| Connector | Pins that can be shorted | What limits the current | Calculated |
| --- | --- | --- | --- |
| J301 … J601 motor | phase to `GND`, phase to phase | the driver module's own short protection (TMC2240 datasheet p1; TMC2209 datasheet p1) | on the module |
| J303 … J603, J701 sensor | `V_SNS` to `GND` | U103's foldback, about 100 mA into a short (Torex sheet); with JP101 on 5 V, U101's protection | 0.5 W in U103 |
| same | SDA or SCL to `GND` or `V_SNS` | pull-ups of 1.5 kΩ at least, 100 Ω to the multiplexer | under 4 mA |
| J302 … J602 home | signal to `GND` (its normal use) or to `V_SNS` | 10 kΩ pull-up and 10 kΩ series | under 1 mA |
| J801 fan | `FAN_V` to `GND`, `FAN_V` to `FAN_N` | on 5 V: U101's protection; on `VM`: F101 | see AUX-03 |

## Not verified in this build

- Nothing is measured. The hot-plug calculation rests on assumed values for the lead's inductance and the
  capacitors' ESR, which are named in `calc/power.py`.
- Which 5 V module the owner buys is open; the three named ones share pin order and pitch. RECOM states the
  back-feed rule; Mornsun says its part may not be used "with output in parallel", which D102 also answers.
- On USB alone `+3V3` is fed from about 4.6 V through a regulator that needs up to 1.3 V at full load; at the
  0.25 A here the calculation leaves it in regulation, but with a weak USB port it can sag towards 3.1 V.
