"""节点层：可扩展的节点类型系统"""
from .base import NodeHandler, NodeContext, NodeStatus
from .registry import NodeRegistry

# 导入以触发节点注册
from . import combat  # noqa: F401
from . import shop    # noqa: F401

__all__ = ["NodeHandler", "NodeContext", "NodeStatus", "NodeRegistry"]
