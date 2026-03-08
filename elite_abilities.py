"""
精英怪特殊能力系统
为精英怪添加独特的技能和行为模式
"""

import math
import random

from attribute import Attr

# ==================== 精英怪特殊能力 ====================


class EliteAbility:
    """精英怪特殊能力基类"""

    def __init__(self, enemy):
        self.enemy = enemy
        self.cooldown = 0.0
        self.cooldown_max = 5.0

    def update(self, dt, player, game):
        """更新能力（每帧调用）"""
        if self.cooldown > 0:
            self.cooldown -= dt

    def can_use(self):
        """是否可以使用能力"""
        return self.cooldown <= 0

    def use(self, player, game):
        """使用能力"""
        self.cooldown = self.cooldown_max


class ShieldAbility(EliteAbility):
    """护盾能力：定期生成护盾，吸收伤害"""

    def __init__(self, enemy):
        super().__init__(enemy)
        self.cooldown_max = 8.0
        self.shield_health = 0
        self.shield_max = enemy.max_health * 0.3  # 30%血量的护盾

    def update(self, dt, player, game):
        super().update(dt, player, game)

        # 自动使用
        if self.can_use() and self.shield_health <= 0:
            self.use(player, game)

    def use(self, player, game):
        super().use(player, game)
        self.shield_health = self.shield_max

        # 视觉效果
        from particles import spawn_particles

        spawn_particles(self.enemy.x, self.enemy.y, "boss_cast")

    def absorb_damage(self, damage):
        """吸收伤害，返回剩余伤害"""
        if self.shield_health > 0:
            absorbed = min(self.shield_health, damage)
            self.shield_health -= absorbed
            return damage - absorbed
        return damage


class TeleportAbility(EliteAbility):
    """瞬移能力：受到大量伤害时瞬移"""

    def __init__(self, enemy):
        super().__init__(enemy)
        self.cooldown_max = 6.0
        self.last_health = enemy.health

    def update(self, dt, player, game):
        super().update(dt, player, game)

        # 检测大量伤害
        damage_taken = self.last_health - self.enemy.health
        if damage_taken > self.enemy.max_health * 0.2 and self.can_use():
            self.use(player, game)

        self.last_health = self.enemy.health

    def use(self, player, game):
        super().use(player, game)

        # 瞬移到随机位置
        from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y

        self.enemy.x = random.randint(ARENA_X + 50, ARENA_X + ARENA_W - 50)
        self.enemy.y = random.randint(ARENA_Y + 50, ARENA_Y + ARENA_H - 50)

        # 视觉效果
        from particles import spawn_particles

        spawn_particles(self.enemy.x, self.enemy.y, "boss_cast")


class SummonAbility(EliteAbility):
    """召唤能力：召唤小怪"""

    def __init__(self, enemy):
        super().__init__(enemy)
        self.cooldown_max = 10.0

    def update(self, dt, player, game):
        super().update(dt, player, game)

        # 血量低于50%时召唤
        if self.enemy.health < self.enemy.max_health * 0.5 and self.can_use():
            self.use(player, game)

    def use(self, player, game):
        super().use(player, game)

        # 召唤2-3个小怪
        from enemy import Enemy

        count = random.randint(2, 3)

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            distance = 80
            x = self.enemy.x + math.cos(angle) * distance
            y = self.enemy.y + math.sin(angle) * distance

            minion = Enemy(
                x, y, health=20, damage=5, speed=100, ai_type="melee", attr=self.enemy.attr, color=self.enemy.color
            )

            if hasattr(game, "enemies"):
                game.enemies.append(minion)

        # 视觉效果
        from particles import spawn_particles

        spawn_particles(self.enemy.x, self.enemy.y, "boss_cast")


class RageAbility(EliteAbility):
    """狂暴能力：血量低时提升攻击和速度"""

    def __init__(self, enemy):
        super().__init__(enemy)
        self.cooldown_max = 999.0  # 只触发一次
        self.is_raged = False

    def update(self, dt, player, game):
        super().update(dt, player, game)

        # 血量低于30%时狂暴
        if self.enemy.health < self.enemy.max_health * 0.3 and not self.is_raged:
            self.use(player, game)

    def use(self, player, game):
        super().use(player, game)
        self.is_raged = True

        # 提升属性
        self.enemy.damage = int(self.enemy.damage * 1.5)
        self.enemy.speed = int(self.enemy.speed * 1.3)

        # 改变颜色（变红）
        r, g, b = self.enemy.color
        self.enemy.color = (min(255, r + 50), max(0, g - 30), max(0, b - 30))

        # 视觉效果
        from particles import spawn_particles

        spawn_particles(self.enemy.x, self.enemy.y, "boss_cast_fire")


class HealAbility(EliteAbility):
    """治疗能力：定期回血"""

    def __init__(self, enemy):
        super().__init__(enemy)
        self.cooldown_max = 12.0

    def update(self, dt, player, game):
        super().update(dt, player, game)

        # 血量低于70%时治疗
        if self.enemy.health < self.enemy.max_health * 0.7 and self.can_use():
            self.use(player, game)

    def use(self, player, game):
        super().use(player, game)

        # 回复20%血量
        heal = int(self.enemy.max_health * 0.2)
        self.enemy.health = min(self.enemy.max_health, self.enemy.health + heal)

        # 视觉效果
        from particles import spawn_particles

        spawn_particles(self.enemy.x, self.enemy.y, "boss_cast_wood")

        # 显示治疗飘字
        from damage_text import show_heal

        show_heal(self.enemy.x, self.enemy.y, heal)


# ==================== 能力分配 ====================

ELITE_ABILITIES = {
    "强壮": ShieldAbility,  # 护盾
    "迅捷": TeleportAbility,  # 瞬移
    "狂暴": RageAbility,  # 狂暴
    "坚韧": HealAbility,  # 治疗
}


def assign_elite_ability(enemy, modifier_name):
    """为精英怪分配特殊能力"""
    ability_class = ELITE_ABILITIES.get(modifier_name)
    if ability_class:
        enemy.elite_ability = ability_class(enemy)
    else:
        enemy.elite_ability = None


# ==================== Boss特殊技能 ====================


class BossPhase:
    """Boss阶段"""

    def __init__(self, hp_threshold, skills):
        """
        hp_threshold: 血量阈值（百分比）
        skills: 该阶段可用的技能列表
        """
        self.hp_threshold = hp_threshold
        self.skills = skills
        self.entered = False


class BossSkill:
    """Boss技能基类"""

    def __init__(self, boss):
        self.boss = boss
        self.cooldown = 0.0
        self.cooldown_max = 8.0

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt

    def can_use(self):
        return self.cooldown <= 0

    def use(self, player, game):
        self.cooldown = self.cooldown_max


class BossFireRain(BossSkill):
    """火雨：全屏AOE"""

    def __init__(self, boss):
        super().__init__(boss)
        self.cooldown_max = 12.0

    def use(self, player, game):
        super().use(player, game)

        # 生成多个AOE区域
        from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y
        from enemy import AOEZone

        for _ in range(8):
            x = random.randint(ARENA_X + 50, ARENA_X + ARENA_W - 50)
            y = random.randint(ARENA_Y + 50, ARENA_Y + ARENA_H - 50)

            aoe = AOEZone(x, y, radius=60, damage=20, duration=2.0, color=(255, 100, 50, 120), attr=Attr.FIRE)

            if hasattr(game, "aoe_zones"):
                game.aoe_zones.append(aoe)

        # 屏幕震动
        from screen_shake import shake_screen

        shake_screen(0.5, 20)


class BossSummonWave(BossSkill):
    """召唤波：召唤一波小怪"""

    def __init__(self, boss):
        super().__init__(boss)
        self.cooldown_max = 15.0

    def use(self, player, game):
        super().use(player, game)

        # 召唤5个小怪
        from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y
        from enemy import Enemy

        for _ in range(5):
            x = random.randint(ARENA_X + 50, ARENA_X + ARENA_W - 50)
            y = random.randint(ARENA_Y + 50, ARENA_Y + ARENA_H - 50)

            minion = Enemy(
                x, y, health=30, damage=8, speed=120, ai_type="melee", attr=self.boss.attr, color=self.boss.color
            )

            if hasattr(game, "enemies"):
                game.enemies.append(minion)


class BossEnrage(BossSkill):
    """狂暴：提升所有属性"""

    def __init__(self, boss):
        super().__init__(boss)
        self.cooldown_max = 999.0  # 只触发一次
        self.used = False

    def use(self, player, game):
        if self.used:
            return

        super().use(player, game)
        self.used = True

        # 提升属性
        self.boss.damage = int(self.boss.damage * 1.5)
        self.boss.speed = int(self.boss.speed * 1.3)

        # 屏幕震动
        from screen_shake import shake_screen

        shake_screen(0.8, 30)


# ==================== Boss设计 ====================

BOSS_DESIGNS = {
    "boss_yaowang": {
        "phases": [
            BossPhase(1.0, [BossFireRain]),  # 100%-70%
            BossPhase(0.7, [BossFireRain, BossSummonWave]),  # 70%-30%
            BossPhase(0.3, [BossFireRain, BossSummonWave, BossEnrage]),  # 30%-0%
        ]
    },
}


def init_boss_skills(boss, boss_id):
    """初始化Boss技能"""
    design = BOSS_DESIGNS.get(boss_id)
    if not design:
        return

    boss.phases = design["phases"]
    boss.current_phase = 0
    boss.skills = []

    # 初始化第一阶段技能
    phase = boss.phases[0]
    for skill_class in phase.skills:
        boss.skills.append(skill_class(boss))
