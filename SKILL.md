---
name: project-operating-system
description: Establish and run a low-token, evidence-driven project workflow with research-first communication, first-principles design, Occam-style simplicity, proportional validation, resumable execution, technical-debt control, local knowledge capture, and disciplined subagent coordination. Use for any new project, feature, architecture review, “继续/接手/检查进度”, difficult debugging, GitHub comparison, long-running training or data jobs, or requests to make project work more efficient and reproducible.
---

# Project Operating System

Use this skill as a lightweight project control plane. Keep one main task as coordinator, keep durable facts in project files, and use scripts for repetitive checks. The workflow itself must remain simpler than the project it governs.

## First principles and Occam rule

Before adding code, abstractions, agents, tests, or gates, state:

1. The user outcome and the invariant that must be true.
2. The smallest causal chain that can make it true.
3. The smallest experiment or check that can falsify the assumption.

Prefer the simplest design that satisfies the invariant, has one owner per contract, and can be independently verified. Do not add layers, wrappers, services, metrics, agents, or documents merely because they are considered “best practice”. Every artifact and every gate needs a concrete purpose.

Safety, security, data-integrity, clinical, financial, and production-release gates are not removed just to save time. Remove redundant or ritual checks; keep checks that catch a specific credible failure.

## Communication gate for new development

When the user asks to develop a new product, system, module, or major feature, first determine whether they explicitly asked to skip planning.

For the normal path, do this before creating project files or outputting code:

1. Restate the target and success condition in one short paragraph.
2. Perform read-only GitHub or web research on comparable open-source projects.
3. Compare architecture, dependencies, license, activity, maturity, failure modes, and reusable designs.
4. Return technical choices, proposed architecture, MVP boundary, implementation order, risks, and open decisions.
5. Stop and wait for user confirmation before scaffolding or coding.

If the user explicitly says “直接实现/跳过调研/开始改代码”, record that exception in the task contract and proceed with a bounded plan. Never silently skip the gate.

Use the browser skill or an appropriate connector for web research. Treat README claims as hypotheses: inspect source layout, dependencies, tests, releases, issues, license, and recent activity. Save a concise research report and source links after confirmation; do not repeat a completed comparison without a changed decision or new evidence.

## Mid-project adoption and resume

When entering a project that is already partly built, or when the user says “继续/接手/把这个 skill 应用到现有项目”, run `scripts/adopt_project.py --profile auto` before implementation. This is the normal entry point for large projects; it does not reset Git history, overwrite existing workflow files, rerun the full test suite, or infer that existing code is complete.

The adoption script creates a compact `docs/PROJECT_INVENTORY.json` and uses `bootstrap_project.py --mode adopt` for only missing workflow files. Read, in order: existing project rules/status/manifests/checkpoints, the inventory, recent commits/diff, targeted tests, and active jobs. Treat evidence in this order: reproducible artifacts and tests, committed code/history, project documents, then chat memory.

Classify the current state as confirmed, implemented-but-untested, partial, blocked, or unknown. Write the first real task contract around the single highest-value unresolved gap, run only the minimum reconciliation checks needed to remove uncertainty, then move the project from `adopting/needs_reconciliation` to `planned` or `implementing`. Never restart a large project from an invented “initial” state.

## State machine and durable files

Project phase must be one of:

```text
intake → researching → awaiting_confirmation → planned → implementing → verifying → completed
                                      ↘ blocked ↗
```

After confirmation, or when continuing an existing project, run `scripts/bootstrap_project.py --profile lite|standard|high-risk`. It creates only missing files and never overwrites user work. Choose the smallest profile that covers the risk:

- `lite`: `AGENTS.md`, `PROJECT_STATUS.yaml`, and `TASK_CONTRACT.md`.
- `standard`: lite plus knowledge base, architecture decisions, and evidence index.
- `high-risk`: standard plus active-worker registry, technical-debt ledger, and research index; use for production, financial, clinical, security, data-integrity, or long-running training/runtime work.

Do not upgrade a profile because it is fashionable. Upgrade only when the project crosses a risk boundary.

The files are:

- `AGENTS.md`: project rules, ownership boundaries, and proportional gates.
- `docs/PROJECT_STATUS.yaml`: objective, phase, blocker, next action, and evidence.
- `docs/TASK_CONTRACT.md`: current task scope, acceptance, stop conditions, and ownership.
- `docs/ACTIVE_WORK.jsonl`: active worker/task registry (high-risk profile).
- `docs/EVIDENCE_INDEX.jsonl`: claims linked to commands, artifacts, and hashes (standard+).
- `docs/TECH_DEBT.yaml`: open risks and temporary compromises (high-risk profile).
- `docs/KNOWLEDGE_BASE.md`: verified local and external solutions (standard+).
- `docs/ARCHITECTURE_DECISIONS.md`: short decision records and alternatives (standard+).
- `docs/research/INDEX.yaml`: links to completed research reports (high-risk profile).
- `docs/PROJECT_INVENTORY.json`: compact structural inventory created during mid-project adoption.

If equivalent authoritative files already exist, use them instead of creating duplicates. Never scaffold during research-only intake. Read the durable files, `git status`, recent relevant commits, and project checkpoints/manifests before modifying code. If state is contradictory, reconcile state first.

## Task and worker control

Every task has one owner, one bounded objective, one objective key, one ownership key, and one acceptance gate. The objective key deduplicates thinking; the ownership key protects file boundaries. Use `scripts/task_gate.py` before implementation or delegation and `scripts/worker_registry.py` when a worker starts or finishes.

Normal concurrency is at most three disjoint workers: implementation, verification, and read-only research. Reduce this to one when changing a database schema, migration, public API, model architecture, lockfile, central configuration, or shared generated artifact.

Before spawning a worker, perform the thread-sync protocol in `references/thread-sync.md`: inspect the Codex thread list when available, reconcile it with `ACTIVE_WORK.jsonl` and the task contract for the same objective or overlapping paths, then register the returned `thread_id` and `host_id`. If the thread tool is unavailable, enter degraded mode: allow at most one worker and no concurrent writers. Never claim that thread state is synchronized when it was not checked.

Worker prompts must specify objective, allowed paths, forbidden scope, acceptance command, evidence to return, budget, and a stop condition. Require the response format: conclusion, changed files, commands/results, artifact or commit hash, unresolved risks. The main task alone integrates and gives the user the final report.

Respect the task budget: default to three workers, one full scan, two retries, and one expensive check. Increase a budget only when the task contract records the concrete reason.

## Proportional validation: prevent over-testing

Do not equate more tests or more gates with higher quality. First answer: “What concrete failure does this check catch, and did the changed surface make that failure plausible?” If no, omit or defer it.

Use the minimum sufficient evidence ladder:

- Documentation-only: link/reference check and diff check.
- Isolated code change: syntax/type/lint check plus the narrow affected unit test.
- Boundary or contract change: targeted tests for both sides plus one integration smoke.
- Data, training, runtime, or release change: focused smoke, health/count/hash evidence, and only the release-critical integration check.
- Full suite, full rebuild, long matrix, or large replay: run only for release, high-risk boundary changes, explicit user request, or when focused evidence exposes a systemic risk.

Reuse prior evidence when the relevant code, dependency, input contract, and environment hash are unchanged. Do not rerun passed checks after every commentary update. A normal task should have one preflight, one focused validation, and at most one integration/release gate; document the reason before adding more. Stop after two failed retries and diagnose the failure instead of blindly repeating it.

Do not weaken mandatory safety or integrity checks. Instead, separate “implemented”, “tested”, “verified”, “promoted”, and “production-ready”; a lightweight task may stop at the level its risk justifies.

## Long-running jobs

Use one-instance lock, runtime/environment preflight, heartbeat, checkpoint, bounded batches, and a status/resume path. If a heartbeat shows a job is alive, do not start a second copy. Use `scripts/job_control.py` for generic jobs when the project has no native runner; prefer the project's native runner when it already provides these guarantees.

Start with a bounded smoke test. Record actual counts, ranges, hashes, and checkpoint state. Never represent a partial download, short training run, mock result, or placeholder as complete.

## Difficulties and local knowledge

When blocked:

1. Reproduce the smallest failing case and capture the exact error.
2. Search repository history, official documentation, high-quality GitHub issues, and working implementations.
3. Test the smallest safe fix or workaround.
4. Record the verified result with `scripts/record_knowledge.py`.

Each entry includes problem, environment, root cause or confidence, solution, verification result, source URL/commit, source type, verified date, recheck date, and tags. Separate facts from hypotheses. Do not store secrets or unnecessary logs. Search the knowledge base before starting a new external search; recheck entries after their expiry date.

## Technical-debt and evidence discipline

Record an architecture decision whenever a boundary, dependency, data contract, deployment rule, safety property, or reversible tradeoff changes. Record technical debt only when it has an owner, impact, severity, and repayment condition; do not create a debt ticket for ordinary future ideas.

Every completion claim for a material capability must have an entry in `EVIDENCE_INDEX.jsonl` pointing to a command/result, artifact, test, or hash. “The file exists” is not evidence of behavior.

## Closeout and user updates

Update the user only at meaningful state transitions: research complete, decision needed, implementation milestone, blocker, validation result, and closeout. Do not narrate every search or internal thought.

Before declaring completion, run the narrowest relevant verification, inspect the diff and Git state, confirm no unrelated files changed, update status/contracts/evidence, and report exact local/remote state. Commit or push only when authorized by the user or project rules.

If incomplete, state the exact blocker, evidence, and next recovery condition. Never leave an active task with an implicit next step.

## Bundled resources

- `scripts/bootstrap_project.py`: create the durable project workflow files without overwriting existing files.
- `scripts/adopt_project.py`: adopt a partially built project with a bounded inventory and reconciliation state.
- `scripts/task_gate.py`: check confirmation phase, duplicate task keys, and overlapping active paths.
- `scripts/worker_registry.py`: register/release workers and reject duplicate or overlapping active work.
- `scripts/job_control.py`: provide generic start/status/stop records for resumable long-running jobs.
- `scripts/record_knowledge.py`: append a structured, deduplicated solution entry.
- `scripts/workflow_check.py`: print a compact read-only workflow/Git/task health check.
- `scripts/closeout.py`: run only explicitly selected closeout checks and verify evidence paths.
- `references/task-contract.md`: concise task contract format.
- `references/research-report.md`: research-first proposal format.
- `references/validation-policy.md`: first-principles and proportional-testing decision rules.
- `references/evidence-contract.md`: evidence levels and completion-claim format.
- `references/thread-sync.md`: mandatory Codex-thread and local-registry reconciliation protocol.
