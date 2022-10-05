for x in range(1, 100):
    for y in range(1, 100):

        if x <= y: continue

        a = 2 * x * y
        b = x ** 2 - y ** 2
        c = x ** 2 + y ** 2

        if c > 100: break

        print(f'{a}; {b}; {c}')