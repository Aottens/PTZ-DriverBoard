# Blinde review PTZ-driverprint, Rev A

Datum: 2026-11-10/11. Reviewer: verse subagent, alleen `hardware/review/BRIEF.md`, de ontwerpbestanden en de
datasheets. Niet gelezen: `specs/`, `DECISIONS.md`, `hardware/BUILD_NOTES.md`, `hardware/tools/`, `hardware/calc/`,
`hardware/check_*.py`, `docs/`, git-historie, `STATE.md`, `README.md`, `ARCHITECTURE.md`, `hardware/ASSEMBLY.md`,
`hardware/sourcing/`. Niets in het ontwerp gewijzigd; al het werk stond in een tijdelijke map buiten de repository.
Ik kan niet meten: elke uitspraak hieronder is een netlijst-, bestand- of datasheetcontrole of een berekening.

## Oordeel

**Bestellen na fixes.** Het schema klopt pin voor pin met de datasheets: ik vond in de netlijst geen enkele
verkeerd aangesloten pin op de vier TMC5240, de ESP32-C6-MINI-1U, de W5500, de twee regelaars, de
ompoolbeveiliging, de transceivers, de buffers, de decoder, de expander of de USB-C-connector, en de waarden van
de delers, IREF, de laadpomp en het kristal kloppen met de formules. ERC, DRC en schema-pariteit zijn schoon, de
Gerbers zijn bit voor bit gelijk aan een verse export van de print, en alle 80 LCSC-nummers waren op 2026-11-10 op
voorraad bij JLC en toegestaan voor Economic PCBA. Geen bevinding is KRITIEK. Wel zijn er vijf BELANGRIJKE punten
die vóór de bestelling een kleine layoutwijziging of een schriftelijke aanvaarding vragen: de hele 3,3 V-voeding
loopt door één spoor van 0,2 mm en één via, het kristalspoor XO van de W5500 is 36 mm lang met vijf via's en loopt
langs de 5 V-regelaar, de TVS D102 heeft als enige polaire component geen gecontroleerde plaatsingsrotatie, de
sensorpoorten werken door de gedeelde strobe alleen betrouwbaar met SPI-modes 0 en 1, en vier assen op 1,5 A RMS
continu is thermisch krap.

## KRITIEK

Geen.

## BELANGRIJK

### B1. De hele +3V3-uitgang loopt door één spoor van 0,2 mm en één via `[zeker]`

- **Wat:** de uitgang van de 3,3 V-regelaar (L102 pad 2) is alleen verbonden via één F.Cu-spoor van 0,2 mm breed en
  2,15 mm lang naar één via (boor 0,3 mm) op (21,90; 76,05), en die via is de enige verbinding met het +3V3-vlak op
  In2. De uitgangscondensatoren C112 en C113 hangen met elk een spoor van 0,2 × 0,9 mm aan dezelfde via.
- **Bewijs:** `ptz-driver.kicad_pcb`, net `+3V3` rond L102: sporen (23,85; 76,95)→(21,90; 76,05),
  (21,90; 75,05)→(21,90; 76,05), (21,90; 76,95)→(21,90; 76,05), alle 0,2 mm; één via; geen +3V3-zone op F.Cu.
  Berekening: R = 1,72e-8 × 2,15e-3 / (0,2e-3 × 35e-6) = 5,3 mΩ; bij 1 A is dat 5 mV en 5 mW, elektrisch dus geen
  probleem. IPC-2221 geeft voor 0,2 mm buitenlaag 1 oz ongeveer 0,7 A bij 10 °C opwarming; de TLV62569 kan 2 A
  leveren (datasheet, 2 A-uitvoering) en bij een kortsluiting op een 3V3-poort loopt die stroom tot de PTC afschakelt.
- **Gevolg:** de berekening laat zien dat het bij de verwachte last (ongeveer 0,3 A gemiddeld, 0,6 A piek) werkt,
  maar alle logica hangt aan één via en één dun spoor; de rimpelstroom van de regelaar loopt door dezelfde dunne
  sporen naar de uitgangscondensatoren.
- **Fix:** een vlakje of spoor van minstens 1 mm van L102.2 naar C112/C113 en drie tot vier via's naar In2.

### B2. Kristalspoor XO van de W5500: 36 mm, vijf via's, langs de 5 V-regelaar `[zeker]` (maat), `[vermoeden]` (gevolg)

- **Wat:** pin 31 (XO) van U801 ligt 5,0 mm van kristalpad Y801.3, maar het spoor loopt van de pin onder het IC
  door over In2 naar het noorden tot (18,75; 26,55), en komt dan diagonaal over F.Cu terug via C811 naar het kristal.
  Ook R802 en C810 hangen via een omweg over In2 aan het kristal.
- **Bewijs:** net `ETH_XO`: 22,8 mm F.Cu + 17,9 mm In2 + 2,7 mm B.Cu, zes via's; het pad pin→kristal is ongeveer
  36 mm met vijf via's op (19,30; 39,25), (18,60; 33,90), (19,95; 28,95), (18,75; 26,55), (21,65; 27,05). Het
  F.Cu-stuk (21,65; 27,05)→(27,50; 32,90) loopt op ongeveer 3 mm van de ingangscondensatoren C103/C104 van de
  TPS54360 en begint op ongeveer 2 mm van TP901 (VIN) en F102. Net `ETH_XI`: 8,1 mm F.Cu + 8,9 mm In2, twee via's.
- **Gevolg:** de belastingscapaciteit blijft volgens de berekening in orde (kristal C9006 is 12 pF volgens JLC;
  (18+8)·(18+4,5)/(26+22,5) ≈ 12,1 pF met geschatte strooicapaciteit). Het risico is ingekoppelde schakelruis van
  de 443 kHz-regelaar op het hoogohmige oscillatorknooppunt en uitstraling van een 25 MHz-spoor over drie lagen:
  jitter op de PHY-klok, mogelijk een instabiele Ethernet-link.
- **Fix:** XO en XI direct op F.Cu van pin naar kristal, C810/C811/R802 er direct naast, geen via's, GND eromheen.

### B3. TVS D102 heeft geen gecontroleerde plaatsingsrotatie `[zeker]`

- **Wat:** voor elk onderdeel in de CPL kon ik de rotatie narekenen tegen het EasyEDA-footprint dat JLC gebruikt
  (`fab/easyeda_cache.json`): pad voor pad landen alle onderdelen binnen 0,3 mm (zie de controlelijst onderaan).
  D102 (SMBJ24A, C7470946) is de enige uitzondering: er is geen EasyEDA-footprint voor (de EasyEDA-API antwoordt
  `success: false`, de cache heeft geen ingang) en de CPL-regel bevat de onbewerkte KiCad-hoek (`90.0`).
- **Bewijs:** `fab/jlc/ptz-driver_cpl.csv`: `D102,103.100mm,-121.700mm,Top,90.0`; op de print ligt pad 1 (kathode,
  VM) op (3,10; 23,85) en pad 2 (anode, GND) op (3,10; 19,55).
- **Gevolg:** als JLC's bibliotheek het onderdeel 180° anders definieert, staat de TVS in doorlaat over VM: de
  print start niet en de zekering of de stroombegrenzing spreekt aan. De begrensde eerste inschakeling vangt dit,
  maar het kost handmatig omsolderen van een SMB.
- **Fix:** in de JLC-preview de kathodestreep van D102 controleren (moet aan de kant van F101/TP "VM" liggen, de
  zuidelijke pad), en dat als regel in de checklist van de bestelling opnemen; of een SMBJ24A-nummer kiezen dat wel
  een EasyEDA-footprint heeft.

### B4. Sensorpoorten: alleen SPI-mode 0 en 1 zijn betrouwbaar `[zeker]` (mechanisme), afhankelijk van de sensorkeuze

- **Wat:** de strobe `CS_SNS_EN_N` (GPIO1) zet tegelijk de buffer U701 (SCK/MOSI naar de kabels, pin 1 en 19) aan
  én laat de decoder U202 één `CS_SNSn` laag worden. De kabelkant van SCK wordt in rust door 100 kΩ (R311 enz.) naar
  GND getrokken.
- **Bewijs:** netlijst: U701.1/U701.19 = `CS_SNS_EN_N` = U202.15 (2G); R311/R312 100 kΩ naar GND op `SNSn_SCK` en
  `SNSn_MOSI`.
- **Gevolg:** bij een sensor met CPOL = 1 (SPI-mode 2 of 3, bijvoorbeeld MT6835) springt SCK aan de kabel van 0 naar
  3,3 V op hetzelfde moment dat CS laag wordt (beide enkele nanoseconden na dezelfde flank). De sensor kan dat als
  een extra klokflank zien en het frame een bit verschuiven. Firmware kan dit niet oplossen, omdat één pin beide
  doet. Met CPOL = 0 (mode 0 of 1, bijvoorbeeld AS5047/AS5048A) is er geen flank en is het ontwerp in orde.
- **Fix:** aanvaarden en vastleggen dat de poort alleen CPOL = 0-sensoren ondersteunt, of per poort een niet-bestukte
  pull-up naast R311 voorzien zodat SCK in rust hoog kan liggen, of de buffer met een eigen pin vrijgeven.

### B5. Vier assen op 1,5 A RMS continu is thermisch krap `[vermoeden]` (berekening, niet gemeten)

- **Wat en berekening:** TMC5240-datasheet p. 11: R_ON laag 0,11 Ω + hoog 0,12 Ω typisch (bereik 3 A), p. 166:
  ongeveer +50 % bij 100 °C opwarming; p. 10: θJA 29 °C/W op een JEDEC-vierlaagsprint. P per driver ≈
  2 × 1,5² × 0,23 = 1,04 W koud, ≈ 1,5 W warm, plus ruststroom 24 V × 5 mA = 0,12 W en schakelverlies. Voor één
  driver is dat 35 tot 50 °C boven de print. Vier drivers op 17 mm steek geven 6 tot 7 W op een print van
  100 × 80 mm in een gesloten voet naast een motor; met een ruwe 10 W/m²K over beide zijden warmt de print zelf
  ongeveer 40 °C op. De berekening komt zo op een junctietemperatuur van 100 tot 125 °C, onder de afschakelgrens
  van 165 °C maar rond de voorwaarschuwing.
- **Bewijs layout:** onder elke driver negen via's in de EP naar In1 en een vrijgehouden GND-vlak op B.Cu; dat is
  goed. De VM/+3V3-splitsing op In2 loopt op y = 11,0 tot 11,5 mm precies onder de drivers door.
- **Gevolg:** bij continu vollast op alle assen mogelijk thermische voorwaarschuwing of afschakeling.
- **Fix:** aanvaarden met stilstandsstroomverlaging in firmware en de ventilatoruitgang, en de temperatuur als punt
  in de inbedrijfstellingschecklist opnemen; extra koper is niet nodig om te bestellen.

## KLEIN

1. **VS-ontkoppeling loopt via het vlak** `[zeker]`. Geen van de 100 nF-condensatoren (C301/C302 enz.) is op F.Cu
   met een VS-pin verbonden; elke condensator en elke VS-pin(groep) heeft een eigen via naar het VM-vlak op In2
   (U301: via's (25,9; 8,8), (28,1; 8,75), (30,8; 7,2); C301 via (23,2; 8,0), C302 via (33,35; 7,7)). Afstanden 3,2
   tot 3,8 mm. De 10 µF (C303) zit 12 mm verder aan één via. Werkt naar verwachting; korter is beter (datasheet
   p. 16: "shortest loop"). De 220 µF-elco's C101/C102 hangen elk aan één via (0,3 mm) en een hals van 2,0 mm breed
   en 15 mm lang op In2 (0,5 oz): berekend 7,6 mΩ + 1,3 mΩ, verwaarloosbaar naast de ESR, maar twee tot drie via's
   erbij kost niets.
2. **Marge TVS tot 41 V** `[zeker]`. SMBJ24A (JLC-pagina C7470946): doorslag vanaf 26,7 V, klem 38,9 V bij 15,4 A.
   Absoluut maximum VS is 41 V (datasheet p. 10): marge 2,1 V bij de volle piekstroom, ongeveer 8 V bij 5 A
   (lineair geschat). De marge is echt, maar een voeding die boven 26 V is afgeregeld laat de TVS continu geleiden.
3. **5 V-regelaar** `[zeker]`. Geen thermische via's onder de PowerPAD van U101 (twee GND-via's op 1,9 mm ernaast);
   de lus ingangscondensator–VIN–SW–D103–GND is ongeveer 10 × 8 mm en sluit via het GND-vlak. Bij de lage 5 V-last
   aanvaardbaar. Berekend: Vout = 0,8 × (1 + 52,1/10) = 4,97 V; fsw = 443 kHz (RT 220 kΩ); UVLO aan 9,2 V, uit 8,1 V;
   compensatie 4,7 kΩ/22 nF/100 pF past bij de datasheetformules voor 22 µF effectief.
4. **USB wint van de 5 V-rail** `[zeker]`. VSYS wordt gevoed via D104 (+5V = 4,97 V) en D105 (VBUS, typisch 5,0 tot
   5,2 V). Met USB ingeplugd levert de host dus de logica (berekend 0,25 A gemiddeld, tot 0,5 A piek). Terugvoeden
   naar de host kan niet (D105). Wie dat niet wil, zet de 5 V-rail op ongeveer 5,2 V.
5. **Kortsluiting op signaalpennen** `[zeker]`. Sensor-CS: de decoderuitgang staat in rust hoog en heeft alleen
   33 Ω in serie; kortgesloten naar GND loopt ongeveer 60 mA (3,3 V over 33 Ω plus een geschatte
   uitgangsweerstand van 20 Ω), boven de ±50 mA continu van de SN74LVC139A (datasheet, absolute maxima). 100 Ω voor R309/R409/R509/R609 lost dit op. Ethernet-header J801: pen 1 (TCT, via
   10 Ω aan 3V3A) ligt naast pen 2 (GND); een sluiting geeft 0,33 A en 1,1 W in R805 (0402). Dit volgt het
   WIZnet-referentieschema, maar is hier een kabel.
6. **Sensorvoeding** `[zeker]`. Eén PTC (F701, 200 mA, 0,55 tot 3,5 Ω volgens JLC) voedt alle vier poorten: bij
   80 mA tot 0,28 V spanningsval, en één kortgesloten poort neemt alle sensoren mee. Tot de PTC afschakelt kan de
   3,3 V-rail inzakken `[vermoeden]`.
7. **GPIO4/GPIO5 zweven tijdens reset** `[zeker]` aan de decoderingangen (U202 pin 2/3/13/14); de strobes zijn hoog,
   dus er wordt niets geselecteerd. Twee pull-downs voorkomen zwevende CMOS-ingangen.
8. **Geen ESD-klemmen** `[zeker]` op de SPI-lijnen van de sensorkabels (alleen 33/100 Ω), op CAN, op de I2C-poort, op
   de camera-uitgangen en op BOOT. HOME is wel beschermd (10 kΩ pull-up, 22 kΩ, BAT54S, 1 nF; bij 24 V op de pen
   ongeveer 3 mA in de 3,3 V-rail).
9. **Fysiek** `[zeker]` (maten), `[vermoeden]` (gevolg). Geen van beide lange randen is vrij van connectoren:
   boven J101 en J301 tot J601 op 0,5 mm van de rand, onder J902 op 0,6 mm, J803 op 1,7 mm en de knop SW201 op
   0,7 mm. Alle zijn verticaal, dus insteken van boven kan, maar vingerruimte naast de motor is niet gecontroleerd.
   R210 en TP912 liggen op 3,9 en 5,0 mm van het hart van H3 (kop M3 tot 3 mm straal).
10. **Testpunten en opdruk** `[zeker]`. Geen testpunt op 3V3A, +3V3_SNS, +5V_EXT en VBUS. Geen
    referentieaanduidingen voor passieve onderdelen op de opdruk. Tekst van 0,8 mm hoog is voor JLC aan de kleine
    kant. Ventilator- en sensorpoorten hebben hun polariteit en spanning alleen in de legenda op de achterkant.
11. **Routering van bussen** `[zeker]`. USB D+ 47,7 mm en D− 29,0 mm, elk vier via's, niet als paar; voor full-speed
    (12 Mbit/s) is 19 mm verschil ongeveer 0,13 ns en dus onschadelijk. SPI_SCK is 151 mm over drie lagen met tien
    via's en vertakkingen: met een lage klok beginnen. Op In2 lopen sporen van 23 netten door het +3V3-vlak
    (FAN_PWM 72 mm, DIAG-lijnen, SPI); het GND-vlak op In1 is ononderbroken.
12. **DRC-instellingen** `[zeker]`. Acht controles staan in het project op negeren. Met die controles aan (op een
    kopie): 20× spoor niet midden op via (GND-stubs bij de drivers), 2× onvolledige thermische verbinding (schild
    J201, onschadelijk), 2× opdruk over de rand (J201), 2× opdruk over opdruk, 4× footprintfilter (PTC's). Niets
    daarvan raakt de werking.
13. **Fabricage** `[zeker]` (gegevens), `[vermoeden]` (advies). HASL op QFN/LQFP met 0,5 mm steek en de LGA-module
    kan, ENIG is vlakker. JLC markeert de ESP32-module voor röntgeninspectie (meerkosten). PCAL6416APW had 296 stuks
    voorraad, de laagste van de lijst.
14. **LED** `[vermoeden]`. Groen en blauw aan 3,3 V met 220 Ω branden zwak (doorlaatspanning rond 3 V).
15. **Zekering F101** `[zeker]`. Onderbreekvermogen 50 A (JLC-pagina): voldoende voor een begrensde voeding, niet
    voor een accu.

## Wat ik heb gecontroleerd, in volgorde

1. **ERC en DRC.** `kicad-cli sch erc`: 0 meldingen op alle tien bladen. `kicad-cli pcb drc --schematic-parity
   --severity-all`: 0 overtredingen, 0 niet-verbonden, 0 pariteitsfouten. Daarna op een kopie met de genegeerde
   controles aan (zie KLEIN 12).
2. **Netlijst** (`sch export netlist`, 280 onderdelen), pin → net tegen de datasheet:
   - **TMC5240ATJ ×4** (datasheet analog.com, 169 pagina's, opgehaald via de ingebouwde browser; p. 15 tot 18 en
     10 tot 12): alle 32 pennen en EP kloppen. IREF 12 kΩ (bereik 12 tot 60 kΩ; K_IFS 36 → 3,0 A piek, dus 1,5 A RMS
     = 2,12 A piek is haalbaar), VDD1V8 4,7 µF (≥ 2,2), CPI–CPO 22 nF 50 V, VCP–VS 1 µF 50 V, SLEEPN via 100 kΩ aan
     VS (hoogspanningspen, pull-down 0,8 tot 1,5 MΩ, V_IH 0,9 V), CLK/UART_EN/ENC/REFR/AIN aan GND, OV open. De vier
     assen zijn in de netlijst identiek.
   - **ESP32-C6-MINI-1U** (datasheet v1.5, pentabel en hoofdstuk 4): alle pennen kloppen met `pins.h` (22 GPIO's,
     USB D− op IO12, D+ op IO13, UART0 op IO16/17, FSPI op IO6/7/2). Strappings: GPIO9 10 kΩ omhoog met knop, GPIO8
     hoog via de I2C-pull-up, GPIO15 laag via 100 kΩ (genegeerd bij standaard-eFuses), GPIO4/5 zwevend. EN 10 kΩ/1 µF.
     Antenneconnector is W.FL/MHF III, zoals de opdruk zegt.
   - **W5500** (datasheet v1.1.0 en het referentieschema met magnetics): alle 48 pennen; pen 23 aan GND, 38 tot 42
     open (toegestaan), EXRES1 12,4 kΩ 1 %, TOCAP 4,7 µF, 1V2O 10 nF, PMODE hoog, analoge voorkant gelijk aan de
     referentie (49,9 Ω aan 3V3A, TCT via 10 Ω en 22 nF, 6,8 nF in serie, RCT aan het knooppunt met 10 nF), MISO
     hoogohmig bij SCSn hoog.
   - **TPS54360** (SLVSBB4G), **TLV62569DBV**: pennen en formules (zie KLEIN 3; 3,3 V = 0,6 × (1 + 100/22) = 3,33 V).
   - **Ompoling en zekeringen:** AOD4185 G/D/S = pen 1/tab/3, drain aan de ingang, zener 12 V over gate-source,
     100 kΩ naar GND; V_DS −40 V tegen −24 V omgepoold; inschakel-I²t ½·440 µF·24²/0,25 Ω ≈ 0,5 A²s tegen 124 A²s
     smelt-I²t (waarde uit `datasheets/README.md`, niet zelf nagelezen). F101 7 A voor de motoren, F102 1,5 A/63 V
     voor de logica.
   - **SP3485**, **SN65HVD230**, **SN74LVC139A**, **SN74LVC244A**, **SN74LVC125A**, **SN74AHCT244**, **PCAL6416A**
     (0x20), **TMP1075** (0x48), **USBLC6-2SC6**, **BAT54S**, **SM712**, **AO3422** ×3: alle pennen kloppen.
     USB-C: CC1/CC2 elk 5,1 kΩ naar GND, VBUS via D105, geen pad terug naar de host.
3. **Spanningswaarden** tegen 24 V met marge: alles op VM is 50 V; alle JLC-artikelen komen overeen met de waarde in
   het schema (JLC-onderdeelpagina's).
4. **Layout:** 280 footprints, alle op de bovenkant; print 100 × 80 mm, vier M3-gaten op 4 mm uit de hoeken met
   vrijgehouden zones; GND op In1 één ononderbroken vlak; In2 gesplitst in VM en +3V3. Stroompad J101 → Q101 → F101
   → tien via's (0,4 mm) → VM-vlak → drivers nagelopen; motoruitgangen 0,8 mm met halzen van 0,25 mm × ≤ 1,5 mm bij
   de pads (2,9 mΩ, 7 mW bij 1,5 A). Ontkoppelafstand per voedingspen gemeten (1,2 tot 3,8 mm; U203 pen 2 op
   6,0 mm). Pads, sporen en via's blijven minstens 0,55 mm van de rand, de vlakken 0,3 mm.
5. **Gerbers:** verse export met hetzelfde commando is op de datumregels na identiek aan `fab/gerbers/`, en het
   zip-bestand is identiek aan de map. Vier koperlagen, beide maskers, beide opdrukken, pasta boven, omtrek
   100 × 80 mm, 631 doorgemetalliseerde en 6 niet-gemetalliseerde boringen, passend bij de print.
6. **BOM en CPL:** 251 regels, gelijk aan de onderdelen met een LCSC-veld; alle op "Top". Rotatie en positie
   nagerekend door de pads van het EasyEDA-footprint met de CPL-hoek te draaien en met de pads op de print te
   vergelijken: alle onderdelen binnen 0,3 mm (ook pen 1 van de vier TMC5240, de module, de W5500, de elco's en de
   diodes), behalve D102 (B3). Dit rust op `fab/easyeda_cache.json`; de JLC-preview blijft de laatste controle.
7. **JLC, opgehaald op 2026-11-10/11 van jlcpcb.com:** alle 80 nummers op voorraad en "Economic and Standard";
   de doorsteekconnectoren worden met de hand gesoldeerd; kleinste behuizing 0402, kleinste steek 0,5 mm.
8. **Opdruk:** polariteit en spanning bij J101, poortnamen, printnaam met revisie en datum en de pennenlegenda op
   de achterkant, pen-1-markering bij de IC's en plus bij de elco's.

## Wat ik niet kon controleren

- De JLC-preview zelf (pen 1 en rotatie zoals JLC ze tekent); de pinvolgorde van de RGB-LED en de polariteit van
  de 0603-LED's in JLC's bibliotheek.
- De passing in de voet met motor, stekkers en kabels; welke lange rand naast de motor ligt staat niet in de
  bestanden die ik mocht lezen.
- De revisie van de TMC5240-datasheet (gelezen is de versie die analog.com nu levert); de datasheets van de
  zekeringen, de PTC's, de elco en de spoelen (alleen de kerngegevens van de JLC-pagina's).
- Alles wat een meting vraagt: opwarming, rimpel, EMC, de Ethernet-link, het gedrag bij inpluggen onder spanning.
- Firmware, de eigen controlescripts en de berekeningen van het project: bewust niet gelezen. Van `fab/make_jlc.py`
  heb ik alleen de kopregels gelezen om het formaat van de cache te begrijpen.
