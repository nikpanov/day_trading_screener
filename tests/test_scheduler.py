import pytest
from unittest.mock import patch
from scheduler import is_market_open, get_dynamic_interval
import datetime
import pytz
import subprocess
import os
import sys


# === Unit tests ===

@patch("scheduler.datetime")
def test_is_market_open_true(mock_datetime):
    eastern = pytz.timezone("US/Eastern")
    mock_now  = eastern.localize(datetime.datetime(2025, 7, 7, 10, 0))
    mock_datetime.now.return_value = mock_now
    assert is_market_open() is True


@patch("scheduler.datetime")
def test_is_market_open_false(mock_datetime):
    eastern = pytz.timezone("US/Eastern")
    mock_now  = eastern.localize(datetime.datetime(2025, 7, 7, 8, 0))
    mock_datetime.now.return_value = mock_now
    assert is_market_open() is False


@patch("scheduler.datetime")
def test_dynamic_interval_morning(mock_datetime):
    eastern = pytz.timezone("US/Eastern")
    mock_now  = eastern.localize(datetime.datetime(2025, 7, 7, 9, 35))
    mock_datetime.now.return_value = mock_now
    assert get_dynamic_interval() == 15


@patch("scheduler.datetime")
def test_dynamic_interval_midday(mock_datetime):
    eastern = pytz.timezone("US/Eastern")
    mock_now  = eastern.localize(datetime.datetime(2025, 7, 7, 11, 0))
    mock_datetime.now.return_value = mock_now
    assert get_dynamic_interval() == 30


@patch("scheduler.datetime")
def test_dynamic_interval_closed(mock_datetime):
    eastern = pytz.timezone("US/Eastern")
    mock_now  = eastern.localize(datetime.datetime(2025, 7, 7, 17, 0))
    mock_datetime.now.return_value = mock_now
    assert get_dynamic_interval() is None


# === CLI test ===

def test_scheduler_test_mode_runs():
    scheduler_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scheduler.py"))
    result = subprocess.run([sys.executable, scheduler_path, "--test-mode"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "test mode" in result.stdout.lower()
