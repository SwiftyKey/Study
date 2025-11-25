def min_max_odd_in_columns(matrix, n, m):
    min_elems, max_elems = [], []

    for j in range(m):
        min_odd, max_odd = None, None

        for i in range(n):
            elem = matrix[i][j]
            if elem % 2 == 1:
                if min_odd is None or elem < min_odd:
                    min_odd = elem
                if max_odd is None or elem > max_odd:
                    max_odd = elem

        min_elems.append(min_odd)
        max_elems.append(max_odd)

    return min_elems, max_elems
