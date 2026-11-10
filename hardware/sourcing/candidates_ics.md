# IC / discrete candidates for Economic PCBA

Date: 2026-11-10

How to read this:
- "Page read: yes" means I fetched `https://jlcpcb.com/partdetail/C<number>` and read the PCBA Type there. Every row below is "yes" unless stated.
- Library: as shown on the page. Where the page has no library field, I write "page: n/s" and give the type seen in a search snippet or jlcsearch in brackets (not proof).
- Stock: jlcsearch where it returned a number; otherwise the figure from an LCSC search snippet (marked "LCSC snippet"); "n/a" = not obtained. The partdetail page shows no stock. Re-check stock on the day of the order.
- Key specs marked (mem) come from my own knowledge of the part, not from a page I read; they must be checked against the datasheet (CLAUDE.md: datasheet per part).
- Candidates found via the 22 needs but not fetched are listed under "Not checked".
- Process note: jlcsearch is very incomplete (most MPNs returned nothing), so C-numbers were found with WebSearch. One attempt to use JLC's internal search endpoint was blocked by the permission system and not pursued.

## 1. Stepper driver TMC5240ATJ+T

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C7494373** | TMC5240ATJ+T | TRINAMIC Motion Control GmbH | TQFN-32 | Economic and Standard (page read: yes) | Extended | LCSC snippet: out of stock (reel 1000); jlcsearch stock null | ~$7.2 (jlcsearch), LCSC $9.85 @1 / $7.08 @100 | 36 V, 2 A RMS stepper driver + motion controller, 5x5 TQFN32 | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8590906300236570624-C7494373.pdf |
| C7429725 | TMC5240ATJ+ (tray, no T) | TRINAMIC | TQFN-32 | page not read (HTTP 429) | n/a | LCSC snippet: out of stock | ~$10.98 | same die, tray of 490 | n/a |

Status: PCBA-compatible, but **out of stock at LCSC on the snippet seen**. Stock must be re-checked right before ordering; this is the main sourcing risk.

## 2. Ethernet controller W5500

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C32843** | W5500 | WIZNET | LQFP-48 7x7 | Economic and Standard (page read: yes) | Extended | 17583 (jlcsearch) | $2.82 | SPI, hardwired TCP/IP, 3.3 V, 5 V tolerant I/O | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8579709494722682880-C32843.pdf |

## 3. Wide-input buck, 5 V out at >= 1.5 A

All three are SO-8-EP, page read: yes, Economic and Standard, Extended. Stock n/a (jlcsearch null); LCSC snippet for C182078 only gives a reel of 2500.

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C44377** | TPS54360DDAR | Texas Instruments | SOIC-8-EP | Economic and Standard | Extended | n/a | $0.72 | Vin 4.5-60 V (abs max 60 V), 3.5 A, non-synchronous (needs external Schottky, e.g. SS36), 100 kHz-2.5 MHz adjustable (mem) | https://www.ti.com/cn/lit/gpn/tps54360 |
| C31966 | TPS54560DDAR | Texas Instruments | SOIC-8-EP | Economic and Standard | Extended | n/a | $1.08 | Vin 4.5-60 V, 5 A, non-synchronous (external Schottky), 100 kHz-2.5 MHz (mem) | https://www.ti.com/cn/lit/gpn/tps54560 |
| C182078 | LMR14030SDDAR | Texas Instruments | SO-8-EP | Economic and Standard | Extended | n/a | $0.43 | Vin 4-40 V, abs max 42 V (mem), 3.5 A, synchronous (no external Schottky), 200 kHz-2.2 MHz (mem) | https://www.ti.com/cn/lit/gpn/lmr14030 |

Notes: only C44377 and C31966 reach 60 V; C182078 has only ~2 V margin above 40 V. Not suitable: LM5164DDAR (C477928) is 1 A only. A 60 V-rated synchronous part was not found.

## 4. Buck 5 V -> 3.3 V at >= 1 A

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C479074** | SY8089A1AAC | Silergy Corp | SOT-23-5 | Economic and Standard (page read: yes) | Extended | LCSC snippet: ~191k | ~$0.08 | 2.5-5.5 V in, 2 A synchronous, 1.5 MHz; LCSC says adjustable (check: A1 suffix may be fixed/adj variant) | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8588893149288124417-C479074.pdf |
| C141836 | TLV62569DBVR | Texas Instruments | SOT-23-5 | Economic and Standard (page read: yes) | Extended | 267477 (jlcsearch) | $0.07 | 2.5-5.5 V in, 2 A synchronous, 1.5 MHz, adjustable (mem) | https://www.ti.com/cn/lit/gpn/tlv62569 |
| C42420805 | MT3410LB-N | XI'AN Aerosemi Tech | SOT-23-5 | Economic and Standard (page read: yes) | Extended | 15064 (jlcsearch) | $0.03 | 2.5-5.5 V in, 1 A synchronous (mem), 1.5 MHz (mem) | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8604443499521449984-C42420805.pdf |

Pick note: C141836 has the TI datasheet and by far the most stock, so it is the safer pick if the Silergy A1 output (adjustable vs fixed) is unclear. I mark C479074 as the pick only because its output is adjustable per LCSC; if you want the better-documented part choose C141836. Not checked: TPS563201, AP3418, JW5211.

## 5. P-channel MOSFET, reverse-polarity protection

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C400894** | AOD4185 | Alpha & Omega Semicon | TO-252 (DPAK) | Economic and Standard (page read: yes) | Extended | LCSC snippet: ~36.6k | $0.37 | -40 V, -40 A (Tc), 12.5 mOhm at -10 V (per UMW second-source listing), Vgs +/-20 V (mem) | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8588905177802162176-C400894.pdf |
| C130100 | NCE40P40K | Wuxi NCE Power | TO-252-2L | Economic and Standard (page read: yes) | Extended | 12020 (jlcsearch) | $0.54 | -40 V, -40 A (mem); Rds(on) at -10 V about 20 mOhm (mem, check) | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8586205175320596480-C130100.pdf |

Not qualifying / not checked: AO4421 (C33484) is -60 V but about -6 A and ~50 mOhm (mem), fails Id/Rds. AOD409 (C5182105 Tech Public, C22451434 XBLW) not fetched. DMP4015SK3 only as "-VB" (C22389562), 18 in stock, dropped. NCE60P50K, AON7407, SI7461: no C-number found.

## 6. Zener 12 V SOD-123

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C12747** | LBZT52C12T1G | LRC | SOD-123 | Economic and Standard (page read: yes) | Extended | 34104 (jlcsearch) | $0.02 | 12 V zener, 410 mW class (mem) | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8586185296269987840-C12747.pdf |

## 7. TVS SMBJ24A / SMCJ24A / SMBJ26A

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C211760** | SMBJ24A | Yangzhou Yangjie | SMB (DO-214AA) | Economic and Standard (page read: yes) | Extended | 3003 (jlcsearch) | $0.107 | 24 V standoff, unidirectional, 600 W (mem) | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8603030067900018688-C211760.pdf |
| C7470946 | SMBJ24A | n/s | DO-214AA | page not read | n/a | 10517 (jlcsearch) | $0.038 | same family; unverified PCBA type | n/a |
| **C19077604** | SMCJ24A | hongjiacheng | SMC (DO-214AB) | Economic and Standard (page read: yes) | Extended (jlcsearch said Preferred; page says Extended) | 1794 (jlcsearch) | $0.09 | 24 V, unidirectional, 1500 W (mem) | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8762356663297302528-C19077604.pdf |
| **C5331110** | SMBJ26A | MSKSEMI | SMB (DO-214AA) | Economic and Standard (page read: yes) | Extended | 10160 (jlcsearch) | $0.04 | 26 V standoff, 600 W (mem) | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8757032464508432384-C5331110.pdf |
| C152100 | SMBJ26A | BORN | SMB (DO-214AA) | Economic and Standard (page read: yes) | Extended | 4646 (jlcsearch) | $0.07 | as above | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8757247573969522688-C152100.pdf |

## 8. Dual 2-to-4 decoder 3.3 V

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C7662** | SN74LVC139APWR | Texas Instruments | TSSOP-16 | Economic and Standard (page read: yes) | Extended | n/a | $0.53 | 1.65-3.6 V, 5 V tolerant inputs (mem) | https://www.ti.com/cn/lit/gpn/sn74lvc139a |

## 9. Quad buffer, separate OE

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C7813** | SN74LVC125APWR | Texas Instruments | TSSOP-14 | Economic and Standard (page read: yes) | Extended | LCSC snippet: 4041 (another page said 0; re-check) | $0.37 | 1.65-3.6 V, 5 V tolerant inputs (mem) | https://www.ti.com/cn/lit/gpn/sn74lvc125a |

Do not use C54561941 (TECH PUBLIC -TP): described as a Schmitt-trigger variant, not checked.

## 10. Octal buffer 3.3 V

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C7668** | SN74LVC244APWR | Texas Instruments | TSSOP-20 | Economic and Standard (page read: yes) | Extended | LCSC snippet: 1635 to 13885 (conflicting) | $0.27 | 1.65-3.6 V, 5 V tolerant inputs | https://www.ti.com/cn/lit/gpn/sn74lvc244a |

## 11. Octal buffer, 5 V supply, TTL inputs, Ioff

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C484743** | SN74AHCT244PWR | Texas Instruments | TSSOP-20 | Economic and Standard (page read: yes) | Extended | 3776 (jlcsearch) | $0.59 | 4.5-5.5 V, TTL-compatible inputs. Check in the datasheet that the inputs tolerate drive while VCC = 0 (Ioff); AHCT typically does not guarantee it, 74LVC8T245 or a series resistor may be needed | https://www.ti.com/cn/lit/gpn/sn74ahct244 |

Not checked: 74AHCT541, SN74LV244A, SN74LVC8T245. See "Nothing qualified" for the Ioff caveat.

## 12. 16-bit I2C expander with interrupt mask

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C2652299** | PCAL6416APW,118 | NXP | TSSOP-24 | Economic and Standard (page read: yes) | Extended | n/a | n/a | 1.65-5.5 V, per-pin interrupt mask, agile I/O (mem) | https://www.nxp.com/docs/en/data-sheet/PCAL6416A.pdf |
| C130204 (no mask, fallback) | TCA9535PWR | Texas Instruments | TSSOP-24 | Economic and Standard (page read: yes) | Extended | 18589 (jlcsearch) | n/a | 1.65-5.5 V, no interrupt mask | https://www.ti.com/cn/lit/gpn/tca9535 |

Also exists, not fetched: PCAL6416AHF,128 (C2652287, HWQFN-24), PCA9535PW (C3202154 is PCA9535PWR). MCP23017 and XL9535 not searched.

## 13. RS-485 transceiver 3.3 V

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C8963** | SP3485EN-L/TR | MaxLinear | SOIC-8 | Economic and Standard (page read: yes) | page: n/s [jlcsearch: Basic] | LCSC snippet: ~187k | $0.26 | 3.3 V, half duplex, 10 Mbps | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8579709476515348480-C8963.pdf |

Not fetched: ElecSuper clone C41365340.

## 14. CAN transceiver

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C2671195** | TJA1051T/3/CM,118 | NXP | SOIC-8 | Economic and Standard (page read: yes) | page: n/s | n/a | n/a | 5 V supply, 3.3 V VIO (the /3 variant) | https://www.nxp.com/docs/en/data-sheet/TJA1051.pdf |
| **C12084** (3.3 V-only alternative) | SN65HVD230DR | Texas Instruments | SOIC-8 | Economic and Standard (page read: yes) | Extended [jlcsearch: Preferred] | n/a | $0.56 | 3.3 V only | https://www.ti.com/cn/lit/ds/symlink/sn65hvd230.pdf |

Other TJA1051T/3 listings seen, not fetched: C5342108 (Tokmas, SOP-8, jlcsearch Extended), C38695 (NXP /1J).

## 15. USB ESD

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C7519** | USBLC6-2SC6 | STMicroelectronics | SOT-23-6L | Economic and Standard (page read: yes) | Extended | n/a | $0.18 | 2-line USB ESD | on page (signed link, expires) |

## 16. RS-485 / CAN bus TVS

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C521963** | SM712 | TECH PUBLIC | SOT-23 | Economic and Standard (page read: yes) | Extended | LCSC snippet: ~189k | $0.05 | asymmetric 7 V / 12 V, for RS-485, 150 W | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8588886715804737536-C521963.pdf |

CAN TVS (PESD2CAN, NUP2105L): not searched.

## 17. I2C temperature sensor 3.3 V

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C34565** | LM75BD,118 | NXP | SOIC-8 | Economic and Standard (page read: yes) | Extended | n/a | $0.37 | 2.8-5.5 V, +/-2 C, 3 address pins (mem) | https://www.nxp.com.cn/docs/en/data-sheet/LM75B.pdf |
| C2864807 | TMP1075DGKR | Texas Instruments | VSSOP-8 | Economic and Standard (page read: yes) | Extended | n/a | $0.40 | 1.7-5.5 V, +/-1 C (mem), LM75 compatible | https://www.ti.com/cn/lit/gpn/tmp1075 |

## 18. N-MOSFETs

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C8545** | 2N7002 | Jiangsu Changjing (JSCJ) | SOT-23 | Economic and Standard (page read: yes) | Basic (page labels it Basic) | n/a | $0.017 | 60 V small signal | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8550724090240786432-C8545.pdf |
| **C37130** | AO3422 | Alpha & Omega | SOT-23 | Economic and Standard (page read: yes) | Extended | n/a (clone C22451428 XBLW: 19767) | n/a | 55 V, 2.1 A, 160 mOhm at 4.5 V (LCSC); Rds at 2.5 V is not on the LCSC summary, check datasheet before relying on a 3.3 V gate | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8586177051322175488-C37130.pdf |

Not fetched: SI2308, SI2310, NCE6003, CJ2310, IRLML0060.

## 19. Schottky diodes

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C8678** | SS34 | MDD | SMA (DO-214AC) | Economic and Standard (page read: yes) | page: n/s [search snippet: Basic] | 2948003 (jlcsearch) | n/a | 40 V, 3 A, Vf 550 mV at 3 A | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8586172667476496384-C8678.pdf |
| **C8598** | B5819W SL | Jiangsu Changjing | SOD-123 | Economic and Standard (page read: yes) | page: n/s | 819277 (jlcsearch) | n/a | 40 V, 1 A | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8579707605704359936-C8598.pdf |
| C2910056 | B5819W | Jiangsu Changjing | SOD-123 | Economic and Standard (page read: yes) | Extended (page label) | n/a | n/a | 40 V, 1 A | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8589785040810119168-C2910056.pdf |

SS36, B360: not searched. Note SS34 is only 40 V; for a 60 V input buck the catch diode needs 60 V or more (SS36 or B360), so SS34 only suits a lower-voltage input.

## 20. BAT54S

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C7420333** | BAT54S | hongjiacheng | SOT-23 | Economic and Standard (page read: yes) | Extended [jlcsearch: Preferred] | LCSC snippet: ~837k | $0.013 | dual series Schottky, 30 V | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8755882743622852608-C7420333.pdf |

## 21. Crystal 25 MHz 3225

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C9006** | X322525MOB4SI | YXC | SMD3225-4P | Economic and Standard (page read: yes) | page: n/s [search snippet: Basic] | LCSC snippet: 212k-266k | n/a | 25 MHz, 12 pF, +/-10 ppm per LCSC description (+/-20 ppm stability line also shown), ESR 50 Ohm, -40..85 C | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8756945091208318976-C9006.pdf |

## 22. RGB LED, common anode, not addressable

| LCSC | MPN | Manufacturer | Package | PCBA Type | Library | Stock | Price | Key specs | Datasheet |
|---|---|---|---|---|---|---|---|---|---|
| **C60105** | 19-237/R6GHBHC-A01/2T | Everlight | SMD-4P 1.6x1.6 mm (0606) | Economic and Standard (page read: yes) | page: n/s [jlcsearch: Extended] | n/a | $0.064 | common anode per JLC search snippet, plain R/G/B dies | https://www.everlighteurope.com/custom/files/datasheets/DSE-0001946.pdf |
| C458749 | LTST-C19HE1WT | Lite-On | SMD-4P 1.6x1.6 mm | Economic and Standard (page read: yes) | page: n/s [jlcsearch: Extended] | LCSC snippet: ~17.8k | $0.073 | common anode RGB, 130 deg, 20 mA (LCSC description) | https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/8588934883397259264-C458749.pdf |

## Needs where nothing (fully) qualified

- 1 TMC5240ATJ+T: PCBA type is fine, but LCSC showed it out of stock. Not a PCBA-type problem.
- 3: no synchronous 60 V part found. C44377 (60 V, non-sync) is the best; LMR14030 has only a 40 V rating.
- 5: only AOD4185 and NCE40P40K confirmed. Rds and Vgs numbers are partly from memory.
- 11: part itself qualifies for PCBA, but input-while-VCC=0 (Ioff) behaviour of AHCT is not confirmed; check the datasheet.
- 18 logic-level N-FET: only AO3422 found; its Rds at 2.5 V is not confirmed.
- Not looked up at all (out of time/rate limits): alternatives in 8, 9, 10, 12 (MCP23017, XL9535, TCAL6416), 13 (MAX3485, THVD1450, SN65HVD3082E), 14 (TCAN332, TJA1051TK), CAN TVS in 16, TMP102/NCT75 in 17, SS36/B360 in 19.
