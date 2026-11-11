# JLC check of every assembled part of Rev B, read 2026-11-11

Made by `jlc_read.py` from the BOM in `fab/jlc/`: PCBA Type from each part's page on jlcpcb.com, library type,
stock and price from JLC's parts API that day. One line marked Standard Only would move the whole order off
Economic PCBA: there is none. Basic and Preferred lines carry no loading fee; an Extended line costs $3.07.
Stock changes daily: **recheck every line on the day of the order** (order gate, point 4).

| LCSC | MFR part | Maker | Package | Qty per board | PCBA Type | Library | In stock | $ each | Used as |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C2500 | BAV99,215 | Nexperia | SOT-23 | 4 | Economic and Standard | Basic | 1 086 810 | 0.0111 | BAV99 |
| C4190 | 0603WAF2201T5E | UNI-ROYAL | 0603 | 10 | Economic and Standard | Basic | 4 845 271 | 0.0018 | 2.2k |
| C6186 | AMS1117-3.3 | Advanced Monolithic Systems | SOT-223 | 2 | Economic and Standard | Basic | 1 502 957 | 0.1938 | AMS1117-3.3 |
| C8598 | B5819W SL | Changjing | SOD-123 | 6 | Economic and Standard | Basic | 380 062 | 0.0262 | B5819W |
| C8678 | SS34 | MDD | SMA(DO-214AC) | 1 | Economic and Standard | Basic | 2 828 384 | 0.035 | SS34 |
| C13585 | CL31A106KBHNNNE | Samsung | 1206 | 1 | Economic and Standard | Basic | 3 533 442 | 0.1269 | 10 µF 50 V |
| C14663 | CC0603KRX7R9BB104 | YAGEO | 0603 | 16 | Economic and Standard | Basic | 35 654 549 | 0.0058 | 100 nF |
| C15850 | CL21A106KAYNNNE | Samsung | 0805 | 1 | Economic and Standard | Basic | 8 257 578 | 0.0314 | 10 µF 25 V |
| C16133 | TAJB107K006RNJ | (AVX part number; the page names no maker) | CASE-B-3528-21(mm) | 2 | Economic and Standard | Basic | 600 781 | 0.2513 | 100 µF 6.3 V |
| C20917 | AO3400A | Alpha & Omega | SOT-23 | 1 | Economic and Standard | Basic | 936 909 | 0.0801 | AO3400A |
| C21190 | 0603WAF1001T5E | UNI-ROYAL | 0603 | 4 | Economic and Standard | Basic | 26 227 038 | 0.0017 | 1k |
| C22775 | 0603WAF1000T5E | UNI-ROYAL | 0603 | 11 | Economic and Standard | Basic | 8 677 762 | 0.0021 | 100R |
| C22807 | 0603WAF1503T5E | UNI-ROYAL | 0603 | 1 | Economic and Standard | Basic | 692 953 | 0.0017 | 150k |
| C23140 | 0603WAF330JT5E | UNI-ROYAL | 0603 | 2 | Economic and Standard | Basic | 3 475 892 | 0.0024 | 33R |
| C23162 | 0603WAF4701T5E | UNI-ROYAL | 0603 | 12 | Economic and Standard | Basic | 14 985 025 | 0.0028 | 4.7k |
| C25803 | 0603WAF1003T5E | UNI-ROYAL | 0603 | 3 | Economic and Standard | Basic | 15 342 193 | 0.0029 | 100k |
| C25804 | 0603WAF1002T5E | UNI-ROYAL | 0603 | 13 | Economic and Standard | Basic | 43 968 405 | 0.0022 | 10k |
| C45783 | CL21A226MAQNNNE | Samsung | 0805 | 5 | Economic and Standard | Basic | 3 760 967 | 0.1055 | 22 µF |
| C57112 | 0603B103K500NT | FH | 0603 | 4 | Economic and Standard | Basic | 5 469 737 | 0.0103 | 10 nF |
| C130026 | TCA9548APWR | Texas Instruments | TSSOP-24 | 1 | Economic and Standard | Extended | 20 110 | 0.8206 | TCA9548A |
| C400894 | AOD4185 | Alpha & Omega | TO-252(DPAK) | 1 | Economic and Standard | Extended | 53 597 | 0.3724 | AOD4185 |
| C2892547 | KNTC0603/10KF3950 | KUU | 0603 | 1 | Economic and Standard | Extended | 106 141 | 0.03 | NTC 10k |
| C7420376 | SRV05-4 | hongjiacheng | SOT-23-6L | 5 | Economic and Standard | Preferred | 308 443 | 0.085 | SRV05-4 |
| C19077573 | SMBJ18A | hongjiacheng | DO-214AA(SMB) | 1 | Economic and Standard | Preferred | 14 795 | 0.0494 | SMBJ18A |

24 BOM lines: 19 Basic, 3 Extended, 2 Preferred. All are "Economic and Standard".
Lowest stock: no line has less than 200 times what one board needs.
