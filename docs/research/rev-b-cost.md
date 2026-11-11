# Rev B cost estimate (COST-01..03)

Made 2026-11-11, before any schematic. Redo it before the order (COST-03).

**Tags:** `[page]` = read on jlcpcb.com that day. `[zeker]` = JLC parts search that day or a sum shown here. `[schatting]` = Claude's estimate from memory, not looked up; check it in the JLC quote or the shop.

## The JLC order: five boards, assembled

Assumed board: two layers, at most 100 × 100 mm, about 130 solder joints per board, three to five Extended lines. The plug-in modules and through-hole connectors are not in it.

| Item | Low | High | Source |
| --- | --- | --- | --- |
| Five bare boards, 2 layers, ≤ 100 × 100 mm | $2 | $7 | `[schatting]` |
| Setup fee | $8.18 | $8.18 | `[page]` |
| Stencil | $1.53 | $1.53 | `[page]` |
| SMT joints, 650 × $0.0016 | $1.04 | $1.04 | `[page]`, joint count `[schatting]` |
| Extended loading, 3 to 5 lines × $3.07 | $9.21 | $15.35 | `[page]` |
| Parts, $3 to $5 per board | $15 | $25 | `[schatting]`, with prices in the PRD part check `[zeker]` |
| Shipping to the Netherlands | $15 | $25 | `[schatting]` |
| **Subtotal** | **$52** | **$83** | |
| With 21 % VAT | $63 | $100 | VAT rate and how JLC charges it `[schatting]` |
| **In euros, at about 0.92** | **€58** | **€92** | rate `[schatting]` |

The calculation shows this fits COST-01, but the top of the range is close to €100. The two levers are the number of Extended lines and the shipping method. **Aim for at most three Extended lines**: the multiplexer and two others with a reason each.

For comparison, Rev A: four TMC5240 drivers on the board, 80 BOM lines of which 42 Extended, and four layers at 100 × 80 mm.

## Bought separately

| Item | Estimate | Source |
| --- | --- | --- |
| Headers and connectors the owner solders, for five boards | €10 to €15 | `[schatting]` |
| Per head: ESP32-S3-DevKitC-1U | €15 to €20 | `[schatting]` |
| Per head: four TMC2240 modules (TMC2209s already owned can start) | €40 to €55 | `[schatting]` |
| Per head: four MT6701 boards (AS5600: less) | €8 to €16 | `[schatting]` |
| Per head: W5500 module with RJ45 | €4 to €8 | `[schatting]` |
| Per head: U.FL-to-SMA lead and 2.4 GHz antenna | €5 to €10 | `[schatting]` |
| **Per head** | **€72 to €109** | |
