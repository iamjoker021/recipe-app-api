from app.app import calc

# Sample Calc Test


def test_add_func():
    ans = calc.add(1, 2)
    assert ans == 3
