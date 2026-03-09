"""敌人投射物与 AOE 区域"""

import math

import pygame

from attribute import Attr, attr_from_str


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
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
                self.vx = dx / dist * speed * 0.15 + self.vx * 0.85
                self.vy = dy / dist * speed * 0.15 + self.vy * 0.85
        self.x += self.vx * dt
        self.y += self.vy * dt

    def check_hit_player(self, player):
        if self.dead or not player or player.health <= 0:
            return False
        dx = player.rect.centerx - self.x
        dy = player.rect.centery - self.y
        if dx * dx + dy * dy < (self.radius + 20) ** 2:
            player.take_damage(self.damage, self.attr)
            self.dead = True
            return True
        return False

    def draw(self, screen):
        if self.dead:
            return
        ix, iy = int(self.x), int(self.y)
        # 属性发光色
        attr_colors = {
            "FIRE": (255, 100, 50),
            "WATER": (80, 160, 255),
            "WOOD": (80, 220, 100),
            "METAL": (200, 210, 230),
            "EARTH": (200, 160, 80),
        }
        attr_name = getattr(self.attr, "name", "")
        glow_c = attr_colors.get(attr_name, self.color)
        # 外发光
        gr = self.radius + 3
        gs = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*glow_c, 50), (gr, gr), gr)
        screen.blit(gs, (ix - gr, iy - gr))
        # 核心
        pygame.draw.circle(screen, self.color, (ix, iy), self.radius)
        # 拖尾
        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if speed > 10:
            nx, ny = -self.vx / speed, -self.vy / speed
            for i in range(2):
                tx = int(self.x + nx * (i + 1) * 5)
                ty = int(self.y + ny * (i + 1) * 5)
                tr = max(2, self.radius - i * 2)
                ts = pygame.Surface((tr * 2, tr * 2), pygame.SRCALPHA)
                pygame.draw.circle(ts, (*self.color, max(0, 80 - i * 35)), (tr, tr), tr)
                screen.blit(ts, (tx - tr, ty - tr))


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
            if dx * dx + dy * dy < self.radius**2:
                player.take_damage(self.damage, self.attr)
                self._hit = True

    def draw(self, screen):
        if self.dead:
            return
        ix, iy = int(self.x), int(self.y)
        progress = self.age / self.duration if self.duration else 1
        alpha = int(100 * (1 - progress))
        r = self.radius
        # 半透明填充圆
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        c = self.color[:3]
        pygame.draw.circle(s, (*c, alpha), (r, r), r)
        screen.blit(s, (ix - r, iy - r))
        # 边框（脉动效果）
        pulse = 1.0 + 0.15 * math.sin(self.age * 8)
        border_r = int(r * pulse)
        border_alpha = min(255, alpha + 60)
        pygame.draw.circle(screen, (*c[:3], min(255, border_alpha)), (ix, iy), border_r, 2)
        # 内圈（伤害已触发则暗淡）
        if self._hit:
            pygame.draw.circle(screen, (100, 100, 100), (ix, iy), r // 2, 1)
