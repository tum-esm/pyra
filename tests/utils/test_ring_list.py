import os
import sys
import pytest

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
CONFIG_DIR = os.path.join(PROJECT_DIR, "config")

sys.path.append(PROJECT_DIR)
from packages.core import utils


@pytest.mark.ci
def test_ring_list() -> None:
    ring_list = utils.RingList(4)

    # list is empty at first
    assert ring_list.get() == []
    assert ring_list.get_max_size() == 4
    assert not ring_list.is_full()

    # appending one element
    ring_list.append(23.5)
    assert ring_list.get() == [23.5]
    assert not ring_list.is_full()

    # order of appending elements
    ring_list.append(3)
    assert ring_list.get() == [23.5, 3]
    assert not ring_list.is_full()

    # number of stored elements is correct
    ring_list.append(4)
    ring_list.append(5)
    assert ring_list.get() == [23.5, 3, 4, 5]
    assert ring_list.is_full()

    # sum works
    assert ring_list.sum() == 35.5

    # overflowing works as expected
    ring_list.append(6)
    assert ring_list.get() == [3, 4, 5, 6]
    assert ring_list.is_full()

    # sum still works
    assert ring_list.sum() == 18

    # overflowing a second time
    ring_list.append(7)
    ring_list.append(8)
    ring_list.append(9)
    ring_list.append(10)
    ring_list.append(11)
    assert ring_list.get() == [8, 9, 10, 11]
    assert ring_list.is_full()

    # clearing the list
    ring_list.clear()
    assert ring_list.get() == []

    # appending after clearing
    ring_list.append(12)
    ring_list.append(13)
    ring_list.append(14)
    assert ring_list.get() == [12, 13, 14]

    # overflowing the list once more
    ring_list.append(15)
    ring_list.append(16)
    ring_list.append(17)
    assert ring_list.get() == [14, 15, 16, 17]

    # reducing the size
    ring_list.set_max_size(2)
    assert ring_list.get_max_size() == 2
    assert ring_list.get() == [16, 17]
    ring_list.append(18)
    assert ring_list.get() == [17, 18]
    assert ring_list.is_full()

    # increasing the size
    ring_list.set_max_size(6)
    assert ring_list.get() == [17, 18]
    assert not ring_list.is_full()
    ring_list.append(19)
    assert ring_list.get() == [17, 18, 19]
    ring_list.append(20)
    ring_list.append(21)
    ring_list.append(22)
    assert ring_list.get() == [17, 18, 19, 20, 21, 22]
    assert ring_list.is_full()

    # overflowing still works
    ring_list.append(23)
    assert ring_list.get() == [18, 19, 20, 21, 22, 23]
    assert ring_list.is_full()
