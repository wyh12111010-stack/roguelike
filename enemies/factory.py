"""敌人工厂 - 根据 type_id 创建敌人"""

from enemies.bosses.tuning import BOSS_REGISTRY
from enemies.types.aoe import AOEEnemy, AOEZonerEnemy
from enemies.types.charge import ChargeEnemy, ChargeFeintEnemy
from enemies.types.homing import HomingEnemy
from enemies.types.melee import MeleeEnemy, MeleeHitRunEnemy
from enemies.types.ranged import RangedBurstEnemy, RangedEnemy
from enemies.types.summon import SummonEnemy


# 工厂：根据 type_id 创建敌人，支持 behavior / boss_id
def create_enemy(enemy_type, x, y, behavior=None, boss_id=None, enemy_index=0, **kwargs):
    """根据 type + behavior 创建敌人；boss_id 命中注册表时创建主 Boss。"""
    if boss_id and enemy_index == 0:
        boss_cls = BOSS_REGISTRY.get(boss_id)
        if boss_cls:
            return boss_cls(x, y, **kwargs)
    if enemy_type == "melee" and behavior == "hitrun":
        return MeleeHitRunEnemy(x, y, **kwargs)
    if enemy_type == "ranged" and behavior == "burst":
        return RangedBurstEnemy(x, y, **kwargs)
    if enemy_type == "charge" and behavior == "feint":
        return ChargeFeintEnemy(x, y, **kwargs)
    if enemy_type == "aoe" and behavior == "zoner":
        return AOEZonerEnemy(x, y, **kwargs)
    classes = {
        "melee": MeleeEnemy,
        "ranged": RangedEnemy,
        "charge": ChargeEnemy,
        "aoe": AOEEnemy,
        "homing": HomingEnemy,
        "summon": SummonEnemy,
    }
    cls = classes.get(enemy_type, MeleeEnemy)
    e = cls(x, y, **kwargs)
    if boss_id == "segment_boss_2" and enemy_index > 0:
        e._jianmo_minion = True
    if boss_id == "segment_boss_3" and enemy_index > 0:
        e._danmo_minion = True
    if boss_id == "final_boss" and enemy_index > 0:
        e._huiyuan_minion = True
    return e
