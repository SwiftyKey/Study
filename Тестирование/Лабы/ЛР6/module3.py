def zeros_to_end_correct(arr: list[float]) -> float:
    count = arr.count(0)
    return list(filter(lambda x: x != 0, arr)) + [0] * count


def zeros_to_end_incorrect(arr: list[float]) -> float:
    count = arr.count(0)
    return list(filter(lambda x: x != 0, arr))


def dummy(arr: list[float]) -> float:
    print('Выполнился модуль 3')
