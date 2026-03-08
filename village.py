"""
村子 - 准备阶段
大地图 + 多房间，为村民预留空间。玩家移动至房间触发交互，传送门外出。
参考：docs/VILLAGE_MAP_DESIGN.md、PARTNER_VILLAGER_INITIAL.md
"""

import os

import pygame

from config import COLOR_UI, SCREEN_HEIGHT, SCREEN_WIDTH, get_font

# 伙伴立绘缓存 {partner_id: {"frames": [...], "pivots": [...], "single": bool}}
_PARTNER_SPRITES = {}

# NPC 立绘缓存
_NPC_SPRITES = {}

# 地图尺寸（扩展以容纳 5 伙伴平均分布）
VILLAGE_MAP_W = 1200
VILLAGE_MAP_H = 700
VILLAGE_MAP_RECT = pygame.Rect(0, 0, VILLAGE_MAP_W, VILLAGE_MAP_H)

# 房间定义 (x, y, w, h)，相邻摆放，直接走过去
ROOM_LINGGEN = pygame.Rect(150, 80, 260, 220)  # 灵根殿（玄真）
ROOM_FABAO = pygame.Rect(450, 80, 260, 220)  # 炼器坊（铸心）
ROOM_CENTER = pygame.Rect(300, 320, 260, 200)  # 中央（栖霞）
ROOM_PORTAL = pygame.Rect(150, 540, 560, 110)  # 传送门厅

# NPC 房间列表
NPC_ROOMS = [
    (ROOM_CENTER, "栖霞", "qixia"),
    (ROOM_LINGGEN, "玄真", "xuanzhen"),
    (ROOM_FABAO, "铸心", "zhuxin"),
]

# 5 位可治疗伙伴：平均分布在村庄各处，画面和谐不扎堆
ROOM_XUANXIAO = pygame.Rect(30, 180, 100, 90)  # 玄霄 - 左上角
ROOM_QINGLI = pygame.Rect(1050, 80, 100, 90)  # 青璃 - 右上角
ROOM_CHIYUAN = pygame.Rect(1050, 320, 100, 90)  # 赤渊 - 右中
ROOM_BILUO = pygame.Rect(1050, 560, 100, 90)  # 碧落 - 右下角
ROOM_MOYU = pygame.Rect(30, 560, 100, 90)  # 墨羽 - 左下角

# 伙伴房间列表（用于绘制与碰撞）
PARTNER_ROOMS = [
    (ROOM_XUANXIAO, "玄霄", "xuanxiao"),
    (ROOM_QINGLI, "青璃", "qingli"),
    (ROOM_CHIYUAN, "赤渊", "chiyuan"),
    (ROOM_BILUO, "碧落", "biluo"),
    (ROOM_MOYU, "墨羽", "moyu"),
]

# 伙伴立绘路径
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ASSETS_DIR = os.path.join(_SCRIPT_DIR, "assets")


def _load_partner_sprite(partner_id):
    """加载伙伴立绘，支持单帧、2×2 四帧或 6×6 三十二帧。返回 None 若文件不存在。"""
    if partner_id in _PARTNER_SPRITES:
        return _PARTNER_SPRITES[partner_id]
    path = os.path.join(_ASSETS_DIR, f"partner_{partner_id}.png")
    if not os.path.exists(path):
        _PARTNER_SPRITES[partner_id] = None
        return None
    try:
        from tools.sprite_loader import get_content_center, load_sprite_sheet_grid

        sheet = pygame.image.load(path)
        if sheet.get_alpha() is None:
            sheet = sheet.convert()
        else:
            sheet = sheet.convert_alpha()
        w, h = sheet.get_width(), sheet.get_height()

        # 判断网格类型
        if w == h and w >= 200:  # 大图，可能是 6×6 网格（288×288）
            # 尝试 6×6 网格（32 帧）
            all_frames = load_sprite_sheet_grid(path, 6, 6)
            frames = all_frames[:32]  # 只用前 32 帧
            pivots = [get_content_center(f) for f in frames]
            _PARTNER_SPRITES[partner_id] = {"frames": frames, "pivots": pivots, "single": False}
        elif w == h and w >= 96 and w % 2 == 0:  # 2×2 四帧
            frames = load_sprite_sheet_grid(path, 2, 2)
            pivots = [get_content_center(f) for f in frames]
            _PARTNER_SPRITES[partner_id] = {"frames": frames, "pivots": pivots, "single": False}
        else:  # 单帧
            frames = [sheet]
            pivots = [get_content_center(sheet)]
            _PARTNER_SPRITES[partner_id] = {"frames": frames, "pivots": pivots, "single": True}

        return _PARTNER_SPRITES[partner_id]
    except Exception as e:
        print(f"加载伙伴 {partner_id} 失败: {e}")
        _PARTNER_SPRITES[partner_id] = None
        return None


def _load_npc_sprite(npc_id):
    """加载 NPC 立绘，支持 6×6 三十二帧。返回 None 若文件不存在。"""
    if npc_id in _NPC_SPRITES:
        return _NPC_SPRITES[npc_id]
    path = os.path.join(_ASSETS_DIR, f"npc_{npc_id}.png")
    if not os.path.exists(path):
        _NPC_SPRITES[npc_id] = None
        return None
    try:
        from tools.sprite_loader import get_content_center, load_sprite_sheet_grid

        sheet = pygame.image.load(path).convert_alpha()
        w, h = sheet.get_width(), sheet.get_height()

        # 判断网格类型
        if w == h and w >= 200:  # 大图，6×6 网格（288×288）
            all_frames = load_sprite_sheet_grid(path, 6, 6)
            frames = all_frames[:32]  # 只用前 32 帧
            pivots = [get_content_center(f) for f in frames]
            _NPC_SPRITES[npc_id] = {"frames": frames, "pivots": pivots}
        else:  # 单帧
            frames = [sheet]
            pivots = [get_content_center(sheet)]
            _NPC_SPRITES[npc_id] = {"frames": frames, "pivots": pivots}

        return _NPC_SPRITES[npc_id]
    except Exception as e:
        print(f"加载 NPC {npc_id} 失败: {e}")
        _NPC_SPRITES[npc_id] = None
        return None


# 传送门在传送门厅内
EXIT_PORTAL = pygame.Rect(250, 565, 140, 70)
DEMO_PORTAL = pygame.Rect(470, 565, 140, 70)

# 兼容旧接口：区域即房间
LINGGEN_ZONE = ROOM_LINGGEN
FABAO_ZONE = ROOM_FABAO
CENTER_ZONE = ROOM_CENTER

# 传送门颜色
PORTAL_COLOR = (60, 140, 200)
PORTAL_HOVER = (90, 180, 255)
PORTAL_DEMO = (60, 160, 100)
PORTAL_DEMO_HOVER = (90, 200, 140)

# 房间颜色
ROOM_ALPHA = 50
ROOM_BORDER = (90, 90, 110)
ROOM_ACTIVE = (100, 140, 180)

# 村子 UI
VILLAGE_UI = {
    "linggen_rects": [],
    "fabao_rects": [],
    "unlock_rects": [],
    "growth_rects": [],  # [(rect, growth_type, cost)] 局外成长
    "dialogue_rects": [],  # [(rect, "linggen"|"fabao"|"qixia")]
    "center_rects": [],  # [(rect, "dialogue"|"achievement")] 栖霞
    "partner_rects": [],  # [(rect, partner_id, "heal"|"dialogue"|"select")]
    "new_game_rect": None,
    "resonance_button_rect": None,  # 共鸣设置按钮
    "resonance_panel_rects": [],  # [(rect, pact)] 共鸣选项
    "resonance_confirm_rect": None,  # 确认按钮
    "resonance_cancel_rect": None,  # 取消按钮
}


def get_camera_offset(player_rect):
    """相机跟随玩家，保持玩家在屏幕中央"""
    px = player_rect.centerx
    py = player_rect.centery
    # 限制相机不超出地图
    cam_x = max(0, min(VILLAGE_MAP_W - SCREEN_WIDTH, px - SCREEN_WIDTH // 2))
    cam_y = max(0, min(VILLAGE_MAP_H - SCREEN_HEIGHT, py - SCREEN_HEIGHT // 2))
    return (cam_x, cam_y)


def world_to_screen(rect, cam):
    """世界坐标转屏幕坐标"""
    return pygame.Rect(rect.x - cam[0], rect.y - cam[1], rect.w, rect.h)


def draw_portal(screen, rect, label, color, hover_color, is_hover, cam=(0, 0), sublabel=None):
    """绘制传送门（拱形/椭圆），可选 sublabel 显示在下方（如 ★★ 灵石）"""
    r = world_to_screen(rect, cam)
    c = hover_color if is_hover else color
    cx, cy = r.centerx, r.centery
    pygame.draw.ellipse(screen, c, r, 3)
    inner = r.inflate(-20, -15)
    pygame.draw.ellipse(screen, (*c[:3], 80), inner)
    font = get_font(20)
    txt = font.render(label, True, (255, 255, 255))
    if sublabel:
        t_rect = txt.get_rect(center=(cx, cy - 8))
        screen.blit(txt, t_rect)
        font_small = get_font(14)
        sub = font_small.render(sublabel, True, (200, 220, 200))
        s_rect = sub.get_rect(center=(cx, cy + 10))
        screen.blit(sub, s_rect)
    else:
        t_rect = txt.get_rect(center=(cx, cy))
        screen.blit(txt, t_rect)


def draw_room(screen, rect, label, is_active, cam):
    """绘制房间背景"""
    r = world_to_screen(rect, cam)
    surf = pygame.Surface((r.w, r.h))
    surf.set_alpha(ROOM_ALPHA)
    surf.fill(ROOM_ACTIVE if is_active else (70, 75, 90))
    screen.blit(surf, r.topleft)
    pygame.draw.rect(screen, ROOM_BORDER if not is_active else (120, 160, 200), r, 2)
    font = get_font(18)
    txt = font.render(label, True, COLOR_UI)
    screen.blit(txt, (r.x + 12, r.y + 8))


def draw_village(
    screen,
    avail_linggen,
    avail_fabao,
    linggen_choice,
    fabao_choice,
    daoyun,
    unlocked_linggen,
    unlocked_fabao,
    village_player_rect,
    in_linggen_zone,
    in_fabao_zone,
    camera_offset=(0, 0),
    village_dialogue=None,
    potion_stock=0,
    potion_cap=1,
    in_partner_zone=None,
    partner_can_heal=None,
    partner_bond_levels=None,
    unlocked_accessories=None,
    selected_partner_id=None,
    accessory_slots=6,
    shop_refresh_count=1,
    base_health_bonus=0,
    base_mana_bonus=0,
    start_accessory_mode=0,
    in_center_zone=False,
    achievements_unlocked=None,
    resonance_panel_open=False,
    resonance_system=None,
):
    """绘制村子：NPC 位置、传送门、玩家。village_dialogue 为 "linggen"|"fabao"|partner_id 时显示对话"""
    from attribute import ATTR_COLORS
    from config import (
        COLOR_TEXT_HEADING,
        get_font_small,
    )
    from partner import get_bond_level
    from ui_theme import draw_button
    from village_visual import (
        draw_dialogue_enhanced,
        draw_hud_enhanced,
        draw_player_enhanced,
        draw_portal_enhanced,
        draw_room_enhanced,
        draw_selection_panel_enhanced,
        draw_village_background,
    )

    cam = camera_offset
    partner_bond_levels = partner_bond_levels or {}
    unlocked_accessories = unlocked_accessories or []
    selected_partner_id = selected_partner_id or ""

    # 背景（修仙风格动态背景）
    draw_village_background(screen, cam)

    # 房间（使用增强版绘制）
    draw_room_enhanced(screen, ROOM_CENTER, "中央广场", in_center_zone, cam, "center")
    draw_room_enhanced(screen, ROOM_LINGGEN, "灵根殿", in_linggen_zone, cam, "linggen")
    draw_room_enhanced(screen, ROOM_FABAO, "炼器坊", in_fabao_zone, cam, "fabao")
    draw_room_enhanced(screen, ROOM_PORTAL, "传送门厅", False, cam, "portal")
    # 5 位可治疗伙伴（边缘地带）
    anim_t = pygame.time.get_ticks() / 1000.0
    for rect, label, pid in PARTNER_ROOMS:
        is_active = in_partner_zone == pid
        lv = get_bond_level(pid, partner_bond_levels) if partner_bond_levels else 0
        room_label = f"{label} Lv{lv}" if lv > 0 else label
        draw_room_enhanced(screen, rect, room_label, is_active, cam, "partner")
        # 绘制伙伴立绘
        spr = _load_partner_sprite(pid)
        if spr and spr["frames"] and len(spr["frames"]) > 0:
            from tools.sprite_loader import play_animation

            idx = play_animation(spr["frames"], anim_t, fps=8, loop=True)
            frame = spr["frames"][idx]
            pivot = spr["pivots"][idx]
            zone_scr = world_to_screen(rect, cam)
            # 缩放到房间内合适大小（约 48 像素高）
            fw, fh = frame.get_width(), frame.get_height()
            target_h = min(48, zone_scr.h - 28)
            scale = target_h / fh if fh > 0 else 1
            target_w = int(fw * scale)
            if target_w > 0 and target_h > 0:
                scaled = pygame.transform.scale(frame, (target_w, target_h))
                # 以质心为锚点，居中绘制
                draw_x = zone_scr.centerx - int(pivot[0] * scale)
                draw_y = zone_scr.y + 28 + (zone_scr.h - 28) // 2 - int(pivot[1] * scale)
                screen.blit(scaled, (draw_x, draw_y))

    # 3 位 NPC（中央房间）
    for rect, label, npc_id in NPC_ROOMS:
        # NPC 立绘绘制
        spr = _load_npc_sprite(npc_id)
        if spr and spr["frames"] and len(spr["frames"]) > 0:
            from tools.sprite_loader import play_animation

            idx = play_animation(spr["frames"], anim_t, fps=8, loop=True)
            frame = spr["frames"][idx]
            pivot = spr["pivots"][idx]
            zone_scr = world_to_screen(rect, cam)
            # 缩放到房间内合适大小（约 64 像素高，NPC 比伙伴大一点）
            fw, fh = frame.get_width(), frame.get_height()
            target_h = min(64, zone_scr.h - 28)
            scale = target_h / fh if fh > 0 else 1
            target_w = int(fw * scale)
            if target_w > 0 and target_h > 0:
                scaled = pygame.transform.scale(frame, (target_w, target_h))
                # 以质心为锚点，居中绘制
                draw_x = zone_scr.centerx - int(pivot[0] * scale)
                draw_y = zone_scr.y + 28 + (zone_scr.h - 28) // 2 - int(pivot[1] * scale)
                screen.blit(scaled, (draw_x, draw_y))

    # 传送门（使用增强版绘制）
    exit_scr = world_to_screen(EXIT_PORTAL, cam)
    demo_scr = world_to_screen(DEMO_PORTAL, cam)
    exit_hover = exit_scr.collidepoint(pygame.mouse.get_pos()) or (
        village_player_rect and EXIT_PORTAL.colliderect(village_player_rect)
    )
    demo_hover = demo_scr.collidepoint(pygame.mouse.get_pos()) or (
        village_player_rect and DEMO_PORTAL.colliderect(village_player_rect)
    )
    draw_portal_enhanced(screen, EXIT_PORTAL, "外出", PORTAL_COLOR, PORTAL_HOVER, exit_hover, cam)
    draw_portal_enhanced(screen, DEMO_PORTAL, "演示", PORTAL_DEMO, PORTAL_DEMO_HOVER, demo_hover, cam)

    # 玩家（使用增强版绘制）
    if village_player_rect:
        draw_player_enhanced(screen, village_player_rect, cam)

    # HUD（使用增强版绘制）
    draw_hud_enhanced(screen)

    # 新游戏按钮
    from save import has_run_save

    VILLAGE_UI["new_game_rect"] = None
    if has_run_save():
        base_rect = pygame.Rect(20, SCREEN_HEIGHT - 50, 90, 35)
        is_hover = base_rect.collidepoint(pygame.mouse.get_pos())
        # 悬停时放大 5%
        if is_hover:
            new_rect = base_rect.inflate(int(base_rect.w * 0.05), int(base_rect.h * 0.05))
        else:
            new_rect = base_rect
        VILLAGE_UI["new_game_rect"] = base_rect  # 保存原始尺寸用于碰撞检测
        draw_button(screen, new_rect, "新游戏", is_hover, False)

    # 共鸣设置按钮（在传送门厅附近）
    VILLAGE_UI["resonance_button_rect"] = None
    if not village_dialogue and not resonance_panel_open:
        portal_scr = world_to_screen(ROOM_PORTAL, cam)
        base_rect = pygame.Rect(portal_scr.x + portal_scr.w - 110, portal_scr.y + 10, 100, 32)
        is_hover = base_rect.collidepoint(pygame.mouse.get_pos())
        # 悬停时放大 5%
        if is_hover:
            btn_rect = base_rect.inflate(int(base_rect.w * 0.05), int(base_rect.h * 0.05))
            c = (100, 120, 160)  # 更亮的颜色
        else:
            btn_rect = base_rect
            c = (60, 75, 110)
        VILLAGE_UI["resonance_button_rect"] = base_rect  # 保存原始尺寸
        pygame.draw.rect(screen, c, btn_rect)
        pygame.draw.rect(screen, (140, 160, 200), btn_rect, 2)
        font_small = get_font_small()
        btn_txt = font_small.render("共鸣设置", True, COLOR_TEXT_HEADING)
        screen.blit(btn_txt, (btn_rect.x + 18, btn_rect.y + 6))

    # 共鸣面板（全屏覆盖）
    if resonance_panel_open and resonance_system:
        _draw_resonance_panel(screen, resonance_system)

    # 对话弹窗 / 成就面板（玩家点击后显示）
    achievements_unlocked = achievements_unlocked or set()
    if village_dialogue == "achievement":
        _draw_achievement_overlay(screen, achievements_unlocked)
    elif village_dialogue:
        # 检查是否有特殊对话文本
        dialogue_text = getattr(game if "game" in dir() else None, "village_dialogue_text", None)
        draw_dialogue_enhanced(screen, village_dialogue, dialogue_text)

    # 伙伴区域：治疗/强化 / 对话按钮
    VILLAGE_UI["partner_rects"] = []
    in_partner_zone = in_partner_zone or ""
    partner_can_heal = partner_can_heal or {}
    if in_partner_zone and not village_dialogue:
        p_rect = next((r for r, _, pid in PARTNER_ROOMS if pid == in_partner_zone), None)
        if p_rect:
            zone_scr = world_to_screen(p_rect, cam)
            # 治疗/强化按钮（可首次解锁或羁绊升级时显示）
            can_heal = partner_can_heal.get(in_partner_zone, False)
            if can_heal:
                from partner import get_upgrade_cost

                lv = get_bond_level(in_partner_zone, partner_bond_levels)
                cost = get_upgrade_cost(in_partner_zone, lv) if lv > 0 else 0
                btn_label = f"强化{cost}" if lv > 0 else "治疗"
                btn = pygame.Rect(zone_scr.x + 5, zone_scr.y + 30, 90, 26)
                VILLAGE_UI["partner_rects"].append((btn, in_partner_zone, "heal"))
                is_hover = btn.collidepoint(pygame.mouse.get_pos())
                c = (80, 140, 100) if is_hover else (50, 100, 70)
                pygame.draw.rect(screen, c, btn)
                pygame.draw.rect(screen, (120, 180, 140), btn, 1)
                screen.blit(font_small.render(btn_label, True, COLOR_UI), (btn.x + 25, btn.y + 4))
            # 携带按钮（羁绊≥1 时可选为出战伙伴）
            lv = get_bond_level(in_partner_zone, partner_bond_levels)
            btn_y = zone_scr.y + (58 if can_heal else 30)
            if lv >= 1:
                is_sel = selected_partner_id == in_partner_zone
                btn_sel = pygame.Rect(zone_scr.x + 5, btn_y, 90, 26)
                VILLAGE_UI["partner_rects"].append((btn_sel, in_partner_zone, "select"))
                c_sel = (
                    (120, 180, 140)
                    if is_sel
                    else ((80, 140, 100) if btn_sel.collidepoint(pygame.mouse.get_pos()) else (50, 100, 70))
                )
                pygame.draw.rect(screen, c_sel, btn_sel)
                pygame.draw.rect(screen, (120, 180, 140), btn_sel, 1)
                lbl = "✓携带" if is_sel else "携带"
                screen.blit(font_small.render(lbl, True, COLOR_UI), (btn_sel.x + 22, btn_sel.y + 4))
                btn_y += 28
            # 对话按钮（已解锁或未解锁都可对话）
            btn2 = pygame.Rect(zone_scr.x + 5, btn_y, 85, 26)
            VILLAGE_UI["partner_rects"].append((btn2, in_partner_zone, "dialogue"))
            is_hover2 = btn2.collidepoint(pygame.mouse.get_pos())
            c2 = (80, 120, 160) if is_hover2 else (60, 85, 110)
            pygame.draw.rect(screen, c2, btn2)
            pygame.draw.rect(screen, (140, 160, 180), btn2, 1)
            p_name = next((n for _, n, pid in PARTNER_ROOMS if pid == in_partner_zone), "伙伴")
            screen.blit(font_small.render(f"与{p_name}对话", True, COLOR_UI), (btn2.x + 2, btn2.y + 4))

    # 「对话」按钮：在区域内时，玩家可选择是否与 NPC 交谈
    VILLAGE_UI["dialogue_rects"] = []
    if in_linggen_zone and not village_dialogue:
        zone_scr = world_to_screen(LINGGEN_ZONE, cam)
        btn = pygame.Rect(zone_scr.x + 10, zone_scr.y + 35, 90, 28)
        VILLAGE_UI["dialogue_rects"].append((btn, "linggen"))
        is_hover = btn.collidepoint(pygame.mouse.get_pos())
        c = (80, 120, 160) if is_hover else (60, 85, 110)
        pygame.draw.rect(screen, c, btn)
        pygame.draw.rect(screen, (140, 160, 180), btn, 1)
        screen.blit(font_small.render("与玄真对话", True, COLOR_UI), (btn.x + 8, btn.y + 5))
    if in_fabao_zone and not village_dialogue:
        zone_scr = world_to_screen(FABAO_ZONE, cam)
        btn = pygame.Rect(zone_scr.x + 10, zone_scr.y + 35, 90, 28)
        VILLAGE_UI["dialogue_rects"].append((btn, "fabao"))
        is_hover = btn.collidepoint(pygame.mouse.get_pos())
        c = (80, 120, 160) if is_hover else (60, 85, 110)
        pygame.draw.rect(screen, c, btn)
        pygame.draw.rect(screen, (140, 160, 180), btn, 1)
        screen.blit(font_small.render("与铸心对话", True, COLOR_UI), (btn.x + 8, btn.y + 5))
    # 栖霞（中央广场）：对话、成就
    VILLAGE_UI["center_rects"] = []
    if in_center_zone and not village_dialogue:
        zone_scr = world_to_screen(CENTER_ZONE, cam)
        btn1 = pygame.Rect(zone_scr.x + 10, zone_scr.y + 35, 90, 28)
        btn2 = pygame.Rect(zone_scr.x + 110, zone_scr.y + 35, 90, 28)
        VILLAGE_UI["center_rects"] = [(btn1, "dialogue"), (btn2, "achievement")]
        for rect, action in VILLAGE_UI["center_rects"]:
            is_hover = rect.collidepoint(pygame.mouse.get_pos())
            c = (80, 120, 160) if is_hover else (60, 85, 110)
            pygame.draw.rect(screen, c, rect)
            pygame.draw.rect(screen, (140, 160, 180), rect, 1)
            lbl = "与栖霞对话" if action == "dialogue" else "成就"
            screen.blit(font_small.render(lbl, True, COLOR_UI), (rect.x + 8, rect.y + 5))

    # 灵根选择（在灵根殿内时）
    VILLAGE_UI["linggen_rects"] = []
    if in_linggen_zone and village_dialogue != "linggen":
        zone_scr = world_to_screen(LINGGEN_ZONE, cam)
        draw_selection_panel_enhanced(
            screen, avail_linggen, linggen_choice, zone_scr, get_font(18), ATTR_COLORS, VILLAGE_UI["linggen_rects"]
        )

    # 法宝选择（在炼器坊内时）
    VILLAGE_UI["fabao_rects"] = []
    if in_fabao_zone and village_dialogue != "fabao":
        zone_scr = world_to_screen(FABAO_ZONE, cam)
        draw_selection_panel_enhanced(
            screen, avail_fabao, fabao_choice, zone_scr, get_font(18), None, VILLAGE_UI["fabao_rects"]
        )

    # 解锁区域：灵根殿只显示灵根解锁，炼器坊只显示法宝解锁
    VILLAGE_UI["unlock_rects"] = []
    VILLAGE_UI["growth_rects"] = []
    if in_linggen_zone and not village_dialogue:
        from unlock import get_linggen_cost, get_lockable_linggen

        lockable_lg = get_lockable_linggen(unlocked_linggen)
        zone_scr = world_to_screen(LINGGEN_ZONE, cam)
        unlock_y = zone_scr.bottom - 80
        if lockable_lg:
            unlock_title = font_small.render("解锁灵根（消耗道韵）", True, (160, 140, 100))
            screen.blit(unlock_title, (zone_scr.x, unlock_y - 28))
            x = zone_scr.x
            for lg in lockable_lg:
                cost = get_linggen_cost(lg.id)
                can_afford = daoyun >= cost
                rect = pygame.Rect(x, unlock_y, 100, 32)
                VILLAGE_UI["unlock_rects"].append((rect, lg.id, "linggen", cost))
                color = (60, 80, 60) if can_afford else (60, 50, 50)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (100, 100, 100), rect, 1)
                txt = font_small.render(f"{lg.name} {cost}", True, (200, 200, 200) if can_afford else (120, 120, 120))
                screen.blit(txt, (rect.x + 5, rect.y + 6))
                x += 110
    if in_fabao_zone and not village_dialogue:
        from unlock import get_accessory_unlock_cost, get_fabao_cost, get_lockable_accessories, get_lockable_fabao

        lockable_fb = get_lockable_fabao(unlocked_fabao, partner_bond_levels)
        lockable_acc = get_lockable_accessories(unlocked_accessories, partner_bond_levels)
        zone_scr = world_to_screen(FABAO_ZONE, cam)
        unlock_y = zone_scr.bottom - 80
        # 法宝解锁
        if lockable_fb:
            unlock_title = font_small.render("解锁法宝（消耗道韵）", True, (160, 140, 100))
            screen.blit(unlock_title, (zone_scr.x, unlock_y - 28))
            x = zone_scr.x
            for fb in lockable_fb:
                cost = get_fabao_cost(fb.id)
                can_afford = daoyun >= cost
                rect = pygame.Rect(x, unlock_y, 100, 32)
                VILLAGE_UI["unlock_rects"].append((rect, fb.id, "fabao", cost))
                color = (60, 80, 60) if can_afford else (60, 50, 50)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (100, 100, 100), rect, 1)
                txt = font_small.render(f"{fb.name} {cost}", True, (200, 200, 200) if can_afford else (120, 120, 120))
                screen.blit(txt, (rect.x + 5, rect.y + 6))
                x += 110
        else:
            from fabao import FABAO_LIST

            if len(unlocked_fabao) < len(FABAO_LIST):
                hint = font_small.render("需治疗对应伙伴才可解锁更多法宝", True, (140, 120, 80))
                screen.blit(hint, (zone_scr.x, unlock_y - 24))
                unlock_y -= 28
        unlock_y -= 42 if lockable_fb else 0
        # 饰品解锁
        if lockable_acc:
            acc_title = font_small.render("解锁饰品（消耗道韵）", True, (160, 140, 100))
            screen.blit(acc_title, (zone_scr.x, unlock_y - 28))
            x = zone_scr.x
            for acc in lockable_acc:
                cost = get_accessory_unlock_cost(acc.id)
                can_afford = daoyun >= cost
                rect = pygame.Rect(x, unlock_y, 100, 32)
                VILLAGE_UI["unlock_rects"].append((rect, acc.id, "accessory", cost))
                color = (60, 80, 60) if can_afford else (60, 50, 50)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (100, 100, 100), rect, 1)
                txt = font_small.render(f"{acc.name} {cost}", True, (200, 200, 200) if can_afford else (120, 120, 120))
                screen.blit(txt, (rect.x + 5, rect.y + 6))
                x += 110
        unlock_y -= 42 if lockable_acc else 0
        # 铸心：饰品槽位、商店刷新（道韵逐步递增）
        from unlock import get_growth_cost

        if accessory_slots < 9:
            cost = get_growth_cost("accessory_slot", accessory_slots)
            can = daoyun >= cost
            rect = pygame.Rect(zone_scr.x, unlock_y, 110, 32)
            VILLAGE_UI["growth_rects"].append((rect, "accessory_slot", cost))
            c = (60, 80, 60) if can else (60, 50, 50)
            pygame.draw.rect(screen, c, rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, 1)
            screen.blit(
                font_small.render(f"饰品槽+1 {cost}", True, (200, 200, 200) if can else (120, 120, 120)),
                (rect.x + 5, rect.y + 6),
            )
        if shop_refresh_count < 3:
            cost = get_growth_cost("shop_refresh", shop_refresh_count)
            can = daoyun >= cost
            rect = pygame.Rect(zone_scr.x + 120, unlock_y, 110, 32)
            VILLAGE_UI["growth_rects"].append((rect, "shop_refresh", cost))
            c = (60, 80, 60) if can else (60, 50, 50)
            pygame.draw.rect(screen, c, rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, 1)
            screen.blit(
                font_small.render(f"刷新+1 {cost}", True, (200, 200, 200) if can else (120, 120, 120)),
                (rect.x + 5, rect.y + 6),
            )
        # 开局饰品：随机1个 / 二选一 / 三选一
        if start_accessory_mode < 3:
            cost = get_growth_cost("start_accessory", start_accessory_mode)
            can = daoyun >= cost
            rect = pygame.Rect(zone_scr.x + 240, unlock_y, 120, 32)
            VILLAGE_UI["growth_rects"].append((rect, "start_accessory", cost))
            c = (60, 80, 60) if can else (60, 50, 50)
            pygame.draw.rect(screen, c, rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, 1)
            lbls = ("随机1饰品", "二选一", "三选一")
            lbl = lbls[start_accessory_mode] if start_accessory_mode < 3 else "三选一"
            screen.blit(
                font_small.render(f"{lbl} {cost}", True, (200, 200, 200) if can else (120, 120, 120)),
                (rect.x + 5, rect.y + 6),
            )

    # 碧落：生命/灵力上限（道韵购买）
    if in_partner_zone == "biluo" and not village_dialogue:
        p_rect = next((r for r, _, pid in PARTNER_ROOMS if pid == "biluo"), None)
        if p_rect:
            zone_scr = world_to_screen(p_rect, cam)
            gy = zone_scr.bottom - 50
            from unlock import get_growth_cost

            items = [("health", "生命+10", base_health_bonus), ("mana", "灵力+10", base_mana_bonus)]
            if potion_cap < 4:
                items.append(("potion_cap", "丹药上限+1", potion_cap))
            for i, (gtype, label, current) in enumerate(items):
                cost = get_growth_cost(gtype, current)
                can = daoyun >= cost
                row, col = i // 2, i % 2
                rect = pygame.Rect(zone_scr.x + 5 + col * 95, gy + row * 32, 90, 28)
                VILLAGE_UI["growth_rects"].append((rect, gtype, cost))
                c = (60, 80, 60) if can else (60, 50, 50)
                pygame.draw.rect(screen, c, rect)
                pygame.draw.rect(screen, (100, 100, 100), rect, 1)
                screen.blit(
                    font_small.render(f"{label} {cost}", True, (200, 200, 200) if can else (120, 120, 120)),
                    (rect.x + 5, rect.y + 4),
                )


def _draw_achievement_overlay(screen, achievements_unlocked):
    """绘制成就面板"""
    from achievement import ACHIEVEMENT_LIST

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((25, 30, 45))
    screen.blit(overlay, (0, 0))
    font = get_font(28)
    font_small = get_font(20)
    title = font.render("成就", True, (220, 200, 150))
    t_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
    screen.blit(title, t_rect)
    count = font_small.render(f"已解锁 {len(achievements_unlocked)} / {len(ACHIEVEMENT_LIST)}", True, (160, 160, 160))
    c_rect = count.get_rect(center=(SCREEN_WIDTH // 2, 90))
    screen.blit(count, c_rect)
    y = 130
    for a in ACHIEVEMENT_LIST:
        unlocked = a.id in achievements_unlocked
        color = (200, 200, 200) if unlocked else (100, 100, 100)
        name_txt = font_small.render(f"{'✓ ' if unlocked else '○ '}{a.name}", True, color)
        screen.blit(name_txt, (80, y))
        desc_txt = font_small.render(a.desc, True, (140, 140, 140) if unlocked else (80, 80, 80))
        screen.blit(desc_txt, (100, y + 24))
        y += 55
    if not ACHIEVEMENT_LIST:
        hint = font_small.render("成就条目待规划，见 docs/ACHIEVEMENT_TODO.md", True, (120, 120, 120))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
    hint_close = font_small.render("点击或按空格关闭", True, (140, 140, 140))
    h_rect = hint_close.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
    screen.blit(hint_close, h_rect)


def _draw_dialogue_overlay(screen, npc_key):
    """绘制 NPC 对话弹窗"""
    from village_npc import NPC_DIALOGUES

    data = NPC_DIALOGUES.get(npc_key, {})
    name = data.get("name", "未知")
    lines = data.get("lines", [])
    if not lines:
        return
    # 取当前显示的第一句（对话可多句，此处简化为一句）
    text = lines[0] if lines else ""
    # 半透明遮罩
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((20, 25, 35))
    screen.blit(overlay, (0, 0))
    font = get_font(24)
    font_small = get_font(20)
    # 对话框
    box_w, box_h = 500, 140
    box = pygame.Rect((SCREEN_WIDTH - box_w) // 2, (SCREEN_HEIGHT - box_h) // 2, box_w, box_h)
    pygame.draw.rect(screen, (50, 55, 75), box)
    pygame.draw.rect(screen, (120, 140, 180), box, 2)
    # NPC 名
    name_txt = font.render(name, True, (220, 200, 150))
    screen.blit(name_txt, (box.x + 20, box.y + 15))
    # 对话内容
    content = font_small.render(text, True, COLOR_UI)
    screen.blit(content, (box.x + 20, box.y + 55))
    # 提示
    hint = font_small.render("点击或按空格继续", True, (140, 140, 140))
    screen.blit(hint, (box.x + box_w - 180, box.y + box_h - 35))


def _draw_selection_panel(screen, items, choice, zone_rect, font, attr_colors, out_rects):
    """在区域内绘制选择项（圆形）"""
    n = len(items)
    if n == 0:
        return
    item_r = 28 if n > 4 else 36
    gap = 10
    total_w = n * (item_r * 2) + (n - 1) * gap
    start_x = zone_rect.x + (zone_rect.w - total_w) // 2 + item_r
    cy = zone_rect.y + zone_rect.h // 2
    for i, item in enumerate(items):
        cx = start_x + i * (item_r * 2 + gap)
        rect = pygame.Rect(cx - item_r, cy - item_r, item_r * 2, item_r * 2)
        out_rects.append((rect, item))
        is_sel = i == choice
        color = (100, 160, 220) if is_sel else (60, 70, 90)
        pygame.draw.circle(screen, color, (cx, cy), item_r)
        pygame.draw.circle(screen, (180, 180, 180) if is_sel else (100, 100, 100), (cx, cy), item_r, 2)
        c = attr_colors.get(item.attr, (200, 200, 200)) if attr_colors else (200, 200, 200)
        txt = font.render(item.name[:2], True, c)
        t_rect = txt.get_rect(center=(cx, cy))
        screen.blit(txt, t_rect)


def _draw_resonance_panel(screen, resonance_system):
    """绘制秽源共鸣选择面板"""
    from resonance_system import ResonanceType, get_all_pacts

    # 半透明背景
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((20, 25, 35))
    screen.blit(overlay, (0, 0))

    font_title = get_font(32)
    font = get_font(22)
    font_small = get_font(18)

    # 标题
    title = font_title.render("感知秽源侵蚀", True, (220, 200, 150))
    t_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
    screen.blit(title, t_rect)

    # 当前共鸣强度和道韵加成
    intensity = resonance_system.get_total_intensity()
    daoyun_mult = resonance_system.get_daoyun_multiplier()
    info_text = f"当前共鸣强度：{intensity}    净化奖励：道韵 +{int((daoyun_mult - 1) * 100)}%"
    info = font.render(info_text, True, (180, 200, 180))
    i_rect = info.get_rect(center=(SCREEN_WIDTH // 2, 85))
    screen.blit(info, i_rect)

    # 6 大类侵蚀，每类 3 个选项
    all_pacts = get_all_pacts()
    types = [
        (ResonanceType.FURY, "狂暴侵蚀", (255, 120, 100)),
        (ResonanceType.TENACITY, "坚韧侵蚀", (100, 180, 140)),
        (ResonanceType.SWIFT, "迅捷侵蚀", (120, 200, 255)),
        (ResonanceType.SWARM, "增殖侵蚀", (180, 140, 255)),
        (ResonanceType.CHAOS, "混沌侵蚀", (255, 180, 100)),
        (ResonanceType.BARREN, "贫瘠侵蚀", (140, 120, 100)),
    ]

    VILLAGE_UI["resonance_panel_rects"] = []

    y = 130
    for res_type, type_name, type_color in types:
        # 类型标题
        type_title = font.render(type_name, True, type_color)
        screen.blit(type_title, (80, y))

        # 3 个等级选项
        pacts = [p for p in all_pacts if p.type == res_type]
        x = 250
        for pact in pacts:
            # 检查是否已选择
            is_selected = pact in resonance_system.active_pacts

            # 绘制复选框
            checkbox_rect = pygame.Rect(x, y, 280, 32)
            VILLAGE_UI["resonance_panel_rects"].append((checkbox_rect, pact))

            is_hover = checkbox_rect.collidepoint(pygame.mouse.get_pos())
            bg_color = (80, 100, 120) if is_selected else ((60, 75, 90) if is_hover else (45, 55, 70))
            pygame.draw.rect(screen, bg_color, checkbox_rect)
            pygame.draw.rect(screen, (140, 160, 180) if is_selected else (100, 120, 140), checkbox_rect, 2)

            # 复选框标记
            check_box = pygame.Rect(x + 5, y + 8, 16, 16)
            pygame.draw.rect(screen, (200, 200, 200), check_box, 1)
            if is_selected:
                pygame.draw.line(
                    screen,
                    (100, 255, 100),
                    (check_box.x + 3, check_box.centery),
                    (check_box.centerx, check_box.bottom - 3),
                    2,
                )
                pygame.draw.line(
                    screen,
                    (100, 255, 100),
                    (check_box.centerx, check_box.bottom - 3),
                    (check_box.right - 3, check_box.y + 3),
                    2,
                )

            # 文本
            pact_text = font_small.render(f"{pact.name} (+{pact.intensity})", True, (220, 220, 220))
            screen.blit(pact_text, (x + 28, y + 2))

            # 描述
            desc_text = font_small.render(pact.desc, True, (160, 160, 160))
            screen.blit(desc_text, (x + 28, y + 18))

            x += 300

        y += 50

    # 专属掉落提示
    if intensity > 0:
        drops = resonance_system.get_unique_drops()
        if drops:
            drop_title = font.render("专属掉落：", True, (200, 180, 120))
            screen.blit(drop_title, (80, y + 10))
            drop_text = "、".join([d.replace("_", " ").title() for d in drops[:3]])  # 最多显示3个
            if len(drops) > 3:
                drop_text += f" 等 {len(drops)} 种"
            drop_info = font_small.render(drop_text, True, (180, 160, 100))
            screen.blit(drop_info, (200, y + 12))

    # 确认和取消按钮
    btn_y = SCREEN_HEIGHT - 80
    confirm_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, btn_y, 100, 40)
    cancel_rect = pygame.Rect(SCREEN_WIDTH // 2 + 20, btn_y, 100, 40)

    VILLAGE_UI["resonance_confirm_rect"] = confirm_rect
    VILLAGE_UI["resonance_cancel_rect"] = cancel_rect

    # 确认按钮
    is_confirm_hover = confirm_rect.collidepoint(pygame.mouse.get_pos())
    confirm_color = (80, 140, 100) if is_confirm_hover else (60, 100, 70)
    pygame.draw.rect(screen, confirm_color, confirm_rect)
    pygame.draw.rect(screen, (120, 180, 140), confirm_rect, 2)
    confirm_text = font.render("确认", True, (255, 255, 255))
    c_rect = confirm_text.get_rect(center=confirm_rect.center)
    screen.blit(confirm_text, c_rect)

    # 取消按钮
    is_cancel_hover = cancel_rect.collidepoint(pygame.mouse.get_pos())
    cancel_color = (140, 80, 80) if is_cancel_hover else (100, 60, 60)
    pygame.draw.rect(screen, cancel_color, cancel_rect)
    pygame.draw.rect(screen, (180, 120, 120), cancel_rect, 2)
    cancel_text = font.render("取消", True, (255, 255, 255))
    ca_rect = cancel_text.get_rect(center=cancel_rect.center)
    screen.blit(cancel_text, ca_rect)

    # 提示
    hint = font_small.render("同类型只能选择一个等级", True, (140, 140, 140))
    h_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
    screen.blit(hint, h_rect)


# 兼容 game.py：from village import draw as draw_village
draw = draw_village
