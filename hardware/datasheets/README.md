# Datasheets used for Rev A

The PDFs are not in the repository: they are the makers' and this repository is public. Fetch them from the links
into this folder when you need them (`*.pdf` and `*.txt` here are ignored by git). "Read" means the pin table and the
limits were taken from that revision.

| Part | Revision read | Source | How it loads |
| --- | --- | --- | --- |
| TMC5240ATJ | 19-101625C, Rev 1, 4/24 | https://www.analog.com/media/en/technical-documentation/data-sheets/tmc5240.pdf | Built-in browser only; curl and WebFetch are refused |
| ESP32-C6-MINI-1U | v1.5 | https://www.espressif.com/sites/default/files/documentation/esp32-c6-mini-1_mini-1u_datasheet_en.pdf | curl |
| W5500 | v1.1.0 | https://docs.wiznet.io/img/products/w5500/W5500_ds_v110e.pdf | curl |
| W5500 reference schematic, jack with magnetics | 2015-09-25 | https://docs.wiznet.io/img/products/w5500/w5500_sch_v110_use_mag_.pdf | curl |
| TPS54360 | SLVSBB4G, June 2018 | https://www.ti.com/lit/ds/symlink/tps54360.pdf | curl |
| TLV62569 | revised October 2017 | https://www.ti.com/lit/ds/symlink/tlv62569.pdf | curl |
| SN74LVC139A | SCAS341O, February 2005 | https://www.ti.com/lit/ds/symlink/sn74lvc139a.pdf | curl |
| SN74LVC125A | SCAS290T, September 2024 | https://www.ti.com/lit/ds/symlink/sn74lvc125a.pdf | curl |
| SN74LVC244A | SCAS414AG, June 2026 | https://www.ti.com/lit/ds/symlink/sn74lvc244a.pdf | curl |
| SN74AHCT244 | SCLS228O, July 2024 | https://www.ti.com/lit/ds/symlink/sn74ahct244.pdf | curl |
| TMP1075 | SBOS854F, June 2024 | https://www.ti.com/lit/ds/symlink/tmp1075.pdf | curl |
| PCAL6416A | Rev 7.1, 30 August 2022 | https://www.nxp.com/docs/en/data-sheet/PCAL6416A.pdf | curl |
| SN65HVD230 | SLOS346O, April 2018 | https://www.ti.com/lit/ds/symlink/sn65hvd230.pdf | curl |
| SP3485 | MaxLinear, undated in the text | https://www.maxlinear.com/ds/sp3485.pdf | curl |
| AOD4185 | Rev 4.2, June 2024 | https://aosmd.com/res/data_sheets/AOD4185.pdf | curl |
| AO3422 | Rev 2.1, March 2024 | https://aosmd.com/res/data_sheets/AO3422.pdf | curl |

## Not read from the maker

For these the maker's sheet did not load; what the design uses instead is named. Each is a point for the JLC preview
or the bring-up checklist, and none can damage the board if it is wrong.

| Part | What is used | Source of it |
| --- | --- | --- |
| Everlight 19-237 RGB LED (C60105) | Pin order: 1 red, 2 green, 3 blue cathode, 4 common anode | JLC's own library part, read through the EasyEDA API |
| Littelfuse 0452007.MRL (C72975) | Melting I²t about 124 A²s | A distributor listing; JLC's page gives 7 A, 60 V DC, 50 A breaking |
| 220 µF 50 V electrolytic (C970698) | ESR about 0.3 Ω | An assumption for a general-purpose 10 × 10 mm part, used in `calc/power.py` |
| USBLC6-2SC6, SM712, BAT54S, B5819W, SMBJ24A, SS36, zener | Standard pin order of the package | The specs state it; JLC's part page confirms type and package |
| JST connectors | Pin 1 as in KiCad's footprints | KiCad library, which follows the JST drawings |
| 25 MHz crystal X322525MOB4SI (C9006) | 12 pF load, pads 1 and 3 the crystal | JLC's part page (12 pF, ±10 ppm) |
