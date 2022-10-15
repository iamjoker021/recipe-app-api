# Sample Calc Test

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.app import calc

def test_add_func():
    ans = calc.add(1, 2)
    assert ans == 3
