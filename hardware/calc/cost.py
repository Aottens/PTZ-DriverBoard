#!/usr/bin/env python3
"""Cost of one JLC order of five assembled boards (COST-01..03, BRD-12). An estimate, not a quote.

Run: python3 hardware/calc/cost.py [--md]
It prices the BOM that fab/make_jlc.py wrote (fab/jlc/ptz-driver_bom.csv and the placement file for the joint count),
or, before a board exists, the planned list in sourcing/planned_bom.csv. Part prices, library type and stock come
from JLC's parts API through sourcing/jlc_api.py and are kept in sourcing/jlc_parts.json; pass --refresh to read
them again. Tags: [page] read on jlcpcb.com on 2026-11-11, [api] JLC's parts API that day, [schatting] an estimate.
"""
import csv
import json
import os
import sys

HW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HW, "sourcing"))
import jlc_api  # noqa: E402

BOARDS = 5
LIMIT_EUR = 100.0                 # COST-01
SETUP, STENCIL = 8.18, 1.53       # [page] jlcpcb.com/help/article/pcb-assembly-price, Economic PCBA
PER_JOINT = 0.0016                # [page] same
EXTENDED_FEE = 3.07               # [page] per Extended line; Basic and Preferred lines are free of it
PCB = (2.0, 7.0)                  # [schatting] five bare 2-layer boards up to 100 x 100 mm, low and high
SHIPPING = (15.0, 25.0)           # [schatting] to the Netherlands, low and high
VAT = 0.21                        # [schatting] that JLC charges Dutch VAT on goods and shipping at checkout
USD_EUR = 0.892                   # ECB reference rate of 2026-11-10 (api.frankfurter.dev)
CACHE = os.path.join(HW, "sourcing", "jlc_parts.json")


def parts(lcsc_list, refresh=False):
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) and not refresh else {}
    for c in lcsc_list:
        if c not in cache:
            cache[c] = jlc_api.part(c)
            assert cache[c], f"{c}: not in JLC's parts library"
    json.dump(cache, open(CACHE, "w"), indent=1, sort_keys=True)
    return cache


def bom():
    """[(lcsc, qty per board, pads per part, what)] and where it came from."""
    real, cpl = os.path.join(HW, "fab", "jlc", "ptz-driver_bom.csv"), os.path.join(HW, "fab", "jlc", "ptz-driver_pads.json")
    if os.path.exists(real) and os.path.exists(cpl):
        pads = json.load(open(cpl))            # reference -> number of soldered pads, written by fab/make_jlc.py
        rows = []
        for r in csv.DictReader(open(real)):
            refs = r["Designator"].split(",")
            rows.append((r["LCSC Part #"], len(refs), sum(pads[x] for x in refs) / len(refs), r["Comment"]))
        return rows, "fab/jlc/ptz-driver_bom.csv"
    rows = [(r["LCSC"], int(r["Qty"]), int(r["Pads"]), r["What"]) for r in csv.DictReader(open(os.path.join(HW, "sourcing", "planned_bom.csv")))]
    return rows, "sourcing/planned_bom.csv (planned, before the board)"


def main():
    rows, source = bom()
    info = parts([r[0] for r in rows], "--refresh" in sys.argv)
    joints = round(sum(q * p for _, q, p, _ in rows)) * BOARDS
    part_cost = sum(q * BOARDS * info[c]["price"] for c, q, _, _ in rows)
    extended = [(c, w) for c, _, _, w in rows if info[c]["library"] == "Extended"]
    fixed = SETUP + STENCIL + joints * PER_JOINT + len(extended) * EXTENDED_FEE + part_cost
    low, high = [(fixed + PCB[i] + SHIPPING[i]) * (1 + VAT) * USD_EUR for i in (0, 1)]
    lines = [
        f"Source of the parts list: `{source}`: {len(rows)} lines, {sum(q for _, q, _, _ in rows)} parts and {joints // BOARDS} solder joints per board.",
        "",
        "| Item | Low | High | Source |", "| --- | --- | --- | --- |",
        f"| Five bare boards, 2 layers, up to 100 × 100 mm | ${PCB[0]:.2f} | ${PCB[1]:.2f} | `[schatting]` |",
        f"| Setup fee | ${SETUP:.2f} | ${SETUP:.2f} | `[page]` |",
        f"| Stencil | ${STENCIL:.2f} | ${STENCIL:.2f} | `[page]` |",
        f"| SMT joints, {joints} × ${PER_JOINT} | ${joints * PER_JOINT:.2f} | ${joints * PER_JOINT:.2f} | `[page]`, joints counted from the list |",
        f"| Extended loading, {len(extended)} lines × ${EXTENDED_FEE} | ${len(extended) * EXTENDED_FEE:.2f} | ${len(extended) * EXTENDED_FEE:.2f} | `[page]` |",
        f"| Parts for five boards | ${part_cost:.2f} | ${part_cost:.2f} | `[api]`, price for one piece |",
        f"| Shipping to the Netherlands | ${SHIPPING[0]:.2f} | ${SHIPPING[1]:.2f} | `[schatting]` |",
        f"| **Subtotal** | **${fixed + PCB[0] + SHIPPING[0]:.2f}** | **${fixed + PCB[1] + SHIPPING[1]:.2f}** | |",
        f"| With 21 % VAT | ${(fixed + PCB[0] + SHIPPING[0]) * (1 + VAT):.2f} | ${(fixed + PCB[1] + SHIPPING[1]) * (1 + VAT):.2f} | `[schatting]` |",
        f"| **In euros, at {USD_EUR}** | **€{low:.0f}** | **€{high:.0f}** | ECB rate of 2026-11-10 |",
        "",
        f"Extended lines ({len(extended)} of at most 3): " + "; ".join(f"{w} ({c})" for c, w in extended) + ".",
        "Free of the loading fee: " + f"{sum(info[c]['library'] == 'Basic' for c, *_ in rows)} Basic and {sum(info[c]['library'] == 'Preferred' for c, *_ in rows)} Preferred lines.",
    ]
    print("\n".join(lines))
    print(f"\nper board: parts ${part_cost / BOARDS:.2f}; the high estimate is €{high:.0f} of €{LIMIT_EUR:.0f}", file=sys.stderr)
    assert len(extended) <= 3, "more than three Extended lines (BRD-12): this goes to the owner first"
    assert high <= LIMIT_EUR, "the estimate is over COST-01: this goes to the owner first"


if __name__ == "__main__":
    main()
