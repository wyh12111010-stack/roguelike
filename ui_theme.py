"""修仙风格 UI 主题系统 - 古风仙侠视觉"""
import pygame
import math

# ==================== 配色方案 ====================
# 主色调：青铜、朱砂、碧玉、金箔
THEME_COLORS = {
    # 背景层
    "bg_deep": (15, 18, 25),           # 深邃夜空
    "bg_mid": (25, 30, 42),            # 中层背景
    "bg_light": (35, 42, 58),          # 浅层背景
    
    # 修仙元素
    "immortal_gold": (218, 165, 32),   # 仙金
    "immortal_jade": (64, 224, 208),   # 碧玉
    "immortal_red": (220, 20, 60),     # 朱砂
    "immortal_purple": (138, 43, 226), # 紫气
    "immortal_cyan": (0, 206, 209),    # 青灵
    
    # 五行色
    "fire": (255, 69, 0),              # 火红
    "water": (30, 144, 255),           # 水蓝
    "wood": (34, 139, 34),             # 木绿
    "metal": (192, 192, 192),          # 金银
    "earth": (139, 90, 43),            # 土褐
    
    # UI 元素
    "panel_bg": (20, 25, 35, 230),     # 面板背景（半透明）
    "panel_border": (180, 150, 90),    # 金铜描边
    "panel_glow": (255, 215, 0, 100),  # 金色光晕
    
    "button_normal": (45, 55, 75),     # 按钮常态
    "button_hover": (65, 80, 110),     # 按钮悬停
    "button_active": (85, 105, 140),   # 按钮激活
    "button_border": (150, 130, 80),   # 按钮边框
    
    "text_primary": (240, 230, 210),   # 主文本（米黄）
    "text_secondary": (180, 170, 150), # 次要文本
    "text_highlight": (255, 215, 0),   # 高亮文本（金色）
    "text_dim": (120, 110, 100),       # 暗淡文本
    
    # 资源颜色
    "daoyun": (218, 165, 32),          # 道韵（金色）
    "lingshi": (64, 224, 208),         # 灵石（青色）
    "health": (220, 20, 60),           # 生命（朱红）
    "mana": (0, 191, 255),             # 灵力（深空蓝）
}

# ==================== 渐变效果 ====================
def create_gradient_surface(width, height, color_top, color_bottom, vertical=True):
    """创建渐变表面"""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    if vertical:
        for y in range(height):
            ratio = y / height
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            a = 255
            if len(color_top) > 3:
                a = int(color_top[3] * (1 - ratio) + color_bottom[3] * ratio)
            pygame.draw.line(surface, (r, g, b, a), (0, y), (width, y))
    else:
        for x in range(width):
            ratio = x / width
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            a = 255
            if len(color_top) > 3:
                a = int(color_top[3] * (1 - ratio) + color_bottom[3] * ratio)
            pygame.draw.line(surface, (r, g, b, a), (x, 0), (x, height))
    
    return surface

# ==================== 光晕效果 ====================
def draw_glow(surface, center, radius, color, intensity=1.0):
    """绘制光晕效果"""
    glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    
    for i in range(radius, 0, -2):
        alpha = int((i / radius) * intensity * 60)
        alpha = min(255, max(0, alpha))
        pygame.draw.circle(glow_surf, (*color[:3], alpha), (radius, radius), i)
    
    surface.blit(glow_surf, (center[0] - radius, center[1] - radius), special_flags=pygame.BLEND_ADD)

# ==================== 古风边框 ====================
def draw_ancient_border(surface, rect, color, thickness=2, corner_size=12):
    """绘制古风边框（带转角装饰）"""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    
    # 主边框
    pygame.draw.rect(surface, color, rect, thickness)
    
    # 四角装饰
    corners = [
        (x, y),                    # 左上
        (x + w, y),                # 右上
        (x, y + h),                # 左下
        (x + w, y + h),            # 右下
    ]
    
    for cx, cy in corners:
        # 小方块装饰
        corner_rect = pygame.Rect(cx - corner_size // 2, cy - corner_size // 2, corner_size, corner_size)
        pygame.draw.rect(surface, color, corner_rect, thickness)
        
        # 内部小点
        inner_size = corner_size // 3
        inner_rect = pygame.Rect(cx - inner_size // 2, cy - inner_size // 2, inner_size, inner_size)
        pygame.draw.rect(surface, color, inner_rect)

# ==================== 仙气粒子 ====================
class ImmortalParticle:
    """仙气粒子"""
    def __init__(self, x, y, color, lifetime=2.0):
        self.x = x
        self.y = y
        self.vx = (pygame.time.get_ticks() % 100 - 50) / 50.0
        self.vy = -20 - (pygame.time.get_ticks() % 30)
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.size = 2 + (pygame.time.get_ticks() % 3)
    
    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 5 * dt  # 轻微上升减速
        return self.age < self.lifetime
    
    def draw(self, surface):
        alpha = int(255 * (1 - self.age / self.lifetime))
        alpha = max(0, min(255, alpha))
        color = (*self.color[:3], alpha)
        
        # 绘制粒子
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, color, pos, int(self.size))

# ==================== 动态背景 ====================
class AnimatedBackground:
    """动态修仙背景"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.time = 0
        self.stars = []
        
        # 生成星星
        for _ in range(100):
            self.stars.append({
                "x": pygame.time.get_ticks() % width,
                "y": pygame.time.get_ticks() % height,
                "size": 1 + pygame.time.get_ticks() % 2,
                "brightness": 100 + pygame.time.get_ticks() % 155,
                "twinkle_speed": 0.5 + (pygame.time.get_ticks() % 100) / 100.0,
            })
    
    def update(self, dt):
        self.time += dt
    
    def draw(self, surface):
        # 深邃夜空渐变
        gradient = create_gradient_surface(
            self.width, self.height,
            THEME_COLORS["bg_deep"],
            THEME_COLORS["bg_mid"]
        )
        surface.blit(gradient, (0, 0))
        
        # 闪烁星辰
        for star in self.stars:
            brightness = star["brightness"] + int(50 * math.sin(self.time * star["twinkle_speed"]))
            brightness = max(50, min(255, brightness))
            color = (brightness, brightness, brightness)
            pygame.draw.circle(surface, color, (int(star["x"]), int(star["y"])), star["size"])

# ==================== 面板绘制 ====================
def draw_panel(surface, rect, title=None, glow=True):
    """绘制修仙风格面板"""
    # 背景渐变
    bg_gradient = create_gradient_surface(
        rect.width, rect.height,
        THEME_COLORS["panel_bg"],
        (*THEME_COLORS["bg_deep"], 200)
    )
    surface.blit(bg_gradient, rect.topleft)
    
    # 光晕效果
    if glow:
        for corner in [(rect.left, rect.top), (rect.right, rect.top), 
                       (rect.left, rect.bottom), (rect.right, rect.bottom)]:
            draw_glow(surface, corner, 30, THEME_COLORS["immortal_gold"], 0.3)
    
    # 古风边框
    draw_ancient_border(surface, rect, THEME_COLORS["panel_border"], 2, 10)
    
    # 标题
    if title:
        from config import get_font
        font = get_font(24)
        title_surf = font.render(title, True, THEME_COLORS["text_highlight"])
        title_rect = title_surf.get_rect(centerx=rect.centerx, top=rect.top + 15)
        
        # 标题光晕
        draw_glow(surface, title_rect.center, 40, THEME_COLORS["immortal_gold"], 0.5)
        surface.blit(title_surf, title_rect)
        
        # 标题下划线
        line_y = title_rect.bottom + 8
        pygame.draw.line(surface, THEME_COLORS["panel_border"], 
                        (rect.left + 20, line_y), (rect.right - 20, line_y), 1)

# ==================== 按钮绘制 ====================
def draw_button(surface, rect, text, is_hover=False, is_active=False, icon=None):
    """绘制修仙风格按钮"""
    # 按钮状态颜色
    if is_active:
        bg_color = THEME_COLORS["button_active"]
        border_color = THEME_COLORS["text_highlight"]
    elif is_hover:
        bg_color = THEME_COLORS["button_hover"]
        border_color = THEME_COLORS["panel_border"]
    else:
        bg_color = THEME_COLORS["button_normal"]
        border_color = THEME_COLORS["button_border"]
    
    # 背景渐变
    gradient = create_gradient_surface(
        rect.width, rect.height,
        bg_color,
        tuple(max(0, c - 20) for c in bg_color[:3])
    )
    surface.blit(gradient, rect.topleft)
    
    # 悬停光晕
    if is_hover:
        draw_glow(surface, rect.center, rect.width // 2, THEME_COLORS["immortal_gold"], 0.2)
    
    # 边框
    pygame.draw.rect(surface, border_color, rect, 2)
    
    # 文本
    from config import get_font
    font = get_font(18)
    text_color = THEME_COLORS["text_highlight"] if is_hover else THEME_COLORS["text_primary"]
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

# ==================== 资源显示 ====================
def draw_resource(surface, x, y, icon_text, value, color):
    """绘制资源显示（道韵、灵石等）"""
    from config import get_font
    
    # 图标背景
    icon_size = 32
    icon_rect = pygame.Rect(x, y, icon_size, icon_size)
    
    # 图标渐变
    gradient = create_gradient_surface(icon_size, icon_size, color, tuple(max(0, c - 40) for c in color[:3]))
    surface.blit(gradient, icon_rect.topleft)
    
    # 图标边框
    pygame.draw.rect(surface, THEME_COLORS["panel_border"], icon_rect, 1)
    
    # 图标文字
    font_icon = get_font(16)
    icon_surf = font_icon.render(icon_text, True, THEME_COLORS["text_primary"])
    icon_text_rect = icon_surf.get_rect(center=icon_rect.center)
    surface.blit(icon_surf, icon_text_rect)
    
    # 数值
    font_value = get_font(20)
    value_surf = font_value.render(str(value), True, color)
    value_rect = value_surf.get_rect(left=icon_rect.right + 8, centery=icon_rect.centery)
    surface.blit(value_surf, value_rect)
    
    # 数值光晕
    draw_glow(surface, value_rect.center, 20, color, 0.3)

# ==================== 进度条 ====================
def draw_progress_bar(surface, rect, value, max_value, color, bg_color=None, show_text=True):
    """绘制修仙风格进度条"""
    if bg_color is None:
        bg_color = tuple(max(0, c - 40) for c in color[:3])
    
    # 背景
    pygame.draw.rect(surface, bg_color, rect)
    
    # 进度
    ratio = max(0, min(1, value / max_value)) if max_value > 0 else 0
    fill_width = int(rect.width * ratio)
    if fill_width > 0:
        fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
        
        # 进度渐变
        gradient = create_gradient_surface(fill_width, rect.height, color, tuple(max(0, c - 30) for c in color[:3]))
        surface.blit(gradient, fill_rect.topleft)
        
        # 进度光晕
        if ratio > 0.1:
            draw_glow(surface, (fill_rect.right, fill_rect.centery), 15, color, 0.5)
    
    # 边框
    pygame.draw.rect(surface, THEME_COLORS["panel_border"], rect, 1)
    
    # 文本
    if show_text:
        from config import get_font
        font = get_font(14)
        text = f"{int(value)}/{int(max_value)}"
        text_surf = font.render(text, True, THEME_COLORS["text_primary"])
        text_rect = text_surf.get_rect(center=rect.center)
        
        # 文字描边
        outline_color = (0, 0, 0)
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            outline_surf = font.render(text, True, outline_color)
            surface.blit(outline_surf, (text_rect.x + dx, text_rect.y + dy))
        
        surface.blit(text_surf, text_rect)

# ==================== 工具函数 ====================
def get_element_color(element_name):
    """获取元素对应的颜色"""
    element_map = {
        "fire": THEME_COLORS["fire"],
        "water": THEME_COLORS["water"],
        "wood": THEME_COLORS["wood"],
        "metal": THEME_COLORS["metal"],
        "earth": THEME_COLORS["earth"],
        "none": THEME_COLORS["text_secondary"],
    }
    return element_map.get(element_name.lower(), THEME_COLORS["text_primary"])
