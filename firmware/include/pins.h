// Pin assignments of the PTZ driver board, Rev A. The single source for pins.
//
// hardware/tools/circuit.py builds the schematic from this file and hardware/check_netlist.py checks the
// netlist against it, so firmware and board cannot disagree. Change a pin here and nowhere else.
//
// Format, one per line and parsed by those scripts:  #define <KIND>_<NET> <number>
//   PIN_<NET> n   net <NET> is on ESP32-C6 GPIO n
//   XP_<NET>  n   net <NET> is on I/O expander U203 (PCAL6416A, I2C 0x20) bit n: 0-7 = P0_0-P0_7, 8-15 = P1_0-P1_7
// A net ending in _N is active low.
#pragma once

// SPI bus (SPI2 on its IO_MUX pins): drivers, Ethernet and, through buffers, the sensor ports
#define PIN_SPI_SCK 6
#define PIN_SPI_MOSI 7
#define PIN_SPI_MISO 2

// Chip selects. Drivers and sensors hang on a dual 2-to-4 decoder (U202): put the axis index 0-3 on
// CS_A1:CS_A0, then pull one strobe low. Both strobes have pull-ups, so nothing is selected at reset.
#define PIN_CS_A0 4
#define PIN_CS_A1 5
#define PIN_CS_DRV_EN_N 0
#define PIN_CS_SNS_EN_N 1
#define PIN_ETH_CS_N 14

// Motor enable for all four drivers and the external driver ports. High = off; pulled up on the board.
#define PIN_DRV_ENN 20

// I2C: expander U203 (0x20), temperature sensor U204 (0x48), spare port J202
#define PIN_I2C_SDA 8
#define PIN_I2C_SCL 18
#define PIN_XINT_N 19

// RS-485 (UART0 pins; the ROM prints boot messages on TX, the transceiver is in receive then)
#define PIN_RS485_TX 16
#define PIN_RS485_RX 17
#define PIN_RS485_DE 23

// CAN (TWAI)
#define PIN_CAN_TX 21
#define PIN_CAN_RX 22

// Analog: motor supply after its fuse, divided by 11 (100k / 10k). ADC1 channel 3.
#define PIN_VM_SENSE 3

// Fan output, high = on
#define PIN_FAN_PWM 15

// Boot strap and user button, low = pressed
#define PIN_BOOT 9

// USB (fixed by the chip)
#define PIN_USB_DN 12
#define PIN_USB_DP 13

// I/O expander U203
#define XP_DIAG0_1 0
#define XP_DIAG0_2 1
#define XP_DIAG0_3 2
#define XP_DIAG0_4 3
#define XP_DIAG1_1 4
#define XP_DIAG1_2 5
#define XP_DIAG1_3 6
#define XP_DIAG1_4 7
#define XP_ETH_INT_N 8
#define XP_ETH_RST_N 9
#define XP_LED_R_N 10
#define XP_LED_G_N 11
#define XP_LED_B_N 12
#define XP_TALLY 13
#define XP_REC 14
#define XP_SPARE 15
