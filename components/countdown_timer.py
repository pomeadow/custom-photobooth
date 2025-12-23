from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import QWidget


class CountdownTimer(QWidget):
    # Signal
    tick = Signal(int)
    finished = Signal()
    started = Signal(int)
    cancelled = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._is_running = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._remaining_seconds = 0

    def start(self, seconds_to_countdown: int):
        self._is_running = True
        self.seconds_to_countdown = seconds_to_countdown
        self.stop()  # Stop any existing countdown
        self._remaining_seconds = seconds_to_countdown
        self._is_running = True
        self.started.emit(seconds_to_countdown)
        self.tick.emit(self._remaining_seconds)
        self._timer.start(1000)

    def _on_tick(self):
        if self.seconds_to_countdown > 1:
            self.seconds_to_countdown -= 1
            self.tick.emit(self.seconds_to_countdown)
        else:
            # 1 sec -> 0 sec
            self.seconds_to_countdown -= 1
            # self.tick.emit(self.seconds_to_countdown)
            self._timer.stop()
            self._is_running = False
            self.finished.emit()

    def stop(self):
        if not self._is_running:
            return

        self._timer.stop()
        self._is_running = False
        self.cancelled.emit()

    @property
    def is_running(self) -> bool:
        """Check if countdown is currently running."""
        return self._is_running

    @property
    def remaining_seconds(self) -> int:
        """Get remaining seconds in countdown."""
        return self._remaining_seconds
