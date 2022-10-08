import math

for a in range(1, 100):

    for b in range(1, 100):

        # Kontroluje, aby se neopakovaly dvojice a, b (protože a + b = b + a)
        if a > b: continue

        # Vypočítá proměnnou c pomocí funkce odmocniny
        c = math.sqrt(a ** 2 + b ** 2)

        # Kontroluje, jestli c je celé číslo (pak se jedná o Pyth. trojici)
        # a jestli c není větší než 100, jinak Pyth. trojici nevypíše
        if c%1 != 0 or c > 100: continue

        # Převede c z desetinného čísla na číslo celé
        c = int(c)

        # Vypíše Pythagorejskou trojici
        print(f'{a}; {b}; {c}')
