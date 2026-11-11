// Pin assignments of the PTZ driver board, Rev B. The single source for pins.
//
// hardware/tools/circuit.py builds the schematic from this file and hardware/check_netlist.py checks the
// netlist against it, so firmware and board cannot disagree. Change a pin here and nowhere else.
//
// Format, one per line and parsed by those scripts:  #define PIN_<NET> <gpio>
// The MCU is an ESP32-S3-DevKitC-1U on headers. A net ending in _N is active low.
//
// Rules behind this table (specs/modules/control.md, CTL-08):
//  - GPIO35, 36, 37 are not used: on boards with octal memory (N8R8, N16R8) they belong to the module.
//  - GPIO38 and GPIO48 carry the board's RGB LED (v1.1 and v1.0); GPIO38 is left free, GPIO48 gets a slow input.
//  - GPIO0 (BOOT), GPIO19/20 (USB) and GPIO44 (driven by the USB-UART bridge) are not used.
//  - GPIO43 prints the ROM's boot log, so it only reads a home input, behind a 10 k resistor.
//  - GPIO45 must be low at reset: it drives the fan switch, whose gate has a pull-down.
//  - GPIO46 must be low to enter download mode: it carries DIR2, never the fault line.
//  - Analog inputs are on ADC1 (GPIO1 to 10), which works with WiFi on.
#pragma once

// Header J1, from the antenna end towards USB -------------------------------------------------

// SPI bus shared by the four driver sockets (TMC2240, mode 3) and the Ethernet module (W5500)
#define PIN_SPI_MOSI 4
#define PIN_SPI_SCK 5
#define PIN_SPI_MISO 6

// Axis 4 (focus)
#define PIN_DIR4 7
#define PIN_STEP4 15
#define PIN_DRV4_CS 16
// Axis 3 (zoom)
#define PIN_DIR3 17
#define PIN_STEP3 18
#define PIN_DRV3_CS 8
// Stall or fault of any driver, high = active. Ask the drivers over their bus which one.
// A TMC2240's DIAG0 is open drain after reset and cannot raise this line: set diag0_pushpull in GCONF first.
#define PIN_DIAG_OR 3
// Axis 2 (tilt). GPIO46 must be low to enter download mode: a direction line is, a fault line may not be.
#define PIN_DIR2 46
#define PIN_STEP2 9
#define PIN_DRV2_CS 10
// Axis 1 (pan)
#define PIN_DIR1 11
#define PIN_STEP1 12
#define PIN_DRV1_CS 13

// Motor enable for all four drivers. High = off; pulled up on the board and on every module.
#define PIN_DRV_ENN 14

// Header J3, from the antenna end towards USB -------------------------------------------------

// Home inputs, low = switch closed. HOME4 shares its pin with the ROM's boot log (see above).
#define PIN_HOME4 43
// Motor supply after its fuse, divided by 11 (100k / 10k). ADC1 channel 0.
#define PIN_VM_SENSE 1
// Board temperature: 10k NTC to ground, 10k to 3.3 V. ADC1 channel 1.
#define PIN_NTC_SENSE 2
// Ethernet module
#define PIN_ETH_CS_N 42
#define PIN_ETH_INT_N 41
// I2C to the multiplexer (TCA9548A at 0x70): channel 0-3 = sensor port 1-4, channel 4 = spare header
#define PIN_I2C_SDA 40
#define PIN_I2C_SCL 39
// Fan output, high = on
#define PIN_FAN_PWM 45
#define PIN_HOME3 48
#define PIN_HOME2 47
#define PIN_HOME1 21
