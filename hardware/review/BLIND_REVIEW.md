# Blinde review PTZ-driverbord Rev B

Datum: 2026-11-11. Reviewer: onafhankelijke subagent, alleen met `BRIEF.md`, de ontwerpbestanden in `hardware/`,
`firmware/include/pins.h` en de datasheets. Niets in het ontwerp is gewijzigd.

## Oordeel

**Bestellen na fixes.** Ik vond geen fout die het bord zeker onbruikbaar maakt: alle modulesockets, de pinnen van
elk actief onderdeel, de ESP32-pinkeuze, de polariteit en de JLC-rotaties kloppen met de datasheets, ERC en DRC
(met schema-pariteit) zijn schoon, de Gerbers zijn gelijk aan het bord, en de berekende stroompaden en de
massaretour zijn ruim. Er zijn wel drie punten die ik vóór de bestelling zou oplossen of schriftelijk aanvaarden:
tien SMD-onderdelen liggen onder de Ethernet-module die volgens de zeefdruk vast gesoldeerd moet worden, de
fanuitgang overleeft in de stand VM geen kortsluiting, en het bord legt niet vast welke 5 V-module past terwijl
één van de gelezen kandidaten buiten zijn datasheet valt. Twee daarvan vragen een kleine layoutwijziging, dus dit
is het moment.

Telling: **0 KRITIEK, 3 BELANGRIJK, 14 KLEIN.**

## KRITIEK

Geen.

## BELANGRIJK

### B1. Tien onderdelen liggen onder de Ethernet-module, die maar 2,54 mm boven het bord zit `[vermoeden]`

- **Wat:** de achterzijde-zeefdruk schrijft voor "ETHERNET MODULE: SOLDER IT IN, NO TALL SOCKET". Dat moet ook:
  op een 8,5 mm socket wordt de module 8,5 + 2,54 + 1,6 + 13,61 + 2,0 = 28,3 mm hoog (grens 25 mm); vast gesoldeerd
  19,75 mm (WIZ850io datasheet V1.0 p10). Onder de module-print (x 172,0 tot 197,0, y 148,26 tot 171,26, afgeleid
  van pin 1 op 190,6/149,6 en de tekening p10) liggen: C203 (0805 22 µF), C204, U601 (SOT-23-6), R606 tot R609,
  C603, D602 (SOT-23) en de rand van C107.
- **Bewijs:** de bovenkant van de WIZ850io is volledig RJ45; W5500 (LQFP48, tot 1,6 mm hoog), kristal en passieve
  delen zitten dus op de onderkant, net als op de foto's van de pin-compatibele USR-ES1
  (`USR-ES1_datasheet_iarduino.pdf` p7). De afstandhouder van de pinheader is 2,54 mm (p10). U601 is tot 1,45 mm
  hoog, C203 1,25 ± 0,2 mm. Som met een 0603/0805 op de module: 1,45 + 0,9 tot 1,25 = 2,35 tot 2,7 mm. C203 en
  C204 (191,8/166,4 en 191,9/164,3) liggen bovendien waar ik de zuidelijke bevestigingspen en afschermlip van de
  RJ45 verwacht (ongeveer x 191,5 tot 194,7, y 163 tot 168); die steken naar schatting 1,4 tot 1,7 mm onder de
  module-print uit, dan blijft 0,8 tot 1,1 mm over voor een onderdeel van 0,8 tot 1,45 mm.
- **Wat ik niet kon nagaan:** de exacte onderzijde van de WIZ850io (geen tekening in de map, alleen schema).
  Daarom vermoeden, maar de marge is in het beste geval tienden van millimeters.
- **Gevolg:** module gaat niet vlak, of drukt op U601/C203; en alles daaronder (ESD en pull-ups van sensorpoort 4,
  ontkoppeling van de module) is na het solderen niet meer te bereiken. JP604/JP605 liggen in een sleuf van 3 mm
  tussen module en J603.
- **Fix:** U601, R606 tot R609, C203, C204, C603 en D602 buiten de moduleomtrek leggen (ten westen van x 172 of
  ten zuiden van y 171,3; de module zelf kan niet naar het noorden door J101 en U101). Minimaal: vóór het
  solderen passen en de module zo nodig 1 mm hoger zetten (de pinnen zijn 6,0 mm lang), en dat in de
  assemblagestappen zetten.

### B2. De fanuitgang overleeft in de stand VM geen kortsluiting `[zeker]`

- **Wat:** JP801 kiest +5V (standaard) of VM voor FAN_V. In de stand VM is de enige beveiliging F101 (T 5 A).
  FAN_V is 0,5 mm breed (18,8 mm, één via), de VM-sporen van 0,6 mm zijn samen 16,9 mm.
- **Bewijs (berekening):** spoor 0,5 mm × 35 µm = 0,0175 mm² = 34,5 circular mil. Onderdonk:
  I²t = 34,5² × log10((1083−25)/(234+25)+1) / 33 = 25 A²s tot smelten. De smelt-I²t van de zekering is 80 A²s
  voor de 4 A-uitvoering (Schurter MST 250, tabel) en hoger voor 5 A. Het spoor smelt dus vóór de zekering. Bij
  een voeding die op 5 A begrenst valt de zekering nooit: IPC-2221 geeft voor 4 A in dit spoor al +100 °C
  (I = 0,048 × 100^0,44 × 27,1^0,725 = 4,0 A). Bij kortsluiting tussen FAN+ en FAN− met de fan aan loopt de stroom
  door Q801 (AO3400A, SOT-23, 5,7 A maximaal, R_DS(on) < 48 mΩ bij 2,5 V): bij 10 A is dat tot 4,8 W.
- **Gevolg:** de brief eist dat een kortsluiting op elke uitgangsconnector overleefd wordt. Op 5 V klopt dat (de
  5 V-module begrenst, de MCU valt uit en GPIO45 gaat laag), op VM niet: spoor of Q801 brandt door.
- **Fix:** een PTC of SMD-zekering van 0,5 tot 1 A in FAN_V (dekt beide standen), of de VM-stand schrappen. Als
  het zo blijft: schriftelijk aanvaarden en "VM: NIET KORTSLUITVAST" bij JP801.

### B3. Het bord legt de 5 V-module niet vast, en de R-78E valt buiten zijn datasheet `[zeker]` voor de getallen, `[vermoeden]` voor het gedrag

- **Wat:** U101 is "5 V 1 A SIP-3"; de zeefdruk zegt "7805-PINOUT SWITCHER". Vijf typen zijn gelezen.
- **Bewijs:** RECOM R-78E5.0-1.0: maximale capacitieve last **220 µF**, ingang 8 tot **28 V** (datasheet rev
  3/2016, p1). Murata OKI-78SR: 300 µF bij lage ESR. Traco TSR 1-2450: 470 µF. Mornsun K7805-1000R3: 680 µF, 8 tot
  36 V. Op de 5 V-rail staat direct C107 + C108 + C110 + C113 + C201 = 98 µF keramisch plus de condensatoren van de
  DevKit; daarachter laden via de LDO's C111 en C114 (2 × 100 µF tantaal), C203 en de modules mee: samen ruim
  300 µF. De ingang heeft op de logische tak alleen C105 (10 µF) als F101 open is; bij insteken onder spanning
  schat ik met 2 µH kabel, 6 µF effectief en 0,3 Ω (zekering, FET, kabel) 40 % doorschot, dus ongeveer 24 V bij
  17 V: 4 V onder de grens van de R-78E.
- **Gevolg:** met een R-78E (of OKI-78SR) kan de regelaar bij het opstarten in zijn kortsluitbeveiliging blijven
  hikken, en is de spanningsmarge het kleinst. Niets op het bord of in de stuklijst waarschuwt daarvoor.
- **Fix:** één type voorschrijven op de zeefdruk en in de stuklijst (K7805-1000R3 of R-78K5.0-1.0, beide tot 36 V;
  van de R-78K staat de maximale capacitieve last niet in de gelezen tekst, die nog opzoeken), of C111 en C114
  verkleinen naar 22 tot 47 µF (AMS1117 vraagt 22 µF tantaal).

## KLEIN

1. **+3V3 heeft weinig ruimte boven de AMS1117** `[zeker]`. +5V = 5,0 V − SS34 (ongeveer 0,35 tot 0,45 V) =
   4,55 tot 4,65 V, in het slechtste geval 4,4 V (R-78K −3,5 %). De AMS1117 is gespecificeerd bij ≥ 1,5 V verschil en
   heeft maximaal 1,3 V dropout bij 0,8 A (datasheet, tabel). Typisch regelt hij bij 0,2 A nog, in het slechtste
   geval zakt +3V3 naar 3,1 tot 3,2 V; op alleen USB (VBUS minus de 1N5819 van de DevKit) net zo. W5500 vraagt
   ≥ 2,97 V, de TMC2209 komt pas boven maximaal 3,0 V uit reset. Fix: een echte LDO met dezelfde SOT-223-pinout, of
   aanvaarden en bij de eerste meting TP804 onder last controleren.
2. **DIAG_OR zit op strapping-pin GPIO46** `[zeker]`. Opstarten is goed (GPIO0 = 1: GPIO46 vrij; R205 trekt laag).
   Maar download-modus vraagt GPIO0 = 0 én GPIO46 = 0 (ESP32-S3 datasheet v2.2, tabel 3-3). Staat een TMC2240 in
   push-pull met een fout of stall op DIAG0, dan lukt flashen niet tot de motorvoeding eraf is geweest. In de
   firmware-notities zetten.
3. **TMC2240 DIAG0 is standaard open-drain, actief laag** `[zeker]` (datasheet-uittreksel p57, GCONF bit 12 = 0).
   Met de diode-OF en de pull-down komt er dan nooit een hoog niveau: firmware moet `diag0_pushpull` zetten, anders
   bereikt stall of fout de MCU niet. Geen hardwarefout, wel een voorwaarde.
4. **HOME4 op GPIO43 (U0TXD) met 10 nF direct aan de pin** `[zeker]`. De ROM en bootloader zenden hier bij elke
   reset; 10 nF met ongeveer 40 Ω geeft τ = 0,4 µs, te traag voor flashen over de UART-poort op 921600 baud
   (bit = 1,08 µs). Console moet naar USB-Serial-JTAG, flashen via de USB-poort of op lagere snelheid.
5. **STEP-lijnen zweven tijdens reset** `[zeker]`. GPIO's staan hoogohmig bij reset (datasheet tabel 2-1) en STEP
   heeft geen interne pull (TMC2240 p15). De eindtrap is uit via ENN (R203 plus pull-up op elke module), dus
   ongevaarlijk; de microstapteller kan wel verlopen. 100 kΩ naar massa zou het netjes maken.
6. **TCA9548A en W5500 zijn alleen samen met de MCU te resetten** `[zeker]` (PERIPH_RST_N via D201 aan EN). Een
   sensor die SDA laag houdt is dan niet met een mux-reset los te maken zonder de MCU te herstarten. Er is geen
   vrije pin over, dus aanvaarden; firmware kan negen klokpulsen geven.
7. **Min-teken bij J101 staat niet bij pin 2** `[zeker]`. "+" staat op 195,4/148,6 onder pin 1 (194,4/145,2), "−"
   op 189,6/143,4, links tussen beide pinnen (pin 2 op 194,4/141,2). Verpolen is beveiligd, maar zet "−" naast pin 2.
8. **Alle massapennen zitten vol in het koper, zonder thermische spaken** `[zeker]` (`connect_pads yes` op beide
   GND-vlakken en op VM). Goed voor de stroom, zwaar voor handsolderen van J101 (pad 2,7 mm), de elco's, sockets en
   headers: een krachtige bout is nodig. Voor THT-pennen thermische spaken overwegen.
9. **Hoogte van de drivers heeft 0,4 mm marge** `[vermoeden]`. Socket 8,5 + header 2,54 + print 1,6 + koellichaam
   12 mm (aanname uit `datasheets/README.md`, geen fabrikantmaat) = 24,64 mm tegen 25 mm. Koellichaam van ≤ 9 mm of
   lage sockets kiezen. De K7805 is 17,5 mm, de elco's 11 mm.
10. **Alleen de DevKitC-1U past** `[zeker]`. De antennerand van de DevKit ligt op x = 161,3 + 1,40 = 162,70 mm
    (maattekening V1.1), het huis van U101 begint op 163,75 mm. Een module met printantenne steekt ongeveer 6 mm
    verder en komt boven of tegen de regelaar. De USB-rand ligt op 99,96 mm, gelijk met de bordrand: goed.
11. **De RJ45 wijst naar de oostrand en de kabel komt dus van opzij, niet van boven** `[vermoeden]`. Het front van
    de bus ligt op x = 199,7 mm. Met mijn eigen plaatsing in de ronde bodem (bord y −31 tot +49 mm ten opzichte
    van het midden) is er op die hoogte ongeveer 29 mm tot de wand; een stekker met tule en bocht vraagt 30 mm of
    meer. Haakse of platte kabel voorzien. Niet te controleren zonder het behuizingsmodel.
12. **SMD dicht bij de bordrand** `[vermoeden]`. D101 heeft 1,45 mm, R801 en R802 2,0 mm tussen pad en rand. JLC
    kan daarvoor procesranden toevoegen; in de bestelling nakijken.
13. **Vijf BOM-regels zijn vermoedelijk "extended" bij JLC** `[vermoeden]` (TCA9548APWR, AOD4185, SMBJ18A, SRV05-4,
    NTC): ongeveer 3 dollar per regel. Mijn ruwe schatting voor vijf borden blijft onder € 100, maar prijzen en
    voorraad kon ik niet controleren.
14. **Een kortgesloten sensor- of home-kabel legt alle logica plat** `[zeker]` voor de berekening. V_SNS op 3,3 V:
    U103 begrenst op 0,9 tot 1,5 A, meer dan de 5 V-module naast de rest kan leveren, dus de 5 V-rail zakt in en de
    MCU herstart zolang de kortsluiting duurt. Niets gaat stuk (eis gehaald), maar de kop is dan ook via het
    netwerk onbereikbaar. Een PTC per poort of in V_SNS zou het lokaal houden.

## Wat ik heb nagekeken en in orde vond

- **ERC en DRC:** `kicad-cli sch erc` 0 meldingen; `pcb drc --schematic-parity --severity-all` 0 overtredingen,
  0 open verbindingen, 0 pariteitsfouten. Genegeerd in het project: ontbrekende courtyard, zeefdruk-overlap en
  -randafstand, footprintfilter. Regels: spoor ≥ 0,15, afstand ≥ 0,2, via 0,6/0,3 en 0,8/0,4, alle via's afgedekt.
- **Driversockets, pin voor pin** tegen het BTT TMC2240 V1.0-schema en de pintekening (bovenaanzicht): 1 EN,
  2 MOSI, 3 SCK, 4 CS, 5 MISO, 6 CLK (module heeft 10 kΩ naar massa), 7 STEP, 8 DIR, 9 VM, 10 GND, 11 tot 14 B1 B2
  A2 A1, 15 VIO, 16 GND, 17 AIN, 18 DIAG0. Op het bord: rijen 12,70 mm uit elkaar, steek 2,54, pad 17 en 18 op 2,54
  en 5,08 mm van EN in de kolom EN–VM, niet gespiegeld. Tegen de BTT TMC2209 V1.3: pin 4 = PDN_UART direct (1 kΩ
  R301 volgt figuur 4.1 van de TMC2209), pin 5 TX is op de module niet bestukt, CLK 20 kΩ naar massa, DIAG op
  pad 18, MS1/MS2 met interne pull-down als de jumpers doorgesneden zijn. Spoelparen op J301 kloppen voor beide.
- **ESP32-S3-DevKitC-1:** alle 44 pinnen tegen de gebruikersgids en maattekening; rijafstand 22,86 mm, J1 aan de
  noordkant met de antenne naar het oosten, niet gespiegeld. GPIO0, 19, 20, 35 tot 38 en 44 ongebruikt; GPIO45
  laag bij reset (R802); GPIO3 alleen relevant met eFuses; ADC op GPIO1 en 2 (ADC1). `pins.h` is gelijk aan de
  netlijst. De 5V-pin kan de host niet voeden: D1 en D7 (1N5819HW) op de DevKit, schema V1.1; D102 blokkeert naar
  de regelaar en er is geen pad van +5V naar VM zolang JP801 niet aan beide kanten tegelijk dicht zit.
- **WIZ850io:** J1 en J2 volgens datasheet p5 en 6, rijen 20,32 mm, pin 1 aan de RJ45-kant, front 0,3 mm binnen de
  bordrand. RSTn heeft 4,7 kΩ op de module en twee J1-signalen ook (R1 en R2; uit de schematekening lees ik SCSn
  en INTn, niet met zekerheid); CSN van de TMC2240 heeft een interne pull-up. Zo verwacht ik geen MISO-conflict
  tijdens reset. PERIPH_RST_N laag ≈ 0,3 V, onder 0,8 V (W5500) en 0,99 V (TCA).
- **Overige onderdelen tegen hun datasheet:** TCA9548APWR alle 24 pinnen (adres 0x70); AMS1117 (1 GND, 2 uit,
  3 in, lip = uit; 100 µF tantaal op de uitgang); AOD4185 (G, D-lip, S; drain aan de ingang; V_GS = −0,6 × V_in =
  −10,2 V bij 17 V, grens ±20 V; verpoold −17 V tegen −40 V); AO3400A; BAV99; SRV05-4 (2 GND, 5 VCC);
  SMBJ18A (V_RWM 18 V, klem 29,2 V bij 20,5 A, onder 32 V van de TMC2209); SS34; B5819W-richtingen; elco's en
  tantalen met plus op pad 1; SIP-3 pinvolgorde 1 in, 2 massa, 3 uit met het front naar het zuiden.
- **Stroompaden** (eigen rekenmodel: de kopervlakken uit de plot gerasterd op 0,083 mm, 0,49 mΩ per vierkant,
  via's 1,5 mΩ): massaretour van driver 1 naar J101 pin 2 is 2,4 mΩ; met 1 A uit alle vier de drivers staat er
  hoogstens 6,8 mV over de massa en 1,8 mV bij de MCU; lus elco C101 naar driver 1 is 0,7 mΩ. VM van F101 naar
  driver 1 geeft 37 mV bij 4 × 1 A. VIN_RAW en VIN zijn 3,0 en 1,5 mm, de VM-baan 3,4 tot 4,6 mm (ΔT ≈ 7 °C bij
  5 A), motorsporen 1,0 mm. Ontkoppeling ligt bij de pinnen (C301 op 2,7 mm van pin 9).
- **Gerbers en boorbestanden:** een verse export is op de datumregels na gelijk aan `fab/gerbers/`, en de zip is
  byte voor byte gelijk aan de map. Omtrek 100,0 × 80,0 mm, vier NPTH 3,2 mm op 4 mm uit de hoeken.
- **JLC-bestanden:** 108 onderdelen met LCSC-nummer, alle 108 in BOM en CPL, geen THT erin, alles op de bovenzijde,
  268 soldeerpunten. Elke afwijkende rotatie (SOT-23 180°, SOT-223 180°, SOT-23-6 en TSSOP-24 270°, TO-252 180°)
  heb ik met de hand nagerekend tegen de padposities in `easyeda_cache.json`, en voor C16133 en C7420376 opnieuw
  opgehaald bij EasyEDA: gelijk. Het JLC-symbool van de tantaal tekent de plus bij pin 1 en de footprint markeert
  pad 1. Diodes: pin 1 = kathode in JLC's symbolen.
- **Zeefdruk:** bordnaam, revisie en datum; EN, DIR, VM en GND bij elke socket; USB en ANT; IN en OUT bij de
  regelaar; zekeringwaarden; pinvolgorde van alle connectoren op de achterzijde, gelijk aan de netlijst.

## Wat ik niet kon nagaan

- De volledige TMC2240- en TMC2209-datasheets (alleen de uittreksels in de map; analog.com laadt niet).
- De onderzijde en de exacte pen- en lipposities van de WIZ850io (B1), en of een USR-ES1 mechanisch gelijk is.
- Andere TMC2209-modules dan BIGTREETECH V1.3 pin voor pin (FYSETC, Watterott alleen globaal gelezen).
- JST-tekeningen: gemonteerde hoogte van de VH-stekker met kabel binnen 25 mm.
- Het behuizingsmodel: wandafstanden, bereikbaarheid van de PH-stekkers aan de zuidrand op 1 mm van de motor, de
  ruimte voor USB- en RJ45-stekker (alleen eigen schatting).
- Voorraad, prijs en basic/extended bij JLC op de besteldag, en de JLC-preview zelf.
- Signaalkwaliteit van de SPI-bus (ongeveer 120 mm met aftakkingen, 33 Ω bij de bron), EMC van lange sensorkabels,
  opwarming in de gesloten bodem, en alles wat een meting vraagt.
- De werkelijke hoogte van het koellichaam op de drivermodules en het MT6701-datasheet in zijn huidige revisie.
