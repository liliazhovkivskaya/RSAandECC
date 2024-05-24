import gmpy2
import time


def repeated_encryption_attack(M, e, y):
    original_y = y
    y_i = y
    m = 1  # Счётчик итераций
    while True:
        # Возведение в степень e по модулю M
        y_i = gmpy2.powmod(y_i, e, M)
        m += 1
        # Если y_i снова равно исходному y, значит, предыдущее
        # значение y_(i-1) - это искомое сообщение x
        if y_i == original_y:
            break
    # Возвращаем y_(m-1), то есть исходное сообщение x
    x = gmpy2.powmod(original_y, gmpy2.powmod(e, m - 2, M), M)
    return x, m - 1

# Заданные параметры
M =9754240130179587872802263394776514118202837448930355942907868328784445191072963342447243616313452645777162924481691316213304494941409539027067672901834517105802783664691553148474783637982327851913368457136594634856206212558918719080677902721221195922777513175633739632044017920122468196993
#e =65537
e =65537
y =4396109324020249616788198643007431575263562072060742191746452613131877254685472810659641511830983345226220980342981916613437279764849990559215153936954612114425122688642120396453902149292467014042121505759361569703665374977961093323731814264015933338223598596304651016665878960078241085818
#Выполнение атаки
start = time.process_time()
x, iterations = repeated_encryption_attack(M, e, y)
end = time.process_time()
print(f'Время Повторного шифрования {end - start:.100f}s.')
print(f"Найдено за {iterations} итераций")
