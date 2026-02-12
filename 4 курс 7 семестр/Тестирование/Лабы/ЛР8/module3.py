def sum_above_anti_diagonal(matrix, n):
    if len(matrix) != n or len(matrix[0]) != n:
        raise ValueError("Матрица должна быть квадратной для побочной диагонали")

    total = 0
    for i in range(n):
        for j in range(n):
            if i + j < n - 1:
                total += matrix[i][j]
                
    return total
