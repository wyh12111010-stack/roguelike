"""
增强粒子特效
为击杀、升级、获得物品等添加更好的视觉反馈
"""
import random
import math
from particles import Particle


# ==================== 击杀特效 ====================

def create_kill_particles(x, y, enemy_color):
    """击杀敌人时的粒子爆发"""
    particles = []
    
    # 主爆发（12个粒子）
    for _ in range(12):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(100, 200)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        # 使用敌人颜色
        r, g, b = enemy_color
        color = (
            min(255, r + random.randint(-30, 30)),
            min(255, g + random.randint(-30, 30)),
            min(255, b + random.randint(-30, 30))
        )
        
        particles.append(Particle(
            x, y, vx, vy,
            color=color,
            lifetime=0.6,
            size=random.randint(4, 7),
            shrink=True
        ))
    
    # 小火花（8个）
    for _ in range(8):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(150, 250)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        particles.append(Particle(
            x, y, vx, vy,
            color=(255, 255, 200),
            lifetime=0.3,
            size=random.randint(2, 4),
            shrink=True
        ))
    
    return particles


def create_elite_kill_particles(x, y, enemy_color):
    """击杀精英怪的特殊粒子"""
    particles = []
    
    # 更大的爆发（20个粒子）
    for _ in range(20):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(120, 250)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        r, g, b = enemy_color
        color = (
            min(255, r + 50),
            min(255, g + 50),
            min(255, b + 50)
        )
        
        particles.append(Particle(
            x, y, vx, vy,
            color=color,
            lifetime=0.8,
            size=random.randint(6, 10),
            shrink=True
        ))
    
    # 金色光芒（12个）
    for _ in range(12):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(80, 150)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        particles.append(Particle(
            x, y, vx, vy,
            color=(255, 215, 0),
            lifetime=1.0,
            size=random.randint(5, 8),
            shrink=True
        ))
    
    return particles


# ==================== 升级特效 ====================

def create_levelup_particles(x, y):
    """升级时的粒子特效"""
    particles = []
    
    # 上升的光柱（16个粒子）
    for i in range(16):
        angle = (i / 16) * 2 * math.pi
        radius = 30
        px = x + math.cos(angle) * radius
        py = y + math.sin(angle) * radius
        
        # 向上飘
        vx = math.cos(angle) * 20
        vy = -random.uniform(100, 150)
        
        particles.append(Particle(
            px, py, vx, vy,
            color=(255, 255, 100),
            lifetime=1.2,
            size=6,
            shrink=True
        ))
    
    # 中心爆发（8个）
    for _ in range(8):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 100)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        particles.append(Particle(
            x, y, vx, vy,
            color=(255, 215, 0),
            lifetime=0.8,
            size=8,
            shrink=True
        ))
    
    return particles


# ==================== 获得物品特效 ====================

def create_item_get_particles(x, y, item_type="common"):
    """获得物品时的粒子特效
    
    item_type: common | rare | epic | legendary
    """
    particles = []
    
    # 根据稀有度选择颜色
    colors = {
        "common": (200, 200, 200),
        "rare": (100, 150, 255),
        "epic": (200, 100, 255),
        "legendary": (255, 215, 0),
    }
    color = colors.get(item_type, (200, 200, 200))
    
    # 螺旋上升（12个粒子）
    for i in range(12):
        angle = (i / 12) * 2 * math.pi
        radius = 20 + i * 3
        px = x + math.cos(angle) * radius
        py = y + math.sin(angle) * radius
        
        vx = 0
        vy = -80
        
        particles.append(Particle(
            px, py, vx, vy,
            color=color,
            lifetime=1.0,
            size=5,
            shrink=True
        ))
    
    # 闪光（6个）
    for _ in range(6):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(60, 120)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        particles.append(Particle(
            x, y, vx, vy,
            color=(255, 255, 255),
            lifetime=0.5,
            size=4,
            shrink=True
        ))
    
    return particles


# ==================== 治疗特效 ====================

def create_heal_particles(x, y):
    """治疗时的粒子特效"""
    particles = []
    
    # 绿色上升粒子（10个）
    for _ in range(10):
        vx = random.uniform(-30, 30)
        vy = -random.uniform(60, 100)
        
        particles.append(Particle(
            x + random.uniform(-20, 20),
            y + random.uniform(-20, 20),
            vx, vy,
            color=(100, 255, 100),
            lifetime=0.8,
            size=5,
            shrink=True
        ))
    
    # 白色闪光（4个）
    for _ in range(4):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(40, 80)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        particles.append(Particle(
            x, y, vx, vy,
            color=(200, 255, 200),
            lifetime=0.4,
            size=6,
            shrink=True
        ))
    
    return particles


# ==================== 暴击特效 ====================

def create_crit_particles(x, y):
    """暴击时的粒子特效"""
    particles = []
    
    # 金色爆发（8个）
    for _ in range(8):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(120, 180)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        particles.append(Particle(
            x, y, vx, vy,
            color=(255, 255, 100),
            lifetime=0.5,
            size=6,
            shrink=True
        ))
    
    # 星星闪光（4个）
    for _ in range(4):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(80, 120)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        particles.append(Particle(
            x, y, vx, vy,
            color=(255, 215, 0),
            lifetime=0.6,
            size=8,
            shrink=True
        ))
    
    return particles


# ==================== 技能释放特效 ====================

def create_skill_cast_particles(x, y, element_color):
    """技能释放时的粒子特效"""
    particles = []
    
    # 环形扩散（12个）
    for i in range(12):
        angle = (i / 12) * 2 * math.pi
        speed = 100
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        particles.append(Particle(
            x, y, vx, vy,
            color=element_color,
            lifetime=0.6,
            size=5,
            shrink=True
        ))
    
    # 中心光芒（6个）
    for _ in range(6):
        vx = random.uniform(-40, 40)
        vy = random.uniform(-40, 40)
        
        particles.append(Particle(
            x, y, vx, vy,
            color=(255, 255, 255),
            lifetime=0.4,
            size=7,
            shrink=True
        ))
    
    return particles


# ==================== 便捷函数 ====================

def spawn_kill_effect(x, y, enemy_color, is_elite=False, particle_mgr=None):
    """生成击杀特效"""
    if particle_mgr is None:
        return
    
    if is_elite:
        particles = create_elite_kill_particles(x, y, enemy_color)
    else:
        particles = create_kill_particles(x, y, enemy_color)
    
    particle_mgr.particles.extend(particles)


def spawn_levelup_effect(x, y, particle_mgr=None):
    """生成升级特效"""
    if particle_mgr is None:
        return
    
    particles = create_levelup_particles(x, y)
    particle_mgr.particles.extend(particles)


def spawn_item_get_effect(x, y, item_type="common", particle_mgr=None):
    """生成获得物品特效"""
    if particle_mgr is None:
        return
    
    particles = create_item_get_particles(x, y, item_type)
    particle_mgr.particles.extend(particles)


def spawn_heal_effect(x, y, particle_mgr=None):
    """生成治疗特效"""
    if particle_mgr is None:
        return
    
    particles = create_heal_particles(x, y)
    particle_mgr.particles.extend(particles)


def spawn_crit_effect(x, y, particle_mgr=None):
    """生成暴击特效"""
    if particle_mgr is None:
        return
    
    particles = create_crit_particles(x, y)
    particle_mgr.particles.extend(particles)


def spawn_skill_cast_effect(x, y, element_color, particle_mgr=None):
    """生成技能释放特效"""
    if particle_mgr is None:
        return
    
    particles = create_skill_cast_particles(x, y, element_color)
    particle_mgr.particles.extend(particles)
