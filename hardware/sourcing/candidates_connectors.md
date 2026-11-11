# Candidate connectors and electromechanical parts for Economic PCBA

Date: 2026-11-10

Method: candidates from jlcsearch.tscircuit.com and WebSearch; PCBA Type read on `https://jlcpcb.com/partdetail/C<number>` with WebFetch.
**Every row below was read on its partdetail page (column "PCBA Type") unless a note says otherwise.**
Stock and price come from jlcsearch (stock = jlcsearch `stock`; "n/a" = jlcsearch returned no stock for that C-number, the partdetail page shows no stock either; some LCSC snippets are quoted in the notes and are unverified). Price = jlcsearch, USD per piece, quantity-1 tier or as given. Library: all "Extended" as read on the page unless noted. Recommended pick per need in **bold**.
Specs under "Key specs" come from jlcsearch descriptions (not from datasheets) unless marked "page". Claude cannot measure: Isat, ESR and fuse values below are catalogue data, check datasheets before release.

## Through-hole parts under Economic PCBA (method step 5)

Page https://jlcpcb.com/capabilities/pcb-assembly-capabilities (read 2026-11-10): Economic PCBA supports through-hole parts, with "Single sided placement (SMT/Thru-hole)". THT parts are wave-soldered, solder is applied only to the THT components in the order and unused holes are protected. Economic limits: 2 to 50 pcs, single-sided placement only, no V-cut panels, no gold fingers/castellated holes/edge plating, no SPI. The page's FAQ reads slightly different (THT and mixed SMD+THT under both Economic and Standard); the partdetail "Economic and Standard" tag per part is the proof used here. Single-sided means all THT and SMT parts on one side.

## 1. JST VH 3.96 mm, 2 pin

| LCSC | MPN | Manufacturer | Mounting / orientation | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C160315** | B2P-VH(LF)(SN) | JST | THT, top entry (vertical) | Economic and Standard | Extended | n/a | 0.0627 | 10 A, 250 V; read |
| C158007 | B2PS-VH(LF)(SN) | JST | THT, side entry (right angle) | Economic and Standard | Extended | n/a | 0.1523 | 10 A, 250 V; read |
| C5379868 | VH3.96-2P ZZ | SHOU HAN | THT, top entry | Economic and Standard | Extended | 153130 | 0.0265 | 7 A, 250 V; clone; read |

No SMD VH header found (C485345 B2P-VH(SMT) is reported as discontinued by a WebSearch snippet, not read).

## 2. JST XH 2.54 mm, 4 pin (motor)

| LCSC | MPN | Manufacturer | Mounting / orientation | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C144395** | B4B-XH-A(LF)(SN) | JST | THT, top | Economic and Standard | Extended | n/a | 0.057 | 3 A, 250 V; read |
| C157925 | S4B-XH-A(LF)(SN) | JST | THT, side (right angle) | Economic and Standard | Extended | n/a | 0.1018 | read |
| C2904944 | XH-4A | DEALON | THT, top | Economic and Standard | Extended | 8757 | 0.0213 | clone; read |
| C19271397 | XY-XHB2.54-4A21 | XYECONN | THT, side (right angle) | Economic and Standard | Extended | 14336 | 0.0226 | 2 A; clone; read |
| C161861 | S4B-XH-SM4-TB(LF)(SN) | JST | SMD, side (right angle) | Economic and Standard | Extended | n/a (LCSC snippet 25935, unverified) | 0.4397 | read |

B4B-XH-SM4-TB (SMD top entry): no LCSC listing found (a Digikey forum thread says JST does not list it either). No 4-pin SMD XH clone found; 2-pin SMD clones in need 3.

## 3. JST XH 2 pin (fan)

| LCSC | MPN | Manufacturer | Mounting / orientation | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C158012** | B2B-XH-A(LF)(SN) | JST | THT, top | Economic and Standard | Extended | n/a | 0.0409 | 3 A; read |
| C157931 | S2B-XH-A(LF)(SN) | JST | THT, side | Economic and Standard | Extended | n/a | 0.0688 | read |
| C5142098 | HX 2.54-2P WT | hanxia | SMD, side (right angle) | Economic and Standard | Extended | 70394 | 0.0738 | 3 A, 250 V; clone; read |
| C46061675 | HX PZ2.54-1x2P WT | hanxia | SMD, side (right angle) | Economic and Standard | Extended | 19523 | 0.04 | 3 A; clone; read |

No SMD top-entry XH found.

## 4. JST GH 1.25 mm SMD with lock (3, 4, 7 pin)

| LCSC | MPN | Manufacturer | Mounting / orientation | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C189895** | SM04B-GHS-TB(LF)(SN) (4P) | JST | SMD, side | Economic and Standard | Extended | n/a (LCSC snippet shows 0 or conflicting) | 0.6537 | 1 A; read; check stock on order day |
| C161692 | BM04B-GHS-TBT(LF)(SN) (4P) | JST | SMD, top (vertical) | Economic and Standard | Extended | n/a (snippets 13283 or 0, conflicting) | 0.7085 | read |
| **C495552** | SM07B-GHS-TB(LF)(SN) (7P) | JST | SMD, side | Economic and Standard | Extended | n/a (LCSC snippet 18217, unverified) | 0.5611 | read |
| **C378970** | BM07B-GHS-TBT(LF)(SN)(N) (7P) | JST | SMD, top | Economic and Standard | Extended | 20999 | 0.5532 | 1 A, 50 V; "(N)" suffix variant; read |
| C3029369 | WAFER-GH1.25-3PLB (3P) | XUNPU | SMD, top (vertical) | Economic and Standard | Extended | 82825 | 0.147 | 1 A, 125 V; clone; read |
| C22448488 | WAFER-GH1.25-7PLT-W1-P (7P) | Yuandi | SMD, top (vertical) | Economic and Standard | Extended | 1438 | 0.1102 | clone; read |

Not found / not read: SM03B-GHS-TB and BM03B-GHS-TBT (3P JST) no C-number found; 4P GH clones: none found in jlcsearch. 6P clone C22448487 (stock 4) and 8P clone C42376901 (SH-SM08B-GHS-TB, side, stock 34964) seen in jlcsearch but partdetail not read, so unproven.
JST GH is the same lock family; picks above are 7P side (C495552) or top (C378970), 4P side C189895, 3P top clone C3029369.

## 5. Fallback: JST PH 2.0 mm

| LCSC | MPN | Manufacturer | Mounting / orientation | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C265289** | B4B-PH-K(LF)(SN) (4P) | JST | THT, top | Economic and Standard | Extended | 32646 | 0.091 | 2 A, 100 V; read |
| **C157981** | B7B-PH-K-S(LF)(SN) (7P) | JST | THT, top | Economic and Standard | Extended | 19293 | 0.1064 | 2 A, 100 V; read |
| C7433665 | HCZZ0469-4 (4P) | Hong Cheng | SMD, top (vertical) | Economic and Standard | Extended | 23921 | 0.0386 | PH clone; read |
| C18077773 | BX-HY2.0-4PWT (4P) | Bossie | SMD, side (right angle) | Economic and Standard | Extended | 8294 | 0.0763 | PH clone; read |

Not found: B3B-PH-K-S (3P), 6P THT, S7B-PH-SM4-TB, B7B-PH-SM4-TB (not searched beyond the above; no candidate verified).

## 6. JST SH 1.0 mm 4 pin SMD side

| LCSC | MPN | Manufacturer | Mounting / orientation | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C160404** | SM04B-SRSS-TB(LF)(SN) | JST | SMD, side | Economic and Standard | Extended (page shows no explicit field, listed in assembly parts lib) | n/a | 0.2153 | 1 A, 50 V; read |
| C51940130 | XY-SM04B-SRSS-TB | XYECONN | SMD, side | Economic and Standard | Extended | 17159 | 0.0395 | clone; read |

## 7. USB Type-C 16 pin, USB 2.0

| LCSC | MPN | Manufacturer | Mounting / orientation | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C165948** | TYPE-C-31-M-12 | Korean Hroparts (HRO) | SMD right angle (shell stakes: confirm on drawing, page does not state) | Economic and Standard | Extended | n/a (jlcsearch null) | 0.1873 | 16P, 5 A, 20 V; read |
| C3039307 | MC-107SSY | Hanbo | SMD right angle | Economic and Standard | Extended | 6647 | 0.2312 | 16P 5 A; read |
| C5368946 | GT-USB-7004B | G-Switch | SMD right angle | Economic and Standard | Extended | 3214 | 0.8607 | 16P, 24 V, USB 2.0; read |

KH-TYPE-C-16P, TYPE-C 16PIN 2MD(073), USB4105-GF-A: not found in jlcsearch, not pursued further. Stakes/footprint are not stated on the pages: check the datasheet drawing.

## 8. RJ45 with integrated magnetics (10/100)

| LCSC | MPN | Manufacturer | Mounting / orientation | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C12074** | HR911105A | HANRUN | THT, right angle, with LEDs (page); tab orientation not on page | Economic and Standard | Extended | n/a (LCSC snippet 59581, unverified) | 1.7286 | 21.3 x 16.04 x 13.5 mm (page, L x W x H), 0 to 70 C; read |
| C69427 | HY911105AE | HANRUN | THT, right angle, LEDs | Economic and Standard | Extended | n/a | 3.0106 | same 21.3 x 16.04 x 13.5 mm; -40 to 85 C; read |
| C163507 | HR913550A | HANRUN | THT, right angle, LEDs | Economic and Standard | Extended | n/a (LCSC snippet 1494, unverified) | 1.0775 | 21.3 x 16.04 x 13.5 mm; read |
| C19724785 | HR915310AE | HANRUN | THT, LEDs (tab-up per snippet) | Economic and Standard | Extended | n/a | 2.1219 | 16.8 x 16 x 16.9 mm; read |
| C455444 | J0011D21BNL | Pulse | THT, right angle, LEDs | Economic and Standard | Extended | 2863 | 3.2355 | 21.59 x 16.26 x 13.84 mm; page does not state magnetics (Pulse part is a magjack per its datasheet, verify) ; read |
| C7421421 | RJ45-408-050-11 | XUNPU | SMD, vertical, LEDs | Economic and Standard | Extended | 3371 | 1.0687 | 15.85 x 15.6 x 13.2 mm; page does NOT state magnetics, not proven a magjack |
| C5341217 | HC632701A-M906-A | HCTL | SMD, right angle, LEDs | Economic and Standard | Extended | 369 | 2.5493 | 25.4 x 16.1 x 13.5 mm; page does NOT state magnetics, not proven a magjack |

Result: through-hole magjacks qualify (HR911105A and clones are "Economic and Standard"). No SMD magjack with confirmed integrated magnetics was found; the two SMD jacks above are unproven (the pages do not say). Fallback not needed, but for reference:

Fallback, discrete LAN transformer (16-pin-class SMD), plain jack not pursued because magjack qualifies:

| LCSC | MPN | Manufacturer | Mounting | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| C124001 | PT61017PEL | Bourns | SMD 12.8 x 6.9 mm | Economic and Standard | Extended | 1138 | 1.378 | 10/100 Base-T, 1CT:1CT, 350 uH; read |

H1102NL, HX1188NL, HR601680: not found in jlcsearch.

## 9. Tactile switches

| LCSC | MPN | Manufacturer | Mounting / orientation | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C318884** | TS-1187A-B-A-B | XKB Connection | SMD, top actuated, 5.1 x 5.1 mm | Economic and Standard | not stated on page | n/a (jlcsearch null; seen C318885 sibling 4431) | n/a | read |
| **C318941** | TS-1010-B-A | XKB Connection | SMD, side actuated (right angle), 4.7 x 1.9 mm | Economic and Standard | Extended | 11770 | 0.0459 | 1.6 N, 100k cycles, 12 V 50 mA; read |
| C2888449 | TSB001A3526A | BZCN | SMD, side actuated, 7.7 x 3.6 mm | Economic and Standard | Extended | 3665 | 0.0163 | 2.6 N; read |

## 10. SMD fuses (>= 32 V DC)

| LCSC | MPN | Manufacturer | Rating / size | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C163128** | CFS12V3T5R0 | TA-I Tech | 5 A, 1206 | Economic and Standard | Extended | 24248 | 0.0389 | 32 V, 50 A interrupt (jlcsearch); read |
| C2874921 | R12.000.5 | Reomax | 5 A, 1206 | Economic and Standard | Extended | 2782 | 0.0676 | 72 V (50 A @ 72 VDC); read |
| C553924 | S1206-F-5.0A | SART | 5 A, 1206 | Economic and Standard | not stated | 7796 | 0.0767 | 32 V, 35 A; read |
| **C72975** | 0452007.MRL | Littelfuse | 7 A, 2410 (nearest above 6.3 A found) | Economic and Standard | Extended | 2833 | 0.2921 | 60 V DC (72 V), 50 A; read |
| **C187598** | 046601.5NRHF | Littelfuse | 1.5 A, 1206 | Economic and Standard | Extended | 7811 | 0.0884 | 63 V, 50 A; read |
| C21261121 | 1206TD-1.5A | prosemi | 1.5 A, 1206 | Economic and Standard | Extended | 4265 | 0.1914 | 72 V (50 A @ 72 VDC); read |
| C183160 | S1206-S-1.0A | SART | 1 A, 1206 | Economic and Standard | Extended | 4936 | 0.0741 | 32 V; read |

6.3 A: no 6.3 A SMD fuse >= 32 V found in jlcsearch (the database search is fuzzy); the 7 A 2410 is the nearest and 5 A 1206 is the other option. 1808 size: nothing found.

## 11. Resettable PTC (SMD)

| LCSC | MPN | Manufacturer | Hold / size | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C20785** | SMD0603P020TF | RUILON | 0.2 A hold, 0603 | Economic and Standard | Extended | 3687 | 0.1167 | 9 V (jlcsearch); read |
| C883102 | BSMD0805-020-9V | BHFUSE | 0.2 A hold, 0805 | Economic and Standard | Extended | 18693 | 0.0492 | 9 V; read |
| **C2833485** | SMD0805-050-16V | TECHFUSE | 0.5 A hold, 0805 | Economic and Standard | Extended | 35052 | 0.0549 | 16 V, trip 1 A; read |
| C20789 | SMD0603P050TF | RUILON | 0.5 A hold, 0603 | Economic and Standard | Extended | 12695 | 0.1284 | 6 V; read |
| **C70119** | mSMD110-33V | TECHFUSE | 1.1 A hold, 1812 | Economic and Standard | Extended | 111466 | 0.0674 | 33 V, trip 2.2 A; read |
| C269128 | SMD1812B050TF/30 | Brightking | 0.5 A hold, 1812 | Economic and Standard | Extended | 43073 | 0.0464 | 30 V; read |

## 12. Aluminium electrolytic capacitors

SMD, >= 50 V, height <= 10.5 mm:

| LCSC | MPN | Manufacturer | Size / value | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C51953411** | RVT63V100M10X10 | jieerrui | 100 uF 63 V, D10 x 10.5 | Economic and Standard | Extended | 37353 | 0.1604 | 200 mA @120 Hz ripple; read |
| C2983550 | GVZ1H107M0810CNVC | HRK | 100 uF 50 V, D8 x 10.5 | Economic and Standard | Extended | 2812 | 0.0876 | 340 mOhm @100 kHz, 350 mA @100 kHz; read |
| **C970698** | RVT1H221M1010 | DMBJ | 220 uF 50 V, D10 x 10.2 | Economic and Standard | Extended | 28915 | 0.113 | 230 mA @120 Hz; read |
| C33129631 | EFVZ063ADA221M10B0 | FOLLON | 220 uF 63 V, D10 x 10.5 | Economic and Standard | Extended | 496 | 0.2418 | specs not in jlcsearch; read |

Not low-ESR in the strict sense except C2983550 (340 mOhm @100 kHz): no polymer/hybrid candidate found.

Through-hole radial, 50 V:

| LCSC | MPN | Manufacturer | Size / value | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C109393** | 50ZLH100MEFC8X11.5 | Rubycon | 100 uF, D8 x 11.5 | Economic and Standard | Extended | 64166 | 0.1243 | 362 mA @120 Hz; read |
| **C233093** | ECR1HBK221MLL100012 | Nantong Jianghai | 220 uF, D10 x 12.5 | Economic and Standard | Extended | 3700 | 0.0886 | read |
| C106560 | ERJ1HM221G16OT | AISHI | 220 uF, D10 x 16 | Economic and Standard | Extended | 106486 | 0.0938 | 53 mOhm @100 kHz, 1.65 A; read |
| **C3019919** | KM471M0501020PE1 | UNITED | 470 uF, D10 x 20 | Economic and Standard | Extended | n/a (WebSearch only) | ~0.085 | read; 470 uF needs D10 x 20 (does not fit 10 x 16) |
| C2873990 | KM1H471M1020 | ROQANG | 470 uF, D10 x 20 | Economic and Standard | Extended | n/a | n/a | read |

## 13. Shielded SMD power inductors

| LCSC | MPN | Manufacturer | Value / size | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C334252** | SWPA8065S220MT | Sunlord | 22 uH, 8 x 8 mm | Economic and Standard | Extended | 2582 | 0.2307 | jlcsearch lists 2.7 A and 4.3 A, 60 mOhm; which is Isat is not stated: check datasheet; read |
| C128694 | SMMS0630-220M | SXN | 22 uH, 7.1 x 6.6 mm (molded) | Economic and Standard | Extended | 136526 | 0.0838 | 3.5 A (type not stated), 135 mOhm; read |
| C51933841 | GSM0630-330-M | FAUKU | 33 uH, 7.4 x 6.6 mm | Economic and Standard | Extended | 36005 | 0.0892 | 2.1 A and 2.5 A (which is Isat not stated: 2.5 A only if it is Isat), 253 mOhm; read |
| C19268648 | CYA0850-33UH | SHOU HAN | 33 uH, 9.2 x 8 mm (molded) | Economic and Standard | Extended | 1708 | 0.4705 | 3 A / 6 A, size above 8 x 8; read |
| **C2926400** | YHNR4020-2R2M | YJYCOIN | 2.2 uH, 4 x 4 mm | Economic and Standard | Extended | 15622 | 0.1014 | 4 A / 6 A, 46 mOhm; read |
| C408335 | MWSA0402S-2R2MT | Sunlord | 2.2 uH, 4.4 x 4.2 mm | Economic and Standard | Extended | 6949 | 0.1526 | 4.5 A / 5 A, 58 mOhm; read |

SWPA6045S220MT, SWPA4030S2R2MT, SRN6045: not found in jlcsearch. 33uH within 8x8 and Isat >= 2.5 A confirmed: none (only C51933841 unverified, C19268648 oversize).

## 14. Ferrite bead 0603, 600 ohm

| LCSC | MPN | Manufacturer | Mounting | PCBA Type | Library | Stock | Price | Key specs |
|---|---|---|---|---|---|---|---|---|
| **C85833** | BLM18KG601SN1D | Murata | 0603 | Economic and Standard | Extended | 783416 | 0.0259 | 600 ohm @100 MHz, 1.3 A, 150 mOhm; read |
| C3717088 | BLM18DN601SZ1D | Murata | 0603 | Economic and Standard | Extended | 3798 | 0.3846 | 600 ohm, 700 mA, 435 mOhm; read |

BLM18PG601SN1D and GZ1608D601TF: not found in jlcsearch.

## Needs where nothing (fully) qualified

- 1 SMD VH header: none found.
- 2 B4B-XH-SM4-TB (SMD top XH) and any 4-pin SMD XH clone: none found. SMD side 4P JST version (C161861) qualifies.
- 3 SMD top-entry XH 2P: none found.
- 4 GH 3-pin JST originals (SM03B, BM03B) and 4-pin GH clones: no C-number found; 6/8-pin not verified.
- 5 PH: B3B-PH-K-S, 6P, S7B/B7B-PH-SM4-TB: no candidate verified.
- 7 KH-TYPE-C-16P, TYPE-C 16PIN 2MD(073), USB4105-GF-A: not found.
- 8 SMD magjack with confirmed integrated magnetics: none proven; H1102NL, HX1188NL, HR601680 not found.
- 10 6.3 A fuse: none exact; 1808 size none.
- 12 Polymer/hybrid low-ESR 100/220 uF >= 50 V: none found; 470 uF 50 V does not exist in 8x12/10x12.5/10x16 (needs 10x20).
- 13 33 uH, Isat >= 2.5 A, <= 8x8: not proven; SWPA6045S220MT, SWPA4030S2R2MT, SRN6045 not found.
- 14 BLM18PG601SN1D, GZ1608D601TF: not found (alternates qualify).
- Stock: jlcsearch gave no stock for most JST originals; check on JLC the day of the order (order gate item 4).
