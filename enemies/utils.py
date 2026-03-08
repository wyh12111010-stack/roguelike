"""敌人模块 - 工具函数与常量"""

import math
import os

import pygame

from attribute import Attr
from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y
from particles import spawn_particles

# 敌人立绘缓存
_ENEMY_SPRITES = {}
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ASSETS_DIR = os.path.join(_SCRIPT_DIR, "assets")

# 内置默认（配置缺失时回退）
_DEFAULT_COLORS = {
    "melee": (255, 100, 100),
    "ranged": (255, 180, 80),
    "charge": (200, 80, 200),
    "aoe": (255, 100, 255),
    "homing": (100, 200, 255),
    "summon": (100, 255, 150),
}
_DEFAULT_LABELS = {
    "melee": "近战",
    "ranged": "远程",
    "charge": "突进",
    "aoe": "范围",
    "homing": "追踪",
    "summon": "召唤",
}

TYPE_COLORS = dict(_DEFAULT_COLORS)
TYPE_LABELS = dict(_DEFAULT_LABELS)


def _load_enemy_config():
    from data import load_json

    cfg = load_json("enemies.json", {})
    types = cfg.get("types", {})
    for tid, tcfg in types.items():
        if "color" in tcfg:
            c = tcfg["color"]
            TYPE_COLORS[tid] = tuple(c) if len(c) >= 3 else _DEFAULT_COLORS.get(tid, (255, 100, 100))
        if "label" in tcfg:
            TYPE_LABELS[tid] = tcfg["label"]


_load_enemy_config()


def _load_enemy_sprite(enemy_type):
    """加载敌人立绘（静态图）"""
    if enemy_type in _ENEMY_SPRITES:
        return _ENEMY_SPRITES[enemy_type]

    # 尝试敌人路径
    path = os.path.join(_ASSETS_DIR, f"enemy_{enemy_type}.png")

    # 如果是 Boss，尝试 Boss 路径
    if not os.path.exists(path):
        boss_mapping = {
            "segment_boss_1": "yaowang",
            "segment_boss_2": "jianmo",
            "segment_boss_3": "danmo",
            "final_boss": "huiyuan",
        }
        if enemy_type in boss_mapping:
            path = os.path.join(_ASSETS_DIR, f"boss_{boss_mapping[enemy_type]}.png")

    if not os.path.exists(path):
        _ENEMY_SPRITES[enemy_type] = None
        return None

    try:
        img = pygame.image.load(path).convert_alpha()
        _ENEMY_SPRITES[enemy_type] = img
        return img
    except Exception as e:
        print(f"加载敌人 {enemy_type} 失败: {e}")
        _ENEMY_SPRITES[enemy_type] = None
        return None


# 底层逻辑分类：移动倾向
APPROACH_ACTIVE = "approach"  # 主动靠近型：会主动向玩家移动
APPROACH_PASSIVE = "non_approach"  # 不主动靠近型：不主动向玩家移动（站桩/巡逻/保持距离等）

# 读招公平性底线：低于该窗口容易出现"看到就中"的不公平体感
MIN_TELEGRAPH_WINDOW = 0.22
MIN_BOSS_PREVIEW_WINDOW = 0.22


def _move_entity_towards(rect, tx, ty, speed, dt):
    dx = tx - rect.centerx
    dy = ty - rect.centery
    dist = math.hypot(dx, dy)
    if dist <= 0:
        return
    rect.x += (dx / dist) * speed * dt
    rect.y += (dy / dist) * speed * dt
    rect.clamp_ip(pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H))


def _move_entity_away(rect, tx, ty, speed, dt):
    dx = rect.centerx - tx
    dy = rect.centery - ty
    dist = math.hypot(dx, dy)
    if dist <= 0:
        return
    rect.x += (dx / dist) * speed * dt
    rect.y += (dy / dist) * speed * dt
    rect.clamp_ip(pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H))


def _strafe_around(rect, tx, ty, speed, dt, direction=1):
    dx = tx - rect.centerx
    dy = ty - rect.centery
    dist = math.hypot(dx, dy)
    if dist <= 0:
        return
    # 垂直向量实现环绕走位
    sx = -(dy / dist) * direction
    sy = (dx / dist) * direction
    rect.x += sx * speed * dt
    rect.y += sy * speed * dt
    rect.clamp_ip(pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H))


def _spawn_global_cross_aoe(ctx, damage, duration, attr=None, color=(220, 110, 90, 120), radius=54):
    """全局十字压制：中心+上下左右 5 点 AOE。"""
    points = _cross_points(include_diagonal=False)
    _spawn_points_aoe(ctx, points, radius, damage, duration, color=color, attr=attr)


def _spawn_edge_barrage(ctx, damage, speed, attr=None, color=(160, 255, 180), count=5, axis="horizontal"):
    """全局边缘齐射：支持左右或上下边缘向场内齐射。"""
    from enemies.projectiles import EnemyProjectile

    if count <= 0:
        return
    if axis == "vertical":
        step = ARENA_W / (count + 1)
        for i in range(count):
            x = ARENA_X + int((i + 1) * step)
            ctx["enemy_projectiles"].append(EnemyProjectile(x, ARENA_Y + 8, 0, speed, damage, color=color, attr=attr))
            ctx["enemy_projectiles"].append(
                EnemyProjectile(x, ARENA_Y + ARENA_H - 8, 0, -speed, damage, color=color, attr=attr)
            )
        return
    step = ARENA_H / (count + 1)
    for i in range(count):
        y = ARENA_Y + int((i + 1) * step)
        ctx["enemy_projectiles"].append(EnemyProjectile(ARENA_X + 8, y, speed, 0, damage, color=color, attr=attr))
        ctx["enemy_projectiles"].append(
            EnemyProjectile(ARENA_X + ARENA_W - 8, y, -speed, 0, damage, color=color, attr=attr)
        )


def _spawn_points_aoe(ctx, points, radius, damage, duration, color=(220, 110, 90, 120), attr=None):
    from enemies.projectiles import AOEZone

    for x, y in points:
        ctx["aoe_zones"].append(AOEZone(x, y, radius, damage, duration, color=color, attr=attr))


def _spawn_points_preview(ctx, points, radius, duration, color=(255, 230, 120, 95)):
    # 0 伤害预警区：只负责读招提示
    _spawn_points_aoe(ctx, points, radius, 0, duration, color=color, attr=Attr.NONE)


def _effect_suffix_by_attr(attr):
    if attr == Attr.FIRE:
        return "fire"
    if attr == Attr.WOOD:
        return "wood"
    if attr == Attr.EARTH:
        return "earth"
    return ""


def _spawn_points_particles(points, effect_base, attr=None):
    suffix = _effect_suffix_by_attr(attr)
    effect = f"{effect_base}_{suffix}" if suffix else effect_base
    for x, y in points:
        spawn_particles(x, y, effect)


def _cross_points(include_diagonal=False):
    cx = ARENA_X + ARENA_W // 2
    cy = ARENA_Y + ARENA_H // 2
    points = [
        (cx, cy),
        (ARENA_X + ARENA_W // 4, cy),
        (ARENA_X + ARENA_W * 3 // 4, cy),
        (cx, ARENA_Y + ARENA_H // 4),
        (cx, ARENA_Y + ARENA_H * 3 // 4),
    ]
    if include_diagonal:
        points.extend(
            [
                (ARENA_X + ARENA_W // 4, ARENA_Y + ARENA_H // 4),
                (ARENA_X + ARENA_W * 3 // 4, ARENA_Y + ARENA_H // 4),
                (ARENA_X + ARENA_W // 4, ARENA_Y + ARENA_H * 3 // 4),
                (ARENA_X + ARENA_W * 3 // 4, ARENA_Y + ARENA_H * 3 // 4),
            ]
        )
    return points


def _danmo_flood_points(phase2=False):
    cx = ARENA_X + ARENA_W // 2
    cy = ARENA_Y + ARENA_H // 2
    if not phase2:
        return [
            (ARENA_X + 26, ARENA_Y + 26),
            (ARENA_X + ARENA_W - 26, ARENA_Y + 26),
            (ARENA_X + 26, ARENA_Y + ARENA_H - 26),
            (ARENA_X + ARENA_W - 26, ARENA_Y + ARENA_H - 26),
            (cx, cy),
        ]
    return [
        (cx - 95, cy),
        (cx + 95, cy),
        (cx, cy - 95),
        (cx, cy + 95),
        (cx - 68, cy - 68),
        (cx + 68, cy - 68),
        (cx - 68, cy + 68),
        (cx + 68, cy + 68),
    ]


def _huiyuan_collapse_points(phase2=False):
    points = _cross_points(include_diagonal=False)
    points.extend(
        [
            (ARENA_X + 24, ARENA_Y + 24),
            (ARENA_X + ARENA_W - 24, ARENA_Y + 24),
            (ARENA_X + 24, ARENA_Y + ARENA_H - 24),
            (ARENA_X + ARENA_W - 24, ARENA_Y + ARENA_H - 24),
        ]
    )
    if phase2:
        points.extend(
            [
                (ARENA_X + ARENA_W // 2, ARENA_Y + 30),
                (ARENA_X + ARENA_W // 2, ARENA_Y + ARENA_H - 30),
                (ARENA_X + 30, ARENA_Y + ARENA_H // 2),
                (ARENA_X + ARENA_W - 30, ARENA_Y + ARENA_H // 2),
            ]
        )
    return points
