"""enemies 包 - 导出所有敌人相关类与工厂函数"""

from enemies.base import Enemy
from enemies.bosses import (
    BOSS_REGISTRY,
    BOSS_TUNING,
    BossDanmo,
    BossHuiyuan,
    BossJianmo,
    BossYaowang,
    _deep_merge_dict,
    _merge_boss_skill,
)
from enemies.factory import create_enemy
from enemies.projectiles import AOEZone, EnemyProjectile
from enemies.types import (
    AOEEnemy,
    AOEZonerEnemy,
    ChargeEnemy,
    ChargeFeintEnemy,
    HomingEnemy,
    MeleeEnemy,
    MeleeHitRunEnemy,
    RangedBurstEnemy,
    RangedEnemy,
    SummonEnemy,
)
from enemies.utils import (
    _DEFAULT_COLORS,
    _DEFAULT_LABELS,
    APPROACH_ACTIVE,
    APPROACH_PASSIVE,
    MIN_BOSS_PREVIEW_WINDOW,
    MIN_TELEGRAPH_WINDOW,
    TYPE_COLORS,
    TYPE_LABELS,
    _cross_points,
    _danmo_flood_points,
    _effect_suffix_by_attr,
    _huiyuan_collapse_points,
    _load_enemy_config,
    _load_enemy_sprite,
    _move_entity_away,
    _move_entity_towards,
    _spawn_edge_barrage,
    _spawn_global_cross_aoe,
    _spawn_points_aoe,
    _spawn_points_particles,
    _spawn_points_preview,
    _strafe_around,
)

__all__ = [
    "APPROACH_ACTIVE",
    "APPROACH_PASSIVE",
    "BOSS_REGISTRY",
    "BOSS_TUNING",
    "MIN_BOSS_PREVIEW_WINDOW",
    "MIN_TELEGRAPH_WINDOW",
    # 常量
    "TYPE_COLORS",
    "TYPE_LABELS",
    "AOEEnemy",
    "AOEZone",
    "AOEZonerEnemy",
    "BossDanmo",
    "BossHuiyuan",
    "BossJianmo",
    # Boss
    "BossYaowang",
    "ChargeEnemy",
    "ChargeFeintEnemy",
    # 基础
    "Enemy",
    "EnemyProjectile",
    "HomingEnemy",
    # 类型
    "MeleeEnemy",
    "MeleeHitRunEnemy",
    "RangedBurstEnemy",
    "RangedEnemy",
    "SummonEnemy",
    # 工厂
    "create_enemy",
]
