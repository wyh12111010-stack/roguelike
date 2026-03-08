"""敌人投射物与 AOE 区域"""

import math

import pygame

from attribute import Attr, attr_from_str
from enemy_sprites import load_enemy_sprite


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
            if dx * dx + dy * dy < self.radius**2:
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
