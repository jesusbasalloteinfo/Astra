from datetime import datetime, timezone, timedelta

class Clock:
    """
    Handles time logic.
    Calculates the current time based on an offset from the system clock.
    """
    def __init__(self):
        self.set_actual_time()

    @property
    def now(self) -> datetime:
        """Returns the current dynamic time in UTC"""
        return datetime.now(timezone.utc) + self._offset

    def set_actual_time(self):
        """
        Updates the clock to the actual time
        """
        self._offset = timedelta(seconds=0)
        self._last_sync_time = datetime.now(timezone.utc)

    def set_time(self, new_time: datetime):
        """
        Forces the clock to a specific time.
        """        
        # Convert to UTC timezone
        new_time = new_time.astimezone(timezone.utc)

        now = datetime.now(timezone.utc)
        self._offset = new_time - now
        self._last_sync_time = now

    def adjust_offset(self, latency_ms: float):
        """
        Compensates clock offset caused by latency
        """
        self._offset += timedelta(milliseconds=latency_ms)