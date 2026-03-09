"""
商店 - 局内消费灵石
法宝、道韵碎片、刷新、法宝强化、饰品、饰品升级
"""

import os
import random

import pygame

from accessory import get_accessory
from config import SCREEN_HEIGHT, SCREEN_WIDTH, get_font
from config_assets import get_icon
from fabao import FABAO_LIST
from setting import SHOP_DAOYUN_FRAGMENT_COST, SHOP_FABAO_COST, SHOP_REFRESH_COST

# 设计系统颜色（与 ui.components.Colors 保持一致）
_C_BG = (20, 25, 35)
_C_GOLD = (180, 150, 90)
_C_TEXT_GOLD = (255, 215, 0)
_C_TEXT_LIGHT = (240, 230, 210)
_C_TEXT_GRAY = (180, 170, 150)
_C_LINGSHI = (218, 165, 32)
_C_BORDER_DARK = (100, 100, 120)
_C_AFFORDABLE = (35, 55, 45)
_C_EXPENSIVE = (50, 35, 35)
_C_HOVER_AFFORDABLE = (45, 70, 55)
_C_HOVER_EXPENSIVE = (65, 40, 40)

# 图标缓存
_icon_cache: dict[str, pygame.Surface | None] = {}

# 法宝强化（增强法宝，非饰品）
# 采用分段成本 + 上限封顶，避免无限滚雪球。
FABAO_UPGRADE_RULES = {
    "damage_pct": {"label": "法宝·伤", "step": 10, "cap": 50, "costs": [20, 28, 36, 46, 58]},
    "speed_pct": {"label": "法宝·速", "step": 5, "cap": 25, "costs": [20, 30, 42, 56, 72]},
}

# 每局商店展示的饰品（可随机，此处固定前几个）
SHOP_ACCESSORY_IDS = [
    "dmg_s",
    "dmg_pct",
    "atk_spd",
    "pierce",
    "multi",
    "hp",
    "mp",
    "glass_core",
    "swift_debt",
    "mana_burn",
    "iron_shell",
]

# 饰品升级费用（按等级）
UPGRADE_COST = {1: 15, 2: 25}  # 1->2: 15, 2->3: 25

SHOP_UI = {
    "item_rects": [],  # [(rect, item_type, item_id, cost), ...]
    "exit_rect": None,
    "refresh_rect": None,
    "hover_rect": None,  # 当前悬停的 rect
}


def _load_icon(fabao_id):
    """加载并缓存法宝图标（32×32）"""
    if fabao_id in _icon_cache:
        return _icon_cache[fabao_id]
    try:
        path = get_icon("fabao", fabao_id)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (32, 32))
            _icon_cache[fabao_id] = img
            return img
    except Exception:
        pass
    _icon_cache[fabao_id] = None
    return None


def gen_shop_fabao(unlocked_ids, exclude_ids):
    """从已解锁法宝中随机 1 个，排除 exclude_ids。无可用则返回 None"""
    candidates = [f for f in FABAO_LIST if f.id in unlocked_ids and f.id not in exclude_ids]
    if not candidates:
        return None
    return random.choice(candidates)


def _draw_section_header(screen, text, x, y, font):
    """绘制带装饰线的分区标题"""
    txt = font.render(text, True, _C_TEXT_GOLD)
    screen.blit(txt, (x, y))
    line_y = y + txt.get_height() + 2
    pygame.draw.line(screen, _C_GOLD, (x, line_y), (x + 180, line_y), 1)
    # 小菱形装饰
    dx = x + 184
    for off in [0, 6]:
        pygame.draw.polygon(screen, _C_GOLD, [(dx + off, line_y), (dx + off + 3, line_y - 3),
                                               (dx + off + 6, line_y), (dx + off + 3, line_y + 3)])


def draw(screen, player, lingshi, shop_state=None, unlocked_accessories=None, accessory_slots=6):
    """绘制商店界面：法宝、道韵碎片、刷新、法宝强化、饰品、饰品升级"""
    shop_state = shop_state or {}
    unlocked_accessories = unlocked_accessories or []

    # 半透明暗色背景
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((*_C_BG, 235))
    screen.blit(overlay, (0, 0))

    # 主面板区域（居中、带金边）
    panel_w, panel_h = min(SCREEN_WIDTH - 60, 720), min(SCREEN_HEIGHT - 40, 560)
    panel_x = (SCREEN_WIDTH - panel_w) // 2
    panel_y = (SCREEN_HEIGHT - panel_h) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    # 面板背景
    ps = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(ps, (20, 25, 35, 240), (0, 0, panel_w, panel_h), border_radius=4)
    screen.blit(ps, (panel_x, panel_y))

    # 金色边框 + 角装饰
    pygame.draw.rect(screen, _C_GOLD, panel_rect, 2, border_radius=4)
    cs = 8
    for cx, cy in [(panel_x, panel_y), (panel_x + panel_w, panel_y),
                   (panel_x, panel_y + panel_h), (panel_x + panel_w, panel_y + panel_h)]:
        sx = 1 if cx == panel_x else -1
        sy = 1 if cy == panel_y else -1
        pygame.draw.line(screen, _C_TEXT_GOLD, (cx, cy), (cx + sx * cs, cy), 3)
        pygame.draw.line(screen, _C_TEXT_GOLD, (cx, cy), (cx, cy + sy * cs), 3)

    font_title = get_font(32)
    font_section = get_font(18)
    font_item = get_font(16)
    font_small = get_font(14)

    # 标题
    title = font_title.render("坊  市", True, _C_TEXT_GOLD)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 12))

    # 灵石显示（右上角）
    ls_icon = font_section.render("💰", True, _C_LINGSHI)
    ls_text = font_section.render(f"{lingshi}", True, _C_LINGSHI)
    screen.blit(ls_icon, (panel_x + panel_w - 100, panel_y + 16))
    screen.blit(ls_text, (panel_x + panel_w - 75, panel_y + 16))

    # 分隔线
    div_y = panel_y + 50
    pygame.draw.line(screen, _C_GOLD, (panel_x + 16, div_y), (panel_x + panel_w - 16, div_y), 1)

    # 鼠标位置（用于悬停检测）
    mx, my = pygame.mouse.get_pos()
    SHOP_UI["item_rects"] = []
    SHOP_UI["refresh_rect"] = None

    item_w, item_h = 150, 56
    gap = 10
    content_x = panel_x + 24
    cy = div_y + 16

    # === 法宝 & 道韵碎片 & 刷新 ===
    _draw_section_header(screen, "商品", content_x, cy, font_section)
    cy += 28

    shop_fabao_id = shop_state.get("fabao_id")
    if shop_fabao_id:
        fb = next((f for f in FABAO_LIST if f.id == shop_fabao_id), None)
        if fb:
            have_ids = {f.id for f in getattr(player, "fabao_list", [])}
            can = lingshi >= SHOP_FABAO_COST and shop_fabao_id not in have_ids and len(have_ids) < 2
            rect = pygame.Rect(content_x, cy, item_w, item_h)
            SHOP_UI["item_rects"].append((rect, "fabao_buy", shop_fabao_id, SHOP_FABAO_COST))
            icon = _load_icon(shop_fabao_id)
            _draw_card(screen, rect, fb.name, f"{SHOP_FABAO_COST} 灵石", "法宝",
                        can, font_item, font_small, mx, my, icon=icon)
            content_x += item_w + gap

    daoyun_bought = shop_state.get("daoyun_bought", False)
    if not daoyun_bought:
        can = lingshi >= SHOP_DAOYUN_FRAGMENT_COST
        rect = pygame.Rect(content_x, cy, item_w, item_h)
        SHOP_UI["item_rects"].append((rect, "daoyun_fragment", None, SHOP_DAOYUN_FRAGMENT_COST))
        _draw_card(screen, rect, "道韵碎片", f"{SHOP_DAOYUN_FRAGMENT_COST} 灵石", "+1 道韵",
                    can, font_item, font_small, mx, my)
        content_x += item_w + gap

    refresh_remaining = shop_state.get("refresh_remaining", 0)
    if refresh_remaining > 0:
        can = lingshi >= SHOP_REFRESH_COST
        rect = pygame.Rect(content_x, cy, item_w, item_h)
        SHOP_UI["refresh_rect"] = rect
        SHOP_UI["item_rects"].append((rect, "refresh", None, SHOP_REFRESH_COST))
        _draw_card(screen, rect, "刷新商品", f"{SHOP_REFRESH_COST} 灵石",
                    f"剩余 {refresh_remaining} 次", can, font_item, font_small, mx, my)

    content_x = panel_x + 24
    cy += item_h + gap + 16

    # === 法宝强化 ===
    _draw_section_header(screen, "法宝强化", content_x, cy, font_section)
    cy += 28
    for etype, rule in FABAO_UPGRADE_RULES.items():
        rect = pygame.Rect(content_x, cy, item_w, item_h)
        offer = get_fabao_upgrade_offer(player, etype)
        can = (offer is not None) and lingshi >= offer["cost"]
        if offer is not None:
            SHOP_UI["item_rects"].append((rect, "fabao", ("fb_upgrade", etype, offer["step"]), offer["cost"]))
            _draw_card(screen, rect, rule["label"], f"{offer['cost']} 灵石",
                        f"+{offer['step']}% → {offer['next']}%/{rule['cap']}%",
                        can, font_item, font_small, mx, my)
        else:
            _draw_card(screen, rect, rule["label"], "已满",
                        f"上限 {rule['cap']}%", False, font_item, font_small, mx, my)
        content_x += item_w + gap
    content_x = panel_x + 24
    cy += item_h + gap + 16

    # === 饰品 ===
    _draw_section_header(screen, "饰品", content_x, cy, font_section)
    cy += 28
    acc_ids = (
        [a for a in SHOP_ACCESSORY_IDS if a in unlocked_accessories] if unlocked_accessories else SHOP_ACCESSORY_IDS
    )
    row_start_x = content_x
    for aid in acc_ids:
        acc = get_accessory(aid)
        if not acc:
            continue
        rect = pygame.Rect(content_x, cy, item_w, item_h)
        can = lingshi >= acc.cost and not _has_accessory(player, aid) and len(player.accessories) < accessory_slots
        SHOP_UI["item_rects"].append((rect, "accessory", aid, acc.cost))
        _draw_card(screen, rect, acc.name, f"{acc.cost} 灵石", acc.desc,
                    can, font_item, font_small, mx, my)
        content_x += item_w + gap
        if content_x + item_w > panel_x + panel_w - 16:
            content_x = row_start_x
            cy += item_h + gap
    content_x = row_start_x
    cy += item_h + gap + 16

    # === 饰品升级 ===
    has_upgradeable = any(lv < acc.max_level for acc, lv in player.accessories)
    if has_upgradeable:
        _draw_section_header(screen, "饰品升级", content_x, cy, font_section)
        cy += 28
        for i, (acc, lv) in enumerate(player.accessories):
            if lv >= acc.max_level:
                continue
            cost = UPGRADE_COST.get(lv, 25)
            rect = pygame.Rect(content_x, cy, item_w, item_h)
            can = lingshi >= cost
            SHOP_UI["item_rects"].append((rect, "upgrade", i, cost))
            _draw_card(screen, rect, f"{acc.name} +{lv}", f"{cost} 灵石",
                        f"Lv{lv} → Lv{lv + 1}", can, font_item, font_small, mx, my)
            content_x += item_w + gap
            if content_x + item_w > panel_x + panel_w - 16:
                content_x = row_start_x
                cy += item_h + gap

    # === 离开按钮 ===
    exit_w, exit_h = 160, 42
    exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - exit_w // 2, panel_y + panel_h - 56, exit_w, exit_h)
    SHOP_UI["exit_rect"] = exit_rect
    hovered = exit_rect.collidepoint(mx, my)
    btn_color = (60, 80, 100) if hovered else (40, 55, 75)
    es = pygame.Surface((exit_w, exit_h), pygame.SRCALPHA)
    pygame.draw.rect(es, (*btn_color, 230), (0, 0, exit_w, exit_h), border_radius=4)
    screen.blit(es, exit_rect.topleft)
    border_c = _C_TEXT_GOLD if hovered else _C_GOLD
    pygame.draw.rect(screen, border_c, exit_rect, 2, border_radius=4)
    exit_txt = font_section.render("离开 (ESC)", True, _C_TEXT_LIGHT)
    t_rect = exit_txt.get_rect(center=exit_rect.center)
    screen.blit(exit_txt, t_rect)


def _draw_card(screen, rect, title, cost_text, desc, can_afford, font, font_s, mx, my, icon=None):
    """绘制商品卡片：带圆角、悬停高亮、价格标签"""
    hovered = rect.collidepoint(mx, my)
    if can_afford:
        bg = _C_HOVER_AFFORDABLE if hovered else _C_AFFORDABLE
    else:
        bg = _C_HOVER_EXPENSIVE if hovered else _C_EXPENSIVE

    # 卡片背景
    cs = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(cs, (*bg, 220), (0, 0, rect.w, rect.h), border_radius=4)
    screen.blit(cs, rect.topleft)

    # 边框
    border_c = _C_TEXT_GOLD if hovered else (_C_GOLD if can_afford else _C_BORDER_DARK)
    pygame.draw.rect(screen, border_c, rect, 2 if not hovered else 3, border_radius=4)

    # 图标（如果有）
    text_x = rect.x + 8
    if icon:
        screen.blit(icon, (rect.x + 6, rect.y + (rect.h - 32) // 2))
        text_x = rect.x + 42

    # 标题
    txt_color = _C_TEXT_LIGHT if can_afford else _C_TEXT_GRAY
    screen.blit(font.render(title, True, txt_color), (text_x, rect.y + 4))

    # 价格（右上角小标签）
    cost_c = _C_LINGSHI if can_afford else (140, 80, 80)
    cost_surf = font_s.render(cost_text, True, cost_c)
    screen.blit(cost_surf, (rect.x + rect.w - cost_surf.get_width() - 6, rect.y + 4))

    # 描述
    desc_c = _C_TEXT_GRAY if can_afford else (100, 90, 80)
    desc_surf = font_s.render(desc, True, desc_c)
    screen.blit(desc_surf, (text_x, rect.y + 24))

    # 底部小装饰线（仅可购买时）
    if can_afford and hovered:
        pygame.draw.line(screen, _C_GOLD,
                         (rect.x + 4, rect.y + rect.h - 3),
                         (rect.x + rect.w - 4, rect.y + rect.h - 3), 1)


def _draw_item(screen, rect, title, desc, can_afford, font):
    """旧版兼容 - 简单卡片"""
    _draw_card(screen, rect, title, "", desc, can_afford, font, font,
               *pygame.mouse.get_pos())


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
    return any(acc.id == aid for acc, _ in player.accessories)
