#!/usr/bin/env python3
"""The JLC check of every assembled part of Rev B: writes sourcing/jlc_check.md from the BOM in fab/jlc/.

Run after fab/make_jlc.py:  python3 hardware/sourcing/jlc_read.py [--refresh]
Library type, stock and price come from JLC's parts API (sourcing/jlc_api.py, kept in jlc_parts.json; --refresh reads
them again). The PCBA Type is only on the part's page, jlcpcb.com/partdetail/<number>: PAGE below is what each page
said on 2026-11-11. A part that is not in PAGE stops the script: read its page first.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jlc_api  # noqa: E402

E = "Economic and Standard"
PAGE = {  # LCSC: (PCBA Type, MFR part, maker) as read on the part page, 2026-11-11
    "C13585": (E, "CL31A106KBHNNNE", "Samsung"), "C14663": (E, "CC0603KRX7R9BB104", "YAGEO"), "C45783": (E, "CL21A226MAQNNNE", "Samsung"),
    "C15850": (E, "CL21A106KAYNNNE", "Samsung"), "C7171": (E, "TAJA106K016RNJ", "(AVX part number; the page names no maker)"),
    "C1588": (E, "CL10B102KB8NNNC", "Samsung"),
    "C57112": (E, "0603B103K500NT", "FH"), "C19077573": (E, "SMBJ18A", "hongjiacheng"), "C8678": (E, "SS34", "MDD"),
    "C8598": (E, "B5819W SL", "Changjing"), "C2500": (E, "BAV99,215", "Nexperia"), "C400894": (E, "AOD4185", "Alpha & Omega"),
    "C20917": (E, "AO3400A", "Alpha & Omega"), "C22807": (E, "0603WAF1503T5E", "UNI-ROYAL"), "C25803": (E, "0603WAF1003T5E", "UNI-ROYAL"),
    "C25804": (E, "0603WAF1002T5E", "UNI-ROYAL"), "C23140": (E, "0603WAF330JT5E", "UNI-ROYAL"), "C21190": (E, "0603WAF1001T5E", "UNI-ROYAL"),
    "C22775": (E, "0603WAF1000T5E", "UNI-ROYAL"), "C23162": (E, "0603WAF4701T5E", "UNI-ROYAL"), "C4190": (E, "0603WAF2201T5E", "UNI-ROYAL"),
    "C2892547": (E, "KNTC0603/10KF3950", "KUU"), "C6186": (E, "AMS1117-3.3", "Advanced Monolithic Systems"),
    "C7420376": (E, "SRV05-4", "hongjiacheng"), "C130026": (E, "TCA9548APWR", "Texas Instruments"),
}


def main():
    cache_path = os.path.join(HERE, "jlc_parts.json")
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) and "--refresh" not in sys.argv else {}
    rows = list(csv.DictReader(open(os.path.join(HERE, "..", "fab", "jlc", "ptz-driver_bom.csv"))))
    out = ["# JLC check of every assembled part of Rev B, read 2026-11-11", "",
           "Made by `jlc_read.py` from the BOM in `fab/jlc/`: PCBA Type from each part's page on jlcpcb.com, library type,",
           "stock and price from JLC's parts API that day. One line marked Standard Only would move the whole order off",
           "Economic PCBA: there is none. Basic and Preferred lines carry no loading fee; an Extended line costs $3.07.",
           "Stock changes daily: **recheck every line on the day of the order** (order gate, point 4).", "",
           "| LCSC | MFR part | Maker | Package | Qty per board | PCBA Type | Library | In stock | $ each | Used as |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    kinds, low = {}, []
    for r in sorted(rows, key=lambda r: int(r["LCSC Part #"][1:])):
        c = r["LCSC Part #"]
        assert c in PAGE, f"{c}: its part page has not been read"
        if c not in cache:
            cache[c] = jlc_api.part(c)
        p, qty = cache[c], len(r["Designator"].split(","))
        pcba, mpn, maker = PAGE[c]
        assert pcba == E, f"{c} is {pcba}"
        assert p["mpn"].split(",")[0].strip() == mpn.split(",")[0].strip(), f"{c}: the page says {mpn}, the API {p['mpn']}"
        kinds[p["library"]] = kinds.get(p["library"], 0) + 1
        if p["stock"] < 200 * qty:
            low.append(c)
        stock = f"{p['stock']:,}".replace(",", " ")
        out.append(f"| {c} | {mpn} | {maker} | {p['package']} | {qty} | {pcba} | {p['library']} | {stock}"
                   f"{' **low**' if c in low else ''} | {p['price']} | {r['Comment']} |")
    json.dump(cache, open(cache_path, "w"), indent=1, sort_keys=True)
    out += ["", f"{len(rows)} BOM lines: " + ", ".join(f"{n} {k}" for k, n in sorted(kinds.items())) + f". All are \"{E}\".",
            "Lowest stock: " + (", ".join(low) if low else "no line has less than 200 times what one board needs."), ""]
    open(os.path.join(HERE, "jlc_check.md"), "w").write("\n".join(out))
    print(f"jlc_check.md: {len(rows)} lines, {kinds}")
    assert kinds.get("Extended", 0) <= 3


if __name__ == "__main__":
    main()
