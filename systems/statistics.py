"""
局内战斗统计追踪器 - 从 game.py 提取
负责追踪连击、伤害、元素反应、经济、装备等局内统计数据，
供成就系统和胜利结算使用。
"""


class StatisticsTracker:
    """局内战斗统计"""

    def __init__(self):
        self.reset()

    def reset(self):
        """重置所有统计（新局开始时调用）"""
        import time

        self.combat_start_time = time.time()

        # 连击
        self.max_combo = 0
        self.current_combo = 0
        self.combo_timer = 0.0

        # 伤害
        self.total_damage = 0
        self.max_single_damage = 0

        # 元素反应
        self.total_reactions = 0
        self.vaporize_count = 0
        self.melt_count = 0
        self.overload_count = 0

        # 经济
        self.max_lingshi = 0
        self.shop_purchases = 0

        # 丹药
        self.potions_used = 0

        # 装备
        self.max_accessories = 0
        self.max_accessory_level = 0

        # 生存
        self.low_health_survival_time = 0.0

        # Boss
        self.boss_defeated_flags = {
            "boss_1": False,
            "boss_2": False,
            "boss_3": False,
            "final_boss": False,
        }

    def on_enemy_killed(self, enemy=None):
        """敌人被击杀时更新连击统计"""
        self.current_combo += 1
        self.combo_timer = 2.0  # 2秒内不击杀则连击清零
        if self.current_combo > self.max_combo:
            self.max_combo = self.current_combo

    def on_damage_dealt(self, damage=0):
        """造成伤害时更新统计"""
        self.total_damage += damage
        if damage > self.max_single_damage:
            self.max_single_damage = damage

    def on_reaction_triggered(self, reaction_type=""):
        """触发元素反应时更新统计"""
        self.total_reactions += 1
        if reaction_type == "vaporize":
            self.vaporize_count += 1
        elif reaction_type == "melt":
            self.melt_count += 1
        elif reaction_type == "overload":
            self.overload_count += 1

    def on_shop_purchase(self):
        """购买时更新计数"""
        self.shop_purchases += 1

    def update(self, dt, player):
        """每帧更新统计（连击计时、灵石、饰品、低血生存）"""
        # 连击计时器
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.current_combo = 0

        if player is None:
            return

        # 最大灵石
        if player.lingshi > self.max_lingshi:
            self.max_lingshi = player.lingshi

        # 最大饰品数
        acc_count = len(getattr(player, "accessories", []))
        if acc_count > self.max_accessories:
            self.max_accessories = acc_count

        # 最大饰品等级
        for _acc, lv in getattr(player, "accessories", []):
            if lv > self.max_accessory_level:
                self.max_accessory_level = lv

        # 低血生存时间
        if player.health > 0 and player.health < 10:
            self.low_health_survival_time += dt

    def get_clear_time(self):
        """获取通关用时（秒）"""
        import time

        return int(time.time() - self.combat_start_time) if self.combat_start_time > 0 else 0

    def collect_stats(self, player, meta, max_attack_speed_pct=0, resonance_intensity=0, active_pacts=None):
        """收集全部统计数据，用于胜利结算和成就检查"""
        stats = {
            # 战斗统计
            "max_attack_speed": max_attack_speed_pct,
            "max_combo": self.max_combo,
            "total_damage": self.total_damage,
            "max_single_damage": self.max_single_damage,
            "kill_count": getattr(self, "_kill_count", 0),
            # 元素反应统计
            "total_reactions": self.total_reactions,
            "vaporize_count": self.vaporize_count,
            "melt_count": self.melt_count,
            "overload_count": self.overload_count,
            # 经济统计
            "max_lingshi": self.max_lingshi,
            "shop_purchases": self.shop_purchases,
            # 装备统计
            "max_accessories": self.max_accessories,
            "max_accessory_level": self.max_accessory_level,
            # 挑战统计
            "clear_time": self.get_clear_time(),
            "potions_used": self.potions_used,
            "low_health_survival": int(self.low_health_survival_time),
            "final_health": player.health if player else 0,
            # Boss 击败标记
            "boss_1_defeated": self.boss_defeated_flags.get("boss_1", False),
            "boss_2_defeated": self.boss_defeated_flags.get("boss_2", False),
            "boss_3_defeated": self.boss_defeated_flags.get("boss_3", False),
            "final_boss_defeated": self.boss_defeated_flags.get("final_boss", False),
            # 流派
            "linggen": player.linggen.id if player and player.linggen else "",
            "victory": True,
            # 共鸣统计
            "resonance_intensity": resonance_intensity,
            "active_pacts": active_pacts or [],
            # 局外统计
            "total_wins": meta.total_wins,
            "total_kills": meta.total_kills,
            "total_daoyun": meta.daoyun,
            "linggen_unlocked": len(meta.unlocked_linggen),
            "fabao_unlocked": len(meta.unlocked_fabao),
            "partners_healed": len([pid for pid, lv in meta.partner_bond_levels.items() if lv >= 1]),
        }
        return stats
