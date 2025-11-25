def prod_between_minmax_correct(arr: list[float]) -> float:
    prod_nums = 1
    min_ix = len(arr) - 1
    max_ix = 0

    for i in range(len(arr)):
        if arr[i] > arr[max_ix]:
            max_ix = i
        elif arr[i] < arr[min_ix]:
            min_ix = i

    if min_ix > max_ix:
        max_ix, min_ix = min_ix, max_ix

    for i in range(min_ix + 1, max_ix):
        prod_nums *= arr[i]

    return round(prod_nums, 2)


def prod_between_minmax_incorrect(arr: list[float]) -> float:
    prod_nums = 1
    min_ix = len(arr) - 1
    max_ix = 0

    for i in range(len(arr)):
        if arr[i] > arr[max_ix]:
            max_ix = i
        elif arr[i] < arr[min_ix]:
            min_ix = i

    if min_ix > max_ix:
        max_ix, min_ix = min_ix, max_ix

    for i in range(min_ix, max_ix):
        prod_nums *= arr[i]

    return round(prod_nums, 2)
