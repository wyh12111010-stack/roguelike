"""
粒子系统 - 元素效果表现（蒸发、感电、超载等）
通过 EventBus 订阅 PARTICLE_SPAWN 事件生成
"""
import math
import random
import pygame

from core.events import PARTICLE_SPAWN
from core import EventBus


class Particle:
    """单粒子：位置、速度、颜色、生命周期"""
    def __init__(self, x, y, vx, vy, color, lifetime=0.4, size=4, shrink=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.size = size
        self.shrink = shrink
        self.dead = False

    def update(self, dt):
        self.age += dt
        if self.age >= self.lifetime:
            self.dead = True
            return
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, screen):
        if self.dead:
            return
        progress = self.age / self.lifetime
        size = max(1, int(self.size * (1 - progress))) if self.shrink else self.size
        r, g, b = self.color[:3]
        color = (min(255, r), min(255, g), min(255, b))
        s = pygame.Surface((size * 2 + 4, size * 2 + 4))
        s.set_alpha(int(255 * (1 - progress)))
        s.set_colorkey((0, 0, 0))
        pygame.draw.circle(s, color, (size + 2, size + 2), size)
        screen.blit(s, (int(self.x) - size - 2, int(self.y) - size - 2))


def _spawn_burst(x, y, color, count=8, speed=80, lifetime=0.35):
    """中心爆散粒子"""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        spd = random.uniform(speed * 0.5, speed)
        vx = math.cos(angle) * spd
        vy = math.sin(angle) * spd
        # 增大粒子尺寸（5-7）
        particles.append(Particle(x, y, vx, vy, color, lifetime, size=random.randint(5, 7)))
    return particles


def _spawn_rising(x, y, color, count=6, speed=60, lifetime=0.5):
    """上升飘散（蒸发/蒸汽）"""
    particles = []
    for _ in range(count):
        vx = random.uniform(-30, 30)
        vy = -random.uniform(speed * 0.5, speed)
        # 增大粒子尺寸（4-6）
        particles.append(Particle(x, y, vx, vy, color, lifetime, size=random.randint(4, 6)))
    return particles


def _spawn_sparks(x, y, color, count=10, speed=120, lifetime=0.3):
    """电火花/爆炸火花"""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        spd = random.uniform(speed * 0.3, speed)
        vx = math.cos(angle) * spd
        vy = math.sin(angle) * spd
        particles.append(Particle(x, y, vx, vy, color, lifetime, size=random.randint(2, 4)))
    return particles


def _spawn_frost(x, y, color, count=5, speed=40, lifetime=0.4):
    """冰霜碎片"""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        spd = random.uniform(speed * 0.5, speed)
        vx = math.cos(angle) * spd
        vy = math.sin(angle) * spd
        particles.append(Particle(x, y, vx, vy, color, lifetime, size=random.randint(3, 5)))
    return particles


# 五行/反应对应的粒子效果（强化版：更多粒子、更快速度、更大尺寸、更长生命）
EFFECT_SPAWNERS = {
    # 五行基础
    "metal": lambda x, y: _spawn_burst(x, y, (200, 180, 120), 6, 60),
    "wood": lambda x, y: _spawn_burst(x, y, (80, 160, 80), 5, 50),
    "water": lambda x, y: _spawn_burst(x, y, (80, 150, 255), 5, 50),
    "fire": lambda x, y: _spawn_burst(x, y, (255, 120, 50), 6, 70),
    "earth": lambda x, y: _spawn_burst(x, y, (160, 120, 80), 5, 45),
    # 五行相克反应（强化：更多粒子、更快速度、更长生命）
    "jin_mu": lambda x, y: _spawn_burst(x, y, (200, 180, 120), 15, 180, 0.8),   # 金克木：斩木
    "mu_tu": lambda x, y: _spawn_burst(x, y, (80, 160, 80), 20, 200, 0.7),      # 木克土：破土
    "tu_shui": lambda x, y: _spawn_burst(x, y, (160, 120, 80), 12, 150, 1.0),   # 土克水：堵水
    "shui_huo": lambda x, y: _spawn_rising(x, y, (80, 150, 255), 18, 160, 0.9), # 水克火：灭火
    "huo_jin": lambda x, y: _spawn_burst(x, y, (255, 100, 50), 16, 140, 1.2),   # 火克金：熔金
    "hit": lambda x, y: _spawn_burst(x, y, (255, 100, 100), 4, 40),
    # Boss 全局技能读招/落地
    "boss_warn": lambda x, y: _spawn_rising(x, y, (255, 220, 130), 7, 70, 0.38),
    "boss_warn_fire": lambda x, y: _spawn_rising(x, y, (255, 150, 90), 7, 75, 0.38),
    "boss_warn_wood": lambda x, y: _spawn_rising(x, y, (155, 230, 155), 7, 70, 0.38),
    "boss_warn_earth": lambda x, y: _spawn_rising(x, y, (190, 170, 120), 7, 66, 0.38),
    "boss_cast": lambda x, y: _spawn_sparks(x, y, (255, 120, 120), 12, 135, 0.30),
    "boss_cast_fire": lambda x, y: _spawn_sparks(x, y, (255, 120, 70), 12, 145, 0.30),
    "boss_cast_wood": lambda x, y: _spawn_sparks(x, y, (130, 240, 170), 12, 130, 0.30),
    "boss_cast_earth": lambda x, y: _spawn_sparks(x, y, (180, 160, 120), 12, 120, 0.30),
    # 玩家普攻反馈
    "player_arc": lambda x, y: _spawn_burst(x, y, (255, 180, 90), 5, 55, 0.22),
    "player_pierce": lambda x, y: _spawn_sparks(x, y, (120, 210, 255), 4, 90, 0.20),
    "player_fan": lambda x, y: _spawn_burst(x, y, (150, 230, 150), 5, 65, 0.22),
    "player_heavy": lambda x, y: _spawn_burst(x, y, (255, 205, 130), 8, 80, 0.26),
    "player_parabolic": lambda x, y: _spawn_burst(x, y, (180, 160, 120), 6, 58, 0.24),
}


class ParticleManager:
    """管理粒子列表，订阅 PARTICLE_SPAWN"""
    def __init__(self):
        self.particles = []
        EventBus.on(PARTICLE_SPAWN, self._on_spawn)

    def _on_spawn(self, x=0, y=0, effect="hit", **kwargs):
        spawner = EFFECT_SPAWNERS.get(effect, EFFECT_SPAWNERS["hit"])
        self.particles.extend(spawner(x, y))

    def update(self, dt):
        # 先更新所有粒子
        for p in self.particles:
            p.update(dt)
        # 然后移除死亡的粒子（避免在迭代时修改列表）
        self.particles = [p for p in self.particles if not p.dead]

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

    def clear(self):
        self.particles.clear()


def spawn_particles(x, y, effect="hit"):
    """便捷：触发粒子生成"""
    EventBus.emit(PARTICLE_SPAWN, x=x, y=y, effect=effect)
