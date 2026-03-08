"""
Boss 参数合法性检查
用法: python -m tools.boss_sanity_check
"""

from enemy import BOSS_TUNING


def _assert_positive_num(name, value):
    assert isinstance(value, (int, float)), f"{name} must be numeric"
    assert value > 0, f"{name} must be > 0"


def _assert_non_negative_num(name, value):
    assert isinstance(value, (int, float)), f"{name} must be numeric"
    assert value >= 0, f"{name} must be >= 0"


def _walk_dict(prefix, data, checks):
    for k, v in data.items():
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            _walk_dict(key, v, checks)
            continue
        checks(key, v)


def run():
    # 常见参数规则：cooldown/windup/time/duration/speed/damage 必须 >0
    # limit/threshold 类型参数为 >=0（threshold 同时应 <=1）
    for boss_id, cfg in BOSS_TUNING.items():
        assert isinstance(cfg, dict), f"{boss_id} config must be dict"
        skills = cfg.get("skills", {})
        assert isinstance(skills, dict), f"{boss_id}.skills must be dict"

        def checks(key, value):
            low = key.lower()
            if any(tok in low for tok in ("cooldown", "windup", "time", "duration", "speed", "damage", "radius")):
                _assert_positive_num(key, value)
            elif "limit" in low:
                _assert_non_negative_num(key, value)
            elif "threshold" in low:
                _assert_non_negative_num(key, value)
                assert value <= 1, f"{key} should be <= 1"

        _walk_dict(boss_id, skills, checks)

    print("Boss sanity check passed.")


if __name__ == "__main__":
    run()
