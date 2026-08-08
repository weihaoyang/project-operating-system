# Project Operating System

让 Codex 从一次性代码生成器，升级为能够研究、规划、接管、恢复、验证并持续交付项目的项目操作系统。

> 用更少的代码、更少的测试、更少的代理和更少的 token，把真正重要的事情做对、做稳、做完。

## 为什么值得使用

大项目最怕的不是代码难写，而是做到一半以后上下文断裂、代理重复扫描、多个代理互相覆盖、测试越跑越多却没有产生新证据、困难问题反复搜索，以及架构和技术债持续失控。

`project-operating-system` 把这些问题变成一套轻量、可恢复、证据驱动的工程工作流。项目做到一半时，只要再次运行一次 skill，就能读取当前状态并无缝接管，不需要重新解释背景，也不会把旧项目当成空项目。

## 开始开发之前，先做正确的选择

当你说“我要开发一个新的系统”，它不会立刻创建文件、堆技术栈、输出代码，而是先调研 GitHub 同类开源项目，检查真实代码、架构、依赖、许可证、活跃度、测试、issue 和常见坑点，最后给出：

- 技术选型；
- 系统架构；
- MVP 边界；
- 开发顺序；
- 风险与开放决策。

等用户确认之后才进入实现阶段，让项目从第一天就少走弯路。

## 核心能力

- 中途接管已有项目：读取 Git、依赖、测试、checkpoint 和现有文档，保留历史和决策，围绕最高价值缺口继续推进。
- 第一性原理与奥卡姆剃刀：先找用户结果、不变量、最短因果链和最小可证伪检查，再决定代码、抽象、代理和测试。
- 防止过度防御性编程：不堆无意义的空值判断、重复校验、静默 fallback、吞异常和为不存在需求预留的复杂抽象。
- 防止过度测试与过度门禁：根据风险执行最小充分验证；没有明确失败模式的检查默认不增加，完整测试只在确有必要时运行。
- 多代理协作控制：用 objective key 防止重复解决目标，用 ownership key 防止文件冲突，并与 Codex 线程和 worker registry 对账。
- 长任务可恢复：支持单实例锁、heartbeat、checkpoint、status、resume，避免重复启动和把半成品当完成。
- 困难问题知识沉淀：经过最小复现、官方文档/GitHub issue 检索和验证后，写入本地知识库，减少重复搜索和 token 浪费。
- 证据驱动收口：重要结论绑定命令、结果、artifact、checkpoint 或 hash，区分 `implemented`、`tested`、`verified`、`promoted` 和 `production_ready`。
- 按风险选择 profile：`lite` 适合小脚本，`standard` 适合常规应用，`high-risk` 适合交易、支付、医疗、生产、训练和数据完整性任务。

## 解决的问题

```text
上下文断裂       → 读取项目状态后无缝恢复
重复扫描与重复劳动 → inventory、objective key、知识库去重
代理互相覆盖     → ownership key、线程同步、单 owner 边界
架构越做越复杂   → 第一性原理、奥卡姆剃刀、显式决策记录
防御代码泛滥     → 每个保护逻辑都必须对应真实故障
测试和门禁膨胀   → 只保留能捕获具体失败的最小检查
长任务中断       → heartbeat、checkpoint、status、resume
完成状态模糊     → 证据索引和分级完成声明
困难问题反复搜索 → 验证后的解决方案进入本地知识库
技术债无人负责   → 记录 owner、影响、严重度和偿还条件
```

## 使用

将此 skill 安装到 Codex 的 skills 目录后，在任意项目中使用：

```text
使用 project-operating-system 接管当前项目并继续推进。
```

接管已有项目：

```powershell
python scripts/adopt_project.py --project-root <project> --profile auto
```

新项目在方案确认后初始化：

```powershell
python scripts/bootstrap_project.py --project-root <project> --project-name "Project" --profile standard
```

## 设计底线

它不会为了“最佳实践”给一个小脚本生成企业级流程，也不会为了防风险把所有代码包进保险层。安全、数据完整性、临床、金融和生产发布等真实风险仍保留必要门禁；重复、仪式化、无法解释价值的检查会被移除或延后。

> `project-operating-system`：让 Codex 既不会漏掉真正的风险，也不会为了防风险把项目做复杂。

技能规范见 [SKILL.md](SKILL.md)。本项目采用 [MIT License](LICENSE)。
