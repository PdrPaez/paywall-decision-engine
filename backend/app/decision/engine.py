import time
import uuid

from ..catalog import CONTENT, SUBJECTS
from ..clock import clock
from ..entitlements.resolver import resolve
from ..meter.service import consume, snapshot
from ..models.domain import Decision, Subscription
from .policies import policies


def execute(subject_id,content_id,operation,store, idempotency_key=None):
    started=time.perf_counter(); subject=SUBJECTS.get(subject_id); content=CONTENT.get(content_id)
    if not subject or not content: raise KeyError("subject_or_content_not_found")
    now=clock.now(); sub=store.subs.get(subject_id)
    if not sub: sub=Subscription(subject_id)
    ent=resolve(sub,now); meter=snapshot(subject,store,now,ent); ctx={"subject":subject,"content":content,"subscription":sub,"entitlements":ent,"meter":meter}
    results=policies(ctx)
    match=next((r for r in results if r.terminal),None)
    decision=match.decision if match else Decision.DENY; reason=match.reason_code if match else "safe_default"
    consumed=False
    if operation=="open" and decision in (Decision.ALLOW,Decision.ALLOW_WITH_WARNING) and match.metadata.get("consume"):
        consume(subject,store,now); consumed=True; meter.used+=1
    did=str(uuid.uuid4()); trace_id=str(uuid.uuid4()); elapsed=round((time.perf_counter()-started)*1000,3)
    explanation={"content_public":"Public content is available.","meter_remaining":"Monthly allowance has remaining capacity.","meter_exhausted":"Monthly free article allowance is exhausted.","premium_entitlement_missing":"Premium entitlement is required.","premium_entitlement_present":"Premium entitlement grants access.","past_due_grace_active":"Access retained during the payment grace period.","content_unpublished":"This content is not published."}.get(reason, "Access was evaluated by the ordered policy set.")
    response={"decision_id":did,"decision":decision.value,"reason_code":reason,"explanation":explanation,"paywall_type":match.metadata.get("paywall_type") if match else None,"subject":{"subject_id":subject.subject_id,"subject_type":subject.subject_type},"content":{"content_id":content.content_id,"access_tier":content.access_tier.value,"title":content.title},"subscription":{"state":ent["effective_state"],"plan":sub.plan,"period_end":sub.current_period_end},"entitlements":ent["ids"],"meter":{"meter":"metered_content_monthly","limit":meter.limit,"used":meter.used-(1 if consumed else 0),"remaining":max(meter.limit-meter.used+(1 if consumed else 0),0) if meter.limit else 0,"window_start":meter.window_start,"window_end":meter.window_end,"bypassed":meter.bypassed},"consumed":consumed,"trace_id":trace_id,"duration_ms":elapsed,"policies":[r.__dict__ for r in results]}
    store.decisions[did]=response; store.traces[trace_id]={"trace_id":trace_id,"decision_id":did,"steps":[{"name":"subject_loaded"},{"name":"content_loaded"},{"name":"subscription_resolved"},{"name":"entitlements_resolved"},{"name":"meter_loaded"},{"name":"policy_evaluated","policy_id":match.policy_id if match else None,"reason_code":reason},{"name":"decision_selected","decision":decision.value}]+([{"name":"meter_consumed"}] if consumed else [])+[ {"name":"completion","duration_ms":elapsed} ]}
    return response
