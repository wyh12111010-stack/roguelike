# 回归门槛说明

## 一键执行

在项目根目录执行：

`python -m tools.regression_gate`

按范围执行：

- `python -m tools.regression_gate --scope combat`
- `python -m tools.regression_gate --scope economy`
- `python -m tools.regression_gate --scope level --runs 5 --levels 10 12 14`
- `python -m tools.regression_gate --scope full`

按改动类型执行（自动映射 scope）：

- `python -m tools.regression_gate --change-type enemy_ai`
- `python -m tools.regression_gate --change-type economy`
- `python -m tools.regression_gate --change-type levels --runs 5 --levels 10 12 14`
- `python -m tools.regression_gate --change-type release`

按预设执行（推荐）：

- `python -m tools.regression_gate --preset quick`
- `python -m tools.regression_gate --preset nightly`
- `python -m tools.regression_gate --preset audit`

PowerShell 一键入口（Windows）：

- `.\run_gate.ps1 -Preset quick`
- `.\run_gate.ps1 -Preset nightly`
- `.\run_gate.ps1 -Preset audit`
- `.\run_gate.ps1 -List`
- `.\run_gate.ps1 -Preset quick -Runs 5 -Levels "10,12"`

CMD 一键入口（Windows）：

- `run_gate.cmd quick`
- `run_gate.cmd nightly`
- `run_gate.cmd audit`
- `run_gate.cmd list`
- `run_gate.cmd quick --dry-run`
- `run_gate.cmd --change-type enemy_ai`

查看映射与计划：

- `python -m tools.regression_gate --list`
- `python -m tools.regression_gate --scope level --levels 10 12 14 --dry-run`

该命令会顺序运行：

- `tools.fairness_gate`（可读性/前摇公平性）
- `tools.phase2_gate`（数值与经济封板）
- `tools.smoke_test`（流程冒烟）
- `tools.balance_test --runs 5 --level 10/12/14`（关键关卡回归）

## 通过标准

- 所有子步骤必须输出 `[OK]` 或 `passed`
- 最终输出 `All regression gates passed.`
- 任何子步骤报错或返回非 0 即视为未过线

## Scope 说明

- `combat`：`fairness_gate + smoke_test`
- `economy`：`phase2_gate`
- `level`：仅跑 `balance_test`（可自定义 `--runs` 和 `--levels`）
- `full`：`fairness_gate + phase2_gate + smoke_test + level`

## 预设说明

- `quick`：开发中快测（`scope=combat`, `runs=3`, `levels=[10]`）
- `nightly`：收工/封板全测（`scope=full`, `runs=5`, `levels=[10,12,14]`）
- `audit`：封板审计（`scope=full` + 自动写出 `docs/ECONOMY_SNAPSHOT.md` 与 `docs/economy-history/` 时间戳快照）

可选参数：

- `--economy-archive-dir <path>`：自定义历史快照目录
- `--report-output <path>`：输出本次回归审计报告（markdown）

## change-type 映射

- `ui_text` -> `combat`
- `input_flow` -> `combat`
- `enemy_ai` -> `combat`
- `economy` -> `economy`
- `levels` -> `level`
- `release` -> `full`

## 建议使用时机

- 调整敌人行为/前摇/技能读招后
- 调整经济参数（灵石、道韵、商店价格、强化曲线）后
- 合并较大改动前，作为封板前检查

## 改动类型与最小验证集

- **只改文案/纯 UI 文本**
  - 运行：无需强制门槛（建议人工点开对应界面）
- **改输入、场景流程、战斗主循环**
  - 运行：`python -m tools.smoke_test`
- **改敌人行为、前摇、预警时长、技能节奏**
  - 运行：`python -m tools.fairness_gate` + `python -m tools.smoke_test`
- **改经济参数（灵石/道韵/商店/成长成本/强化曲线）**
  - 运行：`python -m tools.phase2_gate`
- **改关卡编排（`levels.json`）或中后期战斗压力**
  - 运行：`python -m tools.balance_test --runs 5 --level 10`
  - 运行：`python -m tools.balance_test --runs 5 --level 12`
  - 运行：`python -m tools.balance_test --runs 5 --level 14`
- **改动跨多个系统或准备封板**
  - 运行：`python -m tools.regression_gate`

## 日常建议（省时版）

- **开发中（每 1~2 个改动）**：按“最小验证集”跑对应命令
- **当日收工前**：至少跑一次 `python -m tools.regression_gate`
- **准备合并/发布前**：必须跑 `python -m tools.regression_gate`

## 快速卡片

- 见 `docs/GATE_QUICK_CARD.md`（开发中/收工前/封板前的三条固定命令）

## 经济快照

- 生成当前经济快照：
  - `python -m tools.economy_snapshot --write docs/ECONOMY_SNAPSHOT.md`
- 用途：调价后快速对比章节收入、关键消费可达性、成长边界是否偏移
