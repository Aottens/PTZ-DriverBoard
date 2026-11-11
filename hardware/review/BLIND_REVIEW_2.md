# Blinde review 2 — PTZ driver board Rev B

Datum: 2026-11-11. Beoordeeld: `hardware/ptz-driver.kicad_pcb` (bestand van 11:19), de schema's, `ptz.pretty/`,
`fab/` en `firmware/include/pins.h`, tegen `review/BRIEF.md` en de datasheets. Niet gelezen: specs, beslissingen,
bouwnotities, controlescripts, de andere bestanden in `review/`, git-historie.

## Oordeel

**Bestellen na herstel.** Het schema klopt pin voor pin met de datasheets en de moduletekeningen, de drie
modulevoeten zijn niet gespiegeld, ERC en DRC (met schema-pariteit) geven nul meldingen, de Gerbers en het zip-bestand
zijn gelijk aan het bord, en BOM en CPL dekken precies de 114 SMD-onderdelen. Ik vond geen fout die het bord
zeker onbruikbaar maakt. Wel drie punten die ik vóór de bestelling zou oplossen: de massa van het hele motordeel
hangt met ongeveer 4 mm koper aan de rest van het bord, de logica-tak heeft geen overspanningsklem zodra de
motorzekering open is (juist de toestand bij eerste inbedrijfname), en de RJ45-stekker past volgens mijn som
niet zonder haakse of dunne kabel tussen bordrand en wand. De eerste twee zijn kleine layout- en schemawijzigingen.

Alle uitspraken over gedrag hieronder zijn berekeningen of datasheetwaarden; ik heb niets gemeten.

---

## KRITIEK

Geen.

---

## BELANGRIJK

### B1. Massa van het motordeel hangt met ±4 mm koper aan de rest van het bord `[zeker]` (geometrie), `[vermoeden]` (gevolg)

**Wat.** Tussen de onderste rij van de driversockets (y = 25,7 mm) en de J1-rij van de DevKit (y = 40,5 mm) lopen de
SPI-bus, STEP/DIR, CS en DIAG op béide lagen dwars over de volle bordbreedte. Daardoor is de GND-vulling ten
noorden daarvan (vier sockets, motorconnectoren, vier elco's, TVS) alleen aan de oost- en westrand verbonden met
de GND ten zuiden (voedingsconnector J101, DevKit, Ethernet, multiplexer).

**Bewijs.** Uit het bordbestand zelf: zonevullingen, sporen, pads en via's van net GND gerasterd op 0,1–0,2 mm,
daarna breedste-pad en min-cut (max-flow) berekend.
- Min-cut tussen J101 pin 2 en de acht GND-pinnen van de sockets: **3,8 mm** koperbreedte totaal (via = 0,5 mm
  gerekend); met via's onbeperkt 4,4 mm. Tussen DevKit-GND (A201.22) en de sockets: ook 3,8 mm.
- Breedste enkele pad J101.2 → A301/A401/A501/A601 pin 10: **1,4 mm**.
- Oostkant (±2,4 mm van de 3,8): F.Cu-strook tussen het VM-spoor naar TP802 (F.Cu, 0,8 mm, x = 97,3,
  y = 26,0–31,3, daarna schuin naar F101.2) en de bordrand: x = 97,95–99,5 = 1,55 mm breed over ±9 mm. Op B.Cu ligt
  daar de VM-zone (x 94,6–99,6, y 8,3–34,6), dus B.Cu draagt hier geen GND.
- Westkant (±1,3 mm): rond x ≈ 10, y 25–35, 70–90 mm van de voedingsingang.
- Ter vergelijking: J101.2 → DevKit-GND heeft 7,0 mm.

**Gevolg.** Gelijkstroom: de retourstroom van alle motoren (zekering 5 A) gaat vrijwel geheel door de strook van
1,55 mm. Berekening IPC-2221, 35 µm buitenlaag: 5 A → ±30 °C, 3 A → ±10 °C temperatuurstijging; weerstand
0,5 mΩ/□ × 9/1,55 ≈ 3 mΩ → 15 mV. Dat is heet maar niet stuk. Het echte risico is signaal: de retourstroom van
SPI_SCK/MOSI/MISO (120–156 mm lang, 5 lasten) en van STEP/DIR moet tientallen millimeters omlopen via de oost- of
westhals, en deelt die hals met de motorstroom. Dat geeft een grote lus en massasprong tussen MCU en drivers:
kans op dubbele klokflanken op SCK (leesfouten TMC2240/W5500), overspraak en storing op lange sensorkabels. Hoe erg
kan ik niet berekenen zonder meting, vandaar `[vermoeden]` voor het gevolg.

**Herstel.** (1) TP802 niet via een F.Cu-spoor langs de oostrand voeden maar met een via direct in de VM-zone op
B.Cu (of TP802 naast F101.2 zetten); dan is de F.Cu-GND-strook langs de oostrand 4–5 mm breed, precies boven de
VM-zone. (2) In de band y = 27–38 op minstens twee plaatsen (bijv. bij x ≈ 31 en x ≈ 52, tussen de sockets) één
laag vrijhouden van dwarssporen zodat de GND-vulling daar noord–zuid doorloopt, met via's aan beide zijden.
(3) Na de wijziging de min-cut opnieuw uitrekenen; streef naar ≥ 10 mm totaal en ≥ 3 mm per brug. Tot die tijd in
firmware SPI ≤ 1–2 MHz aanhouden.

### B2. Geen overspanningsklem op de logica-tak zodra F101 open is; gate van Q101 krijgt 0,6 × VIN `[zeker]` (schakeling), `[vermoeden]` (hoogte van de piek)

**Wat.** De TVS D101 (SMBJ18A) en de vier elco's zitten op VM, dus áchter de motorzekering F101. De logica-tak
(VIN → F102 → VIN_L → U101) heeft alleen C105 (10 µF/50 V keramisch) en C106. Q101 (AOD4185) heeft geen zener
over gate–source maar een deler R101 150k (G–S) / R102 100k (G–GND).

**Bewijs.** Netlijst: `VM: … D101.1 F101.2 C101–C104`; `VIN_L: C105.1 C106.1 F102.2 U101.1`; `RP_GATE: Q101.1
R101.1 R102.1`, R101.2 op VIN, R102.2 op GND → V_GS = −VIN × 150/(150+100) = −0,6 × VIN. AOD4185 Rev 4.2: V_GS
max ±20 V, V_DS −40 V. TSR 1-2450 en K7805-1000R3: ingang max 36 V. SMBJ18A: V_C 29,2 V.
- F101 heel: VIN wordt via F101 geklemd op ≤ 29,2 V → V_GS ≤ 17,5 V (88 % van het maximum) en de elco's dempen.
  In orde.
- F101 open of niet geplaatst (eerste inbedrijfname met alleen de logica-zekering, of na een doorgebrande
  motorzekering): een hot-plug van een volle accu (16,8 V) op een kabel met alleen een keramische condensator
  slingert theoretisch tot 2 × VIN = 34 V, en in de praktijk hoger doordat X5R capaciteit verliest onder
  spanning (Linear AN88 meet 57 V bij 24 V). Bij 34 V: V_GS = 20,4 V (boven het absolute maximum) en 2 V onder
  het maximum van de 5 V-module; bij 40 V zijn beide overschreden.

**Gevolg.** Mogelijke schade aan Q101 en/of de 5 V-module bij een hot-plug zonder motorzekering — de toestand die
een stroombegrensde eerste inbedrijfname juist opzoekt. De brief eist dat het bord een hot-plug overleeft.

**Herstel.** D101 verplaatsen naar net VIN (na Q101, vóór beide zekeringen), of een tweede klem/demping op VIN_L
(SMBJ18A of een elco 47–100 µF/35 V). Daarnaast een zener 12–15 V (bijv. BZT52C12, SOD-123) van source naar gate
van Q101, parallel aan R101. Tot dan in de inbedrijfname-checklist: F101 altijd geplaatst vóór de eerste hot-plug,
of opregelen met een labvoeding.

### B3. RJ45-stekker heeft ±29 mm tussen bordrand en wand; een gewone patchkabel past niet `[vermoeden]`

**Wat.** De WIZ850io staat met de RJ45-opening gelijk met de oostrand (pin 1 op x = 90,6; printje tot x = 97,0;
bus steekt 2,7 mm over → x = 99,7; opening op y ≈ 59,8). De kabel komt dus horizontaal uit de rand, terwijl de
brief zegt dat kabels van boven het midden komen en de rand 10 mm van de wand mag liggen.

**Bewijs (som met de maten uit de brief).** Bord 100 × 80 in een cirkel R = 80 met een motor van 42 mm op 1 mm
onder de zuidrand: de hoeken moeten binnen R = 70 blijven, dus de noordrand ligt op y = +45,8 … +49 mm van het
midden en het bord kan hooguit ±3 mm oost–west schuiven. De RJ45 ligt dan op y ≈ −11 … −14; wand op
x = √(80² − y²) ≈ 79 mm; bordrand op x = 50 ± 3 → **26–32 mm vrije ruimte**. Een RJ45-stekker steekt ±8–9 mm uit
de bus; een ronde Cat5e-kabel wil ±22 mm buigstraal (4 × Ø), met tule nog 12–20 mm erbij → ≥ 31 mm zonder tule,
≥ 45 mm met. Stekkermaten uit algemene kennis, niet uit een datasheet; de positie in de behuizing ken ik alleen
uit de brief.

**Gevolg.** Met een standaard patchkabel sluit de kop niet of staat de kabel strak tegen de wand. Hetzelfde geldt
in mindere mate voor de USB-stekker aan de westrand (±29 mm; alleen nodig bij flashen).

**Herstel.** Geen bordwijziging nodig als dit bewust is: een haakse (omhoog) RJ45-stekker of platte/dunne
patchkabel voorschrijven en in CAD met stekker natekenen. Anders de module 90° draaien zodat de bus naar een rand
met meer ruimte wijst (kost herroutering van zes signalen).

---

## KLEIN

**K1. DIAG-lijn werkt pas nadat firmware `diag0_pushpull` zet `[zeker]`.** TMC2240 Rev 2 p.57 en p.79: DIAG0 is
na reset open-drain, actief laag. De OR-schakeling (D301/D401/D501/D601, anode aan DIAG, kathode aan DIAG_OR, R205
10k naar GND) kan alleen een actief-hoge push-pull uitgang doorgeven. Gevolg: zonder GCONF bit 12 = 1 ziet GPIO3
nooit iets. Herstel: in `pins.h` bij `PIN_DIAG_OR` vermelden; geen bordwijziging.

**K2. BTT TMC2209 V1.3: DIAG-pen staat op de foto naar boven `[vermoeden]`.** Handleiding p.1: de twee pennen bij
EN wijzen omhoog; dan bereikt DIAG pad 18 niet. Geldt alleen voor de alternatieve module. Herstel: pen omsolderen;
in de bouwinstructie zetten. Of de TMC2240-module zijn AIN/DIAG0-pennen naar beneden heeft, kon ik niet zien.

**K3. AMS1117 achter een Schottky: 1,3 V ruimte bij 1,1–1,3 V dropout `[zeker]`.** +5V = 5,0 V − V_F(SS34,
±0,4 V) ≈ 4,6 V; op USB 5,0 − V_F(1N5819HW op de DevKit) ≈ 4,5 V. AMS1117: dropout typ. 1,1 V, max 1,3 V bij
0,8 A. Bij ±0,17 A (W5500 132 mA + VIO + mux) blijft +3V3 naar verwachting op 3,3 V, maar zonder marge: met een
5 V-module op −3 % of een slappe USB-poort zakt +3V3 tot ±3,1–3,2 V (W5500 min 2,97 V; TMC2209 VIO-reset tot
3,0 V). Geen schade. Herstel als het in de praktijk speelt: D102 vervangen door een type met lagere V_F, of U102
door een LDO met < 0,5 V dropout in SOT-223.

**K4. 5 V-budget dicht bij 1 A `[zeker]` (som).** ESP32-S3 WiFi-piek ±355 mA + W5500 132 mA + vier VIO en
multiplexer ±30 mA + vier sensoren ±40 mA + 5 V-ventilator 100–200 mA = 0,65–0,75 A, pieken hoger, op een
1 A-module. Herstel: ventilator ≤ 150 mA kiezen.

**K5. Kortsluiting op V_SNS of de ventilatorpen trekt de hele 5 V-rail omlaag; op USB begrenst alleen de host
`[vermoeden]`.** V_SNS komt uit U103 (stroomgrens 0,9–1,5 A) of direct uit +5V (JP101 op 5V); J801.1 is direct
+5V. Op de 12 V-voeding begrenst de 5 V-module (kortsluitvast) en reset de MCU; het bord overleeft. Op alleen USB
aan een lader van 2 A loopt de stroom door D1/D7 van de DevKit (1N5819HW, 1 A). Herstel: PTC van 200–500 mA in
V_SNS en in de ventilatorplus.

**K6. Ompoolbeveiliging dekt geen geaarde voeding samen met USB `[zeker]` (principe).** Q101 zit in de plus. Bij
omgepoolde stekker ligt bord-GND aan de plus van de voeding; hangt tegelijk een geaarde pc aan USB en is de
voeding geaard, dan loopt de kortsluitstroom via de USB-massa. Met accu of zwevende adapter speelt dit niet.
Herstel: in de bouwinstructie zetten.

**K7. TVS-klem ligt op de bedrijfsgrens van de TMC2209 `[zeker]`.** SMBJ18A: V_C 29,2 V; TMC2209: 29 V bedrijf,
32–33 V absoluut. Bij 17 V normaal bedrijf is de marge 12 V; tijdens een klem 0 V tot bedrijf en ±3 V tot
absoluut. Voor de TMC2240 (36/41 V) ruim.

**K8. ESP32-S3-DevKitC-1 v1.0 heeft de RGB-led op GPIO48 = HOME3 `[zeker]`.** Gebruikersgids v1.0 tegenover v1.1
(GPIO38, vrij gelaten). Op een v1.0-bord vervalt de statusled of HOME3. Herstel: v1.1 voorschrijven.

**K9. Geen firmware-reset voor multiplexer en W5500, geen GPIO over `[zeker]`.** PERIPH_RST_N volgt alleen EN
(D201, R204). Een vastgelopen I2C-bus op een lange kabel is alleen met klokpulsen of een MCU-reset te herstellen.
Alle bruikbare GPIO's zijn bezet.

**K10. Alle GND-pads zitten massief in de vulling `[zeker]`.** Zoneverbinding = vol op beide lagen. Voor de
SMD-assemblage geen probleem; de eigenaar soldeert J101 (gat 1,7 mm), elco's, headers en sockets in massief koper
en heeft een krachtige bout nodig. Herstel: thermische spaken voor THT-pads.

**K11. Krappe passingen `[zeker]` (maten uit het bord).** Tussen naast elkaar staande drivermodules 0,68 mm
(fab-omtrek 11,23–31,55 en 32,23–52,55); zekeringhouder F102 0,4–1,1 mm van de rand van A501/A601; SPI-jumpers
0,33 mm naast de sockethuls; DevKit-einde 0,9 mm van U101. Hoogte driver: 8,5 + 2,5 + 1,6 + koellichaam; bij
12 mm koellichaam 24,6 mm tegen 25 mm toegestaan — de 12 mm staat nergens in de BTT-documenten. WIZ850io op een
8,5 mm-socket wordt 26,25 mm; de onderzijde zegt terecht "solder it in". Herstel: koellichaam nameten of lage
sockets nemen.

**K12. Drie rails zonder testpunt `[zeker]`.** VIN_L, +5V_REG en +3V3_SNS hebben geen TP (wel bereikbaar op
F102.2/U101.1, U101.3 en JP101 pad 1). De brief vraagt een testpunt op elke rail.

**K13. Silkscreen `[zeker]`.** Penfuncties van sensor-, home- en ventilatorstekkers staan alleen op de onderzijde;
bovenop alleen H1–H4, S1–S4, FAN, +5V. De teksten "VSNS"/"3V3" bij JP101 overlappen (posities 2,0;63,3 en
4,4;64,3). Het minteken bij J101 staat op y = 43,0, midden tussen de pads (41,24 en 45,2); volgorde klopt.
Referenties zijn overal verborgen. Polariteit van elco's, tantalen, diodes, pin 1 van U701 en sockets klopt met de
pads.

**K14. Boorkaarten in het Gerber-zip `[vermoeden]`.** `ptz-driver-PTH-drl_map.gbr` en `-NPTH-drl_map.gbr` zitten in
`ptz-driver_gerbers.zip`. JLC's lezer kan extra `.gbr`-bestanden als laag aanzien. Herstel: `--generate-map`
weglaten of de twee bestanden niet inpakken.

**K15. Kosten `[vermoeden]`.** Vermoedelijk uitgebreide onderdelen (elk een toeslag): SMBJ18A C19077573, AOD4185
C400894, SRV05-4 C7420376, TCA9548APWR C130026, NTC C2892547. Schatting 5 borden: printen ±€8, assemblage en
opstart ±€12, onderdelen ±€17, toeslagen ±€15, verzending en btw ±€25 → ±€75–80. Onder de €100, niet ruim. Ik kon
geen prijzen of voorraad opvragen.

---

## Wat ik controleerde en in orde vond

**Netlijst** (`kicad-cli sch export netlist`, 185 onderdelen, 149 netten), pin voor pin:
- ESP32-S3-DevKitC-1 (A201): alle 44 pennen tegen de maattekening V1.1 (J1: 3V3, 3V3, RST, 4, 5, 6, 7, 15, 16,
  17, 18, 8, 3, 46, 9, 10, 11, 12, 13, 14, 5V, G; J3: G, TX, RX, 1, 2, 42, 41, 40, 39, 38, 37, 36, 35, 0, 45, 48,
  47, 21, 20, 19, G, G). Rijafstand 22,86 mm, laatste pen 8,0 mm van het USB-einde: klopt met de voet.
- `pins.h` tegen de netlijst: alle 28 toewijzingen gelijk.
- Pingebruik tegen Espressif: GPIO0, 19, 20, 35–37, 38, 44 ongebruikt; GPIO45 (strap VDD_SPI) laag via R802 100k;
  GPIO46 op DIR2 (TMC-ingang zonder pull-up, interne pull-down blijft gelden); GPIO3 met 10k pull-down, geen
  bezwaar bij standaard-eFuses; GPIO43 (ROM-log) achter R603 10k met 1 nF; ADC op ADC1 (GPIO1, 2); GPIO47/48 zijn
  3,3 V op N8 en N16R8 (alleen R16V is 1,8 V). Opstartpulsen (datasheet tabel 2-2): GPIO14 60 µs laag, GPIO18
  60 µs hoog — zonder gevolg, de TMC2240 start met TOFF = 0.
- Driversocket tegen BTT TMC2240 V1.0 (pintekening en schema): 1 EN, 2 MOSI, 3 SCK, 4 CS, 5 MISO, 6 CLK (los; de
  module heeft 10k naar GND), 7 STEP, 8 DIR, 9 VM, 10 GND, 11 B1, 12 B2, 13 A2, 14 A1, 15 VIO, 16 GND, 17 AIN,
  18 DIAG0. Tegen BTT TMC2209 V1.3: zelfde posities, pen 4 = PDN_UART (eendraads via R301 1k), pen 5 los (R10 niet
  geplaatst), MS1/MS2 met interne pull-down na het doorsnijden van de jumpers, CLK 20k naar GND op de module.
  Spoelparen op 11–12 en 13–14 bij beide modules.
- WIZ850io: J1 GND, GND, MOSI, SCLK, SCNn, INTn; J2 GND, 3V3, 3V3, NC, RSTn, MISO (datasheet V1.0 p.5–6). De module
  heeft zelf 4,7k pull-ups op SCNn, INTn en RSTn. TMC2240 CSN/SCK/SDI hebben interne pull-ups (p.15), dus geen
  zwevende CS tijdens MCU-reset.
- TCA9548APWR alle 24 pennen (SCPS207H), adres 0x70, RESET aan PERIPH_RST_N; kanaal 0–3 naar de poorten, 4 naar
  J701. Pull-ups naar V_SNS aan de kabelzijde; met V_SNS = 5 V blijft de MCU-zijde op 3,3 V (pass-gate).
- AOD4185: 1 G, tab D aan de ingang, 3 S aan de last — juist voor ompoolbeveiliging. AO3400A 1 G, 2 S, 3 D.
  AMS1117 1 GND, 2/tab uit, 3 in. SRV05-4 2 GND, 5 VCC, 1 en 3 aan de lijnen. BAV99 1 aan GND, 2 aan +3V3, 3 aan
  het signaal. SMBJ18A, SS34, B5819W: kathode op pad 1, juiste kant. Tantalen: pad 1 aan de plus.
- 5 V-module: 1 in, 2 GND, 3 uit; omtrek van de voet tegen de TSR 1-tekening (pennen 2,0 mm van de voorkant, pen 1
  op 3,3 mm van de zijkant): klopt, de module past maar op één manier.
- Functies uit de brief: aparte zekeringen (F101 motor, F102 logica, parallel vanaf VIN); USB voedt alleen de
  logica en kan niet terugvoeden (D1/D7 op de DevKit, D102 naar de 5 V-module); VM-meting 100k/10k → 1,55 V bij
  17 V, 2,65 V bij de TVS-klem; DRV_ENN 10k omhoog, drivers uit tijdens reset; STEP 100k omlaag; home-ingang
  verdraagt 17 V (1,3 mA door 10k in de BAV99); ventilator standaard uit, vrijloopdiode juist gepoold.

**Bord:**
- ERC 0 meldingen. DRC met `--schematic-parity`: 0 overtredingen, 0 onverbonden, 0 pariteitsfouten. Genegeerde
  controles zijn alleen silkscreen, ontbrekende courtyards en voetfilters; geen uitsluitingen.
- Modulevoeten op spiegeling: voor DevKit, WIZ850io en StepStick is de afbeelding bovenaanzicht → bord een zuivere
  draaiing (determinant +1). Socketrijen 12,7 mm uit elkaar, pad 17/18 op 2,54 en 5,08 mm van EN richting VM.
- Stroompaden: VIN_RAW en VIN 3,0 mm (F.Cu), tak naar F102 1,5 mm; VM-zone op B.Cu 3,6 mm (bus) en 5 mm
  (ooststrook) plus 2,0 mm naar elke socket, breedste pad F101.2 → VM-pennen 2,0 mm; motoruitgangen 1,0 mm over
  8,6 mm; logicarails 0,5–0,6 mm. Dunste spoor 0,19 mm, via's 0,6/0,3 en 0,8/0,4: binnen JLC's grenzen.
- Ontkoppeling: 100 µF op 8 mm en 100 nF op 2,5 mm van elke VM-pen; 100 nF bij VIO, U701, W5500 en de 5V-pen.
- Onder de modules: onder de WIZ850io niets; onder de DevKit alleen SMD tot 1,8 mm hoog; testpunten vallen net
  buiten de DevKit-omtrek.
- Gerbers: opnieuw geëxporteerd met de opdracht uit `make_gerbers.sh`; alle lagen en boorbestanden gelijk aan
  `fab/gerbers/` en aan het zip-bestand. Omtrek 100 × 80 mm, vier NPTH 3,2 mm op 4 mm uit de hoeken.
- BOM en CPL: 114 SMD-voeten = 114 BOM-regels = 114 CPL-regels; LCSC-nummers gelijk aan de schemavelden; alles op
  de bovenzijde. CPL nagerekend: JLC's voet (padposities uit `fab/easyeda_cache.json`) met de CPL-rotatie en
  -positie op het bord gelegd, pad voor pad op nummer: grootste afwijking 0,4 mm (SMB en SOT-23, bredere pads bij
  JLC), overige ≤ 0,2 mm. SOT-23 +180°, SOT-223 +180°, SOT-23-6 en TSSOP +270°, TO-252 +180° zijn dus juist.

## Wat ik niet kon controleren

- **TMC2240 en TMC2209:** alleen de uittreksels in de map; analog.com weigert geautomatiseerde toegang. Gedrag van
  SDO zonder VS (bord op alleen USB) staat er niet in.
- **Polariteit van de tantaal C7171 in JLC's bibliotheek:** de EasyEDA-API gaf geen bruikbaar antwoord op mijn
  verzoek; ik heb dat niet omzeild. De CPL legt KiCad-pad 1 (plus) op JLC-pad 1. Of JLC-pad 1 de plus is, moet in
  de JLC-preview blijken — een verkeerd om geplaatste tantaal op 3,3 V faalt als kortsluiting. Zelfde
  previewcontrole voor D101, D102, de zes B5819W, de vier BAV99, Q101, Q801, U102, U103, U701 en de SRV05's.
- **Voorraad en prijzen bij JLC**, en welke onderdelen "basic" zijn.
- **FYSETC- en Watterott-modules:** niet nagelopen; alleen de twee BTT-modules.
- **De behuizing:** alleen de maten uit de brief; B3 en de USB-ruimte zijn daarop gebaseerd.
- **Hoogte van het koellichaam** en of de AIN/DIAG0-pennen van de TMC2240-module naar beneden wijzen.
- **MT6701:** alleen datasheet Rev 0.1; de breakoutbordjes (eigen pull-ups, 3,3 of 5 V) ken ik niet.
- **Alles wat een meting vraagt:** SPI-signaalvorm over de gedeelde massa, hot-plugpiek, temperatuur van de
  GND-strook, storing op de sensorkabels.
- Het bordbestand is van 11:19 vandaag en er werd tijdens de review nog in de map gewerkt; mijn kopie was aan het
  eind van de review nog gelijk aan het bestand. Een latere wijziging valt buiten deze review.
