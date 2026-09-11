from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class Tier(StrEnum): PUBLIC="public"; METERED="metered"; PREMIUM="premium"
class SubState(StrEnum): NONE="none"; TRIALING="trialing"; ACTIVE="active"; PAST_DUE="past_due"; CANCELED="canceled"; EXPIRED="expired"
class Decision(StrEnum): ALLOW="allow"; ALLOW_WITH_WARNING="allow_with_warning"; PREVIEW="preview"; PAYWALL="paywall"; DENY="deny"
class PaywallType(StrEnum): HARD="hard"; METER_EXHAUSTED="meter_exhausted"; PREMIUM_REQUIRED="premium_required"; SUBSCRIPTION_LAPSED="subscription_lapsed"

@dataclass
class Subject: subject_id: str; subject_type: str; display_name: str; device_id: str|None=None
@dataclass
class Content: content_id: str; slug: str; title: str; access_tier: Tier; published: bool=True; preview_percent: int=15
@dataclass
class Subscription:
    subject_id: str; plan: str="free"; state: SubState=SubState.NONE; current_period_start: datetime|None=None; current_period_end: datetime|None=None; trial_end: datetime|None=None; grace_period_end: datetime|None=None; cancel_at_period_end: bool=False; version: int=0; last_event: str|None=None
@dataclass
class Meter:
    limit: int; used: int; window_start: datetime; window_end: datetime; bypassed: bool=False
    @property
    def remaining(self): return max(self.limit - self.used, 0) if self.limit else 0
@dataclass
class PolicyResult:
    policy_id: str; matched: bool; terminal: bool; decision: Decision|None=None; reason_code: str|None=None; metadata: dict = field(default_factory=dict); duration_ms: float=0.0
