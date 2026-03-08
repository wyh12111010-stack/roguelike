"""Boss 子包 - 导出所有 Boss 类并填充注册表"""

from enemies.bosses.danmo import BossDanmo
from enemies.bosses.huiyuan import BossHuiyuan
from enemies.bosses.jianmo import BossJianmo
from enemies.bosses.tuning import BOSS_REGISTRY, BOSS_TUNING, _deep_merge_dict, _merge_boss_skill
from enemies.bosses.yaowang import BossYaowang

# 填充注册表
BOSS_REGISTRY["segment_boss_1"] = BossYaowang
BOSS_REGISTRY["segment_boss_2"] = BossJianmo
BOSS_REGISTRY["segment_boss_3"] = BossDanmo
BOSS_REGISTRY["final_boss"] = BossHuiyuan

__all__ = [
    "BOSS_REGISTRY",
    "BOSS_TUNING",
    "BossDanmo",
    "BossHuiyuan",
    "BossJianmo",
    "BossYaowang",
    "_deep_merge_dict",
    "_merge_boss_skill",
]
