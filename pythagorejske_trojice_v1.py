for a in range(1, 100):

    for b in range(1, 100):

        # Kontroluje, aby se neopakovaly dvojice a, b (protože a + b = b + a)
        if a > b: continue

        for c in range(1, 100):

            # Jestliže se matem. def. níže nerovná, nejedná se
            # o Pyth. trojici (PT) a kolo cyklu se přeskočí, trojice se nevypíše
            if a ** 2 + b ** 2 != c ** 2: continue

            # Vypíše Pythagorejskou trojici
            print(f'{a}; {b}; {c}')