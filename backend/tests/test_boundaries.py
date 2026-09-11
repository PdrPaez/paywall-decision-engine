from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.clock import clock
from app.main import app
from app.models.domain import Subscription, SubState
from app.store import store

client=TestClient(app)
def setup_function(): client.post('/api/demo/reset')
def test_evaluate_is_read_only():
    before=client.get('/api/subjects/anonymous_demo/meter').json()['used']; client.post('/api/access/evaluate',json={'subject_id':'anonymous_demo','content_id':'article_metered_1'}); assert client.get('/api/subjects/anonymous_demo/meter').json()['used']==before
def test_trial_and_grace_boundaries():
    now=datetime(2026,9,11,tzinfo=UTC); store.subs['trial_demo']=Subscription('trial_demo','premium',SubState.TRIALING,now,now+timedelta(days=2),trial_end=now+timedelta(days=1)); store.subs['grace_demo']=Subscription('grace_demo','premium',SubState.PAST_DUE,now,now+timedelta(days=4),grace_period_end=now+timedelta(days=3))
    clock.set(now+timedelta(days=1)); assert client.post('/api/access/evaluate',json={'subject_id':'trial_demo','content_id':'article_premium_1'}).json()['decision']=='paywall'; clock.set(now+timedelta(days=3)); assert client.post('/api/access/evaluate',json={'subject_id':'grace_demo','content_id':'article_premium_1'}).json()['decision']=='paywall'
def test_webhook_invalid_duplicate_and_stale():
    import json

    from app.billing.webhooks import sign
    event={'event_id':'boundary-event','event_type':'subscription.started','occurred_at':'2026-09-11T00:00:00Z','subject_id':'user_free','plan':'premium'}; body=json.dumps(event).encode(); assert client.post('/api/billing/webhooks/mock',content=body,headers={'x-mock-signature':sign(body)}).json()['projection_applied']; assert client.post('/api/billing/webhooks/mock',content=body,headers={'x-mock-signature':sign(body)}).json()['duplicate']; event['plan']='plus'; body2=json.dumps(event).encode(); assert client.post('/api/billing/webhooks/mock',content=body2,headers={'x-mock-signature':sign(body2)}).status_code==409
