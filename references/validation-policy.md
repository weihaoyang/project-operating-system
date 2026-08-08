# Proportional validation policy

Use the smallest check that can falsify the changed behavior.

| Change surface | Default evidence | Escalate only when |
|---|---|---|
| Docs/config comments | link/reference check + diff check | generated output or release packaging changes |
| Isolated function | syntax/type/lint + focused unit test | public boundary or serialization changes |
| Module/API boundary | focused tests on both sides + one smoke | database, network, auth, or deployment boundary changes |
| Data/training/runtime | smoke + real counts/ranges/hashes + checkpoint/heartbeat | promotion, release, safety, or unexplained regression |
| Production/release | release-critical integration and rollback check | never replace with a broad suite without a reason |

Every additional gate must state the failure it catches. Reuse evidence when code, dependencies, input contract, environment, and relevant hashes are unchanged. Full suites and long matrices are escalation tools, not default rituals.

First-principles review questions:

- What must be true for the user outcome to hold?
- Which smallest component can violate that condition?
- What is the shortest causal test from input to outcome?
- Which abstraction or gate can be removed without weakening the invariant?
- Is the proposed complexity buying reliability, or only producing activity?
