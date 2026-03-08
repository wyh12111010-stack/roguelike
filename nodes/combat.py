"""
战斗节点 - 清敌后过关
"""

from .base import NodeContext, NodeHandler, NodeStatus
from .registry import register_node


@register_node("combat")
class CombatNodeHandler(NodeHandler):
    node_type = "combat"

    def enter(self, ctx: NodeContext) -> None:
        """进入时由外部加载敌人，此处可做初始化"""
        pass

    def update(self, dt: float, ctx: NodeContext) -> NodeStatus:
        """战斗逻辑由 RunScene/Game 主循环处理，此处仅占位"""
        return NodeStatus.CONTINUE

    def draw(self, screen, ctx: NodeContext) -> None:
        pass

    def exit(self, ctx: NodeContext) -> dict:
        """过关时返回奖励"""
        return {"lingshi": 10, "daoyun": 3}
