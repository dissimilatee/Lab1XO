#!/bin/bash
# Повна серія замірів: ./run_all.sh <MASTER_EXTERNAL_IP> [повторів=3]
M=$1; R=${2:-3}
cd "$(dirname "$0")"
for r in $(seq 1 $R); do for n in 1 2 3 4; do ./bench.sh $M $n | grep -E "workers=|C\(n,k\)"; done; done
