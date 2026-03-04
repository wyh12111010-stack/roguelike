"""
战斗可读性/公平性门槛检查
用法: python -m tools.fairness_gate
"""
import re
from pathlib import Path


MIN_WINDOW = 0.22
MIN_BOSS_WINDUP = 0.30


def _fail(msg):
    raise AssertionError(msg)


def _check_enemy_file(path: Path):
    text = path.read_text(encoding="utf-8")
    if "MIN_TELEGRAPH_WINDOW = 0.22" not in text:
        _fail("enemy.py 缺少 MIN_TELEGRAPH_WINDOW = 0.22")
    if "MIN_BOSS_PREVIEW_WINDOW = 0.22" not in text:
        _fail("enemy.py 缺少 MIN_BOSS_PREVIEW_WINDOW = 0.22")

    # 检查显式 telegraph 时长（_set_telegraph(0.xx, ...))
    for m in re.finditer(r"_set_telegraph\(\s*([0-9]+\.[0-9]+)", text):
        val = float(m.group(1))
        if val < MIN_WINDOW:
            _fail(f"_set_telegraph 时长过短: {val} < {MIN_WINDOW}")

    # 检查明确的预警触发阈值（_timer < 0.xx）
    for m in re.finditer(r"_timer\s*<\s*([0-9]+\.[0-9]+)", text):
        val = float(m.group(1))
        if val < MIN_WINDOW:
            _fail(f"预警触发窗口过短: {val} < {MIN_WINDOW}")

    # 检查全局预警区 duration=max(0.xx, ...)
    for m in re.finditer(r"duration\s*=\s*max\(\s*([0-9]+\.[0-9]+)\s*,", text):
        val = float(m.group(1))
        if val < MIN_WINDOW:
            _fail(f"全局预警区最小时长过短: {val} < {MIN_WINDOW}")

    # Boss 关键 windup 下限（避免“看见就中”）
    # 1) dict 形态: "skill": {"windup": 0.xx, ...}
    for m in re.finditer(r'"windup"\s*:\s*([0-9]+\.[0-9]+)', text):
        val = float(m.group(1))
        if val < MIN_BOSS_WINDUP:
            _fail(f"Boss skill windup 过短: {val} < {MIN_BOSS_WINDUP}")
    # 2) 扁平字段形态: "xxx_windup": 0.xx
    for m in re.finditer(r'"[a-z_]+_windup"\s*:\s*([0-9]+\.[0-9]+)', text):
        val = float(m.group(1))
        if val < MIN_BOSS_WINDUP:
            _fail(f"Boss flat windup 过短: {val} < {MIN_BOSS_WINDUP}")


def main():
    root = Path(__file__).resolve().parent.parent
    enemy_py = root / "enemy.py"
    _check_enemy_file(enemy_py)
    print("Fairness gate passed.")


if __name__ == "__main__":
    main()
