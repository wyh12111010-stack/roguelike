"""
事件总线 - 模块间解耦通信
用法：EventBus.emit("event_name", **kwargs) / EventBus.on("event_name", callback)
"""
from typing import Callable, Dict, List, Any


class EventBus:
    _listeners: Dict[str, List[Callable]] = {}

    @classmethod
    def on(cls, event: str, callback: Callable[..., None]) -> None:
        """订阅事件"""
        if event not in cls._listeners:
            cls._listeners[event] = []
        cls._listeners[event].append(callback)

    @classmethod
    def off(cls, event: str, callback: Callable[..., None] = None) -> None:
        """取消订阅。若 callback 为 None 则取消该事件所有订阅"""
        if event not in cls._listeners:
            return
        if callback is None:
            cls._listeners[event] = []
        else:
            cls._listeners[event] = [c for c in cls._listeners[event] if c != callback]

    @classmethod
    def emit(cls, event: str, **kwargs: Any) -> None:
        """发布事件"""
        if event not in cls._listeners:
            return
        for callback in cls._listeners[event][:]:
            try:
                callback(**kwargs)
            except Exception as e:
                print(f"[EventBus] Error in {event} callback: {e}")

    @classmethod
    def clear(cls, event: str = None) -> None:
        """清空订阅。若 event 为 None 则清空所有"""
        if event is None:
            cls._listeners.clear()
        elif event in cls._listeners:
            del cls._listeners[event]
