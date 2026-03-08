"""
UI 模块 - 使用 frontend-design Skill 的设计系统
"""

from ui.character_panel import CharacterPanel
from ui.combat_log import CombatLogUI  # 保持兼容
from ui.components import Colors, FontSize, Panel, ProgressBar, Spacing, UIComponent, draw_text
from ui.fabao_display import DualFabaoDisplay, FabaoDisplay
from ui.hud import HUD
from ui.ui_manager import UIManager

__all__ = [
    "HUD",
    "CharacterPanel",
    "Colors",
    "CombatLogUI",
    "DualFabaoDisplay",
    "FabaoDisplay",
    "FontSize",
    "Panel",
    "ProgressBar",
    "Spacing",
    "UIComponent",
    "UIManager",
    "draw_text",
]
