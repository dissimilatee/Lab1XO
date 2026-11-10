# ЛР1 (тема 8.4): паралельні біноміальні коефіцієнти на PARCS-Python

C(n,k) та P(n,k) = n!/(n-k)!. Діапазон `i = 1..k` ділиться порівну між воркерами;
кожен рахує добуток `(n-k+i)` і `i` на своєму відрізку, master перемножує і ділить.
Режими (3-й рядок input): `mod` — за модулем 1e9+7 (дані мінімальні, чисте масштабування),
`exact` — точні великі числа (hex-рядки по мережі).

Файли: `solution.py` (PARCS-модуль), `sequential.py` (еталон), `input.txt`,
`plot.py` (таблиця + графік з `results.csv`), `local/check.py` (перевірка з math.comb).

## Локальна перевірка (без хмари)
    PYTHONPATH=local:. python3 local/check.py        # корректність для 1..7 воркерів
    PYTHONPATH=local:. python3 sequential.py input.txt

## Хмара (за README parcs-python, Google Cloud, Docker-образ)
    gcloud auth login
    gcloud projects create <name> && gcloud config set project <name>
    gcloud config set compute/zone europe-north1-a
    gcloud compute firewall-rules create allow-all --direction=INGRESS --priority=1000 \
      --network=default --action=ALLOW --rules=all --source-ranges=0.0.0.0/0
    gcloud compute instances create-with-container master \
      --container-image=registry.hub.docker.com/hummer12007/parcs-node --container-env PARCS_ARGS="master"
    # INTERNAL_IP master -> $MASTER_INT
    gcloud compute instances create-with-container worker1 worker2 worker3 worker4 \
      --container-image=registry.hub.docker.com/hummer12007/parcs-node \
      --container-env PARCS_ARGS="worker $MASTER_INT"
Веб-інтерфейс: `http://<EXTERNAL_IP master>:8080` -> Add job: завантажити `solution.py` і `input.txt`,
обрати кількість воркерів (1, 2, 3, 4), записати час у `results.csv`
(`workers,time_s`; рядок `0,<час>` — результат `sequential.py` на тій самій машині).
Після замірів видалити VM: `gcloud compute instances delete master worker1 worker2 worker3 worker4`.

Примітки:
- PARCS-Python працює на Python 2.7; `solution.py` сумісний з Python 2 і 3 (у Python 2 використовується `xrange`).
- `gcloud compute instances create-with-container` більше не підтримується, тому VM створюються з образу Ubuntu,
  а `cloud/startup.sh` ставить Docker і запускає образ `hummer12007/parcs-node`.
- Автоматичний прогін замірів: `./cloud/run_all.sh <MASTER_HOST:PORT> 3` (результати в `results_raw.csv`), далі `python3 plot.py`.
- Результати: `results.csv`, `plot.png`; звіт: `report/`.
