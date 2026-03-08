"""
左上角 HUD - 显示血条、蓝条、资源
参考小骨英雄的设计
"""

import pygame

from ui.components import Colors, FontSize, Panel, ProgressBar, Spacing, UIComponent, draw_text


class HUD(UIComponent):
    """左上角 HUD 组件"""

    def __init__(self, x=10, y=10):
        # HUD 尺寸：150×280
        super().__init__(x, y, 150, 280)

        # 背景面板
        self.panel = Panel(x, y, 150, 280)

        # 血条
        self.hp_bar = ProgressBar(
            x + Spacing.MD,
            y + Spacing.MD + 20,
            126,  # 150 - 24 (左右边距)
            20,
            Colors.HP_RED,
            Colors.HP_RED_BG,
        )

        # 蓝条
        self.mp_bar = ProgressBar(x + Spacing.MD, y + Spacing.MD + 60, 126, 20, Colors.MP_BLUE, Colors.MP_BLUE_BG)

        # 玩家数据引用
        self.player = None

    def set_player(self, player):
        """设置玩家引用"""
        self.player = player

    def update(self, dt, mouse_pos):
        super().update(dt, mouse_pos)

        if self.player:
            # 更新血条
            self.hp_bar.set_value(self.player.health, self.player.max_health)
            self.hp_bar.update(dt, mouse_pos)

            # 更新蓝条
            self.mp_bar.set_value(self.player.mana, self.player.max_mana)
            self.mp_bar.update(dt, mouse_pos)

    def _draw_impl(self, screen):
        # 绘制背景面板
        self.panel.draw(screen)

        if not self.player:
            return

        # 绘制血条标签和图标
        draw_text(screen, "❤", self.x + Spacing.MD, self.y + Spacing.MD, FontSize.BASE, Colors.HP_RED)
        draw_text(screen, "生命", self.x + Spacing.MD + 20, self.y + Spacing.MD, FontSize.SM, Colors.TEXT_LIGHT)

        # 绘制血条
        self.hp_bar.draw(screen)

        # 绘制血量数值
        hp_text = f"{int(self.player.health)}/{int(self.player.max_health)}"
        draw_text(screen, hp_text, self.x + Spacing.MD, self.y + Spacing.MD + 42, FontSize.SM, Colors.TEXT_LIGHT)

        # 绘制蓝条标签和图标
        draw_text(screen, "💧", self.x + Spacing.MD, self.y + Spacing.MD + 50, FontSize.BASE, Colors.MP_BLUE)
        draw_text(screen, "灵力", self.x + Spacing.MD + 20, self.y + Spacing.MD + 50, FontSize.SM, Colors.TEXT_LIGHT)

        # 绘制蓝条
        self.mp_bar.draw(screen)

        # 绘制灵力数值
        mp_text = f"{int(self.player.mana)}/{int(self.player.max_mana)}"
        draw_text(screen, mp_text, self.x + Spacing.MD, self.y + Spacing.MD + 82, FontSize.SM, Colors.TEXT_LIGHT)

        # 绘制分隔线
        pygame.draw.line(
            screen,
            Colors.BORDER_DARK,
            (self.x + Spacing.MD, self.y + 110),
            (self.x + self.width - Spacing.MD, self.y + 110),
            1,
        )

        # 绘制资源
        # 灵石
        draw_text(screen, "💰", self.x + Spacing.MD, self.y + 120, FontSize.BASE, Colors.LINGSHI_GOLD)
        draw_text(
            screen, str(self.player.lingshi), self.x + Spacing.MD + 25, self.y + 122, FontSize.XL, Colors.LINGSHI_GOLD
        )

        # 道韵（从 meta 获取）
        try:
            from meta import meta

            daoyun = meta.daoyun
        except:
            daoyun = 0

        draw_text(screen, "📿", self.x + Spacing.MD, self.y + 150, FontSize.BASE, Colors.DAOYUN_JADE)
        draw_text(screen, str(daoyun), self.x + Spacing.MD + 25, self.y + 152, FontSize.XL, Colors.DAOYUN_JADE)

        # 绘制分隔线
        pygame.draw.line(
            screen,
            Colors.BORDER_DARK,
            (self.x + Spacing.MD, self.y + 180),
            (self.x + self.width - Spacing.MD, self.y + 180),
            1,
        )

        # 绘制法宝快捷显示（简化版）
        if self.player.fabao:
            fabao_y = self.y + 190

            # 法宝名称
            draw_text(screen, "法宝", self.x + Spacing.MD, fabao_y, FontSize.SM, Colors.TEXT_GRAY)

            # 法宝名称和属性
            fabao_name = self.player.fabao.name[:6]  # 限制长度
            draw_text(screen, fabao_name, self.x + Spacing.MD, fabao_y + 18, FontSize.BASE, Colors.TEXT_LIGHT)

            # 属性颜色
            attr_color = {
                "FIRE": Colors.FIRE,
                "WATER": Colors.WATER,
                "WOOD": Colors.WOOD,
                "METAL": Colors.METAL,
                "EARTH": Colors.EARTH,
            }.get(self.player.fabao.attr.name, Colors.TEXT_GRAY)

            attr_text = {
                "FIRE": "火",
                "WATER": "水",
                "WOOD": "木",
                "METAL": "金",
                "EARTH": "土",
            }.get(self.player.fabao.attr.name, "?")

            draw_text(screen, attr_text, self.x + Spacing.MD, fabao_y + 38, FontSize.SM, attr_color)

        # 绘制提示
        hint_y = self.y + self.height - 30
        draw_text(screen, "[I] 角色面板", self.x + Spacing.MD, hint_y, FontSize.XS, Colors.TEXT_DARK)
