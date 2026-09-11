from datetime import datetime

from .models.domain import *

SUBJECTS = {"anonymous_demo": Subject("anonymous_demo","anonymous","Anonymous Demo","device-demo"), "user_free": Subject("user_free","registered","Free Reader"), "user_premium": Subject("user_premium","registered","Premium Reader"), "trial_demo": Subject("trial_demo","registered","Trial Reader"), "grace_demo": Subject("grace_demo","registered","Grace Reader"), "expired_demo": Subject("expired_demo","registered","Expired Reader"), "cancel_demo": Subject("cancel_demo","registered","Cancel Reader")}
CONTENT = {"article_public": Content("article_public","welcome","Welcome to the engine",Tier.PUBLIC), "article_metered_1": Content("article_metered_1","daily-brief","Daily Brief",Tier.METERED), "article_premium_1": Content("article_premium_1","deep-dive","Premium Deep Dive",Tier.PREMIUM), "article_unpublished": Content("article_unpublished","draft","Unpublished Draft",Tier.PUBLIC,False)}
PLANS = {"free":{"meter_limit_registered":5},"plus":{"meter_bypass":True,"archive_access":True,"ad_free":True},"premium":{"meter_bypass":True,"premium_content":True,"archive_access":True,"ad_free":True}}
LIMITS={"anonymous":3,"registered":5}

def effective_sub(s: Subscription, now: datetime) -> SubState:
    if s.state == SubState.TRIALING and s.trial_end and now >= s.trial_end: return SubState.NONE
    if s.state == SubState.PAST_DUE and s.grace_period_end and now >= s.grace_period_end: return SubState.EXPIRED
    if s.cancel_at_period_end and s.current_period_end and now >= s.current_period_end: return SubState.EXPIRED
    return s.state
