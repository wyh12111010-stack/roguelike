"""数据配置加载 - 敌人、关卡、演示"""
import json
import os


def _data_dir():
    return os.path.dirname(os.path.abspath(__file__))


def load_json(filename: str, default: dict = None) -> dict:
    """加载 JSON 配置，失败返回 default"""
    path = os.path.join(_data_dir(), filename)
    if not os.path.exists(path):
        return default or {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default or {}
