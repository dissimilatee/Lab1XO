#!/bin/bash
# Запуск замірів: ./bench.sh <MASTER_EXTERNAL_IP> <кількість_воркерів> [input.txt]
# Вмикає перші N воркерів, вимикає решту, подає задачу, чекає результат, дописує час у results.csv.
M=$1; N=$2; IN=${3:-input.txt}
cd "$(dirname "$0")/.."
IDS=($(curl -s http://$M/api/worker | grep -o '"id":[0-9]*' | cut -d: -f2))
for idx in "${!IDS[@]}"; do
  [ $idx -lt $N ] && S=enable || S=disable
  curl -s -X POST http://$M/api/worker/${IDS[$idx]}/$S >/dev/null
done
ID=$(curl -s http://$M/jobs | grep -o '#[0-9][0-9]*' | wc -l | tr -d ' ')
curl -s -F job_name=binom_w$N -F solution_file=@solution.py -F input_file=@$IN http://$M/api/job >/dev/null
for t in $(seq 1 400); do
  OUT=$(curl -s -f http://$M/api/job/$ID/output) && break
  sleep 2
done
echo "$OUT"
EL=$(echo "$OUT" | sed -n 's/.*elapsed=\([0-9.]*\) s.*/\1/p')
[ -n "$EL" ] && echo "$N,$EL" >> results_raw.csv
