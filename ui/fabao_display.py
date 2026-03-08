"""
法宝显示组件 - 显示当前法宝图标
可以扩展为显示两个法宝（双法宝系统）
"""

import pygame

from ui.components import Colors, FontSize, Spacing, UIComponent, draw_text


class FabaoDisplay(UIComponent):
    """法宝显示组件"""

    def __init__(self, x, y):
        # 单个法宝图标：64×64（包含边框和名称）
        super().__init__(x, y, 64, 80)

        self.player = None
        self.icon_size = 48
        self.hover_scale = 1.0
        self.target_scale = 1.0

    def set_player(self, player):
        """设置玩家引用"""
        self.player = player

    def update(self, dt, mouse_pos):
        super().update(dt, mouse_pos)

        # 悬停放大效果
        self.target_scale = 1.1 if self.hover else 1.0

        # 平滑过渡
        if abs(self.hover_scale - self.target_scale) > 0.01:
            self.hover_scale += (self.target_scale - self.hover_scale) * 10 * dt
        else:
            self.hover_scale = self.target_scale

    def _draw_impl(self, screen):
        if not self.player or not self.player.fabao:
            return

        fabao = self.player.fabao

        # 计算缩放后的尺寸
        scaled_size = int(self.icon_size * self.hover_scale)
        offset = (self.icon_size - scaled_size) // 2

        icon_x = self.x + 8 + offset
        icon_y = self.y + offset

        # 绘制图标背景（占位符）
        # TODO: 替换为实际图标图片
        icon_rect = pygame.Rect(icon_x, icon_y, scaled_size, scaled_size)

        # 根据属性选择背景颜色
        attr_color = {
            "FIRE": Colors.FIRE,
            "WATER": Colors.WATER,
            "WOOD": Colors.WOOD,
            "METAL": Colors.METAL,
            "EARTH": Colors.EARTH,
        }.get(fabao.attr.name, Colors.TEXT_GRAY)

        # 绘制图标背景
        pygame.draw.rect(screen, attr_color, icon_rect)

        # 绘制边框（高亮）
        border_color = Colors.BORDER_GOLD if self.hover else Colors.BORDER_DARK
        border_width = 3 if self.hover else 2
        pygame.draw.rect(screen, border_color, icon_rect, border_width)

        # 绘制法宝名称
        name_y = self.y + self.icon_size + 8
        draw_text(screen, fabao.name[:4], self.x + 8, name_y, FontSize.XS, Colors.TEXT_LIGHT, center=False)

        # 如果悬停，显示详细信息
        if self.hover:
            self._draw_tooltip(screen, fabao)

    def _draw_tooltip(self, screen, fabao):
        """绘制悬停提示"""
        tooltip_x = self.x + self.width + 10
        tooltip_y = self.y
        tooltip_width = 200
        tooltip_height = 120

        # 背景
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        pygame.draw.rect(tooltip_surface, Colors.PANEL_BG, (0, 0, tooltip_width, tooltip_height))
        pygame.draw.rect(tooltip_surface, Colors.BORDER_GOLD, (0, 0, tooltip_width, tooltip_height), 2)
        screen.blit(tooltip_surface, (tooltip_x, tooltip_y))

        # 法宝名称
        draw_text(screen, fabao.name, tooltip_x + Spacing.SM, tooltip_y + Spacing.SM, FontSize.BASE, Colors.TEXT_GOLD)

        # 属性
        attr_text = {
            "FIRE": "火属性",
            "WATER": "水属性",
            "WOOD": "木属性",
            "METAL": "金属性",
            "EARTH": "土属性",
        }.get(fabao.attr.name, "未知")

        attr_color = {
            "FIRE": Colors.FIRE,
            "WATER": Colors.WATER,
            "WOOD": Colors.WOOD,
            "METAL": Colors.METAL,
            "EARTH": Colors.EARTH,
        }.get(fabao.attr.name, Colors.TEXT_GRAY)

        draw_text(screen, attr_text, tooltip_x + Spacing.SM, tooltip_y + Spacing.SM + 22, FontSize.SM, attr_color)

        # 攻击形态
        form_text = {
            "arc": "弧形挥砍",
            "pierce": "直线穿透",
            "fan": "扇形范围",
            "heavy": "重击",
            "parabolic": "抛物线",
        }.get(fabao.attack_form, "普通攻击")

        draw_text(
            screen,
            f"形态: {form_text}",
            tooltip_x + Spacing.SM,
            tooltip_y + Spacing.SM + 44,
            FontSize.SM,
            Colors.TEXT_LIGHT,
        )

        # 伤害和攻速
        draw_text(
            screen,
            f"伤害: {fabao.damage}",
            tooltip_x + Spacing.SM,
            tooltip_y + Spacing.SM + 66,
            FontSize.SM,
            Colors.TEXT_LIGHT,
        )

        cd_text = f"{fabao.attack_cooldown:.2f}s"
        draw_text(
            screen,
            f"攻速: {cd_text}",
            tooltip_x + Spacing.SM,
            tooltip_y + Spacing.SM + 88,
            FontSize.SM,
            Colors.TEXT_LIGHT,
        )


class DualFabaoDisplay(UIComponent):
    """双法宝显示组件 - 显示两个法宝"""

    def __init__(self, x, y):
        # 两个法宝图标：140×80
        super().__init__(x, y, 140, 80)

        self.player = None

        # 法宝1（当前手持）
        self.fabao1_display = FabaoDisplay(x, y)

        # 法宝2（备用）
        self.fabao2_display = FabaoDisplay(x + 70, y)

    def set_player(self, player):
        """设置玩家引用"""
        self.player = player
        self.fabao1_display.set_player(player)
        self.fabao2_display.set_player(player)

    def update(self, dt, mouse_pos):
        super().update(dt, mouse_pos)

        if self.player:
            self.fabao1_display.update(dt, mouse_pos)
            # TODO: 如果有第二个法宝，更新 fabao2_display

    def _draw_impl(self, screen):
        if not self.player:
            return

        # 绘制法宝1（当前手持）
        self.fabao1_display.draw(screen)

        # TODO: 如果有第二个法宝，绘制 fabao2_display

        # 绘制切换提示
        hint_y = self.y + 85
        draw_text(screen, "[Tab] 切换法宝", self.x, hint_y, FontSize.XS, Colors.TEXT_DARK)
