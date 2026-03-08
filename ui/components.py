"""
UI 组件基类 - 带类型注解和完整文档
使用 frontend-design Skill 的设计系统
"""

import pygame


# 设计系统 - 颜色（修仙古风）
class Colors:
    """颜色设计系统 - 修仙古风配色"""

    # 背景
    BG_DARK: tuple[int, int, int] = (15, 18, 25)
    PANEL_BG: tuple[int, int, int, int] = (20, 25, 35, 230)

    # 边框
    BORDER_GOLD: tuple[int, int, int] = (180, 150, 90)
    BORDER_DARK: tuple[int, int, int] = (100, 100, 120)

    # 强调色
    HP_RED: tuple[int, int, int] = (220, 60, 60)
    HP_RED_BG: tuple[int, int, int] = (50, 25, 25)
    MP_BLUE: tuple[int, int, int] = (60, 140, 200)
    MP_BLUE_BG: tuple[int, int, int] = (25, 45, 65)
    LINGSHI_GOLD: tuple[int, int, int] = (218, 165, 32)
    DAOYUN_JADE: tuple[int, int, int] = (64, 224, 208)

    # 文字
    TEXT_GOLD: tuple[int, int, int] = (255, 215, 0)
    TEXT_LIGHT: tuple[int, int, int] = (240, 230, 210)
    TEXT_GRAY: tuple[int, int, int] = (180, 170, 150)
    TEXT_DARK: tuple[int, int, int] = (120, 110, 100)

    # 元素颜色（五行）
    FIRE: tuple[int, int, int] = (255, 69, 0)
    WATER: tuple[int, int, int] = (30, 144, 255)
    WOOD: tuple[int, int, int] = (34, 139, 34)
    METAL: tuple[int, int, int] = (218, 165, 32)
    EARTH: tuple[int, int, int] = (139, 90, 43)


# 设计系统 - 间距
class Spacing:
    """间距设计系统 - 统一的间距标准"""

    XS: int = 4
    SM: int = 8
    MD: int = 12
    LG: int = 16
    XL: int = 24
    XXL: int = 32


# 设计系统 - 字体大小
class FontSize:
    """字体大小设计系统 - 统一的字体层级"""

    XS: int = 12
    SM: int = 14
    BASE: int = 18
    LG: int = 20
    XL: int = 24
    XXL: int = 36


class UIComponent:
    """
    UI 组件基类

    所有 UI 组件的基类，提供基础的更新、绘制和事件处理接口。

    Attributes:
        x (int): 组件 X 坐标
        y (int): 组件 Y 坐标
        width (int): 组件宽度
        height (int): 组件高度
        visible (bool): 是否可见
        hover (bool): 是否鼠标悬停
        alpha (int): 透明度 (0-255)
    """

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """
        初始化 UI 组件

        Args:
            x: 组件 X 坐标
            y: 组件 Y 坐标
            width: 组件宽度
            height: 组件高度
        """
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.visible: bool = True
        self.hover: bool = False
        self.alpha: int = 255

    def update(self, dt: float, mouse_pos: tuple[int, int]) -> None:
        """
        更新组件状态

        Args:
            dt: 时间增量（秒）
            mouse_pos: 鼠标位置 (x, y)
        """
        if self.visible:
            # 检查鼠标悬停
            mx, my = mouse_pos
            self.hover = self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height

    def draw(self, screen: pygame.Surface) -> None:
        """
        绘制组件

        Args:
            screen: pygame 绘制表面
        """
        if self.visible:
            self._draw_impl(screen)

    def _draw_impl(self, screen: pygame.Surface) -> None:
        """
        子类实现具体绘制逻辑

        Args:
            screen: pygame 绘制表面
        """
        pass

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        处理事件

        Args:
            event: pygame 事件

        Returns:
            bool: 是否处理了该事件
        """
        return False


class Panel(UIComponent):
    """
    面板组件 - 带边框和背景

    提供带有古风边框装饰的面板，支持半透明背景。

    Attributes:
        bg_color: 背景颜色 (R, G, B) 或 (R, G, B, A)
        border_color: 边框颜色 (R, G, B)
        border_width: 边框宽度
        corner_size: 角装饰大小
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        bg_color: tuple[int, ...] | None = None,
        border_color: tuple[int, int, int] | None = None,
    ) -> None:
        """
        初始化面板组件

        Args:
            x: 面板 X 坐标
            y: 面板 Y 坐标
            width: 面板宽度
            height: 面板高度
            bg_color: 背景颜色，默认为 Colors.PANEL_BG
            border_color: 边框颜色，默认为 Colors.BORDER_GOLD
        """
        super().__init__(x, y, width, height)
        self.bg_color: tuple[int, ...] = bg_color or Colors.PANEL_BG
        self.border_color: tuple[int, int, int] = border_color or Colors.BORDER_GOLD
        self.border_width: int = 2
        self.corner_size: int = 4

    def _draw_impl(self, screen: pygame.Surface) -> None:
        """绘制面板（背景 + 边框 + 角装饰）"""
        # 创建半透明表面
        if len(self.bg_color) == 4:  # 有 alpha 通道
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(surface, self.bg_color, (0, 0, self.width, self.height))
            screen.blit(surface, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))

        # 绘制边框
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), self.border_width)

        # 绘制四角装饰（简化版）
        corner = self.corner_size
        # 左上角
        pygame.draw.line(screen, self.border_color, (self.x, self.y + corner), (self.x, self.y), 3)
        pygame.draw.line(screen, self.border_color, (self.x, self.y), (self.x + corner, self.y), 3)
        # 右上角
        pygame.draw.line(
            screen, self.border_color, (self.x + self.width - corner, self.y), (self.x + self.width, self.y), 3
        )
        pygame.draw.line(
            screen, self.border_color, (self.x + self.width, self.y), (self.x + self.width, self.y + corner), 3
        )
        # 左下角
        pygame.draw.line(
            screen, self.border_color, (self.x, self.y + self.height - corner), (self.x, self.y + self.height), 3
        )
        pygame.draw.line(
            screen, self.border_color, (self.x, self.y + self.height), (self.x + corner, self.y + self.height), 3
        )
        # 右下角
        pygame.draw.line(
            screen,
            self.border_color,
            (self.x + self.width - corner, self.y + self.height),
            (self.x + self.width, self.y + self.height),
            3,
        )
        pygame.draw.line(
            screen,
            self.border_color,
            (self.x + self.width, self.y + self.height - corner),
            (self.x + self.width, self.y + self.height),
            3,
        )


class ProgressBar(UIComponent):
    """
    进度条组件 - 用于血条、蓝条

    支持动态更新、闪烁效果的进度条。

    Attributes:
        color: 填充颜色
        bg_color: 背景颜色
        value: 当前值 (0.0-1.0)
        max_value: 最大值
        flash_timer: 闪烁计时器
        flash_color: 闪烁颜色
    """

    def __init__(
        self, x: int, y: int, width: int, height: int, color: tuple[int, int, int], bg_color: tuple[int, int, int]
    ) -> None:
        """
        初始化进度条组件

        Args:
            x: 进度条 X 坐标
            y: 进度条 Y 坐标
            width: 进度条宽度
            height: 进度条高度
            color: 填充颜色
            bg_color: 背景颜色
        """
        super().__init__(x, y, width, height)
        self.color: tuple[int, int, int] = color
        self.bg_color: tuple[int, int, int] = bg_color
        self.value: float = 1.0  # 0.0 - 1.0
        self.max_value: float = 1.0
        self.flash_timer: float = 0.0
        self.flash_color: tuple[int, int, int] = (255, 255, 255)

    def set_value(self, current: float, maximum: float) -> None:
        """
        设置当前值和最大值

        Args:
            current: 当前值
            maximum: 最大值
        """
        old_value = self.value
        self.value = max(0.0, min(1.0, current / maximum if maximum > 0 else 0))
        self.max_value = maximum

        # 如果减少，触发闪烁
        if self.value < old_value:
            self.flash_timer = 0.3

    def update(self, dt: float, mouse_pos: tuple[int, int]) -> None:
        """更新进度条状态（包括闪烁效果）"""
        super().update(dt, mouse_pos)
        if self.flash_timer > 0:
            self.flash_timer -= dt

    def _draw_impl(self, screen: pygame.Surface) -> None:
        """绘制进度条（背景 + 填充 + 闪烁 + 边框）"""
        # 背景
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))

        # 填充
        fill_width = int(self.width * self.value)
        if fill_width > 0:
            pygame.draw.rect(screen, self.color, (self.x, self.y, fill_width, self.height))

        # 闪烁效果
        if self.flash_timer > 0:
            alpha = int(255 * (self.flash_timer / 0.3))
            flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_surface.fill((*self.flash_color, alpha))
            screen.blit(flash_surface, (self.x, self.y))

        # 边框
        pygame.draw.rect(screen, Colors.BORDER_DARK, (self.x, self.y, self.width, self.height), 1)


def draw_text(
    screen: pygame.Surface,
    text: str,
    x: int,
    y: int,
    size: int = FontSize.BASE,
    color: tuple[int, int, int] = Colors.TEXT_LIGHT,
    font_name: str | None = None,
    center: bool = False,
) -> tuple[int, int]:
    """
    绘制文字的辅助函数

    Args:
        screen: pygame 绘制表面
        text: 要绘制的文字
        x: X 坐标
        y: Y 坐标
        size: 字体大小，默认为 FontSize.BASE
        color: 文字颜色，默认为 Colors.TEXT_LIGHT
        font_name: 字体名称，None 使用默认字体
        center: 是否居中对齐

    Returns:
        Tuple[int, int]: 文字的宽度和高度
    """
    # 使用config.py中的get_font函数来支持中文
    try:
        from config import get_font

        font = get_font(size)
    except:
        # 如果导入失败，尝试系统字体
        try:
            font = pygame.font.SysFont("microsoftyahei", size)
        except:
            font = pygame.font.Font(None, size)

    text_surface = font.render(str(text), True, color)

    if center:
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)
    else:
        screen.blit(text_surface, (x, y))

    return text_surface.get_width(), text_surface.get_height()
