def arr_sort_correct(arr: list[float]) -> list[float]:
    sorted_arr = arr[:]

    for i in range(len(sorted_arr)):
        for j in range(len(sorted_arr)):
            if sorted_arr[i] < sorted_arr[j]:
                sorted_arr[i], sorted_arr[j] = sorted_arr[j], sorted_arr[i]

    return list(map(lambda x: round(x, 2), sorted_arr))



def arr_sort_incorrect(arr: list[float]) -> list[float]:
    sorted_arr = arr[:]

    for i in range(len(sorted_arr)):
        for j in range(len(sorted_arr)):
            if sorted_arr[i] > sorted_arr[j]:
                sorted_arr[i], sorted_arr[j] = sorted_arr[j], sorted_arr[i]

    return list(map(lambda x: round(x, 2), sorted_arr))
