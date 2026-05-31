"""
Clock utility for managing synchronized time with offsets.
"""
from datetime import datetime, timezone, timedelta

class Clock:
    """
    Handles time logic with synchronization capabilities.

    Calculates the current time based on an offset from the system clock,
    allowing the application to synchronize its internal time with an 
    external source (like a server or GPS).
    """
    def __init__(self):
        """
        Initializes the Clock with zero offset.
        """
        self.set_actual_time()

    @property
    def now(self) -> datetime:
        """
        Returns the current dynamic time in UTC, including the offset.

        Returns:
            datetime: The current synchronized time in UTC.
        """
        return datetime.now(timezone.utc) + self._offset

    def set_actual_time(self):
        """
        Resets the clock offset to zero, matching the system time.
        """
        self._offset = timedelta(seconds=0)
        self._last_sync_time = datetime.now(timezone.utc)

    def set_time(self, new_time: datetime):
        """
        Forces the clock to a specific time by calculating a new offset.

        Args:
            new_time (datetime): The target time to synchronize with.
        """        
        # Convert to UTC timezone
        new_time = new_time.astimezone(timezone.utc)

        now = datetime.now(timezone.utc)
        self._offset = new_time - now
        self._last_sync_time = now

    def adjust_offset(self, latency_ms: float):
        """
        Adjusts the clock offset to compensate for network latency.

        Args:
            latency_ms (float): The latency in milliseconds to add to the offset.
        """
        self._offset += timedelta(milliseconds=latency_ms)
