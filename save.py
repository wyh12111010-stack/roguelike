"""
存档系统 - 局外 + 局内存档
- 局外 (meta): 道韵、解锁、总场次等，跨局保留
- 局内 (run): 当前局进度，退出可续玩
"""
import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, Any

from meta import MetaData, meta

SAVE_PATH = "save.json"
RUN_SAVE_PATH = "run_save.json"
RUN_SAVE_VERSION = 1


def get_save_path() -> str:
    """获取局外存档路径"""
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, SAVE_PATH)


def get_run_save_path() -> str:
    """获取局内存档路径"""
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, RUN_SAVE_PATH)


# ---------- 局外存档 ----------

def load() -> MetaData:
    """加载局外存档"""
    path = get_save_path()
    if not os.path.exists(path):
        return MetaData()
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        return MetaData.from_dict(d)
    except Exception:
        return MetaData()


def save(data: MetaData) -> bool:
    """保存局外存档"""
    path = get_save_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data.to_dict(), f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def init_meta():
    """初始化全局 meta（游戏启动时调用）"""
    global meta
    meta = load()


def persist_meta():
    """持久化当前 meta（通关/死亡时调用）"""
    save(meta)


# ---------- 局内存档 ----------

@dataclass
class PlayerSaveData:
    """玩家可序列化状态"""
    x: int
    y: int
    health: int
    max_health: int
    mana: int
    max_mana: int
    lingshi: int
    linggen_id: str
    fabao_id: str
    accessories: List[tuple] = field(default_factory=list)  # [(id, level), ...]
    fabao_damage_pct: int = 0
    fabao_speed_pct: int = 0
    fabao_ids: List[str] = field(default_factory=list)  # [主法宝id, 副法宝id]
    current_fabao_index: int = 0
    partner_id: Optional[str] = None
    partner_bond_level: int = 0
    partner_charge: float = 0

    def to_dict(self) -> dict:
        acc = getattr(self, "accessories", [])
        acc_ser = [[a[0], a[1]] for a in acc]
        d = {
            "x": self.x, "y": self.y,
            "health": self.health, "max_health": self.max_health,
            "mana": self.mana, "max_mana": self.max_mana,
            "lingshi": self.lingshi,
            "linggen_id": self.linggen_id, "fabao_id": self.fabao_id,
            "accessories": acc_ser,
            "fabao_damage_pct": getattr(self, "fabao_damage_pct", 0),
            "fabao_speed_pct": getattr(self, "fabao_speed_pct", 0),
        }
        if getattr(self, "fabao_ids", []):
            d["fabao_ids"] = self.fabao_ids
            d["current_fabao_index"] = getattr(self, "current_fabao_index", 0)
        if getattr(self, "partner_id", None):
            d["partner_id"] = self.partner_id
            d["partner_bond_level"] = getattr(self, "partner_bond_level", 0)
            d["partner_charge"] = getattr(self, "partner_charge", 0)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "PlayerSaveData":
        acc_raw = d.get("accessories", [])
        acc = [(a[0], a[1]) if isinstance(a, (list, tuple)) else (a.get("id", ""), a.get("level", 1)) for a in acc_raw]
        return cls(
            x=d.get("x", 0), y=d.get("y", 0),
            health=d.get("health", 100), max_health=d.get("max_health", 100),
            mana=d.get("mana", 100), max_mana=d.get("max_mana", 100),
            lingshi=d.get("lingshi", 0),
            linggen_id=d.get("linggen_id", "fire"), fabao_id=d.get("fabao_id", "sword"),
            accessories=acc,
            fabao_damage_pct=d.get("fabao_damage_pct", 0),
            fabao_speed_pct=d.get("fabao_speed_pct", 0),
            fabao_ids=d.get("fabao_ids", []),
            current_fabao_index=d.get("current_fabao_index", 0),
            partner_id=d.get("partner_id"),
            partner_bond_level=d.get("partner_bond_level", 0),
            partner_charge=d.get("partner_charge", 0),
        )


@dataclass
class RunSaveData:
    """局内存档：村子 / 战斗（路线选择/商店）"""
    version: int = RUN_SAVE_VERSION
    scene: str = "village"  # village | combat

    # 村子状态
    linggen_choice: int = 0
    fabao_choice: int = 0
    fabao_id: str = ""  # 选中的法宝 id，用于加载时还原
    village_player_x: int = -1  # 村子内玩家位置，-1 表示未保存
    village_player_y: int = -1

    # 战斗状态（仅 scene=combat 时有效）
    player: Optional[PlayerSaveData] = None
    current_level: int = 0
    kill_count: int = 0
    demo_mode: bool = False
    demo_level: int = 0
    in_shop: bool = False
    route_options: List[Any] = field(default_factory=list)
    run_potions: int = 0  # 局内丹药数量（从 meta.potion_stock 带入，局结束归入存量）
    # 商店状态（局内）
    shop_daoyun_bought: bool = False
    shop_fabao_id: Optional[str] = None
    shop_refresh_remaining: int = 1
    shop_shown_fabao_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {
            "version": self.version,
            "scene": self.scene,
            "linggen_choice": self.linggen_choice,
            "fabao_choice": getattr(self, "fabao_choice", 0),
            "fabao_id": getattr(self, "fabao_id", ""),
            "village_player_x": getattr(self, "village_player_x", -1),
            "village_player_y": getattr(self, "village_player_y", -1),
        }
        if self.scene == "combat" and self.player:
            d["combat"] = {
                "player": self.player.to_dict(),
                "current_level": self.current_level,
                "kill_count": self.kill_count,
                "demo_mode": self.demo_mode,
                "demo_level": self.demo_level,
                "in_shop": self.in_shop,
                "route_options": self.route_options,
                "run_potions": getattr(self, "run_potions", 0),
                "shop_daoyun_bought": getattr(self, "shop_daoyun_bought", False),
                "shop_fabao_id": getattr(self, "shop_fabao_id"),
                "shop_refresh_remaining": getattr(self, "shop_refresh_remaining", 1),
                "shop_shown_fabao_ids": getattr(self, "shop_shown_fabao_ids", []),
            }
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RunSaveData":
        obj = cls(
            version=d.get("version", 1),
            scene=d.get("scene", "village"),
            linggen_choice=d.get("linggen_choice", 0),
            fabao_choice=d.get("fabao_choice", 0),
            fabao_id=d.get("fabao_id") or (d.get("fabao_ids", [])[0] if d.get("fabao_ids") else ""),
            village_player_x=d.get("village_player_x", -1),
            village_player_y=d.get("village_player_y", -1),
        )
        combat = d.get("combat", {})
        if combat:
            obj.player = PlayerSaveData.from_dict(combat.get("player", {}))
            obj.current_level = combat.get("current_level", 0)
            obj.kill_count = combat.get("kill_count", 0)
            obj.demo_mode = combat.get("demo_mode", False)
            obj.demo_level = combat.get("demo_level", 0)
            obj.in_shop = combat.get("in_shop", False)
            obj.route_options = combat.get("route_options", [])
            obj.run_potions = combat.get("run_potions", 0)
            obj.shop_daoyun_bought = combat.get("shop_daoyun_bought", False)
            obj.shop_fabao_id = combat.get("shop_fabao_id")
            obj.shop_refresh_remaining = combat.get("shop_refresh_remaining", 1)
            obj.shop_shown_fabao_ids = combat.get("shop_shown_fabao_ids", [])
        return obj


def has_run_save() -> bool:
    """是否存在局内存档"""
    return os.path.exists(get_run_save_path())


def load_run() -> Optional[RunSaveData]:
    """加载局内存档，失败返回 None"""
    path = get_run_save_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        return RunSaveData.from_dict(d)
    except Exception:
        return None


def save_run(data: RunSaveData) -> bool:
    """保存局内存档"""
    path = get_run_save_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data.to_dict(), f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def clear_run_save():
    """清除局内存档（新游戏 / 通关 / 死亡）"""
    path = get_run_save_path()
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass
