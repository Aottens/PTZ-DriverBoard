# Module spec: camera and other I/O (CAM, AUX)

Status: **written in the Rev A one-run build (2026-11-10); gate 1 is the owner's approval of `docs/prompts/fable-board-rev-a.md`.**
Grows out of CAM-02 and AUX-01..05 in `specs/PRD.md`.

## Parts and datasheets

| Ref | Part | LCSC | Datasheet read |
| --- | --- | --- | --- |
| Q901, Q902, Q903 | AO3422, N-channel, 55 V 2.1 A, logic level, SOT-23 | C37130 | Alpha & Omega, Rev 2.1, March 2024; pin 1 gate, 2 source, 3 drain |
| J901 | JST SM04B-GHS-TB, 4 pins | C189895 | JST GH series |
| J902 | JST B2B-XH-A, 2 pins, through-hole, top entry | C158012 | JST XH series |
| D901 | B5819W Schottky, SOD-123 | C8598 | |
| F901 | 0.5 A 30 V PTC, 1812 | C269128 | |
| D201 | Everlight 19-237/R6GHBHC-A01/2T, RGB LED, common anode, 1.6 × 1.6 mm | C60105 | Pin order from JLC's own library part: 1 red, 2 green, 3 blue cathode, 4 common anode. The maker's drawing did not load; a wrong order only swaps colours |

## Acceptance criteria

- **CAM-02** Two open-drain outputs on one connector, for tally and record trigger. J901: 1 = tally, 2 = record, 3 and 4 = `GND`. Each is the drain of an AO3422 whose gate is an expander pin with 100 kΩ to `GND`, so both are off at reset. Rated 55 V; by calculation in `hardware/calc/power.py` each sinks 0.5 A with under 0.2 V drop.
- **AUX-01** A spare I2C port, J202, with the pin order of Qwiic and STEMMA QT: 1 = `GND`, 2 = 3.3 V, 3 = SDA, 4 = SCL (`specs/modules/control.md`).
- **AUX-02** A status RGB LED, D201, on three expander pins (low = on), so firmware can keep it dark during a show; and a user button, SW201, which is also the boot button.
- **AUX-03** One switched output for a fan, J902: 1 = `FAN_V` (plus), 2 = `FAN_N` (switched to `GND`). An AO3422 on a direct MCU pin for PWM, off at reset through 100 kΩ on its gate, with a diode across the fan. Solder jumper JP901 picks the fan supply: `+5V` as delivered, or `VM`. F901 limits it.
- **AUX-04** Firmware reads the board temperature from U204 on I2C, placed between the drivers (`specs/modules/control.md`). Each driver also reports its own chip temperature over SPI.
- **AUX-05** A test point on every rail and bus: `VIN`, `VM`, `+5V`, `VSYS`, `+3V3`, `GND` (two); `SPI_SCK`, `SPI_MOSI`, `SPI_MISO` and both decoder strobes; `I2C_SDA`, `I2C_SCL`, `XINT_N`; `DRV_ENN`; `CAN_TX`, `CAN_RX`; `RS485_TX`, `RS485_RX`; `EN`; the spare expander pin. Pads of at least 1.0 mm, on the top side, each named on the silkscreen.

## Connections

| Ref | Value | Connections |
| --- | --- | --- |
| Q901 | AO3422 | G = `TALLY`, S = `GND`, D = `TALLY_OD` |
| Q902 | AO3422 | G = `REC`, S = `GND`, D = `REC_OD` |
| R901 | 100k | `TALLY`, `GND` |
| R902 | 100k | `REC`, `GND` |
| J901 | SM04B-GHS-TB | 1 = `TALLY_OD`, 2 = `REC_OD`, 3 = `GND`, 4 = `GND`; mounting pads = `GND` |
| Q903 | AO3422 | G = `FAN_G`, S = `GND`, D = `FAN_N` |
| R903 | 100R | `FAN_PWM`, `FAN_G` |
| R904 | 100k | `FAN_G`, `GND` |
| D901 | B5819W | A = `FAN_N`, K = `FAN_V` |
| JP901 | 3-pad solder jumper, 1-2 bridged | 1 = `+5V`, 2 = `FAN_SRC`, 3 = `VM` |
| F901 | 0.5 A PTC | `FAN_SRC`, `FAN_V` |
| J902 | B2B-XH-A | 1 = `FAN_V`, 2 = `FAN_N` |
| D201 | RGB LED | common anode = `+3V3`; red cathode = `LED_R_K`; green cathode = `LED_G_K`; blue cathode = `LED_B_K` |
| R213 | 1k | `LED_R_K`, `LED_R_N` |
| R214 | 220R | `LED_G_K`, `LED_G_N` |
| R215 | 220R | `LED_B_K`, `LED_B_N` |

Test points, one pad each:

| Ref | Net | Ref | Net | Ref | Net |
| --- | --- | --- | --- | --- | --- |
| TP901 | `VIN` | TP908 | `SPI_SCK` | TP915 | `CS_DRV_EN_N` |
| TP902 | `VM` | TP909 | `SPI_MOSI` | TP916 | `CS_SNS_EN_N` |
| TP903 | `+5V` | TP910 | `SPI_MISO` | TP917 | `SPARE` |
| TP904 | `VSYS` | TP911 | `I2C_SDA` | TP918 | `CAN_TX` |
| TP905 | `+3V3` | TP912 | `I2C_SCL` | TP919 | `CAN_RX` |
| TP906 | `GND` | TP913 | `DRV_ENN` | TP920 | `RS485_TX` |
| TP907 | `GND` | TP914 | `XINT_N` | TP921 | `RS485_RX` |
| | | | | TP922 | `EN` |

H1 to H4 are the four mounting holes; they have no pins and no net.

## Not verified in this build

LED colours and brightness, the fan output under PWM, and the camera's response to tally and record are for `tests/hardware/bringup-rev-a.md`.
