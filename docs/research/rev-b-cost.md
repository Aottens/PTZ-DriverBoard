# Rev B cost estimate (COST-01..03)

First made on 2026-11-11 before any design (about €58 to €92), redone the same day from the planned parts list
before the schematic (€59 to €75), and **redone from the real BOM at the end of the build** (this version).
The numbers come from `hardware/calc/cost.py`; rerun it to refresh them. It is an estimate until JLC's quote.

**Tags:** `[page]` = read on jlcpcb.com on 2026-11-11. `[api]` = JLC's parts API that day
(`hardware/sourcing/jlc_api.py`). `[schatting]` = Claude's estimate, not looked up; the JLC quote settles it.

## The JLC order: five boards, assembled

Source of the parts list: `hardware/fab/jlc/ptz-driver_bom.csv`: 24 lines, 115 parts and 282 solder joints per board.

| Item | Low | High | Source |
| --- | --- | --- | --- |
| Five bare boards, 2 layers, 100 × 80 mm | $2.00 | $7.00 | `[schatting]` |
| Setup fee | $8.18 | $8.18 | `[page]` |
| Stencil | $1.53 | $1.53 | `[page]` |
| SMT joints, 1410 × $0.0016 | $2.26 | $2.26 | `[page]`, joints counted from the placement file |
| Extended loading, 3 lines × $3.07 | $9.21 | $9.21 | `[page]` |
| Parts for five boards | $20.54 | $20.54 | `[api]`, price for one piece |
| Shipping to the Netherlands | $15.00 | $25.00 | `[schatting]` |
| **Subtotal** | **$58.72** | **$73.72** | |
| With 21 % VAT | $71.05 | $89.20 | `[schatting]` |
| **In euros, at 0.892** | **€63** | **€80** | ECB rate of 2026-11-10 |

The calculation shows this fits COST-01 with about €20 to spare at the high end. Against the estimate from the
planned list it rose by €5: a second 3.3 V regulator for the sensor supply, one ESD array per port instead of one
per two, and after the two blind reviews six small tantalum capacitors in place of two large ones, a pull-down
on each step line and a second TVS. That is inside the €5 that COST-03 allows without asking.

What the estimate cannot know: the bare-board price JLC shows for this order, the shipping method, and whether JLC
rounds small parts up to a minimum quantity. The first two are the two `[schatting]` rows; the third could add a
dollar or two.

## How the parts were chosen (COST-02)

JLC's library has 351 Basic parts and 1 235 parts flagged Preferred. Neither carries the $3.07 loading fee on
Economic PCBA: "Preferred extended parts are also fee-free on Economic PCBA"
(jlcpcb.com/solutions/pcb-prototype-assembly, `[page]`). Every resistor and capacitor, both regulators, the
diodes, the fan switch, the TVS and the ESD arrays come from those two lists.

**Three Extended lines, each because nothing fee-free does the job:**

| Part | Why it is needed | Why no Basic or Preferred part |
| --- | --- | --- |
| TCA9548APWR (C130026), $0.82 | The AS5600 has one fixed I2C address, so four of them need a multiplexer (ENC-01) | The two lists hold no I2C multiplexer |
| AOD4185 (C400894), $0.37 | Reverse-polarity protection in the 5 A motor supply (POW-02) | The fee-free P-channel FETs are all SOT-23 parts of 4 A; by calculation they do not survive the current a 5 A time-lag fuse lets through |
| NTC 10 kΩ 0603 (C2892547), $0.03 | Board temperature (AUX-04) | The two lists hold no thermistor and no temperature sensor |

**Kept off the JLC order on purpose,** because JLC has them only as Extended parts and the owner solders
through-hole parts anyway: the two fuses (no fuse is fee-free; a radial fuse in a holder can also be replaced),
the four bulk capacitors (no electrolytic is fee-free), and the 5 V regulator (no power inductor is fee-free, so
a buck on the board would cost a fourth Extended line; a three-pin regulator module does the same job and is
bought once, not five times).

## Bought separately

For one head. A price with a link was read on that shop's page on 2026-11-11; `[schatting]` is not looked up.

| Item | Price | Where |
| --- | --- | --- |
| ESP32-S3-DevKitC-1U-N8R8 | €20.00 | [TinyTronics](https://www.tinytronics.nl/en/development-boards/microcontroller-boards/with-wi-fi/espressif-esp32-s3-devkitc-1u-n8r8-8mb-flash-8mb-psram), in stock. The N8 the PRD prefers is end of life; the board takes either |
| Four BIGTREETECH TMC2240 V1.0 modules, with heat sink | 4 × €9.75 = €39.00 | [TinyTronics](https://www.tinytronics.nl/en/mechanics-and-actuators/motor-controllers-and-drivers/stepper-motor-controllers-and-drivers/bigtreetech-tmc2240-motor-driver-module-v1.0), in stock. TMC2209s already owned can start |
| W5500 module, WIZ850io compatible | €9.00 | [TinyTronics](https://www.tinytronics.nl/en/communication-and-signals/ethernet/modules/w5500-ethernet-module-wiz850io-compatible), in stock. A clone: its pin order is the shop's claim. WIZnet's own is $22.12 at [DigiKey](https://www.digikey.com/en/products/detail/wiznet/WIZ850IO/8789619), out of stock that day |
| 5 V regulator, YLPTEC K7805-1000R3 | $2.38 | [LCSC C2992391](https://www.lcsc.com/product-detail/C2992391.html), in the order of `hardware/sourcing/owner_bom.md`. A Traco TSR 1-2450 is €5.57 + VAT at [DigiKey](https://www.digikey.nl/en/products/detail/traco-power/TSR-1-2450/9383780), with €18 shipping below €50. Not a RECOM R-78E5.0-1.0: it may charge 220 µF at most, less than the board and its modules hold (`calc/power.py`) |
| Four AS5600 boards | 4 × €3.00 = €12.00 | [TinyTronics](https://www.tinytronics.nl/en/sensors/magnetic-field/as5600-magnetic-angle-sensor-encoder-module). No shop page for an MT6701 board could be opened |
| Fuse T 5 A, radial | €0.76 + VAT | [DigiKey](https://www.digikey.nl/nl/products/detail/conquer/MST-5A-250V/16928153) (Conquer MST; check its 5.08 mm pitch in the sheet). No page for a T 1 A fuse could be opened: Schurter 0034.6615 is the part |
| Two TR5 fuse holders, Schurter 0031.7601 | SEK 9.50 each | [Electrokit](https://www.electrokit.com/en/fuse-holder-microfuse-tr5-6.3a-pcb); or solder the fuses in |
| Four capacitors 100 µF 35 V, Rubycon 35PX100MEFC6.3X11 | 4 × €0.34 + VAT | [DigiKey](https://www.digikey.nl/nl/products/detail/rubycon/35PX100MEFC6-3X11/3134231) |
| JST XH and PH housings, contacts and headers | 2 × €6.00 for the sets | TinyTronics: [XH set](https://www.tinytronics.nl/en/cables-and-connectors/connectors/jst-compatible/jst-xh-crimp-connector-and-housing-set), [PH set](https://www.tinytronics.nl/en/cables-and-connectors/connectors/jst-compatible/jst-ph-compatible-crimp-connector-and-housing-set), [board headers](https://www.tinytronics.nl/en/cables-and-connectors/connectors/jst-compatible). Compatible parts, not JST's own |
| JST VH 2-pin header, housing and contacts | about €2 `[schatting]` | no shop page could be opened; B2P-VH and VHR-2N are the parts |
| Female and male pin headers, 1×40 | 4 × €0.46 + €0.40 | TinyTronics: [female](https://www.tinytronics.nl/en/cables-and-connectors/connectors/pin-headers/female/40-pins-header-female), [male](https://www.tinytronics.nl/shop/en/cables-and-connectors/connectors/pin-headers/male/40-pins-header-male) |
| U.FL to SMA bulkhead lead and a 2.4 GHz antenna | €5 to €10 `[schatting]` | no shop page could be opened; check SMA against RP-SMA |
| **Per head** | **about €105 to €115** | |
