#!/usr/bin/env python3
"""The owner's shopping list: every part JLC does not assemble, with its mating parts (BRD-08).

  python3 hardware/sourcing/owner_bom.py [boards]      default: parts for one board
  python3 hardware/sourcing/owner_bom.py --refresh     read stock and prices at LCSC again

The list starts from the schematic: every part without an LCSC field is the owner's to buy (jumpers, test points
and mounting holes aside), so a part added to the schematic stops this script until BUY below says what to buy for
it. BUY maps a part's value and footprint to the things to order per part: the part itself, the plug that mates
with it, crimp contacts, a socket. Stock, minimum quantity and price come from LCSC's product endpoint, the one
its own product pages use; a quantity is rounded up to what LCSC sells.

Writes owner_bom_lcsc.csv (to upload in LCSC's BOM tool) and owner_bom.md (the whole list, other shops included).
"""
import csv
import json
import math
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import netlist  # noqa: E402

READ = "2026-11-11"         # the day the shop pages below were read; --refresh updates LCSC only
TT = "https://www.tinytronics.nl/en/"
# (value, footprint name) -> [(LCSC number or shop link, what it is, how many per part)]
BUY = {
    ("B4B-XH-A", "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical"): [
        ("C144395", "Motor connector on the board, JST B4B-XH-A", 1), ("C493083", "Its plug housing, JST XHP-4 (green)", 1),
        ("C140573", "Crimp contact for XH, 22 to 28 AWG", 4)],
    ("B2P-VH", "JST_VH_B2P-VH_1x02_P3.96mm_Vertical"): [
        ("C160315", "Supply connector on the board, JST B2P-VH", 1), ("C595405", "Its plug housing, JST VHR-2N (black)", 1),
        ("C160349", "Crimp contact for VH, 18 to 22 AWG", 2)],
    ("B4B-PH-K", "JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical"): [
        ("C131334", "Sensor connector on the board, JST B4B-PH-K-S", 1), ("C111514", "Its plug housing, JST PHR-4", 1),
        ("C111515", "Crimp contact for PH, 24 to 30 AWG", 4)],
    ("B3B-PH-K", "JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical"): [
        ("C131339", "Home connector on the board, JST B3B-PH-K-S", 1), ("C265393", "Its plug housing, JST PHR-3", 1),
        ("C111515", "Crimp contact for PH, 24 to 30 AWG", 3)],
    ("100 µF 35 V", "CP_Radial_D6.3mm_P2.50mm"): [("C135785", "Bulk capacitor 100 µF 35 V, 6.3 × 11 mm, general purpose", 1)],
    ("T 5 A", "Fuseholder_TR5_Littelfuse_No560_No460"): [
        ("C3164152", "Motor fuse T 5 A, TR5, Littelfuse 382 (lead length not read: the holder takes 4.3 mm, cut longer ones)", 2),
        ("C142909", "Fuse holder TR5, Littelfuse 560", 1)],
    ("T 1 A", "Fuseholder_TR5_Littelfuse_No560_No460"): [
        ("C142712", "Logic fuse T 1 A, TR5, Littelfuse 382", 2), ("C142909", "Fuse holder TR5, Littelfuse 560", 1)],
    ("1x4 header", "PinHeader_1x04_P2.54mm_Vertical"): [("C42431788", "Pin header 1×40, to cut: spare I2C port and fan", 0.5)],
    ("1x2 header", "PinHeader_1x02_P2.54mm_Vertical"): [("C42431788", "Pin header 1×40, to cut: spare I2C port and fan", 0.5)],
    ("ESP32-S3-DevKitC-1U", "ESP32-S3-DevKitC-1"): [
        (TT + "development-boards/microcontroller-boards/with-wi-fi/espressif-esp32-s3-devkitc-1u-n8r8-8mb-flash-8mb-psram",
         "ESP32-S3-DevKitC-1U-N8R8, €20.00 at TinyTronics", 1),
        ("C41376161", "Socket for the MCU module: female header 1×22, 8.5 mm", 2),
        (None, "U.FL to SMA bulkhead lead and a 2.4 GHz antenna: no shop page was read", 1)],
    ("StepStick", "StepStick_Socket"): [
        (TT + "mechanics-and-actuators/motor-controllers-and-drivers/stepper-motor-controllers-and-drivers/bigtreetech-tmc2240-motor-driver-module-v1.0",
         "BIGTREETECH TMC2240 V1.0 driver module with heat sink, €9.75 at TinyTronics", 1),
        ("C42431840", "Socket for a driver: female header 1×8, 8.5 mm", 2),
        ("C42431841", "Socket for a driver's two extra pins: female header 1×2, 8.5 mm", 1)],
    ("WIZ850io", "WIZ850io"): [
        (TT + "communication-and-signals/ethernet/modules/w5500-ethernet-module-wiz850io-compatible",
         "W5500 module, WIZ850io compatible, €9.00 at TinyTronics (a clone: check its pin order). WIZnet's own is LCSC C134462", 1)],
    ("5 V 1 A SIP-3", "SIP3_DCDC_7805"): [
        ("C2992391", "5 V regulator, YLPTEC's K7805-1000R3 (8 to 36 V in, 680 µF load; sheet V1.00 06/2013), and a spare. "
                     "The certified one is a Traco TSR 1-2450: none at LCSC, €18 shipping at DigiKey", 2)],
}
NOT_ON_THE_BOARD = [
    (TT + "sensors/magnetic-field/as5600-magnetic-angle-sensor-encoder-module", "AS5600 sensor board, €3.00 at TinyTronics, one per axis", 4),
]
CACHE = os.path.join(HERE, "lcsc_parts.json")


def lcsc(code, cache):
    if code not in cache:
        raw = subprocess.run(["curl", "-s", "-m", "30", f"https://wmsc.lcsc.com/ftps/wm/product/detail?productCode={code}"],
                             capture_output=True, text=True).stdout
        r = json.loads(raw)["result"]
        assert r, f"{code} is not at LCSC"
        cache[code] = dict(mpn=r["productModel"], maker=r["brandNameEn"], stock=r["stockNumber"], min=r["minBuyNumber"], step=r["split"],
                           prices=[(p["ladder"], p["usdPrice"]) for p in r["productPriceList"]])
        time.sleep(0.7)
    return cache[code]


def main():
    boards = int(next((a for a in sys.argv[1:] if a.isdigit()), 1))
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) and "--refresh" not in sys.argv else {}
    comps = netlist.components(netlist.export(os.path.join(HERE, "..", "ptz-driver.kicad_sch")))
    need, other, used = {}, [], set()
    for ref, c in sorted(comps.items()):
        if c["fields"].get("LCSC") or ref.startswith(("JP", "TP", "H")):
            continue
        key = (c["value"], c["footprint"].split(":")[1])
        assert key in BUY, f"{ref} {key}: the owner solders it, and BUY does not say what to buy for it"
        used.add(key)
        for what, text, n in BUY[key]:
            if what and what.startswith("C"):
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
    other += [[w, t, n * boards] for w, t, n in NOT_ON_THE_BOARD]

    rows, total = [], 0.0
    for code, (text, n, refs) in need.items():
        p = lcsc(code, cache)
        qty = max(math.ceil(n), p["min"])
        qty = math.ceil(qty / p["step"]) * p["step"]
        price = [pr for ladder, pr in p["prices"] if ladder <= qty][-1]
        assert p["stock"] >= qty, f"{code} {p['mpn']}: LCSC has {p['stock']}, {qty} needed"
        total += qty * price
        rows.append((code, p["mpn"], p["maker"], text, math.ceil(n), qty, price, p["stock"], refs))
    json.dump(cache, open(CACHE, "w"), indent=1, sort_keys=True)

    with open(os.path.join(HERE, "owner_bom_lcsc.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Quantity", "Manufacture Part Number", "Manufacturer", "Description", "LCSC Part Number"])
        for code, mpn, maker, text, n, qty, price, stock, refs in rows:
            w.writerow([qty, mpn, maker, text, code])
    out = [f"# What the owner buys for Rev B, for {boards} board{'s' if boards > 1 else ''}", "",
           "Made by `owner_bom.py` from the schematic: every part JLC does not assemble, with its plug, contacts or socket.",
           f"LCSC's stock and prices were read from its product pages' own data on {READ}; rerun with `--refresh` before",
           "ordering. `owner_bom_lcsc.csv` holds the LCSC lines for LCSC's BOM tool. The other shops' pages were read on",
           "2026-11-11. Shipping, and VAT on the LCSC order, are not in these numbers and were not looked up.", "",
           "## At LCSC", "",
           "| LCSC | Part | Maker | What | Needed | Order | $ each | $ line | In stock | For |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for code, mpn, maker, text, n, qty, price, stock, refs in rows:
        out.append(f"| [{code}](https://www.lcsc.com/product-detail/{code}.html) | {mpn} | {maker} | {text} | {n} | {qty} | {price:.4f} | "
                   f"{qty * price:.2f} | {stock} | {', '.join(sorted(set(refs)))} |")
    out += ["", f"{len(rows)} lines, ${total:.2f} before shipping and tax. *Order* is *Needed* rounded up to LCSC's minimum and pack size.",
            "The crimp contacts need a crimping tool for JST XH, PH and VH contacts.", "",
            "The two fuses are Littelfuse 382 parts, the TR5 fuses LCSC had in stock. Their data sheet states no DC rating;",
            "the DC-rated ones `ASSEMBLY.md` names (Schurter MST 250) were out of stock at LCSC, and a Conquer MST 5 A is at",
            "DigiKey (`docs/research/rev-b-cost.md`). LCSC had 25 of the 5 A fuse: the line most likely to run out.", "",
            "## Elsewhere", "", "| What | Count | Where |", "| --- | --- | --- |"]
    for what, text, n in other:
        out.append(f"| {text} | {math.ceil(n)} | {'[shop page](' + what + ')' if what else 'to find'} |")
    open(os.path.join(HERE, "owner_bom.md"), "w").write("\n".join(out) + "\n")
    print(f"owner_bom.md, owner_bom_lcsc.csv: {len(rows)} LCSC lines, ${total:.2f}; {len(other)} lines elsewhere")


if __name__ == "__main__":
    main()
