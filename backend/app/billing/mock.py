import json
from collections.abc import Mapping
from datetime import datetime

from .events import EVENT_TYPES, BillingEvent


class MockBillingProvider:
    name = "mock"
    def normalize_event(self, payload: bytes, headers: Mapping[str, str]) -> BillingEvent:
        data=json.loads(payload); event_type=data["event_type"]
        if event_type not in EVENT_TYPES: raise ValueError("unsupported_event_type")
        return BillingEvent(data["event_id"],event_type,data.get("provider",self.name),datetime.fromisoformat(data["occurred_at"]),data["subject_id"],data.get("subscription_external_id",f"mock:{data['subject_id']}"),data.get("plan","premium"))
