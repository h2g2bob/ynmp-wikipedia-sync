#!/bin/bash
out="${DEST:-/tmp}"
python chgparty_dot.py -n -t -T -o  | dot -T png > "$out/chgparty_interesting.png"
python chgparty_dot.py -c -i | dot -T png > "$out/chgparty_everything.png"
python chgparty_dot.py -sss | dot -T png > "$out/chgparty_big_parties.png"
python chgparty_dot.py -t -i  | dot -T png > "$out/chgparty_multiple_defections.png"
