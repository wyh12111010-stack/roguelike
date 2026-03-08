"""
节点基类 - 所有节点类型实现此接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class NodeStatus(Enum):
    """节点执行状态"""

    CONTINUE = "continue"  # 继续执行
    COMPLETE = "complete"  # 完成，进入下一节点
    FAIL = "fail"  # 失败（如身陨）


@dataclass
class NodeContext:
    """节点执行上下文"""

    node_index: int
    node_type: str
    node_config: dict
    player: Any
    run_data: Any
    meta: Any
    # 扩展：可传入 screen、combat_data 等
    extra: dict = None

    def __post_init__(self):
        if self.extra is None:
            self.extra = {}


class NodeHandler(ABC):
    """节点处理器基类 - 新节点类型继承此类并注册"""

    node_type: str = "base"

    @abstractmethod
    def enter(self, ctx: NodeContext) -> None:
        """进入节点时调用"""
        pass

    def update(self, dt: float, ctx: NodeContext) -> NodeStatus:
        """每帧更新，默认返回 CONTINUE"""
        return NodeStatus.CONTINUE

    def draw(self, screen, ctx: NodeContext) -> None:
        """绘制"""
        pass

    def handle_event(self, event, ctx: NodeContext) -> bool:
        """处理输入，返回 True 表示已消费"""
        return False

    def exit(self, ctx: NodeContext) -> dict:
        """离开节点时返回结果（奖励/消耗等）"""
        return {}
