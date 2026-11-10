# -*- coding: utf-8 -*-
# Таблиця і графік з results.csv (колонки: workers,time_s). Рядок workers=0 — послідовна версія.
# Запуск: python3 plot.py   (потрібен matplotlib: pip install matplotlib)
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rows = [(int(r['workers']), float(r['time_s'])) for r in csv.DictReader(open('results.csv'))]
seq = [t for w, t in rows if w == 0]
par = sorted((w, t) for w, t in rows if w > 0)
t1 = dict(par)[1]
print('| Воркерів | Час, с | Прискорення (vs 1 воркер) |')
print('|---|---|---|')
if seq:
    print('| послідовна | %.2f | - |' % seq[0])
for w, t in par:
    print('| %d | %.2f | %.2fx |' % (w, t, t1 / t))

ws = [w for w, _ in par]
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].plot(ws, [t for _, t in par], 'o-')
ax[0].set_xlabel('Кількість воркерів'); ax[0].set_ylabel('Час, с'); ax[0].set_title('Час виконання')
ax[0].set_xticks(ws); ax[0].grid(alpha=.3)
ax[1].plot(ws, [t1 / t for _, t in par], 'o-', label='виміряне')
ax[1].plot(ws, ws, '--', color='gray', label='ідеальне')
ax[1].set_xlabel('Кількість воркерів'); ax[1].set_ylabel('Прискорення'); ax[1].set_title('Прискорення')
ax[1].set_xticks(ws); ax[1].grid(alpha=.3); ax[1].legend()
plt.tight_layout(); plt.savefig('plot.png', dpi=150)
