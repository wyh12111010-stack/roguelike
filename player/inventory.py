"""
玩家装备/背包组件 - 从 player.py 提取
负责灵根、法宝、饰品、永久加成、侵蚀效果。
"""


class PlayerInventory:
    """装备/背包相关方法 mixin"""

    def set_linggen(self, linggen):
        self.linggen = linggen

    def set_fabao(self, fabao):
        """兼容旧逻辑：单法宝时当作 [fabao]"""
        self.fabao_list = [fabao] if fabao else []
        self.current_fabao_index = 0
        self._gongfa = None

    def set_fabao_pair(self, primary, secondary):
        """设置双法宝"""
        self.fabao_list = [primary, secondary] if primary and secondary else ([primary] if primary else [])
        self.current_fabao_index = 0

    def switch_fabao(self):
        """Q 键切换法宝"""
        if len(self.fabao_list) < 2:
            return
        self.current_fabao_index = 1 - self.current_fabao_index

    def add_accessory(self, acc, level=1):
        """装备饰品，应用生命/灵力上限。acc 为 Accessory 实例"""
        self.accessories.append((acc, level))
        self.max_health += (getattr(acc, "health_bonus", 0) or 0) * level
        self.max_health = max(1, self.max_health)
        self.health = min(self.max_health, self.health + (getattr(acc, "health_bonus", 0) or 0) * level)
        self.max_mana += (getattr(acc, "mana_bonus", 0) or 0) * level
        self.max_mana = max(1, self.max_mana)
        self.mana = min(self.max_mana, self.mana + (getattr(acc, "mana_bonus", 0) or 0) * level)
        return True

    def upgrade_accessory(self, index):
        """升级已装备饰品，返回是否成功"""
        if index < 0 or index >= len(self.accessories):
            return False
        acc, lv = self.accessories[index]
        if lv >= acc.max_level:
            return False
        self.accessories[index] = (acc, lv + 1)
        self.max_health += getattr(acc, "health_bonus", 0) or 0
        self.max_health = max(1, self.max_health)
        self.health = min(self.max_health, self.health + (getattr(acc, "health_bonus", 0) or 0))
        self.max_mana += getattr(acc, "mana_bonus", 0) or 0
        self.max_mana = max(1, self.max_mana)
        self.mana = min(self.max_mana, self.mana + (getattr(acc, "mana_bonus", 0) or 0))
        return True

    def apply_meta_bonuses(self):
        """应用局外永久加成（碧落处购买的属性加成）"""
        from meta import meta

        self.max_health += meta.base_health_bonus
        self.health += meta.base_health_bonus
        self.max_mana += meta.base_mana_bonus
        self.mana += meta.base_mana_bonus

    def apply_erosion_effects(self):
        """应用侵蚀度效果（属性修正）"""
        from erosion_system import ErosionSystem

        erosion = ErosionSystem()
        erosion.erosion_level = getattr(self, "erosion_level", 0)
        modifiers = erosion.get_stat_modifiers()
        for stat, change in modifiers.items():
            if stat == "max_hp":
                self.max_health = max(1, self.max_health + int(change))
                self.health = min(self.max_health, self.health)
            elif stat == "speed":
                self.speed = max(50, self.speed + int(change))
