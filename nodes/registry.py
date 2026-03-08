"""
节点类型注册表 - 扩展新节点只需 register
"""

from .base import NodeHandler


class NodeRegistry:
    _handlers: dict[str, type[NodeHandler]] = {}

    @classmethod
    def register(cls, node_type: str, handler_class: type[NodeHandler]) -> None:
        """注册节点类型"""
        cls._handlers[node_type] = handler_class

    @classmethod
    def get(cls, node_type: str) -> type[NodeHandler] | None:
        """获取节点处理器类"""
        return cls._handlers.get(node_type)

    @classmethod
    def create(cls, node_type: str) -> NodeHandler | None:
        """创建节点处理器实例"""
        h = cls.get(node_type)
        return h() if h else None

    @classmethod
    def list_types(cls) -> list:
        """列出已注册的节点类型"""
        return list(cls._handlers.keys())


# 便捷别名
def register_node(node_type: str):
    """装饰器：注册节点类"""

    def decorator(handler_class: type[NodeHandler]):
        NodeRegistry.register(node_type, handler_class)
        return handler_class

    return decorator
