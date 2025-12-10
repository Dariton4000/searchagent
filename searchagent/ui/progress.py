"""Progress bar display for LLM processing.

This module provides a progress bar with ETA calculation using exponential
moving average for smooth, stable estimates.
"""

import time
from datetime import timedelta
from typing import Any

from ..config import config, ANSIColors, ProgressSymbols


class ProgressBarPrinter:
    """Displays a progress bar during LLM processing with ETA calculation.

    Uses exponential moving average (EMA) to smooth speed calculations and
    provide stable ETA estimates. Automatically detects new processing phases
    when progress drops significantly.

    Attributes:
        start_time: Timestamp when progress tracking started
        last_time: Timestamp of last update
        ema_speed: Exponential moving average of processing speed (units/sec)
        alpha: Smoothing factor for EMA (higher = more weight to recent values)
        last_pct: Last recorded progress percentage
        first_call: Whether this is the first progress update
    """

    def __init__(self):
        """Initialize the progress bar printer."""
        self.start_time = None
        self.last_time = None
        self.ema_speed = None  # Units per second
        self.alpha = config.progress.ema_alpha
        self.last_pct = 0
        self.first_call = True

    def update_progress(self, progress: float, _: Any) -> None:
        """Update and display the progress bar.

        Args:
            progress: Current progress value (0.0-1.0 or 0-100)
            _: Unused parameter (for compatibility with callback signature)
        """
        # Normalize progress to 0-100
        if progress <= 1.0:
            pct = progress * 100
        else:
            pct = progress

        now = time.time()

        if self.first_call:
            print()  # Newline to start
            self.first_call = False

        # Detect new processing phase: if progress dropped significantly
        # This indicates a new prompt processing started after a tool call
        if self.last_pct >= config.progress.reset_threshold and pct < 50:
            self.start_time = None
            self.last_time = None
            self.ema_speed = None
            self.last_pct = 0

        if self.start_time is None:
            if pct > 0:
                self.start_time = now
                self.last_time = now
                self.last_pct = pct
                self._render(pct)
                return
            else:
                self._render(pct)
                return

        dt = now - self.last_time

        # Update stats every update_interval or if finished
        if dt > config.progress.update_interval or pct >= 100:
            dp = pct - self.last_pct
            if dt > 0:
                speed = dp / dt
                if self.ema_speed is None:
                    self.ema_speed = speed
                else:
                    # Use exponential moving average to smooth speed calculations
                    # and avoid jitter from outliers
                    self.ema_speed = self.alpha * speed + (1 - self.alpha) * self.ema_speed

            self.last_time = now
            self.last_pct = pct
            self._render(pct)

    def _render(self, pct: float) -> None:
        """Render the progress bar to the terminal.

        Args:
            pct: Current progress percentage (0-100)
        """
        # Calculate ETA
        if self.ema_speed and self.ema_speed > 0:
            remaining = 100 - pct
            eta_seconds = remaining / self.ema_speed
            eta_str = str(timedelta(seconds=int(eta_seconds)))
        else:
            eta_str = "Calculating..."

        if self.start_time:
            elapsed = time.time() - self.start_time
        else:
            elapsed = 0
        elapsed_str = str(timedelta(seconds=int(elapsed)))

        # Build progress bar
        width = config.progress.bar_width
        filled = int(width * (pct / 100))
        bar = ProgressSymbols.FILLED * filled + ProgressSymbols.EMPTY * (width - filled)

        # Build the complete line with colors
        line = (
            f"\r{ANSIColors.CLEAR_LINE}{ANSIColors.BLUE}Processing{ANSIColors.RESET} "
            f"{ProgressSymbols.LEFT_BRACKET}{bar}{ProgressSymbols.RIGHT_BRACKET} "
            f"{pct:3.0f}% • {ANSIColors.GREEN}ETA: {eta_str}{ANSIColors.RESET} • "
            f"Elapsed: {elapsed_str}"
        )
        print(line, end="", flush=True)

    def clear(self) -> None:
        """Clear the progress bar line."""
        print(f"\r{ANSIColors.CLEAR_LINE}", end="", flush=True)
