#!/usr/bin/env python3
"""Pin number -> pin name of JLC's own library symbol for every polar or multi-pin part in the BOM.

Run from hardware/:  python3 fab/jlc_pins.py     (after fab/make_jlc.py)
JLC places a part by its own footprint, whose pad numbers belong to its own symbol. fab/make_jlc.py fits pad numbers
onto pad numbers; this prints what JLC calls each numbered pin, next to the net the board puts on that pad, so the
pin order of every such part can be read against the specs in one table. Source: the EasyEDA library API.
"""
import csv
import json
import os
import subprocess
import sys
import time

HW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HW, "tools"))
import netlist  # noqa: E402

CACHE = os.path.join(HW, "fab", "easyeda_pins.json")
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}


def pins(lcsc):
    if lcsc not in cache:
        time.sleep(1.5)
        raw = subprocess.run(["curl", "-s", "-m", "30", f"https://easyeda.com/api/products/{lcsc}/components?version=6.4.19.5"],
                             capture_output=True, text=True).stdout
        out = {}
        for s in json.loads(raw)["result"]["dataStr"]["shape"]:
            if s.startswith("P~"):
                seg = s.split("^^")
                out[seg[4].split("~")[4]] = seg[3].split("~")[4]
        cache[lcsc] = out
        json.dump(cache, open(CACHE, "w"), indent=0, sort_keys=True)
    return cache[lcsc]


if __name__ == "__main__":
    nets = netlist.pin_nets(netlist.export(os.path.join(HW, "ptz-driver.kicad_sch")))
    print("| LCSC | Part | First reference | JLC's pin: name -> net on the board |\n| --- | --- | --- | --- |")
    for row in csv.DictReader(open(os.path.join(HW, "fab", "jlc", "ptz-driver_bom.csv"))):
        ref = row["Designator"].split(",")[0]
        if ref[0] in "RC" and not row["Footprint"].startswith("CP_") and ref[:2] != "RT":
            continue                                   # resistors and ceramic capacitors have no pin order
        p = pins(row["LCSC Part #"])
        cells = ", ".join(f"{n}: {name} -> {nets.get((ref, n), 'not connected')}" for n, name in sorted(p.items(), key=lambda x: x[0].zfill(3)))
        print(f"| {row['LCSC Part #']} | {row['Comment']} | {ref} | {cells} |")
