"""
统一回归门槛脚本
用法:
  python -m tools.regression_gate --scope full
  python -m tools.regression_gate --scope combat
  python -m tools.regression_gate --change-type enemy_ai
  python -m tools.regression_gate --preset quick
  python -m tools.regression_gate --preset nightly
  python -m tools.regression_gate --preset audit
  python -m tools.regression_gate --list
  python -m tools.regression_gate --scope level --dry-run
"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import time


DEFAULT_LEVELS = [10, 12, 14]
DEFAULT_RUNS = 5
PRESET_CONFIG = {
    "quick": {"scope": "combat", "runs": 3, "levels": [10]},
    "nightly": {"scope": "full", "runs": 5, "levels": [10, 12, 14]},
    "audit": {"scope": "full", "runs": 5, "levels": [10, 12, 14]},
}
CHANGE_TYPE_TO_SCOPE = {
    "ui_text": "combat",
    "input_flow": "combat",
    "enemy_ai": "combat",
    "economy": "economy",
    "levels": "level",
    "release": "full",
}


def _run_step(name, cmd):
    started = time.perf_counter()
    print(f"\n=== {name} ===")
    ret = subprocess.run(cmd, check=False)
    elapsed = time.perf_counter() - started
    if ret.returncode != 0:
        raise SystemExit(f"[FAIL] {name} (exit_code={ret.returncode})")
    print(f"[OK] {name}")
    return elapsed


def _print_registry():
    print("Scopes: combat, economy, level, full")
    print("Presets:")
    for k, cfg in PRESET_CONFIG.items():
        print(f"  - {k} -> scope={cfg['scope']}, runs={cfg['runs']}, levels={cfg['levels']}")
    print("Change-type mapping:")
    for k, v in CHANGE_TYPE_TO_SCOPE.items():
        print(f"  - {k} -> {v}")


def _steps_for_scope(scope, runs, levels):
    level_steps = [
        (f"Balance L{lv}", [sys.executable, "-m", "tools.balance_test", "--runs", str(runs), "--level", str(lv)])
        for lv in levels
    ]
    if scope == "combat":
        return [
            ("Fairness Gate", [sys.executable, "-m", "tools.fairness_gate"]),
            ("Smoke Test", [sys.executable, "-m", "tools.smoke_test"]),
        ]
    if scope == "economy":
        return [("Phase2 Gate", [sys.executable, "-m", "tools.phase2_gate"])]
    if scope == "level":
        return level_steps
    return [
        ("Fairness Gate", [sys.executable, "-m", "tools.fairness_gate"]),
        ("Phase2 Gate", [sys.executable, "-m", "tools.phase2_gate"]),
        ("Smoke Test", [sys.executable, "-m", "tools.smoke_test"]),
        *level_steps,
    ]


def _economy_snapshot_step(output_path: str):
    return ("Economy Snapshot", [sys.executable, "-m", "tools.economy_snapshot", "--write", output_path])


def _write_report(path: str, scope: str, args, steps: list, elapsed_map: dict, started_at: datetime, finished_at: datetime):
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# 回归审计报告")
    lines.append("")
    lines.append(f"- 开始时间: `{started_at.isoformat(timespec='seconds')}`")
    lines.append(f"- 结束时间: `{finished_at.isoformat(timespec='seconds')}`")
    lines.append(f"- 预设: `{args.preset or '-'}`")
    lines.append(f"- 变更类型: `{args.change_type or '-'}`")
    lines.append(f"- scope: `{scope}`")
    lines.append(f"- runs: `{args.runs if args.runs is not None else 'preset/default'}`")
    lines.append(f"- levels: `{args.levels if args.levels is not None else 'preset/default'}`")
    lines.append("")
    lines.append("## 步骤明细")
    lines.append("")
    lines.append("| 步骤 | 命令 | 耗时(s) |")
    lines.append("|---|---|---:|")
    total = 0.0
    for name, cmd in steps:
        sec = elapsed_map.get(name, 0.0)
        total += sec
        lines.append(f"| {name} | `{' '.join(cmd)}` | {sec:.2f} |")
    lines.append("")
    lines.append(f"- 总耗时: `{total:.2f}s`")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[written] {out}")


def main():
    parser = argparse.ArgumentParser(description="统一回归门槛")
    parser.add_argument(
        "--scope",
        choices=["combat", "economy", "level", "full"],
        default=None,
        help="回归范围: combat/economy/level/full",
    )
    parser.add_argument(
        "--change-type",
        choices=list(CHANGE_TYPE_TO_SCOPE.keys()),
        default=None,
        help="按改动类型自动选择 scope",
    )
    parser.add_argument(
        "--preset",
        choices=list(PRESET_CONFIG.keys()),
        default=None,
        help="快捷预设: quick/nightly",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="仅列出可用 scope 和 change-type 映射",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅展示将要执行的步骤，不实际运行",
    )
    parser.add_argument(
        "--with-economy-snapshot",
        action="store_true",
        help="附加执行 economy_snapshot 并写入报告",
    )
    parser.add_argument(
        "--economy-output",
        type=str,
        default="docs/ECONOMY_SNAPSHOT.md",
        help="经济快照输出路径（配合 --with-economy-snapshot）",
    )
    parser.add_argument(
        "--economy-archive-dir",
        type=str,
        default="",
        help="额外写入带时间戳的历史快照目录（仅快照开启时生效）",
    )
    parser.add_argument(
        "--report-output",
        type=str,
        default="",
        help="写出本次回归审计报告（markdown）",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=None,
        help="balance_test 模拟次数（scope=level/full 时生效）",
    )
    parser.add_argument(
        "--levels",
        type=int,
        nargs="+",
        default=None,
        help="balance_test 关卡列表（scope=level/full 时生效）",
    )
    args = parser.parse_args()
    if args.list:
        _print_registry()
        return
    scope = args.scope
    runs = DEFAULT_RUNS
    levels = list(DEFAULT_LEVELS)
    if args.preset:
        cfg = PRESET_CONFIG[args.preset]
        scope = cfg["scope"]
        runs = cfg["runs"]
        levels = list(cfg["levels"])
    if args.runs is not None:
        runs = args.runs
    if args.levels is not None:
        levels = list(args.levels)
    if args.change_type:
        scope = CHANGE_TYPE_TO_SCOPE[args.change_type]
    if scope is None:
        scope = "full"

    print(f"=== Regression Gate ({scope}) ===")
    if args.preset:
        print(f"[info] preset={args.preset} -> scope={scope}, runs={runs}, levels={levels}")
    if args.change_type:
        print(f"[info] change-type={args.change_type} -> scope={scope}")
    steps = _steps_for_scope(scope, runs, levels)
    include_snapshot = args.with_economy_snapshot or (args.preset == "audit")
    report_output = args.report_output
    if (not report_output) and args.preset == "audit":
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_output = f"docs/gate-history/GATE-{stamp}.md"
    if include_snapshot:
        steps.append(_economy_snapshot_step(args.economy_output))
        archive_dir = args.economy_archive_dir
        if (not archive_dir) and args.preset == "audit":
            archive_dir = "docs/economy-history"
        if archive_dir:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            archive_path = f"{archive_dir}/ECONOMY_SNAPSHOT-{stamp}.md"
            steps.append(_economy_snapshot_step(archive_path))
    if args.dry_run:
        print("[dry-run] planned steps:")
        for name, cmd in steps:
            print(f"  - {name}: {' '.join(cmd)}")
        if report_output:
            print(f"[dry-run] report output: {report_output}")
        return
    started_at = datetime.now()
    elapsed_map = {}
    for name, cmd in steps:
        elapsed_map[name] = _run_step(name, cmd)
    finished_at = datetime.now()
    if report_output:
        _write_report(report_output, scope, args, steps, elapsed_map, started_at, finished_at)
    print("\nAll regression gates passed.")


if __name__ == "__main__":
    main()
