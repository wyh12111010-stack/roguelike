"""
摄像机系统
让视角跟随玩家移动
"""
import pygame


class Camera:
    """摄像机类 - 跟随玩家"""
    
    def __init__(self, arena_x, arena_y, arena_w, arena_h):
        """
        初始化摄像机
        
        Args:
            arena_x: 战斗区域X坐标
            arena_y: 战斗区域Y坐标
            arena_w: 战斗区域宽度
            arena_h: 战斗区域高度
        """
        self.arena_x = arena_x
        self.arena_y = arena_y
        self.arena_w = arena_w
        self.arena_h = arena_h
        
        # 摄像机位置（世界坐标）
        self.x = 0
        self.y = 0
        
        # 目标位置（平滑跟随）
        self.target_x = 0
        self.target_y = 0
        
        # 跟随速度（0-1，越大越快）
        self.follow_speed = 0.1
        
        # 世界大小（可以比战斗区域大）
        self.world_w = arena_w * 2
        self.world_h = arena_h * 2
    
    def follow(self, target_x, target_y):
        """
        跟随目标
        
        Args:
            target_x: 目标X坐标（世界坐标）
            target_y: 目标Y坐标（世界坐标）
        """
        # 计算摄像机应该在的位置（让目标在屏幕中心）
        self.target_x = target_x - self.arena_w // 2
        self.target_y = target_y - self.arena_h // 2
        
        # 限制摄像机范围
        self.target_x = max(0, min(self.target_x, self.world_w - self.arena_w))
        self.target_y = max(0, min(self.target_y, self.world_h - self.arena_h))
    
    def update(self, dt):
        """
        更新摄像机位置（平滑移动）
        
        Args:
            dt: 时间增量
        """
        # 平滑插值
        self.x += (self.target_x - self.x) * self.follow_speed
        self.y += (self.target_y - self.y) * self.follow_speed
    
    def apply(self, world_x, world_y):
        """
        将世界坐标转换为屏幕坐标
        
        Args:
            world_x: 世界X坐标
            world_y: 世界Y坐标
            
        Returns:
            (screen_x, screen_y): 屏幕坐标
        """
        screen_x = world_x - self.x + self.arena_x
        screen_y = world_y - self.y + self.arena_y
        return int(screen_x), int(screen_y)
    
    def apply_rect(self, rect):
        """
        将世界坐标的矩形转换为屏幕坐标
        
        Args:
            rect: pygame.Rect（世界坐标）
            
        Returns:
            pygame.Rect: 屏幕坐标的矩形
        """
        screen_x, screen_y = self.apply(rect.x, rect.y)
        return pygame.Rect(screen_x, screen_y, rect.width, rect.height)
    
    def is_visible(self, world_x, world_y, margin=100):
        """
        检查世界坐标是否在屏幕可见范围内
        
        Args:
            world_x: 世界X坐标
            world_y: 世界Y坐标
            margin: 边缘余量
            
        Returns:
            bool: 是否可见
        """
        return (self.x - margin <= world_x <= self.x + self.arena_w + margin and
                self.y - margin <= world_y <= self.y + self.arena_h + margin)


# 全局实例
_camera = None


def init_camera(arena_x, arena_y, arena_w, arena_h):
    """初始化摄像机"""
    global _camera
    _camera = Camera(arena_x, arena_y, arena_w, arena_h)
    return _camera


def get_camera():
    """获取摄像机实例"""
    global _camera
    return _camera
