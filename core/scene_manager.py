"""
场景管理器 - 场景注册、切换、委托 update/draw
"""
from typing import Dict, Optional, Type, Any

# 场景基类接口
SceneBase = Any  # 避免循环导入，实际为 Scene


class SceneManager:
    _scenes: Dict[str, type] = {}
    _current: Optional[Any] = None
    _current_name: str = ""

    @classmethod
    def register(cls, name: str, scene_class: Type) -> None:
        """注册场景类"""
        cls._scenes[name] = scene_class

    @classmethod
    def switch(cls, name: str, **kwargs) -> bool:
        """切换场景。返回是否成功"""
        if name not in cls._scenes:
            return False
        if cls._current:
            cls._current.exit()
        cls._current = cls._scenes[name](**kwargs)
        cls._current_name = name
        cls._current.enter()
        return True

    @classmethod
    def get_current(cls) -> Optional[Any]:
        return cls._current

    @classmethod
    def get_current_name(cls) -> str:
        return cls._current_name

    @classmethod
    def update(cls, dt: float) -> None:
        if cls._current and hasattr(cls._current, "update"):
            cls._current.update(dt)

    @classmethod
    def draw(cls, screen) -> None:
        if cls._current and hasattr(cls._current, "draw"):
            cls._current.draw(screen)

    @classmethod
    def handle_event(cls, event) -> bool:
        """处理事件，返回 True 表示已消费"""
        if cls._current and hasattr(cls._current, "handle_event"):
            return cls._current.handle_event(event)
        return False
