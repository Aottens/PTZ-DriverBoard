#!/usr/bin/env python3
"""Independent netlist check for the PTZ driver board, Rev B.

Expectations are derived from specs/modules/{power,drive,sensing,control,io}.md and the manufacturers' pinouts,
never from the schematic. The GPIO of every net comes from firmware/include/pins.h at run time.

One function per acceptance criterion, named after its id (pow_02a_..., drv_02_...). Each returns
{(ref, pad): expected_net}. Special forms:
  * expected None             -> pad must be unconnected (absent, "unconnected-*", or alone on its net)
  * key (ref, "1,2")          -> two-pad part without polarity: the two pads carry the pair (a, b) in either order
  * key (ref, "pins.h:...")   -> a pins.h consistency problem (never present in a netlist, so it always fails)
Pad numbers are footprint pad names. Conventions of the build brief:
  diodes D101 D102 D201 D801 D301..D601: pad 1 cathode, pad 2 anode. C111 and C101..C104: pad 1 plus.
  BAV99 (D302..D602): 1 anode, 2 cathode, 3 common. Q101 (TO-252): 1 gate, 2 drain, 3 source.
  Q801 (SOT-23): 1 gate, 2 source, 3 drain. U102 (SOT-223): 1 ground, 2 out, 3 in. U103: 1 ground, 2 out, 3 in.
  U101 (SIP-3): 1 in, 2 ground, 3 out. Axis n = 1..4 has reference hundreds a = n + 2.
A closed solder jumper may be drawn as a bridge that merges its two nets: for a two-pad jumper, and for pads 1 and 2
of JP101 and JP801, both pads on one of the two expected nets also passes.

Run from the repo root:  python3 hardware/check_netlist.py [--list]     Exit 0 only when there is no mismatch.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = os.path.join(ROOT, "hardware", "ptz-driver.kicad_sch")
PINS_H = os.path.join(ROOT, "firmware", "include", "pins.h")
sys.path.insert(0, os.path.join(ROOT, "hardware", "tools"))

VAL = {}          # ref -> value the spec text gives (R and C), number and prefix compared, rating ignored
NET_ONLY = {}     # function name -> [(net, {refs allowed on it})]
AXES = [(n, n + 2) for n in range(1, 5)]   # axis n -> reference hundreds a (axis 1 = 3xx)
BRIDGE12 = {"JP101", "JP801"}              # three-pad jumpers whose pads 1 and 2 are closed as delivered


# ---------------------------------------------------------------- helpers
def two(d, ref, a, b, val=None):
    """Two-pad part without polarity, nets a and b in either order."""
    d[(ref, "1,2")] = (a, b)
    if val:
        VAL[ref] = val


def ordered(d, ref, a, b, val=None):
    """Two-pad part with polarity: pad 1 = a, pad 2 = b."""
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


# ---------------------------------------------------------------- pins.h and the A201 header (control.md)
def parse_pins_h():
    try:
        text = open(PINS_H).read()
    except OSError:
        return {}
    return {net: int(num) for net, num in re.findall(r"^\s*#define\s+PIN_(\w+)\s+(\d+)", text, re.M)}


# control.md "The modules": socket pad -> header pin name / GPIO. Pads 1..22 are J1, pads 23..44 are J3.
J1 = {1: "3V3", 2: "3V3", 3: "EN", 4: 4, 5: 5, 6: 6, 7: 7, 8: 15, 9: 16, 10: 17, 11: 18, 12: 8, 13: 3, 14: 46,
      15: 9, 16: 10, 17: 11, 18: 12, 19: 13, 20: 14, 21: "5V", 22: "GND"}
J3 = [("GND"), 43, 44, 1, 2, 42, 41, 40, 39, 38, 37, 36, 35, 0, 45, 48, 47, 21, 20, 19, "GND", "GND"]
A201 = dict(J1)
A201.update({22 + i + 1: v for i, v in enumerate(J3)})
GPIO_PAD = {v: p for p, v in A201.items() if isinstance(v, int)}
FORBIDDEN = {35, 36, 37, 0, 19, 20, 44, 38}        # CTL-08 "not used at all"
UNUSED_PADS = [GPIO_PAD[g] for g in (44, 38, 37, 36, 35, 0, 20, 19)]   # CTL-09: 25, 32..35, 36, 41, 42
NETS28 = (["SPI_MOSI", "SPI_SCK", "SPI_MISO"] + ["DRV%d_CS" % n for n in range(1, 5)] +
          ["STEP%d" % n for n in range(1, 5)] + ["DIR%d" % n for n in range(1, 5)] +
          ["DRV_ENN", "DIAG_OR", "ETH_CS_N", "ETH_INT_N", "I2C_SDA", "I2C_SCL"] +
          ["HOME%d" % n for n in range(1, 5)] + ["VM_SENSE", "NTC_SENSE", "FAN_PWM"])
MCU_RENAME = {"SPI_SCK": "SPI_SCK_MCU", "SPI_MOSI": "SPI_MOSI_MCU"}       # CTL-05, CTL-08


def pins_h_problems(pins):
    """CTL-08 demands of pins.h itself. Returns {(A201, 'pins.h:<what>'): requirement}."""
    bad = {}

    def flag(what, req):
        bad[("A201", "pins.h:" + what)] = req
    for n in NETS28:
        if n not in pins:
            flag(n + " missing", "PIN_%s defined" % n)
    for n in sorted(set(pins) - set(NETS28)):
        flag(n + " not in the 28", "no PIN_%s (not one of the 28 nets)" % n)
    by_gpio = {}
    for n, g in pins.items():
        by_gpio.setdefault(g, []).append(n)
    for g, ns in sorted(by_gpio.items()):
        if len(ns) > 1:
            flag("GPIO%d twice" % g, "GPIO%d on one net only, is on %s" % (g, "+".join(sorted(ns))))
        if g in FORBIDDEN:
            flag("GPIO%d forbidden" % g, "GPIO%d unused, is %s" % (g, "+".join(sorted(ns))))
        elif g not in GPIO_PAD:
            flag("GPIO%d not on header" % g, "GPIO%d on a header pad of A201" % g)
    for n in ("VM_SENSE", "NTC_SENSE"):
        if n in pins and not 1 <= pins[n] <= 10:
            flag(n + " not ADC1", "%s on GPIO1..10, is GPIO%d" % (n, pins[n]))
    if pins.get("FAN_PWM") != 45:
        flag("FAN_PWM not GPIO45", "FAN_PWM on GPIO45")
    if pins.get("DIAG_OR") != 46:
        flag("DIAG_OR not GPIO46", "DIAG_OR on GPIO46")
    for g in (43, 48):
        for n in by_gpio.get(g, []):
            if not n.startswith("HOME"):
                flag("GPIO%d on %s" % (g, n), "GPIO%d only on a HOME net" % g)
    for g, only in ((45, "FAN_PWM"), (46, "DIAG_OR")):
        for n in by_gpio.get(g, []):
            if n != only:
                flag("GPIO%d on %s" % (g, n), "GPIO%d only on %s" % (g, only))
    return bad


# ================================================================ POWER (specs/modules/power.md)
def pow_01_input():
    """POW-01. J101 JST B2P-VH: pin 1 VIN_RAW (plus), pin 2 GND."""
    return {("J101", "1"): "VIN_RAW", ("J101", "2"): "GND"}


def pow_02a_reverse_polarity():
    """POW-02a. Q101 AOD4185 TO-252: 1 gate RP_GATE, 2 drain VIN_RAW, 3 source VIN. R101 RP_GATE-VIN, R102 RP_GATE-GND."""
    d = {}
    setp(d, "Q101", {1: "RP_GATE", 2: "VIN_RAW", 3: "VIN"})
    two(d, "R101", "RP_GATE", "VIN", "150k")
    two(d, "R102", "RP_GATE", "GND", "100k")
    return d


def pow_02b_hotplug_clamp():
    """POW-02b. C101..C104 plus on VM; D101 cathode VM, anode GND."""
    d = {}
    for c in ("C101", "C102", "C103", "C104"):
        ordered(d, c, "VM", "GND", "100 µF")
    ordered(d, "D101", "VM", "GND")
    return d


def pow_03_separate_fuses():
    """POW-03. F101 VIN-VM, F102 VIN-VIN_L. Only Q101, R101, F101, F102, TP801 on VIN."""
    d = {}
    two(d, "F101", "VIN", "VM")
    two(d, "F102", "VIN", "VIN_L")
    NET_ONLY["pow_03_separate_fuses"] = [("VIN", {"Q101", "R101", "F101", "F102", "TP801"})]
    return d


def pow_05_usb_blocking_diode():
    """POW-05. D102 cathode +5V, anode +5V_REG."""
    d = {}
    ordered(d, "D102", "+5V", "+5V_REG")
    return d


def pow_06_vm_sense():
    """POW-06. VM / 11: R103 VM-VM_SENSE, R104 and C115 VM_SENSE-GND."""
    d = {}
    two(d, "R103", "VM", "VM_SENSE", "100k")
    two(d, "R104", "VM_SENSE", "GND", "10k")
    two(d, "C115", "VM_SENSE", "GND", "100 nF")
    return d


def pow_07_regulator_5v():
    """POW-07. U101 SIP-3: 1 VIN_L, 2 GND, 3 +5V_REG. C105 C106 on VIN_L, C107 on +5V_REG, C108 C109 on +5V."""
    d = {}
    setp(d, "U101", {1: "VIN_L", 2: "GND", 3: "+5V_REG"})
    two(d, "C105", "VIN_L", "GND", "10 µF")
    two(d, "C106", "VIN_L", "GND", "100 nF")
    two(d, "C107", "+5V_REG", "GND", "22 µF")
    two(d, "C108", "+5V", "GND", "22 µF")
    two(d, "C109", "+5V", "GND", "100 nF")
    NET_ONLY["pow_07_regulator_5v"] = [("VIN_L", {"F102", "U101", "C105", "C106"}),
                                       ("+5V_REG", {"U101", "D102", "C107"})]
    return d


def pow_08_regulators_3v3():
    """POW-08. U102 SOT-223 (1 GND, 2 +3V3, 3 +5V); U103 (1 GND, 2 +3V3_SNS, 3 +5V); JP101 1 +3V3_SNS, 2 V_SNS, 3 +5V."""
    d = {}
    setp(d, "U102", {1: "GND", 2: "+3V3", 3: "+5V"})
    two(d, "C110", "+5V", "GND", "10 µF")
    ordered(d, "C111", "+3V3", "GND", "100 µF")
    two(d, "C112", "+3V3", "GND", "100 nF")
    setp(d, "U103", {1: "GND", 2: "+3V3_SNS", 3: "+5V"})
    two(d, "C113", "+5V", "GND", "22 µF")
    ordered(d, "C114", "+3V3_SNS", "GND", "100 µF")
    setp(d, "JP101", {1: "+3V3_SNS", 2: "V_SNS", 3: "+5V"})
    return d


# ================================================================ DRIVE (specs/modules/drive.md)
def drv_01_sockets():
    """DRV-01. Supply and unused pads of the socket table: 9 VM, 10 and 16 GND, 15 +3V3, 6 and 17 not connected."""
    d = {}
    for n, a in AXES:
        s = "A%d01" % a
        setp(d, s, {9: "VM", 10: "GND", 15: "+3V3", 16: "GND", 6: None, 17: None})
    return d


def drv_02_driver_bus():
    """DRV-02. Pads 2 DRVn_SDI, 3 DRVn_SCK, 4 DRVn_CSP, 5 DRVn_SDO; jumpers JPa01..03; Ra01 DRVn_CS-DRVn_CSP."""
    d = {}
    for n, a in AXES:
        setp(d, "A%d01" % a, {2: "DRV%d_SDI" % n, 3: "DRV%d_SCK" % n, 4: "DRV%d_CSP" % n, 5: "DRV%d_SDO" % n})
        two(d, "JP%d01" % a, "DRV%d_SDI" % n, "SPI_MOSI")
        two(d, "JP%d02" % a, "DRV%d_SCK" % n, "SPI_SCK")
        two(d, "JP%d03" % a, "DRV%d_SDO" % n, "SPI_MISO")
        two(d, "R%d01" % a, "DRV%d_CS" % n, "DRV%d_CSP" % n, "1k")
    return d


def drv_04_enable():
    """DRV-04. Pad 1 of every socket DRV_ENN; R203 DRV_ENN-+3V3."""
    d = {}
    for n, a in AXES:
        d[("A%d01" % a, "1")] = "DRV_ENN"
    two(d, "R203", "DRV_ENN", "+3V3", "10k")
    return d


def drv_05_stall_fault():
    """DRV-05. Pad 18 DIAGn; Da01 cathode DIAG_OR, anode DIAGn; R205 DIAG_OR-GND."""
    d = {}
    for n, a in AXES:
        d[("A%d01" % a, "18")] = "DIAG%d" % n
        ordered(d, "D%d01" % a, "DIAG_OR", "DIAG%d" % n)
    two(d, "R205", "DIAG_OR", "GND", "10k")
    NET_ONLY["drv_05_stall_fault"] = [("DIAG_OR", {"D301", "D401", "D501", "D601", "R205", "A201", "TP814"})]
    return d


def drv_06_step_dir():
    """DRV-06. Pad 7 STEPn, pad 8 DIRn."""
    d = {}
    for n, a in AXES:
        setp(d, "A%d01" % a, {7: "STEP%d" % n, 8: "DIR%d" % n})
    return d


def drv_07_motor_connector():
    """DRV-07. Socket pads 11..14 Mn_1..Mn_4, and Ja01 pins 1..4 the same."""
    d = {}
    for n, a in AXES:
        for k in range(1, 5):
            d[("A%d01" % a, str(10 + k))] = "M%d_%d" % (n, k)
            d[("J%d01" % a, str(k))] = "M%d_%d" % (n, k)
    return d


def drv_08_decoupling():
    """DRV-08. Ca01 VM-GND, Ca02 +3V3-GND."""
    d = {}
    for n, a in AXES:
        two(d, "C%d01" % a, "VM", "GND", "100 nF")
        two(d, "C%d02" % a, "+3V3", "GND", "100 nF")
    return d


# ================================================================ SENSING (specs/modules/sensing.md)
def enc_01_multiplexer():
    """ENC-01. U701 TCA9548A TSSOP-24; channel k on SDk/SCk = pins 4/5, 6/7, 8/9, 10/11, 13/14."""
    d = {}
    setp(d, "U701", {24: "+3V3", 12: "GND", 1: "GND", 2: "GND", 21: "GND", 23: "I2C_SDA", 22: "I2C_SCL",
                     3: "PERIPH_RST_N"})
    for k, (sd, sc) in enumerate([(4, 5), (6, 7), (8, 9), (10, 11), (13, 14)]):
        setp(d, "U701", {sd: "MUX%d_SDA" % (k + 1), sc: "MUX%d_SCL" % (k + 1)})
    same(d, "U701", range(15, 21), None)
    two(d, "C701", "+3V3", "GND", "100 nF")
    two(d, "R701", "I2C_SDA", "+3V3", "4.7k")
    two(d, "R702", "I2C_SCL", "+3V3", "4.7k")
    return d


def enc_02_sensor_ports():
    """ENC-02. Ja03: 1 V_SNS, 2 GND, 3 SNSn_SDA, 4 SNSn_SCL; Ra04 / Ra05 100 ohm from MUXn_xxx."""
    d = {}
    for n, a in AXES:
        setp(d, "J%d03" % a, {1: "V_SNS", 2: "GND", 3: "SNS%d_SDA" % n, 4: "SNS%d_SCL" % n})
        two(d, "R%d04" % a, "MUX%d_SDA" % n, "SNS%d_SDA" % n, "100")
        two(d, "R%d05" % a, "MUX%d_SCL" % n, "SNS%d_SCL" % n, "100")
    return d


def enc_03_home_inputs():
    """ENC-03. Ja02: 1 V_SNS, 2 GND, 3 HOMEn_IN. Ra02 pull-up, Ra03 series, Ca03, Da02 BAV99 (1 GND, 2 +3V3, 3 HOMEn)."""
    d = {}
    for n, a in AXES:
        setp(d, "J%d02" % a, {1: "V_SNS", 2: "GND", 3: "HOME%d_IN" % n})
        two(d, "R%d02" % a, "HOME%d_IN" % n, "+3V3", "10k")
        two(d, "R%d03" % a, "HOME%d_IN" % n, "HOME%d" % n, "10k")
        two(d, "C%d03" % a, "HOME%d" % n, "GND", "10 nF")
        setp(d, "D%d02" % a, {1: "GND", 2: "+3V3", 3: "HOME%d" % n})
    return d


def enc_05_pullups():
    """ENC-05. Ra06/Ra07 4.7k to PUn_A (JPa04 to V_SNS); Ra08/Ra09 2.2k to PUn_B (JPa05 to V_SNS).
    Ra06 and Ra08 on SDA, Ra07 and Ra09 on SCL (the spec gives no assignment: assumed in listing order)."""
    d = {}
    for n, a in AXES:
        two(d, "R%d06" % a, "SNS%d_SDA" % n, "PU%d_A" % n, "4.7k")
        two(d, "R%d07" % a, "SNS%d_SCL" % n, "PU%d_A" % n, "4.7k")
        two(d, "R%d08" % a, "SNS%d_SDA" % n, "PU%d_B" % n, "2.2k")
        two(d, "R%d09" % a, "SNS%d_SCL" % n, "PU%d_B" % n, "2.2k")
        two(d, "JP%d04" % a, "PU%d_A" % n, "V_SNS")
        two(d, "JP%d05" % a, "PU%d_B" % n, "V_SNS")
    return d


def enc_07_esd():
    """ENC-07. One SRV05-4 (SOT-23-6) per port: SDA on pin 1, SCL on pin 3, pins 4 and 6 open, 2 GND, 5 V_SNS.
    Ua01 for sensor port n, U702 for the spare port."""
    d = {}
    for n, a in AXES:
        setp(d, "U%d01" % a, {1: "SNS%d_SDA" % n, 2: "GND", 3: "SNS%d_SCL" % n, 4: None, 5: "V_SNS", 6: None})
    setp(d, "U702", {1: "AUX_SDA", 2: "GND", 3: "AUX_SCL", 4: None, 5: "V_SNS", 6: None})
    return d


def enc_08_spare_channel():
    """ENC-08. J701: 1 V_SNS, 2 GND, 3 AUX_SDA, 4 AUX_SCL; R703/R704 100 ohm; R705/R706 4.7k to PU5_A (JP701);
    R707/R708 2.2k to PU5_B (JP702). SDA before SCL in listing order (assumed)."""
    d = {}
    setp(d, "J701", {1: "V_SNS", 2: "GND", 3: "AUX_SDA", 4: "AUX_SCL"})
    two(d, "R703", "MUX5_SDA", "AUX_SDA", "100")
    two(d, "R704", "MUX5_SCL", "AUX_SCL", "100")
    two(d, "R705", "AUX_SDA", "PU5_A", "4.7k")
    two(d, "R706", "AUX_SCL", "PU5_A", "4.7k")
    two(d, "R707", "AUX_SDA", "PU5_B", "2.2k")
    two(d, "R708", "AUX_SCL", "PU5_B", "2.2k")
    two(d, "JP701", "PU5_A", "V_SNS")
    two(d, "JP702", "PU5_B", "V_SNS")
    return d


# ================================================================ CONTROL (specs/modules/control.md)
def ctl_01_mcu_socket():
    """CTL-01. A201 pad 21 +5V; 22, 23, 43, 44 GND; 3 EN; 1 and 2 MCU_3V3. C201 / C202 across +5V and GND."""
    d = {}
    setp(d, "A201", {21: "+5V", 22: "GND", 23: "GND", 43: "GND", 44: "GND", 3: "EN", 1: "MCU_3V3", 2: "MCU_3V3"})
    two(d, "C201", "+5V", "GND", "22 µF")
    two(d, "C202", "+5V", "GND", "100 nF")
    NET_ONLY["ctl_01_mcu_socket"] = [("MCU_3V3", {"A201", "TP816"})]
    return d


def ctl_03_ethernet():
    """CTL-03. A202: 1, 2, 7 GND; 8, 9 +3V3; 3 SPI_MOSI; 4 SPI_SCK; 12 SPI_MISO; 5 ETH_CS_N; 6 ETH_INT_N;
    11 PERIPH_RST_N; 10 not connected. C203 / C204 across +3V3 and GND."""
    d = {}
    setp(d, "A202", {1: "GND", 2: "GND", 7: "GND", 8: "+3V3", 9: "+3V3", 3: "SPI_MOSI", 4: "SPI_SCK", 12: "SPI_MISO",
                     5: "ETH_CS_N", 6: "ETH_INT_N", 11: "PERIPH_RST_N", 10: None})
    two(d, "C203", "+3V3", "GND", "22 µF")
    two(d, "C204", "+3V3", "GND", "100 nF")
    return d


def ctl_05_spi_bus():
    """CTL-05. R201 SPI_SCK_MCU-SPI_SCK, R202 SPI_MOSI_MCU-SPI_MOSI, 33 ohm (listing order assumed)."""
    d = {}
    two(d, "R201", "SPI_SCK_MCU", "SPI_SCK", "33")
    two(d, "R202", "SPI_MOSI_MCU", "SPI_MOSI", "33")
    return d


def ctl_06_peripheral_reset():
    """CTL-06. R204 PERIPH_RST_N-+3V3; D201 cathode EN, anode PERIPH_RST_N."""
    d = {}
    two(d, "R204", "PERIPH_RST_N", "+3V3", "10k")
    ordered(d, "D201", "EN", "PERIPH_RST_N")
    NET_ONLY["ctl_06_peripheral_reset"] = [("PERIPH_RST_N", {"R204", "D201", "U701", "A202", "TP815"})]
    return d


def ctl_08_pin_table():
    """CTL-08. Every usable A201 GPIO pad carries the net pins.h gives it (SPI_SCK, SPI_MOSI as *_MCU), or none;
    plus what CTL-08 demands of pins.h itself."""
    pins = parse_pins_h()
    inv = {g: n for n, g in pins.items()}
    d = {}
    for g, pad in sorted(GPIO_PAD.items(), key=lambda kv: kv[1]):
        if g in FORBIDDEN:
            continue                                  # CTL-09
        n = inv.get(g)
        d[("A201", str(pad))] = MCU_RENAME.get(n, n) if n else None
    d.update(pins_h_problems(pins))
    return d


def ctl_09_unused_pins():
    """CTL-09. Pads 25, 32..35, 36, 41, 42 not connected."""
    return {("A201", str(p)): None for p in UNUSED_PADS}


# ================================================================ I/O (specs/modules/io.md)
def aux_03_fan():
    """AUX-03. J801 1 FAN_V, 2 FAN_N; Q801 1 gate FAN_G, 2 source GND, 3 drain FAN_N; R801 FAN_PWM-FAN_G;
    R802 FAN_G-GND; D801 cathode FAN_V, anode FAN_N; JP801 1 +5V, 2 FAN_V, 3 VM."""
    d = {}
    setp(d, "J801", {1: "FAN_V", 2: "FAN_N"})
    setp(d, "Q801", {1: "FAN_G", 2: "GND", 3: "FAN_N"})
    two(d, "R801", "FAN_PWM", "FAN_G", "100")
    two(d, "R802", "FAN_G", "GND", "100k")
    ordered(d, "D801", "FAN_V", "FAN_N")
    setp(d, "JP801", {1: "+5V", 2: "FAN_V", 3: "VM"})
    NET_ONLY["aux_03_fan"] = [("FAN_G", {"Q801", "R801", "R802"}), ("FAN_N", {"Q801", "D801", "J801"}),
                              ("FAN_V", {"J801", "D801", "JP801"})]
    return d


def aux_04_temperature():
    """AUX-04. RT801 NTC_SENSE-GND, R803 NTC_SENSE-+3V3, C801 NTC_SENSE-GND."""
    d = {}
    two(d, "RT801", "NTC_SENSE", "GND")
    two(d, "R803", "NTC_SENSE", "+3V3", "10k")
    two(d, "C801", "NTC_SENSE", "GND", "100 nF")
    return d


def aux_05_test_points():
    """AUX-05. TP801..TP816, pad 1, nets as in the table (column-wise)."""
    nets = ["VIN", "VM", "+5V", "+3V3", "V_SNS", "GND", "GND", "SPI_SCK",
            "SPI_MOSI", "SPI_MISO", "I2C_SDA", "I2C_SCL", "DRV_ENN", "DIAG_OR", "PERIPH_RST_N", "MCU_3V3"]
    return {("TP%d" % (801 + i), "1"): net for i, net in enumerate(nets)}


FUNCS = sorted((n, f) for n, f in list(globals().items())
               if re.match(r"^(pow|drv|enc|ctl|aux)_\d\d[a-z]?_", n) and callable(f))


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


def parse_val(v):
    """(number, prefix) of a value like '4.7 kΩ', '220 µF 35 V', '100R', '4k7'; the rating is ignored."""
    s = v.lower().replace("µ", "u").replace("μ", "u").replace("ω", "").replace("ohm", "").replace(" ", "")
    m = re.match(r"^(\d+)([kmunp])(\d+)", s)
    if m:
        return float("%s.%s" % (m.group(1), m.group(3))), m.group(2)
    m = re.match(r"^(\d+(?:\.\d+)?)([kmunpg]?)", s)
    return (float(m.group(1)), m.group(2)) if m else None


def value_ok(want, got):
    return parse_val(want) is not None and parse_val(want) == parse_val(got)


def exp_refs(exp):
    return {r for r, _ in exp}


def show(want):
    return "(unconnected)" if want is None else (" , ".join(want) + " (either order)") if isinstance(want, tuple) else want


def list_all():
    n_pads = 0
    for name, fn in FUNCS:
        exp = fn()
        for (r, pin), want in sorted(exp.items(), key=lambda kv: (kv[0][0], [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", kv[0][1])])):
            print("%s %s.%s -> %s" % (name, r, pin, show(want) if not pin.startswith("pins.h:") else "PROBLEM: " + want))
            n_pads += len(pin.split(",")) if not pin.startswith("pins.h:") else 0
        for net, allowed in NET_ONLY.get(name, []):
            print("%s net %s -> only %s" % (name, net, ", ".join(sorted(allowed))))
    print("%d functions, %d pads expected" % (len(FUNCS), n_pads))
    return 0


def main():
    if "--list" in sys.argv:
        return list_all()
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
            if pin.startswith("pins.h:"):          # a problem in pins.h: fails whether or not the schematic exists
                checked += 1
                bad.append("%s %s.%s: expected %s, is not so" % (fid, r, pin, want))
                continue
            checked += len(pins)
            if r not in comps:
                gone[r] = gone.get(r, 0) + len(pins)
                continue
            if "," in pin:
                got = tuple(net_of(r, p) for p in pins)
                ok = sorted(map(str, got)) == sorted(want)
                if not ok and r.startswith("JP") and got[0] == got[1] and got[0] in want:   # closed jumper, merged nets
                    ok = True
                if not ok:
                    bad.append("%s %s.%s: expected %s in either order, is %s" % (fid, r, pin, want, got))
            elif want is None:
                if not unconnected(r, pin):
                    bad.append("%s %s.%s: expected unconnected, is %s" % (fid, r, pin, net_of(r, pin)))
            elif net_of(r, pin) != want:
                ok = False
                if r in BRIDGE12 and pin in ("1", "2"):    # pads 1 and 2 closed as delivered, nets merged
                    other = exp.get((r, "2" if pin == "1" else "1"))
                    ok = net_of(r, "1") == net_of(r, "2") and net_of(r, pin) in (want, other)
                if not ok:
                    bad.append("%s %s.%s: expected %s, is %s" % (fid, r, pin, want, net_of(r, pin) or "(no net)"))
        for r, k in sorted(gone.items()):
            missing.add(r)
            bad.append("%s %s: missing from the netlist (%d pads)" % (fid, r, k))
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


if __name__ == "__main__":
    sys.exit(main())
