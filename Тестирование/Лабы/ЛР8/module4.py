def sort_above_anti_diagonal_insertion(matrix, n):
    if len(matrix) != n or len(matrix[0]) != n:
        raise ValueError("Матрица должна быть квадратной")

    elements = []
    positions = []
    new_matrix = matrix[:]

    for i in range(n):
        for j in range(n):
            if i + j < n - 1:
                elements.append(matrix[i][j])
                positions.append((i, j))

    for i in range(1, len(elements)):
        key = elements[i]
        j = i - 1
        while j >= 0 and elements[j] > key:
            elements[j + 1] = elements[j]
            j -= 1
        elements[j + 1] = key

    for idx, (i, j) in enumerate(positions):
        new_matrix[i][j] = elements[idx]

    return new_matrix
