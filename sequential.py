# -*- coding: utf-8 -*-
# Послідовна версія (еталон): та сама формула в одному процесі, без PARCS.
# Запуск: python sequential.py input.txt
import sys
import time
from solution import Solver

lines = open(sys.argv[1] if len(sys.argv) > 1 else 'input.txt').read().split()
n, k = int(lines[0]), int(lines[1])
mode = lines[2] if len(lines) > 2 else 'exact'
M = Solver.MOD
t = time.time()
if mode == 'mod':
    perm, den = Solver.mymap(n, k, 1, k + 1, 'mod')
    comb = perm * pow(den, M - 2, M) % M
    print('n=%d k=%d mode=mod' % (n, k))
    print('C(n,k) mod 1e9+7 = %d' % comb)
    print('P(n,k) mod 1e9+7 = %d' % perm)
else:
    num, den = Solver.mymap(n, k, 1, k + 1, 'exact')
    perm, den = int(num, 16), int(den, 16)
    comb = perm // den
    print('n=%d k=%d mode=exact' % (n, k))
    print('C(n,k): bits=%d, mod 1e9+7 = %d' % (comb.bit_length(), comb % M))
    print('P(n,k): bits=%d, mod 1e9+7 = %d' % (perm.bit_length(), perm % M))
print('sequential time: %.2f s' % (time.time() - t))
