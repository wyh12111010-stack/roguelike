"""关卡配置 - 从 data/levels.json、data/demo.json 加载"""

from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y
from data import load_json

# 内置默认（配置缺失时回退）3大关×5小关：只有大关有名字，小关按类型显示
_DEFAULT_ROUTE_TREE = {
    0: [1, 2, 3, 4, 5],
    1: [6, 7, 8, 9, 10],
    2: [6, 7, 8, 9, 10],
    3: [6, 7, 8, 9, 10],
    4: [6, 7, 8, 9, 10],
    5: [6, 7, 8, 9, 10],
    6: [11, 12, 13, 14, 15],
    7: [11, 12, 13, 14, 15],
    8: [11, 12, 13, 14, 15],
    9: [11, 12, 13, 14, 15],
    10: [11, 12, 13, 14, 15],
    11: ["boss_1", "boss_2", "boss_3"],
    12: ["boss_1", "boss_2", "boss_3"],
    13: ["boss_1", "boss_2", "boss_3"],
    14: ["boss_1", "boss_2", "boss_3"],
    15: ["boss_1", "boss_2", "boss_3"],
    "shop": [6, 7, 8, 9, 10],
    "rest": [6, 7, 8, 9, 10],
    "treasure": [6, 7, 8, 9, 10],
    "boss_1": [],
    "boss_2": [],
    "boss_3": [],
}
_DEFAULT_NODE_TYPES = {
    "1": "combat",
    "2": "combat",
    "3": "shop",
    "4": "rest",
    "5": "treasure",
    "6": "combat",
    "7": "combat",
    "8": "shop",
    "9": "rest",
    "10": "treasure",
    "11": "combat",
    "12": "combat",
    "13": "shop",
    "14": "rest",
    "15": "treasure",
}
_DEFAULT_MAJOR_NAMES = ["试炼", "秘境", "凶地"]
_DEFAULT_TYPE_NAMES = {
    "combat": "战斗",
    "shop": "坊市",
    "rest": "休息",
    "treasure": "宝箱",
    "elite": "精英",
    "boss": "Boss",
    "event": "奇遇",
}
_DEFAULT_REWARD_HINTS = {
    "combat": "灵石",
    "shop": "法宝/饰品",
    "rest": "回复",
    "treasure": "随机",
    "elite": "饰品",
    "boss": "丹药",
}
_DEFAULT_ENTRANCE_NAMES = {"boss_1": "Boss 妖王", "boss_2": "Boss 剑魔", "boss_3": "Boss 丹魔"}
_DEFAULT_DEMO = {
    "types": ["melee", "ranged", "charge", "aoe", "homing", "summon"],
    "names": ["近战", "远程", "突进", "范围", "追踪", "召唤"],
    "route_tree": {"0": [1], "1": [2], "2": [3], "3": [4], "4": [5], "5": []},
    "default_health": 25,
    "default_speed": 80,
    "default_damage": 10,
    "positions": [[30, 40], [50, 60], [70, 40]],
}


def _parse_route_tree(raw: dict) -> dict:
    """解析路线树，支持 int 和 str 键（如 boss_1、shop）"""
    if not raw:
        return {}
    result = {}
    for k, v in raw.items():
        if not isinstance(v, list):
            continue
        # 数字键转为 int，字符串键保留（如 "boss_1", "shop"）
        try:
            ki = int(k)
            key = ki
        except (ValueError, TypeError):
            key = k
        # 子节点：数字转 int，字符串保留
        parsed = []
        for x in v:
            if isinstance(x, str):
                parsed.append(x)
            elif isinstance(x, (int, float)):
                parsed.append(int(x))
            else:
                parsed.append(x)
        result[key] = parsed
    return result


def _parse_entrance_names(raw: dict) -> dict:
    """将 JSON 的字符串 key 转为 int"""
    if not raw:
        return {}
    result = {}
    for k, v in raw.items():
        try:
            result[int(k)] = v
        except (ValueError, TypeError):
            result[k] = v
    return result


def _load_levels_config():
    cfg = load_json("levels.json", {})
    return cfg


def _load_demo_config():
    cfg = load_json("demo.json", _DEFAULT_DEMO)
    return {**_DEFAULT_DEMO, **cfg}


# 懒加载缓存
_levels_cfg = None
_demo_cfg = None


def _get_levels_cfg():
    global _levels_cfg
    if _levels_cfg is None:
        _levels_cfg = _load_levels_config()
    return _levels_cfg


def _get_demo_cfg():
    global _demo_cfg
    if _demo_cfg is None:
        _demo_cfg = _load_demo_config()
    return _demo_cfg


# 对外接口
ROUTE_TREE = None
ENTRANCE_NAMES = None
NODE_TYPES = None
MAJOR_NAMES = None
TYPE_NAMES = None
MAJOR_OF = None
REWARD_HINTS = None
NODE_REWARDS = None
LEVELS = None
BOSSES = None
DEMO_TYPES = None
DEMO_NAMES = None
DEMO_ROUTE_TREE = None


def _ensure_loaded():
    """首次访问时加载配置"""
    global \
        ROUTE_TREE, \
        ENTRANCE_NAMES, \
        NODE_TYPES, \
        MAJOR_NAMES, \
        TYPE_NAMES, \
        MAJOR_OF, \
        REWARD_HINTS, \
        NODE_REWARDS, \
        LEVELS, \
        BOSSES, \
        DEMO_TYPES, \
        DEMO_NAMES, \
        DEMO_ROUTE_TREE
    if ROUTE_TREE is None:
        cfg = _get_levels_cfg()
        ROUTE_TREE = _parse_route_tree(cfg.get("route_tree", _DEFAULT_ROUTE_TREE)) or _DEFAULT_ROUTE_TREE
        ENTRANCE_NAMES = cfg.get("entrance_names", _DEFAULT_ENTRANCE_NAMES) or _DEFAULT_ENTRANCE_NAMES
        raw_nt = cfg.get("node_types", _DEFAULT_NODE_TYPES)
        NODE_TYPES = {str(k): v for k, v in raw_nt.items()} if raw_nt else dict(_DEFAULT_NODE_TYPES)
        MAJOR_NAMES = cfg.get("major_names", _DEFAULT_MAJOR_NAMES) or _DEFAULT_MAJOR_NAMES
        TYPE_NAMES = cfg.get("type_names", _DEFAULT_TYPE_NAMES) or _DEFAULT_TYPE_NAMES
        REWARD_HINTS = cfg.get("reward_hints", _DEFAULT_REWARD_HINTS) or _DEFAULT_REWARD_HINTS
        NODE_REWARDS = cfg.get("node_rewards", {}) or {}
        raw_mo = cfg.get("major_of", {})
        MAJOR_OF = {str(k): int(v) for k, v in raw_mo.items()} if raw_mo else {}
        LEVELS = cfg.get("levels", [])
        BOSSES = cfg.get("bosses", {})
    if DEMO_TYPES is None:
        dc = _get_demo_cfg()
        DEMO_TYPES = dc.get("types", _DEFAULT_DEMO["types"])
        DEMO_NAMES = dc.get("names", _DEFAULT_DEMO["names"])
        DEMO_ROUTE_TREE = _parse_route_tree(dc.get("route_tree", _DEFAULT_DEMO["route_tree"]))


# 大关专属敌人池：试炼仅 melee/ranged，秘境加入 charge/aoe，凶地全部
_ALLOWED_TYPES_BY_MAJOR = {
    0: frozenset(["melee", "ranged"]),
    1: frozenset(["melee", "ranged", "charge", "aoe"]),
    2: frozenset(["melee", "ranged", "charge", "aoe", "homing", "summon"]),
}
# 类型不在当前大关时回退：远程系→ranged，近战/突进/范围/召唤→melee
_TYPE_FALLBACK = {"homing": "ranged", "charge": "melee", "aoe": "melee", "summon": "melee"}
# Balanced 难度曲线：小幅抬升，避免后期伤害断崖
_MAJOR_SCALES = (1.0, 1.12, 1.24)


def _resolve_type_for_major(etype: str, major_idx: int) -> str:
    """按大关限制解析敌人类型，不允许则回退"""
    allowed = _ALLOWED_TYPES_BY_MAJOR.get(major_idx, _ALLOWED_TYPES_BY_MAJOR[2])
    if etype in allowed:
        return etype
    return _TYPE_FALLBACK.get(etype, "melee")


def get_level_enemies(level_index, elite=False):
    """获取某关的敌人生成数据。难度按大关递增（大关0/1/2 分别 ×1.0/1.12/1.24）。elite 时血×1.5、攻×1.2"""
    _ensure_loaded()
    if level_index >= len(LEVELS):
        return []
    levels_per_major = _get_levels_cfg().get("levels_per_major", 5)
    major_idx = min(2, level_index // levels_per_major)
    major_scale = _MAJOR_SCALES[major_idx]
    result = []
    for e in LEVELS[level_index]:
        pos = e.get("pos", [50, 50])
        x_pct, y_pct = pos[0], pos[1]
        x = ARENA_X + ARENA_W * x_pct // 100
        y = ARENA_Y + ARENA_H * y_pct // 100
        t = _resolve_type_for_major(e.get("type", "melee"), major_idx)
        h = int(e.get("health", 20) * major_scale)
        d = int(e.get("damage", 10) * major_scale)
        if elite:
            h = int(h * 1.5)
            d = int(d * 1.2)
        attr = e.get("attr", "none")
        behavior = e.get("behavior", "chase")
        result.append((x, y, h, e.get("speed", 80), d, t, attr, behavior))
    return result


def get_boss_enemies(boss_id):
    """获取 Boss 关卡的敌人生成数据，返回 (x, y, health, speed, damage, type) 列表"""
    _ensure_loaded()
    boss_cfg = BOSSES.get(boss_id, [])
    if isinstance(boss_cfg, dict):
        boss_cfg = boss_cfg.get("enemies", [])
    if not isinstance(boss_cfg, list):
        return []
    result = []
    for e in boss_cfg:
        pos = e.get("pos", [50, 50])
        x_pct, y_pct = pos[0], pos[1]
        x = ARENA_X + ARENA_W * x_pct // 100
        y = ARENA_Y + ARENA_H * y_pct // 100
        t = e.get("type", "melee")
        attr = e.get("attr", "none")
        behavior = e.get("behavior", "chase")
        result.append((x, y, e.get("health", 100), e.get("speed", 80), e.get("damage", 15), t, attr, behavior))
    return result


def get_demo_enemies(demo_level):
    """演示关卡：指定关只生成一种敌人类型"""
    _ensure_loaded()
    if demo_level < 0 or demo_level >= len(DEMO_TYPES):
        return []
    etype = DEMO_TYPES[demo_level]
    dc = _get_demo_cfg()
    positions = dc.get("positions", _DEFAULT_DEMO["positions"])
    health = dc.get("default_health", 25)
    speed = dc.get("default_speed", 80)
    damage = dc.get("default_damage", 10)
    result = []
    for px, py in positions:
        x = ARENA_X + ARENA_W * px // 100
        y = ARENA_Y + ARENA_H * py // 100
        result.append((x, y, health, speed, damage, etype, "none", "chase"))
    return result


def get_route_tree():
    _ensure_loaded()
    return ROUTE_TREE


def get_node_type(node_id):
    """获取节点类型：combat|shop|rest|treasure|boss"""
    _ensure_loaded()
    key = str(node_id)
    if key.startswith("boss_"):
        return "boss"
    return NODE_TYPES.get(key, "combat")


def get_node_display_name(node_id):
    """小关按类型显示，Boss/段末Boss/休整点用 entrance_names。战斗关加编号避免重复"""
    _ensure_loaded()
    nt = get_node_type(node_id)
    if nt == "boss" or nt == "rest_point":
        return ENTRANCE_NAMES.get(node_id, TYPE_NAMES.get(nt, "战斗"))
    if nt == "rest":
        return TYPE_NAMES.get("rest", "休息")
    if nt == "shop":
        return TYPE_NAMES.get("shop", "坊市")
    if nt == "combat" and isinstance(node_id, int):
        return f"战斗-{node_id}"
    return TYPE_NAMES.get(nt, "战斗")


# 奖励类型到显示名的映射
REWARD_DISPLAY = {"lingshi": "灵石", "fabao": "法宝", "accessory": "饰品", "daoyun": "道韵"}


def get_node_reward(node_id):
    """奖励倾向显示（兼容旧接口，无 reward_type 时用 hint）"""
    return get_node_reward_display(node_id, None)


def get_node_reward_display(node_id, reward_type=None):
    """奖励倾向显示：reward_type 由 RouteSystem 选路时抽取传入，非固定循环"""
    _ensure_loaded()
    if reward_type:
        return REWARD_DISPLAY.get(reward_type, "灵石")
    return REWARD_HINTS.get(get_node_type(node_id), "灵石")


def get_node_reward_type(node_id, selected_reward_type=None):
    """实际奖励类型：由选路时抽取的 selected_reward_type 传入，用于过关发放"""
    if selected_reward_type:
        return selected_reward_type
    _ensure_loaded()
    nt = get_node_type(node_id)
    if nt not in ("combat", "elite"):
        return "lingshi"
    return "lingshi"  # 无传入时回退


def get_level_display(node_id):
    """当前关卡显示：大关名 · 类型名，Boss/休整点用 entrance_names"""
    _ensure_loaded()
    nt = get_node_type(node_id)
    if nt == "boss" or nt == "rest_point":
        return ENTRANCE_NAMES.get(node_id, "Boss")
    major_idx = MAJOR_OF.get(str(node_id), 0)
    major_name = MAJOR_NAMES[major_idx] if major_idx < len(MAJOR_NAMES) else ""
    type_name = TYPE_NAMES.get(nt, "战斗")
    return f"{major_name} · {type_name}" if major_name else type_name


def get_entrance_names():
    _ensure_loaded()
    return ENTRANCE_NAMES


def get_demo_names():
    _ensure_loaded()
    return DEMO_NAMES


def get_demo_route_tree():
    _ensure_loaded()
    return DEMO_ROUTE_TREE


def get_levels():
    _ensure_loaded()
    return LEVELS


# 首次导入时加载配置
_ensure_loaded()
