#!/usr/bin/env python3
"""Look parts up in JLC's assembly library, the way jlcpcb.com/parts does: plain JSON over HTTPS, no login.

  python3 hardware/sourcing/jlc_api.py C130026 SMBJ18A        search by LCSC number or keyword
  python3 hardware/sourcing/jlc_api.py --free "AO3401A"       only parts without a loading fee on Economic PCBA

A part is free of the Extended loading fee when it is in the Basic library or flagged Preferred
("Preferred extended parts are also fee-free on Economic PCBA", jlcpcb.com/solutions/pcb-prototype-assembly,
read 2026-11-11). The API does not give the PCBA Type (Economic / Standard Only): that is on the part's page,
jlcpcb.com/partdetail/C<number>, and is recorded by sourcing/jlc_read.py.
"""
import json
import subprocess
import sys
import time

URL = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"


def search(keyword="", n=15, **flt):
    body = dict(flt, keyword=keyword, currentPage=1, pageSize=n)
    for attempt in range(4):
        raw = subprocess.run(["curl", "-s", "-m", "40", "-X", "POST", URL, "-H", "Content-Type: application/json",
                              "-d", json.dumps(body)], capture_output=True, text=True).stdout
        if raw.lstrip().startswith("{"):
            return (json.loads(raw).get("data") or {}).get("componentPageInfo", {}).get("list") or []
        time.sleep(5 * (attempt + 1))
    raise SystemExit(f"{keyword}: JLC's parts API does not answer")


def part(lcsc):
    """One part by its LCSC number, as a small dict, or None."""
    for r in search(lcsc, 5):
        if r["componentCode"] == lcsc:
            price = (r.get("componentPrices") or [{}])[0].get("productPrice")
            lib = "Basic" if r["componentLibraryType"] == "base" else ("Preferred" if r.get("preferredComponentFlag") else "Extended")
            return dict(lcsc=lcsc, mpn=r["componentModelEn"], package=r.get("componentSpecificationEn") or "", library=lib,
                        stock=r["stockCount"], price=price, maker=r.get("componentBrandEn") or "", describe=r.get("describe") or "")
    return None


if __name__ == "__main__":
    free = "--free" in sys.argv
    for kw in [a for a in sys.argv[1:] if not a.startswith("--")]:
        rows = search(kw, 30)
        print(f"== {kw}")
        for r in rows:
            lib = "Basic" if r["componentLibraryType"] == "base" else ("Preferred" if r.get("preferredComponentFlag") else "Extended")
            if free and lib == "Extended":
                continue
            price = (r.get("componentPrices") or [{}])[0].get("productPrice", 0)
            print(f"{r['componentCode']:10} {lib:9} stock {r['stockCount']:>8}  ${price:<7} {r['componentModelEn'][:28]:28} "
                  f"{(r.get('componentSpecificationEn') or '')[:16]:16} {(r.get('describe') or '')[:80]}")
        time.sleep(1)
