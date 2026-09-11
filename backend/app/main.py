from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .billing.webhooks import process, sign
from .catalog import CONTENT, PLANS, SUBJECTS
from .clock import clock
from .decision.engine import execute
from .evaluation.run import run as run_eval
from .store import store

app=FastAPI(title="Paywall Decision Engine",version="0.1.0"); app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
class AccessIn(BaseModel): subject_id:str; content_id:str
@app.get('/health')
def health(): return {"status":"ok","sqlite":"ready","billing_provider":"mock","demo_mode":True}
@app.get('/api/subjects')
def subjects(): return list(SUBJECTS.values())
@app.get('/api/content')
def content(): return list(CONTENT.values())
@app.get('/api/plans')
def plans(): return PLANS
@app.get('/api/subjects/{sid}/subscription')
def subscription(sid:str):
    if sid not in SUBJECTS: raise HTTPException(404,"unknown_subject")
    return store.subs.get(sid,{"state":"none","plan":"free"})
@app.get('/api/subjects/{sid}/entitlements')
def entitlements(sid:str):
    if sid not in SUBJECTS: raise HTTPException(404,"unknown_subject")
    from .entitlements.resolver import resolve
    return resolve(store.subs.get(sid,__import__('app.models.domain',fromlist=['Subscription']).Subscription(sid)),clock.now())
@app.get('/api/subjects/{sid}/meter')
def meter(sid:str):
    if sid not in SUBJECTS: raise HTTPException(404,"unknown_subject")
    from .entitlements.resolver import resolve
    from .meter.service import snapshot
    from .models.domain import Subscription
    m=snapshot(SUBJECTS[sid],store,clock.now(),resolve(store.subs.get(sid,Subscription(sid)),clock.now())); return m.__dict__
def access(payload, operation, key=None):
    fp=f"{payload.subject_id}:{payload.content_id}"
    if operation=='open':
        if not key: raise HTTPException(422,"Idempotency-Key is required")
        if (payload.subject_id,key) in store.opens:
            old_fp,old=store.opens[(payload.subject_id,key)]
            if old_fp!=fp: raise HTTPException(409,"idempotency_key_conflict")
            return {**old,"idempotent":True,"consumed":False}
    try: result=execute(payload.subject_id,payload.content_id,operation,store,key)
    except KeyError as e: raise HTTPException(404,str(e))
    if operation=='open': store.opens[(payload.subject_id,key)]=(fp,result)
    return result
@app.post('/api/access/evaluate')
def evaluate(p:AccessIn): return access(p,'evaluate')
@app.post('/api/access/open')
def open_access(p:AccessIn, idempotency_key:str|None=Header(default=None,alias='Idempotency-Key')): return access(p,'open',idempotency_key)
@app.get('/api/decisions/{did}')
def decision(did:str):
    if did not in store.decisions: raise HTTPException(404,"unknown_decision")
    return store.decisions[did]
@app.get('/api/traces/{tid}')
def trace(tid:str):
    if tid not in store.traces: raise HTTPException(404,"unknown_trace")
    return store.traces[tid]
@app.post('/api/demo/reset')
def reset(): store.reset(); return {"reset":True}
@app.post('/api/evaluation/run')
def evaluation(): return run_eval()
@app.get('/api/billing/events')
def events(): return store.event_history
@app.post('/api/billing/webhooks/mock')
async def webhook(request:Request, x_mock_signature:str|None=Header(default=None)):
    body=await request.body()
    try: return process(body,x_mock_signature,store)
    except PermissionError: raise HTTPException(401,"invalid_signature")
    except ValueError as e: raise HTTPException(409,str(e))
@app.post('/api/demo/billing/{action}')
def billing_action(action:str):
    import uuid
    from datetime import timedelta
    if action not in {'start-premium','mark-past-due','recover','cancel-at-period-end','expire','send-duplicate','send-stale'}: raise HTTPException(404,'unknown_action')
    et={'start-premium':'subscription.started','mark-past-due':'subscription.past_due','recover':'subscription.recovered','cancel-at-period-end':'subscription.updated','expire':'subscription.expired'} .get(action,'subscription.updated')
    now=clock.now(); data={"event_id":str(uuid.uuid4()),"event_type":et,"provider":"mock","occurred_at":now.isoformat().replace('+00:00','Z'),"subject_id":"user_premium","plan":"premium","period_end":(now+timedelta(days=30)).isoformat().replace('+00:00','Z'),"cancel_at_period_end":action=='cancel-at-period-end'}; body=__import__('json').dumps(data).encode(); result=process(body,sign(body),store)
    if action=='send-duplicate': result=process(body,sign(body),store)
    return result
