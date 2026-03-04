"""
响应式UI系统
基于frontend-design skill的设计原则
"""
import pygame


class ResponsiveUI:
    """响应式UI管理器 - 根据分辨率自动调整"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 基准分辨率（设计时的分辨率）
        self.base_width = 1600
        self.base_height = 900
        
        # 计算缩放比例
        self.scale_x = screen_width / self.base_width
        self.scale_y = screen_height / self.base_height
        self.scale = min(self.scale_x, self.scale_y)  # 保持比例
        
        # 间距系统（基于8px基准）
        self.spacing = {
            'xs': int(4 * self.scale),
            'sm': int(8 * self.scale),
            'md': int(12 * self.scale),
            'lg': int(16 * self.scale),
            'xl': int(24 * self.scale),
            'xxl': int(32 * self.scale),
        }
        
        # 字体大小（响应式）
        self.font_sizes = {
            'xs': int(12 * self.scale),
            'sm': int(14 * self.scale),
            'base': int(18 * self.scale),
            'lg': int(20 * self.scale),
            'xl': int(24 * self.scale),
            'xxl': int(36 * self.scale),
        }
        
        # UI区域定义
        self._calculate_ui_areas()
    
    def _calculate_ui_areas(self):
        """计算UI区域"""
        # 左侧UI面板
        self.left_panel = {
            'x': self.spacing['lg'],
            'y': self.spacing['lg'],
            'width': int(240 * self.scale),
            'height': self.screen_height - self.spacing['lg'] * 2,
        }
        
        # 战斗区域（右侧）
        arena_margin = self.spacing['xl']
        self.arena = {
            'x': self.left_panel['x'] + self.left_panel['width'] + self.spacing['lg'],
            'y': arena_margin,
            'width': self.screen_width - (self.left_panel['x'] + self.left_panel['width'] + self.spacing['lg']) - arena_margin,
            'height': self.screen_height - arena_margin * 2,
        }
    
    def scale_value(self, value):
        """缩放数值"""
        return int(value * self.scale)
    
    def get_font_size(self, size_name='base'):
        """获取字体大小"""
        return self.font_sizes.get(size_name, self.font_sizes['base'])
    
    def get_spacing(self, spacing_name='md'):
        """获取间距"""
        return self.spacing.get(spacing_name, self.spacing['md'])


# 全局实例
_responsive_ui = None


def init_responsive_ui(screen_width, screen_height):
    """初始化响应式UI"""
    global _responsive_ui
    _responsive_ui = ResponsiveUI(screen_width, screen_height)
    return _responsive_ui


def get_responsive_ui():
    """获取响应式UI实例"""
    global _responsive_ui
    if _responsive_ui is None:
        _responsive_ui = ResponsiveUI(1600, 900)
    return _responsive_ui
