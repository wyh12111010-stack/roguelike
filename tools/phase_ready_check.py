"""
阶段就绪检查（基于 gate-history 审计报告）
用法:
  python -m tools.phase_ready_check
  python -m tools.phase_ready_check --min-runs 3
"""

from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_HISTORY_DIR = Path("docs/gate-history")


def _collect_reports(history_dir: Path) -> list[Path]:
    if not history_dir.exists():
        return []
    return sorted(history_dir.glob("GATE-*.md"))


def _report_passed(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    # regression_gate 失败时不会写出报告；若写出报告，默认要求包含总耗时行
    return "# 回归审计报告" in text and "- 总耗时:" in text


def main():
    parser = argparse.ArgumentParser(description="检查是否满足下一阶段进入条件")
    parser.add_argument("--min-runs", type=int, default=3, help="最近至少通过的审计次数")
    parser.add_argument("--history-dir", type=str, default=str(DEFAULT_HISTORY_DIR), help="审计报告目录")
    args = parser.parse_args()

    history_dir = Path(args.history_dir)
    reports = _collect_reports(history_dir)
    if len(reports) < args.min_runs:
        print(f"[NOT READY] 审计报告数量不足: {len(reports)}/{args.min_runs}")
        raise SystemExit(1)

    recent = reports[-args.min_runs :]
    failed = [p for p in recent if not _report_passed(p)]
    if failed:
        print("[NOT READY] 最近审计存在不完整报告：")
        for p in failed:
            print(f"  - {p}")
        raise SystemExit(1)

    print("[READY] 满足下一阶段进入条件")
    print(f"- 最近通过审计次数: {args.min_runs}")
    print(f"- 检查目录: {history_dir}")
    for p in recent:
        print(f"  - {p}")


if __name__ == "__main__":
    main()
