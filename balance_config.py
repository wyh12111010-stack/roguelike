"""
balance_config - YAML 驱动的游戏平衡配置加载器。

用法:
    from balance_config import cfg
    speed = cfg("player.base_speed")          # -> 200
    colors = cfg("colors.player")             # -> (100, 200, 255)
    rewards = cfg("treasure_rewards")         # -> [{"type":"potion","amount":1}, ...]

设计:
    - 启动时读取 data/balance.yaml（若存在）。
    - 通过 dot-path 访问嵌套值。
    - 缺失键返回 default 参数（默认 None），不抛异常。
    - reload() 支持运行时热重载。
"""

from __future__ import annotations

import os
from typing import Any

_DATA: dict = {}
_YAML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "balance.yaml")


def _load_yaml(path: str) -> dict:
    """Load YAML file, return empty dict on failure."""
    try:
        import yaml

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def reload() -> None:
    """(Re)load balance config from YAML."""
    global _DATA
    _DATA = _load_yaml(_YAML_PATH)


def cfg(path: str, default: Any = None) -> Any:
    """Retrieve a value by dot-separated path.

    Examples:
        cfg("player.base_speed")  -> 200
        cfg("economy.lingshi_per_kill")  -> 5
        cfg("colors.player")  -> [100, 200, 255]
    """
    if not _DATA:
        reload()
    node: Any = _DATA
    for key in path.split("."):
        if isinstance(node, dict) and key in node:
            node = node[key]
        else:
            return default
    return node


# Auto-load on first import
reload()
