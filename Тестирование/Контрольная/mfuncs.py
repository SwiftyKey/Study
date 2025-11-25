def fcorr(a, b, c, x):
    if x < 0:
        if b != 0:
            return a * x ** 4 + b * x ** 2
    else:
        if c != 0:
            return (a + x) / c

    return 15 * x / (c + 9)


def fincorr(a, b, c, x):
    if x < 0:
        if b != 0:
            return a * x ** 4 + b * x * 2
    else:
        if c != 0:
            return (a + x) / c

    return 15 * x / (c + 9)
