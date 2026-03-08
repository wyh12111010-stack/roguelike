"""核心层：事件总线、游戏状态、场景管理"""

from . import events
from .event_bus import EventBus
from .game_state import GameState
from .scene_manager import SceneManager

__all__ = ["EventBus", "GameState", "SceneManager", "events"]
