import pytest
from module1 import count_zeros
from module2 import min_max_odd_in_columns
from module3 import sum_above_anti_diagonal
from module4 import sort_above_anti_diagonal_insertion


def test_count_zeros_all_zeros():
    matrix = [[0, 0], [0, 0]]
    assert count_zeros(matrix) == 4

def test_count_zeros_no_zeros():
    matrix = [[1, 2], [3, 4]]
    assert count_zeros(matrix) == 0

def test_count_zeros_mixed():
    matrix = [[0, 1, -2], [3, 0, 5], [0, 0, 7]]
    assert count_zeros(matrix) == 4

def test_count_zeros_empty():
    matrix = []
    assert count_zeros(matrix) == 0

def test_count_zeros_single_zero():
    matrix = [[0]]
    assert count_zeros(matrix) == 1


def test_min_max_odd_normal():
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    min_elems, max_elems = min_max_odd_in_columns(matrix, 3, 3)
    assert min_elems == [1, 5, 3]
    assert max_elems == [7, 5, 9]

def test_min_max_odd_negative():
    matrix = [
        [-3, 2, -1],
        [4, -5, 6],
        [7, 8, 0]
    ]
    min_elems, max_elems = min_max_odd_in_columns(matrix, 3, 3)
    assert min_elems == [-3, -5, -1]
    assert max_elems == [7, -5, -1]

def test_min_max_odd_no_odd():
    matrix = [[2, 4], [6, 8]]
    min_elems, max_elems = min_max_odd_in_columns(matrix, 2, 2)
    assert min_elems == [None, None]
    assert max_elems == [None, None]

def test_min_max_odd_single_odd():
    matrix = [[2, 3], [4, 6]]
    min_elems, max_elems = min_max_odd_in_columns(matrix, 2, 2)
    assert min_elems == [None, 3]
    assert max_elems == [None, 3]

def test_min_max_odd_rectangular():
    matrix = [
        [1, 2],
        [3, 4],
        [5, 6]
    ]
    min_elems, max_elems = min_max_odd_in_columns(matrix, 3, 2)
    assert min_elems == [1, None]
    assert max_elems == [5, None]


def test_sum_above_anti_diagonal_3x3():
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    assert sum_above_anti_diagonal(matrix, 3) == 7

def test_sum_above_anti_diagonal_4x4():
    matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16]
    ]
    assert sum_above_anti_diagonal(matrix, 4) == 26

def test_sum_above_anti_diagonal_1x1():
    matrix = [[5]]
    assert sum_above_anti_diagonal(matrix, 1) == 0

def test_sum_above_anti_diagonal_empty():
    matrix = [[]]
    with pytest.raises(ValueError, match="квадратной"):
        sum_above_anti_diagonal(matrix, 1)

def test_sum_above_anti_diagonal_non_square():
    matrix = [[1, 2, 3], [4, 5, 6]]
    with pytest.raises(ValueError):
        sum_above_anti_diagonal(matrix, 2)


def test_sort_above_anti_diagonal_3x3():
    matrix = [
        [3, 2, 1],
        [6, 5, 4],
        [9, 8, 7]
    ]
    result = sort_above_anti_diagonal_insertion(matrix, 3)
    expected = [
        [2, 3, 1],
        [6, 5, 4],
        [9, 8, 7]
    ]
    assert result == expected

def test_sort_above_anti_diagonal_4x4():
    matrix = [
        [4, 3, 2, 1],
        [8, 7, 6, 5],
        [12, 11, 10, 9],
        [16, 15, 14, 13]
    ]
    result = sort_above_anti_diagonal_insertion(matrix, 4)
    expected = [
        [2, 3, 4, 1],
        [7, 8, 6, 5],
        [12, 11, 10, 9],
        [16, 15, 14, 13]
    ]
    assert result == expected

def test_sort_above_anti_diagonal_no_elements():
    matrix = [[5]]
    result = sort_above_anti_diagonal_insertion(matrix, 1)
    assert result == [[5]]

def test_sort_above_anti_diagonal_non_square():
    matrix = [[1, 2], [3, 4], [5, 6]]
    with pytest.raises(ValueError):
        sort_above_anti_diagonal_insertion(matrix, 3)

def test_sort_above_anti_diagonal_negative():
    matrix = [
        [-1, -3, 0],
        [2, -5, 4],
        [1, 2, 3]
    ]
    result = sort_above_anti_diagonal_insertion(matrix, 3)
    expected = [
        [-3, -1, 0],
        [2, -5, 4],
        [1, 2, 3]
    ]
    assert result == expected

