"""
局外数据 - 跨局保留的解锁与成长
轮回中保留：道韵、已解锁灵根、已解锁法宝
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from controls import default_keybinds, merge_keybinds


def _parse_partner_bond_levels(d: dict) -> dict:
    """解析伙伴羁绊，兼容旧存档 unlocked_partners"""
    levels = d.get("partner_bond_levels", {})
    if levels:
        return levels
    # 旧存档：unlocked_partners 列表转羁绊 1
    old = d.get("unlocked_partners", [])
    return {pid: 1 for pid in old} if isinstance(old, list) else {}


@dataclass
class MetaData:
    """局外存档结构"""
    # 局外货币（道韵）- 用于解锁灵根、部分法宝
    daoyun: int = 0
    
    # 解锁
    unlocked_linggen: List[str] = field(default_factory=lambda: ["fire"])
    unlocked_fabao: List[str] = field(default_factory=lambda: ["sword", "needle"])
    unlocked_accessories: List[str] = field(default_factory=lambda: ["dmg_s", "mp", "glass_core", "swift_debt"])  # 局外饰品池（默认开放）
    unlocked_routes: List[int] = field(default_factory=lambda: [0, 1, 2, 3])
    
    # 永久加成（碧落处道韵购买）
    base_health_bonus: int = 0
    base_mana_bonus: int = 0

    # 局外成长（铸心处道韵购买）
    accessory_slots: int = 6       # 饰品槽位上限，默认 6，可扩至 9
    shop_refresh_count: int = 1    # 每局商店刷新次数，默认 1，可扩至 3
    start_accessory_mode: int = 0  # 开局饰品：0=无 1=随机1个 2=二选一 3=三选一
    boss_cue_mode: int = 1         # Boss 提示音：0=关 1=标准 2=强化
    master_volume: float = 1.0     # 全局音量：0.0 ~ 1.0
    bgm_volume: float = 0.8        # 背景音乐音量：0.0 ~ 1.0
    sfx_volume: float = 1.0        # 音效音量：0.0 ~ 1.0
    resolution_index: int = 0      # 分辨率档位索引（见 config.RESOLUTION_PRESETS）
    fullscreen: bool = False       # 全屏开关
    pause_on_focus_lost: bool = True   # 窗口失焦自动暂停
    autosave_on_exit: bool = True      # 退出游戏自动保存局内进度
    keybinds: dict = field(default_factory=default_keybinds)  # 可配置按键映射

    # 丹药（局外存储，存量上限由局外成长决定）
    potion_stock: int = 1      # 当前存量
    potion_cap: int = 1        # 存量上限 1→2→3→4，碧落处道韵解锁
    
    # 进度
    total_runs: int = 0
    total_wins: int = 0

    # 伙伴治疗条件（累计局内数据，跨局累加）
    total_kills: int = 0           # 累计击杀
    total_levels_cleared: int = 0  # 累计过关
    total_element_damage: int = 0   # 元素伤害累计
    total_deaths: int = 0          # 身陨次数

    # 伙伴羁绊等级（治疗解锁+多次治疗升级，1-3 级）
    partner_bond_levels: dict = field(default_factory=dict)  # {partner_id: 1|2|3}
    # 手动选择的伙伴（村子内选带谁，只带 1 个）
    selected_partner_id: Optional[str] = None  # None 时沿用羁绊最高
    # 成就（栖霞处查看）
    achievements: set = field(default_factory=set)  # 已解锁成就 id 集合
    
    # 渐进式解锁（根据通关次数解锁功能）
    unlocked_features: set = field(default_factory=lambda: {"linggen_select", "fabao_select", "partner_heal"})
    erosion_level: int = 0  # 当前侵蚀度（玩家自主选择）
    
    def check_unlock_features(self):
        """根据通关次数解锁功能"""
        wins = self.total_wins
        
        # 第 1 次通关：解锁铸心坊（饰品解锁）
        if wins >= 1:
            self.unlocked_features.add("accessory_unlock")
        
        # 第 2 次通关：解锁碧落丹阁（局外成长）
        if wins >= 2:
            self.unlocked_features.add("meta_growth")
        
        # 第 3 次通关：解锁侵蚀度系统
        if wins >= 3:
            self.unlocked_features.add("erosion_system")
        
        # 第 5 次通关：解锁劫难印记系统
        if wins >= 5:
            self.unlocked_features.add("calamity_seal")
    
    def on_win(self, daoyun_earned: int, stats: dict):
        """通关时调用：增加道韵、检查成就、解锁功能"""
        self.total_wins += 1
        self.daoyun += daoyun_earned
        
        # 检查成就
        from achievement import check_achievements
        new_achievements = check_achievements(stats, self.achievements)
        for ach_id in new_achievements:
            self.achievements.add(ach_id)
        
        # 解锁功能
        self.check_unlock_features()
        
        return new_achievements

    def to_dict(self):
        return {
            "daoyun": self.daoyun,
            "unlocked_linggen": self.unlocked_linggen,
            "unlocked_fabao": self.unlocked_fabao,
            "unlocked_accessories": self.unlocked_accessories,
            "unlocked_routes": self.unlocked_routes,
            "base_health_bonus": self.base_health_bonus,
            "base_mana_bonus": self.base_mana_bonus,
            "accessory_slots": self.accessory_slots,
            "shop_refresh_count": self.shop_refresh_count,
            "start_accessory_mode": self.start_accessory_mode,
            "boss_cue_mode": self.boss_cue_mode,
            "master_volume": self.master_volume,
            "bgm_volume": self.bgm_volume,
            "sfx_volume": self.sfx_volume,
            "resolution_index": self.resolution_index,
            "fullscreen": self.fullscreen,
            "pause_on_focus_lost": self.pause_on_focus_lost,
            "autosave_on_exit": self.autosave_on_exit,
            "keybinds": self.keybinds,
            "potion_stock": self.potion_stock,
            "potion_cap": self.potion_cap,
            "total_runs": self.total_runs,
            "total_wins": self.total_wins,
            "total_kills": self.total_kills,
            "total_levels_cleared": self.total_levels_cleared,
            "total_element_damage": self.total_element_damage,
            "total_deaths": self.total_deaths,
            "partner_bond_levels": self.partner_bond_levels,
            "selected_partner_id": self.selected_partner_id,
            "achievements": list(self.achievements),
            "unlocked_features": list(self.unlocked_features),
            "erosion_level": self.erosion_level,
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> "MetaData":
        return cls(
            daoyun=d.get("daoyun", 0),
            unlocked_linggen=d.get("unlocked_linggen", ["fire"]),
            unlocked_fabao=d.get("unlocked_fabao", ["sword", "needle"]),
            unlocked_accessories=d.get("unlocked_accessories", ["dmg_s", "mp", "glass_core", "swift_debt"]),
            unlocked_routes=d.get("unlocked_routes", [0, 1, 2, 3]),
            base_health_bonus=d.get("base_health_bonus", 0),
            base_mana_bonus=d.get("base_mana_bonus", 0),
            accessory_slots=d.get("accessory_slots", 6),
            shop_refresh_count=d.get("shop_refresh_count", 1),
            start_accessory_mode=d.get("start_accessory_mode", 0),
            boss_cue_mode=max(0, min(2, d.get("boss_cue_mode", 1))),
            master_volume=max(0.0, min(1.0, float(d.get("master_volume", 1.0)))),
            bgm_volume=max(0.0, min(1.0, float(d.get("bgm_volume", 0.8)))),
            sfx_volume=max(0.0, min(1.0, float(d.get("sfx_volume", 1.0)))),
            resolution_index=max(0, int(d.get("resolution_index", 0))),
            fullscreen=bool(d.get("fullscreen", False)),
            pause_on_focus_lost=bool(d.get("pause_on_focus_lost", True)),
            autosave_on_exit=bool(d.get("autosave_on_exit", True)),
            keybinds=merge_keybinds(d.get("keybinds", {})),
            potion_cap=min(d.get("potion_cap", 1), 4),
            potion_stock=min(d.get("potion_stock", 1), min(d.get("potion_cap", 1), 4)),
            total_runs=d.get("total_runs", 0),
            total_wins=d.get("total_wins", 0),
            total_kills=d.get("total_kills", 0),
            total_levels_cleared=d.get("total_levels_cleared", 0),
            total_element_damage=d.get("total_element_damage", 0),
            total_deaths=d.get("total_deaths", 0),
            partner_bond_levels=_parse_partner_bond_levels(d),
            selected_partner_id=d.get("selected_partner_id"),
            achievements=set(d.get("achievements", [])),
            unlocked_features=set(d.get("unlocked_features", {"linggen_select", "fabao_select", "partner_heal"})),
            erosion_level=d.get("erosion_level", 0),
        )


# 全局局外数据（由 save 模块加载）
meta: MetaData = MetaData()
