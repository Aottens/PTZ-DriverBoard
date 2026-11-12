# Blinde review 3 van de PTZ-driverprint, Rev B

- **Beoordeeld bestand:** `hardware/ptz-driver.kicad_pcb`, wijzigingstijd 2026-11-11 12:06:00, 2 151 930 bytes,
  SHA-256 `7f8679c4c8892f285d88e9a48be118fcdd7ad667704cc642db64eac8917c39ea`.
- **Datum review:** 2026-11-12. KiCad 10.0.6 (`kicad-cli` en `pcbnew` in Python), alles alleen-lezen; netlijsten,
  exports en scripts staan in een tijdelijke map buiten de repository.
- **Gekregen:** `hardware/review/BRIEF.md`, de ontwerpbestanden, `firmware/include/pins.h` en `hardware/datasheets/`.
  Geen specs, beslissingen, eerdere reviews of git-geschiedenis geopend. Wat ik buiten mijn wil toch zag staat onderaan.
- **Ik kan niets meten.** Elke uitspraak hieronder is een berekening met haar invoer, een datasheetpagina of een
  bestand; de rest is gemerkt `[vermoeden]`.

## Oordeel

**Bestellen.** Ik heb in schema, netlijst, layout en productiebestanden geen fout gevonden waardoor de print niet
werkt, beschadigd raakt of bij JLC niet te maken is: ERC en DRC (met schema-pariteit en opnieuw gevulde zones) geven
nul meldingen, elke modulevoet klopt pin voor pin en niet gespiegeld met de tekening van de module, de Gerbers en
boorbestanden in `fab/` zijn byte-gelijk (op de datumregels na) aan wat het bordbestand nu oplevert, en alle 115
CPL-regels zetten JLC's pad n op onze pad n. Er is geen KRITIEK-bevinding. Er is één BELANGRIJK-bevinding, een
inbouwvraag en geen elektrische fout: de RJ45-bus opent naar de oostwand en ik schat daar ongeveer 29 mm vrije
ruimte; meet dat vóór de bestelling na in het CAD-model met de echte stekker, of aanvaard het schriftelijk. De
overige bevindingen zijn klein en vragen geen wijziging van de print, wel een paar keuzes bij het inkopen van
modules en voetjes.

## KRITIEK

Geen.

## BELANGRIJK

### B1. De RJ45-bus opent naar de oostwand; een gewone patchkabel past daar waarschijnlijk niet `[vermoeden]`

- **Wat:** de Ethernet-module (A202) staat zo dat de bus aan de oostrand naar buiten opent. De brief zegt dat de
  kabels van boven het midden van de print komen en dat de oostrand minimaal 10 mm van de wand ligt.
- **Bewijs:** A202 op (190,6; 149,6), rotatie −90°; pad 2 ligt op (188,06; 149,6), dus de lokale +y-as van de
  footprint wijst naar bord −x en de busopening (lokaal y = −9,1) ligt op x = 199,7, 0,3 mm binnen de rand
  (x = 200). Ruimte tot de wand, mijn eigen schatting uit de brief: print 100 × 80 in een cirkel met straal 80,
  noordhoeken minstens 10 mm van de wand geeft noordrand op hoogstens 49 mm boven het middelpunt; de bus ligt
  59,8 mm onder de noordrand, dus op −10,8 mm; de wand ligt daar op x = √(80² − 10,8²) = 79,3 mm, de oostrand
  op 50 mm (print in oost-west gecentreerd aangenomen): **29 mm vrij**. Een RJ45-stekker steekt ongeveer 8 mm
  uit de bus, een tule 12 tot 18 mm daarachter, en dan moet de kabel nog 180° terug naar het midden.
- **Gevolg:** met een gewone patchkabel met tule sluit de voet mogelijk niet of staat er blijvend kracht op de bus
  en op de zes soldeerpennen per rij van de module. Ligt de print niet gecentreerd, dan is de ruimte kleiner.
- **Herstel:** vóór de bestelling in het CAD-model nalopen met de stekker die gebruikt gaat worden. Past een
  haakse stekker (kabel omhoog) of een platte kabel met korte stekker, dan hoeft de print niet te wijzigen; leg
  die keuze vast. Past het niet, dan moet de module 90° of 180° gedraaid worden en is dat een layoutwijziging.

## KLEIN

### K1. De stapel driver + koellichaam komt op 24,6 mm bij 25 mm toegestaan `[vermoeden]`

- **Bewijs:** vrouwelijke header 8,5 mm + kunststof van de pennen van de module 2,54 mm + print van de module
  1,6 mm + koellichaam 12 mm = 24,64 mm. De 12 mm is een aanname (`datasheets/README.md` zegt dat zelf);
  BIGTREETECH geeft geen maat. Een koellichaam van 13 mm (bestaat voor StepSticks, 14,5 × 15 × 13) of een
  plakpad van 0,5 mm maakt 25,6 respectievelijk 25,1 mm.
- **Gevolg:** de kap raakt de koellichamen.
- **Herstel:** geen printwijziging. Meet het meegeleverde koellichaam voordat de voetjes gekocht worden; neem
  anders lage voetjes (5 mm) of gedraaide pennen (3 mm).

### K2. De 3,3 V-rail voor de randapparatuur heeft weinig ruimte boven de uitvalspanning van de AMS1117 `[zeker]`

- **Bewijs (berekening):** U101 geeft 5,0 V ± 3 % (YLPTEC K7805-1000R3, blad 2), dus minimaal 4,85 V. D102 (SS34)
  kost bij 0,3 tot 0,6 A ongeveer 0,35 tot 0,45 V (MDD: maximaal 0,55 V bij 3 A). Op `+5V` staat dus 4,40 tot
  4,65 V. De AMS1117-3.3 heeft 1,1 V typisch en 1,3 V maximaal nodig (tabel met elektrische kenmerken, bij
  0,8 A; bij 0,15 A iets minder). Nodig voor 3,3 V: 4,4 tot 4,6 V. Typisch is er 0,2 V over, in het slechtste geval komt `+3V3` op
  ongeveer 3,1 V. Op USB alleen: 4,75 tot 5,0 V van de computer, min kabel, min de 1N5819HW op de DevKit
  (schema DevKitC-1, D1 en D7) geeft 4,1 tot 4,55 V en dus `+3V3` tussen 3,0 en 3,3 V.
- **Gevolg:** de W5500-module mag tot 2,97 V (WIZ850io-datasheet p7) en blijft dus werken; de TMC2209 reset op
  VCC_IO tussen 2,1 en 3,0 V (datasheet p78) en zit op USB alleen in het slechtste geval op de grens. De
  NTC-meting (deler aan `+3V3`, ADC aan de eigen 3,3 V van de DevKit) schuift mee, minder dan 1 °C.
- **Herstel:** aanvaarden, of bij een volgende revisie een LDO met lage uitvalspanning in dezelfde SOT-223-voet.

### K3. De randapparatuur wordt alleen gereset als de EN-pen van de DevKit laag gaat `[zeker]`

- **Bewijs (netlijst):** `PERIPH_RST_N` = A202.11 (RSTn), U701.3 (RESET), R204 naar `+3V3`, D201-anode; de kathode
  van D201 ligt aan `EN` (A201.3). Er zit geen GPIO aan. Een reset via USB-Serial-JTAG, de watchdog,
  `esp_restart()` of een brown-out trekt EN niet laag.
- **Gevolg:** na zo'n reset staan de W5500 en de multiplexer nog in hun oude toestand. De W5500 kan via SPI zacht
  gereset worden, de TCA9548A alleen door zijn register opnieuw te schrijven; een I2C-bus die een sensor laag
  houdt is niet via de reset van de multiplexer los te krijgen.
- **Herstel:** in firmware afhandelen (zachte reset W5500, kanaalregister altijd opnieuw schrijven, negen
  klokpulsen bij een hangende bus). Bij een volgende revisie een vrije GPIO via een diode aan `PERIPH_RST_N`.

### K4. Welke DevKit past: alleen de echte -1U, bij voorkeur v1.1 `[zeker]`, klonen `[vermoeden]`

- **Bewijs:** de voet heeft rijen op 22,86 mm (Espressif-maattekening: 25,40 breed, pennen 1,27 uit de rand).
  Veel klonen die als "DevKitC-1 N16R8" verkocht worden zijn breder met rijen op 25,4 mm `[vermoeden]`: die
  passen niet. Op bord v1.0 zit de RGB-led aan GPIO48 (user guide v1.0, regel "RGB LED ... GPIO48"), en GPIO48
  is hier `HOME3` (A201.38): de statusled is dan niet te gebruiken naast de home-ingang van as 3. Op v1.1 zit de
  led aan GPIO38, dat vrij is. Een bord met printantenne (zonder U) steekt volgens dezelfde tekening ongeveer
  6 tot 7 mm voorbij de pen-1-rand (uit de tekening geschaald); daar staat U101 (rand op x = 163,75; de DevKit eindigt op x = 162,87) en F102.
- **Herstel:** geen printwijziging. Koop een Espressif ESP32-S3-DevKitC-1U v1.1 en meet bij een ander bord eerst
  de rijafstand.

### K5. Het middelpunt van asymmetrische onderdelen in de JLC-preview nalopen `[vermoeden]`

- **Bewijs:** de CPL geeft voor elk onderdeel het midden tussen de padcentra van JLC's footprint. Daarmee landen
  alle pads goed (zie "Gecontroleerd"). Of JLC datzelfde punt als oorsprong van het onderdeel neemt weet ik
  niet; bij de TO-252 ligt de oorsprong van JLC's tekening 1,5 mm van dat midden (EasyEDA-gegevens C400894:
  pad 2 op x = 3992,3 en pads 1 en 3 op 4019,7, oorsprong 4000, eenheid 0,254 mm).
- **Gevolg:** in het slechtste geval staat Q101, U102, U103 of een SOT-23 in de preview een millimeter verschoven.
  De rotaties zijn goed.
- **Herstel:** in de preview Q101, U102, U103, Q801 en D302 tot D602 op verschuiving bekijken, naast pen 1 en
  polariteit van C111, C114, C116 tot C119, D101 tot D103, D201, D301 tot D601, D801, U301 tot U702.

### K6. Op USB alleen staat SLEEPN van elke TMC2240 boven zijn absolute grens `[zeker]` voor de berekening, schade `[vermoeden]` onwaarschijnlijk

- **Bewijs:** TMC2240-datasheet p9: SLEEPN maximaal VS + 0,3 V. Op de BIGTREETECH-module hangt SLEEPN via R8
  (4,7 kΩ) aan VCC_IO (schema TMC2240 V1.0). Op USB alleen is VM 0 V en `+3V3` aanwezig (A301.15 enz.), dus er
  loopt (3,3 − ongeveer 0,6) / 4,7 kΩ ≈ 0,6 mA per module de pen in.
- **Gevolg:** op papier buiten de grens; de stroom is door de module zelf begrensd en elk 3D-printerbord doet
  hetzelfde op USB. De brief vraagt deze voeding uitdrukkelijk.
- **Herstel:** schriftelijk aanvaarden.

### K7. Drie rails hebben geen testpunt `[zeker]`

- **Bewijs (netlijst):** `VIN_L` (na F102), `+5V_REG` (vóór D102) en `+3V3_SNS` (vóór JP101) hebben geen TP; de
  brief vraagt een testpunt op elke rail. Wel aanwezig: VIN, VM, +5V, +3V3, V_SNS, MCU_3V3, twee keer GND, SPI,
  I2C, DRV_ENN, DIAG_OR, PERIPH_RST_N.
- **Gevolg:** klein: `VIN_L` en `+5V_REG` zijn te meten op pen 1 en 3 van U101, `+3V3_SNS` op pad 1 van JP101.
- **Herstel:** aanvaarden en in de opstartchecklist die meetplekken noemen.

### K8. De home-ingangen hebben geen TVS-array zoals de sensorpoorten `[zeker]` voor het schema, het gevolg `[vermoeden]`

- **Bewijs (netlijst):** `HOMEn_IN` gaat van de stekker naar R302 (10 kΩ naar `+3V3`) en R303 (10 kΩ in serie),
  daarna 10 nF (as 4: 1 nF) en een BAV99 naar GND en `+3V3`. De SRV05-4 zit alleen op SDA en SCL. De brief vraagt
  ESD-bescherming op de bekabelde poorten.
- **Gevolg:** de MCU-pen is beschermd (10 kΩ begrenst bij 17 V op de draad tot 1,3 mA). Een harde ontlading op
  de draad komt over een 0603-weerstand van 10 kΩ te staan; die kan daar op den duur van verlopen.
- **Herstel:** aanvaarden; de twee vrije kanalen van elke SRV05-4 (pen 4 en 6) kunnen bij een volgende revisie de
  home-ingang van dezelfde as meenemen.

### K9. De sensor- en home-stekkers staan 3,4 mm uit de zuidrand, waar de motor op 1 mm staat `[vermoeden]`

- **Bewijs:** J302 tot J603 op y = 176,6, rand op y = 180; de behuizingen lopen tot ongeveer 179,4. De motor
  (42 mm breed) staat volgens de brief 1 mm van die rand en is hoger dan de stekkers.
- **Gevolg:** de stekkers achter de motor zijn alleen recht van boven te steken en moeilijk vast te pakken om ze
  los te trekken.
- **Herstel:** in het CAD-model en de montagevolgorde nalopen: stekkers erin vóór de print naast de motor komt,
  of de assen achter de motor niet gebruiken voor wat vaak los moet.

## Aandachtspunten voor de firmware (geen bevindingen aan de print)

- `DIAG_OR` werkt pas nadat `diag0_pushpull` in GCONF van elke TMC2240 gezet is; na reset is DIAG0 open drain en
  laag-actief (datasheet p57, p79) en kan hij de lijn met diode en pull-down niet omhoog trekken. Een driver die
  zelf in reset of onderspanning zit meldt zich dus niet: bevragen over SPI blijft nodig.
- GPIO43 (`HOME4`) is U0TXD: de console moet van UART0 af, anders stuurt de MCU die pen zelf aan.
- De SPI-bus is gedeeld door vier drivers en de W5500: de TMC2240 mag maximaal 10 MHz (datasheet p12), mode 3;
  de W5500 kan mode 0 en 3.
- Bij een TMC2209 is `DRVn_CS` de enkeldraads UART via 1 kΩ (R301 enz.) naar pen 4 van de voet, bij BIGTREETECH
  V1.3 direct PDN_UART (schema: UART_RX = pen 14 van de chip, R10 naar TX niet geplaatst).

## Gecontroleerd en in orde bevonden

**Regels en pariteit.** `kicad-cli sch erc --severity-all`: 0 fouten, 0 waarschuwingen. `kicad-cli pcb drc
--schematic-parity --severity-all --all-track-errors`, ook met `--refill-zones` op een kopie: 0 overtredingen,
0 niet-verbonden pads, 0 pariteitsverschillen; de gevulde oppervlakken zijn na opnieuw vullen gelijk (GND voor
4159,2 mm², GND achter 5220,6 mm², VM achter 501,7 mm²), de vulling in het bestand is dus actueel. Uitgezet in
het project en dus niet getoetst: ontbrekende courtyards, zeefdruk over zeefdruk en over de rand.

**Productiebestanden.** Gerbers en boorbestanden opnieuw geëxporteerd met dezelfde opties als
`fab/make_gerbers.sh`: alle elf bestanden gelijk aan `fab/gerbers/` en aan de inhoud van
`fab/ptz-driver_gerbers.zip` (vergeleken zonder de datum- en commentaarregels). Omtrek 100,0 × 80,0 mm, twee
lagen, 1,6 mm. Boringen: 666 geplateerd (195 pennen, 471 via's) en 4 ongeplateerd van 3,2 mm, gelijk aan het
bord. Kleinste via 0,6/0,3 mm, smalste spoor 0,187 mm, kleinste afstand 0,2 mm, sporen minstens 0,5 mm en vlakken
minstens 0,3 mm uit de rand. Geen pasta op soldeerjumpers of testpunten (alleen de 115 te plaatsen onderdelen hebben pasta). Alle SMD
op de bovenzijde.

**BOM en CPL.** 115 footprints met een LCSC-veld, 115 regels in de CPL, 115 in de BOM, geen verschil; elk
LCSC-nummer in de BOM is gelijk aan het veld op de footprint. Voor elke CPL-regel heb ik JLC's pads (uit
`fab/easyeda_cache.json`) met de opgegeven positie en rotatie op het bord gelegd en vergeleken met onze pads van
hetzelfde nummer: grootste afwijking 0,40 mm (SMB, verschil in padmaat), dus geen onderdeel gedraaid of
gespiegeld. De cache heb ik voor vier polaire onderdelen onafhankelijk nagehaald bij EasyEDA: C7171 (pad 1 links,
plusteken in footprint en symbool aan pad 1), C8598 (pen 1 = kathode, streep aan pad 1), C19077573 (pen 1 = C),
C400894 (1 = G, 2 = D op het vlak, 3 = S); alle vier gelijk aan de cache en aan het schema.

**Pinnen tegen datasheets, uit de netlijst.**
- TCA9548APWR (TI SCPS207H, pintabel): A0, A1, A2 aan GND (adres 0x70), RESET pen 3, SD0/SC0 tot SD4/SC4 op
  pen 4 tot 14, SCL 22, SDA 23, VCC 24: klopt. Kanaal 0 tot 3 = sensorpoort 1 tot 4, kanaal 4 = J701, zoals
  `pins.h` zegt.
- AOD4185 (Rev 4.2): 1 = G, vlak = D aan `VIN_RAW`, 3 = S aan `VIN`; de bodydiode geleidt van ingang naar last,
  de gate hangt aan een deler 100 k/100 k, dus VGS = −VIN/2 = −5,5 V bij 11 V (RDS(on) < 20 mΩ bij −4,5 V),
  −8,5 V bij 17 V en −14,6 V bij de klemspanning van 29,2 V, binnen ± 20 V. Omgepoold is VGS 0 en blokkeert hij
  17 V van de 40 V.
- AMS1117-3.3: 1 = GND, 2 en lip = uit, 3 = in; aan de uitgang drie keer 10 µF tantaal (de datasheet rekent met
  22 µF tantaal). SMBJ18A: kathode aan de rail; 18 V sperspanning, doorslag 20,0 tot 22,1 V, 29,2 V bij 20,5 A:
  boven de 16,8 V van een volle accu en onder de 32 V (TMC2209) en 41 V (TMC2240). SS34, B5819W, BAV99, AO3400A,
  SRV05-4 en de tantalen: pennen zoals in het schema bedoeld.
- 5 V-regelaar: voet 1 = in, 2 = GND, 3 = uit, pennen 2,0 mm achter de voorkant en het huis 7,1 mm naar achteren
  getekend; gelijk aan de YLPTEC-tekening (blad 3: vooraanzicht pen 1 links, pennen 2,00 mm uit de voorkant,
  huis 11,50 × 7,55). Ingang 8 tot 36 V, capacitieve last maximaal 680 µF (er hangt ruwweg 80 µF aan).

**Modulevoeten, pin voor pin en op spiegeling.**
- StepStick (A301 tot A601): voet 1 tot 8 = EN, SDI/MS1, SCK/MS2, CS/UART, SDO, CLK, STEP, DIR; 9 tot 16 = VM,
  GND, vier motorpennen, VIO, GND; 17 en 18 op 2,54 en 5,08 mm van EN in de bovenste rij. Gelijk aan de
  pentekening en het schema van de BIGTREETECH TMC2240 V1.0 (J1, J2, J3: AIN naast EN, dan DIAG0) en van de
  TMC2209 V1.3 (EN, MS1, MS2, RX, TX, CLK, STEP, DIR; VM, GND, A2, A1, B1, B2, VIO, GND; DIAG op de derde pen).
  Rijafstand 12,70 mm. Op het bord: pen 1 op (112,5; 125,7), pen 9 op (112,5; 113,0), pennen oplopend in +x:
  een zuivere rotatie, niet gespiegeld. CLK is op beide modules zelf naar GND getrokken (10 kΩ en 20 kΩ) en mag
  op de print open blijven; de modules trekken EN zelf omhoog. De twee spoelen liggen bij beide modules op
  pen 1-2 en 3-4 van de motorstekker.
- DevKitC-1 (A201): 1 tot 22 = J1 (3V3, 3V3, RST, 4, 5, 6, 7, 15, 16, 17, 18, 8, 3, 46, 9, 10, 11, 12, 13, 14,
  5V, G), 23 tot 44 = J3 (G, TX, RX, 1, 2, 42, 41, 40, 39, 38, 37, 36, 35, 0, 45, 48, 47, 21, 20, 19, G, G);
  gelijk aan de maattekening. Rijen 22,86 mm, niet gespiegeld, USB-eind op x = 100,0 (de westrand).
- WIZ850io (A202): 1 tot 6 = J1 (GND, GND, MOSI, SCLK, SCNn, INTn), 7 tot 12 = J2 (GND, 3,3 V, 3,3 V, NC, RSTn,
  MISO); rijen 20,32 mm, pen 1 op 6,4 mm van de voorkant, bus 2,7 mm buiten de moduleprint: gelijk aan de
  datasheet p5, p6 en p10; niet gespiegeld. De USR-ES1 heeft dezelfde pennen.

**ESP32-S3.** Alle 28 gebruikte pennen zijn gelijk aan `pins.h`. Strap-pennen (module-datasheet tabel 4-1):
GPIO0 vrij; GPIO3 (`DIAG_OR`) heeft 10 kΩ naar GND en telt alleen met een gebrande eFuse; GPIO45 (`FAN_PWM`)
wordt via R801 en R802 laag gehouden; GPIO46 (`DIR2`) hangt alleen aan een driveringang zonder pull-up.
GPIO35, 36, 37 (octaal geheugen), 19 en 20 (USB), 38 (led v1.1), 44 en 0 zijn niet aangesloten. De analoge
ingangen zitten op ADC1 (GPIO1 en 2). USB voedt niet terug: beide USB-bussen van de DevKit hebben een eigen
1N5819HW naar de 5 V-rail, en D102 houdt USB-voeding weg van U101 en dus van de motorvoeding. De drivers staan
uit tijdens reset: `DRV_ENN` heeft R203 naar `+3V3`, en de ventilator blijft uit.

**Stroompaden, uit de sporen in het bordbestand.** Stroom voor 10 °C opwarming volgens IPC-2221, 35 µm buitenlaag.
- `VIN_RAW`: 3,0 mm over 9,9 mm. `VIN`: 3,0 mm naar F101 (5,3 A), 1,5 mm naar F102 (1 A-zekering).
- `VM`: van F101 een kolom van 4,6 mm spoor in een vlak van 5,0 mm, dan een band van 3,4 mm spoor in een vlak
  van 3,6 mm over 86 mm (6,0 A; de zekering is 5 A), aftakkingen van 2,0 mm naar elke voet en elko. Weerstand
  tot driver 1 ongeveer 14,5 mΩ (0,49 mΩ per vierkant), dus 22 mV bij 1,5 A.
- Motoruitgangen: 1,0 mm over 8,6 mm (2,4 A bij 10 °C, 3,2 A bij 20 °C; de TMC2240 levert 2,1 A effectief).
- `+5V`, `+3V3`, `V_SNS`: 0,5 tot 0,6 mm (1,4 A); langste 5 V-pad ongeveer 70 mm, 69 mΩ, 35 mV bij 0,5 A.

**Massaretour op twee lagen.** Ik heb al het GND-koper van beide lagen uit het bordbestand gerasterd (0,25 mm),
op een rooster van 0,5 mm gezet waarin een cel alleen geleidt als alle vier de monsters koper zijn (dus aan de
voorzichtige kant), via's en pennen als doorverbinding (1,5 mΩ per via van 0,3 mm), en de weerstand opgelost:
van de twee GND-pennen van een voet naar J101 pen 2 is het 2,7 mΩ (driver 1), 2,1 mΩ (driver 2), 1,7 mΩ
(driver 3) en 1,5 mΩ (driver 4). Per ampère motorstroom verschuift de massa van de MCU hoogstens 2,1 mV en die
van de Ethernet-module 0,3 mV. Van de min van elke elko naar de GND-pennen van zijn voet: 0,8 tot 2,3 mΩ. Geen
flessenhals; de aparte brede GND-sporen achter (1,0 tot 3,0 mm) liggen in het vlak.

**Ontkoppeling, afstanden uit de padposities.** 100 nF op VM en op VIO van elke voet op 2,7 mm van de pen; elko
van 100 µF op 8 mm van de VM-pen; C701 op 2,7 mm van U701 pen 24; C204 op 4,2 mm van de 3,3 V-pennen van de
Ethernet-module; C202 op 3 mm van de 5 V-pen van de DevKit; de filtercondensatoren van de twee ADC-ingangen op
3,2 en 3,6 mm van de pen.

**Onder en naast de modules.** Onder de DevKit liggen U103, U701, C108 tot C119, C202, C701, C801, R104, R204,
R701, R702, R803; hoogste is 1,8 mm, ook bij vastsolderen (2,54 mm vrij) geen botsing. Onder elke driver: twee
condensatoren, de DIAG-diode en een weerstand, hoogste 1,35 mm. Onder de Ethernet-module en onder U101 ligt
niets. De Ethernet-module vastgesoldeerd is 2,54 + 1,6 + 13,61 = 17,75 mm hoog, 19,75 mm met het lipje van de
stekker; op een voetje van 8,5 mm zou het 26,25 mm zijn, de achterzijde van de print zegt terecht "solder it
in". Tussen twee drivers zit 0,68 mm. Koper blijft 3,48 mm uit het hart van elk M3-gat, vrij van een boutkop
en een ring van 7 mm. Alle soldeerjumpers liggen buiten de modules en blijven bereikbaar.

**Zeefdruk.** Naam, revisie en datum voor en achter; plus en min en "11-17V" bij J101; F1 T5A en F2 T1A; M1
tot M4, H1 tot H4, S1 tot S4, I2C, FAN +5V; EN, DIR, VM en GND bij elke voet; pen-1-stip bij elke module; IN en
OUT bij de regelaar; 3V3 en 5V aan weerszijden van JP101; op de achterzijde de pinbezetting van elke stekker,
de jumperstanden en welke regelaar past.

## Niet kunnen controleren

- **Voorraad en prijs bij JLC op de dag van bestellen**, en daarmee de grens van € 100. JLC's onderdeelpagina
  laadde zonder voorraad en prijs; wel bevestigd dat C19077573 (SMBJ18A) "Extended" is en voor Economic PCBA
  mag. Mijn schatting van vijf Extended-onderdelen (C19077573, C400894, C7420376, C130026, C2892547) is
  `[vermoeden]`.
- **De inbouw in de voet**: ik heb geen CAD-model, alleen de maten uit de brief. B1, K1 en K9 zijn daarop
  gebaseerd. De ruimte voor de USB-stekker aan de westrand schat ik op dezelfde manier op ongeveer 30 mm.
- **De hoogte van het koellichaam van BIGTREETECH** en of een gekochte DevKit een echte v1.1 is.
- **Gedrag op de bank**: I2C over lange kabels naast motordraden, het in- en uitschakelen bij hot-plug, de
  opwarming van de drivers, de nauwkeurigheid van de VM- en temperatuurmeting. Dit kan alleen een meting tonen.
- **De volledige datasheets van de TMC2240 en TMC2209**: alleen de uittreksels in `hardware/datasheets/` gelezen.
- **De maker van de BAV99 en de AO3400A**: pinvolgorde uit de standaard van de behuizing en uit JLC's symbool,
  zoals `datasheets/README.md` ook meldt.
- **De JLC-preview zelf** (K5): die bestaat pas na het uploaden.

## Wat ik zag dat buiten de opdracht viel

- De inhoud van `CLAUDE.md` en de titels van het geheugenbestand en van de laatste vijf commits zijn door de
  omgeving automatisch in mijn context gezet. Ik heb ze niet geopend, maar ze waren zichtbaar: werkwijze,
  bestelpoort, algemene hardwareregels en toolnotities, en commit-titels over inkoop. Er staat geen redenering
  over een ontwerpkeuze van deze print in, behalve dat alle SMD boven moet en dat eerdere reviews bestonden.
- Met `ls hardware` heb ik de namen van de verboden bestanden en mappen gezien, niet hun inhoud.
- `firmware/include/pins.h` en `hardware/datasheets/README.md` mocht ik lezen; ze bevatten wel redeneringen
  (waarom welke GPIO, welke aannames in `check_fit.py` en `calc/power.py`). In `hardware/fab/` heb ik
  `jlc_pins.md`, `easyeda_cache.json`, `easyeda_pins.json` en `make_gerbers.sh` gelezen; `make_jlc.py` en
  `jlc_pins.py` niet.
- Verder niets geopend uit `specs/`, `docs/`, `tests/`, `hardware/route/`, `hardware/tools/`, `hardware/calc/`,
  `hardware/sourcing/`, de andere bestanden in `hardware/review/`, GitHub of de git-geschiedenis.
