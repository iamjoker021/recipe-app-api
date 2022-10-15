import os
import sys
from app.app import calc

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    )

# Sample Calc Test


def test_add_func():
    ans = calc.add(1, 2)
    assert ans == 3
