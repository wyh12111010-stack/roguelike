"""
UI 管理器 - 统一管理所有 UI 组件
"""

import pygame

from ui.character_panel import CharacterPanel
from ui.fabao_display import FabaoDisplay
from ui.hud import HUD


class UIManager:
    """
    UI 管理器

    统一管理所有 UI 组件，包括 HUD、法宝显示、角色面板等。
    负责组件的创建、更新、绘制和事件处理。

    Attributes:
        screen_width (int): 屏幕宽度
        screen_height (int): 屏幕高度
        hud (HUD): HUD 组件
        fabao_display (FabaoDisplay): 法宝显示组件
        character_panel (CharacterPanel): 角色面板组件
        player: 玩家对象引用
    """

    def __init__(self, screen_width: int = 800, screen_height: int = 600) -> None:
        """
        初始化 UI 管理器

        Args:
            screen_width: 屏幕宽度，默认 800
            screen_height: 屏幕高度，默认 600
        """
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height

        # 创建 UI 组件
        self.hud: HUD = HUD(x=10, y=10)
        self.fabao_display: FabaoDisplay = FabaoDisplay(x=10, y=300)
        self.character_panel: CharacterPanel = CharacterPanel(screen_width, screen_height)

        self.player: object | None = None

    def set_player(self, player: object) -> None:
        """
        设置玩家引用

        Args:
            player: 玩家对象
        """
        self.player = player
        self.hud.set_player(player)
        self.fabao_display.set_player(player)
        self.character_panel.set_player(player)

    def update(self, dt: float) -> None:
        """
        更新所有 UI 组件

        Args:
            dt: 时间增量（秒）
        """
        if not self.player:
            return

        mouse_pos = pygame.mouse.get_pos()

        # 更新 HUD
        self.hud.update(dt, mouse_pos)

        # 更新法宝显示
        self.fabao_display.update(dt, mouse_pos)

        # 更新角色面板
        if self.character_panel.visible:
            self.character_panel.update(dt, mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        """
        绘制所有 UI 组件

        Args:
            screen: pygame 绘制表面
        """
        if not self.player:
            return

        # 绘制 HUD（始终显示）
        self.hud.draw(screen)

        # 绘制法宝显示（始终显示）
        self.fabao_display.draw(screen)

        # 绘制角色面板（按需显示）
        if self.character_panel.visible:
            self.character_panel.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        处理事件

        Args:
            event: pygame 事件

        Returns:
            bool: 是否处理了该事件
        """
        # 角色面板优先处理事件
        if self.character_panel.visible and self.character_panel.handle_event(event):
            return True

        # 打开角色面板
        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            self.character_panel.toggle()
            return True

        return False

    def is_panel_open(self) -> bool:
        """
        检查是否有面板打开

        Returns:
            bool: 是否有面板打开
        """
        return self.character_panel.visible
