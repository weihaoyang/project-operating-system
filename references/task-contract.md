# Task contract

```yaml
task: "短句描述唯一目标"
objective_key: "由目标生成"
ownership_key: "由目标 + scope 生成"
owner: "主会话或明确代理名"
mode: "research_only | implementation | verification | operations"
scope:
  include: []
  exclude: []
acceptance:
  - "可执行的验收条件"
verification:
  commands: []
  evidence: []
  reason_for_each_gate: []
budget:
  max_workers: 3
  max_full_scans: 1
  max_retries: 2
  max_expensive_checks: 1
stop_conditions:
  - "遇到该条件就暂停并汇报，不扩展范围"
file_ownership:
  - worker: "owner"
    paths: []
status: "planned"
next_action: "下一步"
```

Keep this file short. It is a coordination contract, not a progress diary. If a check has no concrete failure mode, do not add it to `verification`.
