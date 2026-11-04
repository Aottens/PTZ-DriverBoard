# PTZ-Head — Ontwerpdocument v1.1

3D-printbare PTZ-head voor camera's tot 2 kg. Main PCB in de voet, gevoed door een externe 12V/3A AC-DC-adapter (geen 230V in het print). Aansturing via OSC over WiFi, motoren NEMA 17 met MKS SERVO42C closed-loop drivers, hall-sensors voor nulpunt, presets met positie-lock.

> Wijzigingen v1.1: externe 12V/3A adapter i.p.v. interne Mean Well; Sweep Dynamics-drives geëvalueerd (zie §2.1).

## 1. Systeemarchitectuur

```
                 ┌──────────────────────────────┐
   OSC / WiFi ──▶│ ESP32 (main PCB, in de voet) │
                 └──────┬───────────────┬───────┘
                   UART2│           UART1│  (door holle pan-as)
                 ┌──────▼──────┐  ┌─────▼───────┐
                 │ SERVO42C    │  │ SERVO42C    │
                 │ PAN-motor   │  │ TILT-motor  │
                 │ (in voet)   │  │ (in yoke)   │
                 └─────────────┘  └─────────────┘
   Hall pan (voet) ──▶ GPIO34      Hall tilt (yoke-arm) ──▶ GPIO35
```

Verdeling van functies: de SERVO42C's doen de closed-loop positieregeling (FOC, encoder aan boord) en het vasthouden van positie ("lock"). De ESP32 doet alleen trajectplanning, homing, presets en OSC. De hall-sensors zitten op de **uitgaande assen** (niet op de motoras) omdat door de reductie één motoromwenteling ≠ één as-omwenteling; het interne zeroMode van de SERVO42C is daarom niet bruikbaar voor het output-nulpunt.

## 2. Reductie — keuze en motivatie

**Keuze: GT2 riemreductie, enkele trap.** Dit is voor 3D-print de makkelijkste én beste optie:

| Optie | Oordeel |
|---|---|
| **GT2 riem (gekozen)** | Grote pulley printbaar, motorpulley kant-en-klaar aluminium (€2), geen speling bij goede spanning, stil, dempt trillingen, tolerant voor printonnauwkeurigheid, spanning instelbaar via slobgaten |
| Geprinte tandwielen | Backlash, slijtage, hoorbaar — ongeschikt voor video |
| Planetair (geprint) | Compact maar veel speling door printtoleranties, complexe assemblage |
| Cycloïdaal | Vrijwel spelingsvrij maar gevoelig voor printtolerantie, veel onderdelen |
| Harmonic drive (geprint) | Experimenteel, flexspline in filament niet duurzaam |

### 2.1 Evaluatie Sweep Dynamics drives (kant-en-klare printbare ontwerpen)

Sweep Dynamics verkoopt uitgewerkte, deels printbare NEMA 17-drives (STL/STEP, ~$15–18) — gemeten specs van hun productpagina's:

| Drive | Ratio | Backlash | Eff. | Koppel | Formaat |
|---|---|---|---|---|---|
| 26:1 Micro Harmonic | 26:1 | ±10,5′ (0,18°) | 73,5% | 3–4 Nm | 42×42×26 |
| 20:1 Micro Cycloidal | 20:1 | ±28′ (0,47°) | 91% | 4–5 Nm | 42×42×26 |
| 26:1 HT Cycloidal | 26:1 | ±15,5′ (0,26°) | 91,5% | 6–7 Nm | 62×62×35 |
| 8:1 Lotus | 8:1 | ±24,5′ (0,41°) | 86% | 3–4 Nm | 42×42×26 |

Conclusie voor deze PTZ: **niet gekozen**. Voor pan valt de optie sowieso af (geen holle as → kabeldoorvoer onmogelijk). Voor tilt is de 26:1 Harmonic het beste alternatief: compactere arm, geen grote pulley. Maar zelfs diens 0,18° backlash is bij ingezoomd beeld zichtbaar op richtingswissel, de TPU-flexspline is een slijtdeel, en de riem is stiller. De harmonic blijft een valide tilt-variant als compactheid zwaarder weegt dan beeldkwaliteit: backlash is dan te maskeren door de camera bewust ~1 cm voorlastig te balanceren (permanent eenzijdig belast tandcontact). De yoke-arm krijgt hiervoor een alternatieve motorplaat-uitsparing in de CAD.

Ratio's:

| As | Pulleys | Ratio | Effect |
|---|---|---|---|
| Pan | 16T (alu, op motor) → 80T (geprint) | 5:1 | max ~360°/s bij 300 rpm motor, resolutie 0,016° |
| Tilt | 16T (alu) → 144T (geprint) | 9:1 | max ~200°/s, resolutie 0,009°, meer koppel voor zwaartekracht |

Riem: GT2, 6 mm breed, gesloten lus (lengte volgt uit hartafstand; motorplaten krijgen 8 mm slobgaten voor spanning). De 144T-pulley is Ø91,7 mm, de 80T Ø50,9 mm — beide printbaar in één stuk, plat op het bed.

### Koppelverificatie

- Tilt worst case (camera 2 kg + montageplaat 0,5 kg, zwaartepunt 60 mm uit de tilt-as): 1,47 Nm nodig. Beschikbaar dynamisch bij 9:1: ~2,1 Nm; statisch (lock): ~4 Nm. Marge ≥ 40%, en met een gebalanceerde camera (CG op de as, zie §3.4) daalt de belasting naar vrijwel nul.
- Pan (versnelling 360°/s² van 3,5 kg bewegende massa): ~0,18 Nm — triviaal bij 5:1.

## 3. Mechanisch ontwerp

Drie hoofdmodules: **voet**, **pan-toren met holle as**, **U-yoke met tiltplateau**.

### 3.1 Voet (Ø170 mm, hoogte 70 mm — volledige maatvoering in 03-cad-specificatie.md)

- Bevat: main PCB, pan-motor + SERVO42C, pan-riemaandrijving. Voeding extern: 12V/3A AC-DC-adapter op een DC-jack (5,5×2,5 mm) achterin de voet — geen 230V in het print, dus geen scheidingscompartiment nodig en de voet kan lager (~70 mm).
- Pan-motor hangt aan een motorplaat met slobgaten (riemspanning). NEMA 17-flens: 31×31 mm gatpatroon, M3.
- Onderzijde: 3/8"-16 en 1/4"-20 statief-inserts (messing, inlijmen/insmelten) + 4 rubberen voeten.
- Hall-sensor pan: op de voet gemonteerd, magneet (Ø6×3 neodymium, diametrisch) in de rand van de 80T-pulley.

### 3.2 Pan-as (hol, voor kabeldoorvoer)

- Geprinte holle as: buiten Ø30 mm (perspassing in bearing), binnenbore Ø22 mm.
- Twee lagers **6806-2RS** (30×42×7), verticaal ~40 mm uit elkaar in de voet-toren → hoge kantelstijfheid.
- De 80T-pulley klemt onderop de as (klemverbinding met M3-bout, geen setscrew in plastic).
- Door de bore lopen: tilt-motorkabel (24V + UART, 4 aders) en tilt-hall (3 aders) = 7 aders, ruim passend. Bovenin een trekontlasting-klem.
- **Pan-bereik: ±170° (firmware-limiet)** — kabels vormen een servicelus, geen sleepring nodig. Presets werken hier prima mee.

### 3.3 U-yoke

- U-vormige beugel op de pan-as; twee armen omhoog. U-vorm i.p.v. L-arm: dubbelzijdige ondersteuning van de tilt-as is bij 2 kg aanzienlijk stijver in print.
- Print in twee arm-delen + brugdek, verbonden met M3-bouten en inserts (past zo op een Bambu-bed en print in gunstige oriëntatie).
- Rechterarm: tilt-motor (SERVO42C naar buiten gericht — OLED zichtbaar, koeling) + 144T-pulley op de tilt-as. Linkerarm: lager **6802-2RS** (15×24×5).
- Tilt-as: 15 mm; geprint met stalen 15 mm as-stomp of volledig geprint massief (PETG-CF is stijf genoeg over deze korte lengte).
- Hall-sensor tilt in de rechterarm, magneet in de 144T-pulley.

### 3.4 Tiltplateau / camerabevestiging

- Plateau tussen de armen met 1/4"-20 kamerabout + anti-verdraaipin (videostandaard).
- **Balansverstelling**: plateau schuift ±20 mm voor/achter over zwaluwstaart met klemhendel, zodat het zwaartepunt van de camera óp de tilt-as gelegd kan worden. Dit haalt vrijwel alle statische last van de tilt-motor — cruciaal voor stille, vloeiende bewegingen en koele motoren.
- Tilt-bereik: ±90° mechanisch, firmware-limiet instelbaar.

### 3.5 Lock / presets

Geen mechanische rem: in CR_UART-mode houdt de SERVO42C de positie actief vast (FOC, positielus 10 kHz) zolang enabled. Bij "lock" zet de firmware de as op houdstroom; afwijking door aanraken wordt actief weggeregeld. Bij stroomuitval valt de positie weg → na opstarten draait de homing-routine (hall) en zijn alle presets weer geldig, want presets worden opgeslagen t.o.v. het hall-nulpunt.

### 3.6 Print-advies (Bambu Lab, PETG-CF of PLA-CF)

| Onderdeel | Materiaal | Instellingen |
|---|---|---|
| Voet, yoke-armen, motorplaten | PETG-CF (aanrader: kruipt niet onder constante belasting, warmtebestendig) | 6 wanden, 40% gyroid, 0.2 mm |
| Pulleys 80T/144T | PETG-CF of PLA-CF (tandprofiel scherper in PLA-CF) | 4 wanden, 25% infill, 0.16 mm laag voor tandkwaliteit |
| Holle pan-as | PETG-CF | 100% infill of 8 wanden, verticaal geprint |
| Afdekkappen | willekeurig | 3 wanden, 15% |

Overal M3 heat-set inserts (geen zelftappers in CF-filament). PLA-CF alleen voor delen zonder constante mechanische spanning of gebruik het hele ontwerp in PETG-CF. Lagerzittingen: print 0,1 mm ondermaats en ruim op maat, of ontwerp met 0,15 mm perspassing-compensatie.

## 4. Elektronica-overzicht

| Blok | Keuze |
|---|---|
| Voeding | Externe 12V/3A AC-DC-adapter (36 W), DC-jack 5,5×2,5 mm in de voet |
| Drivers | 2× MKS SERVO42C V1.1 (7–28 V, dus 12 V toegestaan), current-gear **1,0–1,2 A** |
| MCU | ESP32-WROOM-32E op custom PCB (zie 02-pcb-specificatie.md) |
| Hall | 2× 3,3V digitale omnipolaire hall-switch (bv. TI DRV5032FB of AH1815) + Ø6×3 magneet |
| Netwerk | WiFi (OSC over UDP, poort 8000) |

SERVO42C-configuratie per motor (eenmalig via het schermpje of firmware): CtrMode = CR_UART, Mstep = 16, MotType = 1.8°, UartAddr pan = e0, tilt = e1, baud 38400. Beide drivers kunnen dan desgewenst zelfs op één UART-bus, maar het PCB voorziet twee aparte UARTs (robuuster, geen adresafhankelijkheid).

Consequenties 12 V i.p.v. 24 V: holdkoppel (lock) ongewijzigd — dat is stroombegrensd. Bij hogere toerentallen zakt het koppel eerder door beperkte spanningsmarge; onze max motorsnelheid (~300 rpm) blijft haalbaar, maar houd de ACC-parameter gematigd. Budget 3 A totaal: current-gear max 1,2 A per driver en beide assen niet gelijktijdig maximaal laten accelereren (firmware faseert preset-recalls licht).

## 5. Stuklijst (kopen)

| # | Onderdeel | Aantal | Indicatie |
|---|---|---|---|
| 1 | Pan: 17HS13-0404D dual-shaft 34 mm · Tilt: NEMA 17 dual-shaft 40 mm ≥0,4 Nm (achteras verplicht voor encoder) | 2 | €30 |
| 2 | MKS SERVO42C V1.1 | 2 | €50 |
| 3 | AC-DC adapter 12V/3A + DC-jack 5,5×2,5 mm (panel mount) | 1 | €15 |
| 4 | GT2 pulley 16T, bore 5 mm, alu | 2 | €4 |
| 5 | GT2 riem gesloten, 6 mm (lengtes volgen uit CAD-hartafstand) | 2 | €8 |
| 6 | Lager 6806-2RS | 2 | €8 |
| 7 | Lager 6802-2RS | 1 | €3 |
| 8 | Hall-switch DRV5032/AH1815 + magneet Ø6×3 | 2+2 | €4 |
| 9 | Custom main PCB (JLC/PCBWay, assembled) | 1 | €30–60 |
| 10 | M3 heat-set inserts, M3 bouten, JST-XH connectorset | — | €15 |
| 11 | 1/4"-20 + 3/8"-16 inserts, kamerabout | — | €8 |

Totaal indicatief: **€185–215** (excl. filament).

## 6. Vervolg

1. CAD uitwerken (kan als parametrische OpenSCAD in een volgende sessie).
2. PCB: zie `02-pcb-specificatie.md`.
3. Firmware: zie `firmware/` (PlatformIO-skelet, OSC-adressenlijst in de README daar).
4. Toekomstige optie: fysieke bedienconsole (tweede ESP32 + joystick + OLED) die dezelfde OSC-berichten stuurt — het protocol is daarop voorbereid.
