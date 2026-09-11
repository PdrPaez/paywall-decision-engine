import hashlib
import hmac
import json
from datetime import datetime, timedelta

from ..config import settings
from ..models.domain import SubState

EVENT_STATES={"subscription.started":SubState.ACTIVE,"subscription.renewed":SubState.ACTIVE,"subscription.updated":SubState.ACTIVE,"subscription.past_due":SubState.PAST_DUE,"subscription.recovered":SubState.ACTIVE,"subscription.canceled":SubState.CANCELED,"subscription.expired":SubState.EXPIRED}
def sign(payload:bytes): return hmac.new(settings.webhook_secret.encode(),payload,hashlib.sha256).hexdigest()
def verify(payload,signature): return hmac.compare_digest(sign(payload),signature or "")
def process(payload,signature,store):
    if not verify(payload,signature): raise PermissionError("invalid_signature")
    data=json.loads(payload); eid=data["event_id"]; normalized=json.dumps(data,sort_keys=True)
    if eid in store.events:
        if store.events[eid]["normalized"]!=normalized: raise ValueError("event_id_collision")
        return {"event_id":eid,"accepted":True,"duplicate":True,"projection_applied":False,"reason":"duplicate_event"}
    subject=data["subject_id"]; occurred=datetime.fromisoformat(data["occurred_at"]); sub=store.subs.get(subject)
    if sub and sub.last_event and occurred < sub._occurred_at:
        store.events[eid]={"normalized":normalized,"occurred_at":occurred}; store.event_history.append(data); store.save()
        return {"event_id":eid,"accepted":True,"duplicate":False,"projection_applied":False,"reason":"stale_event"}
    if not sub:
        from ..models.domain import Subscription
        sub=Subscription(subject, data.get("plan","premium")); store.subs[subject]=sub
    sub.plan=data.get("plan",sub.plan); sub.state=EVENT_STATES[data["event_type"]]; sub.last_event=eid; sub._occurred_at=occurred; sub.version+=1
    if sub.state==SubState.PAST_DUE: sub.grace_period_end=occurred+timedelta(days=3)
    if data.get("cancel_at_period_end"): sub.cancel_at_period_end=True
    if data.get("period_end"): sub.current_period_end=datetime.fromisoformat(data["period_end"])
    store.events[eid]={"normalized":normalized,"occurred_at":occurred}; store.event_history.append(data); store.save()
    return {"event_id":eid,"accepted":True,"duplicate":False,"projection_applied":True,"reason":"projection_updated","projection_version":sub.version}
