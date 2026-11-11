#!/bin/sh
# Gerbers and drill files for JLCPCB, from the current board. Run from hardware/:  sh fab/make_gerbers.sh
# Two copper layers, both masks, both silkscreens, top paste, outline; drill in Excellon with separate PTH and NPTH.
set -e
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
OUT=fab/gerbers
rm -rf "$OUT" && mkdir -p "$OUT"
"$CLI" pcb export gerbers --output "$OUT/" \
  --layers "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,Edge.Cuts" \
  --subtract-soldermask --no-x2 --no-netlist ptz-driver.kicad_pcb
"$CLI" pcb export drill --output "$OUT/" --format excellon --excellon-separate-th --excellon-units mm \
  --drill-origin absolute --generate-map --map-format gerberx2 ptz-driver.kicad_pcb
(cd "$OUT" && zip -q -r ../ptz-driver_gerbers.zip . && ls | wc -l | xargs echo files:)
echo "fab/ptz-driver_gerbers.zip"
