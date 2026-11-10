#!/usr/bin/env python3
"""The Rev A circuit, written as data. Run it to (re)write the schematic:  python3 hardware/tools/circuit.py

The schematic files are generated from this file and firmware/include/pins.h; the LCSC number, value and footprint of
every part are fields on its symbol, so the BOM comes from the schematic. After a change here, rerun this script,
then hardware/check_netlist.py. The specs in specs/modules/ say why each part is there.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schgen import G, Circuit, Part, kicad_symbol, make_symbol, write, write_symbol_lib  # noqa: E402

HW = os.path.dirname(HERE)
PINS_H = os.path.join(HW, "..", "firmware", "include", "pins.h")
_defs = re.findall(r"^#define (PIN|XP)_(\w+) (\d+)", open(PINS_H).read(), re.M)
GPIO = {int(n): net for kind, net, n in _defs if kind == "PIN"}   # gpio -> net
XP = {int(n): net for kind, net, n in _defs if kind == "XP"}      # expander bit -> net
assert len(GPIO) == 22 and len(XP) == 16, "pins.h must assign every GPIO and every expander bit once"

c = Circuit("ptz-driver")
c.title, c.rev, c.date = "PTZ driver board", "A", "2026-11-10"

# ------------------------------------------------------------------ parts catalogue

# value -> (LCSC, footprint). Passives: the LCSC numbers were read on jlcpcb.com/partdetail (hardware/sourcing/).
FP_R, FP_C = "Resistor_SMD:R_{}_{}Metric", "Capacitor_SMD:C_{}_{}Metric"
METRIC = {"0402": "1005", "0603": "1608", "0805": "2012", "1206": "3216"}
RES = {"22R": "C25092", "33R": "C25105", "49.9R": "C25120", "100R": "C25076", "220R": "C25091", "330R": "C25104",
       "1k": "C11702", "2.2k": "C25879", "4.7k": "C25900", "5.1k": "C25905", "10k": "C25744", "12k": "C25752",
       "12.4k": "C2929935", "22k": "C25768", "47k": "C25792", "100k": "C25741", "220k": "C25767", "330k": "C25778",
       "1M": "C26083", "10R": "C25077", "120R": ("C22787", "0603")}
CAP = {"100 nF": ("C1525", "0402"), "100 nF 50 V": ("C307331", "0402"), "1 nF": ("C1523", "0402"),
       "10 nF": ("C15195", "0402"), "22 nF 50 V": ("C1532", "0402"), "22 nF": ("C1532", "0402"),
       "470 pF 50 V": ("C307449", "0402"), "18 pF": ("C1549", "0402"), "22 pF": ("C1555", "0402"),
       "100 pF": ("C1546", "0402"), "6.8 nF": ("C1568", "0402"), "1 µF": ("C52923", "0402"),
       "4.7 µF": ("C23733", "0402"), "1 µF 50 V": ("C15849", "0603"), "4.7 µF 16 V": ("C19666", "0603"),
       "10 µF 10 V": ("C19702", "0603"), "10 µF": ("C19702", "0603"), "22 µF": ("C45783", "0805"),
       "22 µF 25 V": ("C45783", "0805"), "10 µF 50 V": ("C13585", "1206"), "4.7 µF 50 V": ("C29823", "1206")}

S = {k: kicad_symbol(v) for k, v in dict(
    R="Device:R", C="Device:C", CP="Device:C_Polarized", L="Device:L", D="Device:D", DZ="Device:D_Zener",
    DS="Device:D_Schottky", F="Device:Fuse", PTC="Device:Polyfuse", FB="Device:FerriteBead", Y="Device:Crystal_GND24",
    SW="Switch:SW_Push", LED="Device:LED", JPO="Jumper:SolderJumper_2_Open", JPB="Jumper:SolderJumper_2_Bridged",
    JP3="Jumper:SolderJumper_3_Bridged12", TP="Connector:TestPoint", H="Mechanical:MountingHole",
    FLG="power:PWR_FLAG").items()}
OWN = []  # the project's own symbols, written to ptz.kicad_sym


def own(name, left, right, ref="U"):
    s = make_symbol(f"ptz:{name}", left, right, ref)
    OWN.append(s)
    return s


def conn(name, names, mp=False):
    return own(name, [(i + 1, n, "passive") for i, n in enumerate(names)] + ([("MP", "MP", "passive")] if mp else []), [], "J")


def add(ref, value, sym, fp, sheet, lcsc="", mpn="", nets=(), bom=True, **named):
    p = c.add(Part(ref, value, sym, fp, sheet, lcsc, mpn, bom))
    for i, n in enumerate(nets):
        p.net(i + 1, n)
    for k, v in named.items():
        p.net(k.lstrip("_"), v)
    return p


def res(ref, value, a, b, sheet):
    lcsc = RES[value]
    lcsc, pkg = lcsc if isinstance(lcsc, tuple) else (lcsc, "0402")
    return add(ref, value, S["R"], FP_R.format(pkg, METRIC[pkg]), sheet, lcsc, nets=(a, b))


def cap(ref, value, a, b, sheet):
    lcsc, pkg = CAP[value]
    return add(ref, value, S["C"], FP_C.format(pkg, METRIC[pkg]), sheet, lcsc, nets=(a, b))


def two(ref, value, kind, fp, a, b, sheet, lcsc, mpn=""):
    return add(ref, value, S[kind], fp, sheet, lcsc, mpn, nets=(a, b))


# ------------------------------------------------------------------ symbols drawn from datasheet pin tables

P, I, O, B, T, W, OC, NC = "passive", "input", "output", "bidirectional", "tri_state", "power_in", "open_collector", "no_connect"

# TMC5240ATJ, TQFN-32: datasheet 19-101625C Rev 1, p16-18
TMC = own("TMC5240ATJ", [
    (17, "VS", W), (20, "VS", W), (21, "VS", W), (24, "VS", W), (5, "VCC_IO", W), None,
    (26, "CSN", I), (27, "SCK", I), (28, "SDI", I), (29, "SDO", T), None,
    (9, "DRV_ENN", I), (25, "SLEEPN", I), (10, "UART_EN", I), (30, "CLK", I), None,
    (31, "REFL", I), (32, "REFR", I), (8, "ENCA", I), (7, "ENCB", I), (6, "ENCN", I), (2, "AIN", I)], [
    (23, "OUT1A", P), (22, "OUT2A", P), (18, "OUT1B", P), (19, "OUT2B", P), None,
    (11, "DIAG0", O), (12, "DIAG1/SW", O), (13, "OV", OC), None,
    (16, "VCP", P), (15, "CPO", P), (14, "CPI", P), (3, "VDD1V8", P), (1, "IREF", P), None,
    (4, "AGND", W), (33, "EP", W)])

# ESP32-C6-MINI-1U: datasheet v1.5, table 3-1
_esp_io = {5: 2, 6: 3, 9: 4, 10: 5, 12: 0, 13: 1, 15: 6, 16: 7, 17: 12, 18: 13, 19: 14, 20: 15, 22: 8, 23: 9, 24: 18,
           25: 19, 26: 20, 27: 21, 28: 22, 29: 23, 30: 17, 31: 16}  # module pin -> GPIO
ESP = own("ESP32-C6-MINI-1U", [(3, "3V3", W), (8, "EN", I), None] + [(p, f"IO{g}", B) for p, g in sorted(_esp_io.items())],
          [(p, "NC", NC) for p in (4, 7, 21, 32, 33, 34, 35)] + [None] +
          [(p, "GND", W) for p in [1, 2, 11, 14] + list(range(36, 54))])

W5500 = own("W5500", [
    (28, "VDD", W), (4, "AVDD", W), (8, "AVDD", W), (11, "AVDD", W), (15, "AVDD", W), (17, "AVDD", W), (21, "AVDD", W), None,
    (32, "SCSn", I), (33, "SCLK", I), (35, "MOSI", I), (34, "MISO", T), (36, "INTn", O), (37, "RSTn", I), None,
    (45, "PMODE0", I), (44, "PMODE1", I), (43, "PMODE2", I), (23, "RSVD23", I), None,
    (30, "XI", I), (31, "XO", P), (10, "EXRES1", P), (20, "TOCAP", P), (22, "1V2O", P)], [
    (2, "TXP", P), (1, "TXN", P), (6, "RXP", P), (5, "RXN", P), None,
    (25, "LINKLED", O), (27, "ACTLED", O), (24, "SPDLED", O), (26, "DUPLED", O), None,
    (7, "DNC", NC), (18, "VBG", NC), (12, "NC", NC), (13, "NC", NC), (46, "NC", NC), (47, "NC", NC),
    (38, "RSVD", NC), (39, "RSVD", NC), (40, "RSVD", NC), (41, "RSVD", NC), (42, "RSVD", NC), None,
    (29, "GND", W), (3, "AGND", W), (9, "AGND", W), (14, "AGND", W), (16, "AGND", W), (19, "AGND", W), (48, "AGND", W)])

TPS54360 = own("TPS54360DDA", [(2, "VIN", W), (3, "EN", I), (4, "RT/CLK", P), (6, "COMP", P), (5, "FB", I)],
               [(1, "BOOT", P), (8, "SW", P), None, (7, "GND", W), (9, "PAD", W)])
TLV62569 = own("TLV62569DBV", [(4, "VIN", W), (1, "EN", I)], [(3, "SW", P), (5, "FB", I), (2, "GND", W)])
LVC139 = own("SN74LVC139APW", [(16, "VCC", W), (1, "1G", I), (2, "1A", I), (3, "1B", I), None, (15, "2G", I), (14, "2A", I), (13, "2B", I), (8, "GND", W)],
             [(4, "1Y0", O), (5, "1Y1", O), (6, "1Y2", O), (7, "1Y3", O), None, (12, "2Y0", O), (11, "2Y1", O), (10, "2Y2", O), (9, "2Y3", O)])
LVC125 = own("SN74LVC125APW", [(14, "VCC", W), (1, "1OE", I), (2, "1A", I), (4, "2OE", I), (5, "2A", I), (10, "3OE", I), (9, "3A", I), (13, "4OE", I), (12, "4A", I), (7, "GND", W)],
             [None, (3, "1Y", T), None, (6, "2Y", T), None, (8, "3Y", T), None, (11, "4Y", T)])
_244l = [(20, "VCC", W), (1, "1OE", I), (2, "1A1", I), (4, "1A2", I), (6, "1A3", I), (8, "1A4", I), None,
         (19, "2OE", I), (11, "2A1", I), (13, "2A2", I), (15, "2A3", I), (17, "2A4", I), (10, "GND", W)]
_244r = [None, None, (18, "1Y1", T), (16, "1Y2", T), (14, "1Y3", T), (12, "1Y4", T), None, None,
         (9, "2Y1", T), (7, "2Y2", T), (5, "2Y3", T), (3, "2Y4", T)]
LVC244 = own("SN74LVC244APW", _244l, _244r)
AHCT244 = own("SN74AHCT244PW", _244l, _244r)
PCAL = own("PCAL6416APW", [(2, "VDD(I2C)", W), (24, "VDD(P)", W), (22, "SCL", I), (23, "SDA", B), (1, "INT", OC), (3, "RESET", I), (21, "ADDR", I), (12, "VSS", W)],
           [(4 + i, f"P0_{i}", B) for i in range(8)] + [None] + [(13 + i, f"P1_{i}", B) for i in range(8)])
TMP1075 = own("TMP1075DGK", [(8, "V+", W), (2, "SCL", I), (1, "SDA", B), (4, "GND", W)], [(3, "ALERT", OC), (7, "A0", I), (6, "A1", I), (5, "A2", I)])
USBLC6 = own("USBLC6-2SC6", [(1, "IO1", P), (3, "IO2", P), (2, "GND", W)], [(6, "IO1", P), (4, "IO2", P), (5, "VBUS", P)])
SP3485 = own("SP3485EN", [(8, "VCC", W), (4, "DI", I), (3, "DE", I), (2, "RE", I), (1, "RO", T), (5, "GND", W)], [(6, "A", B), (7, "B", B)])
TJA1051 = own("TJA1051T-3", [(3, "VCC", W), (5, "VIO", W), (1, "TXD", I), (4, "RXD", O), (8, "S", I), (2, "GND", W)], [(7, "CANH", B), (6, "CANL", B)])
PFET = own("AOD4185", [(1, "G", I)], [(2, "D", P), (3, "S", P)], "Q")
NFET = own("AO3422", [(1, "G", I)], [(3, "D", P), (2, "S", P)], "Q")
BAT54S = own("BAT54S", [(1, "A", P), (2, "K", P)], [(3, "COM", P)], "D")
SM712 = own("SM712", [(1, "IO1", P), (2, "IO2", P)], [(3, "GND", P)], "D")
RGB = own("LED_RGB_CA", [(4, "A", P)], [(1, "RK", P), (2, "GK", P), (3, "BK", P)], "D")
USBC = own("USB_C_16P", [(n, "VBUS", P) for n in ("A4", "A9", "B4", "B9")] + [("A5", "CC1", P), ("B5", "CC2", P)] +
           [("A6", "D+", P), ("B6", "D+", P), ("A7", "D-", P), ("B7", "D-", P), ("A8", "SBU1", NC), ("B8", "SBU2", NC)],
           [(n, "GND", P) for n in ("A1", "A12", "B1", "B12")] + [("SH", "SHIELD", P)], "J")
J_VH2 = conn("VH_2", ["+VIN", "GND"])
J_XH4 = conn("XH_4_MOTOR", ["A1", "A2", "B1", "B2"])
J_XH2 = conn("XH_2_FAN", ["FAN+", "FAN-"])
J_GH7 = conn("GH_7_SENSOR", ["3V3", "GND", "SCK", "MOSI", "MISO", "CS", "HOME"], mp=True)
J_GH7E = conn("GH_7_ETH", ["TCT", "GND", "TD+", "TD-", "RD+", "RD-", "RCT"], mp=True)
J_GH4E = conn("GH_4_EXT", ["5V", "STEP", "DIR", "GND"], mp=True)
J_GH4 = conn("GH_4", ["1", "2", "3", "4"], mp=True)
J_SH4 = conn("SH_4_I2C", ["GND", "3V3", "SDA", "SCL"], mp=True)

FP = dict(
    TMC="Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm", ESP="ptz:ESP32-C6-MINI-1U", W5500="Package_QFP:LQFP-48_7x7mm_P0.5mm",
    HSOP8="Package_SO:TI_SO-PowerPAD-8", SOT235="Package_TO_SOT_SMD:SOT-23-5", SOT23="Package_TO_SOT_SMD:SOT-23",
    SOT236="Package_TO_SOT_SMD:SOT-23-6", DPAK="Package_TO_SOT_SMD:TO-252-2", SOD123="Diode_SMD:D_SOD-123", SMB="Diode_SMD:D_SMB",
    SMA="Diode_SMD:D_SMA", TSSOP14="Package_SO:TSSOP-14_4.4x5mm_P0.65mm", TSSOP16="Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
    TSSOP20="Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm", TSSOP24="Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
    SOIC8="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", VSSOP8="Package_SO:VSSOP-8_3x3mm_P0.65mm",
    XTAL="Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", NANO2="Fuse:Fuse_Littelfuse-NANO2-451_453", F1206="Fuse:Fuse_1206_3216Metric",
    F0603="Fuse:Fuse_0603_1608Metric", F1812="Fuse:Fuse_1812_4532Metric", ELEC="Capacitor_SMD:CP_Elec_10x10",
    L0630="Inductor_SMD:L_7.3x7.3_H4.5", L0402S="Inductor_SMD:L_Sunlord_MWSA0402S", FB0603="Inductor_SMD:L_0603_1608Metric",
    VH2="Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", XH4="Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
    XH2="Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", GH7="Connector_JST:JST_GH_SM07B-GHS-TB_1x07-1MP_P1.25mm_Horizontal",
    GH7V="Connector_JST:JST_GH_BM07B-GHS-TBT_1x07-1MP_P1.25mm_Vertical", GH4V="Connector_JST:JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical",
    GH4="Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal", SH4="Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal",
    USBC="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", LED0603="LED_SMD:LED_0603_1608Metric",
    SW="Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A", RGB="ptz:LED_RGB_1616", JPO="Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
    JPB="Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm", JP3="Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm",
    TP="ptz:TestPoint_D1.0", HOLE="MountingHole:MountingHole_3.2mm_M3")

# ------------------------------------------------------------------ power (POW)

sh = c.sheet("power", "Power: input protection, 5 V and 3.3 V")
add("J101", "B2P-VH", J_VH2, FP["VH2"], sh, "C160315", "B2P-VH(LF)(SN)", nets=("VIN_RAW", "GND"))
add("Q101", "AOD4185", PFET, FP["DPAK"], sh, "C400894", "AOD4185", G="RP_GATE", D="VIN_RAW", S="VIN")
two("D101", "12 V zener", "DZ", FP["SOD123"], "VIN", "RP_GATE", sh, "C12747", "LBZT52C12T1G")
res("R101", "100k", "RP_GATE", "GND", sh)
two("F101", "7 A slow", "F", FP["NANO2"], "VIN", "VM", sh, "C72975", "0452007.MRL")
two("F102", "1.5 A", "F", FP["F1206"], "VIN", "VIN_L", sh, "C187598", "046601.5NRHF")
two("D102", "SMBJ24A", "DZ", FP["SMB"], "VM", "GND", sh, "C211760", "SMBJ24A")
for r in ("C101", "C102"):
    two(r, "220 µF 50 V", "CP", FP["ELEC"], "VM", "GND", sh, "C970698")
add("U101", "TPS54360", TPS54360, FP["HSOP8"], sh, "C44377", "TPS54360DDAR", VIN="VIN_L", EN="BUCK_EN", COMP="BUCK_COMP",
    FB="BUCK_FB", BOOT="BUCK_BOOT", SW="BUCK_SW", GND="GND", PAD="GND").net("RT/CLK", "BUCK_RT")
cap("C103", "4.7 µF 50 V", "VIN_L", "GND", sh)
cap("C104", "4.7 µF 50 V", "VIN_L", "GND", sh)
cap("C105", "100 nF 50 V", "VIN_L", "GND", sh)
cap("C106", "100 nF 50 V", "BUCK_BOOT", "BUCK_SW", sh)
res("R102", "330k", "VIN_L", "BUCK_EN", sh)
res("R103", "47k", "BUCK_EN", "GND", sh)
res("R104", "220k", "BUCK_RT", "GND", sh)
res("R105", "4.7k", "BUCK_COMP", "BUCK_COMP_RC", sh)
cap("C107", "22 nF", "BUCK_COMP_RC", "GND", sh)
cap("C108", "100 pF", "BUCK_COMP", "GND", sh)
two("D103", "SS36", "DS", FP["SMA"], "BUCK_SW", "GND", sh, "C7420367", "SS36")
two("L101", "22 µH", "L", FP["L0630"], "BUCK_SW", "+5V", sh, "C128694", "SMMS0630-220M")
cap("C109", "22 µF 25 V", "+5V", "GND", sh)
cap("C110", "22 µF 25 V", "+5V", "GND", sh)
res("R106", "47k", "+5V", "BUCK_FB_MID", sh)
res("R112", "5.1k", "BUCK_FB_MID", "BUCK_FB", sh)
res("R107", "10k", "BUCK_FB", "GND", sh)
two("D104", "B5819W", "DS", FP["SOD123"], "VSYS", "+5V", sh, "C8598", "B5819W")
two("D105", "B5819W", "DS", FP["SOD123"], "VSYS", "VBUS", sh, "C8598", "B5819W")
add("U102", "TLV62569", TLV62569, FP["SOT235"], sh, "C141836", "TLV62569DBVR", VIN="VSYS", EN="VSYS", SW="SW3V3", FB="FB3V3", GND="GND")
cap("C111", "4.7 µF 16 V", "VSYS", "GND", sh)
two("L102", "2.2 µH", "L", FP["L0402S"], "SW3V3", "+3V3", sh, "C408335", "MWSA0402S-2R2MT")
cap("C112", "10 µF 10 V", "+3V3", "GND", sh)
cap("C113", "10 µF 10 V", "+3V3", "GND", sh)
res("R108", "100k", "+3V3", "FB3V3", sh)
res("R109", "22k", "FB3V3", "GND", sh)
cap("C115", "22 pF", "+3V3", "FB3V3", sh)
res("R110", "100k", "VM", "VM_SENSE", sh)
res("R111", "10k", "VM_SENSE", "GND", sh)
cap("C114", "100 nF", "VM_SENSE", "GND", sh)

# ------------------------------------------------------------------ MCU and logic (CTL)

sh = c.sheet("mcu", "MCU, chip selects, expander, USB, I2C")
esp = add("U201", "ESP32-C6-MINI-1U-H4", ESP, FP["ESP"], sh, "C20627095", "ESP32-C6-MINI-1U-H4", _3V3="+3V3", EN="EN", GND="GND")
esp.nc("NC")
for pin, gpio in _esp_io.items():
    esp.net(pin, {"SPI_SCK": "SPI_SCK_MCU", "SPI_MOSI": "SPI_MOSI_MCU"}.get(GPIO[gpio], GPIO[gpio]))
cap("C201", "22 µF", "+3V3", "GND", sh)
cap("C202", "100 nF", "+3V3", "GND", sh)
res("R201", "10k", "EN", "+3V3", sh)
cap("C203", "1 µF", "EN", "GND", sh)
two("SW201", "BOOT", "SW", FP["SW"], "BOOT", "GND", sh, "C318884", "TS-1187A-B-A-B")
res("R202", "10k", "BOOT", "+3V3", sh)
res("R203", "22R", "SPI_SCK_MCU", "SPI_SCK", sh)
res("R204", "22R", "SPI_MOSI_MCU", "SPI_MOSI", sh)
u = add("U202", "SN74LVC139A", LVC139, FP["TSSOP16"], sh, "C7662", "SN74LVC139APWR", VCC="+3V3", GND="GND")
u.net("1G", "CS_DRV_EN_N").net("1A", "CS_A0").net("1B", "CS_A1").net("2G", "CS_SNS_EN_N").net("2A", "CS_A0").net("2B", "CS_A1")
for i in range(4):
    u.net(f"1Y{i}", f"CS_DRV{i + 1}").net(f"2Y{i}", f"CS_SNS{i + 1}")
cap("C204", "100 nF", "+3V3", "GND", sh)
res("R205", "10k", "CS_DRV_EN_N", "+3V3", sh)
res("R206", "10k", "CS_SNS_EN_N", "+3V3", sh)
res("R207", "10k", "ETH_CS_N", "+3V3", sh)
u = add("U203", "PCAL6416A", PCAL, FP["TSSOP24"], sh, "C2652299", "PCAL6416APW,118", SCL="I2C_SCL", SDA="I2C_SDA", INT="XINT_N",
        RESET="EN", ADDR="GND", VSS="GND")
u.net("VDD(I2C)", "+3V3").net("VDD(P)", "+3V3")
for bit, net in XP.items():
    u.net(f"P{bit // 8}_{bit % 8}", net)
cap("C205", "100 nF", "+3V3", "GND", sh)
res("R208", "10k", "XINT_N", "+3V3", sh)
add("U204", "TMP1075", TMP1075, FP["VSSOP8"], sh, "C2864807", "TMP1075DGKR", SCL="I2C_SCL", SDA="I2C_SDA", GND="GND", A0="GND",
    A1="GND", A2="GND").net("V+", "+3V3").nc("ALERT")
cap("C206", "100 nF", "+3V3", "GND", sh)
res("R209", "2.2k", "I2C_SDA", "+3V3", sh)
res("R210", "2.2k", "I2C_SCL", "+3V3", sh)
add("J201", "USB-C", USBC, FP["USBC"], sh, "C165948", "TYPE-C-31-M-12", VBUS="VBUS", GND="GND", SHIELD="GND", CC1="CC1", CC2="CC2").net(
    "D+", "USB_DP").net("D-", "USB_DN").nc("SBU1", "SBU2")
res("R211", "5.1k", "CC1", "GND", sh)
res("R212", "5.1k", "CC2", "GND", sh)
add("U205", "USBLC6-2SC6", USBLC6, FP["SOT236"], sh, "C7519", "USBLC6-2SC6", IO1="USB_DN", IO2="USB_DP", GND="GND", VBUS="VBUS")
cap("C207", "1 µF", "VBUS", "GND", sh)
add("J202", "SM04B-SRSS-TB", J_SH4, FP["SH4"], sh, "C160404", "SM04B-SRSS-TB(LF)(SN)", GND="GND", SDA="I2C_SDA", SCL="I2C_SCL", MP="GND").net("3V3", "+3V3_I2C")
two("F201", "0.2 A PTC", "PTC", FP["F0603"], "+3V3", "+3V3_I2C", sh, "C20785", "SMD0603P020TF")
cap("C208", "1 µF", "+3V3_I2C", "GND", sh)
add("D201", "RGB LED", RGB, FP["RGB"], sh, "C60105", "19-237/R6GHBHC-A01/2T", A="+3V3", RK="LED_R_K", GK="LED_G_K", BK="LED_B_K")
res("R213", "1k", "LED_R_K", "LED_R_N", sh)
res("R214", "220R", "LED_G_K", "LED_G_N", sh)
res("R215", "220R", "LED_B_K", "LED_B_N", sh)

# ------------------------------------------------------------------ axes (DRV, ENC)


def axis(n):
    a = n + 2
    sh = c.sheet(f"axis{n}", f"Axis {n}: driver, motor, sensor port, external driver port")
    r, k = (lambda i: f"R{a}{i:02d}"), (lambda i: f"C{a}{i:02d}")
    u = add(f"U{a}01", "TMC5240ATJ", TMC, FP["TMC"], sh, "C7494373", "TMC5240ATJ+T", VS="VM", VCC_IO="+3V3", AGND="GND", EP="GND",
            VDD1V8=f"A{n}_1V8", VCP=f"A{n}_VCP", CPO=f"A{n}_CPO", CPI=f"A{n}_CPI", IREF=f"A{n}_IREF", SLEEPN=f"A{n}_SLEEPN",
            AIN="GND", CLK="GND", UART_EN="GND", ENCA="GND", ENCB="GND", ENCN="GND", REFR="GND", CSN=f"CS_DRV{n}",
            SCK="SPI_SCK", SDI="SPI_MOSI", SDO="SPI_MISO", DRV_ENN="DRV_ENN", DIAG0=f"DIAG0_{n}", REFL=f"HOME{n}",
            OUT1A=f"M{n}_A1", OUT2A=f"M{n}_A2", OUT1B=f"M{n}_B1", OUT2B=f"M{n}_B2")
    u.net("DIAG1/SW", f"DIAG1_{n}").nc("OV")
    add(f"J{a}01", "B4B-XH-A", J_XH4, FP["XH4"], sh, "C144395", "B4B-XH-A(LF)(SN)", nets=[f"M{n}_{x}" for x in ("A1", "A2", "B1", "B2")])
    add(f"J{a}02", "BM07B-GHS-TBT", J_GH7, FP["GH7V"], sh, "C378970", "BM07B-GHS-TBT(LF)(SN)(N)", GND="GND", SCK=f"SNS{n}_SCK", MOSI=f"SNS{n}_MOSI",
        MISO=f"SNS{n}_MISO", CS=f"SNS{n}_CS", HOME=f"HOME{n}_IN", MP="GND").net("3V3", "+3V3_SNS")
    add(f"J{a}03", "SM04B-GHS-TB", J_GH4E, FP["GH4"], sh, "C189895", "SM04B-GHS-TB(LF)(SN)", STEP=f"STEP{n}_O", DIR=f"DIR{n}_O", GND="GND", MP="GND").net("5V", "+5V_EXT")
    cap(k(1), "100 nF 50 V", "VM", "GND", sh)
    cap(k(2), "100 nF 50 V", "VM", "GND", sh)
    cap(k(3), "10 µF 50 V", "VM", "GND", sh)
    cap(k(4), "1 µF 50 V", f"A{n}_VCP", "VM", sh)
    cap(k(5), "22 nF 50 V", f"A{n}_CPI", f"A{n}_CPO", sh)
    cap(k(6), "4.7 µF", f"A{n}_1V8", "GND", sh)
    cap(k(7), "100 nF", "+3V3", "GND", sh)
    for i, x in enumerate(("A1", "A2", "B1", "B2")):
        cap(k(8 + i), "470 pF 50 V", f"M{n}_{x}", "GND", sh)
    cap(k(12), "1 nF", f"HOME{n}", "GND", sh)
    res(r(1), "12k", f"A{n}_IREF", "GND", sh)
    res(r(2), "100k", f"A{n}_SLEEPN", "VM", sh)
    res(r(3), "10k", f"DIAG0_{n}", "+3V3", sh)
    res(r(4), "10k", f"DIAG1_{n}", "+3V3", sh)
    res(r(5), "10k", f"HOME{n}_IN", "+3V3", sh)
    res(r(6), "22k", f"HOME{n}_IN", f"HOME{n}", sh)
    res(r(7), "33R", f"SNS_SCK{n}_B", f"SNS{n}_SCK", sh)
    res(r(8), "33R", f"SNS_MOSI{n}_B", f"SNS{n}_MOSI", sh)
    res(r(9), "33R", f"CS_SNS{n}", f"SNS{n}_CS", sh)
    res(r(10), "100R", f"SNS{n}_MISO", f"SNS{n}_MISO_B", sh)
    res(r(11), "100k", f"SNS{n}_SCK", "GND", sh)
    res(r(12), "100k", f"SNS{n}_MOSI", "GND", sh)
    res(r(13), "100k", f"SNS{n}_MISO_B", "GND", sh)
    res(r(14), "220R", f"STEP{n}_B", f"STEP{n}_O", sh)
    res(r(15), "220R", f"DIR{n}_B", f"DIR{n}_O", sh)
    add(f"D{a}01", "BAT54S", BAT54S, FP["SOT23"], sh, "C7420333", "BAT54S", A="GND", K="+3V3", COM=f"HOME{n}")


for n in (1, 2, 3, 4):
    axis(n)

# ------------------------------------------------------------------ buffers to the ports (ENC-05, DRV-06)

sh = c.sheet("buffers", "Buffers to the sensor and external driver ports")
u = add("U701", "SN74LVC244A", LVC244, FP["TSSOP20"], sh, "C7668", "SN74LVC244APWR", VCC="+3V3", GND="GND", _1OE="CS_SNS_EN_N", _2OE="CS_SNS_EN_N")
v = add("U703", "SN74AHCT244", AHCT244, FP["TSSOP20"], sh, "C484743", "SN74AHCT244PWR", VCC="+5V", GND="GND", _1OE="DRV_ENN", _2OE="DRV_ENN")
w = add("U702", "SN74LVC125A", LVC125, FP["TSSOP14"], sh, "C7813", "SN74LVC125APWR", VCC="+3V3", GND="GND")
for i in range(1, 5):
    u.net(f"1A{i}", "SPI_SCK").net(f"1Y{i}", f"SNS_SCK{i}_B").net(f"2A{i}", "SPI_MOSI").net(f"2Y{i}", f"SNS_MOSI{i}_B")
    v.net(f"1A{i}", f"DIAG0_{i}").net(f"1Y{i}", f"STEP{i}_B").net(f"2A{i}", f"DIAG1_{i}").net(f"2Y{i}", f"DIR{i}_B")
    w.net(f"{i}OE", f"CS_SNS{i}").net(f"{i}A", f"SNS{i}_MISO_B").net(f"{i}Y", "SPI_MISO")
cap("C701", "100 nF", "+3V3", "GND", sh)
cap("C702", "100 nF", "+3V3", "GND", sh)
cap("C703", "100 nF", "+5V", "GND", sh)
two("F701", "0.2 A PTC", "PTC", FP["F0603"], "+3V3", "+3V3_SNS", sh, "C20785", "SMD0603P020TF")
cap("C704", "4.7 µF", "+3V3_SNS", "GND", sh)
two("F702", "0.2 A PTC", "PTC", FP["F0603"], "+5V", "+5V_EXT", sh, "C20785", "SMD0603P020TF")
cap("C705", "1 µF", "+5V_EXT", "GND", sh)
res("R701", "10k", "DRV_ENN", "+3V3", sh)
res("R702", "100k", "SPI_MISO", "GND", sh)

# ------------------------------------------------------------------ Ethernet, RS-485, CAN (CTL-03, -04, -06)

sh = c.sheet("comms", "Ethernet, RS-485, CAN")
u = add("U801", "W5500", W5500, FP["W5500"], sh, "C32843", "W5500", VDD="+3V3", AVDD="3V3A", GND="GND", AGND="GND", TXP="ETH_TXP", TXN="ETH_TXN",
        RXP="ETH_RXP", RXN="ETH_RXN", EXRES1="ETH_RES", TOCAP="ETH_TOCAP", XI="ETH_XI", XO="ETH_XO", SCSn="ETH_CS_N", SCLK="SPI_SCK",
        MOSI="SPI_MOSI", MISO="SPI_MISO", INTn="ETH_INT_N", RSTn="ETH_RST_N", PMODE0="+3V3", PMODE1="+3V3", PMODE2="+3V3",
        RSVD23="GND", LINKLED="ETH_LINK", ACTLED="ETH_ACT")
u.net("1V2O", "ETH_1V2").nc("DNC", "VBG", "SPDLED", "DUPLED", "NC", "RSVD")
add("J801", "SM07B-GHS-TB", J_GH7E, FP["GH7"], sh, "C495552", "SM07B-GHS-TB(LF)(SN)",
    nets=("ETH_TCT", "GND", "ETH_TXP", "ETH_TXN", "ETH_RDP", "ETH_RDN", "ETH_RCT"), MP="GND")
two("D802", "LINK", "LED", FP["LED0603"], "ETH_LED_L", "+3V3", sh, "C2286", "KT-0603R")
two("D803", "ACT", "LED", FP["LED0603"], "ETH_LED_A", "+3V3", sh, "C2286", "KT-0603R")
two("FB801", "600R ferrite", "FB", FP["FB0603"], "+3V3", "3V3A", sh, "C85833", "BLM18KG601SN1D")
for i in range(1, 5):
    cap(f"C80{i}", "100 nF", "3V3A", "GND", sh)
cap("C805", "10 µF", "3V3A", "GND", sh)
cap("C806", "100 nF", "+3V3", "GND", sh)
cap("C807", "4.7 µF", "+3V3", "GND", sh)
res("R801", "12.4k", "ETH_RES", "GND", sh)
cap("C808", "4.7 µF", "ETH_TOCAP", "GND", sh)
cap("C809", "10 nF", "ETH_1V2", "GND", sh)
add("Y801", "25 MHz", S["Y"], FP["XTAL"], sh, "C9006", "X322525MOB4SI", nets=("ETH_XI", "GND", "ETH_XO", "GND"))
cap("C810", "18 pF", "ETH_XI", "GND", sh)
cap("C811", "18 pF", "ETH_XO", "GND", sh)
res("R802", "1M", "ETH_XI", "ETH_XO", sh)
res("R803", "49.9R", "ETH_TXP", "3V3A", sh)
res("R804", "49.9R", "ETH_TXN", "3V3A", sh)
res("R805", "10R", "3V3A", "ETH_TCT", sh)
cap("C812", "22 nF", "ETH_TCT", "GND", sh)
res("R806", "49.9R", "ETH_RXP", "ETH_RCT", sh)
res("R807", "49.9R", "ETH_RXN", "ETH_RCT", sh)
cap("C813", "6.8 nF", "ETH_RXP", "ETH_RDP", sh)
cap("C814", "6.8 nF", "ETH_RXN", "ETH_RDN", sh)
cap("C815", "10 nF", "ETH_RCT", "GND", sh)
res("R808", "1k", "ETH_LINK", "ETH_LED_L", sh)
res("R809", "1k", "ETH_ACT", "ETH_LED_A", sh)
res("R810", "10k", "ETH_INT_N", "+3V3", sh)
res("R811", "10k", "ETH_RST_N", "+3V3", sh)
add("U802", "SP3485", SP3485, FP["SOIC8"], sh, "C8963", "SP3485EN-L/TR", VCC="+3V3", GND="GND", RO="RS485_RX", RE="RS485_DE", DE="RS485_DE",
    DI="RS485_TX", A="RS485_A", B="RS485_B")
cap("C816", "100 nF", "+3V3", "GND", sh)
res("R812", "10k", "RS485_DE", "GND", sh)
res("R813", "10k", "RS485_RX", "+3V3", sh)
add("D801", "SM712", SM712, FP["SOT23"], sh, "C521963", "SM712", IO1="RS485_A", IO2="RS485_B", GND="GND")
res("R814", "120R", "RS485_A", "RS485_TERM", sh)
two("JP801", "open", "JPO", FP["JPO"], "RS485_TERM", "RS485_B", sh, "").bom = False
add("J802", "SM04B-GHS-TB", J_GH4, FP["GH4"], sh, "C189895", "SM04B-GHS-TB(LF)(SN)", nets=("RS485_A", "RS485_B", "GND", "GND"), MP="GND")
add("U803", "TJA1051T/3", TJA1051, FP["SOIC8"], sh, "C2671195", "TJA1051T/3/CM,118", VCC="+5V", VIO="+3V3", GND="GND", S="GND", TXD="CAN_TX",
    RXD="CAN_RX", CANH="CAN_H", CANL="CAN_L")
cap("C817", "100 nF", "+5V", "GND", sh)
cap("C818", "100 nF", "+3V3", "GND", sh)
res("R815", "120R", "CAN_H", "CAN_TERM", sh)
two("JP802", "bridged", "JPB", FP["JPB"], "CAN_TERM", "CAN_L", sh, "").bom = False
add("J803", "BM04B-GHS-TBT", J_GH4, FP["GH4V"], sh, "C161692", "BM04B-GHS-TBT(LF)(SN)", nets=("CAN_H", "CAN_L", "GND", "GND"), MP="GND")

# ------------------------------------------------------------------ camera, fan, test points (CAM, AUX)

sh = c.sheet("io", "Camera outputs, fan, test points, mounting")
add("Q901", "AO3422", NFET, FP["SOT23"], sh, "C37130", "AO3422", G="TALLY", S="GND", D="TALLY_OD")
add("Q902", "AO3422", NFET, FP["SOT23"], sh, "C37130", "AO3422", G="REC", S="GND", D="REC_OD")
res("R901", "100k", "TALLY", "GND", sh)
res("R902", "100k", "REC", "GND", sh)
add("J901", "SM04B-GHS-TB", J_GH4, FP["GH4"], sh, "C189895", "SM04B-GHS-TB(LF)(SN)", nets=("TALLY_OD", "REC_OD", "GND", "GND"), MP="GND")
add("Q903", "AO3422", NFET, FP["SOT23"], sh, "C37130", "AO3422", G="FAN_G", S="GND", D="FAN_N")
res("R903", "100R", "FAN_PWM", "FAN_G", sh)
res("R904", "100k", "FAN_G", "GND", sh)
two("D901", "B5819W", "DS", FP["SOD123"], "FAN_V", "FAN_N", sh, "C8598", "B5819W")
add("JP901", "5V | VM", S["JP3"], FP["JP3"], sh, nets=("+5V", "FAN_SRC", "VM"), bom=False)
two("F901", "0.5 A PTC", "PTC", FP["F1812"], "FAN_SRC", "FAN_V", sh, "C269128")
add("J902", "B2B-XH-A", J_XH2, FP["XH2"], sh, "C158012", "B2B-XH-A(LF)(SN)", nets=("FAN_V", "FAN_N"))
TESTPOINTS = ["VIN", "VM", "+5V", "VSYS", "+3V3", "GND", "GND", "SPI_SCK", "SPI_MOSI", "SPI_MISO", "I2C_SDA", "I2C_SCL", "DRV_ENN",
              "XINT_N", "CS_DRV_EN_N", "CS_SNS_EN_N", "SPARE", "CAN_TX", "CAN_RX", "RS485_TX", "RS485_RX", "EN"]
for i, net in enumerate(TESTPOINTS):
    add(f"TP{901 + i}", net, S["TP"], FP["TP"], sh, nets=(net,), bom=False)
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
        x, y, col_h = 30, 14, 0
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
