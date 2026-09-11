"""Small provider boundary: providers normalize external payloads into our event vocabulary."""
from collections.abc import Mapping
from typing import Protocol

from .events import BillingEvent


class BillingProvider(Protocol):
    name: str
    def normalize_event(self, payload: bytes, headers: Mapping[str, str]) -> BillingEvent: ...
