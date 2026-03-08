"""
战斗日志 UI - 订阅事件，显示浮动消息
"""

import pygame

from config import get_font
from core import EventBus
from core.events import (
    COMBAT_START,
    ENEMY_KILLED,
    LEVEL_CLEAR,
    PLAYER_DEATH,
    PLAYER_HIT,
    SHOP_ENTER,
    VICTORY,
)
from enemy import TYPE_LABELS


class CombatLogUI:
    """战斗日志：订阅事件，显示近期消息，自动淡出"""

    MAX_ENTRIES = 6
    ENTRY_DURATION = 2.5  # 秒
    FADE_START = 1.5  # 秒后开始淡出

    def __init__(self):
        self.entries = []  # [(text, color, age), ...]
        self._subscribed = False

    def _subscribe(self):
        if self._subscribed:
            return
        self._subscribed = True
        EventBus.on(COMBAT_START, self._on_combat_start)
        EventBus.on(ENEMY_KILLED, self._on_enemy_killed)
        EventBus.on(PLAYER_HIT, self._on_player_hit)
        EventBus.on(PLAYER_DEATH, self._on_player_death)
        EventBus.on(LEVEL_CLEAR, self._on_level_clear)
        EventBus.on(VICTORY, self._on_victory)
        EventBus.on(SHOP_ENTER, self._on_shop_enter)

    def _add(self, text: str, color=(220, 220, 220)):
        self.entries.append({"text": text, "color": color, "age": 0.0})
        if len(self.entries) > self.MAX_ENTRIES:
            self.entries.pop(0)

    def clear(self):
        """清空日志（新局开始时调用）"""
        self.entries.clear()

    def _on_combat_start(self, **kwargs):
        self._add("进入战斗", (150, 200, 255))

    def _on_enemy_killed(self, enemy_type="", **kwargs):
        label = TYPE_LABELS.get(enemy_type, enemy_type or "敌人")
        self._add(f"击杀 {label}", (100, 255, 150))

    def _on_player_hit(self, damage=0, **kwargs):
        self._add(f"受到 {damage} 点伤害", (255, 120, 100))

    def _on_player_death(self, kill_count=0, **kwargs):
        self._add(f"身陨 · 击杀 {kill_count}", (255, 80, 80))

    def _on_level_clear(self, lingshi=0, daoyun=0, reward_type="lingshi", **kwargs):
        parts = []
        if lingshi:
            parts.append(f"+{lingshi} 灵石")
        if daoyun:
            parts.append(f"+{daoyun} 道韵")
        if reward_type == "fabao":
            parts.append("获得法宝")
        elif reward_type == "accessory":
            parts.append("获得饰品")
        if parts:
            self._add("关卡完成 " + " ".join(parts), (180, 220, 150))

    def _on_victory(self, **kwargs):
        self._add("凯旋！", (100, 255, 100))

    def _on_shop_enter(self, **kwargs):
        self._add("进入商店", (200, 180, 120))

    def update(self, dt: float):
        self._subscribe()
        for e in self.entries[:]:
            e["age"] += dt
            if e["age"] >= self.ENTRY_DURATION:
                self.entries.remove(e)

    def draw(self, screen: pygame.Surface):
        if not self.entries:
            return
        font = get_font(18)
        x, y = 10, 200
        line_h = 22
        for e in self.entries:
            alpha = 255
            if e["age"] > self.FADE_START:
                alpha = int(255 * (1 - (e["age"] - self.FADE_START) / (self.ENTRY_DURATION - self.FADE_START)))
            color = tuple(min(255, max(0, c * alpha // 255)) for c in e["color"][:3])
            txt = font.render(e["text"], True, color)
            screen.blit(txt, (x, y))
            y += line_h
