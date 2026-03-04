"""
游戏状态 - 集中管理全局状态，单例
"""
from dataclasses import dataclass, field
from typing import Optional, List, Any

# 延迟导入避免循环
_instance: Optional["GameState"] = None


@dataclass
class RunData:
    """本局运行数据"""
    kill_count: int = 0
    current_node_index: int = 0
    lingshi: int = 0
    route_history: List[int] = field(default_factory=list)
    # 可扩展：饰品列表、伙伴、buff 等


class GameState:
    """游戏全局状态"""

    def __init__(self):
        self.current_scene: str = "village"
        self.run_data: RunData = RunData()
        self.meta = None  # 由外部注入 meta 模块
        self.player = None
        self.screen = None
        # 闯关模式下的临时数据（敌人、投射物等）
        self._combat_data: dict = {}

    @classmethod
    def get(cls) -> "GameState":
        """获取单例"""
        global _instance
        if _instance is None:
            _instance = cls()
        return _instance

    @classmethod
    def reset(cls) -> None:
        """重置单例（用于测试或新游戏）"""
        global _instance
        _instance = None

    def set_meta(self, meta) -> None:
        self.meta = meta

    def set_player(self, player) -> None:
        self.player = player

    def set_combat_data(self, **kwargs) -> None:
        self._combat_data.update(kwargs)

    def get_combat_data(self, key: str, default=None):
        return self._combat_data.get(key, default)

    def clear_combat_data(self) -> None:
        self._combat_data.clear()
