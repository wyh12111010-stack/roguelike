"""
UI 模块 - 使用 frontend-design Skill 的设计系统
"""
from ui.components import UIComponent, Panel, ProgressBar, Colors, Spacing, FontSize, draw_text
from ui.hud import HUD
from ui.fabao_display import FabaoDisplay, DualFabaoDisplay
from ui.character_panel import CharacterPanel
from ui.ui_manager import UIManager
from ui.combat_log import CombatLogUI  # 保持兼容

__all__ = [
    'UIComponent',
    'Panel',
    'ProgressBar',
    'Colors',
    'Spacing',
    'FontSize',
    'draw_text',
    'HUD',
    'FabaoDisplay',
    'DualFabaoDisplay',
    'CharacterPanel',
    'UIManager',
    'CombatLogUI',
]
