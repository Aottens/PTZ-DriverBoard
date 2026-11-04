# CAD-specificatie & maatvoering v1.0

Concrete maatvoering voor het 3D-ontwerp. Coördinatensysteem: Z omhoog, Z=0 = bovenkant voetbodem. Alle maten in mm. Bijbehorende maattekening: `maattekening.svg`.

## 1. Hoofdmaten

| | Maat |
|---|---|
| Voet | Ø170 × **70 hoog** (excl. 6 mm rubbervoetjes) |
| Yoke-deck bovenkant | Z = 82 |
| Tilt-as hoogte | Z = 212 (130 boven deck) |
| Totale hoogte t/m armtop | ~275 |
| Breedte over de armen | 200 |
| Pan-bereik | ±170° · Tilt-bereik ±90° |

De voet komt van 90 → **70 mm** door drie ingrepen: platte pan-motor 17HS13-0404D (34 i.p.v. 40 mm), SERVO42C-board verzonken in een bodempocket (−6 mm, binnen de voetjeshoogte), en het riemvlak hoog in de voet zodat toren en motor dezelfde verticale zone delen.

## 2. Voet (Z 0–70)

### 2.1 Verticale stack (pan-aandrijving)

| Onderdeel | Z-bereik | Opmerking |
|---|---|---|
| Bodemplaat | −4–0 | met pocket −6–+7 voor SERVO42C (board wijst omlaag; OLED alleen voor setup nodig) |
| Pan-motor 17HS13-0404D | 7–41 | flens boven, hangend aan motorplaat |
| Motorplaat | 41–45 | 4 dik, **slobgaten 8 lang** radiaal (riemspanning) |
| 16T pulley (alu, boring 5) | 45–57 | tanden 50–56 |
| 80T pulley (geprint, deel van as) | 48–60 | tanden 50–56 → riemvlak Z≈53 |
| Deksel | 66–70 | opening Ø64 met labyrintrand |

### 2.2 Pan-toren en holle as

| | Maat |
|---|---|
| Toren (stationair) | buiten Ø54, Z 0–48, vast aan bodem (of één print met voet) |
| Lagers 2× 6806-2RS (30×42×7) | zittingen in toren: onder Z 12–19, boven Z 40–47 |
| Holle as (één print: as + 80T + topflens) | Z 8–66, buiten Ø30 op lagerzones, **bore Ø22** |
| Topflens | Ø60, Z 60–66, 6× M3-insert op steek Ø48 (deck-bevestiging) |
| Borgring onder onderste lager | geprinte ring Ø30 klem/M3, Z 8–12 |
| Kabelinvoer | onder de as, 8 mm vrije hoogte boven bodem; bundel ≤ Ø6 (7 aders) |

### 2.3 Plattegrond (bovenaanzicht)

| Element | Positie t.o.v. centrum |
|---|---|
| Pan-as | centrum |
| Pan-motor hart | 48 naar achteren (**C = 48**, riem GT2 gesloten **200 mm**) |
| Main PCB (90×70) | voorzijde, in bodempocket-zone |
| DC-jack 5,5×2,5 | achterwand, Z ≈ 25 |
| Hall-sensor pan | in torenwand Z 62; magneet Ø6×3 in rand topflens |
| 2× 1/4"-20 + 1× 3/8"-16 inserts | onderzijde op ±40 van centrum (centrum is bezet door kabeldoorvoer — statiefmontage dus off-center of via cheese-plate patroon 4× 1/4" op 60×60) |
| Wanddikte | 3; bodem 4 |

Riemomspanning 16T bij C=48: ~130° → 5,8 tanden in ingrijping. Voldoende bij deze lage last; voorzie optioneel twee F695-idlerposities naast de kleine pulley.

## 3. U-frame (yoke)

### 3.1 Deck

| | Maat |
|---|---|
| Plaat | 180 × 90 × 10, centraal 6× M3 op steek Ø48 naar topflens |
| Kabeldoorvoer | Ø24 gat centraal + trekontlastingsklem |
| Hoogte boven deksel | 2 mm spleet (deck onderkant Z 72, bovenkant 82) |

### 3.2 Armen (print elk als één deel, plat op zij op het bed)

| | Links | Rechts |
|---|---|---|
| Voetafdruk op deck | 60 × 22 | 60 × 22 + motorpod |
| Doorsnede lijf | kokervormig 55 breed × 22 dik, wand 4 | idem |
| Kop | Ø60 schijf rond tilt-as | **Ø112** schijf (huisje om 144T-pulley Ø94) |
| Armhoogte (deck → tilt-as) | 130 | 130 |
| Lager(s) | 1× 6802-2RS (15×24×5) | 2× 6802-2RS (binnen- én buitenwand) |
| Inwendige holte kop | — | 14 breed (144T-pulley 12 breed incl. flenzen) |
| Onderlinge afstand armen (binnenkant) | **150** | |

### 3.3 Tilt-aandrijving (in rechterarm)

| | Maat |
|---|---|
| Tilt-motor | NEMA 17 dual-shaft 40 mm (bv. 17HS15-1684D), hart **91 onder tilt-as** (Z 121) |
| Motorpod | uitwendig op rechterarm: 46×46×58 (motor 42 + board 13 + kap 3), slobgaten 8 in podflens |
| 16T pulley | op motoras, in lijn met arm-holte |
| Riem | GT2 gesloten **360 mm**, riemvlak in arm-holte |
| 144T pulley | geprint, één deel met rechter tilt-stub + flens Ø40 (4× M3 naar plateauwang) |
| Hall-sensor tilt | in rechterarmkop Z 212+40; magneet in 144T-rand |

### 3.4 Tilt-as en cameraplateau

| | Maat |
|---|---|
| Stub-assen | Ø15, links vrij (in 6802), rechts aangedreven (één print met 144T) |
| Plateau | 146 breed × 90 diep × 8 dik, bovenvlak **40 onder tilt-as** (Z 172) |
| Zijwangen (cradle) | 8 dik, verbinden plateau met stub-flenzen |
| Balansverstelling | zwaluwstaartslede ±20 voor/achter, M4-klemhendel |
| Camerabevestiging | 1/4"-20 doorsteekbout in sleuf 60 lang + anti-verdraaipin |
| Vrije draaicirkel | camera-radius max 120 vanaf tilt-as (10 marge op deck) |

## 4. Geprinte onderdelen (overzicht)

| # | Deel | Envelop (mm) | Oriëntatie | Materiaal |
|---|---|---|---|---|
| P1 | Voetschaal + toren | Ø170×70 | opening boven | PETG-CF, 6 wanden |
| P2 | Deksel voet | Ø170×8 | plat | PETG-CF |
| P3 | Holle as + 80T + flens | Ø60×62 | verticaal, tanden onder → **tanden omhoog printen** (flens onder) | PETG-CF/PLA-CF, 100% |
| P4 | Motorplaat pan | 60×60×4 | plat | PETG-CF |
| P5 | Yoke-deck | 180×90×10 | plat | PETG-CF |
| P6 | Arm links | 60×22×195 | op zij | PETG-CF |
| P7 | Arm rechts + podflens | 112×80×195 | op zij | PETG-CF |
| P8 | 144T + tilt-stub rechts | Ø94×30 | tanden boven | PLA-CF, 0.16 laag |
| P9 | Tilt-stub links + flens | Ø40×20 | staand | PETG-CF |
| P10 | Plateau + zwaluwstaart | 146×90×20 | plat | PETG-CF |
| P11 | Motorpod-kap, kabelclips | div. | — | vrij |

Alles past op een Bambu-bed (256×256). Lagerzittingen 0,15 ondermaats printen en naruimen; M3 heat-set inserts overal.

## 5. Gewijzigde inkooponderdelen t.o.v. stuklijst v1.1

| Onderdeel | Was | Wordt |
|---|---|---|
| Pan-motor | NEMA 17 40 mm | **17HS13-0404D** dual-shaft 42×42×34, 0,26 Nm, 0,4 A (~€12) |
| Tilt-motor | NEMA 17 40 mm | dual-shaft verplicht (achteras = encodermagneet), bv. 17HS15-1684D — of SERVO42C-bundel mét motor |
| Riemen | 2× n.t.b. | GT2 gesloten 200 mm (pan) + 360 mm (tilt), 6 breed |

Let op: échte pancakes (20–25 mm) en NEMA 14 zijn **niet** bruikbaar: SERVO42C vereist het 42×42-gatpatroon en een uitstekende achteras voor de encodermagneet; pancakes zijn single-shaft.
