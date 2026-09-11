# Billing events

Mock payloads are HMAC-SHA256 signed with `MOCK_WEBHOOK_SECRET`. Valid normalized events are deduplicated by event ID. A newer occurred-at timestamp advances the projection; an older event is retained as audit history but marked stale. A collision with changed normalized content returns 409.

