"""
故事线 - 序章、节点剧情、结局
"""

from dataclasses import dataclass


@dataclass
class StoryNode:
    """剧情节点"""

    id: str
    trigger: str  # 触发条件：level_0, route_1, victory, death
    title: str
    text: str


# 序章（从 setting 导入世界观）
from setting import GOAL_DESC, WORLD

PROLOGUE = {
    "title": "轮回",
    "text": f"{WORLD.overview} 你身负世界意志，拥有轮回之力，不被污染，是唯一能外出之人。",
    "text2": GOAL_DESC,
}

# 节点剧情：关卡/路线触发
STORY_NODES: dict[str, StoryNode] = {
    "level_0_clear": StoryNode(
        "level_0_clear",
        "level_0_clear",
        "初战告捷",
        "敌尽，前方出现数道入口，通往不同试炼之地。",
    ),
    "route_trial": StoryNode(
        "route_trial",
        "route_1",
        "试炼之路",
        "你选择了试炼入口，前方传来剑鸣之声。",
    ),
    "route_secret": StoryNode(
        "route_secret",
        "route_2",
        "秘境之路",
        "秘境深处，灵气浓郁，却也暗藏凶险。",
    ),
    "route_danger": StoryNode(
        "route_danger",
        "route_3",
        "凶地之路",
        "凶地煞气逼人，唯有强者可存。",
    ),
}

# 结局
ENDINGS = {
    "victory": {
        "title": "凯旋",
        "text": "你闯过重重险阻，携道韵归来。村中众人有望了。",
    },
    "death": {
        "title": "身陨",
        "text": "你倒在了被污染的外界。轮回再起，下一世再战。",
    },
}


def get_node_by_trigger(trigger: str) -> StoryNode | None:
    """根据触发条件获取剧情节点"""
    for node in STORY_NODES.values():
        if node.trigger == trigger:
            return node
    return None


def get_ending(key: str) -> dict:
    """获取结局文本"""
    return ENDINGS.get(key, ENDINGS["death"])
