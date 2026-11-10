# -*- coding: utf-8 -*-
# ЛР1, тема 8.4: паралельне обчислення C(n,k) та P(n,k) на PARCS-Python.
# Код сумісний з Python 2.7 (на ньому працює PARCS-Python) і з Python 3.
#
#   P(n,k) = n!/(n-k)! = prod_{i=1..k} (n-k+i)      (чисельник)
#   C(n,k) = P(n,k) / k!,  k! = prod_{i=1..k} i      (знаменник)
#
# Діапазон i = 1..k ділиться порівну між воркерами (map). Кожен воркер рахує
# добуток чисельника і знаменника на своєму відрізку (дерево добутків).
# Master перемножує часткові добутки (reduce) і ділить: C = P // k!.
# Великі числа ходять мережею як hex-рядки (лінійне перетворення).

import time

from Pyro4 import expose

try:
    range = xrange  # Python 2: range() будує список в пам'яті (OOM на великих діапазонах)
except NameError:
    pass


class Solver:
    MOD = 10 ** 9 + 7

    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers

    def solve(self):
        t0 = time.time()
        n, k, mode = self.read_input()
        w = len(self.workers)
        print("n=%d k=%d mode=%s workers=%d" % (n, k, mode, w))

        # map: відрізки [lo, hi) діапазону 1..k, довжини різняться максимум на 1
        base, rem = divmod(k, w)
        mapped = []
        lo = 1
        for i in range(w):
            hi = lo + base + (1 if i < rem else 0)
            mapped.append(self.workers[i].mymap(n, k, lo, hi, mode))
            lo = hi

        # reduce
        perm, den = self.myreduce(mapped, mode)
        if mode == 'mod':
            comb = perm * pow(den, Solver.MOD - 2, Solver.MOD) % Solver.MOD
        else:
            comb = perm // den
        self.write_output(n, k, mode, perm, comb, time.time() - t0)

    @staticmethod
    @expose
    def mymap(n, k, lo, hi, mode='exact'):
        # чисельник: (n-k+i), знаменник: i, для i з [lo, hi)
        if mode == 'mod':
            # режим mod: усе за модулем простого MOD (потрібно n < MOD)
            M = Solver.MOD
            num = 1
            den = 1
            for i in range(lo, hi):
                num = num * (n - k + i) % M
                den = den * i % M
            return (num, den)
        num = Solver.prod_range(n - k + lo, n - k + hi)
        den = Solver.prod_range(lo, hi)
        return ('%x' % num, '%x' % den)

    @staticmethod
    @expose
    def myreduce(mapped, mode='exact'):
        perm = 1
        den = 1
        for m in mapped:
            a, b = m.value
            if mode == 'mod':
                perm = perm * a % Solver.MOD
                den = den * b % Solver.MOD
            else:
                perm *= int(a, 16)
                den *= int(b, 16)
        return perm, den

    @staticmethod
    def prod_range(a, b):
        """Добуток цілих з [a, b) деревом: множаться числа порівнюваних розмірів."""
        if b <= a:
            return 1
        if b - a == 1:
            return a
        if b - a <= 8:
            r = 1
            for x in range(a, b):
                r *= x
            return r
        m = (a + b) // 2
        return Solver.prod_range(a, m) * Solver.prod_range(m, b)

    def read_input(self):
        with open(self.input_file_name) as f:
            n = int(f.readline())
            k = int(f.readline())
            mode = (f.readline().strip() or 'exact')
        assert 0 <= k <= n and mode in ('exact', 'mod')
        if mode == 'mod':
            assert n < Solver.MOD
        return n, k, mode

    def write_output(self, n, k, mode, perm, comb, elapsed):
        with open(self.output_file_name, 'w') as f:
            f.write('n=%d k=%d mode=%s\n' % (n, k, mode))
            f.write('workers=%d elapsed=%.3f s\n' % (len(self.workers), elapsed))
            if mode == 'mod':
                f.write('C(n,k) mod 1e9+7 = %d\n' % comb)
                f.write('P(n,k) mod 1e9+7 = %d\n' % perm)
            else:
                M = Solver.MOD
                f.write('C(n,k): bits=%d, mod 1e9+7 = %d\n' % (comb.bit_length(), comb % M))
                f.write('P(n,k): bits=%d, mod 1e9+7 = %d\n' % (perm.bit_length(), perm % M))
