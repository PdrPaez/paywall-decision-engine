import pickle
import sqlite3
from copy import deepcopy
from datetime import UTC, datetime

from .models.domain import *


class Store:
    def __init__(self):
        self.db = sqlite3.connect("paywall.db", check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS runtime_state (id INTEGER PRIMARY KEY CHECK (id=1), payload BLOB NOT NULL)")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS subjects(subject_id TEXT PRIMARY KEY, subject_type TEXT NOT NULL, display_name TEXT NOT NULL, device_id TEXT);
        CREATE TABLE IF NOT EXISTS content(content_id TEXT PRIMARY KEY, slug TEXT NOT NULL, title TEXT NOT NULL, access_tier TEXT NOT NULL, published INTEGER NOT NULL, preview_percent INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS plans(plan_id TEXT PRIMARY KEY, entitlements TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS subscriptions(subject_id TEXT PRIMARY KEY, plan TEXT NOT NULL, state TEXT NOT NULL, projection_version INTEGER NOT NULL, last_event TEXT);
        CREATE TABLE IF NOT EXISTS meter_consumptions(id INTEGER PRIMARY KEY AUTOINCREMENT, subject_id TEXT NOT NULL, window_start TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS idempotency_records(subject_id TEXT NOT NULL, idempotency_key TEXT NOT NULL, fingerprint TEXT NOT NULL, decision_id TEXT NOT NULL, PRIMARY KEY(subject_id,idempotency_key));
        CREATE TABLE IF NOT EXISTS decisions(decision_id TEXT PRIMARY KEY, trace_id TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS decision_trace_steps(trace_id TEXT NOT NULL, step_index INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(trace_id,step_index));
        CREATE TABLE IF NOT EXISTS billing_events(event_id TEXT PRIMARY KEY, occurred_at TEXT NOT NULL, normalized_payload TEXT NOT NULL, projection_applied INTEGER NOT NULL);
        """)
        self.db.commit()
        row = self.db.execute("SELECT payload FROM runtime_state WHERE id=1").fetchone()
        if row:
            self.__dict__.update(pickle.loads(row[0]))
        else:
            self.reset()
    def save(self):
        payload = {k: v for k, v in self.__dict__.items() if k != "db"}
        self.db.execute("INSERT OR REPLACE INTO runtime_state(id,payload) VALUES(1,?)", (pickle.dumps(payload),))
        from .catalog import CONTENT, PLANS, SUBJECTS
        self.db.execute("DELETE FROM subjects")
        for subject in SUBJECTS.values(): self.db.execute("INSERT INTO subjects VALUES(?,?,?,?)", (subject.subject_id, subject.subject_type, subject.display_name, subject.device_id))
        self.db.execute("DELETE FROM content")
        for item in CONTENT.values(): self.db.execute("INSERT INTO content VALUES(?,?,?,?,?,?)", (item.content_id, item.slug, item.title, item.access_tier.value, int(item.published), item.preview_percent))
        self.db.execute("DELETE FROM plans")
        for plan, entitlements in PLANS.items(): self.db.execute("INSERT INTO plans VALUES(?,?)", (plan, __import__("json").dumps(entitlements)))
        self.db.execute("DELETE FROM subscriptions")
        for sid, sub in self.subs.items(): self.db.execute("INSERT INTO subscriptions VALUES(?,?,?,?,?)", (sid, sub.plan, sub.state.value, sub.version, sub.last_event))
        self.db.execute("DELETE FROM meter_consumptions")
        for (sid, window_start), count in self.usage.items():
            for _ in range(count): self.db.execute("INSERT INTO meter_consumptions(subject_id,window_start,created_at) VALUES(?,?,?)", (sid, window_start, datetime.now(UTC).isoformat()))
        self.db.execute("DELETE FROM idempotency_records")
        for (sid, key), (fingerprint, response) in self.opens.items(): self.db.execute("INSERT INTO idempotency_records VALUES(?,?,?,?)", (sid, key, fingerprint, response["decision_id"]))
        self.db.execute("DELETE FROM decisions")
        for did, payload_json in self.decisions.items(): self.db.execute("INSERT INTO decisions VALUES(?,?,?)", (did, payload_json["trace_id"], __import__("json").dumps(payload_json, default=str)))
        self.db.execute("DELETE FROM decision_trace_steps")
        for trace_id, trace in self.traces.items():
            for index, step in enumerate(trace["steps"]): self.db.execute("INSERT INTO decision_trace_steps VALUES(?,?,?)", (trace_id, index, __import__("json").dumps(step, default=str)))
        self.db.execute("DELETE FROM billing_events")
        for event_id, event in self.events.items(): self.db.execute("INSERT INTO billing_events VALUES(?,?,?,?)", (event_id, str(event["occurred_at"]), event["normalized"], 1))
        self.db.commit()
    def reset(self):
        now=datetime(2026,9,11,tzinfo=UTC)
        self.subs={"user_premium":Subscription("user_premium","premium",SubState.ACTIVE,now,now.replace(day=30),version=1)}
        self.usage={}; self.opens={}; self.events={}; self.decisions={}; self.traces={}; self.event_history=[]
        if hasattr(self, "db"): self.save()
    def snapshot(self): return deepcopy(self)
    def restore(self, other): self.__dict__=deepcopy(other.__dict__)
store=Store()
