# Module spec: position sensing (ENC)

Status: **written in the Rev A one-run build (2026-11-10); gate 1 is the owner's approval of `docs/prompts/fable-board-rev-a.md`.**
Grows out of ENC-01..04 in `specs/PRD.md`.

Each axis has one port for a small remote sensor board on SPI, or for a home switch. The sensor cable never sees the bus that the drivers and Ethernet share: it gets its own buffered copy of clock and data, and only while a sensor is selected.

```
SPI_SCK, SPI_MOSI ─► U701 (74LVC244, outputs on only while CS_SNS_EN_N is low) ─► 33 Ω ─► port n
CS_SNSn (decoder) ───────────────────────────────────────────────────────────────► 33 Ω ─► port n
SPI_MISO ◄── U702 (74LVC125, gate n open only while CS_SNSn is low) ◄── 100 Ω ◄── port n
HOMEn_IN (port) ── 10k pull-up, 22k series, 1 nF, clamp diodes ──► REFL of the axis driver
```

## Parts and datasheets

| Ref | Part | LCSC | Datasheet read |
| --- | --- | --- | --- |
| J302, J402, J502, J602 | JST BM07B-GHS-TBT, 7 pins, 1.25 mm, SMD, top entry, with latch | C378970 | JST GH series |
| U701 | SN74LVC244APWR, octal buffer, TSSOP-20 | C7668 | TI SCAS414AG, June 2026 |
| U702 | SN74LVC125APWR, quad buffer with separate enables, TSSOP-14 | C7813 | TI SCAS290T, September 2024 |
| D301, D401, D501, D601 | BAT54S, two Schottky diodes in series, SOT-23 | C7420333 | Pin 1 anode, pin 2 cathode, pin 3 the common point |
| F701 | 0.2 A PTC, 0603 | C20785 | SMD0603P020TF |

## Acceptance criteria

- **ENC-01** One sensor port per axis, on SPI. A port carries its own clock, data out, data in and chip select, so any SPI sensor that runs on 3.3 V fits by configuration (AS5047P, MT6701, TLE5012B and AS5048A all do, by their datasheets' supply ranges; none is on this board).
- **ENC-02** The pinout is the same on all four ports: 1 = `+3V3_SNS`, 2 = `GND`, 3 = SCK, 4 = MOSI, 5 = MISO, 6 = CS (active low), 7 = HOME.
- **ENC-03** One home or limit input per axis, on pin 7. It has a 10 kΩ pull-up to `+3V3`, so a switch to `GND` works with two wires, and reaches the driver's REFL pin through 22 kΩ with 1 nF to `GND` and clamp diodes to `GND` and `+3V3` (datasheet p59). The driver stops the motor on it by itself. By calculation in `hardware/calc/power.py`, 24 V on this pin puts under 1 mA into the clamp.
- **ENC-04** Cable integrity over the longest run is a bench test on the rig (R-T2) and is **not** proven by this build. What the board does for it: ENC-05 and ENC-06.
- **ENC-05** The sensor cables are isolated from the main bus. U701 drives each port's SCK and MOSI separately, and its outputs are off unless `CS_SNS_EN_N` is low; 100 kΩ pull-downs hold the lines then. U702 lets only the selected port's MISO onto `SPI_MISO`.
- **ENC-06** Every signal to a port has a series resistor at the driving end (33 Ω out, 100 Ω in), to damp the cable and to limit the current into a short.
- **ENC-07** The port supply `+3V3_SNS` is `+3V3` through F701, shared by the four ports, with 4.7 µF after it. Ports are 3.3 V only: with a 5 V sensor the 3.3 V clock would not reach its input-high level.

## Connections, per axis

n = axis 1 to 4, a = 3 to 6.

| Ref | Value | Connections |
| --- | --- | --- |
| Ja02 | BM07B-GHS-TBT | 1 = `+3V3_SNS`, 2 = `GND`, 3 = `SNSn_SCK`, 4 = `SNSn_MOSI`, 5 = `SNSn_MISO`, 6 = `SNSn_CS`, 7 = `HOMEn_IN`; mounting pads = `GND` |
| Ra07 | 33R | `SNS_SCKn_B`, `SNSn_SCK` |
| Ra08 | 33R | `SNS_MOSIn_B`, `SNSn_MOSI` |
| Ra09 | 33R | `CS_SNSn`, `SNSn_CS` |
| Ra10 | 100R | `SNSn_MISO`, `SNSn_MISO_B` |
| Ra11 | 100k | `SNSn_SCK`, `GND` |
| Ra12 | 100k | `SNSn_MOSI`, `GND` |
| Ra13 | 100k | `SNSn_MISO_B`, `GND` |
| Ra05 | 10k | `HOMEn_IN`, `+3V3` |
| Ra06 | 22k | `HOMEn_IN`, `HOMEn` |
| Ca12 | 1 nF | `HOMEn`, `GND` |
| Da01 | BAT54S | common (pin 3) = `HOMEn`, anode (pin 1) = `GND`, cathode (pin 2) = `+3V3` |

`HOMEn` goes to REFL of driver Ua01 (`specs/modules/drive.md`).

## Connections, shared

| Ref | Value | Connections |
| --- | --- | --- |
| U701 | SN74LVC244A | VCC = `+3V3`; GND = `GND`; 1OE and 2OE = `CS_SNS_EN_N`; 1A1..1A4 = `SPI_SCK`; 1Y1..1Y4 = `SNS_SCK1_B`..`SNS_SCK4_B`; 2A1..2A4 = `SPI_MOSI`; 2Y1..2Y4 = `SNS_MOSI1_B`..`SNS_MOSI4_B` |
| U702 | SN74LVC125A | VCC = `+3V3`; GND = `GND`; 1OE..4OE = `CS_SNS1`..`CS_SNS4`; 1A..4A = `SNS1_MISO_B`..`SNS4_MISO_B`; 1Y..4Y = `SPI_MISO` |
| C701, C702 | 100 nF | `+3V3`, `GND` |
| F701 | 0.2 A PTC | `+3V3`, `+3V3_SNS` |
| C704 | 4.7 µF | `+3V3_SNS`, `GND` |
| R702 | 100k | `SPI_MISO`, `GND` |

## Not verified in this build

No sensor has been read through these ports. Cable length, read errors next to a running motor and the best clock rate are for R-T2 and the bring-up checklist.
