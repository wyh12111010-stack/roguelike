"""
快捷键提示和操作说明界面
帮助玩家快速了解游戏操作
"""

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH, get_font

# ==================== 快捷键配置 ====================

KEYBINDS = {
    "移动": {
        "keys": ["WASD", "方向键"],
        "desc": "控制角色移动",
    },
    "攻击": {
        "keys": ["鼠标左键"],
        "desc": "朝鼠标方向攻击",
    },
    "技能": {
        "keys": ["E"],
        "desc": "释放当前法宝技能",
    },
    "闪避": {
        "keys": ["空格", "Shift"],
        "desc": "快速冲刺，短暂无敌",
    },
    "切换法宝": {
        "keys": ["Q", "鼠标滚轮"],
        "desc": "切换手持法宝",
    },
    "使用药水": {
        "keys": ["R"],
        "desc": "使用丹药回复生命",
    },
    "角色面板": {
        "keys": ["C"],
        "desc": "查看灵根、法宝、饰品",
    },
    "共鸣面板": {
        "keys": ["V"],
        "desc": "查看元素共鸣效果",
    },
    "暂停": {
        "keys": ["ESC"],
        "desc": "暂停游戏/关闭面板",
    },
}


# ==================== 游戏提示 ====================

GAME_TIPS = [
    "💡 灵根决定你的元素属性，影响元素反应",
    "💡 法宝决定攻击方式，每个法宝有独特技能",
    "💡 饰品提供被动加成，可以叠加多个",
    "💡 元素反应能造成额外伤害，注意敌人属性",
    "💡 共鸣系统：多个相同元素可以触发强力效果",
    "💡 闪避有短暂无敌时间，用来躲避危险攻击",
    "💡 商店价格会随购买次数上涨，合理规划",
    "💡 道韵用于村子永久升级，不会在死亡时丢失",
    "💡 灵石用于战斗中购买，死亡后清零",
    "💡 暴击率可以通过饰品提升，暴击伤害2倍",
]


# ==================== 操作说明界面 ====================


class HelpPanel:
    """操作说明面板"""

    def __init__(self):
        self.visible = False
        self.current_tab = "keybinds"  # keybinds | tips

    def toggle(self):
        """切换显示/隐藏"""
        self.visible = not self.visible

    def draw(self, screen):
        """绘制面板"""
        if not self.visible:
            return

        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))

        # 面板背景
        panel_w, panel_h = 800, 600
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2

        panel_bg = pygame.Surface((panel_w, panel_h))
        panel_bg.fill((40, 40, 50))
        screen.blit(panel_bg, (panel_x, panel_y))

        # 边框
        pygame.draw.rect(screen, (180, 150, 90), (panel_x, panel_y, panel_w, panel_h), 3)

        # 标题
        title_font = get_font(32)
        title = title_font.render("操作说明", True, (255, 215, 0))
        title_x = panel_x + (panel_w - title.get_width()) // 2
        screen.blit(title, (title_x, panel_y + 20))

        # 标签页
        tab_y = panel_y + 70
        tab_font = get_font(20)

        # 快捷键标签
        keybind_color = (255, 215, 0) if self.current_tab == "keybinds" else (150, 150, 150)
        keybind_tab = tab_font.render("[1] 快捷键", True, keybind_color)
        screen.blit(keybind_tab, (panel_x + 50, tab_y))

        # 提示标签
        tips_color = (255, 215, 0) if self.current_tab == "tips" else (150, 150, 150)
        tips_tab = tab_font.render("[2] 游戏提示", True, tips_color)
        screen.blit(tips_tab, (panel_x + 250, tab_y))

        # 内容区域
        content_y = tab_y + 50

        if self.current_tab == "keybinds":
            self._draw_keybinds(screen, panel_x, content_y, panel_w)
        else:
            self._draw_tips(screen, panel_x, content_y, panel_w)

        # 底部提示
        hint_font = get_font(18)
        hint = hint_font.render("按 [H] 或 [ESC] 关闭", True, (150, 150, 150))
        hint_x = panel_x + (panel_w - hint.get_width()) // 2
        screen.blit(hint, (hint_x, panel_y + panel_h - 40))

    def _draw_keybinds(self, screen, x, y, width):
        """绘制快捷键列表"""
        key_font = get_font(18)
        desc_font = get_font(16)

        current_y = y
        for action, info in KEYBINDS.items():
            # 操作名称
            action_text = key_font.render(action, True, (255, 215, 0))
            screen.blit(action_text, (x + 50, current_y))

            # 按键
            keys_text = " / ".join(info["keys"])
            keys_surface = key_font.render(keys_text, True, (100, 200, 255))
            screen.blit(keys_surface, (x + 200, current_y))

            # 说明
            desc_surface = desc_font.render(info["desc"], True, (180, 180, 180))
            screen.blit(desc_surface, (x + 450, current_y))

            current_y += 40

    def _draw_tips(self, screen, x, y, width):
        """绘制游戏提示"""
        tip_font = get_font(18)

        current_y = y
        for tip in GAME_TIPS:
            tip_surface = tip_font.render(tip, True, (200, 200, 200))
            screen.blit(tip_surface, (x + 50, current_y))
            current_y += 45

    def handle_input(self, event):
        """处理输入"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h or event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
            elif event.key == pygame.K_1:
                self.current_tab = "keybinds"
                return True
            elif event.key == pygame.K_2:
                self.current_tab = "tips"
                return True
        return False


# ==================== 快捷提示HUD ====================


class QuickTipsHUD:
    """快捷提示HUD（屏幕右下角）"""

    def __init__(self):
        self.tips = [
            "[H] 帮助",
            "[C] 角色",
            "[V] 共鸣",
        ]
        self.visible = True

    def draw(self, screen):
        """绘制快捷提示"""
        if not self.visible:
            return

        font = get_font(16)
        x = SCREEN_WIDTH - 150
        y = SCREEN_HEIGHT - 100

        for tip in self.tips:
            tip_surface = font.render(tip, True, (150, 150, 150))
            screen.blit(tip_surface, (x, y))
            y += 25


# ==================== 全局实例 ====================

_help_panel = None
_quick_tips_hud = None


def init_help_system():
    """初始化帮助系统"""
    global _help_panel, _quick_tips_hud
    _help_panel = HelpPanel()
    _quick_tips_hud = QuickTipsHUD()
    return _help_panel, _quick_tips_hud


def get_help_panel():
    """获取帮助面板"""
    global _help_panel
    if _help_panel is None:
        _help_panel = HelpPanel()
    return _help_panel


def get_quick_tips_hud():
    """获取快捷提示HUD"""
    global _quick_tips_hud
    if _quick_tips_hud is None:
        _quick_tips_hud = QuickTipsHUD()
    return _quick_tips_hud
