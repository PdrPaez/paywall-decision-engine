from fastapi.testclient import TestClient

from app.main import app

client=TestClient(app)
def setup_function(): client.post('/api/demo/reset')
def test_public_does_not_consume():
    r=client.post('/api/access/open',headers={'Idempotency-Key':'a'},json={'subject_id':'anonymous_demo','content_id':'article_public'}).json(); assert r['decision']=='allow' and not r['consumed']
def test_meter_idempotency_and_conflict():
    first=client.post('/api/access/open',headers={'Idempotency-Key':'same'},json={'subject_id':'anonymous_demo','content_id':'article_metered_1'}).json(); second=client.post('/api/access/open',headers={'Idempotency-Key':'same'},json={'subject_id':'anonymous_demo','content_id':'article_metered_1'}).json(); assert first['consumed'] and second['idempotent'] and not second['consumed']; assert client.post('/api/access/open',headers={'Idempotency-Key':'same'},json={'subject_id':'anonymous_demo','content_id':'article_public'}).status_code==409
def test_premium_flow():
    assert client.post('/api/access/evaluate',json={'subject_id':'user_free','content_id':'article_premium_1'}).json()['decision']=='paywall'
    client.post('/api/demo/billing/start-premium'); assert client.post('/api/access/evaluate',json={'subject_id':'user_premium','content_id':'article_premium_1'}).json()['decision']=='allow'
def test_evaluation(): assert client.post('/api/evaluation/run').json()['passed']

