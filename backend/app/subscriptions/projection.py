from datetime import datetime, timedelta

from ..catalog import effective_sub
from ..models.domain import Subscription, SubState


def apply_projection(subscription: Subscription, event_type: str, occurred_at: datetime, plan: str = "premium") -> Subscription:
    subscription.plan=plan; subscription.state={"subscription.started":SubState.ACTIVE,"subscription.renewed":SubState.ACTIVE,"subscription.updated":SubState.ACTIVE,"subscription.past_due":SubState.PAST_DUE,"subscription.recovered":SubState.ACTIVE,"subscription.canceled":SubState.CANCELED,"subscription.expired":SubState.EXPIRED}[event_type]
    subscription.last_event=event_type; subscription.version+=1
    if subscription.state==SubState.PAST_DUE: subscription.grace_period_end=occurred_at+timedelta(days=3)
    return subscription

def effective_state(subscription: Subscription, now: datetime) -> SubState: return effective_sub(subscription, now)
