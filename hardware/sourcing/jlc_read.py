#!/usr/bin/env python3
"""What jlcpcb.com/partdetail/C<number> said on 2026-11-10, and the table made from it for the parts on the board.

PCBA Type, MPN, package and library type were read from each part page's HTML; stock from the same page as the
built-in browser shows it ("In Stock"). A part without a stock figure here is a Basic-library part or a resistor whose
stock was not read one by one. Run after fab/make_jlc.py to rewrite jlc_check.md:  python3 hardware/sourcing/jlc_read.py
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
E = "Economic and Standard"
READ = {  # LCSC: (MPN, package, PCBA Type, library, stock or None)
    "C1523": ("0402B102K500NT", "0402", E, "Basic", None), "C1525": ("CL05B104KO5NNNC", "0402", E, "Basic", None),
    "C1532": ("0402B223K500NT", "0402", E, "Basic", None), "C1542": ("0402B682K500NT", "0402", E, "Extended", 172514),
    "C1546": ("0402CG101J500NT", "0402", E, "Basic", None), "C1549": ("0402CG180J500NT", "0402", E, "Basic", None),
    "C1555": ("0402CG220J500NT", "0402", E, "Basic", None), "C2286": ("KT-0603R", "0603", E, "Basic", None),
    "C7519": ("USBLC6-2SC6", "SOT-23-6L", E, "Extended", 30229), "C7662": ("SN74LVC139APWR", "TSSOP-16", E, "Extended", 3929),
    "C7668": ("SN74LVC244APWR", "TSSOP-20", E, "Extended", 97496), "C7813": ("SN74LVC125APWR", "TSSOP-14", E, "Extended", 45811),
    "C8598": ("B5819W SL", "SOD-123", E, "Basic", None), "C8963": ("SP3485EN-L/TR", "SOIC-8", E, "Basic", None),
    "C9006": ("X322525MOB4SI", "SMD3225-4P", E, "Basic", None), "C11702": ("0402WGF1001TCE", "0402", E, "Basic", None),
    "C12084": ("SN65HVD230DR", "SOIC-8", E, "Extended", 105760), "C12747": ("LBZT52C12T1G", "SOD-123", E, "Extended", 34046),
    "C13585": ("CL31A106KBHNNNE", "1206", E, "Basic", None), "C15195": ("CL05B103KB5NNNC", "0402", E, "Basic", None),
    "C15849": ("CL10A105KB8NNNC", "0603", E, "Basic", None), "C19666": ("CL10A475KO8NNNC", "0603", E, "Basic", None),
    "C19702": ("CL10A106KP8NNNC", "0603", E, "Basic", None), "C20785": ("SMD0603P020TF", "0603", E, "Extended", 3687),
    "C22787": ("0603WAF1200T5E", "0603", E, "Basic", None), "C23733": ("CL05A475MP5NRNC", "0402", E, "Basic", None),
    "C25076": ("0402WGF1000TCE", "0402", E, "Basic", None), "C25077": ("0402WGF100JTCE", "0402", E, "Basic", None),
    "C25091": ("0402WGF2200TCE", "0402", E, "Basic", None), "C25092": ("0402WGF220JTCE", "0402", E, "Basic", None),
    "C25105": ("0402WGF330JTCE", "0402", E, "Basic", None), "C25120": ("0402WGF499JTCE", "0402", E, "Basic", None),
    "C25741": ("0402WGF1003TCE", "0402", E, "Basic", None), "C25744": ("0402WGF1002TCE", "0402", E, "Basic", None),
    "C25752": ("0402WGF1202TCE", "0402", E, "Basic", None), "C25767": ("0402WGF2203TCE", "0402", E, "Extended", None),
    "C25768": ("0402WGF2202TCE", "0402", E, "Basic", None), "C25778": ("0402WGF3303TCE", "0402", E, "Extended", None),
    "C25792": ("0402WGF4702TCE", "0402", E, "Basic", None), "C25879": ("0402WGF2201TCE", "0402", E, "Basic", None),
    "C25900": ("0402WGF4701TCE", "0402", E, "Basic", None), "C25905": ("0402WGF5101TCE", "0402", E, "Basic", None),
    "C26083": ("0402WGF1004TCE", "0402", E, "Basic", None), "C29823": ("1206B475K500NT", "1206", E, "Basic", None),
    "C32843": ("W5500", "LQFP-48 7x7", E, "Extended", 15662), "C37130": ("AO3422", "SOT-23", E, "Extended", 69626),
    "C44377": ("TPS54360DDAR", "SOIC-8-EP", E, "Extended", 53853), "C45783": ("CL21A226MAQNNNE", "0805", E, "Basic", None),
    "C52923": ("CL05A105KA5NQNC", "0402", E, "Basic", None), "C60105": ("19-237/R6GHBHC-A01/2T", "SMD-4P 1.6x1.6", E, "Extended", 20381),
    "C72975": ("0452007.MRL", "2410", E, "Extended", 2803), "C85833": ("BLM18KG601SN1D", "0603", E, "Extended", 782464),
    "C128694": ("SMMS0630-220M", "SMD 7.1x6.6", E, "Extended", 134449), "C141836": ("TLV62569DBVR", "SOT-23-5", E, "Extended", 265832),
    "C144395": ("B4B-XH-A(LF)(SN)", "through-hole, 2.5 mm", E, "Extended", 627935),
    "C158012": ("B2B-XH-A(LF)(SN)", "through-hole, 2.5 mm", E, "Extended", 588890),
    "C160315": ("B2P-VH(LF)(SN)", "through-hole, 3.96 mm", E, "Extended", 220525),
    "C160404": ("SM04B-SRSS-TB(LF)(SN)", "SMD, 1.0 mm", E, "Extended", 80682), "C161692": ("BM04B-GHS-TBT(LF)(SN)", "SMD, 1.25 mm", E, "Extended", 1999),
    "C165948": ("TYPE-C-31-M-12", "SMD", E, "Extended", 292446), "C187598": ("046601.5NRHF", "1206", E, "Extended", 7831),
    "C189895": ("SM04B-GHS-TB(LF)(SN)", "SMD, 1.25 mm", E, "Extended", 34649), "C269128": ("SMD1812B050TF/30", "1812", E, "Extended", 42823),
    "C307331": ("CL05B104KB54PNC", "0402", E, "Basic", None), "C318884": ("TS-1187A-B-A-B", "SMD 5.1x5.1", E, "Basic", None),
    "C378970": ("BM07B-GHS-TBT(LF)(SN)(N)", "SMD, 1.25 mm", E, "Extended", 20992), "C400894": ("AOD4185", "TO-252", E, "Extended", 64261),
    "C408335": ("MWSA0402S-2R2MT", "SMD 4.4x4.2", E, "Extended", 6802), "C484743": ("SN74AHCT244PWR", "TSSOP-20", E, "Extended", 3747),
    "C495552": ("SM07B-GHS-TB(LF)(SN)", "SMD, 1.25 mm", E, "Extended", 25771), "C521963": ("SM712", "SOT-23", E, "Extended", 487299),
    "C970698": ("RVT1H221M1010", "SMD D10xL10.2", E, "Extended", 28796), "C2652299": ("PCAL6416APW,118", "TSSOP-24", E, "Extended", 296),
    "C2864807": ("TMP1075DGKR", "VSSOP-8", E, "Extended", 15738), "C2929935": ("FRC0402F1242TS", "0402", E, "Extended", 504851),
    "C7420333": ("BAT54S", "SOT-23", E, "Extended", 556855), "C7420367": ("SS36", "SMA", E, "Extended", 423930),
    "C7470946": ("SMBJ24A", "DO-214AA", E, "Extended", 10517), "C7494373": ("TMC5240ATJ+T", "TQFN-32", E, "Extended", 3329),
    "C20627095": ("ESP32-C6-MINI-1U-H4", "SMD 13.2x12.5", E, "Extended", 3549),
}


def main():
    bom = os.path.join(HERE, "..", "fab", "jlc", "ptz-driver_bom.csv")
    rows = list(csv.DictReader(open(bom)))
    out = ["# JLC check of every assembled part, read 2026-11-10", "",
           "Made by `jlc_read.py` from the BOM in `fab/jlc/` and what each part's page on jlcpcb.com said that day.",
           "One line marked Standard Only would move the whole order off Economic PCBA: there is none.",
           "Stock changes daily: **recheck every line on the day of the order** (order gate, point 4).", "",
           "| LCSC | MPN | Package | Qty per board | PCBA Type | Library | In stock | Used as |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    missing, basic, extended = [], 0, 0
    for r in sorted(rows, key=lambda r: int(r["LCSC Part #"][1:])):
        c = r["LCSC Part #"]
        if c not in READ:
            missing.append(c)
            continue
        mpn, pkg, pcba, lib, stock = READ[c]
        qty = len(r["Designator"].split(","))
        basic += lib == "Basic"
        extended += lib != "Basic"
        assert pcba == E, f"{c} is {pcba}"
        low = stock is not None and stock < 100 * qty
        out.append(f"| {c} | {mpn} | {pkg} | {qty} | {pcba} | {lib} | {'not read' if stock is None else f'{stock:,}'.replace(',', ' ')}{' **low**' if low else ''} | {r['Comment']} |")
    out += ["", f"{len(rows)} BOM lines: {basic} Basic, {extended} Extended. All are \"{E}\".", "",
            "Tightest stock: the I/O expander PCAL6416APW (296) and the top-entry 4-pin header BM04B-GHS-TBT (1 999).",
            "The TJA1051T/3 CAN transceiver first chosen had 6 left, so the board uses the SN65HVD230DR instead.", ""]
    assert not missing, f"no page read for {missing}"
    open(os.path.join(HERE, "jlc_check.md"), "w").write("\n".join(out))
    print(f"jlc_check.md: {len(rows)} lines, {basic} Basic, {extended} Extended")


if __name__ == "__main__":
    main()
