import time
from functools import reduce
from gmpy2 import gmpy2
from RSA import RSA


def solve_crt(ai: list, mi: list):
    # mi и ai - это список модулей и остатков.
    # Предварительное условие функции состоит в том, что числа
    # в списке mi попарно взаимно просты.
    M = reduce(lambda x, y: x * y, mi)
    ti = [a * (M // m) * int(gmpy2.invert(M // m, m)) for (m, a) in zip(mi, ai)]
    return reduce(lambda x, y: x + y, ti) % M


def rsa_broadcast_attack(ctexts: list, moduli: list):
    # атака RSA: применение CRT для взлома e=3
    c0, c1, c2 = ctexts[0], ctexts[1], ctexts[2]
    n0, n1, n2 = moduli[0], moduli[1], moduli[2]
    m0, m1, m2 = n1 * n2, n0 * n2, n0 * n1
    t0 = (c0 * m0 * int(gmpy2.invert(m0, n0)))
    t1 = (c1 * m1 * int(gmpy2.invert(m1, n1)))
    t2 = (c2 * m2 * int(gmpy2.invert(m2, n2)))
    c = (t0 + t1 + t2) % (n0 * n1 * n2)
    return int(gmpy2.iroot(c, 3)[0])


def uint_to_bytes(x: int) -> bytes:
    # преобразовать целое число без знака в массив байтов
    if x == 0:
        return bytes(1)
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


quote = b'The date of completion of the final qualifying work is June 13'
start = time.process_time()
bob = RSA(1024, 3)
carol = RSA(1024, 3)
dave = RSA(1024, 3)
print(dave)
cipher_list = [bob.encrypt(quote), carol.encrypt(quote), dave.encrypt(quote)]
modulus_list = [bob.n, carol.n, dave.n]
print(modulus_list)
cracked_cipher = solve_crt(cipher_list, modulus_list)
cracked_int = int(gmpy2.iroot(cracked_cipher, 3)[0])
end = time.process_time()
print(f'Время работы Китайской теоремы об остатках {end - start:.10f}s.')
assert cracked_int == rsa_broadcast_attack(cipher_list, modulus_list)
print(cracked_int)
hacked_quote = uint_to_bytes(cracked_int)
assert hacked_quote == quote
print(hacked_quote)
