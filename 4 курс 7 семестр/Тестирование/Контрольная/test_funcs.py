import pytest

from setup import get_base_test_cases
from mfuncs import fcorr

MOCKS = get_base_test_cases() + [((-1, 0, 6, 10), 1.5), ((1, -5, 6, 8), 1.5), ((10, 0, 9, -6), -5), ((11, 0, 0, 9), 15)]

@pytest.mark.parametrize("data,expected", MOCKS)
def test_fcorr_base_path(data, expected):
    assert fcorr(*data) == expected

def test_fcorr_zero_div_error():
    data = (0, 0, -9, -3)
    error = ZeroDivisionError

    with pytest.raises(error):
        fcorr(*data)
