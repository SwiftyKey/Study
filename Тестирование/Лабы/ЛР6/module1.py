def max_elem_correct(arr: list[float]) -> float:
    return max(map(abs, arr))


def max_elem_incorrect(arr: list[float]) -> float:
    return max(arr)


def dummy(arr: list[float]) -> float:
    print('Выполнился модуль 1')
