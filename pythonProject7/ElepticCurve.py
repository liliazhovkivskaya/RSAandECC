class EllipticCurve:
    # Эллиптическая кривая над простым полем.
    # Поле задается параметром "p".
    # Коэффициентами кривой являются "a" и "b".
    # Базовой точкой циклической подгруппы является "g".
    # Порядок расположения подгруппы равен "n".
    def __init__(self, p, a, b, g, n):
        self.p = p
        self.a = a
        self.b = b
        self.g = g
        self.n = n
        assert pow(2, p - 1, p) == 1
        assert (4 * a * a * a + 27 * b * b) % p != 0
        assert self.is_on_curve(g)
        assert self.mult(n, g) is None

    def is_on_curve(self, point):
        # Проверяет, лежит ли данная точка на эллиптической кривой.
        if point is None:
            return True
        x, y = point

        return (y * y - x * x * x - self.a * x - self.b) % self.p == 0

    def add(self, point1, point2):
        # Возвращает результат вычисления точка1 + точка2 в соответствии с групповым законом
        assert self.is_on_curve(point1)
        assert self.is_on_curve(point2)
        if point1 is None:
            return point2
        if point2 is None:
            return point1
        x1, y1 = point1
        x2, y2 = point2
        if x1 == x2 and y1 != y2:
            return None
        if x1 == x2:
            m = (3 * x1 * x1 + self.a) * inverse_mod(2 * y1, self.p)
        else:
            m = (y1 - y2) * inverse_mod(x1 - x2, self.p)
        x3 = m * m - x1 - x2
        y3 = y1 + m * (x3 - x1)
        result = (x3 % self.p, -y3 % self.p)
        assert self.is_on_curve(result)
        return result

    def double(self, point):
        # возвращает 2 * точек.
        return self.add(point, point)

    def neg(self, point):
        # Возвращает -точек.
        if point is None:
            return None
        x, y = point
        result = x, -y % self.p
        assert self.is_on_curve(result)
        return result

    def mult(self, n, point):
        # Возвращает n * точек, вычисленных с использованием алгоритма удвоения и сложения.
        if n % self.n == 0 or point is None:
            return None
        if n < 0:
            return self.neg(self.mult(-n, point))
        result = None
        addend = point
        while n:
            if n & 1:
                result = self.add(result, addend)
            addend = self.double(addend)
            n >>= 1
        return result

    def __str__(self):
        a = abs(self.a)
        b = abs(self.b)
        a_sign = '-' if self.a < 0 else '+'
        b_sign = '-' if self.b < 0 else '+'
        return 'y^2 = (x^3 {} {}x {} {}) mod {}'.format(
            a_sign, a, b_sign, b, self.p)


def inverse_mod(n, p):
    # Возвращает значение, обратное n по модулю p.
    # Эта функция возвращает единственное целое число x, такое, что (x * n) % p == 1.
    # n должно быть не нулевым, а p - простым.
    if n == 0:
        raise ZeroDivisionError('деление на ноль')
    if n < 0:
        return p - inverse_mod(-n, p)
    s, old_s = 0, 1
    t, old_t = 1, 0
    r, old_r = p, n
    while r != 0:
        count = old_r // r
        old_r, r = r, old_r - count * r
        old_s, s = s, old_s - count * s
        old_t, t = t, old_s - count * t
    gcd, x, y = old_r, old_s, old_t
    assert gcd == 1
    assert (n * x) % p == 1
    return x % p


ExampleCurve = EllipticCurve(
    p=7387789250824511,
    a=6238554010247637,
    b=5070534591820985,
    g=(4392514062910494, 2959958970177251),
    n=11037913511,

)
