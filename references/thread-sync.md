# Thread synchronization protocol

Use this protocol immediately before and after subagent work. It is a coordination gate, not a reason to repeatedly read full transcripts.

## Before spawning

1. Read the project's task contract and calculate the objective/ownership keys.
2. If Codex thread tools are available, call `list_threads` once with the smallest useful limit. Filter by project/cwd and active status; do not read every transcript.
3. Match candidates by objective, title, cwd, task key, or clearly overlapping paths.
4. If an equivalent active thread exists, reuse or message it; do not spawn a duplicate.
5. Spawn only after the check passes. Immediately register the returned `thread_id`, `host_id`, objective key, ownership key, paths, and `sync_mode: verified` using `worker_registry.py`.

## After completion

1. Read the worker's compact result and evidence.
2. Release the local worker record with its final status.
3. If the thread tool is available, take one bounded status snapshot to confirm it is completed or waiting for attention.
4. Update the project status and evidence index. Do not repeatedly poll unchanged state.

## Degraded mode

If thread tools are unavailable, record `sync_mode: degraded`, allow at most one worker, and prohibit concurrent writers. Report the limitation in the final handoff. This is safer than inventing thread state or treating the local registry as a complete view of Codex.
