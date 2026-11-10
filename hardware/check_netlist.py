#!/usr/bin/env python3
"""Independent netlist check for the PTZ driver board, Rev A.

Expectations are derived from specs/modules/*.md and the manufacturers' datasheets (hardware/datasheets/), never
from the schematic. MCU and I/O expander pins come from firmware/include/pins.h at run time.

One function per acceptance criterion, named after its id (pow_02a_..., drv_06_...). Each returns
{(ref, pin): expected_net}. Special forms:
  * expected None             -> pin must be unconnected (absent, "unconnected-*", or alone on its net)
  * key (ref, "1,2")          -> two-pin part without polarity: the two pins carry the pair (a, b) in either order
  * key (ref, "pins.h:...")   -> a pins.h consistency problem (never present in a netlist, so it always fails)
Pin numbers are footprint pad names, see the conventions in the build brief. Datasheet pages are quoted per function.

Run from the repo root:  python3 hardware/check_netlist.py      Exit 0 only when there is no mismatch.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = os.path.join(ROOT, "hardware", "ptz-driver.kicad_sch")
PINS_H = os.path.join(ROOT, "firmware", "include", "pins.h")
sys.path.insert(0, os.path.join(ROOT, "hardware", "tools"))

VAL = {}          # ref -> value the spec's Value column gives (R, C, L only), checked loosely
NET_ONLY = {}     # function name -> [(net, {refs allowed on it})]
AXES = [(n, n + 2) for n in range(1, 5)]   # axis n -> reference hundreds a (axis 1 = 3xx)


# ---------------------------------------------------------------- helpers
def two(d, ref, a, b, val=None):
    """Two-pin part without polarity, nets a and b in either order."""
    d[(ref, "1,2")] = (a, b)
    if val:
        VAL[ref] = val


def ordered(d, ref, a, b, val=None):
    """Two-pin part with polarity: pin 1 = a, pin 2 = b."""
    d[(ref, "1")] = a
    d[(ref, "2")] = b
    if val:
        VAL[ref] = val


def setp(d, ref, mapping):
    for pin, net in mapping.items():
        d[(ref, str(pin))] = net


def same(d, ref, pins, net):
    for p in pins:
        d[(ref, str(p))] = net


def ref(letter, a, k):
    return "%s%d%02d" % (letter, a, k)


# ---------------------------------------------------------------- pins.h
def parse_pins_h():
    pin, xp = {}, {}
    try:
        text = open(PINS_H).read()
    except OSError:
        return pin, xp
    for kind, net, num in re.findall(r"^\s*#define\s+(PIN|XP)_(\w+)\s+(\d+)", text, re.M):
        (pin if kind == "PIN" else xp)[net] = int(num)
    return pin, xp


# ESP32-C6-MINI-1 datasheet v1.5, Table 3-1 (p10-11): module pin number per GPIO
GPIO_PIN = {0: 12, 1: 13, 2: 5, 3: 6, 4: 9, 5: 10, 6: 15, 7: 16, 8: 22, 9: 23, 12: 17, 13: 18, 14: 19, 15: 20,
            16: 31, 17: 30, 18: 24, 19: 25, 20: 26, 21: 27, 22: 28, 23: 29}
MCU_NC = [4, 7, 21, 32, 33, 34, 35]
MCU_GND = [1, 2, 11, 14] + list(range(36, 54))
MCU_RENAME = {"SPI_SCK": "SPI_SCK_MCU", "SPI_MOSI": "SPI_MOSI_MCU"}   # control.md, CTL-10
# nets the specs route to a direct MCU pin / to the expander; pins.h must define them
MCU_NEEDED = ["SPI_SCK", "SPI_MOSI", "SPI_MISO", "CS_A0", "CS_A1", "CS_DRV_EN_N", "CS_SNS_EN_N", "ETH_CS_N", "DRV_ENN",
              "I2C_SDA", "I2C_SCL", "XINT_N", "RS485_TX", "RS485_RX", "RS485_DE", "CAN_TX", "CAN_RX", "VM_SENSE",
              "FAN_PWM", "BOOT", "USB_DN", "USB_DP"]
XP_NEEDED = (["DIAG0_%d" % n for n in range(1, 5)] + ["DIAG1_%d" % n for n in range(1, 5)] +
             ["ETH_INT_N", "ETH_RST_N", "LED_R_N", "LED_G_N", "LED_B_N", "TALLY", "REC", "SPARE"])


def xp_pin(bit):
    """PCAL6416APW TSSOP-24 (datasheet Rev 7.1, p4 and Table 3): P0_0..P0_7 = pins 4..11, P1_0..P1_7 = pins 13..20."""
    return 4 + bit if bit < 8 else 5 + bit


# ================================================================ POWER (specs/modules/power.md)
def pow_01_input_connector():
    """POW-01. J101 JST B2P-VH: pin 1 plus, pin 2 minus (spec text, JST VH series)."""
    return {("J101", "1"): "VIN_RAW", ("J101", "2"): "GND"}


def pow_02a_reverse_polarity():
    """POW-02a. Q101 AOD4185 TO-252 (datasheet p1 drawing: G left, D tab middle, S right; JEDEC G=1, D=2, S=3).
    D101 zener: pin 1 cathode, pin 2 anode (build convention)."""
    d = {}
    setp(d, "Q101", {1: "RP_GATE", 2: "VIN_RAW", 3: "VIN"})
    ordered(d, "D101", "VIN", "RP_GATE")
    two(d, "R101", "RP_GATE", "GND", "100k")
    return d


def pow_02b_hotplug_clamp():
    """POW-02b. C101/C102 polarised, pin 1 plus. D102 SMBJ24A, K = VM, A = GND."""
    d = {}
    for c in ("C101", "C102"):
        ordered(d, c, "VM", "GND", "220 µF 50 V")
    ordered(d, "D102", "VM", "GND")
    return d


def pow_03_separate_fuses():
    """POW-03. F101 VIN-VM, F102 VIN-VIN_L. Only F101, F102, Q101, D101 and TP901 may sit on VIN."""
    d = {}
    two(d, "F101", "VIN", "VM")
    two(d, "F102", "VIN", "VIN_L")
    NET_ONLY["pow_03_separate_fuses"] = [("VIN", {"F101", "F102", "Q101", "D101", "TP901"})]
    return d


def pow_05_vsys_diodes():
    """POW-05. D104 anode +5V, D105 anode VBUS, both cathodes on VSYS (diode: pin 1 K, pin 2 A). VSYS and VBUS carry
    nothing else but the parts that the specs name."""
    d = {}
    ordered(d, "D104", "VSYS", "+5V")
    ordered(d, "D105", "VSYS", "VBUS")
    NET_ONLY["pow_05_vsys_diodes"] = [("VSYS", {"D104", "D105", "U102", "C111", "TP904"}),
                                      ("VBUS", {"D105", "J201", "U205", "C207"})]
    return d


def pow_06_vm_sense():
    """POW-06. VM / 11 divider: R110 VM to VM_SENSE, R111 and C114 VM_SENSE to GND."""
    d = {}
    two(d, "R110", "VM", "VM_SENSE", "100k")
    two(d, "R111", "VM_SENSE", "GND", "10k")
    two(d, "C114", "VM_SENSE", "GND", "100 nF")
    return d


def pow_07_buck_5v():
    """POW-07. U101 TPS54360DDA HSOP-8, datasheet SLVSBB4G p4: 1 BOOT, 2 VIN, 3 EN, 4 RT/CLK, 5 FB, 6 COMP, 7 GND,
    8 SW, 9 thermal pad."""
    d = {}
    setp(d, "U101", {1: "BUCK_BOOT", 2: "VIN_L", 3: "BUCK_EN", 4: "BUCK_RT", 5: "BUCK_FB", 6: "BUCK_COMP", 7: "GND",
                     8: "BUCK_SW", 9: "GND"})
    for c in ("C103", "C104"):
        two(d, c, "VIN_L", "GND", "4.7 µF 50 V")
    two(d, "C105", "VIN_L", "GND", "100 nF 50 V")
    two(d, "C106", "BUCK_BOOT", "BUCK_SW", "100 nF 50 V")
    two(d, "R102", "VIN_L", "BUCK_EN", "330k")
    two(d, "R103", "BUCK_EN", "GND", "47k")
    two(d, "R104", "BUCK_RT", "GND", "220k")
    two(d, "R105", "BUCK_COMP", "BUCK_COMP_RC", "4.7k")
    two(d, "C107", "BUCK_COMP_RC", "GND", "22 nF")
    two(d, "C108", "BUCK_COMP", "GND", "100 pF")
    ordered(d, "D103", "BUCK_SW", "GND")
    two(d, "L101", "BUCK_SW", "+5V", "22 µH")
    for c in ("C109", "C110"):
        two(d, c, "+5V", "GND", "22 µF 25 V")
    two(d, "R106", "+5V", "BUCK_FB_MID", "47k")
    two(d, "R112", "BUCK_FB_MID", "BUCK_FB", "5.1k")
    two(d, "R107", "BUCK_FB", "GND", "10k")
    return d


def pow_08_buck_3v3():
    """POW-08. U102 TLV62569DBV SOT-23-5, datasheet SLVSDM0 p3: 1 EN, 2 GND, 3 SW, 4 VIN, 5 FB."""
    d = {}
    setp(d, "U102", {1: "VSYS", 2: "GND", 3: "SW3V3", 4: "VSYS", 5: "FB3V3"})
    two(d, "C111", "VSYS", "GND", "4.7 µF 16 V")
    two(d, "L102", "SW3V3", "+3V3", "2.2 µH")
    for c in ("C112", "C113"):
        two(d, c, "+3V3", "GND", "10 µF 10 V")
    two(d, "R108", "+3V3", "FB3V3", "100k")
    two(d, "R109", "FB3V3", "GND", "22k")
    two(d, "C115", "+3V3", "FB3V3", "22 pF")
    return d


# ================================================================ DRIVE (specs/modules/drive.md)
def _drv_pins(n, a):
    """TMC5240 TQFN-32, datasheet 19-101625C Rev 1 p15-18 (pin description table, TQFN32 column)."""
    u = "U%d01" % a
    d = {}
    setp(d, u, {1: "A%d_IREF" % n, 2: "GND", 3: "A%d_1V8" % n, 4: "GND", 5: "+3V3", 6: "GND", 7: "GND", 8: "GND",
                9: "DRV_ENN", 10: "GND", 11: "DIAG0_%d" % n, 12: "DIAG1_%d" % n, 13: None, 14: "A%d_CPI" % n,
                15: "A%d_CPO" % n, 16: "A%d_VCP" % n, 17: "VM", 18: "M%d_B1" % n, 19: "M%d_B2" % n, 20: "VM",
                21: "VM", 22: "M%d_A2" % n, 23: "M%d_A1" % n, 24: "VM", 25: "A%d_SLEEPN" % n, 26: "CS_DRV%d" % n,
                27: "SPI_SCK", 28: "SPI_MOSI", 29: "SPI_MISO", 30: "GND", 31: "HOME%d" % n, 32: "GND", 33: "GND"})
    return d


def drv_01_motor_connectors():
    """DRV-01. J?01 JST S4B-XH-A: 1 = OUT1A, 2 = OUT2A, 3 = OUT1B, 4 = OUT2B; bridge outputs pins 23, 22, 18, 19."""
    d = {}
    for n, a in AXES:
        setp(d, "J%d01" % a, {1: "M%d_A1" % n, 2: "M%d_A2" % n, 3: "M%d_B1" % n, 4: "M%d_B2" % n})
        setp(d, "U%d01" % a, {23: "M%d_A1" % n, 22: "M%d_A2" % n, 18: "M%d_B1" % n, 19: "M%d_B2" % n})
    return d


def drv_02_spi_and_selects():
    """DRV-02. TMC5240 p16: SPI mode UART_EN (10) and CLK (30) at GND; CSN 26, SCK 27, SDI 28, SDO 29."""
    d = {}
    for n, a in AXES:
        u = "U%d01" % a
        setp(d, u, {10: "GND", 30: "GND", 26: "CS_DRV%d" % n, 27: "SPI_SCK", 28: "SPI_MOSI", 29: "SPI_MISO"})
    return d


def drv_03_iref():
    """DRV-03. IREF (pin 1, p16) 12 kOhm 1 % to GND."""
    d = {}
    for n, a in AXES:
        d[("U%d01" % a, "1")] = "A%d_IREF" % n
        two(d, ref("R", a, 1), "A%d_IREF" % n, "GND", "12k")
    return d


def drv_04_diag_pullups():
    """DRV-04. DIAG0 (11) and DIAG1/SW (12) with 10 kOhm pull-ups to +3V3 (p17)."""
    d = {}
    for n, a in AXES:
        setp(d, "U%d01" % a, {11: "DIAG0_%d" % n, 12: "DIAG1_%d" % n})
        two(d, ref("R", a, 3), "DIAG0_%d" % n, "+3V3", "10k")
        two(d, ref("R", a, 4), "DIAG1_%d" % n, "+3V3", "10k")
    return d


def drv_05_exposed_pad():
    """DRV-05. Exposed pad = pad 33, ground (p18). The via count is a board check, not a netlist one."""
    return {("U%d01" % a, "33"): "GND" for n, a in AXES}


def drv_06_external_driver_port():
    """DRV-06. J?03 JST SM04B-GHS-TB: 1 +5V_EXT, 2 STEP, 3 DIR, 4 GND, MP GND. U703 SN74AHCT244 TSSOP-20 (SCLS228O p3):
    1OE 1, 1A1-4 2/4/6/8, 1Y1-4 18/16/14/12, 2OE 19, 2A1-4 11/13/15/17, 2Y1-4 9/7/5/3, GND 10, VCC 20."""
    d = {}
    for n, a in AXES:
        setp(d, "J%d03" % a, {1: "+5V_EXT", 2: "STEP%d_O" % n, 3: "DIR%d_O" % n, 4: "GND", "MP": "GND"})
        two(d, ref("R", a, 14), "STEP%d_B" % n, "STEP%d_O" % n, "220R")
        two(d, ref("R", a, 15), "DIR%d_B" % n, "DIR%d_O" % n, "220R")
    setp(d, "U703", {20: "+5V", 10: "GND", 1: "DRV_ENN", 19: "DRV_ENN"})
    for i, (a1, y1, a2, y2) in enumerate([(2, 18, 11, 9), (4, 16, 13, 7), (6, 14, 15, 5), (8, 12, 17, 3)], 1):
        setp(d, "U703", {a1: "DIAG0_%d" % i, y1: "STEP%d_B" % i, a2: "DIAG1_%d" % i, y2: "DIR%d_B" % i})
    two(d, "C703", "+5V", "GND", "100 nF")
    two(d, "F702", "+5V", "+5V_EXT")
    two(d, "C705", "+5V_EXT", "GND", "1 µF")
    return d


def drv_07_drv_enn():
    """DRV-07. DRV_ENN (pin 9) to all four drivers and U703 (1OE 1, 2OE 19), 10 kOhm pull-up R701 to +3V3."""
    d = {("U%d01" % a, "9"): "DRV_ENN" for n, a in AXES}
    setp(d, "U703", {1: "DRV_ENN", 19: "DRV_ENN"})
    two(d, "R701", "DRV_ENN", "+3V3", "10k")
    return d


def drv_08_supply_decoupling():
    """DRV-08. Supply and charge-pump pins (p16): VS 17/20/21/24, VCP 16, CPO 15, CPI 14, VDD1V8 3, VCC_IO 5, AGND 4."""
    d = {}
    for n, a in AXES:
        setp(d, "U%d01" % a, {17: "VM", 20: "VM", 21: "VM", 24: "VM", 16: "A%d_VCP" % n, 15: "A%d_CPO" % n,
                              14: "A%d_CPI" % n, 3: "A%d_1V8" % n, 5: "+3V3", 4: "GND"})
        two(d, ref("C", a, 1), "VM", "GND", "100 nF 50 V")
        two(d, ref("C", a, 2), "VM", "GND", "100 nF 50 V")
        two(d, ref("C", a, 3), "VM", "GND", "10 µF 50 V")
        two(d, ref("C", a, 4), "A%d_VCP" % n, "VM", "1 µF 50 V")
        two(d, ref("C", a, 5), "A%d_CPI" % n, "A%d_CPO" % n, "22 nF 50 V")
        two(d, ref("C", a, 6), "A%d_1V8" % n, "GND", "4.7 µF")
        two(d, ref("C", a, 7), "+3V3", "GND", "100 nF")
    return d


def drv_09_tie_offs():
    """DRV-09. AIN 2, ENCN 6, ENCB 7, ENCA 8, REFR 32 to GND; OV 13 open; SLEEPN 25 via 100 kOhm to VM (p16-18)."""
    d = {}
    for n, a in AXES:
        u = "U%d01" % a
        setp(d, u, {2: "GND", 6: "GND", 7: "GND", 8: "GND", 32: "GND", 13: None, 25: "A%d_SLEEPN" % n})
        two(d, ref("R", a, 2), "A%d_SLEEPN" % n, "VM", "100k")
    return d


def drv_10_output_esd():
    """DRV-10. 470 pF 50 V from each motor output to GND: C?08 A1, C?09 A2, C?10 B1, C?11 B2."""
    d = {}
    for n, a in AXES:
        for k, o in ((8, "A1"), (9, "A2"), (10, "B1"), (11, "B2")):
            two(d, ref("C", a, k), "M%d_%s" % (n, o), "GND", "470 pF 50 V")
    return d


# ================================================================ SENSING (specs/modules/sensing.md)
def enc_02_port_pinout():
    """ENC-02. J?02 JST SM07B-GHS-TB: 1 +3V3_SNS, 2 GND, 3 SCK, 4 MOSI, 5 MISO, 6 CS, 7 HOME, MP GND."""
    d = {}
    for n, a in AXES:
        setp(d, "J%d02" % a, {1: "+3V3_SNS", 2: "GND", 3: "SNS%d_SCK" % n, 4: "SNS%d_MOSI" % n, 5: "SNS%d_MISO" % n,
                              6: "SNS%d_CS" % n, 7: "HOME%d_IN" % n, "MP": "GND"})
    return d


def enc_03_home_input():
    """ENC-03. 10k pull-up, 22k series to REFL (TMC5240 pin 31, p16), 1 nF, BAT54S: pin 1 anode, pin 2 cathode, pin 3
    common (SOT-23 BAT54S, as the spec states)."""
    d = {}
    for n, a in AXES:
        h, hi = "HOME%d" % n, "HOME%d_IN" % n
        d[("U%d01" % a, "31")] = h
        two(d, ref("R", a, 5), hi, "+3V3", "10k")
        two(d, ref("R", a, 6), hi, h, "22k")
        two(d, ref("C", a, 12), h, "GND", "1 nF")
        setp(d, "D%d01" % a, {1: "GND", 2: "+3V3", 3: h})
    return d


def enc_05_isolation_buffers():
    """ENC-05. U701 SN74LVC244A TSSOP-20 (SCAS414AG p3, same pinout as AHCT244): 1OE 1, 1A1-4 2/4/6/8, 1Y1-4 18/16/14/12,
    2OE 19, 2A1-4 11/13/15/17, 2Y1-4 9/7/5/3, GND 10, VCC 20. U702 SN74LVC125A TSSOP-14 (SCAS290T p3): 1OE 1, 1A 2,
    1Y 3, 2OE 4, 2A 5, 2Y 6, GND 7, 3Y 8, 3A 9, 3OE 10, 4Y 11, 4A 12, 4OE 13, VCC 14. 100k pull-downs after the
    series resistors."""
    d = {}
    setp(d, "U701", {20: "+3V3", 10: "GND", 1: "CS_SNS_EN_N", 19: "CS_SNS_EN_N"})
    for i, (a1, y1, a2, y2) in enumerate([(2, 18, 11, 9), (4, 16, 13, 7), (6, 14, 15, 5), (8, 12, 17, 3)], 1):
        setp(d, "U701", {a1: "SPI_SCK", y1: "SNS_SCK%d_B" % i, a2: "SPI_MOSI", y2: "SNS_MOSI%d_B" % i})
    setp(d, "U702", {14: "+3V3", 7: "GND"})
    for i, (oe, a_, y) in enumerate([(1, 2, 3), (4, 5, 6), (10, 9, 8), (13, 12, 11)], 1):
        setp(d, "U702", {oe: "CS_SNS%d" % i, a_: "SNS%d_MISO_B" % i, y: "SPI_MISO"})
    for c in ("C701", "C702"):
        two(d, c, "+3V3", "GND", "100 nF")
    for n, a in AXES:
        two(d, ref("R", a, 11), "SNS%d_SCK" % n, "GND", "100k")
        two(d, ref("R", a, 12), "SNS%d_MOSI" % n, "GND", "100k")
        two(d, ref("R", a, 13), "SNS%d_MISO_B" % n, "GND", "100k")
    return d


def enc_06_series_resistors():
    """ENC-06. 33 R at the driving end (SCK, MOSI, CS), 100 R on MISO."""
    d = {}
    for n, a in AXES:
        two(d, ref("R", a, 7), "SNS_SCK%d_B" % n, "SNS%d_SCK" % n, "33R")
        two(d, ref("R", a, 8), "SNS_MOSI%d_B" % n, "SNS%d_MOSI" % n, "33R")
        two(d, ref("R", a, 9), "CS_SNS%d" % n, "SNS%d_CS" % n, "33R")
        two(d, ref("R", a, 10), "SNS%d_MISO" % n, "SNS%d_MISO_B" % n, "100R")
    return d


def enc_07_port_supply():
    """ENC-07. F701 +3V3 to +3V3_SNS, C704 4.7 uF after it."""
    d = {}
    two(d, "F701", "+3V3", "+3V3_SNS")
    two(d, "C704", "+3V3_SNS", "GND", "4.7 µF")
    return d


# ================================================================ CONTROL (specs/modules/control.md)
def ctl_01_mcu_supply_and_reset():
    """CTL-01. U201 3V3 pin 3, GND pins and pad (1, 2, 11, 14, 36-53), EN pin 8 (datasheet v1.5 p10-11); 22 uF and
    100 nF at the pin; EN 10k to +3V3, 1 uF to GND (no reset button; test point TP922)."""
    d = {}
    setp(d, "U201", {3: "+3V3", 8: "EN"})
    same(d, "U201", MCU_GND, "GND")
    two(d, "C201", "+3V3", "GND", "22 µF")
    two(d, "C202", "+3V3", "GND", "100 nF")
    two(d, "R201", "EN", "+3V3", "10k")
    two(d, "C203", "EN", "GND", "1 µF")
    return d


def ctl_01a_strapping_boot():
    """CTL-01a. GPIO9 = BOOT: 10k to +3V3 and SW201 to GND. GPIO8 is held high by the I2C pull-up (ctl_09)."""
    d = {}
    two(d, "SW201", "BOOT", "GND")
    two(d, "R202", "BOOT", "+3V3", "10k")
    return d


def ctl_01b_stop_pins_direct():
    """CTL-01b / CTL-10 / CTL-09. Every MCU IO pin carries the net pins.h gives its GPIO (SPI_SCK and SPI_MOSI as
    *_MCU), unused IO pins and the NC pins are open. pins.h must also define the nets the specs call direct pins.
    ESP32-C6-MINI-1 datasheet v1.5 Table 3-1, p10-11."""
    d = {}
    P, _ = parse_pins_h()
    used = {}
    for net, gpio in P.items():
        pin = GPIO_PIN.get(gpio)
        if pin is None:
            d[("U201", "pins.h:PIN_%s=%d" % (net, gpio))] = "a GPIO that the module brings out"
            continue
        if pin in used:
            d[("U201", "pins.h:GPIO%d twice" % gpio)] = "one net per GPIO (%s, %s)" % (used[pin], net)
        used[pin] = net
        d[("U201", str(pin))] = MCU_RENAME.get(net, net)
    for net in MCU_NEEDED:
        if net not in P:
            d[("U201", "pins.h:PIN_%s" % net)] = "defined in pins.h"
    for gpio, pin in GPIO_PIN.items():
        if pin not in used:
            d[("U201", str(pin))] = None
    same(d, "U201", MCU_NC, None)
    return d


def ctl_01c_spi_series_resistors():
    """CTL-10. R203/R204 22 R between the module's SPI pins and the bus; R702 100k pull-down on SPI_MISO."""
    d = {}
    two(d, "R203", "SPI_SCK_MCU", "SPI_SCK", "22R")
    two(d, "R204", "SPI_MOSI_MCU", "SPI_MOSI", "22R")
    two(d, "R702", "SPI_MISO", "GND", "100k")
    return d


def ctl_08_chip_selects():
    """CTL-08. U202 SN74LVC139A TSSOP-16 (SCAS341O p1): 1G 1, 1A 2, 1B 3, 1Y0-3 4/5/6/7, GND 8, 2Y3 9, 2Y2 10, 2Y1 11,
    2Y0 12, 2B 13, 2A 14, 2G 15, VCC 16. Strobe and ETH_CS_N pull-ups 10k."""
    d = {}
    setp(d, "U202", {16: "+3V3", 8: "GND", 1: "CS_DRV_EN_N", 2: "CS_A0", 3: "CS_A1", 4: "CS_DRV1", 5: "CS_DRV2",
                     6: "CS_DRV3", 7: "CS_DRV4", 15: "CS_SNS_EN_N", 14: "CS_A0", 13: "CS_A1", 12: "CS_SNS1",
                     11: "CS_SNS2", 10: "CS_SNS3", 9: "CS_SNS4"})
    two(d, "C204", "+3V3", "GND", "100 nF")
    two(d, "R205", "CS_DRV_EN_N", "+3V3", "10k")
    two(d, "R206", "CS_SNS_EN_N", "+3V3", "10k")
    two(d, "R207", "ETH_CS_N", "+3V3", "10k")
    return d


def ctl_09_io_expander():
    """CTL-09. U203 PCAL6416APW TSSOP-24 (NXP Rev 7.1 p4 and Table 3): 1 INT, 2 VDD(I2C), 3 RESET, 4-11 P0_0-P0_7, 12 VSS,
    13-20 P1_0-P1_7, 21 ADDR, 22 SCL, 23 SDA, 24 VDD(P). Bits from pins.h. TMP1075 U204 VSSOP-8 (SBOS854F p4):
    1 SDA, 2 SCL, 3 ALERT, 4 GND, 5 A2, 6 A1, 7 A0, 8 V+. I2C pull-ups 2.2k."""
    d = {}
    setp(d, "U203", {1: "XINT_N", 2: "+3V3", 3: "EN", 12: "GND", 21: "GND", 22: "I2C_SCL", 23: "I2C_SDA", 24: "+3V3"})
    _, X = parse_pins_h()
    used = set()
    for net, bit in X.items():
        if not 0 <= bit <= 15:
            d[("U203", "pins.h:XP_%s=%d" % (net, bit))] = "a bit from 0 to 15"
            continue
        if bit in used:
            d[("U203", "pins.h:bit %d twice" % bit)] = "one net per bit"
        used.add(bit)
        d[("U203", str(xp_pin(bit)))] = net
    for net in XP_NEEDED:
        if net not in X:
            d[("U203", "pins.h:XP_%s" % net)] = "defined in pins.h"
    for bit in range(16):
        if bit not in used:
            d[("U203", str(xp_pin(bit)))] = None
    two(d, "C205", "+3V3", "GND", "100 nF")
    two(d, "R208", "XINT_N", "+3V3", "10k")
    setp(d, "U204", {1: "I2C_SDA", 2: "I2C_SCL", 3: None, 4: "GND", 5: "GND", 6: "GND", 7: "GND", 8: "+3V3"})
    two(d, "C206", "+3V3", "GND", "100 nF")
    two(d, "R209", "I2C_SDA", "+3V3", "2.2k")
    two(d, "R210", "I2C_SCL", "+3V3", "2.2k")
    return d


def ctl_07_usb_c():
    """CTL-07. J201 USB-C 16 pin: VBUS A4 A9 B4 B9, GND A1 A12 B1 B12, CC1 A5, CC2 B5, D+ A6 B6, D- A7 B7, SBU A8 B8,
    shield SH (USB Type-C spec pinout; not verifiable against the HRO drawing). U205 USBLC6-2SC6 (ST datasheet, not in
    the folder): 1 and 6 I/O1, 2 GND, 3 and 4 I/O2, 5 VBUS. D- to I/O1, D+ to I/O2."""
    d = {}
    same(d, "J201", ["A4", "A9", "B4", "B9"], "VBUS")
    same(d, "J201", ["A1", "A12", "B1", "B12", "SH"], "GND")
    setp(d, "J201", {"A5": "CC1", "B5": "CC2", "A6": "USB_DP", "B6": "USB_DP", "A7": "USB_DN", "B7": "USB_DN",
                     "A8": None, "B8": None})
    two(d, "R211", "CC1", "GND", "5.1k")
    two(d, "R212", "CC2", "GND", "5.1k")
    setp(d, "U205", {1: "USB_DN", 6: "USB_DN", 3: "USB_DP", 4: "USB_DP", 2: "GND", 5: "VBUS"})
    two(d, "C207", "VBUS", "GND", "1 µF")
    return d


def aux_01_i2c_port():
    """AUX-01. J202 JST SM04B-SRSS-TB: 1 GND, 2 +3V3_I2C, 3 SDA, 4 SCL, MP GND; F201 PTC and 1 uF."""
    d = {}
    setp(d, "J202", {1: "GND", 2: "+3V3_I2C", 3: "I2C_SDA", 4: "I2C_SCL", "MP": "GND"})
    two(d, "F201", "+3V3", "+3V3_I2C")
    two(d, "C208", "+3V3_I2C", "GND", "1 µF")
    return d


def ctl_03_w5500():
    """CTL-03. U801 W5500 LQFP-48, datasheet v1.1.0 p7-10 (Table 2). AVDD 4/8/11/15/17/21, AGND 3/9/14/16/19/48,
    NC 12/13/46/47, RSVD 23 (to GND) and 38-42, PMODE2/1/0 43/44/45."""
    d = {}
    setp(d, "U801", {1: "ETH_TXN", 2: "ETH_TXP", 5: "ETH_RXN", 6: "ETH_RXP", 10: "ETH_RES", 20: "ETH_TOCAP",
                     22: "ETH_1V2", 23: "GND", 25: "ETH_LINK", 27: "ETH_ACT", 28: "+3V3", 29: "GND", 30: "ETH_XI",
                     31: "ETH_XO", 32: "ETH_CS_N", 33: "SPI_SCK", 34: "SPI_MISO", 35: "SPI_MOSI", 36: "ETH_INT_N",
                     37: "ETH_RST_N"})
    same(d, "U801", [4, 8, 11, 15, 17, 21], "3V3A")
    same(d, "U801", [3, 9, 14, 16, 19, 48], "GND")
    same(d, "U801", [43, 44, 45], "+3V3")
    same(d, "U801", [7, 18, 24, 26, 38, 39, 40, 41, 42, 12, 13, 46, 47], None)   # DNC VBG SPDLED DUPLED RSVD NC
    return d


def ctl_03_jack_header_and_leds():
    """CTL-03. J801 JST SM07B-GHS-TB header to an off-board jack (control.md): 1 TCT, 2 GND, 3 TD+, 4 TD-, 5 RD+, 6 RD-,
    7 RCT, MP GND. Termination network after the W5500 reference schematic. D802/D803 red LEDs (pin 1 cathode, pin 2
    anode) on 1k from LINKLED/ACTLED (W5500 p9: active-low outputs)."""
    d = {}
    setp(d, "J801", {1: "ETH_TCT", 2: "GND", 3: "ETH_TXP", 4: "ETH_TXN", 5: "ETH_RDP", 6: "ETH_RDN", 7: "ETH_RCT",
                     "MP": "GND"})
    two(d, "R803", "ETH_TXP", "3V3A", "49.9R")
    two(d, "R804", "ETH_TXN", "3V3A", "49.9R")
    two(d, "R805", "3V3A", "ETH_TCT", "10R")
    two(d, "C812", "ETH_TCT", "GND", "22 nF")
    two(d, "R806", "ETH_RXP", "ETH_RCT", "49.9R")
    two(d, "R807", "ETH_RXN", "ETH_RCT", "49.9R")
    two(d, "C813", "ETH_RXP", "ETH_RDP", "6.8 nF")
    two(d, "C814", "ETH_RXN", "ETH_RDN", "6.8 nF")
    two(d, "C815", "ETH_RCT", "GND", "10 nF")
    ordered(d, "D802", "ETH_LED_L", "+3V3")
    ordered(d, "D803", "ETH_LED_A", "+3V3")
    two(d, "R808", "ETH_LINK", "ETH_LED_L", "1k")
    two(d, "R809", "ETH_ACT", "ETH_LED_A", "1k")
    return d


def ctl_03_supply_clock_reset():
    """CTL-03. Ferrite bead, decoupling, EXRES1 12.4k, TOCAP 4.7 uF, 1V2O 10 nF (W5500 p8-9), crystal Y801 (pads 1 and 3
    the crystal, 2 and 4 the case), interrupt and reset pull-ups."""
    d = {}
    two(d, "FB801", "+3V3", "3V3A")
    for c in ("C801", "C802", "C803", "C804"):
        two(d, c, "3V3A", "GND", "100 nF")
    two(d, "C805", "3V3A", "GND", "10 µF")
    two(d, "C806", "+3V3", "GND", "100 nF")
    two(d, "C807", "+3V3", "GND", "4.7 µF")
    two(d, "R801", "ETH_RES", "GND", "12.4k")
    two(d, "C808", "ETH_TOCAP", "GND", "4.7 µF")
    two(d, "C809", "ETH_1V2", "GND", "10 nF")
    d[("Y801", "1,3")] = ("ETH_XI", "ETH_XO")
    same(d, "Y801", [2, 4], "GND")
    two(d, "C810", "ETH_XI", "GND", "18 pF")
    two(d, "C811", "ETH_XO", "GND", "18 pF")
    two(d, "R802", "ETH_XI", "ETH_XO", "1M")
    two(d, "R810", "ETH_INT_N", "+3V3", "10k")
    two(d, "R811", "ETH_RST_N", "+3V3", "10k")
    return d


def ctl_04_rs485():
    """CTL-04. U802 SP3485 SOIC-8 (MaxLinear Rev 2.0.2 p4): 1 RO, 2 RE, 3 DE, 4 DI, 5 GND, 6 A, 7 B, 8 VCC.
    D801 SM712 (not in folder): 1 and 2 lines, 3 ground. J802 JST SM04B-GHS-TB."""
    d = {}
    setp(d, "U802", {8: "+3V3", 5: "GND", 1: "RS485_RX", 2: "RS485_DE", 3: "RS485_DE", 4: "RS485_TX", 6: "RS485_A",
                     7: "RS485_B"})
    two(d, "C816", "+3V3", "GND", "100 nF")
    two(d, "R812", "RS485_DE", "GND", "10k")
    two(d, "R813", "RS485_RX", "+3V3", "10k")
    setp(d, "D801", {1: "RS485_A", 2: "RS485_B", 3: "GND"})
    two(d, "R814", "RS485_A", "RS485_TERM", "120R")
    two(d, "JP801", "RS485_TERM", "RS485_B")
    setp(d, "J802", {1: "RS485_A", 2: "RS485_B", 3: "GND", 4: "GND", "MP": "GND"})
    return d


def ctl_06_can():
    """CTL-06. U803 TJA1051T/3 SO8 (NXP Rev 9 p4): 1 TXD, 2 GND, 3 VCC, 4 RXD, 5 VIO, 6 CANL, 7 CANH, 8 S.
    JP802 is bridged as delivered, so its two pads may also show up as one net (CAN_TERM or CAN_L)."""
    d = {}
    setp(d, "U803", {1: "CAN_TX", 2: "GND", 3: "+5V", 4: "CAN_RX", 5: "+3V3", 6: "CAN_L", 7: "CAN_H", 8: "GND"})
    two(d, "C817", "+5V", "GND", "100 nF")
    two(d, "C818", "+3V3", "GND", "100 nF")
    two(d, "R815", "CAN_H", "CAN_TERM", "120R")
    two(d, "JP802", "CAN_TERM", "CAN_L")
    setp(d, "J803", {1: "CAN_H", 2: "CAN_L", 3: "GND", 4: "GND", "MP": "GND"})
    return d


# ================================================================ I/O (specs/modules/io.md)
def cam_02_tally_record():
    """CAM-02. AO3422 SOT-23 (datasheet p1 drawing; io.md: 1 gate, 2 source, 3 drain). J901: 1 tally, 2 record,
    3 and 4 GND, MP GND."""
    d = {}
    setp(d, "Q901", {1: "TALLY", 2: "GND", 3: "TALLY_OD"})
    setp(d, "Q902", {1: "REC", 2: "GND", 3: "REC_OD"})
    two(d, "R901", "TALLY", "GND", "100k")
    two(d, "R902", "REC", "GND", "100k")
    setp(d, "J901", {1: "TALLY_OD", 2: "REC_OD", 3: "GND", 4: "GND", "MP": "GND"})
    return d


def aux_03_fan():
    """AUX-03. Q903 AO3422; D901 flyback (K = FAN_V = pin 1, A = FAN_N = pin 2); JP901 pads 1 +5V, 2 FAN_SRC, 3 VM;
    J902 JST S2B-XH-A: 1 FAN_V, 2 FAN_N."""
    d = {}
    setp(d, "Q903", {1: "FAN_G", 2: "GND", 3: "FAN_N"})
    two(d, "R903", "FAN_PWM", "FAN_G", "100R")
    two(d, "R904", "FAN_G", "GND", "100k")
    ordered(d, "D901", "FAN_V", "FAN_N")
    setp(d, "JP901", {1: "+5V", 2: "FAN_SRC", 3: "VM"})
    two(d, "F901", "FAN_SRC", "FAN_V")
    setp(d, "J902", {1: "FAN_V", 2: "FAN_N"})
    return d


def aux_02_status_led():
    """AUX-02. D201: 1 red cathode, 2 green cathode, 3 blue cathode, 4 common anode (JLC library order per spec)."""
    d = {}
    setp(d, "D201", {1: "LED_R_K", 2: "LED_G_K", 3: "LED_B_K", 4: "+3V3"})
    two(d, "R213", "LED_R_K", "LED_R_N", "1k")
    two(d, "R214", "LED_G_K", "LED_G_N", "220R")
    two(d, "R215", "LED_B_K", "LED_B_N", "220R")
    return d


def aux_05_test_points():
    """AUX-05. One pad each, pin 1."""
    nets = ["VIN", "VM", "+5V", "VSYS", "+3V3", "GND", "GND", "SPI_SCK", "SPI_MOSI", "SPI_MISO", "I2C_SDA", "I2C_SCL",
            "DRV_ENN", "XINT_N", "CS_DRV_EN_N", "CS_SNS_EN_N", "SPARE", "CAN_TX", "CAN_RX", "RS485_TX", "RS485_RX"]
    # table order in io.md: column-wise TP901-907, TP908-914, TP915-921
    col = [("VIN", "VM", "+5V", "VSYS", "+3V3", "GND", "GND"),
           ("SPI_SCK", "SPI_MOSI", "SPI_MISO", "I2C_SDA", "I2C_SCL", "DRV_ENN", "XINT_N"),
           ("CS_DRV_EN_N", "CS_SNS_EN_N", "SPARE", "CAN_TX", "CAN_RX", "RS485_TX", "RS485_RX")]
    d = {}
    for c, names in enumerate(col):
        for i, net in enumerate(names):
            d[("TP%d" % (901 + 7 * c + i), "1")] = net
    d[("TP922", "1")] = "EN"
    nets.append("EN")
    assert sorted(nets) == sorted(sum(col, ()) + ("EN",))
    return d


FUNCS = sorted((n, f) for n, f in list(globals().items())
               if re.match(r"^(pow|drv|enc|ctl|cam|aux)_\d\d[a-z]?_", n) and callable(f))


# ---------------------------------------------------------------- runner
def load_netlist():
    if not os.path.exists(SCH):
        return {}, {}, "no schematic at hardware/ptz-driver.kicad_sch: netlist treated as empty"
    try:
        from netlist import components, export, pin_nets
        tree = export(SCH)
        return pin_nets(tree), components(tree), None
    except Exception as e:  # kicad-cli missing or the export failed: every expectation then fails
        return {}, {}, "netlist export failed (%s: %s): netlist treated as empty" % (type(e).__name__, e)


def norm(v):
    v = v.lower().replace("µ", "u").replace("μ", "u").replace("ω", "").replace("ohm", "").replace(" ", "")
    return re.sub(r"(?<=\d)r(?![a-z])", "", v)


def value_ok(want, got):
    w, g = norm(want), norm(got)
    s, l = (w, g) if len(w) <= len(g) else (g, w)
    return l.startswith(s) and (len(l) == len(s) or not (l[len(s)].isdigit() or l[len(s)] == "."))


def main():
    nets, comps, note = load_netlist()
    count = {}
    members = {}
    for (r, p), n in nets.items():
        count[n] = count.get(n, 0) + 1
        members.setdefault(n, set()).add(r)

    def net_of(r, p):
        return nets.get((r, p))

    def unconnected(r, p):
        n = net_of(r, p)
        return n is None or n.startswith("unconnected-") or count.get(n, 0) <= 1

    lines, total_pins, total_bad, mentioned, missing = [], 0, 0, set(), set()
    if note:
        print("NOTE: " + note)
    for name, fn in FUNCS:
        fid = re.sub(r"^(\w+?)_(\d\d[a-z]?)_.*", lambda m: "%s-%s" % (m.group(1).upper(), m.group(2)), name)
        try:
            exp = fn()
        except Exception as e:
            print("%s: function failed (%s: %s)" % (name, type(e).__name__, e))
            total_bad += 1
            continue
        checked, bad, gone = 0, [], {}
        for (r, pin), want in exp.items():
            mentioned.add(r)
            pins = pin.split(",")
            checked += len(pins)
            if r not in comps:
                gone[r] = gone.get(r, 0) + len(pins)
                continue
            if pin.startswith("pins.h:"):
                bad.append("%s %s.%s: expected %s, is not so" % (fid, r, pin, want))
            elif "," in pin:
                got = tuple(net_of(r, p) for p in pins)
                ok = sorted(map(str, got)) == sorted(want)
                if not ok and r == "JP802" and got[0] == got[1] and got[0] in want:   # bridged jumper, merged nets
                    ok = True
                if not ok:
                    bad.append("%s %s.%s: expected %s in either order, is %s" % (fid, r, pin, want, got))
            elif want is None:
                if not unconnected(r, pin):
                    bad.append("%s %s.%s: expected unconnected, is %s" % (fid, r, pin, net_of(r, pin)))
            elif net_of(r, pin) != want:
                bad.append("%s %s.%s: expected %s, is %s" % (fid, r, pin, want, net_of(r, pin) or "(no net)"))
        for r, k in sorted(gone.items()):
            missing.add(r)
            bad.append("%s %s: missing from the netlist (%d pins)" % (fid, r, k))
        nbad = len(bad) - len(gone) + sum(gone.values())
        for net, allowed in NET_ONLY.get(name, []):
            checked += 1
            extra = sorted(members.get(net, set()) - allowed)
            if extra:
                nbad += 1
                bad.append("%s net %s: parts that the specs do not put there: %s" % (fid, net, ", ".join(extra)))
        for r, v in VAL.items():
            if r in exp_refs(exp) and r in comps and not value_ok(v, comps[r]["value"]):
                nbad += 1
                bad.append("%s %s value: expected %s, is %s" % (fid, r, v, comps[r]["value"]))
        total_pins += checked
        total_bad += nbad
        lines.append("%-40s %4d pins checked, %d mismatches" % (name, checked, nbad))
        lines.extend(bad)
    for ln in lines:
        print(ln)
    extras = sorted(r for r in set(comps) - mentioned if not re.match(r"^H\d+$", r))
    for r in extras:
        print("WARNING: %s is in the netlist but no spec table mentions it" % r)
    print("%d references that the specs mention are missing from the netlist" % len(missing))
    print("TOTAL: %d functions, %d pins checked, %d mismatches, %d warnings" % (len(FUNCS), total_pins, total_bad, len(extras)))
    return 1 if total_bad else 0


def exp_refs(exp):
    return {r for r, _ in exp}


if __name__ == "__main__":
    sys.exit(main())
