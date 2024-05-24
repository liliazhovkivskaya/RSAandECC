import random

from ElepticCurve import inverse_mod, ExampleCurve as curve


class PollardRhoSequence:

    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
        self.add_a1 = random.randrange(1, curve.n)
        self.add_b1 = random.randrange(1, curve.n)
        self.add_x1 = curve.add(curve.mult(self.add_a1, point1), curve.mult(self.add_b1, point2))
        self.add_a2 = random.randrange(1, curve.n)
        self.add_b2 = random.randrange(1, curve.n)
        self.add_x2 = curve.add(curve.mult(self.add_a2, point1), curve.mult(self.add_b2, point2))

    def __iter__(self):
        path = curve.p // 3 + 1
        x = None
        a = 0
        b = 0
        while True:
            if x is None:
                i = 0
            else:
                i = x[0] // path
            if i == 0:
                # x - это либо точка на бесконечности (нет), либо она находится в первой
                # трети плоскости (x[0] <= curve.p / 3).
                a += self.add_a1
                b += self.add_b1
                x = curve.add(x, self.add_x1)
            elif i == 1:
                # x находится во второй трети плоскости
                # (кривая.p / 3 < x[0] <= кривая.p * 2/3).
                a *= 2
                b *= 2
                x = curve.double(x)
            elif i == 2:
                # x находится в последней трети плоскости (x[0] > кривая.p * 2/3).
                a += self.add_a2
                b += self.add_b2
                x = curve.add(x, self.add_x2)
            else:
                raise AssertionError(i)
            a = a % curve.n
            b = b % curve.n
            yield x, a, b


def log(p, q, counter=None):
    assert curve.is_on_curve(p)
    assert curve.is_on_curve(q)
    # Ро Полларда иногда может давать сбой: он может обнаружить, что a1 == a2 и b1 == b2,
    # что приводит к ошибке при делении на ноль. Поскольку PollardRhoSequence использует
    # случайные коэффициенты, у нас больше шансов найти логарифм
    # если мы попробуем еще раз, не влияя на асимптотическую временную сложность.
    for i in range(3):
        sequence = PollardRhoSequence(p, q)
        tortoise = iter(sequence)  # Обход черепахи
        hare = iter(sequence)  # Обход зайца
        # Диапазон от 0 до кривой.n - 1, но на самом деле алгоритм
        # остановится гораздо раньше (либо найдет логарифм, либо потерпит неудачу с делением на ноль).
        for j in range(curve.n):
            x1, a1, b1 = next(tortoise)

            x2, a2, b2 = next(hare)
            x2, a2, b2 = next(hare)
            if x1 == x2:
                if b1 == b2:
                    # Если делим на нуль.
                    # Попробуем использовать другую случайную последовательность.
                    break
                x = (a1 - a2) * inverse_mod(b2 - b1, curve.n)
                logarithm = x % curve.n
                steps = i * curve.n + j + 1
                return logarithm, steps
    raise AssertionError('Логарифм не найден',)



def main():
    x = random.randrange(1, curve.n)
    print(x)
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
