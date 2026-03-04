"""
商店 - 局内消费灵石
法宝、道韵碎片、刷新、法宝强化、饰品、饰品升级
"""
import pygame
import random

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_UI, get_font
from accessory import ACCESSORY_LIST, get_accessory
from fabao import FABAO_LIST
from setting import SHOP_FABAO_COST, SHOP_DAOYUN_FRAGMENT_COST, SHOP_REFRESH_COST

# 法宝强化（增强法宝，非饰品）
# 采用分段成本 + 上限封顶，避免无限滚雪球。
FABAO_UPGRADE_RULES = {
    "damage_pct": {"label": "法宝·伤", "step": 10, "cap": 50, "costs": [20, 28, 36, 46, 58]},
    "speed_pct": {"label": "法宝·速", "step": 5, "cap": 25, "costs": [20, 30, 42, 56, 72]},
}

# 每局商店展示的饰品（可随机，此处固定前几个）
SHOP_ACCESSORY_IDS = [
    "dmg_s", "dmg_pct", "atk_spd", "pierce", "multi", "hp", "mp",
    "glass_core", "swift_debt", "mana_burn", "iron_shell",
]

# 饰品升级费用（按等级）
UPGRADE_COST = {1: 15, 2: 25}  # 1->2: 15, 2->3: 25

SHOP_UI = {
    "item_rects": [],   # [(rect, item_type, item_id, cost), ...]
    "exit_rect": None,
    "refresh_rect": None,
}


def gen_shop_fabao(unlocked_ids, exclude_ids):
    """从已解锁法宝中随机 1 个，排除 exclude_ids。无可用则返回 None"""
    candidates = [f for f in FABAO_LIST if f.id in unlocked_ids and f.id not in exclude_ids]
    if not candidates:
        return None
    return random.choice(candidates)


def draw(screen, player, lingshi, shop_state=None, unlocked_accessories=None, accessory_slots=6):
    """绘制商店界面：法宝、道韵碎片、刷新、法宝强化、饰品、饰品升级"""
    shop_state = shop_state or {}
    unlocked_accessories = unlocked_accessories or []
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(230)
    overlay.fill((30, 35, 50))
    screen.blit(overlay, (0, 0))

    font_title = get_font(28)
    font_small = get_font(20)

    title = font_title.render("坊市", True, (200, 180, 140))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

    lingshi_text = font_small.render(f"灵石: {lingshi}", True, (150, 200, 150))
    screen.blit(lingshi_text, (20, 60))

    SHOP_UI["item_rects"] = []
    SHOP_UI["refresh_rect"] = None
    item_w, item_h = 130, 44
    gap = 15
    start_x = 40
    cy = 100

    # 1. 法宝（已解锁才出现，65 灵石）
    shop_fabao_id = shop_state.get("fabao_id")
    if shop_fabao_id:
        fb = next((f for f in FABAO_LIST if f.id == shop_fabao_id), None)
        if fb:
            have_ids = {f.id for f in getattr(player, "fabao_list", [])}
            can = lingshi >= SHOP_FABAO_COST and shop_fabao_id not in have_ids and len(have_ids) < 2
            rect = pygame.Rect(start_x, cy, item_w, item_h)
            SHOP_UI["item_rects"].append((rect, "fabao_buy", shop_fabao_id, SHOP_FABAO_COST))
            _draw_item(screen, rect, f"{fb.name} {SHOP_FABAO_COST}", "法宝", can, font_small)
            start_x += item_w + gap

    # 2. 道韵碎片（35 灵石 +1 道韵，限购 1）
    daoyun_bought = shop_state.get("daoyun_bought", False)
    if not daoyun_bought:
        can = lingshi >= SHOP_DAOYUN_FRAGMENT_COST
        rect = pygame.Rect(start_x, cy, item_w, item_h)
        SHOP_UI["item_rects"].append((rect, "daoyun_fragment", None, SHOP_DAOYUN_FRAGMENT_COST))
        _draw_item(screen, rect, f"道韵碎片 {SHOP_DAOYUN_FRAGMENT_COST}", "+1 道韵", can, font_small)
        start_x += item_w + gap

    # 3. 刷新（15 灵石/次）
    refresh_remaining = shop_state.get("refresh_remaining", 0)
    if refresh_remaining > 0:
        can = lingshi >= SHOP_REFRESH_COST
        rect = pygame.Rect(start_x, cy, item_w, item_h)
        SHOP_UI["refresh_rect"] = rect
        SHOP_UI["item_rects"].append((rect, "refresh", None, SHOP_REFRESH_COST))
        _draw_item(screen, rect, f"刷新 {SHOP_REFRESH_COST}", f"剩余{refresh_remaining}次", can, font_small)
        start_x += item_w + gap

    start_x = 40
    cy += item_h + gap + 25

    # 4. 法宝强化
    sect = font_small.render("法宝强化", True, (180, 160, 120))
    screen.blit(sect, (start_x, cy - 22))
    for etype, rule in FABAO_UPGRADE_RULES.items():
        rect = pygame.Rect(start_x, cy, item_w, item_h)
        offer = get_fabao_upgrade_offer(player, etype)
        can = (offer is not None) and lingshi >= offer["cost"]
        if offer is not None:
            SHOP_UI["item_rects"].append((rect, "fabao", ("fb_upgrade", etype, offer["step"]), offer["cost"]))
            _draw_item(
                screen, rect,
                f"{rule['label']} {offer['cost']}",
                f"+{offer['step']}% ({offer['next']}%/{rule['cap']}%)",
                can, font_small
            )
        else:
            _draw_item(screen, rect, f"{rule['label']} 已满", f"上限 {rule['cap']}%", False, font_small)
        start_x += item_w + gap
    start_x = 40
    cy += item_h + gap + 25

    # 2. 饰品（仅显示已解锁的）
    sect = font_small.render("饰品", True, (180, 160, 120))
    screen.blit(sect, (start_x, cy - 22))
    acc_ids = [a for a in SHOP_ACCESSORY_IDS if a in unlocked_accessories] if unlocked_accessories else SHOP_ACCESSORY_IDS
    for aid in acc_ids:
        acc = get_accessory(aid)
        if not acc:
            continue
        rect = pygame.Rect(start_x, cy, item_w, item_h)
        can = lingshi >= acc.cost and not _has_accessory(player, aid) and len(player.accessories) < accessory_slots
        SHOP_UI["item_rects"].append((rect, "accessory", aid, acc.cost))
        _draw_item(screen, rect, f"{acc.name} {acc.cost}", acc.desc, can, font_small)
        start_x += item_w + gap
        if start_x > SCREEN_WIDTH - 150:
            start_x = 40
            cy += item_h + gap
    start_x = 40
    cy += item_h + gap + 25

    # 3. 饰品升级
    sect = font_small.render("饰品升级", True, (180, 160, 120))
    screen.blit(sect, (start_x, cy - 22))
    for i, (acc, lv) in enumerate(player.accessories):
        if lv >= acc.max_level:
            continue
        cost = UPGRADE_COST.get(lv, 25)
        rect = pygame.Rect(start_x, cy, item_w, item_h)
        can = lingshi >= cost
        SHOP_UI["item_rects"].append((rect, "upgrade", i, cost))
        _draw_item(screen, rect, f"{acc.name}+{lv} {cost}", f"Lv{lv}->{lv+1}", can, font_small)
        start_x += item_w + gap
        if start_x > SCREEN_WIDTH - 150:
            start_x = 40
            cy += item_h + gap

    # 离开
    exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 90, 160, 45)
    SHOP_UI["exit_rect"] = exit_rect
    pygame.draw.rect(screen, (80, 100, 120), exit_rect)
    pygame.draw.rect(screen, (150, 150, 150), exit_rect, 2)
    exit_txt = font_small.render("离开 (ESC)", True, (255, 255, 255))
    t_rect = exit_txt.get_rect(center=exit_rect.center)
    screen.blit(exit_txt, t_rect)


def _draw_item(screen, rect, title, desc, can_afford, font):
    color = (50, 80, 60) if can_afford else (50, 45, 45)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (120, 120, 120), rect, 2)
    txt_color = (200, 200, 200) if can_afford else (100, 100, 100)
    screen.blit(font.render(title, True, txt_color), (rect.x + 6, rect.y + 4))
    screen.blit(font.render(desc, True, (140, 140, 140)), (rect.x + 6, rect.y + 24))


def get_fabao_upgrade_offer(player, etype):
    rule = FABAO_UPGRADE_RULES.get(etype)
    if not rule:
        return None
    cur = int(getattr(player, "fabao_damage_pct" if etype == "damage_pct" else "fabao_speed_pct", 0))
    if cur >= rule["cap"]:
        return None
    tier = min(len(rule["costs"]) - 1, cur // rule["step"])
    cost = rule["costs"][tier]
    next_val = min(rule["cap"], cur + rule["step"])
    return {"cost": cost, "step": rule["step"], "next": next_val}


def _has_accessory(player, aid):
    for acc, _ in player.accessories:
        if acc.id == aid:
            return True
    return False
