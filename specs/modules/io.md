# Module spec: other I/O (AUX), Rev B

Status: **written in the Rev B one-run build (2026-11-11); gate 1 is the owner's approval of `docs/prompts/fable-board-rev-b.md`.**
Grows out of AUX-01..05 in `specs/PRD.md`. Nets and references here are the contract that `hardware/check_netlist.py` checks.
Rev A's version of this file is under the git tag `rev-a`. The camera outputs (CAM), RS-485 and CAN are struck from the PRD.

## Parts

| Ref | Part | LCSC | Fitted by | Datasheet read |
| --- | --- | --- | --- | --- |
| Q801 | AO3400A, N-channel, 30 V, SOT-23 | C20917 | JLC | Alpha & Omega; 1 gate, 2 source, 3 drain |
| D801 | B5819W Schottky, SOD-123 | C8598 | JLC | |
| R801 | 100 Ω 0603 | C22775 | JLC | |
| R802 | 100 kΩ 0603 | C25803 | JLC | |
| J801 | Pin header 1×2, 2.54 mm | none | owner | |
| RT801 | NTC 10 kΩ 1 %, B 3950, 0603 | C2892547 (Extended) | JLC | KNTC0603/10KF3950 |
| R803 | 10 kΩ 0603 | C25804 | JLC | |
| C801 | 100 nF 50 V 0603 | C14663 | JLC | |
| TP801 … TP816 | Test point, 1.5 mm bare pad | none | bare copper | |
| H1 … H4 | Mounting hole, 3.2 mm | none | | |

## Acceptance criteria

- **AUX-01** The spare multiplexer channel is on header J701: `specs/modules/sensing.md`, ENC-08.
- **AUX-02** The board has no LED of its own: the RGB LED on the MCU module is the status light, and firmware
  keeps it dark during a show. On board v1.1 it is on GPIO38, which the board leaves alone (CTL-08).
- **AUX-03 Fan output, for a 5 V fan.** J801: 1 = `+5V` (plus), 2 = `FAN_N` (switched minus). Q801 switches
  `FAN_N` to `GND`: drain `FAN_N`, source `GND`, gate `FAN_G`. R801 (100 Ω) joins `FAN_PWM` from the MCU to
  `FAN_G`; R802 (100 kΩ) pulls `FAN_G` to `GND`, so the fan is off while the MCU is in reset, and GPIO45 reads low
  at reset as it must (CTL-08). D801 across the fan: anode `FAN_N`, cathode `+5V`. A short on the connector is
  limited by the 5 V module. There is no jumper to the motor supply: on `VM` only the 5 A fuse would stand
  between a shorted fan lead and a 0.5 mm track (blind review, B2).
- **AUX-04 Board temperature.** RT801 from `NTC_SENSE` to `GND`, R803 (10 kΩ) from `NTC_SENSE` to `+3V3`, C801
  (100 nF) from `NTC_SENSE` to `GND`; `NTC_SENSE` goes to an ADC1 pin. RT801 stands next to the row of drivers.
  The reading is `+3V3 × R / (R + 10 kΩ)`: 1.65 V at 25 °C, by calculation 0.49 V at 70 °C.
- **AUX-05 Test points**, one bare pad each, named on the silkscreen. `VIN_L`, `+5V_REG` and `+3V3_SNS` have none:
  each is on a through-hole pin or jumper pad that a probe reaches (F102, U101's `IN` and `OUT`, JP101's `3V3` pad).

  | Ref | Net | Ref | Net |
  | --- | --- | --- | --- |
  | TP801 | `VIN` | TP809 | `SPI_MOSI` |
  | TP802 | `VM` | TP810 | `SPI_MISO` |
  | TP803 | `+5V` | TP811 | `I2C_SDA` |
  | TP804 | `+3V3` | TP812 | `I2C_SCL` |
  | TP805 | `V_SNS` | TP813 | `DRV_ENN` |
  | TP806 | `GND` | TP814 | `DIAG_OR` |
  | TP807 | `GND` | TP815 | `PERIPH_RST_N` |
  | TP808 | `SPI_SCK` | TP816 | `MCU_3V3` |

- **AUX-06** Four mounting holes H1 to H4, not connected to any net.
