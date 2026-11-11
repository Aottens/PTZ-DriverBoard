#!/bin/sh
# Route the board from scratch. Run from hardware/:  sh route/run.sh [passes]
# Place, DSN out, Freerouting, session in, pours and silkscreen, then the completion rounds.
# The placed board is kept as route/rev-b_input.kicad_pcb; the routed board replaces ptz-driver.kicad_pcb.
set -e
KP=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
$KP tools/board.py place 2>/dev/null
cp ptz-driver.kicad_pcb route/rev-b_input.kicad_pcb
$KP tools/board.py dsn route/rev-b.dsn 2>/dev/null
rm -f route/rev-b.ses
(cd route && /opt/homebrew/opt/openjdk@26/bin/java -Djava.awt.headless=true -jar ~/.kicad-mcp/freerouting.jar \
  -de rev-b.dsn -do rev-b.ses -mp "${1:-12}" --gui.enabled=false > freerouting.log 2>&1)
test -s route/rev-b.ses
$KP tools/board.py ses route/rev-b.ses 2>/dev/null
grep -o "final score[^,]*" route/freerouting.log | tail -1
$KP tools/board.py finish 2>/dev/null
$KP tools/complete.py 4 2>/dev/null
