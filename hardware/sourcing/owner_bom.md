# What the owner buys for Rev B, for 1 board

Made by `owner_bom.py` from the schematic: every part JLC does not assemble, with its plug, contacts or socket.
Two orders, both inside the EU: the loose parts at Reichelt, the modules at TinyTronics. Prices were read on 2026-11-11
and include 21 % VAT. LCSC is cheaper per part, but its parcel pays import duty per kind of product: see
`DECISIONS.md`.

## At Reichelt

| Article | Part | What | Needed | Order | € each | € line | For |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [RAD 105 100/35](https://www.reichelt.com/nl/nl/a-p42401.html) | Frei, no part number | Bulk capacitor 100 µF 35 V, 6.3 × 11 mm, 105 °C | 4 | 5 | 0.07 | 0.35 | C101, C102, C103, C104 |
| [LITT 37215000411](https://www.reichelt.com/nl/nl/a-p242285.html) | Littelfuse 37215000411 | Motor fuse T 5 A, TR5, and a spare | 2 | 2 | 1.12 | 2.24 | F101 |
| [LITT 56000001009](https://www.reichelt.com/nl/nl/a-p229165.html) | Littelfuse 56000001009 | Fuse holder TR5 | 2 | 2 | 0.87 | 1.74 | F101, F102 |
| [LITT 37211000411](https://www.reichelt.com/nl/nl/a-p242278.html) | Littelfuse 37211000411 | Logic fuse T 1 A, TR5, and a spare | 2 | 2 | 1.63 | 3.26 | F102 |
| [JST B2P-VH-B](https://www.reichelt.com/nl/nl/a-p190557.html) | JST B2P-VH-B | Supply connector on the board: the B2P-VH in PBT, same pins and holes | 1 | 1 | 0.25 | 0.25 | J101 |
| [JST VH2P BU](https://www.reichelt.com/nl/nl/a-p185107.html) | JST VHR-2N | Its plug housing | 1 | 2 | 0.10 | 0.20 | J101 |
| [JST VH CKS](https://www.reichelt.com/nl/nl/a-p185113.html) | JST SVH-21T-P1.1 | Crimp contact for VH, 18 to 22 AWG | 2 | 6 | 0.10 | 0.60 | J101 |
| [JST XH4P ST](https://www.reichelt.com/nl/nl/a-p185075.html) | JST B4B-XH-A | Motor connector on the board | 4 | 4 | 0.20 | 0.80 | J301, J401, J501, J601 |
| [JST XH4P BU](https://www.reichelt.com/nl/nl/a-p185087.html) | JST XHP-4 | Its plug housing | 4 | 4 | 0.07 | 0.28 | J301, J401, J501, J601 |
| [JST XH1 CKS](https://www.reichelt.com/nl/nl/a-p405981.html) | JST SXH-001T-P0.6 | Crimp contact for XH, 22 to 28 AWG | 16 | 25 | 0.04 | 1.00 | J301, J401, J501, J601 |
| [JST PH3P ST](https://www.reichelt.com/nl/nl/a-p185050.html) | JST B3B-PH-K-S | Home connector on the board | 4 | 4 | 0.20 | 0.80 | J302, J402, J502, J602 |
| [JST PH3P BU](https://www.reichelt.com/nl/nl/a-p185042.html) | JST PHR-3 | Its plug housing | 4 | 4 | 0.05 | 0.20 | J302, J402, J502, J602 |
| [JST PH CKS](https://www.reichelt.com/nl/nl/a-p185072.html) | JST SPH-002T-P0.5S | Crimp contact for PH, 24 to 30 AWG | 28 | 40 | 0.05 | 2.00 | J302, J303, J402, J403, J502, J503, J602, J603 |
| [JST PH4P ST](https://www.reichelt.com/nl/nl/a-p185051.html) | JST B4B-PH-K-S | Sensor connector on the board | 4 | 4 | 0.17 | 0.68 | J303, J403, J503, J603 |
| [JST PH4P BU](https://www.reichelt.com/nl/nl/a-p185043.html) | JST PHR-4 | Its plug housing | 4 | 4 | 0.05 | 0.20 | J303, J403, J503, J603 |
| [ECON SL40G1E](https://www.reichelt.com/nl/nl/a-p404310.html) | Econ Connect SL40G1E | Pin header 1×40, to cut: spare I2C port and fan | 1 | 1 | 0.68 | 0.68 | J701, J801 |
| [TSR 1-2450](https://www.reichelt.com/nl/nl/a-p116850.html) | Traco TSR 1-2450 | 5 V regulator, 6.5 to 36 V in | 1 | 1 | 6.97 | 6.97 | U101 |

17 lines, €22.25; with €6.95 for DPD to the Netherlands €29.20. *Order* is *Needed* plus spares
for what can fail: crimp contacts, a plug housing, a capacitor. `owner_bom_reichelt.csv` holds article and quantity
per line; whether Reichelt's cart takes it as an upload was not tried. Stock is not checked here: Reichelt's
pages refuse a script. On 2026-11-11 every line was in stock; the pin header had limited stock.

The crimp contacts need a crimping tool for JST XH, PH and VH contacts.

The fuses are Littelfuse 372 parts. Reichelt's pages give 250 V AC and no DC rating, and no lead length: the
holder takes 4.3 mm, so cut longer leads. The DC-rated fuse `ASSEMBLY.md` names (Schurter MST 250) was not
found at Reichelt in 5 A and 1 A.

## At TinyTronics and elsewhere

| What | Count | Where |
| --- | --- | --- |
| ESP32-S3-DevKitC-1U-N8R8, €20.00 at TinyTronics | 1 | [shop page](https://www.tinytronics.nl/en/development-boards/microcontroller-boards/with-wi-fi/espressif-esp32-s3-devkitc-1u-n8r8-8mb-flash-8mb-psram) |
| Female header 1×40, 8.5 mm, to cut into the sockets (a cut costs one position): two strips give the MCU module's two 1×22 and four 1×8, two more the drivers' other 1×8 and 1×2. €0.46 to €0.60 in search results | 4 | [shop page](https://www.tinytronics.nl/en/cables-and-connectors/connectors/pin-headers/female/40-pins-header-female) |
| U.FL to SMA bulkhead lead and a 2.4 GHz antenna: no shop page was read | 1 | to find |
| W5500 module, WIZ850io compatible, €9.00 at TinyTronics (a clone: check its pin order) | 1 | [shop page](https://www.tinytronics.nl/en/communication-and-signals/ethernet/modules/w5500-ethernet-module-wiz850io-compatible) |
| BIGTREETECH TMC2240 V1.0 driver module with heat sink, €9.75 at TinyTronics | 4 | [shop page](https://www.tinytronics.nl/en/mechanics-and-actuators/motor-controllers-and-drivers/stepper-motor-controllers-and-drivers/bigtreetech-tmc2240-motor-driver-module-v1.0) |
| AS5600 sensor board, €3.00 at TinyTronics, one per axis | 4 | [shop page](https://www.tinytronics.nl/en/sensors/magnetic-field/as5600-magnetic-angle-sensor-encoder-module) |
