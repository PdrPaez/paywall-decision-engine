from datetime import UTC, datetime

from ..catalog import LIMITS
from ..models.domain import Meter


def window(now):
    start=datetime(now.year,now.month,1,tzinfo=UTC); end=datetime(now.year+1,1,1,tzinfo=UTC) if now.month==12 else datetime(now.year,now.month+1,1,tzinfo=UTC); return start,end
def snapshot(subject, store, now, entitlements):
    ws,we=window(now); key=(subject.subject_id,ws.isoformat()); used=store.usage.get(key,0); bypass="meter_bypass" in entitlements["ids"]
    return Meter(0 if bypass else LIMITS[subject.subject_type],used,ws,we,bypass)
def consume(subject, store, now):
    ws,_=window(now); key=(subject.subject_id,ws.isoformat()); store.usage[key]=store.usage.get(key,0)+1

