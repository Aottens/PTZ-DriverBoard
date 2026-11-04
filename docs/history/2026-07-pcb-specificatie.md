# Main PCB — Specificatie & KiCad-schema-opzet v1.1

Custom PCB in de voet. Functie: 12V-distributie naar de twee SERVO42C's, ESP32 met WiFi, 2× UART, 2× hall-input, USB-C voor programmeren/debug. Voeding: externe 12V/3A adapter.

## 1. Blokschema

```
12V/3A adapter ─▶ DC-jack ─▶ [12V rail] ─┬─▶ XT30 → SERVO42C PAN
                                         ├─▶ XT30 → SERVO42C TILT (kabel door pan-as)
                                         └─▶ Fuse ▸ TVS ▸ P-FET (ompool) ▸ Buck 12→5V ▸ Buck 5→3.3V
                                                                          │            │
                                                                     USB-C/CH340C   ESP32-WROOM-32E
                                                                                       ├─ UART2 → PAN driver
                                                                                       ├─ UART1 → TILT driver
                                                                                       ├─ GPIO34/35 ← hall ×2
                                                                                       └─ I2C + spare header
```

## 2. Componentkeuzes

| Ref | Component | Opmerking |
|---|---|---|
| U1 | ESP32-WROOM-32E-N8 | module, geen externe antenne nodig; PCB-zone eronder vrij van koper |
| U2 | TPS54302DDCR | buck 12→5 V, 3 A; L 10 µH, Cout 2×22 µF |
| U3 | AP62201WU-7 (of SY8089) | buck 5→3,3 V, 1 A (ESP32 WiFi-pieken ~500 mA) |
| U4 | CH340C | USB-UART, geen extern kristal |
| Q1 | AO3401 P-FET | omvoolbeveiliging 12V-ingang laagspanningszijde |
| Q2,Q3 | MMBT2222 (2N7002 mag ook) | auto-reset/boot circuit (EN/IO0) standaard NodeMCU-schakeling |
| D1 | SMBJ15A | TVS op 12V rail |
| F1 | polyfuse 500 mA | alleen voor het logica-pad; motorstroom loopt buiten deze zekering om |
| J1 | DC-jack DC-005 (5,5×2,5 mm), of 2P schroefklem naar panel-mount jack | 12V in vanaf externe adapter |
| J2,J3 | XT30 of schroefklem | 12V uit naar SERVO42C VIN/GND |
| J4,J5 | JST-XH 4P | UART naar drivers: 3V3(nc)/GND/TX/RX — SERVO42C is 3,3V-logica, direct koppelbaar |
| J6,J7 | JST-XH 3P | hall: 3V3/GND/OUT |
| J8 | USB-C 16P (5,1k CC-pulldowns) | programmeren |
| J9 | JST-XH 4P | I2C reserve (OLED/uitbreiding) |
| SW1,SW2 | tactiel | EN (reset), IO0 (boot) |
| LED1,LED2 | 0603 | power 3V3, status (GPIO2) |

## 3. Netlist (schema-connectiviteit)

Voedingsnetten:

```
+12V_IN : J1.1 → F_motor-pad: J2.1, J3.1 ; via Q1(omvool)+F1 → U2.VIN, D1
GND     : J1.2, J2.2, J3.2, alle GND-pinnen (één massavlak)
+5V     : U2.SW→L1→(+5V): U3.VIN, U4.VCC, J8.VBUS(via diode niet nodig — USB voedt NIET de 5V rail; scheid met schottky B5819: VBUS→D2→+5V)
+3V3    : U3.uit → U1.3V3, pull-ups, J4.1/J5.1(optioneel), J6.1, J7.1, J9.1
```

ESP32 (U1) pintoewijzing:

| GPIO | Net | Naar |
|---|---|---|
| EN | ESP_EN | 10k→3V3, 100 nF→GND, SW1, Q2 (auto-reset) |
| IO0 | ESP_BOOT | SW2, Q3 (auto-boot) |
| IO1/IO3 (UART0) | USB_TX/USB_RX | CH340C RXD/TXD |
| IO16 | PAN_RX | J4.4 (driver TX) |
| IO17 | PAN_TX | J4.3 (driver RX) |
| IO25 | TILT_RX | J5.4 |
| IO26 | TILT_TX | J5.3 |
| IO34 | HALL_PAN | J6.3 + 10k pull-up naar 3V3 + 100 nF (34/35 hebben géén interne pull-up) |
| IO35 | HALL_TILT | J7.3 + 10k pull-up + 100 nF |
| IO21/IO22 | SDA/SCL | J9 + 4k7 pull-ups |
| IO2 | STATUS_LED | LED2 via 1k |

CH340C (U4): V3 → 100 nF naar VCC (5V-mode), UD+/UD- → J8, RTS/DTR → auto-programcircuit (standaard twee-transistor schakeling naar EN/IO0).

## 4. KiCad-werkvolgorde

1. Nieuw project, schema in vier hiërarchische bladen: `power`, `mcu`, `usb`, `io`.
2. Symbolen: alles zit in de standaard KiCad-libs behalve ESP32-WROOM-32E (lib: `RF_Module:ESP32-WROOM-32E`) — zit er ook in sinds KiCad 6.
3. Voer bovenstaande netten in; ERC moet schoon zijn op "power input not driven" na (PWR_FLAG op +12V_IN en GND).
4. Layout-richtlijnen:
   - 2-laags, 35 µm; 12V-motorsporen ≥ 2 mm of polygonen.
   - Bucks: korte hot-loop, Cin direct bij VIN-pin.
   - ESP32-antennegebied buiten de printrand laten steken of keep-out zone zonder koper/GND.
   - USB D+/D− als 90 Ω differentieel paar (kort, niet kritisch bij full-speed).
   - Hall- en UART-connectors aan de zijde van de pan-toren (korte kabels naar de doorvoer).
5. Boardvorm: pas in de voet, Ø of rechthoek ~90×70 mm, M3-gaten op de hoeken.

## 5. Ontwerpnotities

- SERVO42C UART is 3,3 V TTL — geen level shifter nodig.
- De 12V-motorvoeding loopt via dikke sporen rechtstreeks van J1 naar J2/J3; alleen het logica-pad heeft omvool- en overspanningsbeveiliging. De drivers hebben eigen ingangsbescherming.
- USB mag nooit de 12V-keten voeden: schottky-scheiding op VBUS.
- Adapterbudget 3 A: stel de SERVO42C current-gear op max 1,2 A per driver; de firmware faseert gelijktijdige preset-moves.
- Testpunten: TP1 +12V, TP2 +5V, TP3 +3V3, TP4/TP5 UART TX pan/tilt.
