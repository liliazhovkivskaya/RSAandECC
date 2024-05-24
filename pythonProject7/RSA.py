from random import randrange
from hashlib import sha1
from timeit import timeit
from os import urandom

# Первые 50 простых чисел после 2
first_50_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31,
                   37, 41, 43, 47, 53, 59, 61, 67, 71, 73,
                   79, 83, 89, 97, 101, 103, 107, 109, 113, 127,
                   131, 137, 139, 149, 151, 157, 163, 167, 173, 179,
                   181, 191, 193, 197, 199, 211, 223, 227, 229, 233]


def generate_n_bit_odd(n: int):
    # Сгенерируйте случайное нечетное число в диапазоне [2**(n-1)+1, 2**n-1]
    assert n > 1
    return randrange(2 ** (n - 1) + 1, 2 ** n, 2)


def get_lowlevel_prime(n):
    # Сгенерируйте простого число, который не делится на первые простые числа
    while True:
        # Получаем случайное нечетное число
        c = generate_n_bit_odd(n)

        # Проверка делимости чисел
        for divisor in first_50_primes:
            if c % divisor == 0 and divisor ** 2 <= c:
                break
        else:
            return c


def miller_rabin_primality_check(n, k=20):
    # Тест на первичность Миллера-Рабина с заданным циклом тестирования
    # Ввод:
    #    n - n > 3, нечетное целое число, подлежащее проверке на простоту
    #    k - количество раундов тестирования, которые необходимо выполнить.
    # Выход:
    #    Истинно переданное значение (n - сильное вероятное простое число)
    #    False - ошибка (n - составное число)"'

    # # Для заданного нечетного целого числа n > 3, записанного как (2^s)*d+1,
    # , где s и d - положительные целые числа, а d - нечетное.
    assert n > 3
    if n % 2 == 0:
        return False

    s, d = 0, n - 1
    while d % 2 == 0:
        d >>= 1
        s += 1

    for _ in range(k):
        a = randrange(2, n - 1)
        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(s):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def get_random_prime(num_bits):
    while True:
        pp = get_lowlevel_prime(num_bits)
        if miller_rabin_primality_check(pp):
            return pp


def gcd(a, b):
    # Вычисляет нод, используя алгоритм Евклида
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    # Вычисляет наименьшее общее кратное, используя метод GCD
    return a // gcd(a, b) * b


def exgcd(a, b):
    # Расширенный евклидов алгоритм, который может вернуть все значения gcd, s, t таким образом, чтобы
    # будет удовлетворять условию Безу: gcd(a,b) = a*s + b* t
    # Возвращает: (gcd, s, t) в виде кортежа
    old_s, s = 1, 0
    old_t, t = 0, 1
    while b:
        q = a // b
        s, old_s = old_s - q * s, s
        t, old_t = old_t - q * t, t
        a, b = b, a % b
    return a, old_s, old_t


def invmod(e, m):
    # Находит обратное по модулю величину
    g, x, y = exgcd(e, m)
    assert g == 1
    # Теперь зная e*x + m*y = g = 1, so e*x ≡ 1 (mod m).
    if x < 0:
        x += m
    return x


# Принимает на вход целое число без знака x и преобразует его в последовательность байтов.
def uint_to_bytes(x: int) -> bytes:
    if x == 0:
        return bytes(1)
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


# Принимает на вход последовательность байтов xbytes и преобразует ее обратно в целое число без знака.
def uint_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')


RSA_DEFAULT_EXPONENT = 65537
RSA_DEFAULT_MODULUS_LEN = 2048


class RSA:
    # Реализует шифрование/дешифрование с открытым ключом RSA с показателем
    # степени по умолчанию 65537 и размером ключа по умолчанию 2048
    def __init__(self, key_length=RSA_DEFAULT_MODULUS_LEN,
                 exponent=RSA_DEFAULT_EXPONENT, fast_decrypt=False):
        self.e = exponent
        self.fast = fast_decrypt
        t = 0
        p = q = 2
        while gcd(self.e, t) != 1:
            p = get_random_prime(key_length // 2)
            q = get_random_prime(key_length // 2)
            t = lcm(p - 1, q - 1)
        self.n = p * q
        self.d = invmod(self.e, t)
        if (fast_decrypt):
            self.p, self.q = p, q
            self.d_P = self.d % (p - 1)
            self.d_Q = self.d % (q - 1)
            self.q_Inv = invmod(q, p)

    def encrypt(self, binary_data: bytes):
        int_data = uint_from_bytes(binary_data)
        return pow(int_data, self.e, self.n)

    def decrypt(self, encrypted_int_data: int):
        int_data = pow(encrypted_int_data, self.d, self.n)
        return uint_to_bytes(int_data)

    def decrypt_fast(self, encrypted_int_data: int):
        # Для использования китайской теоремы об остатках + Малую теорему Ферма
        assert self.fast == True
        m1 = pow(encrypted_int_data, self.d_P, self.p)
        m2 = pow(encrypted_int_data, self.d_Q, self.q)
        t = m1 - m2
        if t < 0:
            t += self.p
        h = (self.q_Inv * t) % self.p
        m = (m2 + h * self.q) % self.n
        return uint_to_bytes(m)

    def generate_signature(self, encoded_msg_digest: bytes):
        # для использования закрытого ключа RSA для генерации цифровой подписи
        int_data = uint_from_bytes(encoded_msg_digest)
        return pow(int_data, self.d, self.n)

    def generate_signature_fast(self, encoded_msg_digest: bytes):
        # Для использования китайской теоремы об остатках + Малую теорему Ферма
        assert self.fast == True
        int_data = uint_from_bytes(encoded_msg_digest)
        s1 = pow(int_data, self.d_P, self.p)
        s2 = pow(int_data, self.d_Q, self.q)
        t = s1 - s2
        if t < 0:
            t += self.p
        h = (self.q_Inv * t) % self.p
        s = (s2 + h * self.q) % self.n
        return s

    def verify_signature(self, digital_signature: int):
        # для использования открытого ключа
        int_data = pow(digital_signature, self.e, self.n)
        return uint_to_bytes(int_data)


alice = RSA(1024, 3, True)
msg = b'The date of completion of the final qualifying work is June 13'
ctxt = alice.encrypt(msg)
# print(ctxt)
assert alice.decrypt(ctxt) == msg
assert alice.decrypt_fast(ctxt) == msg
# print("Тест на шифрование/дешифрование сообщений RSA пройден!")

mdg = sha1(msg).digest()
# print(mdg)
sign1 = alice.generate_signature(mdg)
sign2 = alice.generate_signature_fast(mdg)
# print("sign1", sign1)
# print("sign2", sign2)
assert sign1 == sign2
assert alice.verify_signature(sign1) == mdg
assert alice.verify_signature(sign2) == mdg


# print("Тест на генерацию/верификацию подписи RSA пройден!")


def decrypt_norm(tester, ctxt: bytes, msg: bytes):
    ptxt = tester.decrypt(ctxt)
    assert ptxt == msg


def decrypt_fast(tester, ctxt: bytes, msg: bytes):
    ptxt = tester.decrypt_fast(ctxt)
    assert ptxt == msg

# print("Запись времени дешифрования RSA...")
# for klen in [512, 1024, 2048, 3072, 4096]:
#    rpt = int(klen ** 0.5)
#    obj = RSA(klen, 65537, True)
#    t_n = t_f = 0
#    for _ in range(5):
#        mg = urandom(int(klen / 16))
#        ct = obj.encrypt(mg)
#        t_n += timeit(lambda: decrypt_norm(obj, ct, mg), number=rpt)
#        t_f += timeit(lambda: decrypt_fast(obj, ct, mg), number=rpt)
#    print("Размер ключа %4d  Стандартная скорость %.4fs"
#          % (klen, t_n / 5 / rpt))
#
