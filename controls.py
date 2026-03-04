"""可配置按键：默认值、显示名、查询工具。"""
import pygame


DEFAULT_KEYBINDS = {
    "move_up": pygame.K_w,
    "move_down": pygame.K_s,
    "move_left": pygame.K_a,
    "move_right": pygame.K_d,
    "dash": pygame.K_LSHIFT,
    "switch_fabao": pygame.K_q,
    "cast_spell": pygame.K_e,
    "partner_skill": pygame.K_f,
    "use_potion": pygame.K_r,
    "char_panel": pygame.K_c,
    "return_village": pygame.K_r,
}

ACTION_ORDER = [
    "move_up",
    "move_down",
    "move_left",
    "move_right",
    "dash",
    "switch_fabao",
    "cast_spell",
    "partner_skill",
    "use_potion",
    "char_panel",
]

ACTION_LABELS = {
    "move_up": "上移",
    "move_down": "下移",
    "move_left": "左移",
    "move_right": "右移",
    "dash": "冲刺",
    "switch_fabao": "切换法宝",
    "cast_spell": "施放法术",
    "partner_skill": "伙伴技能",
    "use_potion": "使用丹药",
    "char_panel": "人物面板",
    "return_village": "回村子(死亡/胜利)",
}

# 保留给系统功能，避免玩家把菜单/取消键绑坏
RESERVED_KEYS = {
    pygame.K_ESCAPE,
    pygame.K_F10,
}


def default_keybinds():
    return dict(DEFAULT_KEYBINDS)


def merge_keybinds(raw):
    merged = default_keybinds()
    if not isinstance(raw, dict):
        return merged
    for action, key in raw.items():
        if action in merged and isinstance(key, int):
            merged[action] = key
    return merged


def key_name(key):
    try:
        return pygame.key.name(int(key)).upper()
    except Exception:
        return str(key)


def action_pressed(keys, bindings, action):
    key = bindings.get(action, DEFAULT_KEYBINDS.get(action))
    return bool(key is not None and keys[key])


def action_down(event, bindings, action):
    key = bindings.get(action, DEFAULT_KEYBINDS.get(action))
    return event.type == pygame.KEYDOWN and event.key == key


def find_conflict(bindings, action, key):
    for a, k in bindings.items():
        if a != action and k == key:
            return a
    return None


def is_reserved_key(key):
    return key in RESERVED_KEYS
