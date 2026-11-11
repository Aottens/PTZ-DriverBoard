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
| In euros, at 0.892 | €63 | €80 | ECB rate of 2026-11-10 |
| EU import duty and handling | €5 | €10 | `[page]` for the rule, `[schatting]` for the number of customs lines |
| **Total** | **€68** | **€90** | |

The calculation shows this fits COST-01 with about €10 to spare at the high end. The import row was added on
2026-11-11 after the owner's LCSC cart showed the charge: since July 2026 a parcel up to €150 from outside the EU
pays €3 of duty per kind of product, and JLC's page adds €2 of handling per customs line since November
(jlcpcb.com/help/article/eu-customs-reform-faq). Assembled boards are one kind of product; the high column counts two
lines. A carrier that advances the duty may charge a fee of its own, which JLC's duty-paid shipping avoids. Against the estimate from the
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
| Loose parts: connectors with plugs and contacts, fuses and holders, capacitors, pin header, the 5 V regulator Traco TSR 1-2450 | €22.25 + €6.95 shipping | Reichelt, 17 lines with article numbers in `hardware/sourcing/owner_bom.md`; prices read on its Dutch pages |
| Four female headers 1×40, 8.5 mm, to cut into the sockets | 4 × €0.46 to €0.60 | [TinyTronics](https://www.tinytronics.nl/en/cables-and-connectors/connectors/pin-headers/female/40-pins-header-female), from search results |
| Four AS5600 boards | 4 × €3.00 = €12.00 | [TinyTronics](https://www.tinytronics.nl/en/sensors/magnetic-field/as5600-magnetic-angle-sensor-encoder-module). No shop page for an MT6701 board could be opened |
| U.FL to SMA bulkhead lead and a 2.4 GHz antenna | €5 to €10 `[schatting]` | no shop page could be opened; check SMA against RP-SMA |
| **Per head** | **about €110 to €115** | before the two shops' shipping |
