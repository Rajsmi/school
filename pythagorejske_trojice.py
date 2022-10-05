import math

# Pythagorejská trojice (PT) je dána předpisem a, b, c = f(x, y); (x, y ∈ N) ∧ (x > y)
# https://cs.wikipedia.org/wiki/Pythagorejsk%C3%A1_trojice

# Největší možná hodnota jednoho z čísel Pyth. trojice
MAX_NUMBER = 100

for x in range(1, 100):
    for y in range(1, 100):

        # Kontrola podmínky pro vytvoření PT
        if x <= y: break

        # Definování čísel PT
        a = 2 * x * y
        b = x ** 2 - y ** 2
        c = x ** 2 + y ** 2

        # Dosáhne-li proměnná největší možné definované hodnoty, cyklus se přeruší
        if c > MAX_NUMBER: break

        # Volitelné. Výpis POUZE základních PT.
        # Zjistí největší možný dělitel tří definovaných čísel. Je-li větší než 1,
        # nejedná se o základní PT, proto tuto PT nevypíše a pokračuje na další kolo cyklu.
        if math.gcd(a, b, c) != 1: continue

        # Vypíše Pythagorejskou trojici
        print(f'{a}; {b}; {c}')

