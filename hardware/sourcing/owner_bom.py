#!/usr/bin/env python3
"""The owner's shopping list: every part JLC does not assemble, with its mating parts (BRD-08).

  python3 hardware/sourcing/owner_bom.py [boards]      default: parts for one board

The list starts from the schematic: every part without an LCSC field is the owner's to buy (jumpers, test points
and mounting holes aside), so a part added to the schematic stops this script until BUY below says what to buy for
it. BUY maps a part's value and footprint to the things to order per part: the part itself, the plug that mates
with it, crimp contacts, a socket.

The shops are inside the EU. An order from LCSC pays, since July 2026, EUR 3 of duty per kind of product and a
handling fee on top: about EUR 22 on a parcel worth USD 22 (the owner's cart, 2026-11-11), so the loose parts come
from Reichelt and ride with the modules from TinyTronics. Reichelt's prices are a table here, read on its Dutch
pages on READ; its pages refuse a script, so there is no stock check: look at the cart.

Writes owner_bom.md (the whole list) and owner_bom_reichelt.csv (article number and quantity per line).
"""
import csv
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import netlist  # noqa: E402

READ = "2026-11-11"         # the day the shop pages below were read
REICHELT = "https://www.reichelt.com/nl/nl/a-p{}.html"      # the number finds the page, whatever stands before it
SHIPPING = 6.95             # DPD to the Netherlands up to 10 kg, reichelt.com/shippingcosts
TT = "https://www.tinytronics.nl/en/"
# Reichelt's article -> (page number, maker and part number, euro each with 21 % VAT)
R = {
    "JST B2P-VH-B": (190557, "JST B2P-VH-B", 0.25),
    "JST VH2P BU": (185107, "JST VHR-2N", 0.10),
    "JST VH CKS": (185113, "JST SVH-21T-P1.1", 0.10),
    "JST XH4P ST": (185075, "JST B4B-XH-A", 0.20),
    "JST XH4P BU": (185087, "JST XHP-4", 0.07),
    "JST XH1 CKS": (405981, "JST SXH-001T-P0.6", 0.04),
    "JST PH3P ST": (185050, "JST B3B-PH-K-S", 0.20),
    "JST PH3P BU": (185042, "JST PHR-3", 0.05),
    "JST PH4P ST": (185051, "JST B4B-PH-K-S", 0.17),
    "JST PH4P BU": (185043, "JST PHR-4", 0.05),
    "JST PH CKS": (185072, "JST SPH-002T-P0.5S", 0.05),
    "RAD 105 100/35": (42401, "Frei, no part number", 0.07),
    "LITT 37215000411": (242285, "Littelfuse 37215000411", 1.12),
    "LITT 37211000411": (242278, "Littelfuse 37211000411", 1.63),
    "LITT 56000001009": (229165, "Littelfuse 56000001009", 0.87),
    "ECON SL40G1E": (404310, "Econ Connect SL40G1E", 0.68),
    "TSR 1-2450": (116850, "Traco TSR 1-2450", 6.97),
}
# Pieces on top of what the schematic asks: a crimp can fail, a housing can break
SPARE = {"JST VH CKS": 4, "JST XH1 CKS": 9, "JST PH CKS": 12, "JST VH2P BU": 1, "RAD 105 100/35": 1}
FEMALE = (TT + "cables-and-connectors/connectors/pin-headers/female/40-pins-header-female",
          "Female header 1×40, 8.5 mm, to cut into the sockets (a cut costs one position): two strips give the MCU "
          "module's two 1×22 and four 1×8, two more the drivers' other 1×8 and 1×2. €0.46 to €0.60 in search results")
# (value, footprint name) -> [(Reichelt article or shop link, what it is, how many per part)]
BUY = {
    ("B4B-XH-A", "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical"): [
        ("JST XH4P ST", "Motor connector on the board", 1), ("JST XH4P BU", "Its plug housing", 1),
        ("JST XH1 CKS", "Crimp contact for XH, 22 to 28 AWG", 4)],
    ("B2P-VH", "JST_VH_B2P-VH_1x02_P3.96mm_Vertical"): [
        ("JST B2P-VH-B", "Supply connector on the board: the B2P-VH in PBT, same pins and holes", 1),
        ("JST VH2P BU", "Its plug housing", 1), ("JST VH CKS", "Crimp contact for VH, 18 to 22 AWG", 2)],
    ("B4B-PH-K", "JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical"): [
        ("JST PH4P ST", "Sensor connector on the board", 1), ("JST PH4P BU", "Its plug housing", 1),
        ("JST PH CKS", "Crimp contact for PH, 24 to 30 AWG", 4)],
    ("B3B-PH-K", "JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical"): [
        ("JST PH3P ST", "Home connector on the board", 1), ("JST PH3P BU", "Its plug housing", 1),
        ("JST PH CKS", "Crimp contact for PH, 24 to 30 AWG", 3)],
    ("100 µF 35 V", "CP_Radial_D6.3mm_P2.50mm"): [("RAD 105 100/35", "Bulk capacitor 100 µF 35 V, 6.3 × 11 mm, 105 °C", 1)],
    ("T 5 A", "Fuseholder_TR5_Littelfuse_No560_No460"): [
        ("LITT 37215000411", "Motor fuse T 5 A, TR5, and a spare", 2), ("LITT 56000001009", "Fuse holder TR5", 1)],
    ("T 1 A", "Fuseholder_TR5_Littelfuse_No560_No460"): [
        ("LITT 37211000411", "Logic fuse T 1 A, TR5, and a spare", 2), ("LITT 56000001009", "Fuse holder TR5", 1)],
    ("1x4 header", "PinHeader_1x04_P2.54mm_Vertical"): [("ECON SL40G1E", "Pin header 1×40, to cut: spare I2C port and fan", 0.5)],
    ("1x2 header", "PinHeader_1x02_P2.54mm_Vertical"): [("ECON SL40G1E", "Pin header 1×40, to cut: spare I2C port and fan", 0.5)],
    ("ESP32-S3-DevKitC-1U", "ESP32-S3-DevKitC-1"): [
        (TT + "development-boards/microcontroller-boards/with-wi-fi/espressif-esp32-s3-devkitc-1u-n8r8-8mb-flash-8mb-psram",
         "ESP32-S3-DevKitC-1U-N8R8, €20.00 at TinyTronics", 1),
        FEMALE + (2,),
        (None, "U.FL to SMA bulkhead lead and a 2.4 GHz antenna: no shop page was read", 1)],
    ("StepStick", "StepStick_Socket"): [
        (TT + "mechanics-and-actuators/motor-controllers-and-drivers/stepper-motor-controllers-and-drivers/bigtreetech-tmc2240-motor-driver-module-v1.0",
         "BIGTREETECH TMC2240 V1.0 driver module with heat sink, €9.75 at TinyTronics", 1),
        FEMALE + (0.5,)],
    ("WIZ850io", "WIZ850io"): [
        (TT + "communication-and-signals/ethernet/modules/w5500-ethernet-module-wiz850io-compatible",
         "W5500 module, WIZ850io compatible, €9.00 at TinyTronics (a clone: check its pin order)", 1)],
    ("5 V 1 A SIP-3", "SIP3_DCDC_7805"): [("TSR 1-2450", "5 V regulator, 6.5 to 36 V in", 1)],
}
NOT_ON_THE_BOARD = [
    (TT + "sensors/magnetic-field/as5600-magnetic-angle-sensor-encoder-module", "AS5600 sensor board, €3.00 at TinyTronics, one per axis", 4),
]


def main():
    boards = int(next((a for a in sys.argv[1:] if a.isdigit()), 1))
    comps = netlist.components(netlist.export(os.path.join(HERE, "..", "ptz-driver.kicad_sch")))
    need, other, used = {}, [], set()
    for ref, c in sorted(comps.items()):
        if c["fields"].get("LCSC") or ref.startswith(("JP", "TP", "H")):
            continue
        key = (c["value"], c["footprint"].split(":")[1])
        assert key in BUY, f"{ref} {key}: the owner solders it, and BUY does not say what to buy for it"
        used.add(key)
        for what, text, n in BUY[key]:
            if what in R:
                e = need.setdefault(what, [text, 0.0, []])
                e[1] += n * boards
                e[2].append(ref)
            else:
                e = next((o for o in other if o[1] == text), None)
                if e:
                    e[2] += n * boards
                else:
                    other.append([what, text, n * boards])
    assert used == set(BUY), f"BUY has entries no part uses: {set(BUY) - used}"
    assert set(SPARE) <= set(need), f"SPARE names lines nothing asks for: {set(SPARE) - set(need)}"
    other += [[w, t, n * boards] for w, t, n in NOT_ON_THE_BOARD]

    rows, total = [], 0.0
    for article, (text, n, refs) in need.items():
        page, part, price = R[article]
        qty = math.ceil(n) + SPARE.get(article, 0)
        total += qty * price
        rows.append((article, page, part, text, math.ceil(n), qty, price, refs))

    with open(os.path.join(HERE, "owner_bom_reichelt.csv"), "w", newline="") as f:
        w = csv.writer(f, delimiter=";")
        for article, page, part, text, n, qty, price, refs in rows:
            w.writerow([article, qty])
    out = [f"# What the owner buys for Rev B, for {boards} board{'s' if boards > 1 else ''}", "",
           "Made by `owner_bom.py` from the schematic: every part JLC does not assemble, with its plug, contacts or socket.",
           f"Two orders, both inside the EU: the loose parts at Reichelt, the modules at TinyTronics. Prices were read on {READ}",
           "and include 21 % VAT. LCSC is cheaper per part, but its parcel pays import duty per kind of product: see",
           "`DECISIONS.md`.", "",
           "## At Reichelt", "",
           "| Article | Part | What | Needed | Order | € each | € line | For |",
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for article, page, part, text, n, qty, price, refs in rows:
        out.append(f"| [{article}]({REICHELT.format(page)}) | {part} | {text} | {n} | {qty} | {price:.2f} | {qty * price:.2f} | "
                   f"{', '.join(sorted(set(refs)))} |")
    out += ["", f"{len(rows)} lines, €{total:.2f}; with €{SHIPPING:.2f} for DPD to the Netherlands €{total + SHIPPING:.2f}. *Order* is *Needed* plus spares",
            "for what can fail: crimp contacts, a plug housing, a capacitor. `owner_bom_reichelt.csv` holds article and quantity",
            "per line; whether Reichelt's cart takes it as an upload was not tried. Stock is not checked here: Reichelt's",
            f"pages refuse a script. On {READ} every line was in stock; the pin header had limited stock.", "",
            "The crimp contacts need a crimping tool for JST XH, PH and VH contacts.", "",
            "The fuses are Littelfuse 372 parts. Reichelt's pages give 250 V AC and no DC rating, and no lead length: the",
            "holder takes 4.3 mm, so cut longer leads. The DC-rated fuse `ASSEMBLY.md` names (Schurter MST 250) was not",
            "found at Reichelt in 5 A and 1 A.", "",
            "## At TinyTronics and elsewhere", "", "| What | Count | Where |", "| --- | --- | --- |"]
    for what, text, n in other:
        out.append(f"| {text} | {math.ceil(n)} | {'[shop page](' + what + ')' if what else 'to find'} |")
    open(os.path.join(HERE, "owner_bom.md"), "w").write("\n".join(out) + "\n")
    print(f"owner_bom.md, owner_bom_reichelt.csv: {len(rows)} Reichelt lines, EUR {total:.2f} + {SHIPPING:.2f} shipping; {len(other)} lines elsewhere")


if __name__ == "__main__":
    main()
