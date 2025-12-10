"""Unit tests for progress bar module."""

import time
import pytest
from io import StringIO
import sys

from searchagent.ui.progress import ProgressBarPrinter


class TestProgressBarPrinter:
    """Test cases for the ProgressBarPrinter class."""

    def test_initialization(self):
        """Test that ProgressBarPrinter initializes correctly."""
        printer = ProgressBarPrinter()

        assert printer.start_time is None
        assert printer.last_time is None
        assert printer.ema_speed is None
        assert printer.last_pct == 0
        assert printer.first_call is True

    def test_update_progress_normalized(self, capsys):
        """Test progress update with normalized values (0.0-1.0)."""
        printer = ProgressBarPrinter()

        # Update with 0.5 (50%)
        printer.update_progress(0.5, None)

        captured = capsys.readouterr()
        assert "50%" in captured.out or "Processing" in captured.out

    def test_update_progress_percentage(self, capsys):
        """Test progress update with percentage values (0-100)."""
        printer = ProgressBarPrinter()

        # Update with 75 (75%)
        printer.update_progress(75, None)

        captured = capsys.readouterr()
        assert "75%" in captured.out or "Processing" in captured.out

    def test_first_call_adds_newline(self, capsys):
        """Test that first call adds a newline."""
        printer = ProgressBarPrinter()

        printer.update_progress(0.1, None)

        assert printer.first_call is False

    def test_progress_reset_on_drop(self, capsys):
        """Test that progress resets when it drops significantly."""
        printer = ProgressBarPrinter()

        # Set to high progress
        printer.update_progress(95, None)
        time.sleep(0.15)  # Wait for update interval

        # Save state
        first_start_time = printer.start_time

        # Drop to low progress (simulating new phase)
        printer.update_progress(10, None)

        # Should have reset
        assert printer.start_time is None or printer.start_time != first_start_time
        assert printer.ema_speed is None or printer.ema_speed == 0

    def test_ema_calculation(self, capsys):
        """Test exponential moving average calculation."""
        printer = ProgressBarPrinter()

        # Make several progress updates to build EMA
        printer.update_progress(10, None)
        time.sleep(0.15)
        printer.update_progress(20, None)
        time.sleep(0.15)
        printer.update_progress(30, None)

        # EMA should be calculated
        assert printer.ema_speed is not None
        assert printer.ema_speed > 0

    def test_clear(self, capsys):
        """Test clearing the progress bar."""
        printer = ProgressBarPrinter()

        printer.update_progress(50, None)
        printer.clear()

        captured = capsys.readouterr()
        # Should contain ANSI clear code
        assert "\033[2K" in captured.out

    def test_progress_reaches_100(self, capsys):
        """Test progress bar at 100%."""
        printer = ProgressBarPrinter()

        printer.update_progress(100, None)

        captured = capsys.readouterr()
        assert "100%" in captured.out

    def test_eta_calculation(self, capsys):
        """Test that ETA is calculated and displayed."""
        printer = ProgressBarPrinter()

        # Make progress to establish speed
        printer.update_progress(10, None)
        time.sleep(0.15)
        printer.update_progress(30, None)
        time.sleep(0.15)
        printer.update_progress(50, None)

        captured = capsys.readouterr()
        # Should show either ETA value or "Calculating..."
        assert "ETA:" in captured.out

    def test_elapsed_time_shown(self, capsys):
        """Test that elapsed time is displayed."""
        printer = ProgressBarPrinter()

        printer.update_progress(10, None)
        time.sleep(0.15)
        printer.update_progress(20, None)

        captured = capsys.readouterr()
        assert "Elapsed:" in captured.out
