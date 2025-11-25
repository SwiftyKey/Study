def sum_negatives_correct(arr: list[float]) -> float:
    return round(sum(filter(lambda x: x < 0, arr)), 2)


def sum_negatives_incorrect(arr: list[float]) -> float:
    return round(sum(filter(lambda x: x > 0, arr)), 2)
