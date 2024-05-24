import math
import random
from ElepticCurve import ExampleCurve as curve


def log(p, q):
    assert curve.is_on_curve(p)
    assert curve.is_on_curve(q)
    sqrt_n = int(math.sqrt(curve.n)) + 1
    # Вычисляем детские шаги и сохраняем их
    # в списке "baby_steps".
    baby_steps = [None] * sqrt_n
    r = None
    for a in range(1, sqrt_n):
        r = curve.add(r, p)
        baby_steps[a] = r
    # Теперь вычисляем гигантские шаги и
    # проверяем, нет ли какой-либо совпадающей точки.
    r = q
    s = curve.mult(sqrt_n, curve.neg(p))
    for b in range(sqrt_n):
        for a in range(sqrt_n):
            if baby_steps[a] == r:
                steps = sqrt_n + b
                logarithm = a + sqrt_n * b
                return logarithm, steps
        r = curve.add(r, s)
    raise AssertionError('Логарифм не найден')


def main():
    x = random.randrange(1, curve.n)
    p = curve.g
    q = curve.mult(x, p)
    print('Конечная кривая: {}'.format(curve))
    print('Порядок кривой: {}'.format(curve.n))
    print('p = ({}, {})'.format(*p))
    print('q = ({}, {})'.format(*q))
    print(x, '* p = q')
    y, steps = log(p, q)
    print(' log(p, q) =', y)
    print('Понадобилось шагов', steps)
    assert x == y


if __name__ == '__main__':
    main()
