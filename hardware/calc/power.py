#!/usr/bin/env python3
"""Power calculations for Rev B (POW-02, -04, -06, -09, DRV-09, ENC-03, AUX-04, BRD-06). Nothing here is measured.

Run: python3 hardware/calc/power.py     Every input is named with its source; asserts hold the specs' numbers.
"""
import math

print("== 1. Input range, the TVS and the drivers' limits (POW-01, POW-04, DRV-09)")
VIN_MIN, VIN_MAX = 11.0, 17.0    # V: a 12 V supply down to 11 V, a full V-mount battery at 16.8 V (PRD POW-01)
TVS_STANDOFF, TVS_VBR_MIN, TVS_VBR_MAX, TVS_VCLAMP, TVS_IPP = 18.0, 20.0, 22.1, 29.2, 20.55   # SMBJ18A, Hongjiacheng Rev 1.1
TMC2240_OP, TMC2240_ABS = 36.0, 41.0     # datasheet Rev 2, p9
TMC2209_OP, TMC2209_ABS = 29.0, 32.0     # datasheet Rev 1.09, p75
assert VIN_MAX < TVS_STANDOFF < TVS_VBR_MIN
print(f"highest supply {VIN_MAX} V < TVS stand-off {TVS_STANDOFF} V < lowest breakdown {TVS_VBR_MIN} V: the TVS does not conduct in normal use")
print(f"TVS clamp at its full rated pulse: {TVS_VCLAMP} V at {TVS_IPP} A (10/1000 us)")
print(f"  TMC2240: {TMC2240_ABS - TVS_VCLAMP:.1f} V below the absolute maximum of {TMC2240_ABS} V, and below its {TMC2240_OP} V operating limit")
print(f"  TMC2209: {TMC2209_ABS - TVS_VCLAMP:.1f} V below the absolute maximum of {TMC2209_ABS} V; {TVS_VCLAMP - TMC2209_OP:.1f} V above its "
      f"{TMC2209_OP} V operating limit, at a pulse current this board's sources do not reach (sections 2 and 3)")
assert TVS_VCLAMP < TMC2209_ABS < TMC2240_ABS

print("\n== 2. Hot-plug (POW-02b)")
C_BULK = 4 * 100e-6              # F, C101..C104, one 100 uF 35 V electrolytic per driver
R_PATH = 0.020 + 0.020 + 0.030   # ohm: Q101 on (20 mOhm at -4.5 V), F101 cold (estimate for a T 5 A fuse), connector and copper (estimate)
worst = 0.0
for esr_each, kind in ((0.50, "general-purpose capacitors, about 0.5 ohm each (assumption)"), (0.10, "low-ESR capacitors, 0.1 ohm each (assumption)")):
    esr = esr_each / 4
    for L in (2e-6, 10e-6):      # H: about 1 m and 5 m of two-wire supply lead: assumptions
        z0 = math.sqrt(L / C_BULK)
        zeta = (esr + R_PATH) / (2 * z0)
        over = math.exp(-math.pi * zeta / math.sqrt(1 - zeta * zeta)) if zeta < 1 else 0.0
        peak = VIN_MAX * (1 + over)
        worst = max(worst, peak)
        print(f"{kind}; lead {L * 1e6:.0f} uH: Z0 {z0 * 1000:.0f} mOhm, damping {zeta:.2f}, overshoot {over * 100:.0f} % -> peak {peak:.1f} V"
              + (" (the TVS starts to conduct)" if peak > TVS_VBR_MIN else ""))
print(f"worst case here {worst:.1f} V: below the TVS clamp of {TVS_VCLAMP} V and both drivers' absolute maxima; with general-purpose capacitors below {TVS_VBR_MIN} V")
assert worst < TVS_VCLAMP
print("The modules' own ceramic capacitors would ring to twice the supply alone; the electrolytics' resistance is what damps it,")
print("so C101..C104 should be ordinary 100 uF 35 V parts, not low-ESR types.")
energy = 0.5 * C_BULK * VIN_MAX ** 2
i2t = energy / (0.5 / 4 + R_PATH)
F101_I2T = 230.0                 # A2s, melting, Schurter MST 250 time-lag 5 A at 10 x In (maker's sheet)
print(f"inrush: {energy * 1000:.0f} mJ into the bulk capacitors gives at most {i2t:.2f} A2s; F101 melts at about {F101_I2T:.0f} A2s")
assert i2t * 50 < F101_I2T

print("\n== 3. Energy coming back from the motors (POW-04)")
J_LOAD = 2.5 * 0.10 ** 2         # kg m2: 2.5 kg payload (TGT-01) at 0.10 m radius, a generous estimate
W_MAX = math.radians(60)         # rad/s at the output (TGT-03)
e_kin = 0.5 * J_LOAD * W_MAX ** 2
dv = math.sqrt(VIN_MAX ** 2 + 2 * e_kin / C_BULK) - VIN_MAX
print(f"all of the head's kinetic energy at 60 deg/s is {e_kin * 1000:.0f} mJ; in {C_BULK * 1e6:.0f} uF it lifts {VIN_MAX} V by {dv:.2f} V, to {VIN_MAX + dv:.1f} V")
KE = 0.42 / (1.5 * math.sqrt(2))  # V s/rad per phase, from 42 Ncm holding torque at 1.5 A RMS (17HE15-1504S): Kt = T / (sqrt(2) I)
w_hand = 2 * math.pi * 1.0 * 7.5  # rad/s at the motor when the head is spun by hand at 1 turn/s through 7.5:1
print(f"a head spun by hand at 1 turn/s: back-EMF peak {KE * w_hand:.1f} V per phase, below the supply, so it cannot pump the rail above it")
assert VIN_MAX + dv < TVS_VBR_MIN and KE * w_hand < TMC2209_OP

print("\n== 4. Reverse polarity and the FET (POW-02a)")
for v in (VIN_MIN, VIN_MAX, TVS_VCLAMP):
    print(f"gate drive at {v:.1f} V in: {0.6 * v:.1f} V (R101 150k over R102 100k)")
assert 0.6 * VIN_MIN >= 4.5 and 0.6 * TVS_VCLAMP < 20.0      # AOD4185: 20 mOhm at -4.5 V, +-20 V absolute (Rev 4.2)
print("reversed: gate and source sit together, the FET is off and its body diode blocks; it sees the supply as Vds, 17 V of 40 V")
I_FUSE = 5.0
print(f"loss at {I_FUSE} A: {I_FUSE ** 2 * 0.020:.2f} W in a TO-252 on its copper")
p_fault = 50.0 ** 2 * 0.023      # W at 10 x In, hot (23 mOhm at 125 C)
t_fault = F101_I2T / 50.0 ** 2
print(f"a dead short behind the fuse: {p_fault:.0f} W in Q101 for {t_fault * 1000:.0f} ms until F101 melts; junction-to-case is 2.4 K/W, so under {p_fault * 2.4:.0f} K above the case")
assert p_fault * 2.4 < 150
p_sot = (50.0 / 3) ** 2 * 0.060  # three AO3401A in parallel, the fee-free alternative: 60 mOhm each at -4.5 V
print(f"three SOT-23 FETs instead would each take {p_sot:.0f} W for those {t_fault * 1000:.0f} ms; at a third of their 125 K/W (assumption for 0.1 s) that is {p_sot * 125 / 3:.0f} K: they do not survive, hence the Extended part")

print("\n== 5. The 5 V and 3.3 V rails (POW-07, POW-08, POW-09)")
MCU = 0.355 + 0.020              # A: module peak, 802.11b transmit (module datasheet v1.8, table 6-4), plus the board's bridge and LED (estimate)
LOADS_3V3 = {"Ethernet module, 100M transmit (WIZ850io datasheet p7)": 0.132, "four drivers' VIO (estimate 5 mA each)": 0.020,
             "multiplexer, pull-ups, home inputs closed, thermistor": 0.005, "U102's own ground current (AMS1117 sheet, max)": 0.011}
LOADS_SNS = {"four MT6701 at 10 mA (datasheet Rev 0.1)": 0.040, "a display on the spare port (estimate)": 0.020,
             "I2C pull-ups, five ports at 1.5 k, both lines low": 0.022, "four hall sensors on the home plugs (estimate)": 0.020,
             "U103's own ground current": 0.011}
i33, isns, fan = sum(LOADS_3V3.values()), sum(LOADS_SNS.values()), 0.20
for name, loads, total in (("+3V3", LOADS_3V3, i33), ("+3V3_SNS", LOADS_SNS, isns)):
    for k, v in loads.items():
        print(f"  {v * 1000:4.0f} mA  {k}")
    print(f"{name}: {total:.2f} A")
i5 = MCU + i33 + isns + fan
print(f"+5V peak: MCU module {MCU:.2f} A + {i33:.2f} A + {isns:.2f} A + a 5 V fan {fan:.2f} A = {i5:.2f} A of the 1 A module")
assert i33 <= 0.25 and isns <= 0.12 and i5 <= 0.9
V_D102 = 0.45                    # V at about 1 A: SS34, 0.55 V max at 3 A (MDD Rev 2024A5); a reading of its curve
v5 = 5.0 - V_D102
print(f"+5V = 5.0 V - {V_D102} V in D102 = {v5:.2f} V; the 3.3 V regulators need 1.1 V typical, 1.3 V at most at 0.8 A, and have {v5 - 3.3:.2f} V")
assert v5 - 3.3 >= 1.2
print(f"U102 dissipates {(v5 - 3.3) * i33:.2f} W, U103 {(v5 - 3.3) * isns:.2f} W; shorted, each limits at 0.9 to 1.5 A and shuts down when hot")
print(f"on USB alone: VBUS 5.0 V less about 0.35 V in the module's diode gives {5.0 - 0.35:.2f} V on +5V; at 4.75 V on the plug it is {4.75 - 0.35:.2f} V and +3V3 may sag to about {4.75 - 0.35 - 1.2:.1f} V")
R_MOTOR, I_MOTOR = 2.3, 1.5      # ohm per phase and A RMS, 17HE15-1504S
p_axis = 2 * I_MOTOR ** 2 * R_MOTOR + 1.7 + 0.22 * 7.85     # copper, driver loss (TMC2240: 2 x I2 x 0.23 + overhead), shaft power at 0.22 Nm and 75 rpm
for vin in (VIN_MIN, 12.0, VIN_MAX):
    i_in = 4 * p_axis / vin + i5 * 5.0 / (0.88 * vin)
    print(f"input at {vin:.0f} V with all four axes at {I_MOTOR} A RMS: {i_in:.1f} A, of which {4 * p_axis / vin:.1f} A through F101 (T 5 A); J101 is rated 10 A")
    assert 4 * p_axis / vin <= I_FUSE + 0.05
print("At 11 V with all four axes at full current F101 runs at its rating: the zoom and focus motors are smaller, and firmware sets the currents.")

print("\n== 6. Copper (BRD-06), IPC-2221 for outer layers: I = 0.048 x dT^0.44 x A^0.725, A in mil2, 1 oz = 1.378 mil")
for name, width, amps in (("VIN_RAW, VIN, VM", 3.0, 5.0), ("VM at the narrowest branch to a socket", 2.0, 2.0), ("motor outputs", 1.0, 2.0),
                          ("+5V, +3V3 and the other logic supplies", 0.5, 0.85)):
    area = width / 0.0254 * 1.378
    rise = (amps / (0.048 * area ** 0.725)) ** (1 / 0.44)
    print(f"{name}: {width} mm carries {amps} A with {rise:.0f} K rise")
    assert rise <= 20

print("\n== 7. Small things")
i_home = (VIN_MAX - 3.3 - 0.6) / 10e3
print(f"{VIN_MAX} V on a home input (ENC-03): {i_home * 1e3:.2f} mA through the 10k series resistor into the clamp, "
      f"{(VIN_MAX - 3.3) ** 2 / 10e3 * 1e3:.0f} mW in the 10k pull-up (0603 is 100 mW)")
assert i_home < 2e-3
print(f"VM_SENSE (POW-06): {VIN_MIN / 11:.2f} V at {VIN_MIN} V, {VIN_MAX / 11:.2f} V at {VIN_MAX} V, {TVS_VCLAMP / 11:.2f} V at the TVS clamp, behind 100k")
B, R25 = 3950.0, 10e3            # KNTC0603/10KF3950: B(25/50)


def ntc(t):
    r = R25 * math.exp(B * (1 / (t + 273.15) - 1 / 298.15))
    return 3.3 * r / (r + 10e3)


print("NTC_SENSE (AUX-04): " + ", ".join(f"{ntc(t):.2f} V at {t} C" for t in (0, 25, 50, 70, 85)))
assert abs(ntc(25) - 1.65) < 0.01 and abs(ntc(70) - 0.49) < 0.01
print("DIAG_OR (DRV-05): a driver's DIAG at 3.3 V less about 0.3 V in its diode gives 3.0 V on a 10k pull-down: above the MCU's 2.5 V input-high level")
print("PERIPH_RST_N (CTL-06): with EN low, D201 holds it at about 0.3 V with 1 mA from the pull-ups (10k on the board, 4.7k on the Ethernet module):")
print("  below the W5500's 0.8 V and the multiplexer's 0.99 V input-low levels")
