import pytest
import pandas as pd
from lights.schedule import _find_bounds, prepare_schedule, _find_time_proportion
# Arrange
@pytest.fixture
def schedule():
    schedule =  pd.read_csv("test_schedule.csv")
    return prepare_schedule(schedule)


def test_ranges(schedule):

    lower, upper = _find_bounds(schedule, 9.30)
    assert lower['Time'].values[0] == 7
    assert upper['Time'].values[0] == 10

    lower, upper = _find_bounds(schedule, 1)
    assert lower['Time'].values[0] == 23
    assert upper['Time'].values[0] == 5

    lower, upper = _find_bounds(schedule, 24)
    assert lower['Time'].values[0] == 23
    assert upper['Time'].values[0] == 5

    lower, upper = _find_bounds(schedule, 10)
    assert lower['Time'].values[0] == 10
    assert upper['Time'].values[0] == 10

def test_times():

    proportion = _find_time_proportion(0, 10, 5)
    assert proportion == 0.5
    proportion = _find_time_proportion(23, 1, 24)
    assert proportion == 0.5
    proportion = _find_time_proportion(22.5, 0.5, 23.5)
    assert proportion == 0.5
    proportion = _find_time_proportion(23.5, 1.5, 0.5)
    assert proportion == 0.5