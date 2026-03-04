"""敌人 - 多种攻击类型，从 data/enemies.json 加载配置。支持元素属性。"""
import math
import os
import pygame
import random

from config import ARENA_X, ARENA_Y, ARENA_W, ARENA_H, get_font, ENEMY_MAX_SPEED
from attribute import attr_from_str, Attr, ATTR_COLORS
from enemy_sprites import load_enemy_sprite
from particles import spawn_particles
from fx_audio import play_boss_cue, play_enemy_cue

# 敌人立绘缓存
_ENEMY_SPRITES = {}
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
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
APPROACH_ACTIVE = "approach"      # 主动靠近型：会主动向玩家移动
APPROACH_PASSIVE = "non_approach" # 不主动靠近型：不主动向玩家移动（站桩/巡逻/保持距离等）

# 读招公平性底线：低于该窗口容易出现“看到就中”的不公平体感
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
    if count <= 0:
        return
    if axis == "vertical":
        step = ARENA_W / (count + 1)
        for i in range(count):
            x = ARENA_X + int((i + 1) * step)
            ctx["enemy_projectiles"].append(EnemyProjectile(x, ARENA_Y + 8, 0, speed, damage, color=color, attr=attr))
            ctx["enemy_projectiles"].append(EnemyProjectile(x, ARENA_Y + ARENA_H - 8, 0, -speed, damage, color=color, attr=attr))
        return
    step = ARENA_H / (count + 1)
    for i in range(count):
        y = ARENA_Y + int((i + 1) * step)
        ctx["enemy_projectiles"].append(EnemyProjectile(ARENA_X + 8, y, speed, 0, damage, color=color, attr=attr))
        ctx["enemy_projectiles"].append(EnemyProjectile(ARENA_X + ARENA_W - 8, y, -speed, 0, damage, color=color, attr=attr))


def _spawn_points_aoe(ctx, points, radius, damage, duration, color=(220, 110, 90, 120), attr=None):
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
        points.extend([
            (ARENA_X + ARENA_W // 4, ARENA_Y + ARENA_H // 4),
            (ARENA_X + ARENA_W * 3 // 4, ARENA_Y + ARENA_H // 4),
            (ARENA_X + ARENA_W // 4, ARENA_Y + ARENA_H * 3 // 4),
            (ARENA_X + ARENA_W * 3 // 4, ARENA_Y + ARENA_H * 3 // 4),
        ])
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
        (cx - 95, cy), (cx + 95, cy), (cx, cy - 95), (cx, cy + 95),
        (cx - 68, cy - 68), (cx + 68, cy - 68), (cx - 68, cy + 68), (cx + 68, cy + 68),
    ]


def _huiyuan_collapse_points(phase2=False):
    points = _cross_points(include_diagonal=False)
    points.extend([
        (ARENA_X + 24, ARENA_Y + 24),
        (ARENA_X + ARENA_W - 24, ARENA_Y + 24),
        (ARENA_X + 24, ARENA_Y + ARENA_H - 24),
        (ARENA_X + ARENA_W - 24, ARENA_Y + ARENA_H - 24),
    ])
    if phase2:
        points.extend([
            (ARENA_X + ARENA_W // 2, ARENA_Y + 30),
            (ARENA_X + ARENA_W // 2, ARENA_Y + ARENA_H - 30),
            (ARENA_X + 30, ARENA_Y + ARENA_H // 2),
            (ARENA_X + ARENA_W - 30, ARENA_Y + ARENA_H // 2),
        ])
    return points


class EnemyProjectile:
    """敌人投射物，击中玩家，可附带元素属性"""
    def __init__(self, x, y, vx, vy, damage, radius=8, color=(255, 150, 150), homing=False, attr=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.radius = radius
        self.color = color
        self.homing = homing
        self.attr = attr_from_str(attr) if isinstance(attr, str) else (attr or Attr.NONE)
        self.dead = False
        self.age = 0
        self.lifetime = 2.0

    def update(self, dt, player):
        if self.dead:
            return
        self.age += dt
        if self.age >= self.lifetime:
            self.dead = True
            return
        if self.homing and player:
            dx = player.rect.centerx - self.x
            dy = player.rect.centery - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                speed = math.sqrt(self.vx*self.vx + self.vy*self.vy)
                self.vx = dx / dist * speed * 0.15 + self.vx * 0.85
                self.vy = dy / dist * speed * 0.15 + self.vy * 0.85
        self.x += self.vx * dt
        self.y += self.vy * dt

    def check_hit_player(self, player):
        if self.dead or not player or player.health <= 0:
            return False
        dx = player.rect.centerx - self.x
        dy = player.rect.centery - self.y
        if dx*dx + dy*dy < (self.radius + 20) ** 2:
            player.take_damage(self.damage, self.attr)
            self.dead = True
            return True
        return False

    def draw(self, screen):
        if self.dead:
            return
        # 尝试加载精灵
        sprite = load_enemy_sprite(self.ai_type)
        if sprite:
            # 绘制精灵
            w, h = sprite.get_size()
            x = int(self.x - w // 2)
            y = int(self.y - h // 2)
            screen.blit(sprite, (x, y))
        else:
            # 降级：绘制圆形
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
class AOEZone:
    """范围伤害区域，可附带元素属性"""
    def __init__(self, x, y, radius, damage, duration, color=(255, 80, 80, 100), attr=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = damage
        self.duration = duration
        self.age = 0
        self.dead = False
        self.color = color
        self.attr = attr_from_str(attr) if isinstance(attr, str) else (attr or Attr.NONE)
        self._hit = False

    def update(self, dt, player):
        self.age += dt
        if self.age >= self.duration:
            self.dead = True
            return
        if not self._hit and player and player.health > 0:
            dx = player.rect.centerx - self.x
            dy = player.rect.centery - self.y
            if dx*dx + dy*dy < self.radius ** 2:
                player.take_damage(self.damage, self.attr)
                self._hit = True

    def draw(self, screen):
        if self.dead:
            return
        alpha = int(120 * (1 - self.age / self.duration))
        s = pygame.Surface((self.radius * 2, self.radius * 2))
        s.set_alpha(alpha)
        s.fill(self.color[:3])
        screen.blit(s, (self.x - self.radius, self.y - self.radius))
        pygame.draw.circle(screen, (255, 100, 100), (int(self.x), int(self.y)), self.radius, 2)


class Enemy:
    """敌人基类"""
    approach_type = APPROACH_ACTIVE  # 子类可覆盖：主动靠近 / 不主动靠近

    def __init__(self, x, y, health=20, speed=80, damage=10, enemy_type="melee", attr=None):
        self.rect = pygame.Rect(x - 12, y - 12, 24, 24)
        self.health = health
        self.max_health = health
        self.speed = min(speed, ENEMY_MAX_SPEED)  # 保证主角始终比敌人快
        self.damage = damage
        self.dead = False
        self.enemy_type = enemy_type
        self.attr = attr_from_str(attr) if isinstance(attr, str) else (attr or Attr.NONE)
        self.attack_cooldown = 0  # 近战攻击间隔
        self._charge_timer = 0
        self._charge_dir = (0, 0)
        self._charge_speed = 0
        self._shoot_timer = 0
        self._aoe_timer = 0
        self._summon_timer = 0
        self._telegraph_until = 0
        self._telegraph_color = (255, 230, 120)
        self._move_timer = 0  # 移动效果计时器

    def update(self, dt, player, ctx):
        """ctx: {enemies, enemy_projectiles, aoe_zones}"""
        if self.dead:
            return
        
        # 更新移动计时器
        self._move_timer += dt
        
        if getattr(self, "_invulnerable_until", 0) > 0:
            self._invulnerable_until -= dt
        if self._telegraph_until > 0:
            self._telegraph_until -= dt
        # 减速
        if getattr(self, "_superconduct_slow", 0) > 0:
            self._superconduct_slow -= dt
        # 虚弱
        if getattr(self, "_weaken_until", 0) > 0:
            self._weaken_until -= dt
        # 持续伤害
        for dot in getattr(self, "_dot_list", [])[:]:
            dot["timer"] += dt
            if dot["timer"] >= dot["interval"]:
                dot["timer"] = 0
                self.health -= dot["dmg"]
                dot["ticks_left"] -= 1
                if dot["ticks_left"] <= 0:
                    self._dot_list.remove(dot)
            if self.health <= 0:
                self.dead = True
                break
        # 主动靠近型：执行向玩家移动；不主动靠近型：由子类自行处理移动
        if self.approach_type == APPROACH_ACTIVE:
            self._move_towards_player(dt, player)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def _effective_speed(self):
        """当前有效移速（减速、虚弱后）"""
        spd = self.speed
        if getattr(self, "_superconduct_slow", 0) > 0:
            pct = min(40, getattr(self, "_superconduct_slow_pct", 20)) / 100
            spd = int(spd * (1 - pct))
        if getattr(self, "_weaken_until", 0) > 0:
            pct = getattr(self, "_weaken_pct", 15) / 100
            spd = int(spd * (1 - pct))
        return spd

    def _effective_damage(self):
        """当前有效伤害（虚弱后，敌人打玩家时用）"""
        if getattr(self, "_weaken_until", 0) <= 0:
            return self.damage
        pct = getattr(self, "_weaken_pct", 15) / 100
        return max(1, int(self.damage * (1 - pct)))

    def _move_towards_player(self, dt, player):
        """主动靠近型：向玩家方向移动"""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            spd = self._effective_speed()
            self.rect.x += dx * spd * dt
            self.rect.y += dy * spd * dt

    def take_damage(self, amount, attacker_attr=None, enemies=None, self_reaction=None):
        if self.dead:
            return
        if getattr(self, "_invulnerable_until", 0) > 0:
            return
        amount = int(amount)
        if amount <= 0:
            return
        self.health -= amount
        cx, cy = self.rect.centerx, self.rect.centery
        if self.health <= 0:
            self.dead = True
            spawn_particles(cx, cy, "hit")
            return
        # 元素伤害累计（伙伴碧落解锁条件）
        if (attacker_attr and attacker_attr != Attr.NONE) or self_reaction:
            from meta import meta
            meta.total_element_damage += amount
        # 五行反应：仅自身属性（灵根+法宝 或 法宝1+法宝2），非法宝 vs 敌人
        reaction = self_reaction
        if reaction:
            from reaction_effects import emit_reaction
            emit_reaction(reaction, amount, self, (cx, cy), attacker_type="player")
        elif attacker_attr and attacker_attr != Attr.NONE:
            from attribute_effects import apply_base_attr_effect
            apply_base_attr_effect(attacker_attr, amount, self, (cx, cy), enemies or [])
            spawn_particles(cx, cy, attacker_attr.name.lower())
        else:
            spawn_particles(cx, cy, "hit")

    def draw(self, screen):
        if self.dead:
            return
        
        # 移动效果：上下晃动
        draw_rect = self.rect.copy()
        if hasattr(self, '_move_timer'):
            bob_offset = int(math.sin(self._move_timer * 10) * 2)
            draw_rect.y += bob_offset
        
        # 尝试加载立绘
        sprite = _load_enemy_sprite(self.enemy_type)
        if sprite:
            # 使用立绘
            scaled = pygame.transform.scale(sprite, (draw_rect.w, draw_rect.h))
            screen.blit(scaled, draw_rect.topleft)
        else:
            # 回退到彩色方块
            color = TYPE_COLORS.get(self.enemy_type, (255, 100, 100))
            pygame.draw.rect(screen, color, draw_rect)
        
        # Debuff 边框
        has_dot = bool(getattr(self, "_dot_list", []))
        has_slow = getattr(self, "_superconduct_slow", 0) > 0
        has_weaken = getattr(self, "_weaken_until", 0) > 0
        if has_dot:
            pygame.draw.rect(screen, (255, 100, 50), draw_rect.inflate(4, 4), 2)   # 灼烧橙
        if has_slow:
            pygame.draw.rect(screen, (100, 180, 255), draw_rect.inflate(6, 6), 1)   # 减速蓝
        if has_weaken:
            pygame.draw.rect(screen, (180, 100, 180), draw_rect.inflate(8, 8), 1)  # 虚弱紫
        if self._telegraph_until > 0:
            # 普通敌人读招提示：浅色外框，便于观察下一拍动作
            pygame.draw.rect(screen, self._telegraph_color, draw_rect.inflate(10, 10), 2)
        # 阶段切换/技能无敌提示（Boss 可复用）
        if getattr(self, "_invulnerable_until", 0) > 0:
            pygame.draw.rect(screen, (255, 220, 120), draw_rect.inflate(12, 12), 2)
        # 类型标签
        from config import get_font_small, COLOR_TEXT_HEADING
        font = get_font_small()
        label = TYPE_LABELS.get(self.enemy_type, "?")
        txt = font.render(label, True, COLOR_TEXT_HEADING)
        t_rect = txt.get_rect(center=(draw_rect.centerx, draw_rect.y - 12))
        screen.blit(txt, t_rect)
        # 血条
        if self.health < self.max_health:
            bar_w, bar_h = 24, 4
            pygame.draw.rect(screen, (50, 50, 50), (draw_rect.x, draw_rect.y - 8, bar_w, bar_h))
            pygame.draw.rect(screen, (255, 0, 0), (draw_rect.x, draw_rect.y - 8, bar_w * self.health / self.max_health, bar_h))

    def _set_telegraph(self, duration=MIN_TELEGRAPH_WINDOW, color=(255, 230, 120)):
        d = max(MIN_TELEGRAPH_WINDOW, duration)
        self._telegraph_until = max(self._telegraph_until, d)
        self._telegraph_color = color


class MeleeEnemy(Enemy):
    """近战型（主动靠近）：追击，接触造成伤害（带冷却）"""
    approach_type = APPROACH_ACTIVE

    def __init__(self, x, y, health=25, speed=90, damage=12, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "melee", attr)
        self._melee_hit_cooldown = 0.8

    def update(self, dt, player, ctx):
        super().update(dt, player, ctx)
        if self.attack_cooldown <= 0 and self.rect.colliderect(player.rect):
            player.take_damage(self._effective_damage(), self.attr)
            self.attack_cooldown = self._melee_hit_cooldown


class MeleeHitRunEnemy(Enemy):
    """近战打带跑：接近→攻击一次→后撤→再接近"""
    approach_type = APPROACH_PASSIVE  # 不交给基类移动，自行处理

    def __init__(self, x, y, health=22, speed=95, damage=11, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "melee", attr)
        self._melee_hit_cooldown = 0.7
        self._retreat_duration = 1.2   # 攻击后后撤时长
        self._retreat_until = 0        # 后撤剩余时间

    def update(self, dt, player, ctx):
        super().update(dt, player, ctx)
        if self.dead:
            return
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx*dx + dy*dy)
        spd = self._effective_speed()

        if self._retreat_until > 0:
            self._retreat_until -= dt
            if dist > 0:
                self.rect.x -= (dx / dist) * spd * dt
                self.rect.y -= (dy / dist) * spd * dt
        else:
            if dist > 0:
                self.rect.x += (dx / dist) * spd * dt
                self.rect.y += (dy / dist) * spd * dt
            if self.rect.colliderect(player.rect) and self.attack_cooldown <= 0:
                player.take_damage(self._effective_damage(), self.attr)
                self.attack_cooldown = self._melee_hit_cooldown
                self._retreat_until = self._retreat_duration


class RangedEnemy(Enemy):
    """远程型（不主动靠近）：保持距离，发射直线弹"""
    approach_type = APPROACH_PASSIVE

    def __init__(self, x, y, health=18, speed=60, damage=10, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "ranged", attr)
        self.keep_dist = 150
        self._shoot_interval = 1.2
        self._shoot_timer = 0.5
        self._proj_speed = 250
        self._pre_shot_warned = False

    def _fire_towards_player(self, player, ctx, spread_deg=0):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= 0:
            return
        ang = math.atan2(dy, dx) + math.radians(spread_deg)
        vx = math.cos(ang) * self._proj_speed
        vy = math.sin(ang) * self._proj_speed
        ctx["enemy_projectiles"].append(EnemyProjectile(
            self.rect.centerx, self.rect.centery, vx, vy, self._effective_damage(),
            color=(255, 180, 80), attr=self.attr
        ))

    def update(self, dt, player, ctx):
        super().update(dt, player, ctx)  # 仅处理 attack_cooldown 等
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            spd = self._effective_speed()
            if dist < self.keep_dist:
                self.rect.x -= dx * spd * dt
                self.rect.y -= dy * spd * dt
            elif dist > self.keep_dist + 30:
                self.rect.x += dx * spd * dt
                self.rect.y += dy * spd * dt
        self._shoot_timer -= dt
        if self._shoot_timer > 0 and self._shoot_timer < 0.28 and not self._pre_shot_warned:
            self._set_telegraph(0.22, (255, 205, 140))
            play_enemy_cue(self.attr, "warn")
            self._pre_shot_warned = True
        if self._shoot_timer <= 0:
            self._shoot_timer = self._shoot_interval
            self._pre_shot_warned = False
            play_enemy_cue(self.attr, "cast")
            self._fire_towards_player(player, ctx)


class RangedBurstEnemy(RangedEnemy):
    """远程压制：周期性三连发，制造更明显弹幕窗口。"""
    approach_type = APPROACH_PASSIVE

    def __init__(self, x, y, health=18, speed=62, damage=9, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, attr, **kwargs)
        self.keep_dist = 165
        self._shoot_interval = 1.8
        self._shoot_timer = 0.8
        self._burst_left = 0
        self._burst_gap = 0.26
        self._proj_speed = 235
        self._pre_burst_warned = False

    def update(self, dt, player, ctx):
        super(RangedEnemy, self).update(dt, player, ctx)
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            spd = self._effective_speed()
            if dist < self.keep_dist:
                self.rect.x -= dx * spd * dt
                self.rect.y -= dy * spd * dt
            elif dist > self.keep_dist + 35:
                self.rect.x += dx * spd * dt
                self.rect.y += dy * spd * dt
            else:
                _strafe_around(self.rect, player.rect.centerx, player.rect.centery, spd * 0.6, dt, 1 if int(self._shoot_timer * 10) % 2 == 0 else -1)
        self._shoot_timer -= dt
        if self._shoot_timer > 0:
            if self._burst_left <= 0 and self._shoot_timer < 0.3 and not self._pre_burst_warned:
                self._set_telegraph(0.24, (255, 210, 130))
                play_enemy_cue(self.attr, "warn")
                self._pre_burst_warned = True
            return
        if self._burst_left <= 0:
            self._burst_left = 3
            self._pre_burst_warned = False
        spread = (-9, 0, 9)[3 - self._burst_left]
        play_enemy_cue(self.attr, "cast")
        self._fire_towards_player(player, ctx, spread_deg=spread)
        self._burst_left -= 1
        self._shoot_timer = self._burst_gap if self._burst_left > 0 else self._shoot_interval


class ChargeEnemy(Enemy):
    """突进型（主动靠近）：蓄力后冲刺向玩家"""
    approach_type = APPROACH_ACTIVE

    def __init__(self, x, y, health=22, speed=70, damage=18, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "charge", attr)
        self._charge_cooldown = 2.0
        self._charge_timer = 1.0
        self._charging = False
        self._charge_duration = 0.3
        self._charge_age = 0
        self._charge_speed = 400
        self._pre_charge_warned = False

    def update(self, dt, player, ctx):
        if self._charging:
            self._charge_age += dt
            self.rect.x += self._charge_dir[0] * self._charge_speed * dt
            self.rect.y += self._charge_dir[1] * self._charge_speed * dt
            if self._charge_age >= self._charge_duration:
                self._charging = False
                self._charge_timer = self._charge_cooldown
            if self.rect.colliderect(player.rect):
                player.take_damage(self._effective_damage(), self.attr)
                self._charging = False
                self._charge_timer = self._charge_cooldown
            return
        super().update(dt, player, ctx)
        self._charge_timer -= dt
        if self._charge_timer > 0 and self._charge_timer < 0.28 and not self._pre_charge_warned:
            self._set_telegraph(0.22, (255, 175, 145))
            play_enemy_cue(self.attr, "warn")
            self._pre_charge_warned = True
        if self._charge_timer <= 0:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                self._charge_dir = (dx / dist, dy / dist)
                self._charging = True
                self._charge_age = 0
                self._pre_charge_warned = False
                play_enemy_cue(self.attr, "cast")


class ChargeFeintEnemy(ChargeEnemy):
    """突进骗位：短暂横移假动作后再真冲。"""
    approach_type = APPROACH_ACTIVE

    def __init__(self, x, y, health=24, speed=72, damage=18, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, attr, **kwargs)
        self._feinting = False
        self._feint_time = 0.2
        self._feint_timer = 0
        self._feint_dir = (0, 0)
        self._charge_cooldown = 2.35
        self._charge_timer = 1.0
        self._pre_charge_warned = False

    def update(self, dt, player, ctx):
        if self._charging:
            return super().update(dt, player, ctx)
        super(ChargeEnemy, self).update(dt, player, ctx)
        if self._feinting:
            self._feint_timer -= dt
            self.rect.x += self._feint_dir[0] * self._effective_speed() * 1.25 * dt
            self.rect.y += self._feint_dir[1] * self._effective_speed() * 1.25 * dt
            self.rect.clamp_ip(pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H))
            if self._feint_timer <= 0:
                self._feinting = False
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    self._charge_dir = (dx / dist, dy / dist)
                    self._charging = True
                    self._charge_age = 0
                else:
                    self._charge_timer = self._charge_cooldown
            return
        self._charge_timer -= dt
        if self._charge_timer > 0:
            if self._charge_timer < 0.3 and not self._pre_charge_warned:
                self._set_telegraph(0.24, (255, 170, 135))
                play_enemy_cue(self.attr, "warn")
                self._pre_charge_warned = True
            return
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= 0:
            self._charge_timer = self._charge_cooldown
            return
        ndx = dx / dist
        ndy = dy / dist
        self._feint_dir = (-ndy, ndx) if (int(self.rect.centerx + self.rect.centery) % 2 == 0) else (ndy, -ndx)
        self._feinting = True
        self._feint_timer = self._feint_time
        play_enemy_cue(self.attr, "cast")
        self._pre_charge_warned = False


class AOEEnemy(Enemy):
    """范围型（主动靠近）：在玩家位置释放 AOE"""
    approach_type = APPROACH_ACTIVE

    def __init__(self, x, y, health=20, speed=50, damage=15, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "aoe", attr)
        self._aoe_interval = 2.5
        self._aoe_timer = 1.0
        self._pre_aoe_warned = False

    def update(self, dt, player, ctx):
        super().update(dt, player, ctx)
        self._aoe_timer -= dt
        if self._aoe_timer > 0 and self._aoe_timer < 0.3 and not self._pre_aoe_warned:
            self._set_telegraph(0.24, (195, 235, 175))
            play_enemy_cue(self.attr, "warn")
            self._pre_aoe_warned = True
        if self._aoe_timer <= 0:
            self._aoe_timer = self._aoe_interval
            self._pre_aoe_warned = False
            play_enemy_cue(self.attr, "cast")
            ctx["aoe_zones"].append(AOEZone(
                player.rect.centerx, player.rect.centery,
                60, self._effective_damage(), 0.5, attr=self.attr
            ))


class AOEZonerEnemy(AOEEnemy):
    """范围封路：中距离绕圈，双点位落区切路线。"""
    approach_type = APPROACH_PASSIVE

    def __init__(self, x, y, health=21, speed=58, damage=14, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, attr, **kwargs)
        self._aoe_interval = 3.1
        self._aoe_timer = 1.1
        self.keep_dist = 150
        self._strafe_dir = 1
        self._strafe_timer = 1.0
        self._pre_zone_warned = False

    def update(self, dt, player, ctx):
        super(AOEEnemy, self).update(dt, player, ctx)
        dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        self._strafe_timer -= dt
        if self._strafe_timer <= 0:
            self._strafe_timer = 1.0
            self._strafe_dir *= -1
        spd = self._effective_speed()
        if dist < self.keep_dist - 25:
            _move_entity_away(self.rect, player.rect.centerx, player.rect.centery, spd, dt)
        elif dist > self.keep_dist + 35:
            _move_entity_towards(self.rect, player.rect.centerx, player.rect.centery, spd * 0.9, dt)
        else:
            _strafe_around(self.rect, player.rect.centerx, player.rect.centery, spd * 0.75, dt, self._strafe_dir)
        self._aoe_timer -= dt
        if self._aoe_timer < 0.32 and not self._pre_zone_warned:
            self._set_telegraph(0.26, (185, 240, 170))
            play_enemy_cue(self.attr, "warn")
            self._pre_zone_warned = True
        if self._aoe_timer <= 0:
            self._aoe_timer = self._aoe_interval
            self._pre_zone_warned = False
            play_enemy_cue(self.attr, "cast")
            mx = (self.rect.centerx + player.rect.centerx) // 2
            my = (self.rect.centery + player.rect.centery) // 2
            ctx["aoe_zones"].append(AOEZone(player.rect.centerx, player.rect.centery, 52, self._effective_damage(), 0.42, attr=self.attr))
            ctx["aoe_zones"].append(AOEZone(mx, my, 48, max(1, int(self._effective_damage() * 0.75)), 0.42, attr=self.attr))


class HomingEnemy(Enemy):
    """追踪型（主动靠近）：发射追踪弹"""
    approach_type = APPROACH_ACTIVE

    def __init__(self, x, y, health=18, speed=65, damage=8, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "homing", attr)
        self._shoot_interval = 1.5
        self._shoot_timer = 0.8
        self._pre_shot_warned = False

    def update(self, dt, player, ctx):
        super().update(dt, player, ctx)
        self._shoot_timer -= dt
        if self._shoot_timer > 0 and self._shoot_timer < 0.3 and not self._pre_shot_warned:
            self._set_telegraph(0.22, (165, 220, 255))
            play_enemy_cue(self.attr, "warn")
            self._pre_shot_warned = True
        if self._shoot_timer <= 0:
            self._shoot_timer = self._shoot_interval
            self._pre_shot_warned = False
            play_enemy_cue(self.attr, "cast")
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                vx = dx / dist * 180
                vy = dy / dist * 180
                ctx["enemy_projectiles"].append(EnemyProjectile(
                    self.rect.centerx, self.rect.centery, vx, vy, self._effective_damage(),
                    color=(100, 200, 255), homing=True, attr=self.attr
                ))


class SummonEnemy(Enemy):
    """召唤型（主动靠近）：召唤近战小怪"""
    approach_type = APPROACH_ACTIVE

    def __init__(self, x, y, health=30, speed=40, damage=5, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "summon", attr)
        self._summon_interval = 3.0
        self._summon_timer = 1.5
        self._pre_summon_warned = False

    def update(self, dt, player, ctx):
        super().update(dt, player, ctx)
        self._summon_timer -= dt
        if self._summon_timer > 0 and self._summon_timer < 0.35 and not self._pre_summon_warned:
            self._set_telegraph(0.24, (180, 250, 170))
            play_enemy_cue(self.attr, "warn")
            self._pre_summon_warned = True
        if self._summon_timer <= 0:
            self._summon_timer = self._summon_interval
            self._pre_summon_warned = False
            play_enemy_cue(self.attr, "cast")
            offset = random.randint(-40, 40)
            sx = self.rect.centerx + offset
            sy = self.rect.centery + offset
            ctx["enemies"].append(MeleeEnemy(sx, sy, health=12, speed=100, damage=6))


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


class BossYaowang(Enemy):
    """妖王（虎形）：猛扑/火爪/震地/二连扑，阶段变化。见 docs/BOSS_DESIGN.md"""
    approach_type = APPROACH_PASSIVE
    BASE_SKILL = {
        "pounce": {"windup": 0.4, "cooldown": 2.3, "dash_speed": 380, "dash_time": 0.25, "min_dist": 55},
        "claw": {"windup": 0.3, "cooldown": 2.5, "proj_speed": 200, "proj_damage": 8, "min_dist": 90},
        "stomp": {"windup": 0.5, "cooldown": 3.0, "radius": 55, "damage": 12, "duration": 0.4},
        "double": {"windup": 0.4, "cooldown": 4.0, "dash_speed": 380, "dash_time": 0.25, "pause": 0.5, "min_dist": 70},
        "global_cross": {"windup": 0.58, "cooldown": 9.0, "damage": 11, "radius": 52, "duration": 0.55},
    }
    SKILL = _merge_boss_skill("segment_boss_1", BASE_SKILL)

    def __init__(self, x, y, health=180, speed=90, damage=18, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "charge", attr or "fire")
        self._cooldown_pounce = 0.2
        self._cooldown_claw = 0
        self._cooldown_stomp = 0.8
        self._cooldown_double = 0
        self._cooldown_global = 2.0
        self._state = "idle"
        self._state_timer = 0
        self._charge_dir = (0, 0)
        self._double_pounce_count = 0
        self._last_skill = None
        self._phase2_entered = False
        self._strafe_dir = 1
        self._strafe_timer = 1.1
        self._rhythm_step = 0

    def update(self, dt, player, ctx):
        if self.dead:
            return
        if getattr(self, "_invulnerable_until", 0) > 0:
            self._invulnerable_until -= dt
        for dot in getattr(self, "_dot_list", [])[:]:
            dot["timer"] += dt
            if dot["timer"] >= dot["interval"]:
                dot["timer"] = 0
                self.health -= dot["dmg"]
                dot["ticks_left"] -= 1
                if dot["ticks_left"] <= 0:
                    self._dot_list.remove(dot)
            if self.health <= 0:
                self.dead = True
                return
        if getattr(self, "_superconduct_slow", 0) > 0:
            self._superconduct_slow -= dt
        if getattr(self, "_weaken_until", 0) > 0:
            self._weaken_until -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        self._cooldown_pounce = max(0, self._cooldown_pounce - dt)
        self._cooldown_claw = max(0, self._cooldown_claw - dt)
        self._cooldown_stomp = max(0, self._cooldown_stomp - dt)
        self._cooldown_double = max(0, self._cooldown_double - dt)
        self._cooldown_global = max(0, self._cooldown_global - dt)
        hp_ratio = self.health / self.max_health if self.max_health > 0 else 0
        if (not self._phase2_entered) and hp_ratio < 0.5:
            self._phase2_entered = True
            self._state = "phase_shift"
            self._state_timer = 0.6
            self._invulnerable_until = max(getattr(self, "_invulnerable_until", 0), 0.6)
            return

        if self._state == "phase_shift":
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._state = "idle"
            return

        if self._state == "charging":
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._execute_skill(player, ctx)
            return
        if self._state == "dashing":
            spd = self.SKILL["double"]["dash_speed"] if self._double_pounce_count > 0 else self.SKILL["pounce"]["dash_speed"]
            self.rect.x += self._charge_dir[0] * spd * dt
            self.rect.y += self._charge_dir[1] * spd * dt
            self.rect.clamp_ip(pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H))
            if self.rect.colliderect(player.rect):
                player.take_damage(self._effective_damage(), self.attr)
                self._end_dash()
                return
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._end_dash()
            return
        if self._state == "double_pause":
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._start_dash(player)
            return

        if self._state == "idle":
            phase2 = self.health / self.max_health < 0.5
            dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            self._strafe_timer -= dt
            if self._strafe_timer <= 0:
                self._strafe_timer = 1.1
                self._strafe_dir *= -1
            # 空间利用：不过度贴脸，也不站桩。中距环绕，近距后撤，远距逼近。
            move_spd = self._effective_speed() * (1.15 if phase2 else 1.0)
            if dist < 78:
                _move_entity_away(self.rect, player.rect.centerx, player.rect.centery, move_spd, dt)
            elif dist > 190:
                _move_entity_towards(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.85, dt)
            else:
                _strafe_around(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.9, dt, self._strafe_dir)
            candidates = []
            if self._cooldown_pounce <= 0 and dist > self.SKILL["pounce"]["min_dist"]:
                candidates.append(("pounce", 3 if dist > 130 else 1))
            if self._cooldown_claw <= 0 and dist >= self.SKILL["claw"]["min_dist"]:
                candidates.append(("claw", 3 if dist >= 120 else 1))
            if self._cooldown_stomp <= 0:
                candidates.append(("stomp", 4 if dist < 110 else 1))
            if phase2 and self._cooldown_double <= 0 and dist > self.SKILL["double"]["min_dist"]:
                candidates.append(("double", 2 if dist > 100 else 1))
            if self._cooldown_global <= 0 and self._rhythm_step >= 2:
                candidates.append(("global_cross", 2))
            if candidates:
                filtered = [c for c in candidates if c[0] != self._last_skill]
                pool = filtered if filtered else candidates
                choices = [k for k, _ in pool]
                weights = [w for _, w in pool]
                choice = random.choices(choices, weights=weights, k=1)[0]
                self._last_skill = choice
                if choice == "pounce":
                    self._start_charge(self.SKILL["pounce"]["windup"], "pounce")
                elif choice == "claw":
                    self._start_charge(self.SKILL["claw"]["windup"], "claw")
                elif choice == "stomp":
                    self._start_charge(self.SKILL["stomp"]["windup"], "stomp")
                elif choice == "global_cross":
                    preview_points = _cross_points(include_diagonal=phase2)
                    play_boss_cue("warn", self.attr, priority=2)
                    _spawn_points_particles(preview_points, "boss_warn", self.attr)
                    _spawn_points_preview(
                        ctx,
                        preview_points,
                        radius=self.SKILL["global_cross"]["radius"],
                        duration=max(MIN_BOSS_PREVIEW_WINDOW, self.SKILL["global_cross"]["windup"] * 0.95),
                        color=(255, 205, 120, 95),
                    )
                    self._start_charge(self.SKILL["global_cross"]["windup"], "global_cross")
                else:
                    self._start_charge(self.SKILL["double"]["windup"], "double")

    def _start_charge(self, duration, skill):
        self._state = "charging"
        self._state_timer = duration
        self._next_skill = skill

    def _execute_skill(self, player, ctx):
        skill = getattr(self, "_next_skill", "pounce")
        if skill == "pounce":
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                self._charge_dir = (dx / dist, dy / dist)
                self._state = "dashing"
                self._state_timer = self.SKILL["pounce"]["dash_time"]
                self._cooldown_pounce = self.SKILL["pounce"]["cooldown"]
            else:
                self._state = "idle"
        elif skill == "claw":
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                base_ang = math.atan2(dy, dx)
                for i in (-1, 0, 1):
                    ang = base_ang + math.radians(i * 30)
                    vx = math.cos(ang) * self.SKILL["claw"]["proj_speed"]
                    vy = math.sin(ang) * self.SKILL["claw"]["proj_speed"]
                    ctx["enemy_projectiles"].append(EnemyProjectile(
                        self.rect.centerx, self.rect.centery, vx, vy, self.SKILL["claw"]["proj_damage"],
                        color=(255, 120, 60), homing=False, attr=self.attr
                    ))
            self._cooldown_claw = self.SKILL["claw"]["cooldown"]
            self._rhythm_step = min(2, self._rhythm_step + 1)
            self._state = "idle"
        elif skill == "stomp":
            ctx["aoe_zones"].append(AOEZone(
                self.rect.centerx, self.rect.centery,
                self.SKILL["stomp"]["radius"],
                self.SKILL["stomp"]["damage"],
                self.SKILL["stomp"]["duration"],
                color=(180, 80, 60, 120), attr=self.attr
            ))
            self._cooldown_stomp = self.SKILL["stomp"]["cooldown"]
            self._rhythm_step = min(2, self._rhythm_step + 1)
            self._state = "idle"
        elif skill == "double":
            self._double_pounce_count = 0
            self._rhythm_step = min(2, self._rhythm_step + 1)
            self._do_double_pounce(player, ctx)
        elif skill == "global_cross":
            phase2 = self.health / self.max_health < 0.5
            points = _cross_points(include_diagonal=phase2)
            play_boss_cue("cast", self.attr, priority=4)
            _spawn_points_particles(points, "boss_cast", self.attr)
            _spawn_points_aoe(
                ctx,
                points,
                radius=self.SKILL["global_cross"]["radius"] + (4 if phase2 else 0),
                damage=max(1, int(self.SKILL["global_cross"]["damage"] * (1.12 if phase2 else 1.0))),
                duration=self.SKILL["global_cross"]["duration"],
                color=(235, 120, 90, 120),
                attr=self.attr,
            )
            self._cooldown_global = self.SKILL["global_cross"]["cooldown"]
            self._rhythm_step = 0
            self._state = "idle"
        self._next_skill = None

    def _do_double_pounce(self, player, ctx):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self._charge_dir = (dx / dist, dy / dist)
            self._state = "dashing"
            self._state_timer = self.SKILL["double"]["dash_time"]
            self._double_pounce_count = 1

    def _end_dash(self):
        if self._double_pounce_count == 1:
            self._state = "double_pause"
            self._state_timer = self.SKILL["double"]["pause"]
            self._double_pounce_count = 2
        else:
            if self._double_pounce_count == 0:
                self._rhythm_step = min(2, self._rhythm_step + 1)
            self._cooldown_double = self.SKILL["double"]["cooldown"] if self._double_pounce_count == 2 else self._cooldown_pounce
            self._state = "idle"
            self._double_pounce_count = 0

    def _start_dash(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self._charge_dir = (dx / dist, dy / dist)
            self._state = "dashing"
            self._state_timer = self.SKILL["double"]["dash_time"]
            self._double_pounce_count = 2
        else:
            self._cooldown_double = self.SKILL["double"]["cooldown"]
            self._state = "idle"

    def _effective_damage(self):
        return 18 if getattr(self, "_weaken_until", 0) <= 0 else max(1, int(18 * 0.85))


class BossJianmo(Enemy):
    """剑魔：近战压迫 + 剑气 + 限次召唤（主副目标切换）"""
    approach_type = APPROACH_PASSIVE
    BASE_SKILL = {
        "slash_cd": 0.9,
        "wave_cd": 2.6,
        "wave_cd_phase2": 2.1,
        "wave_windup": 0.3,
        "wave_speed": 260,
        "wave_damage": 14,
        "summon_windup": 1.5,
        "summon_cd": 10.5,
        "summon_limit": 2,
        "global_barrage_windup": 0.58,
        "global_barrage_cd": 9.5,
        "global_barrage_damage": 11,
        "global_barrage_speed": 230,
        "global_barrage_count": 5,
    }
    SKILL = _merge_boss_skill("segment_boss_2", BASE_SKILL)

    def __init__(self, x, y, health=220, speed=75, damage=22, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "melee", attr or "wood")
        self._state = "idle"
        self._state_timer = 0
        self._wave_cooldown = 1.5
        self._summon_cooldown = 6.0
        self._global_barrage_cd = 3.6
        self._summon_count = 0
        self._phase2_entered = False
        self._pending_skill = None
        self._melee_hit_cooldown = self.SKILL["slash_cd"]
        self._strafe_dir = 1
        self._strafe_timer = 1.0
        self._rhythm_step = 0

    def _count_minions(self, enemies):
        return sum(1 for e in enemies if (e is not self) and (not e.dead) and getattr(e, "_jianmo_minion", False))

    def update(self, dt, player, ctx):
        if self.dead:
            return
        super().update(dt, player, ctx)

        hp_ratio = self.health / self.max_health if self.max_health > 0 else 0
        minion_count = self._count_minions(ctx.get("enemies", []))
        if (not self._phase2_entered) and hp_ratio < 0.5:
            self._phase2_entered = True
            self._state = "phase_shift"
            self._state_timer = 0.6
            self._invulnerable_until = max(getattr(self, "_invulnerable_until", 0), 0.6)
            return

        if self._state == "phase_shift":
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._state = "idle"
            return

        if self._state in ("wave_windup", "summon_windup", "global_barrage_windup"):
            self._state_timer -= dt
            if self._state_timer <= 0:
                if self._pending_skill == "wave":
                    self._cast_wave(player, ctx)
                elif self._pending_skill == "summon":
                    self._cast_summon(ctx)
                elif self._pending_skill == "global_barrage":
                    self._cast_global_barrage(ctx)
                self._pending_skill = None
            return

        self._wave_cooldown = max(0, self._wave_cooldown - dt)
        self._summon_cooldown = max(0, self._summon_cooldown - dt)
        self._global_barrage_cd = max(0, self._global_barrage_cd - dt)
        self._strafe_timer -= dt
        if self._strafe_timer <= 0:
            self._strafe_timer = 1.0
            self._strafe_dir *= -1

        # 空间利用：维持中近距并绕圈压迫，而非无脑直冲
        dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        move_spd = self._effective_speed() * (1.1 if self._phase2_entered else 1.0)
        if dist < 85:
            _move_entity_away(self.rect, player.rect.centerx, player.rect.centery, move_spd, dt)
        elif dist > 165:
            _move_entity_towards(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.9, dt)
        else:
            _strafe_around(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.85, dt, self._strafe_dir)

        # 近战斩击（主压迫）
        if self.attack_cooldown <= 0 and self.rect.colliderect(player.rect):
            player.take_damage(self._effective_damage(), self.attr)
            self.attack_cooldown = self._melee_hit_cooldown
            self._rhythm_step = min(2, self._rhythm_step + 1)

        # 召唤优先：仅在随从清空后触发，且限次
        if minion_count == 0 and self._summon_count < self.SKILL["summon_limit"] and self._summon_cooldown <= 0:
            self._state = "summon_windup"
            self._state_timer = self.SKILL["summon_windup"]
            self._pending_skill = "summon"
            return

        global_need = 1 if self._phase2_entered else 2
        if self._global_barrage_cd <= 0 and self._rhythm_step >= global_need:
            line_count = self.SKILL["global_barrage_count"] + (1 if self._phase2_entered else 0)
            preview_points = []
            h_step = ARENA_H / (line_count + 1)
            for i in range(line_count):
                y = ARENA_Y + int((i + 1) * h_step)
                preview_points.append((ARENA_X + 12, y))
                preview_points.append((ARENA_X + ARENA_W - 12, y))
            if self._phase2_entered:
                v_step = ARENA_W / (line_count + 1)
                for i in range(line_count):
                    x = ARENA_X + int((i + 1) * v_step)
                    preview_points.append((x, ARENA_Y + 12))
                    preview_points.append((x, ARENA_Y + ARENA_H - 12))
            play_boss_cue("warn", self.attr, priority=2)
            _spawn_points_particles(preview_points, "boss_warn", self.attr)
            _spawn_points_preview(
                ctx,
                preview_points,
                radius=18,
                duration=max(MIN_BOSS_PREVIEW_WINDOW, self.SKILL["global_barrage_windup"] * 0.95),
                color=(210, 255, 180, 95),
            )
            self._state = "global_barrage_windup"
            self._state_timer = self.SKILL["global_barrage_windup"]
            self._pending_skill = "global_barrage"
            self._global_barrage_cd = self.SKILL["global_barrage_cd"]
            return

        # 剑气：phase2 或无随从时更频繁
        wave_cd_target = self.SKILL["wave_cd_phase2"] if (self._phase2_entered or minion_count == 0) else self.SKILL["wave_cd"]
        if self._wave_cooldown <= 0:
            self._state = "wave_windup"
            self._state_timer = self.SKILL["wave_windup"]
            self._pending_skill = "wave"
            self._wave_cooldown = wave_cd_target

    def _cast_wave(self, player, ctx):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist <= 0:
            self._state = "idle"
            return
        vx = dx / dist * self.SKILL["wave_speed"]
        vy = dy / dist * self.SKILL["wave_speed"]
        ctx["enemy_projectiles"].append(EnemyProjectile(
            self.rect.centerx, self.rect.centery, vx, vy, self.SKILL["wave_damage"],
            color=(120, 255, 160), homing=False, attr=self.attr
        ))
        self._rhythm_step = min(2, self._rhythm_step + 1)
        self._state = "idle"

    def _cast_summon(self, ctx):
        offsets = [(-42, 35), (42, 35)]
        spawned = 0
        for ox, oy in offsets:
            if spawned >= 1:  # 每次只补一只，避免瞬间爆量
                break
            sx = self.rect.centerx + ox
            sy = self.rect.centery + oy
            m = RangedEnemy(sx, sy, health=80, speed=70, damage=10, attr=self.attr)
            m._jianmo_minion = True
            ctx["enemies"].append(m)
            spawned += 1
        if spawned > 0:
            self._summon_count += 1
            self._summon_cooldown = self.SKILL["summon_cd"]
            self._rhythm_step = min(2, self._rhythm_step + 1)
        self._state = "idle"

    def _cast_global_barrage(self, ctx):
        line_count = self.SKILL["global_barrage_count"] + (1 if self._phase2_entered else 0)
        cast_points = []
        h_step = ARENA_H / (line_count + 1)
        for i in range(line_count):
            y = ARENA_Y + int((i + 1) * h_step)
            cast_points.append((ARENA_X + 10, y))
            cast_points.append((ARENA_X + ARENA_W - 10, y))
        if self._phase2_entered:
            v_step = ARENA_W / (line_count + 1)
            for i in range(line_count):
                x = ARENA_X + int((i + 1) * v_step)
                cast_points.append((x, ARENA_Y + 10))
                cast_points.append((x, ARENA_Y + ARENA_H - 10))
        play_boss_cue("cast", self.attr, priority=4)
        _spawn_points_particles(cast_points, "boss_cast", self.attr)
        _spawn_edge_barrage(
            ctx,
            damage=self.SKILL["global_barrage_damage"],
            speed=self.SKILL["global_barrage_speed"],
            count=line_count,
            color=(150, 240, 170),
            attr=self.attr,
        )
        if self._phase2_entered:
            _spawn_edge_barrage(
                ctx,
                damage=max(1, int(self.SKILL["global_barrage_damage"] * 0.85)),
                speed=max(120, int(self.SKILL["global_barrage_speed"] * 0.9)),
                count=line_count,
                axis="vertical",
                color=(130, 220, 160),
                attr=self.attr,
            )
        self._rhythm_step = 0
        self._state = "idle"


class BossDanmo(Enemy):
    """丹魔：毒爆 + 毒环，40% 以下强化邪灵。"""
    approach_type = APPROACH_PASSIVE
    BASE_SKILL = {
        "toxic_burst": {"windup": 0.42, "cooldown": 2.35, "radius": 65, "damage": 20, "duration": 0.5},
        "toxic_ring": {"windup": 0.52, "cooldown": 3.7, "cooldown_phase2": 3.0, "inner_radius": 40, "outer_radius": 80, "damage": 12, "duration": 0.5},
        "global_flood": {"windup": 0.68, "cooldown": 10.0, "damage": 9, "duration": 0.7, "radius": 44},
        "phase2_threshold": 0.4,
        "minion_speed_mul": 1.2,
        "minion_damage_mul": 1.15,
    }
    SKILL = _merge_boss_skill("segment_boss_3", BASE_SKILL)

    def __init__(self, x, y, health=200, speed=65, damage=20, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "aoe", attr or "earth")
        self._state = "idle"
        self._state_timer = 0
        self._pending_skill = None
        self._burst_cd = 0.8
        self._ring_cd = 1.4
        self._global_flood_cd = 4.2
        self._phase2_entered = False
        self._last_skill = None
        self._strafe_dir = 1
        self._strafe_timer = 1.2
        self._rhythm_step = 0

    def _buff_minions_if_needed(self, enemies):
        if not self._phase2_entered:
            return
        for e in enemies:
            if e.dead or not getattr(e, "_danmo_minion", False):
                continue
            if getattr(e, "_buffed_by_danmo", False):
                continue
            e.speed = min(ENEMY_MAX_SPEED, int(e.speed * self.SKILL["minion_speed_mul"]))
            e.damage = max(1, int(e.damage * self.SKILL["minion_damage_mul"]))
            e._buffed_by_danmo = True

    def update(self, dt, player, ctx):
        if self.dead:
            return
        # Boss 自行处理：不主动贴身，仅放技能
        if getattr(self, "_invulnerable_until", 0) > 0:
            self._invulnerable_until -= dt
        if getattr(self, "_superconduct_slow", 0) > 0:
            self._superconduct_slow -= dt
        if getattr(self, "_weaken_until", 0) > 0:
            self._weaken_until -= dt
        for dot in getattr(self, "_dot_list", [])[:]:
            dot["timer"] += dt
            if dot["timer"] >= dot["interval"]:
                dot["timer"] = 0
                self.health -= dot["dmg"]
                dot["ticks_left"] -= 1
                if dot["ticks_left"] <= 0:
                    self._dot_list.remove(dot)
            if self.health <= 0:
                self.dead = True
                return

        hp_ratio = self.health / self.max_health if self.max_health > 0 else 0
        if (not self._phase2_entered) and hp_ratio < self.SKILL["phase2_threshold"]:
            self._phase2_entered = True
            self._state = "phase_shift"
            self._state_timer = 0.6
            self._invulnerable_until = max(getattr(self, "_invulnerable_until", 0), 0.6)
            self._buff_minions_if_needed(ctx.get("enemies", []))
            return

        self._buff_minions_if_needed(ctx.get("enemies", []))

        if self._state == "phase_shift":
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._state = "idle"
            return

        if self._state in ("burst_windup", "ring_windup", "global_flood_windup"):
            self._state_timer -= dt
            if self._state_timer <= 0:
                if self._pending_skill == "toxic_burst":
                    self._cast_toxic_burst(player, ctx)
                elif self._pending_skill == "toxic_ring":
                    self._cast_toxic_ring(ctx)
                elif self._pending_skill == "global_flood":
                    self._cast_global_flood(ctx)
                self._pending_skill = None
            return

        self._burst_cd = max(0, self._burst_cd - dt)
        self._ring_cd = max(0, self._ring_cd - dt)
        self._global_flood_cd = max(0, self._global_flood_cd - dt)
        ring_cd_target = self.SKILL["toxic_ring"]["cooldown_phase2"] if self._phase2_entered else self.SKILL["toxic_ring"]["cooldown"]

        # 远中距更偏 burst，近距更偏 ring，且尽量不重复
        dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        self._strafe_timer -= dt
        if self._strafe_timer <= 0:
            self._strafe_timer = 1.2
            self._strafe_dir *= -1
        move_spd = self._effective_speed() * (1.1 if self._phase2_entered else 1.0)
        if dist < 115:
            _move_entity_away(self.rect, player.rect.centerx, player.rect.centery, move_spd, dt)
        elif dist > 205:
            _move_entity_towards(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.85, dt)
        else:
            _strafe_around(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.8, dt, self._strafe_dir)
        candidates = []
        if self._burst_cd <= 0:
            candidates.append(("toxic_burst", 3 if dist >= 95 else 1))
        if self._ring_cd <= 0:
            candidates.append(("toxic_ring", 3 if dist < 120 else 1))
        global_need = 1 if self._phase2_entered else 2
        if self._global_flood_cd <= 0 and self._rhythm_step >= global_need:
            candidates.append(("global_flood", 2 if dist >= 90 else 1))
        if not candidates:
            return
        filtered = [c for c in candidates if c[0] != self._last_skill]
        pool = filtered if filtered else candidates
        choices = [k for k, _ in pool]
        weights = [w for _, w in pool]
        pick = random.choices(choices, weights=weights, k=1)[0]
        self._last_skill = pick
        if pick == "toxic_burst":
            self._state = "burst_windup"
            self._state_timer = self.SKILL["toxic_burst"]["windup"]
            self._pending_skill = "toxic_burst"
            self._burst_cd = self.SKILL["toxic_burst"]["cooldown"]
            self._rhythm_step = min(2, self._rhythm_step + 1)
        else:
            if pick == "toxic_ring":
                self._state = "ring_windup"
                self._state_timer = self.SKILL["toxic_ring"]["windup"]
                self._pending_skill = "toxic_ring"
                self._ring_cd = ring_cd_target
                self._rhythm_step = min(2, self._rhythm_step + 1)
            else:
                phase2 = self._phase2_entered
                preview_points = _danmo_flood_points(phase2=phase2)
                play_boss_cue("warn", self.attr, priority=2)
                _spawn_points_particles(preview_points, "boss_warn", self.attr)
                _spawn_points_preview(
                    ctx,
                    preview_points,
                    radius=self.SKILL["global_flood"]["radius"] + (4 if phase2 else 0),
                    duration=max(MIN_BOSS_PREVIEW_WINDOW, self.SKILL["global_flood"]["windup"] * 0.95),
                    color=(180, 230, 160, 100),
                )
                self._state = "global_flood_windup"
                self._state_timer = self.SKILL["global_flood"]["windup"]
                self._pending_skill = "global_flood"
                self._global_flood_cd = self.SKILL["global_flood"]["cooldown"]

    def _cast_toxic_burst(self, player, ctx):
        ctx["aoe_zones"].append(AOEZone(
            player.rect.centerx, player.rect.centery,
            self.SKILL["toxic_burst"]["radius"],
            self.SKILL["toxic_burst"]["damage"],
            self.SKILL["toxic_burst"]["duration"],
            color=(120, 220, 120, 120), attr=self.attr
        ))
        self._state = "idle"

    def _cast_toxic_ring(self, ctx):
        # 近环 + 外环近似“扩散毒环”，避免一次性全屏必中
        ctx["aoe_zones"].append(AOEZone(
            self.rect.centerx, self.rect.centery,
            self.SKILL["toxic_ring"]["inner_radius"],
            self.SKILL["toxic_ring"]["damage"],
            self.SKILL["toxic_ring"]["duration"],
            color=(100, 180, 100, 110), attr=self.attr
        ))
        ctx["aoe_zones"].append(AOEZone(
            self.rect.centerx, self.rect.centery,
            self.SKILL["toxic_ring"]["outer_radius"],
            max(1, int(self.SKILL["toxic_ring"]["damage"] * 0.75)),
            self.SKILL["toxic_ring"]["duration"],
            color=(90, 150, 90, 90), attr=self.attr
        ))
        self._state = "idle"

    def _cast_global_flood(self, ctx):
        # P1: 四角+中心；P2: 环形毒阵（覆盖方式变化）
        phase2 = self._phase2_entered
        points = _danmo_flood_points(phase2=phase2)
        play_boss_cue("cast", self.attr, priority=4)
        _spawn_points_particles(points, "boss_cast", self.attr)
        _spawn_points_aoe(
            ctx,
            points,
            radius=self.SKILL["global_flood"]["radius"] + (4 if phase2 else 0),
            damage=max(1, int(self.SKILL["global_flood"]["damage"] * (1.1 if phase2 else 1.0))),
            duration=self.SKILL["global_flood"]["duration"],
            color=(95, 170, 95, 110), attr=self.attr
        )
        self._rhythm_step = 0
        self._state = "idle"


class BossHuiyuan(Enemy):
    """秽源：秽冲 + 秽弹幕 + 邪气再生（限次）+ 二阶段强化。"""
    approach_type = APPROACH_PASSIVE
    BASE_SKILL = {
        "dash": {"windup": 0.52, "cooldown": 2.5, "cooldown_phase2": 2.2, "speed": 420, "time": 0.35, "damage": 24, "min_dist": 70},
        "barrage": {"windup": 0.42, "cooldown": 3.0, "cooldown_phase2": 2.6, "damage": 10, "speed": 220, "angles": (-22, -11, 0, 11, 22), "min_dist": 90},
        "regen": {"windup": 1.0, "cooldown": 7.0, "cooldown_phase2": 5.0, "limit": 2},
        "global_collapse": {"windup": 0.68, "cooldown": 8.0, "cooldown_phase2": 6.8, "damage": 12, "duration": 0.65, "radius": 48},
    }
    SKILL = _merge_boss_skill("final_boss", BASE_SKILL)

    def __init__(self, x, y, health=280, speed=85, damage=24, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "charge", attr or "fire")
        self._state = "idle"
        self._state_timer = 0
        self._pending_skill = None
        self._dash_cd = 0.8
        self._barrage_cd = 1.6
        self._regen_cd = 5.0
        self._collapse_cd = 3.8
        self._regen_count = 0
        self._phase2_entered = False
        self._dash_dir = (0, 0)
        self._last_skill = None
        self._dash_damage = self.SKILL["dash"]["damage"]
        self._strafe_dir = 1
        self._strafe_timer = 0.9
        self._rhythm_step = 0

    def _count_minions(self, enemies):
        return sum(1 for e in enemies if (e is not self) and (not e.dead) and getattr(e, "_huiyuan_minion", False))

    def _dash_damage_effective(self):
        if getattr(self, "_weaken_until", 0) <= 0:
            return self._dash_damage
        return max(1, int(self._dash_damage * (1 - getattr(self, "_weaken_pct", 15) / 100)))

    def update(self, dt, player, ctx):
        if self.dead:
            return
        if getattr(self, "_invulnerable_until", 0) > 0:
            self._invulnerable_until -= dt
        if getattr(self, "_superconduct_slow", 0) > 0:
            self._superconduct_slow -= dt
        if getattr(self, "_weaken_until", 0) > 0:
            self._weaken_until -= dt
        for dot in getattr(self, "_dot_list", [])[:]:
            dot["timer"] += dt
            if dot["timer"] >= dot["interval"]:
                dot["timer"] = 0
                self.health -= dot["dmg"]
                dot["ticks_left"] -= 1
                if dot["ticks_left"] <= 0:
                    self._dot_list.remove(dot)
            if self.health <= 0:
                self.dead = True
                return

        hp_ratio = self.health / self.max_health if self.max_health > 0 else 0
        if (not self._phase2_entered) and hp_ratio < 0.5:
            self._phase2_entered = True
            self._state = "phase_shift"
            self._state_timer = 0.6
            self._invulnerable_until = max(getattr(self, "_invulnerable_until", 0), 0.6)
            self._dash_damage = max(self._dash_damage, int(self.SKILL["dash"]["damage"] * 1.15))
            return

        if self._state == "phase_shift":
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._state = "idle"
            return

        if self._state in ("dash_windup", "barrage_windup", "regen_windup", "collapse_windup"):
            self._state_timer -= dt
            if self._state_timer <= 0:
                if self._pending_skill == "dash":
                    self._cast_dash(player)
                elif self._pending_skill == "barrage":
                    self._cast_barrage(player, ctx)
                elif self._pending_skill == "regen":
                    self._cast_regen(ctx)
                elif self._pending_skill == "collapse":
                    self._cast_global_collapse(ctx)
                self._pending_skill = None
            return

        if self._state == "dashing":
            spd = self.SKILL["dash"]["speed"]
            if self._phase2_entered:
                spd = int(spd * 1.15)
            self.rect.x += self._dash_dir[0] * spd * dt
            self.rect.y += self._dash_dir[1] * spd * dt
            self.rect.clamp_ip(pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H))
            if self.rect.colliderect(player.rect):
                player.take_damage(self._dash_damage_effective(), self.attr)
                self._state = "idle"
                return
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._state = "idle"
            return

        self._dash_cd = max(0, self._dash_cd - dt)
        self._barrage_cd = max(0, self._barrage_cd - dt)
        self._regen_cd = max(0, self._regen_cd - dt)
        self._collapse_cd = max(0, self._collapse_cd - dt)
        dash_cd_target = self.SKILL["dash"]["cooldown_phase2"] if self._phase2_entered else self.SKILL["dash"]["cooldown"]
        barrage_cd_target = self.SKILL["barrage"]["cooldown_phase2"] if self._phase2_entered else self.SKILL["barrage"]["cooldown"]
        regen_cd_target = self.SKILL["regen"]["cooldown_phase2"] if self._phase2_entered else self.SKILL["regen"]["cooldown"]
        collapse_cd_target = self.SKILL["global_collapse"]["cooldown_phase2"] if self._phase2_entered else self.SKILL["global_collapse"]["cooldown"]
        minion_count = self._count_minions(ctx.get("enemies", []))
        dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        self._strafe_timer -= dt
        if self._strafe_timer <= 0:
            self._strafe_timer = 0.9
            self._strafe_dir *= -1
        # 终局 Boss 更强调空间切割：中距离环绕压迫 + 过远逼近
        move_spd = self._effective_speed() * (1.15 if self._phase2_entered else 1.0)
        if dist < 105:
            _move_entity_away(self.rect, player.rect.centerx, player.rect.centery, move_spd, dt)
        elif dist > 230:
            _move_entity_towards(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.95, dt)
        else:
            _strafe_around(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.95, dt, self._strafe_dir)

        # 邪气再生：仅随从全灭后触发，限次
        if minion_count == 0 and self._regen_count < self.SKILL["regen"]["limit"] and self._regen_cd <= 0:
            self._state = "regen_windup"
            self._state_timer = self.SKILL["regen"]["windup"]
            self._pending_skill = "regen"
            self._last_skill = "regen"
            self._regen_cd = regen_cd_target
            self._rhythm_step = min(2, self._rhythm_step + 1)
            return

        candidates = []
        if self._dash_cd <= 0 and dist > self.SKILL["dash"]["min_dist"]:
            candidates.append(("dash", 3 if dist > 130 else 1))
        if self._barrage_cd <= 0 and dist >= self.SKILL["barrage"]["min_dist"]:
            candidates.append(("barrage", 3 if dist >= 120 else 1))
        global_need = 1 if self._phase2_entered else 2
        if self._collapse_cd <= 0 and self._rhythm_step >= global_need:
            candidates.append(("collapse", 2 if self._phase2_entered else 1))
        if not candidates:
            return
        filtered = [c for c in candidates if c[0] != self._last_skill]
        pool = filtered if filtered else candidates
        choices = [k for k, _ in pool]
        weights = [w for _, w in pool]
        pick = random.choices(choices, weights=weights, k=1)[0]
        self._last_skill = pick
        if pick == "dash":
            self._state = "dash_windup"
            self._state_timer = self.SKILL["dash"]["windup"]
            self._pending_skill = "dash"
            self._dash_cd = dash_cd_target
        elif pick == "barrage":
            self._state = "barrage_windup"
            self._state_timer = self.SKILL["barrage"]["windup"]
            self._pending_skill = "barrage"
            self._barrage_cd = barrage_cd_target
        else:
            phase2 = self._phase2_entered
            preview_points = _huiyuan_collapse_points(phase2=phase2)
            play_boss_cue("warn", self.attr, priority=3)
            _spawn_points_particles(preview_points, "boss_warn", self.attr)
            _spawn_points_preview(
                ctx,
                preview_points,
                radius=self.SKILL["global_collapse"]["radius"] + (5 if phase2 else 0),
                duration=max(MIN_BOSS_PREVIEW_WINDOW, self.SKILL["global_collapse"]["windup"] * 0.95),
                color=(255, 180, 180, 105),
            )
            self._state = "collapse_windup"
            self._state_timer = self.SKILL["global_collapse"]["windup"]
            self._pending_skill = "collapse"
            self._collapse_cd = collapse_cd_target

    def _cast_dash(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist <= 0:
            self._state = "idle"
            return
        self._dash_dir = (dx / dist, dy / dist)
        self._state = "dashing"
        self._state_timer = self.SKILL["dash"]["time"]
        self._rhythm_step = min(2, self._rhythm_step + 1)

    def _cast_barrage(self, player, ctx):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist <= 0:
            self._state = "idle"
            return
        base = math.atan2(dy, dx)
        for deg in self.SKILL["barrage"]["angles"]:
            ang = base + math.radians(deg)
            vx = math.cos(ang) * self.SKILL["barrage"]["speed"]
            vy = math.sin(ang) * self.SKILL["barrage"]["speed"]
            ctx["enemy_projectiles"].append(EnemyProjectile(
                self.rect.centerx, self.rect.centery, vx, vy, self.SKILL["barrage"]["damage"],
                color=(255, 90, 90), homing=False, attr=self.attr
            ))
        self._rhythm_step = min(2, self._rhythm_step + 1)
        self._state = "idle"

    def _cast_regen(self, ctx):
        offsets = [(-40, 32), (40, 32)]
        spawned = 0
        for ox, oy in offsets:
            if spawned >= 1:
                break
            sx = self.rect.centerx + ox
            sy = self.rect.centery + oy
            m = RangedEnemy(sx, sy, health=100, speed=75, damage=12, attr=self.attr)
            m._huiyuan_minion = True
            ctx["enemies"].append(m)
            spawned += 1
        if spawned > 0:
            self._regen_count += 1
        self._state = "idle"

    def _cast_global_collapse(self, ctx):
        # 终局全局压制：P2 增加中轴封线，安全区更窄
        phase2 = self._phase2_entered
        points = _huiyuan_collapse_points(phase2=phase2)
        play_boss_cue("cast", self.attr, priority=5)
        _spawn_points_particles(points, "boss_cast", self.attr)
        _spawn_points_aoe(
            ctx,
            points,
            radius=self.SKILL["global_collapse"]["radius"] + (5 if phase2 else 0),
            damage=max(1, int(self.SKILL["global_collapse"]["damage"] * (1.14 if phase2 else 1.0))),
            duration=self.SKILL["global_collapse"]["duration"],
            color=(210, 70, 70, 120),
            attr=self.attr,
        )
        self._rhythm_step = 0
        self._state = "idle"


# Boss 注册表：boss_id -> Boss 类（首只敌人视为主 Boss）
BOSS_REGISTRY = {
    "segment_boss_1": BossYaowang,
    "segment_boss_2": BossJianmo,
    "segment_boss_3": BossDanmo,
    "final_boss": BossHuiyuan,
}


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
