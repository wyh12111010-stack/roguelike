"""
商店管理器 - 从 game.py 提取
负责商店状态管理、商品生成、购买逻辑。
"""

from meta import meta
from save import persist_meta


class ShopManager:
    """局内商店状态与交易逻辑"""

    def __init__(self):
        self.reset()

    def reset(self):
        """重置商店状态（新局开始时调用）"""
        self.daoyun_bought = False
        self.fabao_id = None
        self.refresh_remaining = getattr(meta, "shop_refresh_count", 1)
        self.shown_fabao_ids = []

    def ensure_state(self):
        """进入商店时确保商品已生成"""
        if self.fabao_id is not None:
            return
        from shop import gen_shop_fabao

        fb = gen_shop_fabao(meta.unlocked_fabao, [])
        if fb:
            self.fabao_id = fb.id
            self.shown_fabao_ids = [fb.id]
        else:
            self.fabao_id = None
            self.shown_fabao_ids = []

    def refresh(self):
        """商店刷新：重新随机法宝，排除已出现过的"""
        from shop import gen_shop_fabao

        shown = set(self.shown_fabao_ids)
        fb = gen_shop_fabao(meta.unlocked_fabao, list(shown))
        if fb:
            self.fabao_id = fb.id
            self.shown_fabao_ids = [*list(shown), fb.id]
        else:
            self.fabao_id = None

    def buy_item(self, item_type, item_id, cost, player, stats_tracker=None):
        """商店购买逻辑，返回 True 表示购买成功"""
        if player.lingshi < cost:
            return False

        # 前置校验
        if item_type == "fabao_buy":
            have_ids = {f.id for f in getattr(player, "fabao_list", [])}
            if item_id in have_ids or len(have_ids) >= 2:
                return False

        if item_type == "daoyun_fragment" and self.daoyun_bought:
            return False

        if item_type == "refresh" and self.refresh_remaining <= 0:
            return False

        if item_type == "accessory":
            from shop import _has_accessory

            if _has_accessory(player, item_id):
                return False
            if len(player.accessories) >= getattr(meta, "accessory_slots", 6):
                return False

        if item_type == "upgrade":
            idx = item_id
            if idx < 0 or idx >= len(player.accessories):
                return False
            acc, lv = player.accessories[idx]
            if lv >= acc.max_level:
                return False

        if item_type == "fabao":
            _fid, etype, val = item_id
            from shop import get_fabao_upgrade_offer

            offer = get_fabao_upgrade_offer(player, etype)
            if offer is None:
                return False
            if int(cost) != int(offer["cost"]) or int(val) != int(offer["step"]):
                return False

        # 扣费
        player.lingshi -= cost
        if stats_tracker:
            stats_tracker.on_shop_purchase()

        # 执行购买效果
        if item_type == "fabao_buy":
            from fabao import FABAO_LIST

            fb = next((f for f in FABAO_LIST if f.id == item_id), None)
            if fb:
                if player.fabao:
                    player.set_fabao_pair(player.fabao, fb)
                else:
                    player.set_fabao(fb)
            self.fabao_id = None

        elif item_type == "daoyun_fragment":
            meta.daoyun += 1
            persist_meta()
            self.daoyun_bought = True

        elif item_type == "refresh":
            self.refresh_remaining -= 1
            self.refresh()

        elif item_type == "fabao":
            fid, etype, val = item_id
            if etype == "damage_pct":
                player.fabao_damage_pct = min(50, player.fabao_damage_pct + val)
            elif etype == "speed_pct":
                player.fabao_speed_pct = min(25, player.fabao_speed_pct + val)

        elif item_type == "accessory":
            from accessory import get_accessory

            acc = get_accessory(item_id)
            if acc:
                player.add_accessory(acc, 1)

        elif item_type == "upgrade":
            player.upgrade_accessory(item_id)

        # 贫瘠之核触发
        from accessory_effects import trigger_barren_moderate

        trigger_barren_moderate(player)

        return True

    def to_save_data(self):
        """返回存档所需的商店状态"""
        return {
            "daoyun_bought": self.daoyun_bought,
            "fabao_id": self.fabao_id,
            "refresh_remaining": self.refresh_remaining,
            "shown_fabao_ids": list(self.shown_fabao_ids),
        }

    def from_save_data(self, data):
        """从存档恢复商店状态"""
        self.daoyun_bought = data.get("daoyun_bought", False)
        self.fabao_id = data.get("fabao_id", None)
        self.refresh_remaining = data.get("refresh_remaining", 1)
        self.shown_fabao_ids = list(data.get("shown_fabao_ids", []))
