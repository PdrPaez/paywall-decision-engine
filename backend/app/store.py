from copy import deepcopy
from datetime import UTC, datetime

from .models.domain import *


class Store:
    def __init__(self): self.reset()
    def reset(self):
        now=datetime(2026,9,11,tzinfo=UTC)
        self.subs={"user_premium":Subscription("user_premium","premium",SubState.ACTIVE,now,now.replace(day=30),version=1)}
        self.usage={}; self.opens={}; self.events={}; self.decisions={}; self.traces={}; self.event_history=[]
    def snapshot(self): return deepcopy(self)
    def restore(self, other): self.__dict__=deepcopy(other.__dict__)
store=Store()

