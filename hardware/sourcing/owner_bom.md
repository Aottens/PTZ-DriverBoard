# What the owner buys for Rev B, for 1 board

Made by `owner_bom.py` from the schematic: every part JLC does not assemble, with its plug, contacts or socket.
LCSC's stock and prices were read from its product pages' own data on 2026-11-11; rerun with `--refresh` before
ordering. `owner_bom_lcsc.csv` holds the LCSC lines for LCSC's BOM tool. The other shops' pages were read on
2026-11-11. Shipping, and VAT on the LCSC order, are not in these numbers and were not looked up.

## At LCSC

| LCSC | Part | Maker | What | Needed | Order | $ each | $ line | In stock | For |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [C41376161](https://www.lcsc.com/product-detail/C41376161.html) | HC-PM254-8.5H-1x22PZ | Hong Cheng | Socket for the MCU module: female header 1×22, 8.5 mm | 2 | 5 | 0.2282 | 1.14 | 17725 | A201 |
| [C42431840](https://www.lcsc.com/product-detail/C42431840.html) | PM2.54-1X8PM-H85 | JXTCONN | Socket for a driver: female header 1×8, 8.5 mm | 8 | 10 | 0.1138 | 1.14 | 10580 | A301, A401, A501, A601 |
| [C42431841](https://www.lcsc.com/product-detail/C42431841.html) | PM2.54-1X2PM-H85 | JXTCONN | Socket for a driver's two extra pins: female header 1×2, 8.5 mm | 4 | 5 | 0.0902 | 0.45 | 1735 | A301, A401, A501, A601 |
| [C135785](https://www.lcsc.com/product-detail/C135785.html) | 35PX100MEFC6.3X11 | Rubycon | Bulk capacitor 100 µF 35 V, 6.3 × 11 mm, general purpose | 4 | 5 | 0.0864 | 0.43 | 1570 | C101, C102, C103, C104 |
| [C3164152](https://www.lcsc.com/product-detail/C3164152.html) | 38215000410 | Littelfuse | Motor fuse T 5 A, TR5, Littelfuse 382 (lead length not read: the holder takes 4.3 mm, cut longer ones) | 2 | 2 | 1.1089 | 2.22 | 25 | F101 |
| [C142909](https://www.lcsc.com/product-detail/C142909.html) | 56000001009 | Littelfuse | Fuse holder TR5, Littelfuse 560 | 2 | 2 | 0.6921 | 1.38 | 32633 | F101, F102 |
| [C142712](https://www.lcsc.com/product-detail/C142712.html) | 38211000000 | Littelfuse | Logic fuse T 1 A, TR5, Littelfuse 382 | 2 | 5 | 0.2043 | 1.02 | 2710 | F102 |
| [C160315](https://www.lcsc.com/product-detail/C160315.html) | B2P-VH(LF)(SN) | JST | Supply connector on the board, JST B2P-VH | 1 | 10 | 0.0520 | 0.52 | 146590 | J101 |
| [C595405](https://www.lcsc.com/product-detail/C595405.html) | VHR-2N-BK | JST | Its plug housing, JST VHR-2N (black) | 1 | 10 | 0.0515 | 0.52 | 23390 | J101 |
| [C160349](https://www.lcsc.com/product-detail/C160349.html) | SVH-21T-P1.1 | JST | Crimp contact for VH, 18 to 22 AWG | 2 | 100 | 0.0264 | 2.64 | 119700 | J101 |
| [C144395](https://www.lcsc.com/product-detail/C144395.html) | B4B-XH-A(LF)(SN) | JST | Motor connector on the board, JST B4B-XH-A | 4 | 10 | 0.0469 | 0.47 | 537170 | J301, J401, J501, J601 |
| [C493083](https://www.lcsc.com/product-detail/C493083.html) | XHP-4-M | JST | Its plug housing, JST XHP-4 (green) | 4 | 10 | 0.0375 | 0.38 | 8030 | J301, J401, J501, J601 |
| [C140573](https://www.lcsc.com/product-detail/C140573.html) | SXH-001T-P0.6 | JST | Crimp contact for XH, 22 to 28 AWG | 16 | 100 | 0.0108 | 1.08 | 1165900 | J301, J401, J501, J601 |
| [C131339](https://www.lcsc.com/product-detail/C131339.html) | B3B-PH-K-S(LF)(SN) | JST | Home connector on the board, JST B3B-PH-K-S | 4 | 10 | 0.0420 | 0.42 | 68730 | J302, J402, J502, J602 |
| [C265393](https://www.lcsc.com/product-detail/C265393.html) | PHR-3 | JST | Its plug housing, JST PHR-3 | 4 | 50 | 0.0164 | 0.82 | 51650 | J302, J402, J502, J602 |
| [C111515](https://www.lcsc.com/product-detail/C111515.html) | SPH-002T-P0.5S | JST | Crimp contact for PH, 24 to 30 AWG | 28 | 100 | 0.0072 | 0.72 | 1601100 | J302, J303, J402, J403, J502, J503, J602, J603 |
| [C131334](https://www.lcsc.com/product-detail/C131334.html) | B4B-PH-K-S(LF)(SN) | JST | Sensor connector on the board, JST B4B-PH-K-S | 4 | 10 | 0.0458 | 0.46 | 72070 | J303, J403, J503, J603 |
| [C111514](https://www.lcsc.com/product-detail/C111514.html) | PHR-4 | JST | Its plug housing, JST PHR-4 | 4 | 50 | 0.0168 | 0.84 | 58400 | J303, J403, J503, J603 |
| [C42431788](https://www.lcsc.com/product-detail/C42431788.html) | PZ2.54-1X40P-H25 | JXTCONN | Pin header 1×40, to cut: spare I2C port and fan | 1 | 5 | 0.2244 | 1.12 | 2930 | J701, J801 |
| [C2992391](https://www.lcsc.com/product-detail/C2992391.html) | K7805-1000R3 | YLPTEC | 5 V regulator, YLPTEC's K7805-1000R3 (8 to 36 V in, 680 µF load; sheet V1.00 06/2013), and a spare. The certified one is a Traco TSR 1-2450: none at LCSC, €18 shipping at DigiKey | 2 | 2 | 2.3751 | 4.75 | 10998 | U101 |

20 lines, $22.51 before shipping and tax. *Order* is *Needed* rounded up to LCSC's minimum and pack size.
The crimp contacts need a crimping tool for JST XH, PH and VH contacts.

The two fuses are Littelfuse 382 parts, the TR5 fuses LCSC had in stock. Their data sheet states no DC rating;
the DC-rated ones `ASSEMBLY.md` names (Schurter MST 250) were out of stock at LCSC, and a Conquer MST 5 A is at
DigiKey (`docs/research/rev-b-cost.md`). LCSC had 25 of the 5 A fuse: the line most likely to run out.

## Elsewhere

| What | Count | Where |
| --- | --- | --- |
| ESP32-S3-DevKitC-1U-N8R8, €20.00 at TinyTronics | 1 | [shop page](https://www.tinytronics.nl/en/development-boards/microcontroller-boards/with-wi-fi/espressif-esp32-s3-devkitc-1u-n8r8-8mb-flash-8mb-psram) |
| U.FL to SMA bulkhead lead and a 2.4 GHz antenna: no shop page was read | 1 | to find |
| W5500 module, WIZ850io compatible, €9.00 at TinyTronics (a clone: check its pin order). WIZnet's own is LCSC C134462 | 1 | [shop page](https://www.tinytronics.nl/en/communication-and-signals/ethernet/modules/w5500-ethernet-module-wiz850io-compatible) |
| BIGTREETECH TMC2240 V1.0 driver module with heat sink, €9.75 at TinyTronics | 4 | [shop page](https://www.tinytronics.nl/en/mechanics-and-actuators/motor-controllers-and-drivers/stepper-motor-controllers-and-drivers/bigtreetech-tmc2240-motor-driver-module-v1.0) |
| AS5600 sensor board, €3.00 at TinyTronics, one per axis | 4 | [shop page](https://www.tinytronics.nl/en/sensors/magnetic-field/as5600-magnetic-angle-sensor-encoder-module) |
