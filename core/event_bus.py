"""
事件总线 - 模块间解耦通信
重构：支持实例化（测试隔离）+ 保留类方法（向后兼容）。

用法（生产）：EventBus.emit("event_name", **kwargs) / EventBus.on("event_name", callback)
用法（测试）：bus = EventBus(); bus.emit(...) —— 独立实例，互不污染。
"""

from collections.abc import Callable
from typing import Any


class EventBus:
    """事件总线 - 实例化隔离 + 全局单例向后兼容。

    实例方法操作自身 _listeners；
    类方法操作共享的 _global 单例（向后兼容旧调用风格）。
    """

    # 全局默认实例（所有类方法操作此实例）
    _global: "EventBus" = None  # 延迟初始化

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    # ─── 实例方法 ───

    def subscribe(self, event: str, callback: Callable[..., None]) -> None:
        """订阅事件（实例级）"""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable[..., None] | None = None) -> None:
        """取消订阅（实例级）。callback 为 None 取消全部"""
        if event not in self._listeners:
            return
        if callback is None:
            self._listeners[event] = []
        else:
            self._listeners[event] = [c for c in self._listeners[event] if c != callback]

    def publish(self, event: str, **kwargs: Any) -> None:
        """发布事件（实例级）"""
        if event not in self._listeners:
            return
        for callback in self._listeners[event][:]:
            try:
                callback(**kwargs)
            except Exception as e:
                print(f"[EventBus] Error in {event} callback: {e}")

    def clear_all(self, event: str | None = None) -> None:
        """清空订阅（实例级）"""
        if event is None:
            self._listeners.clear()
        elif event in self._listeners:
            del self._listeners[event]

    # ─── 类方法（向后兼容，委托到全局实例）───

    @classmethod
    def _get_global(cls) -> "EventBus":
        if cls._global is None:
            cls._global = EventBus()
        return cls._global

    @classmethod
    def on(cls, event: str, callback: Callable[..., None]) -> None:
        """订阅事件（全局）"""
        cls._get_global().subscribe(event, callback)

    @classmethod
    def off(cls, event: str, callback: Callable[..., None] | None = None) -> None:
        """取消订阅（全局）"""
        cls._get_global().unsubscribe(event, callback)

    @classmethod
    def emit(cls, event: str, **kwargs: Any) -> None:
        """发布事件（全局）"""
        cls._get_global().publish(event, **kwargs)

    @classmethod
    def clear(cls, event: str | None = None) -> None:
        """清空订阅（全局）"""
        cls._get_global().clear_all(event)

    @classmethod
    def reset_global(cls) -> None:
        """重置全局实例（用于测试 teardown）"""
        cls._global = EventBus()
