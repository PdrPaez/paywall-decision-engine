# Architecture

FastAPI owns the access application service. Typed subject, content, subscription, entitlement, and meter context feeds the deliberately ordered policy engine. Billing events enter through a provider boundary, are verified and normalized, then update the internal subscription projection. SQLite stores the normalized demo entities plus a compact runtime snapshot for restart-safe local demos. React only visualizes the returned decision and trace. Docker is not required or used.
