# Project Operating System

让 Codex 从一次性代码生成器，升级为能够研究、规划、接管、恢复、验证并持续交付大型项目的项目操作系统。

大项目最怕的不是代码难写，而是做到一半以后上下文断裂、代理重复扫描、多个代理互相覆盖、测试越跑越多却没有产生新证据、困难问题反复搜索，以及架构和技术债持续失控。

`project-operating-system` 用一套轻量、可恢复、证据驱动的工作流解决这些问题。

## 核心能力

- 新项目先做 GitHub 同类项目调研，等用户确认后再写代码。
- 大项目中途可直接接管：读取 Git、依赖、测试、checkpoint 和现有文档，不重置项目状态。
- 第一性原理和奥卡姆剃刀：先找不变量和最短因果链，再决定代码、抽象、代理和测试。
- 防止过度防御性编程：不堆无意义的空值判断、重复校验、静默 fallback 和吞异常逻辑。
- 防止过度测试：按变更风险执行最小充分验证，不把完整测试套件当成默认仪式。
- objective key 防止重复解决同一目标，ownership key 防止文件冲突。
- Codex 线程与本地 worker registry 对账；工具不可用时自动进入单 worker 降级模式。
- 长任务支持单实例、heartbeat、checkpoint、status 和 resume。
- 困难问题经过最小复现、外部检索和验证后，沉淀到本地知识库。
- 重要结论绑定命令、结果、artifact、checkpoint 或 hash，区分 implemented、tested、verified、promoted 和 production_ready。
- `lite`、`standard`、`high-risk` 三档项目 profile，避免小项目被重型流程拖慢。

## 使用

把这个目录安装到 Codex 的 skills 目录，然后在项目中使用：

```text
使用 project-operating-system 接管当前项目并继续推进。
```

中途接管已有项目时，运行：

```powershell
python scripts/adopt_project.py --project-root <project> --profile auto
```

新项目确认方案后，运行：

```powershell
python scripts/bootstrap_project.py --project-root <project> --project-name "Project" --profile standard
```

完整宣传文案见 [docs/project-operating-system-promo.md](docs/project-operating-system-promo.md)。技能规范见 [SKILL.md](SKILL.md)。

## 设计原则

```text
更少的重复扫描
更少的无效测试
更少的防御性代码
更少的代理冲突
更少的上下文浪费
更清晰的架构边界
更可靠的项目恢复
更完整的证据链
```

> 让 Codex 既不会漏掉真正的风险，也不会为了防风险把项目做复杂。
