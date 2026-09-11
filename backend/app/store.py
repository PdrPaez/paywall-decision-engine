import pickle
import sqlite3
from copy import deepcopy
from datetime import UTC, datetime

from .models.domain import *


class Store:
    def __init__(self):
        self.db = sqlite3.connect("paywall.db", check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS runtime_state (id INTEGER PRIMARY KEY CHECK (id=1), payload BLOB NOT NULL)")
        row = self.db.execute("SELECT payload FROM runtime_state WHERE id=1").fetchone()
        if row:
            self.__dict__.update(pickle.loads(row[0]))
        else:
            self.reset()
    def save(self):
        payload = {k: v for k, v in self.__dict__.items() if k != "db"}
        self.db.execute("INSERT OR REPLACE INTO runtime_state(id,payload) VALUES(1,?)", (pickle.dumps(payload),))
        self.db.commit()
    def reset(self):
        now=datetime(2026,9,11,tzinfo=UTC)
        self.subs={"user_premium":Subscription("user_premium","premium",SubState.ACTIVE,now,now.replace(day=30),version=1)}
        self.usage={}; self.opens={}; self.events={}; self.decisions={}; self.traces={}; self.event_history=[]
        if hasattr(self, "db"): self.save()
    def snapshot(self): return deepcopy(self)
    def restore(self, other): self.__dict__=deepcopy(other.__dict__)
store=Store()
