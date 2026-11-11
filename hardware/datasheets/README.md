# Datasheets and drawings used for Rev B

The files are not in the repository: they are the makers' and this repository is public. Fetch them from the links
into this folder when you need them (everything here but this file is ignored by git). "Read" means the pin table
and the limits were taken from that revision, on 2026-11-11.

## Modules the owner plugs in

| Module | Document read | Source | How it loads |
| --- | --- | --- | --- |
| ESP32-S3-DevKitC-1 / -1U | User guide v1.1 and v1.0; schematic V1.1 of 2022-11-30; dimensions drawing (DXF) of 2022-04-29 | https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html and the links on that page | curl |
| ESP32-S3-WROOM-1 / -1U | Datasheet v1.8 | https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf | curl |
| ESP32-S3 | Series datasheet v2.2 | https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf | curl |
| BIGTREETECH TMC2240 V1.0 | Manual (pin drawing p5, size p4), schematic, size drawing | https://github.com/bigtreetech/BIGTREETECH-Stepper-Motor-Driver, folder TMC2240 | curl |
| BIGTREETECH TMC2209 V1.3 | Manual, schematic, size drawing | same repository, folder TMC2209 | curl |
| FYSETC TMC2209 V3.1, FYSETC S2240 V2.0 | Schematics and readme | https://github.com/FYSETC | curl |
| Watterott SilentStepStick TMC2209 v2.0 | Schematic | https://github.com/watterott/SilentStepStick | curl |
| WIZnet WIZ850io | Datasheet V1.0 (pinout p5-6, drawing p10), schematic V1.1 | https://docs.wiznet.io/Product/ioModule/wiz850io | curl; the datasheet from a mirror |
| USR-ES1 | USR datasheet v1.0 with drawing | https://www.pusr.com | a copy at iarduino.ru |
| AS5600 | Datasheet v1-06, 2018-06-20 | ams OSRAM | curl |
| MT6701 | Datasheet Rev 0.1, 2020-03 (the only copy that loaded; not the current one) | MagnTek | a distributor's copy |

## Driver chips on the modules

| Part | Revision read | Source | How it loads |
| --- | --- | --- | --- |
| TMC2240 | 19-101548, Rev 2, 11/23 | https://www.analog.com/media/en/technical-documentation/data-sheets/tmc2240.pdf | Built-in browser only; curl and WebFetch are refused. Only excerpts were saved |
| TMC2209 | Rev 1.09, 2023-02-16 | https://www.analog.com/media/en/technical-documentation/data-sheets/tmc2209_datasheet_rev1.09.pdf | the same |

## Parts JLC assembles

Each was read from the datasheet that LCSC links on the part's page, because the maker matters.

| Part | LCSC | Maker and revision read |
| --- | --- | --- |
| TCA9548APWR | C130026 | Texas Instruments SCPS207H, September 2024 (ti.com/lit/ds/symlink/tca9548a.pdf) |
| AOD4185 | C400894 | Alpha & Omega, Rev 4.2, June 2024 (aosmd.com/res/data_sheets/AOD4185.pdf) |
| AO3400A | C20917 | Alpha & Omega, Rev 3, December 2011. Pin numbers are not printed in the sheet |
| AMS1117-3.3 | C6186 | Advanced Monolithic Systems, undated |
| SMBJ18A | C19077573 | Zhuhai Hongjiacheng, Rev 1.1 |
| SRV05-4 | C7420376 | Hongjiacheng, Rev 2.1. It does not say how to wire pin 5 on a 3.3 V line |
| SS34 | C8678 | MDD, Rev 2024A5 |
| KNTC0603/10KF3950 | C2892547 | KUU: 10 kΩ 1 %, B(25/50) 3950 |
| XC6206P332MR (considered, not used) | C5446 | Torex ETR0305_004b |

## The owner's through-hole parts

| Part | What was read |
| --- | --- |
| 5 V regulator, SIP-3 | RECOM R-78K5.0-1.0 (Rev 6-2025), R-78E5.0-1.0 (Rev 3/2016), Mornsun K7805-1000R3 (2021.01.8-A/3), Traco TSR 1-2450 (20 June 2018), Murata OKI-78SR-5/1.5-W36 |
| Radial fuses, 5.08 mm | Schurter MST 250 (rated 63 V DC); Littelfuse 382 (no DC rating in its sheet); Bel RST |
| JST connectors | JST's series pages ePH, eXH and eVH: current ratings and mounted heights. The drawings per part number did not load |

## Not read from the maker

| Part | What is used | Source of it |
| --- | --- | --- |
| BAV99 (C2500), B5819W (C8598) | Standard pin order of the package | JLC's own library symbol and footprint, read through the EasyEDA API (`fab/jlc_pins.py`) |
| TAJB107K006RNJ (C16133) | Pad 1 is the plus | JLC's library symbol draws the plus sign at pin 1, and its footprint marks pad 1 |
| AO3400A, AOD4185 | 1 gate, 2 source or drain, 3 drain or source | JLC's library symbols name the pins G, S and D (`fab/jlc_pins.py`) |
| Heat sink on a driver module | 12 mm tall | An assumption in `check_fit.py`; BIGTREETECH's documents give no height |
| 100 µF 35 V electrolytic | ESR about 0.5 Ω | An assumption for a general-purpose 6.3 × 11 mm part, used in `calc/power.py` |
