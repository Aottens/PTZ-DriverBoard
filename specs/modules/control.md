# Module spec: control (CTL)

Status: **written in the Rev A one-run build (2026-11-10); gate 1 is the owner's approval of `docs/prompts/fable-board-rev-a.md`.**
Grows out of CTL-01..07 in `specs/PRD.md`. **Which MCU pin carries which net is not written here: `firmware/include/pins.h` is the single source.**

## Parts and datasheets

| Ref | Part | LCSC | Datasheet read |
| --- | --- | --- | --- |
| U201 | ESP32-C6-MINI-1U-H4 | C20627095 | Espressif, ESP32-C6-MINI-1 & MINI-1U datasheet v1.5; pins p10-11, straps p12-15 |
| U202 | SN74LVC139APWR, dual 2-to-4 decoder, TSSOP-16 | C7662 | TI SCAS341O, February 2005 |
| U203 | PCAL6416APW, 16-bit I2C expander with interrupt mask, TSSOP-24 | C2652299 | NXP Rev 7.1, 30 August 2022 |
| U204 | TMP1075DGKR, I2C temperature sensor, VSSOP-8 | C2864807 | TI SBOS854F, June 2024 |
| U205 | USBLC6-2SC6, USB ESD protection, SOT-23-6 | C7519 | ST USBLC6-2 |
| J201 | USB Type-C receptacle, 16 pins, HRO TYPE-C-31-M-12 | C165948 | Korean Hroparts drawing |
| J202 | JST SM04B-SRSS-TB, 4 pins, 1.0 mm, SMD | C160404 | JST SH series |
| U801 | W5500, Ethernet controller, LQFP-48 | C32843 | WIZnet datasheet v1.1.0; reference schematic "W5500-Ref-RJ45WithMag", 2015-09-25 |
| J801 | HanRun HR911105A, RJ45 with magnetics and LEDs, through-hole | C12074 | Pinout from KiCad's library symbol, which cites the HanRun drawing; the drawing itself did not load |
| Y801 | 25 MHz crystal, 3225, 4 pads | C9006 | X322525MOB4SI |
| U802 | SP3485EN, 3.3 V RS-485 transceiver, SOIC-8 | C8963 | MaxLinear SP3485 |
| D801 | SM712, RS-485 TVS, SOT-23 | C521963 | Pins 1 and 2 the lines, pin 3 ground |
| U803 | TJA1051T/3, CAN transceiver with 3.3 V I/O, SOIC-8 | C2671195 | NXP Rev 9, 28 November 2017 |
| J802, J803 | JST SM04B-GHS-TB, 4 pins | C189895 | JST GH series |
| SW201, SW202 | Tactile switch, 5.1 mm, SMD | C318884 | TS-1187A-B-A-B |

## Acceptance criteria

- **CTL-01** The MCU is U201 with an external antenna. Its supply has 22 µF and 100 nF at the pin. EN has 10 kΩ to `+3V3` and 1 µF to `GND` (datasheet p40), and a reset button SW202 to `GND`. No copper keep-out is needed under a MINI-1U (datasheet p10).
- **CTL-01a Strapping pins** (datasheet p12-15). GPIO9 = `BOOT` has 10 kΩ to `+3V3` and the button SW201 to `GND`: high for a normal boot, held low at reset for download. GPIO8 is held high by an I2C pull-up, which download mode requires. GPIO4, GPIO5 and GPIO15 only matter for SDIO and for eFuse-selected JTAG, which this board does not use; they carry `CS_A0`, `CS_A1` and `FAN_PWM`, whose level at reset does no harm.
- **CTL-01b Every signal that stops a motor is on a direct MCU pin:** `DRV_ENN` (DRV-07) and the interrupt `XINT_N` (CTL-09). `check_netlist.py` checks every MCU pin against `pins.h`.
- **CTL-02** WiFi and ESP-NOW come from the module; the antenna plugs into the module's own connector, which must stay reachable (BRD-07).
- **CTL-03** Ethernet: U801 on the shared SPI bus with its own chip select `ETH_CS_N` on a direct pin, wired as WIZnet's reference schematic for a jack with magnetics, and J801 assembled on the board. Interrupt and reset are on the expander. The PHY mode pins are tied high: all modes, auto-negotiation.
- **CTL-04** RS-485: U802, half duplex. DE and the inverted RE are tied together to `RS485_DE`, pulled down so the board listens at reset. The bus has D801 as protection and a 120 Ω terminator behind solder jumper JP801, open as delivered. J802: 1 = A, 2 = B, 3 and 4 = `GND`.
- **CTL-06** CAN: U803 with its S pin at `GND` (normal mode). A 120 Ω terminator behind solder jumper JP802, closed as delivered. J803: 1 = CANH, 2 = CANL, 3 and 4 = `GND`. The transceiver's 5 V supply is only there with motor power.
- **CTL-07** USB-C J201 for flashing and logs, through the chip's own USB serial/JTAG. Both CC pins have 5.1 kΩ to `GND`; D+ and D- go straight to the module with U205 as ESD protection; the shield is at `GND`. It must be reachable from outside (BRD-07).
- **CTL-08 Chip selects.** U202 gives four driver selects `CS_DRV1..4` and four sensor selects `CS_SNS1..4` from two address lines and two strobes. Both strobes and `ETH_CS_N` have 10 kΩ pull-ups, so nothing is selected while the MCU is in reset. Address 0 selects axis 1.
- **CTL-09 I/O expander.** U203 at I2C address 0x20 carries the slow signals listed in `pins.h`. Its interrupt `XINT_N` is on a direct MCU pin with a 10 kΩ pull-up; its reset follows the MCU's EN.
- **CTL-10 SPI bus.** The module's clock and data-out pins feed the bus through 22 Ω at the module (`SPI_SCK_MCU` to `SPI_SCK`, `SPI_MOSI_MCU` to `SPI_MOSI`). `SPI_MISO` has a 100 kΩ pull-down (R702) so it never floats.

## Connections: MCU and logic

| Ref | Value | Connections |
| --- | --- | --- |
| U201 | ESP32-C6-MINI-1U | 3V3 = `+3V3`; all GND pins and the pad = `GND`; EN = `EN`; each IO pin = the net that `pins.h` gives its GPIO, except that the GPIO of `SPI_SCK` carries `SPI_SCK_MCU` and that of `SPI_MOSI` carries `SPI_MOSI_MCU`; pins named NC = not connected |
| C201 | 22 µF | `+3V3`, `GND` |
| C202 | 100 nF | `+3V3`, `GND` |
| R201 | 10k | `EN`, `+3V3` |
| C203 | 1 µF | `EN`, `GND` |
| SW202 | reset | `EN`, `GND` |
| SW201 | boot and user | `BOOT`, `GND` |
| R202 | 10k | `BOOT`, `+3V3` |
| R203 | 22R | `SPI_SCK_MCU`, `SPI_SCK` |
| R204 | 22R | `SPI_MOSI_MCU`, `SPI_MOSI` |
| U202 | SN74LVC139A | VCC = `+3V3`; GND = `GND`; 1G = `CS_DRV_EN_N`; 1A = `CS_A0`; 1B = `CS_A1`; 1Y0..1Y3 = `CS_DRV1`..`CS_DRV4`; 2G = `CS_SNS_EN_N`; 2A = `CS_A0`; 2B = `CS_A1`; 2Y0..2Y3 = `CS_SNS1`..`CS_SNS4` |
| C204 | 100 nF | `+3V3`, `GND` |
| R205 | 10k | `CS_DRV_EN_N`, `+3V3` |
| R206 | 10k | `CS_SNS_EN_N`, `+3V3` |
| R207 | 10k | `ETH_CS_N`, `+3V3` |
| U203 | PCAL6416A | VDD(I2C-bus) and VDD(P) = `+3V3`; VSS = `GND`; SCL = `I2C_SCL`; SDA = `I2C_SDA`; INT = `XINT_N`; RESET = `EN`; ADDR = `GND`; P0_0..P1_7 = the nets that `pins.h` gives bits 0 to 15 |
| C205 | 100 nF | `+3V3`, `GND` |
| R208 | 10k | `XINT_N`, `+3V3` |
| U204 | TMP1075 | V+ = `+3V3`; GND, A0, A1, A2 = `GND`; SCL = `I2C_SCL`; SDA = `I2C_SDA`; ALERT = not connected |
| C206 | 100 nF | `+3V3`, `GND` |
| R209 | 2.2k | `I2C_SDA`, `+3V3` |
| R210 | 2.2k | `I2C_SCL`, `+3V3` |
| J201 | USB-C | VBUS (4 pins) = `VBUS`; GND (4 pins) and shield = `GND`; CC1 = `CC1`; CC2 = `CC2`; D+ (2 pins) = `USB_DP`; D- (2 pins) = `USB_DN`; SBU1, SBU2 = not connected |
| R211 | 5.1k | `CC1`, `GND` |
| R212 | 5.1k | `CC2`, `GND` |
| U205 | USBLC6-2SC6 | pins 1 and 6 = `USB_DN`; pins 3 and 4 = `USB_DP`; pin 2 = `GND`; pin 5 = `VBUS` |
| C207 | 1 µF | `VBUS`, `GND` |
| J202 | SM04B-SRSS-TB | 1 = `GND`, 2 = `+3V3_I2C`, 3 = `I2C_SDA`, 4 = `I2C_SCL`; mounting pads = `GND` |
| F201 | 0.2 A PTC | `+3V3`, `+3V3_I2C` |
| C208 | 1 µF | `+3V3_I2C`, `GND` |

Expander nets: `DIAG0_n` and `DIAG1_n` come from the drivers, `ETH_INT_N` and `ETH_RST_N` go to U801, `LED_R_N`, `LED_G_N`, `LED_B_N`, `TALLY` and `REC` are in `specs/modules/io.md`, and `SPARE` ends on a test point.

## Connections: Ethernet

| Ref | Value | Connections |
| --- | --- | --- |
| U801 | W5500 | TXP = `ETH_TXP`; TXN = `ETH_TXN`; RXP = `ETH_RXP`; RXN = `ETH_RXN`; AVDD (6 pins) = `3V3A`; AGND (6 pins) and GND = `GND`; VDD = `+3V3`; EXRES1 = `ETH_RES`; TOCAP = `ETH_TOCAP`; 1V2O = `ETH_1V2`; XI/CLKIN = `ETH_XI`; XO = `ETH_XO`; SCSn = `ETH_CS_N`; SCLK = `SPI_SCK`; MOSI = `SPI_MOSI`; MISO = `SPI_MISO`; INTn = `ETH_INT_N`; RSTn = `ETH_RST_N`; PMODE0, PMODE1, PMODE2 = `+3V3`; RSVD pin 23 = `GND`; LINKLED = `ETH_LINK`; ACTLED = `ETH_ACT`; DNC, VBG, SPDLED, DUPLED, RSVD pins 38 to 42 and the NC pins = not connected |
| J801 | HR911105A | TD+ = `ETH_TXP`; TD- = `ETH_TXN`; TCT = `ETH_TCT`; RD+ = `ETH_RDP`; RD- = `ETH_RDN`; RCT = `ETH_RCT`; pin 7 = not connected; pin 8 and shield = `GND`; green LED anode (9) = `+3V3`, cathode (10) = `ETH_LED_G`; yellow LED anode (12) = `+3V3`, cathode (11) = `ETH_LED_Y` |
| FB801 | ferrite bead 600 Ω | `+3V3`, `3V3A` |
| C801, C802, C803, C804 | 100 nF | `3V3A`, `GND` |
| C805 | 10 µF | `3V3A`, `GND` |
| C806 | 100 nF | `+3V3`, `GND` |
| C807 | 4.7 µF | `+3V3`, `GND` |
| R801 | 12.4k | `ETH_RES`, `GND` |
| C808 | 4.7 µF | `ETH_TOCAP`, `GND` |
| C809 | 10 nF | `ETH_1V2`, `GND` |
| Y801 | 25 MHz | crystal pads = `ETH_XI`, `ETH_XO`; case pads = `GND` |
| C810 | 18 pF | `ETH_XI`, `GND` |
| C811 | 18 pF | `ETH_XO`, `GND` |
| R802 | 1M | `ETH_XI`, `ETH_XO` |
| R803, R804 | 49.9R | `ETH_TXP` to `3V3A`; `ETH_TXN` to `3V3A` |
| R805 | 10R | `3V3A`, `ETH_TCT` |
| C812 | 22 nF | `ETH_TCT`, `GND` |
| R806, R807 | 49.9R | `ETH_RXP` to `ETH_RCT`; `ETH_RXN` to `ETH_RCT` |
| C813 | 6.8 nF | `ETH_RXP`, `ETH_RDP` |
| C814 | 6.8 nF | `ETH_RXN`, `ETH_RDN` |
| C815 | 10 nF | `ETH_RCT`, `GND` |
| R808 | 330R | `ETH_LINK`, `ETH_LED_G` |
| R809 | 330R | `ETH_ACT`, `ETH_LED_Y` |
| R810 | 10k | `ETH_INT_N`, `+3V3` |
| R811 | 10k | `ETH_RST_N`, `+3V3` |

The jack's shield is tied straight to `GND`: the head is plastic, there is no chassis to refer it to. The isolation of the cable side is the transformer's and the jack's internal 1 nF 2 kV capacitor.

## Connections: RS-485 and CAN

| Ref | Value | Connections |
| --- | --- | --- |
| U802 | SP3485 | VCC = `+3V3`; GND = `GND`; RO = `RS485_RX`; RE and DE = `RS485_DE`; DI = `RS485_TX`; A = `RS485_A`; B = `RS485_B` |
| C816 | 100 nF | `+3V3`, `GND` |
| R812 | 10k | `RS485_DE`, `GND` |
| R813 | 10k | `RS485_RX`, `+3V3` |
| D801 | SM712 | pin 1 = `RS485_A`; pin 2 = `RS485_B`; pin 3 = `GND` |
| R814 | 120R | `RS485_A`, `RS485_TERM` |
| JP801 | solder jumper, open | `RS485_TERM`, `RS485_B` |
| J802 | SM04B-GHS-TB | 1 = `RS485_A`, 2 = `RS485_B`, 3 = `GND`, 4 = `GND`; mounting pads = `GND` |
| U803 | TJA1051T/3 | VCC = `+5V`; VIO = `+3V3`; GND and S = `GND`; TXD = `CAN_TX`; RXD = `CAN_RX`; CANH = `CAN_H`; CANL = `CAN_L` |
| C817 | 100 nF | `+5V`, `GND` |
| C818 | 100 nF | `+3V3`, `GND` |
| R815 | 120R | `CAN_H`, `CAN_TERM` |
| JP802 | solder jumper, bridged | `CAN_TERM`, `CAN_L` |
| J803 | SM04B-GHS-TB | 1 = `CAN_H`, 2 = `CAN_L`, 3 = `GND`, 4 = `GND`; mounting pads = `GND` |

## Not verified in this build

No firmware has run. Radio range in the housing, the Ethernet link, the crystal's start-up and frequency, RS-485 and CAN signalling, and USB enumeration are for `tests/hardware/bringup-rev-a.md`. Whether one core carries the control loop is a firmware question (R-04).
