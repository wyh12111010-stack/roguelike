"""
屏幕震动效果
用于增强打击感和视觉反馈
"""

import random


class ScreenShake:
    """屏幕震动管理器"""

    def __init__(self):
        self.shake_duration = 0.0  # 震动剩余时间
        self.shake_intensity = 0.0  # 震动强度
        self.offset_x = 0
        self.offset_y = 0

    def add_shake(self, duration=0.2, intensity=10):
        """添加震动效果"""
        # 如果当前震动更强，则保留
        if intensity > self.shake_intensity:
            self.shake_duration = duration
            self.shake_intensity = intensity

    def update(self, dt):
        """更新震动"""
        if self.shake_duration > 0:
            self.shake_duration -= dt

            # 计算当前强度（随时间衰减）
            progress = max(0, self.shake_duration / 0.2)
            current_intensity = self.shake_intensity * progress

            # 随机偏移
            self.offset_x = random.uniform(-current_intensity, current_intensity)
            self.offset_y = random.uniform(-current_intensity, current_intensity)
        else:
            self.offset_x = 0
            self.offset_y = 0
            self.shake_intensity = 0

    def get_offset(self):
        """获取当前偏移"""
        return int(self.offset_x), int(self.offset_y)

    def is_shaking(self):
        """是否正在震动"""
        return self.shake_duration > 0


# 全局实例
_screen_shake = None


def init_screen_shake():
    """初始化屏幕震动"""
    global _screen_shake
    _screen_shake = ScreenShake()
    return _screen_shake


def get_screen_shake():
    """获取屏幕震动管理器"""
    global _screen_shake
    if _screen_shake is None:
        _screen_shake = ScreenShake()
    return _screen_shake


def shake_screen(duration=0.2, intensity=10):
    """触发屏幕震动

    参数：
    - duration: 持续时间（秒）
    - intensity: 强度（像素）

    推荐值：
    - 轻微：duration=0.1, intensity=5
    - 中等：duration=0.2, intensity=10
    - 强烈：duration=0.3, intensity=20
    - Boss技能：duration=0.5, intensity=30
    """
    shake = get_screen_shake()
    shake.add_shake(duration, intensity)
