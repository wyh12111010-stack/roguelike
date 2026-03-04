"""
伤害飘字系统
显示伤害数字、暴击、治疗等文本效果
"""
import pygame
import random
from config import get_font


class DamageText:
    """单个伤害飘字"""
    def __init__(self, x, y, text, color=(255, 255, 255), size=24, is_crit=False):
        self.x = x
        self.y = y
        self.text = str(text)
        self.color = color
        self.size = size
        self.is_crit = is_crit
        
        # 动画参数
        self.lifetime = 1.0  # 持续时间
        self.age = 0.0
        self.dead = False
        
        # 移动参数
        self.vx = random.uniform(-20, 20)
        self.vy = -60  # 向上飘
        self.gravity = 80  # 重力（减速上升）
        
        # 暴击特效
        if is_crit:
            self.size = 32
            self.color = (255, 255, 100)  # 金色
            self.lifetime = 1.2
            self.vy = -80
    
    def update(self, dt):
        self.age += dt
        if self.age >= self.lifetime:
            self.dead = True
            return
        
        # 移动
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt  # 减速
    
    def draw(self, screen):
        if self.dead:
            return
        
        # 淡出效果
        progress = self.age / self.lifetime
        alpha = int(255 * (1 - progress))
        
        # 渲染文本
        font = get_font(self.size)
        text_surface = font.render(self.text, True, self.color)
        
        # 应用透明度
        text_surface.set_alpha(alpha)
        
        # 暴击放大效果
        if self.is_crit and progress < 0.3:
            scale = 1.0 + (1 - progress / 0.3) * 0.3  # 前30%时间放大
            w, h = text_surface.get_size()
            text_surface = pygame.transform.scale(
                text_surface,
                (int(w * scale), int(h * scale))
            )
        
        # 绘制
        w, h = text_surface.get_size()
        screen.blit(text_surface, (int(self.x - w // 2), int(self.y - h // 2)))


class DamageTextManager:
    """管理所有伤害飘字"""
    def __init__(self):
        self.texts = []
    
    def add_damage(self, x, y, damage, is_crit=False):
        """添加伤害数字"""
        color = (255, 255, 100) if is_crit else (255, 100, 100)
        text = f"-{int(damage)}"
        if is_crit:
            text = f"暴击! {text}"
        self.texts.append(DamageText(x, y, text, color, is_crit=is_crit))
    
    def add_heal(self, x, y, heal):
        """添加治疗数字"""
        text = f"+{int(heal)}"
        self.texts.append(DamageText(x, y, text, (100, 255, 100), size=20))
    
    def add_text(self, x, y, text, color=(255, 255, 255), size=24):
        """添加自定义文本"""
        self.texts.append(DamageText(x, y, text, color, size))
    
    def update(self, dt):
        """更新所有飘字"""
        for text in self.texts[:]:
            text.update(dt)
            if text.dead:
                self.texts.remove(text)
    
    def draw(self, screen):
        """绘制所有飘字"""
        for text in self.texts:
            text.draw(screen)
    
    def clear(self):
        """清空所有飘字"""
        self.texts.clear()


# 全局实例（在game.py中初始化）
_damage_text_manager = None


def init_damage_text_manager():
    """初始化伤害飘字管理器"""
    global _damage_text_manager
    _damage_text_manager = DamageTextManager()
    return _damage_text_manager


def get_damage_text_manager():
    """获取伤害飘字管理器"""
    global _damage_text_manager
    if _damage_text_manager is None:
        _damage_text_manager = DamageTextManager()
    return _damage_text_manager


def show_damage(x, y, damage, is_crit=False):
    """显示伤害飘字"""
    manager = get_damage_text_manager()
    manager.add_damage(x, y, damage, is_crit)


def show_heal(x, y, heal):
    """显示治疗飘字"""
    manager = get_damage_text_manager()
    manager.add_heal(x, y, heal)


def show_text(x, y, text, color=(255, 255, 255), size=24):
    """显示自定义文本"""
    manager = get_damage_text_manager()
    manager.add_text(x, y, text, color, size)
