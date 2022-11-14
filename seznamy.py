import random

def seznam(n: int, m: int) -> list:
    numbers = list()
    for num in range(n):
        rand = random.randint(0, m)
        numbers.append(rand)
    return numbers


def vycisti(l: list):
    unique = list()
    for num in l:
        if num not in unique: unique.append(num)
    return unique


y = seznam(5, 3)
print(y)
print(vycisti(y))
