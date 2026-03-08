"""游戏配置"""

import pygame

from balance_config import cfg as _cfg

# 屏幕
SCREEN_WIDTH = _cfg("display.screen_width", 1600)
SCREEN_HEIGHT = _cfg("display.screen_height", 900)
FPS = _cfg("display.fps", 60)
RESOLUTION_PRESETS = [
    (800, 600),
    (960, 720),
    (1024, 768),
    (1280, 720),
    (1366, 768),
]

# 战斗区域（框内，偏右避开左侧UI）
ARENA_MARGIN = _cfg("display.arena_margin", 60)
ARENA_X = _cfg("display.arena_x", 280)
ARENA_Y = ARENA_MARGIN
ARENA_W = SCREEN_WIDTH - ARENA_X - ARENA_MARGIN
ARENA_H = SCREEN_HEIGHT - ARENA_MARGIN * 2

# 移速
PLAYER_BASE_SPEED = _cfg("player.base_speed", 200)
ENEMY_MAX_SPEED = _cfg("enemy.max_speed", 175)

# 颜色
COLOR_PLAYER = tuple(_cfg("colors.player", [100, 200, 255]))
COLOR_ENEMY = tuple(_cfg("colors.enemy", [255, 100, 100]))
COLOR_PROJECTILE = tuple(_cfg("colors.projectile", [255, 255, 100]))
COLOR_BG = tuple(_cfg("colors.bg", [30, 30, 40]))
COLOR_UI = tuple(_cfg("colors.ui", [200, 200, 200]))
COLOR_ARENA = tuple(_cfg("colors.arena", [60, 60, 80]))
COLOR_ARENA_BORDER = tuple(_cfg("colors.arena_border", [100, 100, 120]))
COLOR_ENTRANCE = (80, 120, 160)
COLOR_ENTRANCE_HOVER = (120, 180, 220)

# 血条蓝条
COLOR_HP_BAR = tuple(_cfg("colors.hp_bar", [220, 60, 60]))
COLOR_HP_BG = tuple(_cfg("colors.hp_bg", [60, 30, 30]))
COLOR_MP_BAR = tuple(_cfg("colors.mp_bar", [60, 120, 220]))
COLOR_MP_BG = tuple(_cfg("colors.mp_bg", [30, 50, 80]))

# 底部 HUD 条（修真风格：朱红/青灵）
COLOR_HUD_HP = (200, 70, 60)  # 朱红
COLOR_HUD_HP_BG = (50, 25, 25)
COLOR_HUD_MP = (60, 140, 200)  # 青灵
COLOR_HUD_MP_BG = (25, 45, 65)
COLOR_HUD_BORDER = (180, 150, 90)  # 金铜描边


def get_font(size):
    """获取支持中文的字体，带回退机制"""
    # 确保pygame.font已初始化
    if not pygame.font.get_init():
        pygame.font.init()

    # 方法1：尝试系统字体
    font_names = [
        "microsoftyahei",
        "Microsoft YaHei",
        "simhei",
        "SimHei",
        "simsun",
        "SimSun",
        "kaiti",
        "dengxian",
        "fangsong",
    ]

    for font_name in font_names:
        try:
            font = pygame.font.SysFont(font_name, size)
            # 测试渲染中文
            test = font.render("测试", True, (255, 255, 255))
            if test.get_width() > 5:  # 确保真的渲染了
                return font
        except:
            continue

    # 方法2：尝试Windows系统字体路径
    try:
        import os

        windows_fonts = [
            r"C:\Windows\Fonts\msyh.ttc",  # 微软雅黑
            r"C:\Windows\Fonts\simhei.ttf",  # 黑体
            r"C:\Windows\Fonts\simsun.ttc",  # 宋体
        ]
        for font_path in windows_fonts:
            if os.path.exists(font_path):
                font = pygame.font.Font(font_path, size)
                test = font.render("测试", True, (255, 255, 255))
                if test.get_width() > 5:
                    return font
    except:
        pass

    # 方法3：返回默认字体（会显示方块，但至少不崩溃）
    return pygame.font.Font(None, size)


# ==================== UI 字体层级 ====================
def get_font_title():
    """标题字体（36px，用于大标题）"""
    try:
        return pygame.font.SysFont("Microsoft YaHei", 36, bold=True)
    except:
        return pygame.font.Font(None, 36)


def get_font_heading():
    """小标题字体（24px，用于章节标题）"""
    try:
        return pygame.font.SysFont("Microsoft YaHei", 24, bold=True)
    except:
        return pygame.font.Font(None, 24)


def get_font_body():
    """正文字体（18px，用于正常文本）"""
    try:
        return pygame.font.SysFont("Microsoft YaHei", 18)
    except:
        return pygame.font.Font(None, 18)


def get_font_small():
    """小字体（14px，用于说明文字）"""
    try:
        return pygame.font.SysFont("Microsoft YaHei", 14)
    except:
        return pygame.font.Font(None, 14)


# ==================== UI 颜色层级 ====================
COLOR_TEXT_TITLE = (255, 215, 0)  # 金色 - 标题
COLOR_TEXT_HEADING = (240, 230, 210)  # 米黄 - 小标题
COLOR_TEXT_BODY = (200, 190, 170)  # 浅灰 - 正文
COLOR_TEXT_DIM = (120, 110, 100)  # 暗灰 - 说明

# ==================== 元素颜色 ====================
ELEMENT_COLORS = {
    "metal": (218, 165, 32),  # 金
    "wood": (34, 139, 34),  # 木
    "water": (30, 144, 255),  # 水
    "fire": (255, 69, 0),  # 火
    "earth": (139, 90, 43),  # 土
}


def draw_element_icon(surface, x, y, attr, size=24):
    """绘制元素图标占位符（彩色圆形）

    Args:
        surface: 绘制表面
        x, y: 中心坐标
        attr: 属性对象或属性名字符串
        size: 图标半径
    """
    from attribute import ATTR_COLORS, Attr

    # 获取颜色
    if isinstance(attr, Attr):
        color = ATTR_COLORS.get(attr, (180, 180, 180))
    elif isinstance(attr, str):
        color = ELEMENT_COLORS.get(attr.lower(), (180, 180, 180))
    else:
        color = (180, 180, 180)

    # 绘制圆形
    pygame.draw.circle(surface, color, (int(x), int(y)), size)
    # 绘制边框
    pygame.draw.circle(surface, (255, 255, 255), (int(x), int(y)), size, 2)
