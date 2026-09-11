import json
from datetime import UTC, datetime, timedelta

from ..clock import clock
from ..decision.engine import execute
from ..models.domain import Subscription, SubState
from ..store import Store


def run():
    clock.set(datetime(2026,9,11,tzinfo=UTC)); results=[]
    with open(__import__('pathlib').Path(__file__).with_name('scenarios.json')) as scenario_file:
        scenarios=json.load(scenario_file)
    for s in scenarios:
        st=Store(); now=clock.now()
        if s["subject"]=="trial_demo": st.subs[s["subject"]]=Subscription(s["subject"],"premium",SubState.TRIALING,now,now+timedelta(days=14),trial_end=now+timedelta(days=7))
        elif s["subject"]=="grace_demo": st.subs[s["subject"]]=Subscription(s["subject"],"premium",SubState.PAST_DUE,now,now+timedelta(days=14),grace_period_end=now+timedelta(days=3))
        elif s["subject"]=="expired_demo": st.subs[s["subject"]]=Subscription(s["subject"],"premium",SubState.PAST_DUE,now,now-timedelta(days=1),grace_period_end=now-timedelta(seconds=1))
        elif s["subject"]=="cancel_demo": st.subs[s["subject"]]=Subscription(s["subject"],"premium",SubState.ACTIVE,now,now+timedelta(days=5),cancel_at_period_end=True)
        if s.get("seed_usage"): st.usage[(s["subject"],"2026-09-01T00:00:00+00:00")]=s["seed_usage"]
        r=execute(s["subject"],s["content"],"evaluate",st); ok=r["decision"]==s["expected"] and r["reason_code"]==s["reason"]; results.append({"id":s["id"],"passed":ok,"actual":r["decision"],"reason":r["reason_code"]})
    return {"passed":all(x["passed"] for x in results),"total":len(results),"results":results}
if __name__=='__main__':
    report=run(); print(json.dumps(report,indent=2)); raise SystemExit(0 if report["passed"] else 1)
