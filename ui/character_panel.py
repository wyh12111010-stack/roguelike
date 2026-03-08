"""
角色面板 - 按 I 打开，显示完整信息
参考小骨英雄的设计：左侧立绘，右侧信息
"""

import pygame

from ui.components import Colors, FontSize, Panel, Spacing, UIComponent, draw_text


class CharacterPanel(UIComponent):
    """角色面板组件"""

    def __init__(self, screen_width=800, screen_height=600):
        # 全屏覆盖，中央面板
        panel_width = 700
        panel_height = 500
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2

        super().__init__(panel_x, panel_y, panel_width, panel_height)

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player = None
        self.visible = False

        # 背景面板
        self.panel = Panel(panel_x, panel_y, panel_width, panel_height)

        # 滚动偏移（如果内容太多）
        self.scroll_offset = 0

    def set_player(self, player):
        """设置玩家引用"""
        self.player = player

    def toggle(self):
        """切换显示/隐藏"""
        self.visible = not self.visible

    def handle_event(self, event):
        """处理事件"""
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                self.toggle()
                return True
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 20)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_offset += 20
                return True

        return False

    def _draw_impl(self, screen):
        if not self.visible or not self.player:
            return

        # 绘制半透明背景遮罩
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # 绘制面板
        self.panel.draw(screen)

        # 标题
        title_y = self.y + Spacing.LG
        draw_text(screen, "角色面板", self.x + self.width // 2, title_y, FontSize.XXL, Colors.TEXT_GOLD, center=True)

        # 关闭提示
        draw_text(screen, "[ESC] 关闭", self.x + self.width - 100, title_y, FontSize.SM, Colors.TEXT_GRAY)

        # 分隔线
        line_y = title_y + 30
        pygame.draw.line(
            screen, Colors.BORDER_GOLD, (self.x + Spacing.LG, line_y), (self.x + self.width - Spacing.LG, line_y), 2
        )

        # 左侧：角色立绘区域（占位符）
        portrait_x = self.x + Spacing.XL
        portrait_y = line_y + Spacing.LG
        portrait_size = 180

        pygame.draw.rect(screen, Colors.BORDER_DARK, (portrait_x, portrait_y, portrait_size, portrait_size), 2)
        draw_text(
            screen,
            "角色立绘",
            portrait_x + portrait_size // 2,
            portrait_y + portrait_size // 2,
            FontSize.SM,
            Colors.TEXT_DARK,
            center=True,
        )

        # 右侧：信息区域
        info_x = portrait_x + portrait_size + Spacing.XL
        info_y = portrait_y - self.scroll_offset

        # 基础属性
        self._draw_section(screen, "基础属性", info_x, info_y)
        info_y += 30

        info_y = self._draw_stat(
            screen, "生命", f"{int(self.player.health)}/{int(self.player.max_health)}", info_x, info_y, Colors.HP_RED
        )
        info_y = self._draw_stat(
            screen, "灵力", f"{int(self.player.mana)}/{int(self.player.max_mana)}", info_x, info_y, Colors.MP_BLUE
        )
        info_y = self._draw_stat(screen, "灵石", str(self.player.lingshi), info_x, info_y, Colors.LINGSHI_GOLD)
        info_y = self._draw_stat(screen, "道韵", str(self.player.daoyun), info_x, info_y, Colors.DAOYUN_JADE)

        info_y += Spacing.LG

        # 灵根
        if self.player.linggen:
            self._draw_section(screen, "灵根", info_x, info_y)
            info_y += 30

            attr_text = {
                "FIRE": "火灵根",
                "WATER": "水灵根",
                "WOOD": "木灵根",
                "METAL": "金灵根",
                "EARTH": "土灵根",
            }.get(self.player.linggen.attr.name, "未知灵根")

            attr_color = {
                "FIRE": Colors.FIRE,
                "WATER": Colors.WATER,
                "WOOD": Colors.WOOD,
                "METAL": Colors.METAL,
                "EARTH": Colors.EARTH,
            }.get(self.player.linggen.attr.name, Colors.TEXT_GRAY)

            draw_text(screen, attr_text, info_x + Spacing.SM, info_y, FontSize.BASE, attr_color)
            info_y += 25

            draw_text(screen, self.player.linggen.name, info_x + Spacing.SM, info_y, FontSize.SM, Colors.TEXT_LIGHT)
            info_y += 25

        info_y += Spacing.LG

        # 法宝
        if self.player.fabao:
            self._draw_section(screen, "法宝", info_x, info_y)
            info_y += 30

            fabao = self.player.fabao

            # 法宝名称
            draw_text(screen, fabao.name, info_x + Spacing.SM, info_y, FontSize.BASE, Colors.TEXT_LIGHT)
            info_y += 25

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

            draw_text(screen, attr_text, info_x + Spacing.SM, info_y, FontSize.SM, attr_color)
            info_y += 20

            # 伤害和攻速
            draw_text(screen, f"伤害: {fabao.damage}", info_x + Spacing.SM, info_y, FontSize.SM, Colors.TEXT_LIGHT)
            info_y += 20

            draw_text(
                screen,
                f"攻速: {fabao.attack_cooldown:.2f}s",
                info_x + Spacing.SM,
                info_y,
                FontSize.SM,
                Colors.TEXT_LIGHT,
            )
            info_y += 25

        info_y += Spacing.LG

        # 饰品
        self._draw_section(screen, f"饰品 ({len(self.player.accessories)}/6)", info_x, info_y)
        info_y += 30

        if self.player.accessories:
            for acc, lv in self.player.accessories[:6]:  # 最多显示6个
                # 饰品名称和等级
                acc_text = f"{acc.name} Lv.{lv}"
                draw_text(screen, acc_text, info_x + Spacing.SM, info_y, FontSize.SM, Colors.TEXT_LIGHT)
                info_y += 20

                # 效果描述（简化）
                if hasattr(acc, "damage_pct") and acc.damage_pct:
                    effect = f"  伤害 +{acc.damage_pct * lv}%"
                    draw_text(screen, effect, info_x + Spacing.SM, info_y, FontSize.XS, Colors.TEXT_GRAY)
                    info_y += 18

                if hasattr(acc, "attack_speed_pct") and acc.attack_speed_pct:
                    effect = f"  攻速 +{acc.attack_speed_pct * lv}%"
                    draw_text(screen, effect, info_x + Spacing.SM, info_y, FontSize.XS, Colors.TEXT_GRAY)
                    info_y += 18

                info_y += 5
        else:
            draw_text(screen, "无饰品", info_x + Spacing.SM, info_y, FontSize.SM, Colors.TEXT_DARK)
            info_y += 25

    def _draw_section(self, screen, title, x, y):
        """绘制章节标题"""
        draw_text(screen, title, x, y, FontSize.LG, Colors.TEXT_GOLD)
        # 下划线
        pygame.draw.line(screen, Colors.BORDER_GOLD, (x, y + 22), (x + 200, y + 22), 1)

    def _draw_stat(self, screen, label, value, x, y, color=Colors.TEXT_LIGHT):
        """绘制属性行"""
        draw_text(screen, f"{label}:", x + Spacing.SM, y, FontSize.SM, Colors.TEXT_GRAY)
        draw_text(screen, value, x + 100, y, FontSize.SM, color)
        return y + 22
