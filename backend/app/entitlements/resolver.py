from ..catalog import PLANS, effective_sub
from ..models.domain import Subscription, SubState


def resolve(subscription: Subscription, now):
    state=effective_sub(subscription,now); grants=dict(PLANS.get(subscription.plan,{})) if state in (SubState.ACTIVE,SubState.TRIALING,SubState.PAST_DUE) else {}
    reasons=[f"plan:{subscription.plan}",f"effective_state:{state.value}"]
    if subscription.state==SubState.PAST_DUE and state==SubState.PAST_DUE: reasons.append("past_due_grace_active")
    if subscription.state==SubState.TRIALING and state==SubState.TRIALING: reasons.append("trial_entitlement_active")
    return {"ids":[k for k,v in grants.items() if v],"source_plan":subscription.plan,"effective_state":state.value,"effective_until":subscription.grace_period_end or subscription.trial_end or subscription.current_period_end,"reasons":reasons}

