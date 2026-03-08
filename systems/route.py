"""
路线系统 - 根据路线树返回可选下一节点
设计对标 Tiny Rogues + 星座战士：每层 2/3 选，奖励类型在选路时随机抽取（非固定循环）
"""

import random

# 战斗关奖励池：灵石/饰品常见，法宝较少，道韵最少（与已拍板方案一致）
COMBAT_REWARD_WEIGHTS = {
    "lingshi": 0.40,
    "accessory": 0.36,
    "fabao": 0.18,
    "daoyun": 0.06,
}
COMBAT_REWARD_POOL = [
    "lingshi",
    "lingshi",
    "lingshi",
    "lingshi",
    "accessory",
    "accessory",
    "accessory",
    "accessory",
    "fabao",
    "fabao",
    "daoyun",
]
_RARE_REWARDS = {"fabao", "daoyun"}


def _roll_combat_reward(allow_rare=True):
    items = list(COMBAT_REWARD_WEIGHTS.keys())
    weights = []
    for k in items:
        w = COMBAT_REWARD_WEIGHTS[k]
        if (not allow_rare) and (k in _RARE_REWARDS):
            w = 0.0
        weights.append(w)
    if sum(weights) <= 0:
        # 防御性回退：永远至少能抽到常规奖励
        return random.choice(["lingshi", "accessory"])
    return random.choices(items, weights=weights, k=1)[0]


def assign_combat_rewards_for_options(node_types: list[str]) -> list[str | None]:
    """
    为一组选路选项分配奖励类型（仅 combat/elite 生效）。
    规则：同一批次最多 1 个稀有奖励（法宝/道韵），避免三选里连续爆稀有或全是低价值感知。
    """
    reward_types = [None] * len(node_types)
    rare_left = 1
    for i, nt in enumerate(node_types):
        if nt not in ("combat", "elite"):
            continue
        rt = _roll_combat_reward(allow_rare=(rare_left > 0))
        if rt in _RARE_REWARDS:
            rare_left -= 1
        reward_types[i] = rt
    return reward_types


def _get_choice_count(current_level: int | str) -> int:
    """
    根据刚完成的节点决定显示 2 选还是 3 选。
    对标 Tiny Rogues + 星座战士：关 0 后 2 选，Boss 前关 4/9/14 后 2 选，其余 3 选
    """
    if isinstance(current_level, str):
        return 3  # rest_1/shop_1 等：下一节点通常唯一，min(count,len) 会收束
    try:
        nid = int(current_level)
    except (ValueError, TypeError):
        return 3
    if nid == 0:
        return 2  # 关 0 后
    if nid in (4, 9, 14):
        return 2  # Boss 前最后一关，只能选回复或商店
    return 3  # 其余普通关


def get_next_options(
    current_level: int | str,
    route_tree: dict | None = None,
    entrance_names: dict | None = None,
    extra_options: list[int | str] | None = None,
) -> list[tuple[int | str, str]]:
    """
    获取下一关可选列表（完整树，不抽样）。
    返回 [(level_id, name), ...]
    """
    if route_tree is None:
        from levels import ROUTE_TREE

        route_tree = ROUTE_TREE
    extra_options = extra_options or []

    next_ids = list(route_tree.get(current_level, []))
    next_ids.extend(extra_options)
    next_ids = list(dict.fromkeys(next_ids))  # 去重，避免重复选项

    result = []
    for lid in next_ids:
        from levels import get_node_display_name

        name = get_node_display_name(lid)
        result.append((lid, name))
    return result


class RouteSystem:
    """路线系统（类形式，便于扩展）"""

    @staticmethod
    def get_next_options(
        current_level: int | str,
        route_tree: dict | None = None,
        extra_options: list | None = None,
    ) -> list[tuple[int | str, str, str, str]]:
        """
        过关后显示用：从完整树中抽样 2 或 3 个选项。
        返回 (level_id, name, node_type, reward_hint)，无难度星级。
        对标 Tiny Rogues：按层数控制 2/3 选，奖励倾向用图标表示。
        """
        options = get_next_options(current_level, route_tree, None, extra_options)
        if not options:
            return []
        count = _get_choice_count(current_level)
        count = min(count, len(options))
        sampled = random.sample(options, count)

        from levels import get_node_reward_display, get_node_type

        node_types = [get_node_type(lid) for lid, _ in sampled]
        reward_types = assign_combat_rewards_for_options(node_types)
        result = []
        for idx, (lid, name) in enumerate(sampled):
            node_type = node_types[idx]
            reward_type = reward_types[idx]
            reward_hint = get_node_reward_display(lid, reward_type)
            result.append((lid, name, node_type, reward_hint, reward_type))
        return result
