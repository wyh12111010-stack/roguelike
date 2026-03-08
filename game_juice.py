"""
game_juice - 打击感/反馈系统接线层
将已有但未接入的系统（屏幕震动、伤害飘字、增强粒子、帧冻结）
通过 EventBus 统一接入，无需散布到各个模块中。

初始化：在 game.py __init__ 中调用 init_juice(game)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# ─── Hitstop (帧冻结) ───


class Hitstop:
    """帧冻结系统：命中时短暂暂停游戏逻辑，增强打击感。"""

    def __init__(self):
        self._freeze_remaining: float = 0.0

    def freeze(self, duration: float = 0.04) -> None:
        """触发帧冻结。duration 秒内 update 返回 True 表示应跳过逻辑。"""
        self._freeze_remaining = max(self._freeze_remaining, duration)

    def update(self, dt: float) -> bool:
        """返回 True 表示当前帧被冻结，应跳过游戏逻辑更新。"""
        if self._freeze_remaining > 0:
            self._freeze_remaining -= dt
            return True
        return False

    @property
    def active(self) -> bool:
        return self._freeze_remaining > 0


# ─── Juice Wiring ───


def init_juice(game) -> None:
    """将所有打击感系统挂到 EventBus 上。game.py __init__ 调用一次。"""
    from core import EventBus
    from core.events import ENEMY_KILLED, LEVEL_CLEAR, PLAYER_DEATH, PLAYER_HIT

    # 帧冻结实例
    game.hitstop = Hitstop()

    # ── 玩家受击反馈 ──
    def _on_player_hit_juice(damage=0, **_kw):
        player = getattr(game, "player", None)
        if not player:
            return
        cx, cy = player.rect.centerx, player.rect.centery

        # 屏幕震动
        if hasattr(game, "screen_shake"):
            intensity = min(20, 5 + damage // 5)
            game.screen_shake.add_shake(duration=0.15, intensity=intensity)

        # 伤害飘字
        if hasattr(game, "damage_text_mgr") and hasattr(game.damage_text_mgr, "add_damage"):
            game.damage_text_mgr.add_damage(cx, cy - 20, damage)

        # 帧冻结
        game.hitstop.freeze(0.05)

        # 受击音效
        try:
            from fx_audio import play_hit_sfx

            play_hit_sfx()
        except Exception:
            pass

    EventBus.on(PLAYER_HIT, _on_player_hit_juice)

    # ── 敌人被击杀反馈 ──
    def _on_enemy_killed_juice(enemy_type="", **_kw):
        # 增强粒子
        _try_kill_particles(game)

        # 轻微屏幕震动
        if hasattr(game, "screen_shake"):
            game.screen_shake.add_shake(duration=0.08, intensity=4)

        # 短帧冻结
        game.hitstop.freeze(0.03)

        # 击杀音效
        try:
            from fx_audio import play_kill_sfx

            play_kill_sfx()
        except Exception:
            pass

    EventBus.on(ENEMY_KILLED, _on_enemy_killed_juice)

    # ── 关卡通关反馈 ──
    def _on_level_clear_juice(**_kw):
        # 升级粒子
        player = getattr(game, "player", None)
        if player:
            try:
                from enhanced_particles import create_levelup_particles

                create_levelup_particles(player.rect.centerx, player.rect.centery)
            except Exception:
                pass

        # 中度屏幕震动
        if hasattr(game, "screen_shake"):
            game.screen_shake.add_shake(duration=0.25, intensity=12)

        # 过关音效
        try:
            from fx_audio import play_levelup_sfx

            play_levelup_sfx()
        except Exception:
            pass

    EventBus.on(LEVEL_CLEAR, _on_level_clear_juice)

    # ── 玩家死亡反馈 ──
    def _on_player_death_juice(**_kw):
        # 强烈屏幕震动
        if hasattr(game, "screen_shake"):
            game.screen_shake.add_shake(duration=0.4, intensity=25)

        # 长帧冻结
        game.hitstop.freeze(0.12)

        # 死亡音效
        try:
            from fx_audio import play_death_sfx

            play_death_sfx()
        except Exception:
            pass

    EventBus.on(PLAYER_DEATH, _on_player_death_juice)


def _try_kill_particles(game):
    """安全触发击杀粒子"""
    try:
        from enhanced_particles import create_kill_particles

        player = getattr(game, "player", None)
        if player:
            create_kill_particles(player.rect.centerx, player.rect.centery, (255, 100, 100))
    except Exception:
        pass


def wire_enemy_damage_text(game) -> None:
    """Monkey-patch enemy.take_damage 来触发伤害飘字和暴击粒子。
    在 game._load_level / _load_boss 之后调用。
    """
    if not hasattr(game, "damage_text_mgr"):
        return
    mgr = game.damage_text_mgr
    if not hasattr(mgr, "add_damage"):
        return

    from enemies.base import Enemy

    _original_take_damage = Enemy.take_damage

    def _patched_take_damage(self, amount, attacker_attr=None, enemies=None, self_reaction=None):
        was_alive = not self.dead and self.health > 0
        _original_take_damage(self, amount, attacker_attr, enemies=enemies, self_reaction=self_reaction)

        if was_alive and amount > 0:
            cx, cy = self.rect.centerx, self.rect.centery
            is_crit = amount > 30  # 简易暴击判定：高伤害视为暴击
            mgr.add_damage(cx, cy - 10, amount, is_crit=is_crit)

            if is_crit:
                try:
                    from enhanced_particles import create_crit_particles

                    create_crit_particles(cx, cy)
                except Exception:
                    pass

    Enemy.take_damage = _patched_take_damage


def apply_screen_shake_to_draw(screen, game) -> tuple:
    """在 draw_combat 开头调用，返回 (offset_x, offset_y) 偏移量。
    调用方负责 translate 绘制坐标。
    """
    if hasattr(game, "screen_shake") and game.screen_shake.is_shaking():
        return game.screen_shake.get_offset()
    return (0, 0)
