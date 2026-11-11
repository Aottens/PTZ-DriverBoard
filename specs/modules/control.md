# Module spec: control (CTL), Rev B

Status: **written in the Rev B one-run build (2026-11-11); gate 1 is the owner's approval of `docs/prompts/fable-board-rev-b.md`.**
Grows out of CTL-01..07 in `specs/PRD.md`. Nets and references here are the contract that `hardware/check_netlist.py` checks.
Rev A's version of this file is under the git tag `rev-a`.

## What it does

The MCU and the Ethernet interface are modules on headers. The board gives them power, the SPI bus they share with
the drivers, and reset for the parts the MCU cannot reach when it is itself in reset.

## The modules

**A201: ESP32-S3-DevKitC-1U** (Espressif user guide v1.1, schematic V1.1 of 2022-11-30, drawing of 2022-04-29).
Two rows of 22 pins, 2.54 mm pitch, 22.86 mm apart; the board is 25.4 × 62.9 mm. Pin 1 of both rows is at the
antenna end, pin 22 at the USB end. Socket pads 1 to 22 are J1 pins 1 to 22; pads 23 to 44 are J3 pins 1 to 22.

| J1 pin | Name | J3 pin | Name |
| --- | --- | --- | --- |
| 1, 2 | 3V3 | 1 | GND |
| 3 | RST (EN) | 2 | GPIO43 (U0TXD) |
| 4 … 11 | GPIO4, 5, 6, 7, 15, 16, 17, 18 | 3 | GPIO44 (U0RXD) |
| 12, 13, 14 | GPIO8, 3, 46 | 4 … 9 | GPIO1, 2, 42, 41, 40, 39 |
| 15 … 20 | GPIO9, 10, 11, 12, 13, 14 | 10 … 13 | GPIO38, 37, 36, 35 |
| 21 | 5V | 14 … 18 | GPIO0, 45, 48, 47, 21 |
| 22 | GND | 19, 20 | GPIO20 (USB D+), GPIO19 (USB D−) |
| | | 21, 22 | GND |

The N8 variants the PRD prefers are marked end of life in Espressif's user guide; the N16R8 is the one on sale.
Its octal memory takes GPIO35, 36 and 37 (module datasheet v1.8, p12), so the board uses none of them and takes
either variant. The antenna connector on the module is a first-generation one: "compatible with U.FL Series
connector from Hirose, MHF I connector from I-PEX, AMC connector from Amphenol" (module datasheet v1.8, section
10.2). So an ordinary U.FL-to-SMA lead fits.

**A202: WIZnet WIZ850io** (datasheet V1.0; schematic V1.1), or a module sold as compatible with it (USR-ES1, the
"W5500 Lite" boards). Two rows of 6 pins, 2.54 mm pitch, 20.32 mm apart; 23 × 25 mm; the RJ45 jack opens at the
pin 1 end and overhangs that edge by 2.7 mm. 3.3 V only, 132 mA typical. Socket pads 1 to 6 are J1, 7 to 12 are J2.

| J1 pin | Name | J2 pin | Name |
| --- | --- | --- | --- |
| 1, 2 | GND | 1 | GND |
| 3 | MOSI | 2, 3 | 3.3V |
| 4 | SCLK | 4 | NC |
| 5 | SCNn | 5 | RSTn |
| 6 | INTn | 6 | MISO |

The module has 4.7 kΩ pull-ups on SCNn, INTn and RSTn (schematic V1.1). MISO is high-impedance while SCNn is high
(W5500 datasheet v1.1.0, p12).

## Parts

| Ref | Part | LCSC | Fitted by |
| --- | --- | --- | --- |
| A201 | Socket for the DevKitC-1U: 2 × 1×22 female header, 2.54 mm | none | owner |
| A202 | Place for the WIZ850io: soldered in, or 2 × 1×6 low female header | none | owner |
| R201, R202 | 33 Ω 0603 | C23140 | JLC |
| R203, R204, R205 | 10 kΩ 0603 | C25804 | JLC |
| D201 | B5819W Schottky, SOD-123 | C8598 | JLC |
| C201, C203 | 22 µF 25 V 0805 | C45783 | JLC |
| C202, C204 | 100 nF 50 V 0603 | C14663 | JLC |

## Acceptance criteria

- **CTL-01 MCU socket.** A201 pad 21 (5V) is `+5V`; pads 22, 23, 43 and 44 are `GND`; pad 3 (RST) is `EN`; pads 1
  and 2 (3V3) are `MCU_3V3`, which goes to a test point and nowhere else: the board's 3.3 V comes from its own
  regulators (POW-07), not from the module's. C201 and C202 sit across `+5V` and `GND` at the socket.
- **CTL-02** WiFi and ESP-NOW need nothing from the board. The antenna lead leaves the module upwards; the fit
  check keeps the space above its connector free (BRD-07).
- **CTL-03 Ethernet.** A202: pads 1, 2 and 7 `GND`; pads 8 and 9 `+3V3`, with C203 and C204 to `GND`; pad 3
  `SPI_MOSI`, pad 4 `SPI_SCK`, pad 12 `SPI_MISO`; pad 5 `ETH_CS_N`, pad 6 `ETH_INT_N`, both to the MCU; pad 11
  `PERIPH_RST_N`; pad 10 not connected.
- **CTL-05 SPI bus.** The MCU's `SPI_SCK_MCU` and `SPI_MOSI_MCU` reach `SPI_SCK` and `SPI_MOSI` through R201 and
  R202 (33 Ω) at the socket. `SPI_MISO` goes straight to the MCU. On the bus are the Ethernet module and, through
  their jumpers, the four driver sockets (DRV-02); every select line is pulled up, on the module or in the chip.
  The clock rate is a firmware setting: the TMC2240 takes at most 10 MHz (datasheet p12).
- **CTL-06 Reset of the peripherals.** `PERIPH_RST_N` resets the multiplexer (U701 pin 3) and the Ethernet module
  (A202 pad 11). R204 (10 kΩ) pulls it to `+3V3`; D201 has its anode on `PERIPH_RST_N` and its cathode on `EN`.
  So whenever the MCU is in reset the peripherals are too, and a failed `+3V3` cannot pull `EN` down. The MCU has
  no pin left to do this itself (CTL-08); after a software restart, firmware resets both over their buses.
- **CTL-07 USB.** The module's two USB-C sockets are at the board's west edge and point outwards (BRD-07). The
  board connects nothing to GPIO19, GPIO20 or GPIO44.
- **CTL-08 Pin table.** `firmware/include/pins.h` assigns 28 nets, one GPIO each, and nothing is assigned twice:
  `SPI_MOSI`, `SPI_SCK`, `SPI_MISO`, `DRV1_CS` … `DRV4_CS`, `STEP1` … `STEP4`, `DIR1` … `DIR4`, `DRV_ENN`,
  `DIAG_OR`, `ETH_CS_N`, `ETH_INT_N`, `I2C_SDA`, `I2C_SCL`, `HOME1` … `HOME4`, `VM_SENSE`, `NTC_SENSE`, `FAN_PWM`.
  On the schematic `SPI_SCK` and `SPI_MOSI` leave the socket as `SPI_SCK_MCU` and `SPI_MOSI_MCU` (CTL-05); every
  other net keeps its name. The rules, each from Espressif's documents:
  - not used at all: GPIO35, 36, 37 (octal memory), GPIO0 (BOOT button and strap), GPIO19 and 20 (USB), GPIO44
    (driven by the USB-UART bridge through 0 Ω), GPIO38 (the RGB LED on board v1.1, which may serve as AUX-02);
  - `VM_SENSE` and `NTC_SENSE` are on ADC1, GPIO1 to 10, which works with WiFi on (series datasheet v2.2, p59);
  - GPIO45 must be low at reset (module datasheet v1.8, table 4-4): only `FAN_PWM`, whose gate has a pull-down;
  - GPIO46 has a pull-down inside and any level boots from flash (table 4-3): `DIAG_OR`, which rests low;
  - GPIO43 carries the ROM's boot log, and GPIO48 the RGB LED of board v1.0: each only reads a home input,
    behind its 10 kΩ resistor;
  - GPIO3 is a strap without a pull resistor that only selects the JTAG source: it may carry any signal.
- **CTL-09** Every header pin of A201 that carries no net in the table is not connected: pads 25 (GPIO44), 32 to
  35 (GPIO38, 37, 36, 35), 36 (GPIO0), 41 and 42 (GPIO20, 19).

## Not verified in this build

- The modules compatible with the WIZ850io are not drawn by their makers as exactly as the original; the socket
  follows WIZnet's drawing, and USR's drawing of the USR-ES1 gives the same rows.
- The current rating of the DevKitC's own 3.3 V regulator is not in Espressif's documents; the board does not load it.
- All 28 usable pins are in use: there is no spare GPIO.
