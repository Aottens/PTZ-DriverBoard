# Rev B cost estimate (COST-01..03)

First made on 2026-11-11 before any design (about €58 to €92). **Redone the same day from the planned parts
list, before the schematic** (this version). It is redone once more from the real BOM at the end of the build.
The numbers come from `hardware/calc/cost.py`; rerun it to refresh them.

**Tags:** `[page]` = read on jlcpcb.com on 2026-11-11. `[api]` = JLC's parts API that day
(`hardware/sourcing/jlc_api.py`). `[schatting]` = Claude's estimate, not looked up; the JLC quote settles it.

## The JLC order: five boards, assembled

Source of the parts list: `hardware/sourcing/planned_bom.csv`: 26 lines, 106 parts and 255 solder joints per board.

| Item | Low | High | Source |
| --- | --- | --- | --- |
| Five bare boards, 2 layers, up to 100 × 100 mm | $2.00 | $7.00 | `[schatting]` |
| Setup fee | $8.18 | $8.18 | `[page]` |
| Stencil | $1.53 | $1.53 | `[page]` |
| SMT joints, 1275 × $0.0016 | $2.04 | $2.04 | `[page]`, joints counted from the list |
| Extended loading, 3 lines × $3.07 | $9.21 | $9.21 | `[page]` |
| Parts for five boards | $16.39 | $16.39 | `[api]`, price for one piece |
| Shipping to the Netherlands | $15.00 | $25.00 | `[schatting]` |
| **Subtotal** | **$54.35** | **$69.35** | |
| With 21 % VAT | $65.76 | $83.91 | `[schatting]` |
| **In euros, at 0.892** | **€59** | **€75** | ECB rate of 2026-11-10 |

The calculation shows this fits COST-01 with about €25 to spare at the high end.

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

Prices are for one head, not looked up one by one unless a source is given.

| Item | Estimate | Source |
| --- | --- | --- |
| Per head: ESP32-S3-DevKitC-1U (the N8 is end of life; the N16R8 fits too) | €15 to €20 | `[schatting]` |
| Per head: four TMC2240 StepStick modules (TMC2209s already owned can start) | €40 to €55 | `[schatting]` |
| Per head: W5500 module, WIZ850io or compatible | €9 to €22 | TinyTronics €9.00 (compatible), DigiKey $22.12 (WIZnet), both read 2026-11-11 |
| Per head: four MT6701 or AS5600 boards | €8 to €16 | `[schatting]` |
| Per head: 5 V regulator module, SIP-3 | €2 to €8 | LCSC: Mornsun K7805-1000R3 $2.16, Traco TSR 1-2450 $6.47, RECOM R-78K5.0-1.0 $7.83 |
| Per head: U.FL-to-SMA lead and 2.4 GHz antenna | €5 to €10 | `[schatting]` |
| Per board: headers, sockets, JST connectors, two fuses with holders, four capacitors | €8 to €12 | `[schatting]` |
| **Per head** | **€87 to €143** | |
