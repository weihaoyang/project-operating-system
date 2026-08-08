# Evidence contract

Use one JSON line per material completion claim in `docs/EVIDENCE_INDEX.jsonl`:

```json
{"claim":"...","status":"tested","command":"...","result":"...","artifact":"...","hash":"...","timestamp":"..."}
```

Allowed status values are `implemented`, `tested`, `verified`, `promoted`, and `production_ready`. Choose the lowest status justified by evidence. A claim is not `verified` without a reproducible command/result or a traceable artifact. A claim is not `production_ready` without the project's release and rollback evidence.
