# Локальна перевірка без PARCS: емуляція master/worker на заглушці Pyro4, звірка з math.comb/perm.
import math, os, sys, tempfile, time
sys.set_int_max_str_digits(0)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from solution import Solver

class Fut:
    def __init__(s, v): s.value = v
class W:
    def mymap(s, *a): return Fut(Solver.mymap(*a))

def run(n, k, mode, w):
    d = tempfile.mkdtemp(); i = os.path.join(d, 'in'); o = os.path.join(d, 'out')
    open(i, 'w').write('%d\n%d\n%s\n' % (n, k, mode))
    Solver([W() for _ in range(w)], i, o).solve()
    return open(o).read()

M = 10**9 + 7
for mode in ('exact', 'mod'):
    for n, k in [(10, 3), (50, 25), (1000, 1), (1000, 1000), (3000, 1234), (5, 0)]:
        for w in (1, 2, 3, 4, 7):
            out = run(n, k, mode, w)
            c, p = math.comb(n, k), math.perm(n, k)
            assert 'mod 1e9+7 = %d\n' % (c % M) in out and ('= %d' % (p % M)) in out, (mode, n, k, w, out)
print('all ok')
