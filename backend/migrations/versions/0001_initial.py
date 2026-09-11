"""Create the normalized local persistence schema."""
from alembic import op

revision = "0001_initial"
down_revision = None

def upgrade():
    op.execute("CREATE TABLE IF NOT EXISTS subjects(subject_id TEXT PRIMARY KEY, subject_type TEXT NOT NULL, display_name TEXT NOT NULL, device_id TEXT)")
    op.execute("CREATE TABLE IF NOT EXISTS content(content_id TEXT PRIMARY KEY, slug TEXT NOT NULL, title TEXT NOT NULL, access_tier TEXT NOT NULL, published INTEGER NOT NULL, preview_percent INTEGER NOT NULL)")
    op.execute("CREATE TABLE IF NOT EXISTS plans(plan_id TEXT PRIMARY KEY, entitlements TEXT NOT NULL)")
    op.execute("CREATE TABLE IF NOT EXISTS subscriptions(subject_id TEXT PRIMARY KEY, plan TEXT NOT NULL, state TEXT NOT NULL, projection_version INTEGER NOT NULL, last_event TEXT)")
    op.execute("CREATE TABLE IF NOT EXISTS meter_consumptions(id INTEGER PRIMARY KEY AUTOINCREMENT, subject_id TEXT NOT NULL, window_start TEXT NOT NULL, created_at TEXT NOT NULL)")
    op.execute("CREATE TABLE IF NOT EXISTS idempotency_records(subject_id TEXT NOT NULL, idempotency_key TEXT NOT NULL, fingerprint TEXT NOT NULL, decision_id TEXT NOT NULL, PRIMARY KEY(subject_id,idempotency_key))")
    op.execute("CREATE TABLE IF NOT EXISTS decisions(decision_id TEXT PRIMARY KEY, trace_id TEXT NOT NULL, payload TEXT NOT NULL)")
    op.execute("CREATE TABLE IF NOT EXISTS decision_trace_steps(trace_id TEXT NOT NULL, step_index INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(trace_id,step_index))")
    op.execute("CREATE TABLE IF NOT EXISTS billing_events(event_id TEXT PRIMARY KEY, occurred_at TEXT NOT NULL, normalized_payload TEXT NOT NULL, projection_applied INTEGER NOT NULL)")

def downgrade():
    for table in ("billing_events", "decision_trace_steps", "decisions", "idempotency_records", "meter_consumptions", "subscriptions", "plans", "content", "subjects"):
        op.execute(f"DROP TABLE IF EXISTS {table}")
