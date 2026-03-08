"""Boss 调参与注册表"""


def _deep_merge_dict(base: dict, override: dict) -> dict:
    """递归合并 dict（override 覆盖 base），用于 Boss 调参。"""
    result = {}
    for k, v in base.items():
        if isinstance(v, dict):
            result[k] = dict(v)
        else:
            result[k] = v
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge_dict(result[k], v)
        else:
            result[k] = v
    return result


# Boss 一键调参位：后续调难度/手感只改这里（不改具体类逻辑）
BOSS_TUNING = {
    "segment_boss_1": {
        "skills": {
            "pounce": {"cooldown": 2.2, "dash_speed": 380},
            "claw": {"cooldown": 2.5},
            "stomp": {"cooldown": 3.0},
            "double": {"cooldown": 4.0},
            "global_cross": {"cooldown": 8.5},
        }
    },
    "segment_boss_2": {
        "skills": {
            "wave_cd": 2.5,
            "wave_cd_phase2": 2.0,
            "summon_cd": 10.0,
            "summon_limit": 2,
            "global_barrage_cd": 9.0,
        }
    },
    "segment_boss_3": {
        "skills": {
            "toxic_burst": {"cooldown": 2.2},
            "toxic_ring": {"cooldown": 3.5, "cooldown_phase2": 2.8},
            "phase2_threshold": 0.4,
            "global_flood": {"cooldown": 9.5},
        }
    },
    "final_boss": {
        "skills": {
            "dash": {"cooldown": 2.5, "cooldown_phase2": 2.0},
            "barrage": {"cooldown": 3.0, "cooldown_phase2": 2.4},
            "regen": {"cooldown": 7.0, "cooldown_phase2": 5.0, "limit": 2},
            "global_collapse": {"cooldown": 8.0, "cooldown_phase2": 6.5},
        }
    },
}


def _merge_boss_skill(boss_id: str, base_skill: dict) -> dict:
    return _deep_merge_dict(base_skill, BOSS_TUNING.get(boss_id, {}).get("skills", {}))


# Boss 注册表：boss_id -> Boss 类（首只敌人视为主 Boss）
# 在 bosses/__init__.py 中填充，避免循环导入
BOSS_REGISTRY = {}
