from datetime import UTC, datetime


class Clock:
    def __init__(self, current: datetime | None = None): self.current = current
    def now(self) -> datetime: return self.current or datetime.now(UTC)
    def set(self, value: datetime): self.current = value.astimezone(UTC)

clock = Clock()

