#!/usr/bin/env python3
"""The Rev B circuit, written as data. Run it to (re)write the schematic:  python3 hardware/tools/circuit.py

The schematic files are generated from this file and firmware/include/pins.h; the LCSC number, value and footprint of
every part are fields on its symbol, so the BOM comes from the schematic. A part without an LCSC number is one the
owner solders (through-hole) or bare copper (jumpers, test points): it is not in the JLC files.
After a change here, rerun this script, then hardware/check_netlist.py. The specs in specs/modules/ say why each part is there.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schgen import G, Circuit, Part, kicad_symbol, make_symbol, write, write_symbol_lib  # noqa: E402

HW = os.path.dirname(HERE)
PINS_H = os.path.join(HW, "..", "firmware", "include", "pins.h")
GPIO = {int(n): net for net, n in re.findall(r"^#define PIN_(\w+) (\d+)", open(PINS_H).read(), re.M)}   # gpio -> net
assert len(GPIO) == 28, "pins.h must assign 28 nets, one GPIO each"

c = Circuit("ptz-driver")
c.title, c.rev, c.date = "PTZ driver board", "B", "2026-11-11"

# ------------------------------------------------------------------ parts catalogue

# value -> (LCSC, package): all from JLC's Basic library, read through sourcing/jlc_api.py on 2026-11-11
FP_R, FP_C = "Resistor_SMD:R_{}_{}Metric", "Capacitor_SMD:C_{}_{}Metric"
METRIC = {"0603": "1608", "0805": "2012", "1206": "3216"}
RES = {"33R": "C23140", "100R": "C22775", "1k": "C21190", "2.2k": "C4190", "4.7k": "C23162", "10k": "C25804",
       "100k": "C25803", "150k": "C22807"}
CAP = {"100 nF": ("C14663", "0603"), "10 nF": ("C57112", "0603"), 
       "10 µF 25 V": ("C15850", "0805"), "22 µF": ("C45783", "0805"), "10 µF 50 V": ("C13585", "1206")}

S = {k: kicad_symbol(v) for k, v in dict(
    R="Device:R", C="Device:C", CP="Device:C_Polarized", DZ="Device:D_Zener", DS="Device:D_Schottky", F="Device:Fuse",
    NTC="Device:Thermistor_NTC", JPO="Jumper:SolderJumper_2_Open", JPB="Jumper:SolderJumper_2_Bridged",
    JP3="Jumper:SolderJumper_3_Bridged12", TP="Connector:TestPoint", H="Mechanical:MountingHole", FLG="power:PWR_FLAG").items()}
OWN = []  # the project's own symbols, written to ptz.kicad_sym


def own(name, left, right, ref="U"):
    s = make_symbol(f"ptz:{name}", left, right, ref)
    OWN.append(s)
    return s


def conn(name, names):
    return own(name, [(i + 1, n, "passive") for i, n in enumerate(names)], [], "J")


def add(ref, value, sym, fp, sheet, lcsc="", mpn="", nets=(), bom=True, **named):
    p = c.add(Part(ref, value, sym, fp, sheet, lcsc, mpn, bom))
    for i, n in enumerate(nets):
        p.net(i + 1, n)
    for k, v in named.items():
        p.net(k.lstrip("_"), v)
    return p


def res(ref, value, a, b, sheet):
    return add(ref, value, S["R"], FP_R.format("0603", METRIC["0603"]), sheet, RES[value], nets=(a, b))


def cap(ref, value, a, b, sheet):
    lcsc, pkg = CAP[value]
    return add(ref, value, S["C"], FP_C.format(pkg, METRIC[pkg]), sheet, lcsc, nets=(a, b))


def two(ref, value, kind, fp, a, b, sheet, lcsc="", mpn=""):
    return add(ref, value, S[kind], fp, sheet, lcsc, mpn, nets=(a, b))


# ------------------------------------------------------------------ symbols drawn from datasheet pin tables

P, I, O, B, W, NC = "passive", "input", "output", "bidirectional", "power_in", "no_connect"

# StepStick socket: specs/modules/drive.md (BIGTREETECH TMC2240 V1.0 manual p5). Pads 1-8 left row, 9-16 right row, 17-18 extra.
STEPSTICK = own("StepStick_Socket", [
    (1, "EN", P), (2, "SDI/MS1", P), (3, "SCK/MS2", P), (4, "CS/UART", P), (5, "SDO", P), (6, "CLK", NC), (7, "STEP", P), (8, "DIR", P),
    None, (17, "AIN/INDEX", NC), (18, "DIAG", P)], [
    (9, "VM", P), (10, "GND", P), (11, "M1", P), (12, "M2", P), (13, "M3", P), (14, "M4", P), (15, "VIO", P), (16, "GND", P)], "A")

# ESP32-S3-DevKitC-1: specs/modules/control.md (Espressif user guide v1.1). Pads 1-22 = J1, 23-44 = J3.
J1_GPIO = [4, 5, 6, 7, 15, 16, 17, 18, 8, 3, 46, 9, 10, 11, 12, 13, 14]            # J1 pins 4 to 20
J3_GPIO = [43, 44, 1, 2, 42, 41, 40, 39, 38, 37, 36, 35, 0, 45, 48, 47, 21, 20, 19]  # J3 pins 2 to 20
PAD_GPIO = {4 + i: g for i, g in enumerate(J1_GPIO)}
PAD_GPIO.update({24 + i: g for i, g in enumerate(J3_GPIO)})
DEVKIT = own("ESP32-S3-DevKitC-1", [(1, "3V3", P), (2, "3V3", P), (3, "RST", P)] + [(p, f"IO{PAD_GPIO[p]}", P) for p in range(4, 21)] +
             [(21, "5V", P), (22, "GND", P)],
             [(23, "GND", P)] + [(p, f"IO{PAD_GPIO[p]}", P) for p in range(24, 43)] + [(43, "GND", P), (44, "GND", P)], "A")

# WIZ850io: WIZnet datasheet V1.0 p5-6. Pads 1-6 = J1, 7-12 = J2.
WIZ = own("WIZ850io", [(1, "GND", P), (2, "GND", P), (3, "MOSI", P), (4, "SCLK", P), (5, "SCNn", P), (6, "INTn", P)],
          [(7, "GND", P), (8, "3V3", P), (9, "3V3", P), (10, "NC", NC), (11, "RSTn", P), (12, "MISO", P)], "A")

# TCA9548APWR, TSSOP-24: TI SCPS207H, figure 4-1 and table 4-1
TCA = own("TCA9548APW", [(24, "VCC", W), (23, "SDA", B), (22, "SCL", I), (3, "RESET", I), (1, "A0", I), (2, "A1", I), (21, "A2", I), (12, "GND", W)],
          [(4 + 2 * k if k < 4 else 5 + 2 * k, f"SD{k}", B) for k in range(8)] + [None] +
          [(5 + 2 * k if k < 4 else 6 + 2 * k, f"SC{k}", B) for k in range(8)])
SRV05 = own("SRV05-4", [(1, "IO1", P), (3, "IO2", P), (2, "GND", P)], [(4, "IO3", P), (6, "IO4", P), (5, "VCC", P)])
AMS1117 = own("AMS1117-3.3", [(3, "VIN", W)], [(2, "VOUT", P), (1, "GND", W)])
SIP3 = own("DCDC_5V_SIP3", [(1, "VIN", P)], [(3, "VOUT", P), (2, "GND", P)])
PFET = own("AOD4185", [(1, "G", I)], [(2, "D", P), (3, "S", P)], "Q")
NFET = own("AO3400A", [(1, "G", I)], [(3, "D", P), (2, "S", P)], "Q")
BAV99 = own("BAV99", [(1, "A", P), (2, "K", P)], [(3, "COM", P)], "D")
J_VH2 = conn("VH_2_SUPPLY", ["+VIN", "GND"])
J_XH4 = conn("XH_4_MOTOR", ["1", "2", "3", "4"])
J_PH4 = conn("PH_4_SENSOR", ["V", "GND", "SDA", "SCL"])
J_PH3 = conn("PH_3_HOME", ["V", "GND", "HOME"])
J_H4 = conn("HDR_4_I2C", ["V", "GND", "SDA", "SCL"])
J_H2 = conn("HDR_2_FAN", ["FAN+", "FAN-"])

FP = dict(
    STEPSTICK="ptz:StepStick_Socket", DEVKIT="ptz:ESP32-S3-DevKitC-1", WIZ="ptz:WIZ850io", SIP3="ptz:SIP3_DCDC_7805",
    DPAK="ptz:TO-252_JLC", TP="ptz:TestPoint_D1.5", SOT23="Package_TO_SOT_SMD:SOT-23", SOT236="Package_TO_SOT_SMD:SOT-23-6",
    SOT223="Package_TO_SOT_SMD:SOT-223-3_TabPin2", TSSOP24="Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
    SOD123="Diode_SMD:D_SOD-123", SMB="Diode_SMD:D_SMB", SMA="Diode_SMD:D_SMA", TANT_B="Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B",
    ELEC="Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", FUSE="Fuse:Fuseholder_TR5_Littelfuse_No560_No460", NTC="Resistor_SMD:R_0603_1608Metric",
    VH2="Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", XH4="Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
    PH4="Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical", PH3="Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
    H4="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", H2="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
    JPO="Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", JPB="Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm",
    JP3="Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm", HOLE="MountingHole:MountingHole_3.2mm_M3")
SCHOTTKY = ("B5819W", "DS", FP["SOD123"], "C8598", "B5819W")


def schottky(ref, anode, cathode, sheet):
    v, kind, fp, lcsc, mpn = SCHOTTKY
    return add(ref, v, S[kind], fp, sheet, lcsc, mpn, nets=(cathode, anode))     # pad 1 is the cathode


def jumper(ref, a, b, sheet, closed):
    return add(ref, "closed" if closed else "open", S["JPB" if closed else "JPO"], FP["JPB" if closed else "JPO"], sheet, nets=(a, b), bom=False)


# ------------------------------------------------------------------ power (POW)

sh = c.sheet("power", "Power: input protection, 5 V module, 3.3 V rails")
add("J101", "B2P-VH", J_VH2, FP["VH2"], sh, nets=("VIN_RAW", "GND"))
add("Q101", "AOD4185", PFET, FP["DPAK"], sh, "C400894", "AOD4185", G="RP_GATE", D="VIN_RAW", S="VIN")
res("R101", "150k", "RP_GATE", "VIN", sh)
res("R102", "100k", "RP_GATE", "GND", sh)
two("F101", "T 5 A", "F", FP["FUSE"], "VIN", "VM", sh)
two("F102", "T 1 A", "F", FP["FUSE"], "VIN", "VIN_L", sh)
add("D101", "SMBJ18A", S["DZ"], FP["SMB"], sh, "C19077573", "SMBJ18A", nets=("VM", "GND"))
for r in ("C101", "C102", "C103", "C104"):
    two(r, "100 µF 35 V", "CP", FP["ELEC"], "VM", "GND", sh)
cap("C105", "10 µF 50 V", "VIN_L", "GND", sh)
cap("C106", "100 nF", "VIN_L", "GND", sh)
add("U101", "5 V 1 A SIP-3", SIP3, FP["SIP3"], sh, VIN="VIN_L", GND="GND", VOUT="+5V_REG")
cap("C107", "22 µF", "+5V_REG", "GND", sh)
add("D102", "SS34", S["DS"], FP["SMA"], sh, "C8678", "SS34", nets=("+5V", "+5V_REG"))
cap("C108", "22 µF", "+5V", "GND", sh)
cap("C109", "100 nF", "+5V", "GND", sh)
add("U102", "AMS1117-3.3", AMS1117, FP["SOT223"], sh, "C6186", "AMS1117-3.3", VIN="+5V", VOUT="+3V3", GND="GND")
cap("C110", "10 µF 25 V", "+5V", "GND", sh)
add("C111", "100 µF 6.3 V", S["CP"], FP["TANT_B"], sh, "C16133", "TAJB107K006RNJ", nets=("+3V3", "GND"))
cap("C112", "100 nF", "+3V3", "GND", sh)
add("U103", "AMS1117-3.3", AMS1117, FP["SOT223"], sh, "C6186", "AMS1117-3.3", VIN="+5V", VOUT="+3V3_SNS", GND="GND")
cap("C113", "22 µF", "+5V", "GND", sh)
add("C114", "100 µF 6.3 V", S["CP"], FP["TANT_B"], sh, "C16133", "TAJB107K006RNJ", nets=("+3V3_SNS", "GND"))
add("JP101", "3V3 | 5V", S["JP3"], FP["JP3"], sh, nets=("+3V3_SNS", "V_SNS", "+5V"), bom=False)
res("R103", "100k", "VM", "VM_SENSE", sh)
res("R104", "10k", "VM_SENSE", "GND", sh)
cap("C115", "100 nF", "VM_SENSE", "GND", sh)

# ------------------------------------------------------------------ MCU and Ethernet modules (CTL)

sh = c.sheet("mcu", "MCU module, Ethernet module, SPI bus, reset")
mcu = add("A201", "ESP32-S3-DevKitC-1U", DEVKIT, FP["DEVKIT"], sh)
mcu.net(1, "MCU_3V3").net(2, "MCU_3V3").net(3, "EN").net(21, "+5V")
for pad in (22, 23, 43, 44):
    mcu.net(pad, "GND")
for pad, gpio in PAD_GPIO.items():
    net = GPIO.get(gpio)
    mcu.net(pad, {"SPI_SCK": "SPI_SCK_MCU", "SPI_MOSI": "SPI_MOSI_MCU"}.get(net, net))   # None = not connected
res("R201", "33R", "SPI_SCK_MCU", "SPI_SCK", sh)
res("R202", "33R", "SPI_MOSI_MCU", "SPI_MOSI", sh)
res("R203", "10k", "DRV_ENN", "+3V3", sh)
res("R204", "10k", "PERIPH_RST_N", "+3V3", sh)
res("R205", "10k", "DIAG_OR", "GND", sh)
schottky("D201", "PERIPH_RST_N", "EN", sh)
cap("C201", "22 µF", "+5V", "GND", sh)
cap("C202", "100 nF", "+5V", "GND", sh)
add("A202", "WIZ850io", WIZ, FP["WIZ"], sh, nets=("GND", "GND", "SPI_MOSI", "SPI_SCK", "ETH_CS_N", "ETH_INT_N",
                                                   "GND", "+3V3", "+3V3", None, "PERIPH_RST_N", "SPI_MISO"))
cap("C203", "22 µF", "+3V3", "GND", sh)
cap("C204", "100 nF", "+3V3", "GND", sh)

# ------------------------------------------------------------------ axes (DRV, ENC-02, ENC-03, ENC-05)


def axis(n):
    a = n + 2
    sh = c.sheet(f"axis{n}", f"Axis {n}: driver socket, motor, home input, sensor port")
    r, k, jp = (lambda i: f"R{a}{i:02d}"), (lambda i: f"C{a}{i:02d}"), (lambda i: f"JP{a}{i:02d}")
    add(f"A{a}01", "StepStick", STEPSTICK, FP["STEPSTICK"], sh,
        nets=("DRV_ENN", f"DRV{n}_SDI", f"DRV{n}_SCK", f"DRV{n}_CSP", f"DRV{n}_SDO", None, f"STEP{n}", f"DIR{n}",
              "VM", "GND", f"M{n}_1", f"M{n}_2", f"M{n}_3", f"M{n}_4", "+3V3", "GND", None, f"DIAG{n}"))
    add(f"J{a}01", "B4B-XH-A", J_XH4, FP["XH4"], sh, nets=[f"M{n}_{i}" for i in (1, 2, 3, 4)])
    cap(k(1), "100 nF", "VM", "GND", sh)
    cap(k(2), "100 nF", "+3V3", "GND", sh)
    res(r(1), "1k", f"DRV{n}_CS", f"DRV{n}_CSP", sh)
    schottky(f"D{a}01", f"DIAG{n}", "DIAG_OR", sh)
    jumper(jp(1), f"DRV{n}_SDI", "SPI_MOSI", sh, True)
    jumper(jp(2), f"DRV{n}_SCK", "SPI_SCK", sh, True)
    jumper(jp(3), f"DRV{n}_SDO", "SPI_MISO", sh, True)
    # home input
    add(f"J{a}02", "B3B-PH-K", J_PH3, FP["PH3"], sh, nets=("V_SNS", "GND", f"HOME{n}_IN"))
    res(r(2), "10k", f"HOME{n}_IN", "+3V3", sh)
    res(r(3), "10k", f"HOME{n}_IN", f"HOME{n}", sh)
    cap(k(3), "10 nF", f"HOME{n}", "GND", sh)
    add(f"D{a}02", "BAV99", BAV99, FP["SOT23"], sh, "C2500", "BAV99,215", A="GND", K="+3V3", COM=f"HOME{n}")
    # sensor port
    add(f"J{a}03", "B4B-PH-K", J_PH4, FP["PH4"], sh, nets=("V_SNS", "GND", f"SNS{n}_SDA", f"SNS{n}_SCL"))
    res(r(4), "100R", f"MUX{n}_SDA", f"SNS{n}_SDA", sh)
    res(r(5), "100R", f"MUX{n}_SCL", f"SNS{n}_SCL", sh)
    res(r(6), "4.7k", f"SNS{n}_SDA", f"PU{n}_A", sh)
    res(r(7), "4.7k", f"SNS{n}_SCL", f"PU{n}_A", sh)
    jumper(jp(4), f"PU{n}_A", "V_SNS", sh, True)
    res(r(8), "2.2k", f"SNS{n}_SDA", f"PU{n}_B", sh)
    res(r(9), "2.2k", f"SNS{n}_SCL", f"PU{n}_B", sh)
    jumper(jp(5), f"PU{n}_B", "V_SNS", sh, False)
    add(f"U{a}01", "SRV05-4", SRV05, FP["SOT236"], sh, "C7420376", "SRV05-4", IO1=f"SNS{n}_SDA", IO2=f"SNS{n}_SCL", IO3=None, IO4=None,
        GND="GND", VCC="V_SNS")


for n in (1, 2, 3, 4):
    axis(n)

# ------------------------------------------------------------------ multiplexer, ESD, spare port (ENC-01, -07, -08)

sh = c.sheet("sensors", "I2C multiplexer, ESD protection, spare port")
u = add("U701", "TCA9548A", TCA, FP["TSSOP24"], sh, "C130026", "TCA9548APWR", VCC="+3V3", GND="GND", SDA="I2C_SDA", SCL="I2C_SCL",
        RESET="PERIPH_RST_N", A0="GND", A1="GND", A2="GND")
for k in range(8):
    u.net(f"SD{k}", f"MUX{k + 1}_SDA" if k < 5 else None).net(f"SC{k}", f"MUX{k + 1}_SCL" if k < 5 else None)
cap("C701", "100 nF", "+3V3", "GND", sh)
res("R701", "4.7k", "I2C_SDA", "+3V3", sh)
res("R702", "4.7k", "I2C_SCL", "+3V3", sh)
add("U702", "SRV05-4", SRV05, FP["SOT236"], sh, "C7420376", "SRV05-4", IO1="AUX_SDA", IO2="AUX_SCL", IO3=None, IO4=None, GND="GND", VCC="V_SNS")
add("J701", "1x4 header", J_H4, FP["H4"], sh, nets=("V_SNS", "GND", "AUX_SDA", "AUX_SCL"))
res("R703", "100R", "MUX5_SDA", "AUX_SDA", sh)
res("R704", "100R", "MUX5_SCL", "AUX_SCL", sh)
res("R705", "4.7k", "AUX_SDA", "PU5_A", sh)
res("R706", "4.7k", "AUX_SCL", "PU5_A", sh)
jumper("JP701", "PU5_A", "V_SNS", sh, True)
res("R707", "2.2k", "AUX_SDA", "PU5_B", sh)
res("R708", "2.2k", "AUX_SCL", "PU5_B", sh)
jumper("JP702", "PU5_B", "V_SNS", sh, False)

# ------------------------------------------------------------------ fan, temperature, test points (AUX)

sh = c.sheet("io", "Fan output, board temperature, test points, mounting")
add("Q801", "AO3400A", NFET, FP["SOT23"], sh, "C20917", "AO3400A", G="FAN_G", S="GND", D="FAN_N")
schottky("D801", "FAN_N", "FAN_V", sh)
res("R801", "100R", "FAN_PWM", "FAN_G", sh)
res("R802", "100k", "FAN_G", "GND", sh)
add("JP801", "5V | VM", S["JP3"], FP["JP3"], sh, nets=("+5V", "FAN_V", "VM"), bom=False)
add("J801", "1x2 header", J_H2, FP["H2"], sh, nets=("FAN_V", "FAN_N"))
add("RT801", "NTC 10k", S["NTC"], FP["NTC"], sh, "C2892547", "KNTC0603/10KF3950", nets=("NTC_SENSE", "GND"))
res("R803", "10k", "NTC_SENSE", "+3V3", sh)
cap("C801", "100 nF", "NTC_SENSE", "GND", sh)
TESTPOINTS = ["VIN", "VM", "+5V", "+3V3", "V_SNS", "GND", "GND", "SPI_SCK", "SPI_MOSI", "SPI_MISO", "I2C_SDA", "I2C_SCL",
              "DRV_ENN", "DIAG_OR", "PERIPH_RST_N", "MCU_3V3"]
for i, net in enumerate(TESTPOINTS):
    add(f"TP{801 + i}", net, S["TP"], FP["TP"], sh, nets=(net,), bom=False)
for i in range(4):
    add(f"H{i + 1}", "M3", S["H"], FP["HOLE"], sh, bom=False)

# power flags: every net that has a supply pin gets one, so ERC knows it is driven on purpose
_supply = sorted({net for p in c.parts.values() for num, net in p.nets.items() if net and p.symbol.pins[num][4] == "power_in"})
for i, net in enumerate(_supply):
    add(f"#FLG{i + 1:02d}", "PWR_FLAG", S["FLG"], "", "power", nets=(net,), bom=False)

# ------------------------------------------------------------------ where things sit on the sheets


def layout():
    """ICs and connectors in a column on the left, small parts in rows on the right. Readable, not pretty."""
    for name, _ in c.sheets:
        parts = [p for p in c.parts.values() if p.sheet == name]
        big = [p for p in parts if len(p.symbol.pins) > 4]
        mid = [p for p in parts if 2 < len(p.symbol.pins) <= 4]
        small = [p for p in parts if len(p.symbol.pins) <= 2]
        x, y = 30, 14
        for p in sorted(big, key=lambda q: -len(q.symbol.pins)):
            rows = int((p.symbol.box[3] - p.symbol.box[1]) / G) + 4
            if y + rows > 150:
                x, y = x + 44, 14
            top = int(p.symbol.box[3] / G)
            p.at = (x * G, (y + top) * G, 0)
            y += rows + 2
        x0 = x + 40
        for i, p in enumerate(mid):
            p.at = ((x0 + (i % 2) * 22) * G, (16 + (i // 2) * 9) * G, 0)
        x1 = x0 + (46 if mid else 0)
        for i, p in enumerate(sorted(small, key=lambda q: (q.ref[0] == "#", q.ref.rstrip("0123456789"), int(re.sub(r"\D", "", q.ref) or 0)))):
            vertical = any(v[3] in (90.0, 270.0) for v in p.symbol.pins.values()) and len(p.symbol.pins) == 2
            p.at = ((x1 + (i % 4) * 22) * G, (14 + (i // 4) * 4) * G, 90 if vertical else 0)


if __name__ == "__main__":
    layout()
    for old in os.listdir(HW):                     # sheets of an earlier revision
        if old.endswith(".kicad_sch"):
            os.remove(os.path.join(HW, old))
    root = write(c, HW)
    write_symbol_lib(OWN, os.path.join(HW, "ptz.kicad_sym"))
    # read the netlist back through KiCad: what was drawn must be what was meant
    import netlist
    want = {k: [x for x in v if not x[0].startswith("#")] for k, v in c.netlist().items()}
    got = {}
    for (ref, pin), net in netlist.pin_nets(netlist.export(os.path.join(HW, root))).items():
        if not net.startswith("unconnected-"):
            got.setdefault(net, []).append((ref, pin))
    got = {k: sorted(v) for k, v in got.items()}
    assert got == want, "KiCad reads a different netlist: " + ", ".join(sorted(k for k in set(want) | set(got) if want.get(k) != got.get(k))[:10])
    print(f"{root}: {len(c.parts)} parts, {len(want)} nets, read back identical")
