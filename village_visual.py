"""村子场景视觉升级 - 修仙风格"""

import math

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH, get_font
from ui_theme import (
    THEME_COLORS,
    AnimatedBackground,
    ImmortalParticle,
    create_gradient_surface,
    draw_ancient_border,
    draw_glow,
    draw_panel,
    draw_resource,
    get_element_color,
)

# 全局背景实例
_village_background = None
_village_particles = []


def get_village_background():
    """获取村子背景实例"""
    global _village_background
    if _village_background is None:
        _village_background = AnimatedBackground(1200, 700)
    return _village_background


def update_village_visual(dt):
    """更新村子视觉效果"""
    global _village_particles

    # 更新背景
    bg = get_village_background()
    bg.update(dt)

    # 更新粒子
    _village_particles = [p for p in _village_particles if p.update(dt)]

    # 随机生成仙气粒子
    if pygame.time.get_ticks() % 100 < 5:  # 5% 概率每帧
        import random

        x = random.randint(0, 1200)
        y = random.randint(500, 700)
        color = random.choice(
            [
                THEME_COLORS["immortal_jade"],
                THEME_COLORS["immortal_cyan"],
                THEME_COLORS["immortal_purple"],
            ]
        )
        _village_particles.append(ImmortalParticle(x, y, color, lifetime=3.0))


def draw_village_background(surface, camera_offset):
    """绘制村子背景"""
    bg = get_village_background()

    # 创建临时大表面
    bg_surface = pygame.Surface((1200, 700))
    bg.draw(bg_surface)

    # 绘制仙气粒子
    particle_surface = pygame.Surface((1200, 700), pygame.SRCALPHA)
    for particle in _village_particles:
        particle.draw(particle_surface)
    bg_surface.blit(particle_surface, (0, 0))

    # 根据相机偏移裁剪并绘制
    cam_x, cam_y = camera_offset
    view_rect = pygame.Rect(cam_x, cam_y, SCREEN_WIDTH, SCREEN_HEIGHT)
    surface.blit(bg_surface, (0, 0), view_rect)


def draw_room_enhanced(surface, rect, label, is_active, cam, room_type="normal"):
    """绘制增强版房间"""
    from village import world_to_screen

    r = world_to_screen(rect, cam)

    # 房间类型配色
    type_colors = {
        "linggen": THEME_COLORS["immortal_purple"],
        "fabao": THEME_COLORS["immortal_gold"],
        "center": THEME_COLORS["immortal_jade"],
        "portal": THEME_COLORS["immortal_cyan"],
        "partner": THEME_COLORS["immortal_red"],
        "normal": THEME_COLORS["panel_border"],
    }

    room_color = type_colors.get(room_type, type_colors["normal"])

    # 背景渐变
    if is_active:
        bg_top = (*room_color[:3], 80)
        bg_bottom = (*THEME_COLORS["bg_mid"], 60)
    else:
        bg_top = (*THEME_COLORS["bg_mid"], 40)
        bg_bottom = (*THEME_COLORS["bg_deep"], 30)

    gradient = create_gradient_surface(r.width, r.height, bg_top, bg_bottom)
    surface.blit(gradient, r.topleft)

    # 激活光晕
    if is_active:
        draw_glow(surface, r.center, r.width // 2, room_color, 0.4)

    # 古风边框
    border_color = room_color if is_active else THEME_COLORS["panel_border"]
    draw_ancient_border(surface, r, border_color, 2, 8)

    # 标题
    font = get_font(20)
    text_color = THEME_COLORS["text_highlight"] if is_active else THEME_COLORS["text_secondary"]
    txt = font.render(label, True, text_color)
    txt_rect = txt.get_rect(centerx=r.centerx, top=r.top + 8)

    # 标题光晕
    if is_active:
        draw_glow(surface, txt_rect.center, 30, room_color, 0.3)

    surface.blit(txt, txt_rect)


def draw_portal_enhanced(surface, rect, label, color, hover_color, is_hover, cam, sublabel=None):
    """绘制增强版传送门"""
    from village import world_to_screen

    r = world_to_screen(rect, cam)
    c = hover_color if is_hover else color
    cx, cy = r.centerx, r.centery

    # 传送门光晕（多层）
    for i in range(3):
        radius = r.width // 2 + i * 10
        alpha = 30 - i * 10
        draw_glow(surface, (cx, cy), radius, c, alpha / 100.0)

    # 传送门主体（椭圆渐变）
    portal_surface = pygame.Surface((r.width, r.height), pygame.SRCALPHA)

    # 外圈
    pygame.draw.ellipse(portal_surface, (*c[:3], 200), portal_surface.get_rect(), 4)

    # 内圈渐变
    inner = r.inflate(-20, -15)
    inner_local = pygame.Rect(10, 7, inner.width, inner.height)

    # 创建径向渐变效果
    for i in range(inner_local.width // 2, 0, -2):
        ratio = i / (inner_local.width // 2)
        alpha = int(150 * ratio)
        color_with_alpha = (*c[:3], alpha)
        pygame.draw.ellipse(
            portal_surface,
            color_with_alpha,
            inner_local.inflate(-2 * (inner_local.width // 2 - i), -2 * (inner_local.height // 2 - i)),
        )

    surface.blit(portal_surface, r.topleft)

    # 旋转粒子效果
    time = pygame.time.get_ticks() / 1000.0
    for i in range(8):
        angle = time * 2 + i * (math.pi * 2 / 8)
        px = cx + math.cos(angle) * (r.width // 3)
        py = cy + math.sin(angle) * (r.height // 3)
        particle_color = (*c[:3], 150)
        pygame.draw.circle(surface, particle_color, (int(px), int(py)), 3)

    # 文字
    font = get_font(22)
    txt = font.render(label, True, THEME_COLORS["text_highlight"])

    if sublabel:
        t_rect = txt.get_rect(center=(cx, cy - 10))
        surface.blit(txt, t_rect)

        font_small = get_font(16)
        sub = font_small.render(sublabel, True, THEME_COLORS["text_secondary"])
        s_rect = sub.get_rect(center=(cx, cy + 12))
        surface.blit(sub, s_rect)
    else:
        t_rect = txt.get_rect(center=(cx, cy))
        surface.blit(txt, t_rect)


def draw_player_enhanced(surface, player_rect, cam):
    """绘制增强版玩家"""
    from village import world_to_screen

    pr = world_to_screen(player_rect, cam)

    # 玩家光晕
    draw_glow(surface, pr.center, pr.width, THEME_COLORS["immortal_cyan"], 0.5)

    # 玩家主体渐变
    gradient = create_gradient_surface(
        pr.width, pr.height, THEME_COLORS["immortal_cyan"], THEME_COLORS["immortal_jade"]
    )
    surface.blit(gradient, pr.topleft)

    # 边框
    pygame.draw.rect(surface, THEME_COLORS["text_highlight"], pr, 2)

    # 脚下光圈
    time = pygame.time.get_ticks() / 1000.0
    circle_radius = int(pr.width // 2 + 5 + math.sin(time * 3) * 3)
    pygame.draw.circle(surface, (*THEME_COLORS["immortal_cyan"], 100), (pr.centerx, pr.bottom), circle_radius, 2)


def draw_hud_enhanced(surface):
    """绘制增强版 HUD（顶部资源栏）"""
    from meta import meta

    # HUD 背景面板
    pygame.Rect(0, 0, SCREEN_WIDTH, 60)
    gradient = create_gradient_surface(
        SCREEN_WIDTH, 60, (*THEME_COLORS["bg_mid"], 200), (*THEME_COLORS["bg_deep"], 150)
    )
    surface.blit(gradient, (0, 0))

    # 底部边框
    pygame.draw.line(surface, THEME_COLORS["panel_border"], (0, 59), (SCREEN_WIDTH, 59), 2)

    # 资源显示
    draw_resource(surface, 20, 14, "道", meta.daoyun, THEME_COLORS["daoyun"])
    draw_resource(surface, 150, 14, "石", meta.potion_stock, THEME_COLORS["lingshi"])

    # 丹药上限
    font = get_font(14)
    cap_text = f"/{meta.potion_cap}"
    cap_surf = font.render(cap_text, True, THEME_COLORS["text_dim"])
    surface.blit(cap_surf, (230, 26))


def draw_selection_panel_enhanced(surface, items, choice, zone_rect, font, attr_colors, out_rects):
    """绘制增强版选择面板（灵根/法宝）"""
    n = len(items)
    if n == 0:
        return

    item_size = 60 if n > 4 else 70
    gap = 15
    total_w = n * item_size + (n - 1) * gap
    start_x = zone_rect.x + (zone_rect.w - total_w) // 2
    cy = zone_rect.y + zone_rect.h // 2 + 20

    for i, item in enumerate(items):
        cx = start_x + i * (item_size + gap) + item_size // 2
        rect = pygame.Rect(cx - item_size // 2, cy - item_size // 2, item_size, item_size)
        out_rects.append((rect, item))

        is_sel = i == choice
        is_hover = rect.collidepoint(pygame.mouse.get_pos())

        # 选中/悬停光晕
        if is_sel or is_hover:
            glow_color = (
                attr_colors.get(item.attr, THEME_COLORS["immortal_gold"])
                if attr_colors
                else THEME_COLORS["immortal_gold"]
            )
            draw_glow(surface, (cx, cy), item_size, glow_color, 0.6 if is_sel else 0.3)

        # 背景渐变
        if is_sel:
            bg_color = THEME_COLORS["button_active"]
        elif is_hover:
            bg_color = THEME_COLORS["button_hover"]
        else:
            bg_color = THEME_COLORS["button_normal"]

        gradient = create_gradient_surface(item_size, item_size, bg_color, tuple(max(0, c - 30) for c in bg_color[:3]))
        surface.blit(gradient, rect.topleft)

        # 边框
        border_color = THEME_COLORS["text_highlight"] if is_sel else THEME_COLORS["panel_border"]
        pygame.draw.rect(surface, border_color, rect, 3 if is_sel else 2)

        # 元素颜色标识
        if attr_colors and hasattr(item, "attr"):
            elem_color = attr_colors.get(item.attr, THEME_COLORS["text_primary"])
            elem_indicator = pygame.Rect(rect.x + 4, rect.y + 4, 8, 8)
            pygame.draw.circle(surface, elem_color, elem_indicator.center, 4)

        # 名称
        name_font = get_font(16)
        c = (
            get_element_color(item.attr.name)
            if (attr_colors and hasattr(item, "attr"))
            else THEME_COLORS["text_primary"]
        )
        txt = name_font.render(item.name[:2], True, c)
        t_rect = txt.get_rect(center=(cx, cy))
        surface.blit(txt, t_rect)

        # 完整名称（悬停时显示）
        if is_hover:
            full_name_font = get_font(14)
            full_txt = full_name_font.render(item.name, True, THEME_COLORS["text_highlight"])
            full_rect = full_txt.get_rect(centerx=cx, top=rect.bottom + 5)

            # 名称背景
            bg_rect = full_rect.inflate(10, 4)
            pygame.draw.rect(surface, (*THEME_COLORS["bg_deep"], 200), bg_rect)
            pygame.draw.rect(surface, THEME_COLORS["panel_border"], bg_rect, 1)

            surface.blit(full_txt, full_rect)


def draw_dialogue_enhanced(surface, npc_key, dialogue_text=None):
    """绘制增强版对话框"""
    from village_npc import NPC_DIALOGUES

    # 半透明遮罩
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((*THEME_COLORS["bg_deep"], 180))
    surface.blit(overlay, (0, 0))

    # 对话框
    box_w, box_h = 600, 200
    box_rect = pygame.Rect((SCREEN_WIDTH - box_w) // 2, (SCREEN_HEIGHT - box_h) // 2, box_w, box_h)

    # 绘制面板
    draw_panel(surface, box_rect, glow=True)

    # NPC 信息
    data = NPC_DIALOGUES.get(npc_key, {})
    name = data.get("name", "未知")
    lines = data.get("lines", [])
    text = dialogue_text if dialogue_text else (lines[0] if lines else "...")

    # NPC 名称
    font_name = get_font(26)
    name_surf = font_name.render(name, True, THEME_COLORS["text_highlight"])
    name_rect = name_surf.get_rect(left=box_rect.left + 30, top=box_rect.top + 25)

    # 名称光晕
    draw_glow(surface, name_rect.center, 40, THEME_COLORS["immortal_gold"], 0.4)
    surface.blit(name_surf, name_rect)

    # 对话内容
    font_content = get_font(20)

    # 多行文本处理
    words = text
    max_width = box_w - 60
    lines_to_draw = []
    current_line = ""

    for char in words:
        test_line = current_line + char
        if font_content.size(test_line)[0] > max_width:
            lines_to_draw.append(current_line)
            current_line = char
        else:
            current_line = test_line

    if current_line:
        lines_to_draw.append(current_line)

    # 绘制文本行
    y_offset = box_rect.top + 70
    for line in lines_to_draw[:3]:  # 最多3行
        line_surf = font_content.render(line, True, THEME_COLORS["text_primary"])
        surface.blit(line_surf, (box_rect.left + 30, y_offset))
        y_offset += 30

    # 提示
    font_hint = get_font(16)
    hint = font_hint.render("点击或按空格继续", True, THEME_COLORS["text_dim"])
    hint_rect = hint.get_rect(right=box_rect.right - 20, bottom=box_rect.bottom - 15)
    surface.blit(hint, hint_rect)
