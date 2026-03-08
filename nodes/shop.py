"""
商店节点 - 花灵石购买
"""

from .base import NodeContext, NodeHandler, NodeStatus
from .registry import register_node


@register_node("shop")
class ShopNodeHandler(NodeHandler):
    node_type = "shop"

    def enter(self, ctx: NodeContext) -> None:
        pass

    def update(self, dt: float, ctx: NodeContext) -> NodeStatus:
        return NodeStatus.CONTINUE

    def draw(self, screen, ctx: NodeContext) -> None:
        pass

    def handle_event(self, event, ctx: NodeContext) -> bool:
        return False

    def exit(self, ctx: NodeContext) -> dict:
        return {}
