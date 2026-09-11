from ..models.domain import *


def policies(ctx):
    c,e,m=ctx["content"],ctx["entitlements"],ctx["meter"]
    out=[]
    def add(pid,match,decision=None,reason=None,meta=None): out.append(PolicyResult(pid,match,decision is not None,decision,reason,meta or {}))
    add("content_published",not c.published,Decision.DENY if not c.published else None,"content_unpublished")
    if not c.published: return out
    add("public_access",c.access_tier==Tier.PUBLIC,Decision.ALLOW if c.access_tier==Tier.PUBLIC else None,"content_public")
    if c.access_tier==Tier.PUBLIC:return out
    add("premium_entitlement","premium_content" in e["ids"] and c.access_tier==Tier.PREMIUM,Decision.ALLOW_WITH_WARNING if e["effective_state"]=="past_due" else Decision.ALLOW if "premium_content" in e["ids"] and c.access_tier==Tier.PREMIUM else None,"past_due_grace_active" if e["effective_state"]=="past_due" else "premium_entitlement_present")
    if c.access_tier==Tier.PREMIUM and "premium_content" not in e["ids"]:
        add("premium_entitlement_missing",True,Decision.PAYWALL,"premium_entitlement_missing",{"paywall_type":"premium_required"}); return out
    add("meter_bypass",m.bypassed,Decision.ALLOW if m.bypassed else None,"meter_bypassed")
    if m.remaining>0: add("meter_remaining",True,Decision.ALLOW_WITH_WARNING if e["effective_state"]=="past_due" else Decision.ALLOW,"past_due_grace_active" if e["effective_state"]=="past_due" else "meter_remaining",{"consume":not m.bypassed}); return out
    add("meter_exhausted",True,Decision.PAYWALL,"meter_exhausted",{"paywall_type":"meter_exhausted"}); return out
