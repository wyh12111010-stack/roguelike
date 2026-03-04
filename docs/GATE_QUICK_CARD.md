# 回归门槛操作卡

这份卡片只解决一件事：**你现在该跑哪条命令**。

## 1) 开发中（快测）

```powershell
python -m tools.regression_gate --preset quick
```

- 适用：改敌人行为、前摇、输入/流程、小范围 UI
- 目标：尽快发现明显回归

## 2) 收工前（全测）

```powershell
python -m tools.regression_gate --preset nightly
```

- 适用：当天代码准备收口
- 目标：保证当日版本可继续迭代

## 3) 封板前（发布检查）

```powershell
python -m tools.regression_gate --change-type release
```

- 适用：准备合并主线/发版本前
- 目标：通过完整门槛

## 3.5) 封板审计（含经济快照）

```powershell
python -m tools.regression_gate --preset audit
```

- 适用：需要留档本次封板时的经济状态
- 输出：自动更新 `docs/ECONOMY_SNAPSHOT.md`，并额外写入：
  - `docs/economy-history/` 时间戳快照
  - `docs/gate-history/` 回归审计报告

## 4) 只看将执行什么（不实际运行）

```powershell
python -m tools.regression_gate --preset nightly --dry-run
```

## 5) 查看所有可用映射

```powershell
python -m tools.regression_gate --list
```

## 6) 进入下一阶段前检查

```powershell
python -m tools.phase_ready_check --min-runs 3
```

- 含义：最近 3 次封板审计报告都完整通过，才建议进入内容扩张阶段

## Windows 一键入口

- PowerShell:
  - `.\run_gate.ps1 -Preset quick`
  - `.\run_gate.ps1 -Preset nightly`
  - `.\run_gate.ps1 -Preset audit`
- CMD:
  - `run_gate.cmd quick`
  - `run_gate.cmd nightly`
  - `run_gate.cmd audit`
