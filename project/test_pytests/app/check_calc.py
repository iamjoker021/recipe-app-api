from app.app import calc

# Sample Calc Test


def test_add_func():
    ans = calc.add(1, 2)
    assert ans == 3


def test_subtract_func():
    ans = calc.subtract(10, 15)
    assert ans == -5
