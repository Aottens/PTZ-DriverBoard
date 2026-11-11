"""Where the parts sit on Rev B. All numbers in mm, origin at the board's top-left corner, x east, y south.

The south edge (y = BOARD_H) faces the pan motor. Every part has its place here: POS[ref] = (x, y, rotation, anchor).
The anchor is "c" (the centre of the courtyard) or the name of a pad that must land on (x, y), which is what
matters for a header that has to line up with a module. Rotation is counter-clockwise as seen from the top.

The floor plan, north to south:
  y  0 .. 9    motor connectors and one bulk capacitor per driver
  y 11 .. 27   the four driver modules, motor supply pins north, logic pins south; VM runs along y 8 .. 12 on the bottom
  y 27 .. 39   the drivers' bus jumpers, then the channel where step, direction and the bus run to the MCU
  y 39 .. 65   the MCU module (USB at the west edge); east of it the power input, and the Ethernet module (jack east)
  y 65 .. 80   sensor ports and home inputs, one cell per axis
"""
BOARD_W, BOARD_H = 100.0, 80.0
HOLES = [(4.0, 4.0), (96.0, 4.0), (4.0, 76.0), (96.0, 76.0)]
XK = [12.5, 33.5, 54.5, 75.5]      # x of pad 9 (VM) of each driver socket; the modules are 21.0 mm apart
Y_PWR, Y_LOG = 13.0, 25.7          # the sockets' north row (VM, GND, motor, VIO) and south row (EN ... DIR)
CX = [7.8 + 20.4 * k for k in range(4)]   # west edge of each axis' sensor cell along the south edge
Y_CONN = 76.6                      # pin row of the sensor and home connectors
MCU = (61.3, 40.5)                 # pad 1 of the MCU module (J1 pin 1): J1 runs west from here, J3 is 22.86 mm south
ETH = (90.6, 49.6)                 # pad 1 of the Ethernet module: J1 runs west from here, J2 is 20.32 mm south
P = 2.54

POS = {}


def at(ref, x, y, rot=0, anchor="c"):
    assert ref not in POS, ref
    POS[ref] = (round(x, 3), round(y, 3), rot, anchor)


for i, (hx, hy) in enumerate(HOLES):
    at(f"H{i + 1}", hx, hy)

# ---------------------------------------------------------------- the four axes
for k, x in enumerate(XK):
    n, a = k + 1, k + 3
    at(f"A{a}01", x, Y_PWR, 90, "9")                     # socket: pad 9 (VM) north-west, pad 1 (EN) south-west
    at(f"J{a}01", x + 5.14, 4.4, 0, "1")                 # motor connector straight north of socket pads 11 to 14
    at(f"C10{n}", x - 0.2, 5.0, 180, "1")                # bulk capacitor: plus over the VM pin, minus to the west
    at(f"C{a}01", x + 1.27, 15.4, 0)                     # 100 nF across VM and GND, under the module
    at(f"C{a}02", x + 16.51, 15.4, 0)                    # 100 nF across VIO and GND, under the module
    at(f"D{a}01", x + 4.0, Y_LOG - 2 * P, 180)           # DIAG diode beside socket pad 18, anode west
    at(f"JP{a}01", x + 2.45, 29.0, 270)                  # bus jumpers south of pads 2, 3 and 5, outside the module
    at(f"JP{a}02", x + 5.17, 29.0, 270)
    at(f"R{a}01", x + 7.75, 29.0, 90)                    # 1 k in the select line, south of pad 4
    at(f"JP{a}03", x + 10.16, 29.0, 270)
    # home input and sensor port: connectors on the south edge, their parts north of them
    cx = CX[k]
    yb = 69.6 if k < 3 else 66.6                         # cell 4 lies under the Ethernet module's south pin row
    at(f"J{a}02", cx + 2.5, Y_CONN, 0, "1")
    at(f"J{a}03", cx + 11.7, Y_CONN, 0, "1")
    at(f"R{a}02", cx + 4.9, 72.75, 90)                   # home pull-up
    at(f"R{a}03", cx + 6.5, 72.75, 90)                   # home series resistor, north of the connector's pin 3
    at(f"C{a}03", cx + 6.5, 69.6, 90)
    at(f"D{a}02", cx + 3.0, 69.4, 0)                     # clamp
    at(f"JP{a}04", cx + 9.5, 72.95, 0)                   # pull-up jumpers: 4.7 k (closed) and 2.2 k (open)
    at(f"JP{a}05", cx + 12.95, 72.95, 0)
    at(f"R{a}04", cx + 16.2, 73.35, 0)                   # 100 R in SDA and SCL, north of the connector's pins 3 and 4
    at(f"R{a}05", cx + 19.2, 73.35, 0)
    for i, r in enumerate((6, 7, 8, 9)):
        at(f"R{a}0{r}", cx + 10.3 + 1.6 * i, yb, 270)    # pull-ups, their jumper side south
    at(f"U{a}01", cx + 18.4, yb - 0.2, 0)                # ESD array at the port

# ---------------------------------------------------------------- MCU module and what hangs on its pins
at("A201", *MCU, 270, "1")


def j1(pin):
    """x of pin 1..22 of the MCU module's north row (J1); the south row (J3) has the same x per pin number."""
    return MCU[0] - (pin - 1) * P


at("R201", j1(5), 37.4, 90)        # 33 R in the SPI clock, north of GPIO5
at("R202", j1(4), 37.4, 90)        # 33 R in MOSI, north of GPIO4
at("D201", j1(3), 36.4, 90)        # reset diode, cathode at the RST pin
at("R203", j1(20), 37.4, 90)       # enable pull-up, north of GPIO14
at("R205", j1(14), 37.4, 90)       # DIAG_OR pull-down, north of GPIO46
at("C201", 9.23, 43.2, 180)        # across the 5V and GND pins, under the module
at("C202", 9.23, 45.1, 180)
at("TP816", 60.0, 36.5)            # MCU_3V3
at("TP815", 58.6, 33.6)            # PERIPH_RST_N
at("TP814", 30.6, 34.3)            # DIAG_OR
# under the MCU module: the multiplexer and the two analog inputs' parts
at("U701", 40.0, 52.5, 0)
at("C701", 45.5, 49.6, 0)
at("R701", 45.7, 51.6, 0)
at("R702", 45.7, 53.2, 0)
at("R204", 45.5, 47.9, 180)       # reset pull-up, its 3.3 V end beside C701's
at("R104", j1(4), 60.2, 90)        # VM_SENSE: lower divider resistor and its capacitor at GPIO1
at("C115", j1(4) + 1.7, 60.2, 90)
at("C801", j1(5), 60.2, 90)        # NTC_SENSE at GPIO2
at("R803", j1(5) - 1.7, 60.2, 90)
at("RT801", 50.3, 29.0, 0)         # the thermistor itself between the second and third driver
at("TP811", j1(8), 66.5)           # I2C_SDA and I2C_SCL, south of GPIO40 and GPIO39
at("TP812", j1(9), 66.5)

# ---------------------------------------------------------------- Ethernet module
at("A202", *ETH, 270, "1")
at("C203", 91.8, 66.4, 180)
at("C204", 91.9, 64.3, 180)

# ---------------------------------------------------------------- power input, east
at("J101", 94.4, 45.2, 90, "1")    # plus south, minus north, at the east edge
at("Q101", 84.5, 41.0, 270, "o")   # tab (drain) south towards J101, source and gate north
at("R101", 84.5, 35.2, 180)        # gate to source
at("R102", 89.0, 40.5, 270)        # gate to ground
at("F101", 90.5, 33.0, 0, "1")     # motor fuse: VIN west, VM east
at("F102", 74.08, 32.35, 180, "1") # logic fuse: VIN east, VIN_L west
at("TP801", 79.0, 33.1)            # VIN
at("TP802", 97.3, 26.0)            # VM
at("TP807", 97.3, 12.2)            # GND
at("D101", 97.3, 20.5, 270)        # TVS on the VM strip, cathode north
at("C105", 65.0, 33.5, 90)
at("C106", 62.4, 33.5, 90)
at("U101", 67.06, 44.85, 0, "1")   # 5 V module, pins on its south side: in west, out east
at("C107", 74.5, 48.15, 0)
at("D102", 67.4, 48.95, 0)          # cathode (+5V) west
at("U102", 67.5, 55.3, 270, "o")   # 3.3 V regulator: input north-west, tab (output) south
at("C110", 61.6, 52.2, 90)         # the 5 V capacitors under the antenna end of the MCU module
at("C108", 59.4, 50.2, 90)
at("C109", 61.6, 48.4, 90)
at("C111", 67.5, 62.0, 0)
at("C112", 67.5, 64.9, 0)
at("TP803", 64.2, 66.6)            # +5V
at("TP804", 70.4, 66.6)            # +3V3

# ---------------------------------------------------------------- sensor supply, south-west corner
at("U103", 17.5, 51.0, 0, "o")     # under the west half of the MCU module, next to its 5V pin: input south-west, tab east
at("C113", 11.4, 53.3, 180)
at("C114", 17.5, 57.6, 180)
at("JP101", 4.3, 68.4, 0)
at("TP805", 7.7, 68.4)             # V_SNS

# ---------------------------------------------------------------- west column: spare I2C port, fan, test points
at("J701", 2.2, 10.9, 0, "1")
at("U702", 6.6, 10.4, 0)
at("R103", 9.4, 13.0, 180)         # VM_SENSE: upper divider resistor at the west end of the VM bus
at("R703", 6.2, 14.9, 0)
at("R704", 6.2, 16.5, 0)
at("R705", 9.3, 14.9, 0)
at("R706", 9.3, 16.5, 0)
at("R707", 6.2, 18.1, 0)
at("R708", 9.3, 18.1, 0)
at("JP701", 6.05, 20.4, 0)
at("JP702", 9.15, 23.1, 0)
at("J801", 2.2, 23.0, 0, "1")      # fan
at("JP801", 6.7, 26.0, 0)          # fan supply: 5 V west, VM east
at("Q801", 6.2, 29.3, 0)
at("D801", 10.3, 30.3, 90)
at("R801", 2.4, 30.0, 90)
at("R802", 2.4, 33.4, 90)
for i, ref in enumerate(("TP806", "TP813", "TP808", "TP809")):   # GND, ENN, SCK, MOSI
    at(ref, 1.6 + 2.5 * i, 37.2)
at("TP810", 9.1, 34.6)             # MISO

# ---------------------------------------------------------------- copper laid before routing (tools/board.py)
# (net, layer, polygon): the paths that carry the supply current are pours, so their width is known (BRD-06)
ZONES = [
    # VM: along the north row of the sockets, with a branch from each bulk capacitor's plus pad to its socket's VM
    # pad, and down the east edge to the fuse; on the bottom
    ("VM", "B.Cu", [(9.2, 8.3)] + [p for x in XK for p in ((x - 1.25, 8.3), (x - 1.25, 4.0), (x + 1.25, 4.0), (x + 1.25, 8.3))] +
     [(99.6, 8.3), (99.6, 34.6), (94.4, 34.6), (94.4, 31.4), (94.6, 31.4), (94.6, 11.9)] +
     [p for x in reversed(XK) for p in ((x + 1.25, 11.9), (x + 1.25, 13.9), (x - 1.25, 13.9), (x - 1.25, 11.9))] + [(9.2, 11.9)]),
]
# (net, layer, width, [points]): motor outputs, straight from socket to connector
TRACKS = []
for k, x in enumerate(XK):
    for i in range(4):
        TRACKS.append((f"M{k + 1}_{i + 1}", "F.Cu", 1.0, [(x + 5.08 + P * i, Y_PWR), (x + 5.14 + 2.5 * i, 4.4)]))
# The supply path as tracks of a known width as well: a router treats a pour as a plane it may cut, a track it leaves
# whole. VM on the bottom along the sockets and down the east edge; VIN_RAW from connector to the FET's tab; VIN from
# the FET's source to both fuses.
TRACKS.append(("VM", "B.Cu", 3.4, [(10.9, 10.1), (97.1, 10.1)]))
TRACKS.append(("VM", "B.Cu", 4.6, [(97.1, 10.1), (97.1, 33.0)]))
TRACKS.append(("VM", "B.Cu", 2.0, [(97.1, 33.0), (95.58, 33.0)]))
for x in XK:
    TRACKS.append(("VM", "B.Cu", 2.0, [(x - 0.2, 5.0), (x - 0.1, 5.6), (x - 0.1, 12.4), (x, Y_PWR)]))
TRACKS.append(("VIN_RAW", "F.Cu", 3.0, [(84.5, 45.2), (94.4, 45.2)]))
TRACKS.append(("VIN", "F.Cu", 3.0, [(90.5, 33.0), (90.0, 32.85), (82.2, 32.85)]))
TRACKS.append(("VIN", "F.Cu", 1.2, [(82.214, 32.85), (82.214, 37.525)]))
TRACKS.append(("VIN", "F.Cu", 1.5, [(82.2, 32.85), (74.08, 32.35)]))
# the sensor supply: a riser up the west edge to the spare port, and a trunk along the south edge on the bottom, south of the connectors, with a stub up to pin 1 of each
TRACKS.append(("V_SNS", "B.Cu", 0.6, [(CX[0] + 2.5, Y_CONN), (8.9, 75.2), (8.9, 66.6), (6.3, 66.6), (3.2, 63.5), (0.8, 61.1),
                                      (0.8, 10.9), (2.2, 10.9)]))
TRACKS.append(("V_SNS", "B.Cu", 0.6, [(CX[0] + 2.5, 78.7), (CX[3] + 11.7, 78.7)]))
for cx in CX:
    for dx in (2.5, 11.7):
        TRACKS.append(("V_SNS", "B.Cu", 0.6, [(cx + dx, Y_CONN), (cx + dx, 78.7)]))
# each port's ESD array has its supply pin on the far side from the connector: a via beside it and a track on the
# bottom straight south to the trunk (port 4 has its own way round, below)
for cx in CX[:3]:
    TRACKS.append(("V_SNS", "F.Cu", 0.5, [(cx + 19.54, 69.4), (cx + 20.6, 69.4)]))
    TRACKS.append(("V_SNS", "B.Cu", 0.5, [(cx + 20.6, 69.4), (cx + 20.6, 78.7)]))
# the fan jumper's VM pad: a short track east, a via, and north on the bottom to the west end of the VM bus
TRACKS.append(("VM", "F.Cu", 0.6, [(8.0, 26.0), (9.9, 26.0)]))
TRACKS.append(("VM", "B.Cu", 0.6, [(9.9, 26.0), (9.9, 11.0)]))
# the ESD array of port 4 sits under the Ethernet module, shut in by its pin row: its supply pin goes round the east
TRACKS.append(("V_SNS", "F.Cu", 0.5, [(CX[3] + 19.54, 66.4), (89.8, 66.4), (89.8, 64.2)]))
TRACKS.append(("V_SNS", "B.Cu", 0.5, [(89.8, 64.2), (93.4, 64.2), (93.4, 72.0), (91.0, 74.4), (91.0, 78.7), (CX[3] + 11.7, 78.7)]))
# (net, x, y): vias from the TVS's cathode pad down to the VM strip, and the vias of the tracks above
VIAS = [("VM", 96.2, 16.9), ("VM", 97.3, 16.9), ("VM", 98.4, 16.9), ("V_SNS", 6.3, 66.6), ("VM", 9.9, 26.0), ("V_SNS", 89.8, 64.2)] + [("V_SNS", cx + 20.6, 69.4) for cx in CX[:3]]

# ---------------------------------------------------------------- silkscreen names (tools/silk.py)
TP_NAMES = {"+5V": "5V", "+3V3": "3V3", "V_SNS": "VSNS", "SPI_SCK": "SCK", "SPI_MOSI": "MOSI", "SPI_MISO": "MISO",
            "I2C_SDA": "SDA", "I2C_SCL": "SCL", "DRV_ENN": "ENN", "DIAG_OR": "DIAG", "PERIPH_RST_N": "RST", "MCU_3V3": "M3V3"}
