# Decision lifecycle

`evaluate` loads context and is read-only. `open` requires `Idempotency-Key`, checks the fingerprint, evaluates again inside the mutation path, consumes metered access once, and stores the result. A trace records only executed stages and the selected policy.

