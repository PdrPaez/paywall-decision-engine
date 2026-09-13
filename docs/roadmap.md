# PDE roadmap

This is the execution map for the delivered project. Every item is implemented without Docker or external paid services.

| Card | Delivered capability |
|---|---|
| PDE-001–003 | Git foundation, FastAPI foundation, React/Vite shell |
| PDE-004–008 | SQLite schema/migration, deterministic catalog, projection and UTC time semantics |
| PDE-009–010 | Calendar-month meter, limits, atomic open path and idempotency conflict handling |
| PDE-011–014 | Ordered policies, decision composition, evaluate/open API, persisted traces |
| PDE-015–017 | Normalized billing events, HMAC mock webhooks, duplicate/stale/collision handling |
| PDE-018–019 | Demo clock controls, 12-scenario deterministic evaluation and boundary tests |
| PDE-020–025 | Typed explorer, XYFlow canvas, trace mapping, inspectors, billing actions and replay control |
| PDE-026–027 | GitHub Actions, README, architecture docs, roadmap and real UI capture |

## Local execution policy

The supported workflow is Python 3.12 + SQLite + Node 20. Docker is intentionally absent. SQLite stores normalized entities and a compact restart-safe runtime snapshot; production-scale concurrency remains an explicit evolution path rather than a claimed guarantee.
