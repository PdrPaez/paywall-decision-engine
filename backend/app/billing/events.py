from dataclasses import dataclass
from datetime import datetime

EVENT_TYPES = frozenset({"subscription.started", "subscription.renewed", "subscription.updated", "subscription.past_due", "subscription.recovered", "subscription.canceled", "subscription.expired"})
@dataclass(frozen=True)
class BillingEvent:
    event_id: str
    event_type: str
    provider: str
    occurred_at: datetime
    subject_id: str
    subscription_external_id: str
    plan: str
    schema_version: int = 1
