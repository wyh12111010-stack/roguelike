"""
场景基类 - 所有场景实现此接口
"""

from abc import ABC, abstractmethod


class Scene(ABC):
    """场景接口"""

    @abstractmethod
    def enter(self) -> None:
        """进入场景"""
        pass

    def update(self, dt: float) -> None:
        """每帧更新"""
        pass

    @abstractmethod
    def draw(self, screen) -> None:
        """绘制"""
        pass

    def handle_event(self, event) -> bool:
        """处理事件，返回 True 表示已消费"""
        return False

    def exit(self) -> None:
        """离开场景"""
        pass
