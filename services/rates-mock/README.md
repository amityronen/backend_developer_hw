# Rates mock

Stand-in for an external exchange-rate provider. It is an external dependency
of the catalog service: do not modify it as part of the assignment.

## Endpoints

- `GET /rates?base=ILS` - returns `{"base": "ILS", "rates": {"USD": "0.27", "EUR": "0.25"}, "as_of": "<UTC timestamp>"}`.
  Only `ILS` is accepted as base (otherwise `400`).
- `GET /health` - always instant.
- `GET /_chaos` / `POST /_chaos` - read or set the failure mode.

## Behaviour

Like most third-party APIs, it is not perfectly reliable. In the default `random` mode:

- every call takes a random 0 to 300 ms,
- about 15% of calls fail with `503` and `{"error": {"code": "upstream_unavailable", ...}}`,
- about 5% of calls stall for 30 seconds before responding.

## Chaos switch

Handy for testing your own work deterministically:

```bash
curl -X POST localhost:8003/_chaos -H 'content-type: application/json' -d '{"mode": "fail"}'
```

Modes: `random` (default), `ok` (always fast and healthy), `fail` (always 503), `hang` (always stalls 30 s).
The mode is held in memory and resets to `random` when the container restarts.
