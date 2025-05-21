import pytest
from wakeup_timer.main import today_or_tomorrow as tot


def test_tot():
    assert tot((23, 45)) == (2025, 5, 21) 

print(tot((12, 5)))

if __name__ == '__main__':
    pytest.main()

