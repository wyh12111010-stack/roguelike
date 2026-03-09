"""投射物 / 攻击判定，支持元素属性
对标 Tiny Rogues：爽点在弹道、射速、范围
"""

import math

import pygame

from config import ARENA_H, ARENA_Y, COLOR_PROJECTILE


class Projectile:
    """远程弹道"""

    def __init__(self, x, y, vx, vy, damage, lifetime=0.5, pierce=False, attr=None, self_reaction=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.lifetime = lifetime
        self.pierce = pierce
        self.attr = attr
        self.self_reaction = self_reaction  # 五行反应：灵根+法宝 或 法宝1+法宝2
        self.age = 0
        self.dead = False
        self.radius = 8
        self._hit_ids = set()

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        if self.age >= self.lifetime:
            self.dead = True

    def check_hit(self, enemies):
        for e in enemies:
            if e.dead or id(e) in self._hit_ids:
                continue
            dx = e.rect.centerx - self.x
            dy = e.rect.centery - self.y
            if dx * dx + dy * dy < (self.radius + 15) ** 2:
                e.take_damage(
                    self.damage, self.attr, enemies=enemies, self_reaction=getattr(self, "self_reaction", None)
                )
                self._hit_ids.add(id(e))
                if not self.pierce:
                    self.dead = True
                    break

    def draw(self, screen):
        if self.dead:
            return
        ix, iy = int(self.x), int(self.y)
        color = _attr_color(self.attr, COLOR_PROJECTILE)
        glow = _glow_color(color)
        # 拖尾
        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if speed > 10:
            nx, ny = -self.vx / speed, -self.vy / speed
            for i in range(3):
                tx = int(self.x + nx * (i + 1) * 6)
                ty = int(self.y + ny * (i + 1) * 6)
                tr = max(2, self.radius - i * 2)
                s = pygame.Surface((tr * 2, tr * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*glow, max(0, 100 - i * 35)), (tr, tr), tr)
                screen.blit(s, (tx - tr, ty - tr))
        # 外发光
        gr = self.radius + 4
        gs = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*glow, 60), (gr, gr), gr)
        screen.blit(gs, (ix - gr, iy - gr))
        # 核心
        pygame.draw.circle(screen, color, (ix, iy), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (ix - 2, iy - 2), max(1, self.radius // 3))


def _attr_color(attr, default):
    """根据五行属性返回颜色"""
    if attr is None:
        return default
    name = getattr(attr, "name", "")
    return {
        "FIRE": (255, 100, 50),
        "WATER": (80, 160, 255),
        "WOOD": (80, 220, 100),
        "METAL": (200, 210, 230),
        "EARTH": (200, 160, 80),
    }.get(name, default)


def _glow_color(color):
    """从基础色生成柔和发光色"""
    return (min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40))


class MeleeSlash:
    """近战挥砍判定，支持弧线宽度 arc_half（弧度）"""

    def __init__(self, x, y, angle, length, duration, damage, attr=None, arc_half=1.0, self_reaction=None):
        self.x = x
        self.y = y
        self.angle = angle
        self.length = length
        self.duration = duration
        self.damage = damage
        self.attr = attr
        self.self_reaction = self_reaction
        self.arc_half = arc_half  # 扇形半角，1.0≈60°，1.5≈90°，2.1≈120°
        self.age = 0
        self.dead = False
        self.hit_enemies = set()

    def update(self, dt):
        self.age += dt
        if self.age >= self.duration:
            self.dead = True

    def check_hit(self, enemies):
        if self.dead:
            return
        for e in enemies:
            if e.dead or id(e) in self.hit_enemies:
                continue
            dx = e.rect.centerx - self.x
            dy = e.rect.centery - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > self.length:
                continue
            angle_to = math.atan2(dy, dx)
            diff = abs((angle_to - self.angle + math.pi) % (2 * math.pi) - math.pi)
            if diff < self.arc_half:
                e.take_damage(
                    self.damage, self.attr, enemies=enemies, self_reaction=getattr(self, "self_reaction", None)
                )
                self.hit_enemies.add(id(e))

    def draw(self, screen):
        if self.dead:
            return
        progress = min(1.0, self.age / self.duration)
        color = _attr_color(self.attr, (255, 255, 150))
        glow = _glow_color(color)
        # 扇形弧线
        start_a = self.angle - self.arc_half
        sweep = self.arc_half * 2 * progress
        steps = max(4, int(sweep * 6))
        r = self.length * (0.5 + 0.5 * progress)
        # 绘制填充扇形（半透明）
        pts = [(int(self.x), int(self.y))]
        for i in range(steps + 1):
            a = start_a + sweep * i / steps
            pts.append((int(self.x + math.cos(a) * r), int(self.y + math.sin(a) * r)))
        if len(pts) >= 3:
            fade = max(0, int(180 * (1 - progress)))
            s = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            pygame.draw.polygon(s, (*color, fade), pts)
            screen.blit(s, (0, 0))
            pygame.draw.polygon(screen, glow, pts, 2)


class ParabolicProjectile:
    """抛物线弹道，落地或命中时 AOE 爆炸"""

    def __init__(self, x, y, vx, vy, damage, aoe_radius=60, gravity=600, attr=None, self_reaction=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.aoe_radius = aoe_radius
        self.gravity = gravity
        self.attr = attr
        self.self_reaction = self_reaction
        self.age = 0
        self.dead = False
        self._exploded = False
        self.radius = 10

    def update(self, dt):
        if self.dead:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.age += dt
        # 落地或超时爆炸
        ground = ARENA_Y + ARENA_H - 20
        if self.y >= ground or self.age >= 1.2:
            self._exploded = True

    def _do_explode(self, enemies):
        """AOE 伤害"""
        sr = getattr(self, "self_reaction", None)
        for e in enemies:
            if e.dead:
                continue
            dx = e.rect.centerx - self.x
            dy = e.rect.centery - self.y
            if dx * dx + dy * dy < self.aoe_radius**2:
                e.take_damage(self.damage, self.attr, enemies=enemies, self_reaction=sr)

    def check_hit(self, enemies):
        if self.dead:
            return
        if self._exploded:
            self._do_explode(enemies)
            self.dead = True
            return
        # 飞行中命中单体会提前爆炸
        for e in enemies:
            if e.dead:
                continue
            dx = e.rect.centerx - self.x
            dy = e.rect.centery - self.y
            if dx * dx + dy * dy < (self.radius + 15) ** 2:
                self._do_explode(enemies)
                self.dead = True
                return

    def draw(self, screen):
        if self.dead:
            return
        ix, iy = int(self.x), int(self.y)
        color = _attr_color(self.attr, (180, 160, 80))
        if self._exploded:
            # 爆炸环
            s = pygame.Surface((self.aoe_radius * 2, self.aoe_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, 40), (self.aoe_radius, self.aoe_radius), self.aoe_radius)
            pygame.draw.circle(s, (*_glow_color(color), 120), (self.aoe_radius, self.aoe_radius), self.aoe_radius, 3)
            screen.blit(s, (ix - self.aoe_radius, iy - self.aoe_radius))
            return
        # 飞行中：发光弹
        glow = _glow_color(color)
        gr = self.radius + 5
        gs = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*glow, 50), (gr, gr), gr)
        screen.blit(gs, (ix - gr, iy - gr))
        pygame.draw.circle(screen, color, (ix, iy), self.radius)
        # 落点预告（影子）
        ground = ARENA_Y + ARENA_H - 20
        shadow_y = min(iy + 20, ground)
        pygame.draw.ellipse(screen, (0, 0, 0, 60) if hasattr(pygame, 'SRCALPHA') else (40, 40, 40),
                            (ix - 6, shadow_y, 12, 4))


class FlameBeam:
    """烈焰冲击：直线粗火焰波，短持续"""

    def __init__(self, x, y, angle, length=180, width=45, duration=0.4, damage=35, attr=None, self_reaction=None):
        self.x = x
        self.y = y
        self.angle = angle
        self.length = length
        self.width = width
        self.duration = duration
        self.damage = damage
        self.attr = attr
        self.self_reaction = self_reaction
        self.age = 0
        self.dead = False
        self.hit_enemies = set()

    def update(self, dt):
        self.age += dt
        if self.age >= self.duration:
            self.dead = True

    def check_hit(self, enemies):
        if self.dead:
            return
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        half_w = self.width / 2
        for e in enemies:
            if e.dead or id(e) in self.hit_enemies:
                continue
            ex, ey = e.rect.centerx, e.rect.centery
            dx = ex - self.x
            dy = ey - self.y
            proj = dx * cos_a + dy * sin_a
            perp = abs(-dx * sin_a + dy * cos_a)
            if 0 <= proj <= self.length and perp <= half_w:
                e.take_damage(
                    self.damage, self.attr, enemies=enemies, self_reaction=getattr(self, "self_reaction", None)
                )
                self.hit_enemies.add(id(e))

    def draw(self, screen):
        if self.dead:
            return
        end_x = self.x + math.cos(self.angle) * self.length
        end_y = self.y + math.sin(self.angle) * self.length
        perp_x = -math.sin(self.angle) * self.width / 2
        perp_y = math.cos(self.angle) * self.width / 2
        pts = [
            (self.x + perp_x, self.y + perp_y),
            (self.x - perp_x, self.y - perp_y),
            (end_x - perp_x, end_y - perp_y),
            (end_x + perp_x, end_y + perp_y),
        ]
        progress = 1 - self.age / self.duration
        r = int(255 * progress)
        g = int(120 * progress)
        b = int(40 * progress)
        pygame.draw.polygon(screen, (r, g, b), pts)
        pygame.draw.polygon(screen, (255, 150, 60), pts, 2)


class SlowZone:
    """范围强减速（水牢/藤蔓）"""

    def __init__(self, x, y, radius=90, duration=3.5, slow_pct=70, slow_duration=1.5, color=(100, 180, 255)):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.slow_pct = slow_pct
        self.slow_duration = slow_duration
        self.color = color
        self.age = 0
        self.dead = False

    def update(self, dt):
        self.age += dt
        if self.age >= self.duration:
            self.dead = True

    def apply_to_enemies(self, enemies):
        for e in enemies:
            if e.dead:
                continue
            dx = e.rect.centerx - self.x
            dy = e.rect.centery - self.y
            if dx * dx + dy * dy < self.radius**2:
                e._superconduct_slow = self.slow_duration
                e._superconduct_slow_pct = self.slow_pct

    def draw(self, screen):
        if self.dead:
            return
        alpha = int(80 * (1 - self.age / self.duration))
        s = pygame.Surface((self.radius * 2, self.radius * 2))
        s.set_alpha(alpha)
        s.fill(self.color)
        screen.blit(s, (self.x - self.radius, self.y - self.radius))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius, 2)


class EarthWall:
    """土墙：反弹弹道 + 击退敌人"""

    def __init__(self, x, y, angle, width=70, height=25, duration=3.5, knockback=70):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.centerx = x
        self.rect.centery = y
        self.angle = angle
        self.duration = duration
        self.knockback = knockback
        self.age = 0
        self.dead = False

    def update(self, dt, enemies, enemy_projectiles, projectiles):
        self.age += dt
        if self.age >= self.duration:
            self.dead = True
            return
        # 反弹敌人弹道
        for p in enemy_projectiles[:]:
            if p.dead:
                continue
            px, py = int(p.x), int(p.y)
            if self.rect.collidepoint(px, py):
                p.dead = True
                ref = Projectile(p.x, p.y, -p.vx, -p.vy, p.damage, lifetime=1.0, pierce=True, attr=p.attr)
                projectiles.append(ref)
        # 击退敌人
        for e in enemies:
            if e.dead:
                continue
            if not self.rect.colliderect(e.rect):
                continue
            dx = e.rect.centerx - self.rect.centerx
            dy = e.rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                dx /= dist
                dy /= dist
                e.rect.x += int(dx * self.knockback)
                e.rect.y += int(dy * self.knockback)

    def draw(self, screen):
        if self.dead:
            return
        alpha = int(180 * (1 - self.age / self.duration))
        s = pygame.Surface((self.rect.w, self.rect.h))
        s.set_alpha(alpha)
        s.fill((140, 110, 70))
        screen.blit(s, self.rect)
        pygame.draw.rect(screen, (180, 150, 100), self.rect, 2)


class NeedleRainZone:
    """针雨区域：持续降下火针"""

    def __init__(self, x, y, radius, duration, tick_interval, damage_per_tick, attr, self_reaction):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.tick_interval = tick_interval
        self.damage_per_tick = damage_per_tick
        self.attr = attr
        self.self_reaction = self_reaction
        self.timer = 0
        self.tick_timer = 0
        self.dead = False

    def update(self, dt, enemies):
        self.timer += dt
        if self.timer >= self.duration:
            self.dead = True
            return

        self.tick_timer += dt
        if self.tick_timer >= self.tick_interval:
            self.tick_timer = 0
            # 对范围内所有敌人造成伤害
            for e in enemies:
                if e.dead:
                    continue
                dx = e.rect.centerx - self.x
                dy = e.rect.centery - self.y
                if dx * dx + dy * dy < self.radius * self.radius:
                    e.take_damage(self.damage_per_tick, self.attr, enemies=enemies, self_reaction=self.self_reaction)

    def draw(self, screen):
        if self.dead:
            return
        # 绘制红色圆圈表示范围
        alpha = int(100 * (1 - self.timer / self.duration))
        s = pygame.Surface((self.radius * 2, self.radius * 2))
        s.set_alpha(alpha)
        s.fill((255, 100, 50))
        screen.blit(s, (self.x - self.radius, self.y - self.radius))
        pygame.draw.circle(screen, (255, 100, 50), (int(self.x), int(self.y)), self.radius, 2)


class GravityFieldZone:
    """重力场：拉扯敌人 + 持续伤害"""

    def __init__(self, x, y, radius, duration, pull_strength, tick_interval, damage_per_tick, attr, self_reaction):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.pull_strength = pull_strength
        self.tick_interval = tick_interval
        self.damage_per_tick = damage_per_tick
        self.attr = attr
        self.self_reaction = self_reaction
        self.timer = 0
        self.tick_timer = 0
        self.dead = False

    def update(self, dt, enemies):
        self.timer += dt
        if self.timer >= self.duration:
            self.dead = True
            return

        # 拉扯敌人
        for e in enemies:
            if e.dead:
                continue
            dx = e.rect.centerx - self.x
            dy = e.rect.centery - self.y
            dist_sq = dx * dx + dy * dy
            if dist_sq < self.radius * self.radius and dist_sq > 1:
                dist = math.sqrt(dist_sq)
                # 向中心拉
                pull_x = -dx / dist * self.pull_strength * dt
                pull_y = -dy / dist * self.pull_strength * dt
                e.rect.x += pull_x
                e.rect.y += pull_y

        # 持续伤害
        self.tick_timer += dt
        if self.tick_timer >= self.tick_interval:
            self.tick_timer = 0
            for e in enemies:
                if e.dead:
                    continue
                dx = e.rect.centerx - self.x
                dy = e.rect.centery - self.y
                if dx * dx + dy * dy < self.radius * self.radius:
                    e.take_damage(self.damage_per_tick, self.attr, enemies=enemies, self_reaction=self.self_reaction)

    def draw(self, screen):
        if self.dead:
            return
        # 绘制棕色圆圈表示范围
        alpha = int(120 * (1 - self.timer / self.duration))
        s = pygame.Surface((self.radius * 2, self.radius * 2))
        s.set_alpha(alpha)
        s.fill((160, 120, 80))
        screen.blit(s, (self.x - self.radius, self.y - self.radius))
        pygame.draw.circle(screen, (160, 120, 80), (int(self.x), int(self.y)), self.radius, 2)
