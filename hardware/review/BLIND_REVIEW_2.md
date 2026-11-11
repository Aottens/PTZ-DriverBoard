# Tweede blinde review PTZ-driverprint, Rev A

Datum: 2026-11-11. Reviewer: verse subagent, tweede blik na de wijzigingen op de eerste review.
Gelezen: `hardware/review/BRIEF.md`, `hardware/review/BLIND_REVIEW.md`, de ontwerpbestanden in `hardware/`
(schema, print, `fab/`), `fab/easyeda_cache.json`, de kopregels van `fab/make_jlc.py` en `fab/make_gerbers.sh`.
Niet gelezen: `hardware/review/HANDLED.md`, `DECISIONS.md`, `STATE.md`, `README.md`, `BACKLOG.md`,
`ARCHITECTURE.md`, `hardware/ASSEMBLY.md`, `hardware/README.md`, `hardware/BUILD_NOTES.md`, `hardware/sourcing/`,
`hardware/tools/`, `hardware/calc/`, `hardware/check_*.py`, `specs/`, `docs/`, `tests/`, commitberichten.
Niets in het ontwerp gewijzigd; al het werk stond in een tijdelijke map buiten de repository, op kopieën.
Om onbedoelde wijzigingen te vinden heb ik de print van vóór de wijzigingen (`git show 4efb315:hardware/ptz-driver.kicad_pcb`)
naast de huidige gelegd: alleen het bestand, geen berichten.
Ik kan niet meten: elke uitspraak is een telling of maat uit de bestanden, of een berekening met de invoer erbij.
Coördinaten zijn printmillimeters vanaf de linkerbovenhoek.

## Oordeel

**Bestellen.** Ik vond geen KRITIEKE en geen nieuwe BELANGRIJKE bevinding, en geen defect dat door de wijzigingen
is ontstaan: ERC 0, DRC 0 overtredingen, 0 niet-verbonden en 0 pariteitsfouten (ook na opnieuw vullen van de
vlakken), de opgeslagen vlakvullingen zijn gelijk aan een verse vulling, de Gerbers, boorbestanden en het
zip-bestand zijn op de datumregels na gelijk aan een verse export, en BOM en CPL kloppen met de 251 bestukte
footprints. Tussen de oude en de nieuwe print is geen enkele footprint verplaatst of gedraaid; koper is alleen
gewijzigd op de netten `+3V3`, `ETH_XO`, `ETH_XI`, `VM`, `GND` en `DIAG1_1`. Van de eerste review is B1 opgelost,
B2 voor het grootste deel (XI is nu direct, XO loopt nog 21,9 mm over drie lagen met drie via's), en B3, B4 en B5
zijn in de ontwerpbestanden ongewijzigd. Dat geeft drie voorwaarden die geen ontwerpwijziging zijn: de
kathodestreep van D102 in de JLC-preview controleren, en de rest van B2, B4 en B5 schriftelijk aanvaard hebben
(of dat gebeurd is kon ik niet nagaan, want die bestanden mocht ik niet lezen). De nieuwe bevindingen zijn alle
KLEIN; twee ervan (via tegen een 0402-pad bij R601 en C806) zijn het meenemen waard als er toch nog een
layoutronde komt, en zijn geen reden om er een te doen.

## A. Stand van de bevindingen uit de eerste review

| Nr | Stand | Bewijs uit de bestanden |
|---|---|---|
| **B1** 3,3 V-uitgang door één spoor en één via | **Opgelost** `[zeker]` | L102 pad 2 (23,85; 76,95) heeft vier F.Cu-sporen van 0,5 mm naar vier via's (0,6/0,3 mm): (21,90; 76,05) 2,15 mm, (22,75; 75,50) 1,82 mm, (22,65; 77,70) 1,41 mm, (25,00; 77,25) 1,19 mm. C112 pad 1 en C113 pad 1 hangen aan een balk van 0,5 mm op x = 21,90 (y 74,15 tot 76,95) met eigen via's op (21,75; 77,85) en (21,90; 74,15). Zes via's, was één. Alle zes liggen in het hoofdstuk van het `+3V3`-vlak op In2 en blijven daarin als ik alle halzen smaller dan 1,0 mm wegneem. De dichtstbijzijnde uitsparingen in het vlak zijn de GND-via's van C112 en C113 op 2,5 mm en de `I2C_SCL`-via (23,70; 71,85) op 2,9 mm; het dichtstbijzijnde In2-spoor ligt op 5,2 mm. Berekening: vier sporen parallel 0,38 mΩ (1 oz, 0,98 mΩ/mm bij 0,5 mm), vier via's parallel 0,33 mΩ (1,3 mΩ per via tot In2); bij 2 A samen 1,4 mV. Het gevraagde vlakje van 1 mm is het niet geworden, vier sporen van 0,5 mm zijn gelijkwaardig. |
| **B2** kristalsporen W5500 | **Deels opgelost** `[zeker]` (maten), `[vermoeden]` (restrisico) | **XI opgelost:** pin 30 → Y801 pad 1 is 2,65 mm F.Cu, geen via's; heel het net 6,12 mm F.Cu, 0 via's (was 8,1 mm F.Cu + 8,9 mm In2, twee via's). **XO korter, niet direct:** pin 31 → Y801 pad 3 is 21,9 mm: 5,0 mm F.Cu + 10,8 mm In2 + 6,1 mm B.Cu, drie via's op (19,30; 39,25), (19,95; 28,95), (24,25; 33,25); hemelsbreed is het 5,0 mm. Heel het net 32,4 mm (8,5 F.Cu, 17,8 In2, 6,1 B.Cu), vier via's (was 43,4 mm, zes via's; pad 36 mm, vijf via's). De tak naar R802 loopt 7,0 mm over In2 met via (25,60; 41,10). Afstand tot de 5 V-regelaar: `BUCK_SW` minstens 13,0 mm, `VIN_L` 3,7 mm, het `VIN`-spoor bij TP901 1,56 mm van via (19,95; 28,95). Op In2 loopt XO 6,15 mm parallel aan `SPI_MOSI` op 0,20 mm; het B.Cu-stuk kruist `SPI_SCK` en `SPI_MOSI` op In2 (0,21 mm prepreg ertussen) en ligt boven het stuk van In2 waar het `+3V3`-vlak in eilanden is gesneden. Onder het kristal ligt op F.Cu alleen nog GND en het eigen net; het `+3V3`-spoor dat in de vorige versie tussen de kristalpads door liep (x 23,85, y 34,65 tot 39,05) is weg. Geen GND-ring om XI/XO; de nieuwe `+3V3`-via (21,80; 39,95) staat op 0,15 tot 0,175 mm van het XI-spoor. Mijn inschatting van de rest: KLEIN. XO is de aangestuurde kant; geschatte strooicapaciteit XO ongeveer 6 pF tegen XI ongeveer 3 pF geeft (18+3)·(18+6)/(36+9) = 11,2 pF tegen 12 pF nominaal, dus enkele ppm tot ongeveer 10 ppm afwijking. |
| **B3** TVS D102 zonder gecontroleerde rotatie | **Ongewijzigd** `[zeker]` | `fab/jlc/ptz-driver_cpl.csv` regel 80: `D102,103.100mm,-121.700mm,Top,90.0`, de onbewerkte KiCad-hoek. `fab/easyeda_cache.json` heeft geen footprint voor C7470946; de EasyEDA-API antwoordde op 2026-11-11 nog steeds `404 Component not found`. Pad 1 (kathode, `VM`) ligt op (3,10; 23,85), pad 2 (`GND`) op (3,10; 19,55). Steun voor de hoek `[vermoeden]`: D103 (SMA, zelfde pad-1-is-kathode, zelfde KiCad-hoek 90°) past met CPL-hoek 90 binnen 0,15 mm op het EasyEDA-footprint. De controle in de JLC-preview blijft nodig: kathodestreep aan de zuidelijke pad, de kant van F101. |
| **B4** sensorpoorten alleen SPI-mode 0 en 1 | **Ongewijzigd in het ontwerp** `[zeker]` | U701 pin 1 en 19 = `CS_SNS_EN_N` = U202 pin 15; R311 (en R411, R511, R611) 100 kΩ van `SNSn_SCK` naar GND; op `SNS1_SCK` zitten alleen R307, J302 pin 3 en R311, dus geen plek voor een pull-up. Schemawijzigingen sinds de eerste review: alleen waarde en LCSC van R309, R409, R509, R609. |
| **B5** vier assen 1,5 A RMS thermisch krap | **Ongewijzigd in het ontwerp** `[zeker]` | Onder elke TMC5240 negen via's in de EP (U301: x 26,97 tot 29,03, y 11,02 tot 13,08), het vrijgehouden B.Cu-vlak, de VM/+3V3-splitsing op In2 op y 11,0 tot 11,5. Rond de drivers is alleen de breedte van `+3V3`-sporen gewijzigd. |
| **KLEIN 1** VS-ontkoppeling en elco's via het vlak | **Deels opgelost** `[zeker]` | **Elco's opgelost:** C101 heeft drie `VM`-via's op (52,15 / 53,10 / 54,85; 30,65) met sporen van 0,6 mm vanaf het midden van pad 1, en drie `GND`-via's op (60,55 / 61,50 / 62,40; 30,65); C102 idem op (69,15 / 70,10 / 71,00; 30,65) en (78,50 / 79,40 / 80,30; 30,65). Was één via per pad. De `VM`-via's liggen in het `VM`-vlak op In2, dat één stuk blijft tot ik halzen smaller dan 1,5 mm wegneem; de `GND`-via's liggen in de GND-vlakken op F.Cu, In1 en B.Cu. **100 nF aan de VS-pinnen ongewijzigd:** C301 via (23,20; 8,00), C302 via (33,35; 7,70), VS-pinnen via (25,90; 8,80), (28,10; 8,75), (30,80; 7,20): dezelfde coördinaten als in de eerste review, geen F.Cu-verbinding van condensator naar pin. |
| **KLEIN 5** kortsluiting op signaalpennen | **Deels opgelost** `[zeker]` | **Sensor-CS opgelost:** R309, R409, R509, R609 zijn `100R`, LCSC `C25076`, in het schema (vier bladen), op de print (veld `LCSC` van de footprint) en in de BOM (regel `100R`, negen stuks); ze zitten tussen `CS_SNSn` en `SNSn_CS`. Berekening: 3,3 V / (100 + 20 Ω) = 27,5 mA, onder de ±50 mA van de SN74LVC139A. **Ethernet-header ongewijzigd:** J801 pin 1 = `ETH_TCT` naast pin 2 = GND, R805 is 10 Ω in 0402 aan `3V3A` (0,33 A, 1,1 W bij een sluiting). |

## Nieuwe bevindingen

### KRITIEK

Geen.

### BELANGRIJK

Geen.

### KLEIN

1. **Via tegen een 0402-pad: C806 (nieuw) en R601 (bestond al)** `[zeker]` (maat), `[vermoeden]` (gevolg).
   - **Wat:** de nieuwe `+3V3`-via (21,80; 39,95) overlapt met zijn ring 0,06 mm de hoek van C806 pad 1
     (22,27; 40,30; 0,56 × 0,62 mm); de rand van het gat ligt 0,09 mm buiten het pad. Bij R601 pad 2 (GND) overlapt
     de via (77,20; 17,45) het pad 0,13 mm en ligt de gatrand 0,02 mm buiten het pad. Bij de drie andere assen staat
     dezelfde via 0,15 mm lager, op (26,20 / 43,20 / 60,20; 17,60), met 0,02 mm tussen ring en pad.
   - **Bewijs:** `ptz-driver.kicad_pcb`; via's zijn afgedekt (`tenting front yes, back yes`) en de maskeropening is
     gelijk aan het pad (`pad_to_mask_clearance 0`); de via's staan niet in `F_Mask.gts`.
   - **Gevolg:** bij een maskerverschuiving van 0,05 mm of meer komt bij R601 een deel van het gat in de
     padopening te liggen en kan soldeer in de via trekken: een magere las of een rechtopstaande 0402. R601 is de
     IREF-weerstand (12 kΩ) van as 4; los betekent geen stroominstelling op die as. Zichtbaar bij inspectie en met
     de bout te herstellen. Bij C806 is de marge groter.
   - **Fix:** via R601 naar (77,20; 17,60) zoals bij de andere assen; via C806 0,15 mm van het pad af. Daarna DRC
     en de fabricagebestanden opnieuw.
2. **Twee eilanden in het `+3V3`-vlak op In2 bij de W5500** `[zeker]`. De vulling bestaat uit drie stukken: het
   hoofdvlak (5398 mm²) en twee eilanden van 17 en 24 mm² tussen de sporen op x 19,5 tot 27,2, y 26,4 tot 40,3,
   met via's (20,75; 32,05) en (20,85; 33,15) in het ene en (22,35; 33,55) in het andere. Ze hangen aan het
   hoofdvlak via via (19,65; 30,95), die zelf op een strookje van 1,2 mm² met een hals tussen 0,2 en 0,3 mm ligt,
   en het B.Cu-spoor van 0,5 mm naar (20,75; 32,05). Deze keten voedde in de vorige versie de VDD-pin van de
   W5500; nu hangt er alleen R207 (10 kΩ) aan, en pin 28, C806 en C807 hangen direct aan via (21,80; 39,95) in het
   hoofdvlak. Onschadelijk. Opruimen kan: R207 direct aan het hoofdvlak, de drie overbodige via's weg.
3. **Losse spoorstompjes en overlappende segmenten** `[zeker]`. Drie F.Cu-stompjes eindigen nergens: `DIAG1_2`
   (48,65; 12,30)→(48,95; 12,40), `DIAG1_3` (65,65; 12,30)→(65,95; 12,40), elk 0,32 mm, en `CS_DRV1`
   (30,35; 55,90)→(29,85; 55,70), 0,54 mm. Op as 1 en 4 staat op die plek een via, op as 2 en 3 niet. Verder zeven
   segmenten met lengte nul en 31 segmenten die geheel op een ander segment van hetzelfde net liggen (onder
   andere `GND` (45,40; 25,1 tot 27,05) driemaal, `3V3A` (11,20; 40,55 tot 41,35) driemaal). Exact dubbele
   segmenten: 50 in de vorige versie, nu 0. Geen gevolg voor de werking; de DRC van KiCad meldt ze niet.
4. **BOM: vier LCSC-nummers op twee regels** `[zeker]`. C45783 (`22 µF` en `22 µF 25 V`), C1532 (`22 nF` en
   `22 nF 50 V`), C19702 (`10 µF` en `10 µF 10 V`) en C2286 (`LINK` en `ACT`) staan elk op twee regels omdat de
   waarde anders gespeld is: 84 regels voor 80 nummers. JLC kan bij het inlezen om samenvoegen vragen; de
   aantallen kloppen. Bestond al.
5. **GND-sporen naar de nieuwe via's bij de elco's zijn 0,2 mm** `[zeker]`, de `VM`-sporen 0,6 mm. Zonder gevolg:
   de GND-via's staan in het GND-vlak op F.Cu, dat het pad met thermische spaken van 0,3 mm bereikt.

## Wat ik heb gecontroleerd, in volgorde

1. **ERC en DRC, op een kopie.** `kicad-cli sch erc --severity-all`: 0 meldingen. `kicad-cli pcb drc
   --schematic-parity --severity-all`: 0 overtredingen, 0 niet-verbonden, 0 pariteitsfouten. Nogmaals met
   `--refill-zones --all-track-errors` en de acht genegeerde controles aangezet: 24× spoor niet midden op via
   (was 20; erbij onder meer drie korte `+3V3`-stukjes bij (28,95; 17,6) en `DIAG1_1` op B.Cu bij (31,95; 12,4)),
   2× thermische verbinding J201, 2× opdruk over de rand (J201), 2× opdruk over opdruk, 4× footprintfilter (PTC's).
   Geen afstand, kortsluiting of open verbinding.
2. **Vlakvullingen.** In het geheugen opnieuw gevuld en vergeleken met wat in het bestand staat: voor alle acht
   vullingen gelijk aantal stukken, oppervlak en hoekpunten (onder meer GND In1 één stuk 7432,8 mm², `+3V3` In2
   drie stukken 5439,2 mm², `VM` In2 één stuk 1415,4 mm²). De Gerbers bevatten dus geen verouderde vulling.
3. **Oud tegen nieuw.** 280 footprints, geen erbij of weg, geen verplaatst of gedraaid, alle pad-netten gelijk;
   alleen waarde en LCSC van R309, R409, R509, R609. Sporen 3890 → 3950, via's 607 → 617: erbij vijf `+3V3` bij de
   regelaar, één `+3V3` bij C806, één `ETH_XO`, vier `VM` en vier `GND` bij de elco's; weg twee `ETH_XI` en drie
   `ETH_XO`. Geometrie gewijzigd alleen op `+3V3`, `ETH_XO`, `ETH_XI`, `VM`, `GND` en `DIAG1_1` (twaalf B.Cu-segmenten
   weg: een tak van via (31,95; 12,40) naar (25,40; 8,35) die daar zonder via of pad eindigde, onder U301 door). Breedtes: `+3V3` op F.Cu nu 66,9 mm op 0,5 mm en 9,9 mm op 0,2 mm (bij de
   IC-pennen); `VM` 0,6 mm met halzen van 0,25 tot 0,3 mm bij de pennen; motoruitgangen 0,8 mm met halzen van
   0,25 mm.
4. **Afstanden van het gewijzigde koper** (290 sporen en via's tegen alle pads, sporen en via's van andere
   netten, per laag): kleinste afstand 0,15 tot 0,175 mm (via (21,80; 39,95) tot het XI-spoor), dan 0,175 tot
   0,2 mm (XO op In2 tot een `SPI_MOSI`-via), alle andere 0,2 mm of meer. Nieuwe via's: gatwand tot gatwand minstens
   0,6 mm. Dichtste spoor of via bij de printrand: 0,55 mm (GND-via's), als in de eerste review.
5. **De drie gewijzigde gebieden in beeld** (eigen SVG uit de printgegevens, per laag gekleurd, naar PNG): de
   3,3 V-uitgang, het kristal met de W5500-pennen 27 tot 33, en beide elco's. Geen koper van een ander net tussen
   de nieuwe via's en hun pads, geen spoor onder het kristal op F.Cu, geen snede in In2 rond de nieuwe
   `+3V3`-via's. De nieuwe GND-via's bij de elco's maken met de bestaande een gleuf van ongeveer 2,8 mm in het
   `+3V3`-vlak op In2, de `VM`-via's een van ongeveer 2,7 mm in GND op In1: te klein om iets af te snijden.
6. **Via's bij pads.** Geen via met het gat in een SMD-pad behalve de 4 × 9 in de EP's van de drivers. Twee via's
   overlappen een pad van hetzelfde net (KLEIN 1). Alle via's afgedekt; steekproef van vijf nieuwe via's staat in
   `F_Cu.gtl` en `PTH.drl` en niet in de maskerbestanden.
7. **Vlakken op halzen.** `+3V3` op In2: als ik halzen smaller dan 1,0 mm wegneem blijft een hoofdstuk van
   4750 mm² over met 37 van de 56 via's, waaronder alle zes van de regelaar; de overige via's hangen aan
   pull-ups en ontkoppelcondensatoren op korte uitlopers. Per `+3V3`-pad het spoor tot de eerste via nagelopen:
   langste 2,86 mm (pin 5 van U301, U401, U501, met 0,2 mm bij de pen). `VM` op In2: één stuk tot halzen van
   1,5 mm.
8. **Gerbers en boorbestanden.** Verse export met de opdrachten uit `fab/make_gerbers.sh`: alle 15 bestanden
   verschillen alleen in de datumregels (2 of 4 regels per bestand). Het zip-bestand bevat dezelfde 15 bestanden,
   byte voor byte gelijk aan de map. `PTH.drl`: 595 × 0,3 mm en 22 × 0,4 mm = 617, gelijk aan het aantal via's, plus
   16 × 0,95, 2 × 1,0, 2 × 1,7 mm en vier sleuven van 0,6 mm (USB-C). `NPTH.drl`: 4 × 3,2 en 2 × 0,65 mm.
9. **BOM en CPL.** 251 footprints met een LCSC-veld, 251 CPL-regels, 251 aanduidingen in de BOM (84 regels);
   de drie verzamelingen zijn gelijk. Voor alle 251: LCSC, waarde en footprintnaam in de BOM gelijk aan de velden
   op de print. Zonder LCSC en buiten BOM en CPL: 4 montagegaten, 3 soldeerbruggen, 22 testpunten. Alle footprints
   op F.Cu, alle CPL-regels `Top`. Rotatie en positie: voor 250 onderdelen de pads van het EasyEDA-footprint met
   de CPL-hoek om het CPL-midden gedraaid en per padnummer met de print vergeleken: grootste afwijking 0,30 mm
   (C101, C102), en 3 tot 15 mm als ik het onderdeel 180° verdraai, dus de toets onderscheidt. Uitzondering D102
   (B3). In die 250 zitten alle IC's (U101, U102, U201 tot U205, U301 tot U601, U701 tot U703, U801 tot U803) en
   alle polaire onderdelen (C101, C102, D101, D103 tot D105, D201, D301 tot D601, D801 tot D803, D901, Q101, Q901
   tot Q903, Y801). Het CPL-bestand is sinds de eerste review niet gewijzigd en geen footprint is verplaatst,
   dus dat klopt met elkaar.

   | Onderdeel | KiCad-hoek | CPL-hoek | Afwijking pads |
   |---|---|---|---|
   | U301, U401, U501, U601 (TMC5240) | 90 | 0 | 0,03 mm |
   | U201 (ESP32-C6-MINI-1U) | 0 | 0 | 0,10 mm |
   | U801 (W5500) | 0 | 270 | 0,09 mm |
   | U101 (TPS54360) | 0 | 270 | 0,01 mm (pennen 1 tot 8) |
   | U102 (TLV62569) | 0 | 180 | 0,20 mm |
   | U202, U203, U204, U205 | 0 | 270 | 0,00 tot 0,16 mm |
   | U701, U702, U703 | 0 | 270 | 0,01 tot 0,06 mm |
   | U802, U803 | 0 | 270 | 0,23 en 0,13 mm |
   | Q101 (AOD4185) | 90 | 270 | 0,00 mm |
   | Q901, Q902 / Q903 (AO3422) | 90 / −90 | 270 / 90 | 0,28 mm |
   | C101, C102 (220 µF) | 0 | 0 | 0,30 mm |
   | D101, D104, D105, D901 (SOD-123) | 0, 90, 0, 0 | 0, 90, 0, 0 | 0,04 tot 0,05 mm |
   | D103 (SS36) | 90 | 90 | 0,15 mm |
   | D102 (SMBJ24A) | 90 | 90,0 | geen referentie |
   | D201 (RGB-LED) | 0 | 0 | 0,00 mm |
   | D301, D401, D501, D601 (BAT54S) / D801 (SM712) | 90 / −90 | 270 / 90 | 0,08 mm |
   | D802 / D803 (LED 0603) | 180 / 0 | 0 / 180 | 0,04 mm |
   | Y801 (kristal) | 0 | 0 | 0,00 mm |
   | L101 / L102 | 0 / 180 | 0 / 0 | 0,12 / 0,18 mm |
10. **Verder gezocht naar wat de eerste review miste:** stroompad en thermische spaken van de hoogstroompads
    (J101 in volle verbinding met `VIN_RAW` op F.Cu en met GND op In1), halzen in het `VM`-vlak tussen de ingang
    en de drivers, de boortabel, en de punten onder KLEIN hierboven. Geen pin-voor-pin-controle van ongewijzigde
    onderdelen herhaald.

## Wat ik niet kon controleren

- De JLC-preview: de kathode van D102, de pinvolgorde van de RGB-LED en de polariteit van de 0603-LED's zoals
  JLC ze tekent. De toets op het EasyEDA-footprint rust op padnummers, niet op wat JLC als pen 1 tekent.
- Of de rest van B2 en B4 en B5 schriftelijk zijn aanvaard: die bestanden mocht ik niet lezen.
- De voorraad bij JLC op de dag van de bestelling; niet opnieuw opgehaald. Er is geen nieuw artikelnummer
  bijgekomen (C25076 stond al in de BOM).
- De TMC5240-pinnen tegen de datasheet: die datasheet staat niet in `hardware/datasheets/`, en de eerste review
  heeft dit pin voor pin gedaan; ik heb het niet herhaald.
- Alles wat een meting vraagt: de oscillator van de W5500 en de Ethernet-link, rimpel op 3,3 V, opwarming van
  de drivers, het solderen van R601 en C806.
- De passing in de voet met motor, stekkers en kabels.
