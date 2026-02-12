def count_zeros(matrix):
    count = 0
    for row in matrix:
        for elem in row:
            if elem == 0:
                count += 1
    return count
