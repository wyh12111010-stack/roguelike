# 解锁系统重新设计（具体方案）

> 基于现有代码，给出可直接实现的方案

---

## 一、当前问题

### 1.1 道韵价格问题

```python
# 当前价格（unlock.py）
LINGGEN_COST = {
    "fire": 0, "water": 15, "wood": 15,
    "metal": 18, "earth": 20, "none": 25,
}

FABAO_COST = {
    "sword": 0, "spell": 15, "staff": 18,
    "blade": 20, "stone": 22, "needle": 24, "cauldron": 26,
}

ACCESSORY_UNLOCK_COST = {
    "dmg_s": 12, "dmg_pct": 15, "atk_spd": 14,
    "pierce": 18, "multi": 20, ...
}
```

**问题**：
1. 梯度太小（15-26），没有贵重感
2. 没有考虑侵蚀度收益（后期道韵溢出）
3. 没有成就门槛（全部用道韵）
4. 伙伴解锁的法宝/饰品也要道韵（重复付费）

---

## 二、解决方案

### 2.1 道韵价格重新设计

#### 原则
```
1. 梯度明显：10 → 30 → 60 → 100
2. 考虑侵蚀度收益：
   - 侵蚀度 0：35 道韵/局
   - 侵蚀度 5：70 道韵/局
   - 侵蚀度 10：105 道韵/局
3. 伙伴解锁的内容免费（已经付过治疗费）
4. 成就解锁的内容需要道韵（但有成就门槛）
```

#### 具体价格

```python
# 灵根（保持简单）
LINGGEN_COST = {
    "fire": 0,      # 初始
    "water": 0,     # 初始
    "wood": 0,      # 初始
    "metal": 30,    # 1 局（侵蚀度 0）
    "earth": 30,    # 1 局（侵蚀度 0）
    "none": 60,     # 2 局（侵蚀度 0）
}

# 法宝（伙伴解锁的免费，成就解锁的需要道韵）
FABAO_COST = {
    "sword": 0,     # 初始
    "spell": 0,     # 伙伴解锁（玄霄）
    "staff": 0,     # 伙伴解锁（青璃）
    "blade": 0,     # 伙伴解锁（赤渊）
    "stone": 0,     # 伙伴解锁（碧落）
    "cauldron": 0,  # 伙伴解锁（墨羽）
    "needle": 50,   # 成就解锁（速度大师）
}

# 饰品（伙伴解锁的免费，其他分档）
ACCESSORY_UNLOCK_COST = {
    # 基础（便宜）
    "dmg_s": 15,
    "mp": 12,
    "evap_splash": 20,
    "elec_chain": 25,
    "melt_heal": 18,
    
    # 伙伴解锁（免费）
    "dmg_pct": 0,       # 玄霄
    "atk_spd": 0,       # 青璃
    "mana_burn": 0,     # 赤渊
    "hp": 0,            # 碧落
    "iron_shell": 0,    # 墨羽
    
    # 进阶（中等）
    "pierce": 40,
    "multi": 50,
    
    # 风险收益（贵）
    "glass_core": 60,
    "swift_debt": 60,
}
```

---

### 2.2 成就系统设计

#### 成就与法宝关联

```python
# achievement.py（新增）

ACHIEVEMENT_LIST = [
    # 法宝解锁成就
    {
        "id": "speed_master",
        "name": "速度大师",
        "desc": "单局攻速达到 200%",
        "unlock": "needle",  # 解锁离火针
        "check": lambda stats: stats.get("max_attack_speed", 0) >= 200,
    },
    
    # 饰品解锁成就（暂时没有，但预留）
    {
        "id": "combo_100",
        "name": "百连击",
        "desc": "达成 100 连击",
        "unlock": None,  # 暂时没有对应饰品
        "check": lambda stats: stats.get("max_combo", 0) >= 100,
    },
]

# 检查成就
def check_achievements(stats: dict, completed: set) -> list:
    """返回新完成的成就 ID 列表"""
    new_achievements = []
    for ach in ACHIEVEMENT_LIST:
        if ach["id"] not in completed and ach["check"](stats):
            new_achievements.append(ach["id"])
    return new_achievements
```

#### 解锁条件修改

```python
# unlock.py 修改

def get_lockable_fabao(unlocked, partner_bond_levels=None, achievements=None):
    """可解锁法宝：未解锁 且 满足条件"""
    from partner import PARTNER_UNLOCKS_FABAO
    
    bond = partner_bond_levels or {}
    achievements = achievements or set()
    allowed = set()
    
    # 1. 初始法宝
    allowed.add("sword")
    
    # 2. 伙伴解锁（治疗后可见）
    for pid, fid in PARTNER_UNLOCKS_FABAO.items():
        if fid and bond.get(pid, 0) >= 1:
            allowed.add(fid)
    
    # 3. 成就解锁（完成成就后可见）
    if "speed_master" in achievements:
        allowed.add("needle")
    
    return [fb for fb in FABAO_LIST if fb.id not in unlocked and fb.id in allowed]
```

---

### 2.3 渐进式呈现设计

#### 核心思路
```
不是一次性显示所有局外成长
而是根据通关次数逐步解锁

通关次数 → 解锁内容：
  0 次：无（只能看到基础内容）
  1 次：玄真的灵根殿、铸心的炼器坊
  2 次：碧落的丹阁（生命/灵力/丹药成长）
  3 次：饰品槽扩展（6→7）
  5 次：商店刷新（1→2）
  8 次：开局饰品（0→1）
  10 次：饰品槽扩展（7→8）
```

#### 实现方案

```python
# meta.py 修改

class MetaProgress:
    def __init__(self):
        self.total_wins = 0  # 总通关次数
        self.unlocked_features = set()  # 已解锁的功能
        
    def check_unlock_features(self):
        """根据通关次数解锁功能"""
        new_unlocks = []
        
        # 1 次通关：解锁灵根殿、炼器坊
        if self.total_wins >= 1 and "linggen_hall" not in self.unlocked_features:
            self.unlocked_features.add("linggen_hall")
            self.unlocked_features.add("fabao_forge")
            new_unlocks.append("linggen_hall")
            new_unlocks.append("fabao_forge")
        
        # 2 次通关：解锁丹阁
        if self.total_wins >= 2 and "growth_hall" not in self.unlocked_features:
            self.unlocked_features.add("growth_hall")
            new_unlocks.append("growth_hall")
        
        # 3 次通关：解锁饰品槽扩展
        if self.total_wins >= 3 and "accessory_slot_upgrade" not in self.unlocked_features:
            self.unlocked_features.add("accessory_slot_upgrade")
            new_unlocks.append("accessory_slot_upgrade")
        
        # 5 次通关：解锁商店刷新
        if self.total_wins >= 5 and "shop_refresh_upgrade" not in self.unlocked_features:
            self.unlocked_features.add("shop_refresh_upgrade")
            new_unlocks.append("shop_refresh_upgrade")
        
        # 8 次通关：解锁开局饰品
        if self.total_wins >= 8 and "start_accessory" not in self.unlocked_features:
            self.unlocked_features.add("start_accessory")
            new_unlocks.append("start_accessory")
        
        return new_unlocks
```

#### 村子界面修改

```python
# village_scene.py 修改

def render_village(self):
    """渲染村子界面"""
    # 中央广场（栖霞）- 始终可见
    self.draw_npc("qixia", (400, 300))
    
    # 玄霄、青璃 - 始终可见
    self.draw_npc("xuanxiao", (200, 200))
    self.draw_npc("qingli", (600, 200))
    
    # 玄真的灵根殿 - 1 次通关后可见
    if "linggen_hall" in self.meta.unlocked_features:
        self.draw_building("linggen_hall", (100, 400))
    else:
        self.draw_locked("???", (100, 400))
    
    # 铸心的炼器坊 - 1 次通关后可见
    if "fabao_forge" in self.meta.unlocked_features:
        self.draw_building("fabao_forge", (700, 400))
    else:
        self.draw_locked("???", (700, 400))
    
    # 碧落的丹阁 - 2 次通关后可见
    if "growth_hall" in self.meta.unlocked_features:
        self.draw_building("growth_hall", (400, 500))
    elif self.meta.total_wins >= 1:
        self.draw_locked("???", (400, 500), hint="继续探索以解锁...")
    
    # 赤渊 - 治疗后可见
    if self.meta.partner_bond_levels.get("chiyuan", 0) >= 1:
        self.draw_npc("chiyuan", (300, 300))
    elif self.meta.total_wins >= 1:
        self.draw_locked("???", (300, 300), hint="完成挑战以解锁...")
```

#### 炼器坊界面修改

```python
# village_scene.py - 炼器坊界面

def render_fabao_forge(self):
    """渲染炼器坊界面"""
    y = 100
    
    # 已解锁法宝
    y = self.draw_section("已解锁", y)
    for fb_id in self.meta.unlocked_fabao:
        fb = get_fabao(fb_id)
        self.draw_item(fb.name, y)
        y += 30
    
    # 可解锁法宝
    lockable = get_lockable_fabao(
        self.meta.unlocked_fabao,
        self.meta.partner_bond_levels,
        self.meta.completed_achievements
    )
    
    if lockable:
        y = self.draw_section("可解锁", y)
        for fb in lockable:
            cost = get_fabao_cost(fb.id)
            # 显示解锁条件
            condition = self.get_unlock_condition(fb.id)
            self.draw_unlock_item(fb.name, cost, condition, y)
            y += 40
    
    # 未解锁（隐藏）
    if self.meta.total_wins >= 1:
        y = self.draw_section("未解锁", y)
        self.draw_hint("治疗伙伴以解锁更多法宝...", y)
        y += 30
        self.draw_hint("完成成就以解锁特殊法宝...", y)
    
    # 局外成长（渐进式显示）
    y += 50
    y = self.draw_section("局外成长", y)
    
    # 饰品槽扩展 - 3 次通关后可见
    if "accessory_slot_upgrade" in self.meta.unlocked_features:
        current = self.meta.accessory_slots
        if current < 9:
            cost = get_growth_cost("accessory_slot", current)
            self.draw_upgrade("饰品槽", f"{current}→{current+1}", cost, y)
            y += 35
    
    # 商店刷新 - 5 次通关后可见
    if "shop_refresh_upgrade" in self.meta.unlocked_features:
        current = self.meta.shop_refresh_count
        if current < 3:
            cost = get_growth_cost("shop_refresh", current)
            self.draw_upgrade("商店刷新", f"{current}→{current+1}", cost, y)
            y += 35
    
    # 开局饰品 - 8 次通关后可见
    if "start_accessory" in self.meta.unlocked_features:
        current = self.meta.start_accessory_count
        if current < 3:
            cost = get_growth_cost("start_accessory", current)
            self.draw_upgrade("开局饰品", f"{current}→{current+1}", cost, y)
            y += 35

def get_unlock_condition(self, fb_id: str) -> str:
    """获取法宝解锁条件描述"""
    # 伙伴解锁
    for pid, fid in PARTNER_UNLOCKS_FABAO.items():
        if fid == fb_id:
            partner = get_partner(pid)
            if self.meta.partner_bond_levels.get(pid, 0) >= 1:
                return "✓ 已治疗伙伴"
            else:
                return f"需要：治疗{partner.name}"
    
    # 成就解锁
    if fb_id == "needle":
        if "speed_master" in self.meta.completed_achievements:
            return "✓ 已完成成就"
        else:
            return "需要：成就「速度大师」"
    
    return ""
```

---

### 2.4 丹阁界面（新增）

```python
# village_scene.py - 丹阁界面

def render_growth_hall(self):
    """渲染碧落的丹阁（局外成长）"""
    y = 100
    
    self.draw_title("碧落的丹阁", y)
    y += 50
    
    # 生命上限成长
    current_hp = self.meta.bonus_health
    cost_hp = get_growth_cost("health", current_hp)
    self.draw_upgrade("生命上限", f"+10（当前 +{current_hp}）", cost_hp, y)
    y += 40
    
    # 灵力上限成长
    current_mp = self.meta.bonus_mana
    cost_mp = get_growth_cost("mana", current_mp)
    self.draw_upgrade("灵力上限", f"+10（当前 +{current_mp}）", cost_mp, y)
    y += 40
    
    # 丹药上限成长
    current_potion = self.meta.potion_cap
    if current_potion < 4:
        cost_potion = get_growth_cost("potion_cap", current_potion)
        self.draw_upgrade("丹药上限", f"{current_potion}→{current_potion+1}", cost_potion, y)
        y += 40
    else:
        self.draw_text("丹药上限已满", y)
```

---

## 三、实现步骤

### 3.1 修改 unlock.py

```python
# 1. 修改道韵价格
LINGGEN_COST = {
    "fire": 0, "water": 0, "wood": 0,
    "metal": 30, "earth": 30, "none": 60,
}

FABAO_COST = {
    "sword": 0, "spell": 0, "staff": 0,
    "blade": 0, "stone": 0, "cauldron": 0,
    "needle": 50,
}

ACCESSORY_UNLOCK_COST = {
    "dmg_s": 15, "mp": 12,
    "evap_splash": 20, "elec_chain": 25, "melt_heal": 18,
    "dmg_pct": 0, "atk_spd": 0, "mana_burn": 0, "hp": 0, "iron_shell": 0,
    "pierce": 40, "multi": 50,
    "glass_core": 60, "swift_debt": 60,
}

# 2. 修改解锁条件函数
def get_lockable_fabao(unlocked, partner_bond_levels=None, achievements=None):
    from partner import PARTNER_UNLOCKS_FABAO
    bond = partner_bond_levels or {}
    achievements = achievements or set()
    allowed = {"sword"}
    
    for pid, fid in PARTNER_UNLOCKS_FABAO.items():
        if fid and bond.get(pid, 0) >= 1:
            allowed.add(fid)
    
    if "speed_master" in achievements:
        allowed.add("needle")
    
    return [fb for fb in FABAO_LIST if fb.id not in unlocked and fb.id in allowed]
```

### 3.2 新增 achievement.py

```python
"""成就系统"""

ACHIEVEMENT_LIST = [
    {
        "id": "speed_master",
        "name": "速度大师",
        "desc": "单局攻速达到 200%",
        "unlock": "needle",
        "check": lambda stats: stats.get("max_attack_speed", 0) >= 200,
    },
]

def check_achievements(stats: dict, completed: set) -> list:
    new_achievements = []
    for ach in ACHIEVEMENT_LIST:
        if ach["id"] not in completed and ach["check"](stats):
            new_achievements.append(ach["id"])
    return new_achievements
```

### 3.3 修改 meta.py

```python
# 添加字段
class MetaProgress:
    def __init__(self):
        self.total_wins = 0
        self.unlocked_features = set()
        self.completed_achievements = set()
        self.bonus_health = 0
        self.bonus_mana = 0
        self.potion_cap = 1
        self.accessory_slots = 6
        self.shop_refresh_count = 1
        self.start_accessory_count = 0
    
    def on_win(self):
        self.total_wins += 1
        new_unlocks = self.check_unlock_features()
        return new_unlocks
    
    def check_unlock_features(self):
        new_unlocks = []
        if self.total_wins >= 1 and "linggen_hall" not in self.unlocked_features:
            self.unlocked_features.update(["linggen_hall", "fabao_forge"])
            new_unlocks.extend(["linggen_hall", "fabao_forge"])
        if self.total_wins >= 2 and "growth_hall" not in self.unlocked_features:
            self.unlocked_features.add("growth_hall")
            new_unlocks.append("growth_hall")
        if self.total_wins >= 3 and "accessory_slot_upgrade" not in self.unlocked_features:
            self.unlocked_features.add("accessory_slot_upgrade")
            new_unlocks.append("accessory_slot_upgrade")
        if self.total_wins >= 5 and "shop_refresh_upgrade" not in self.unlocked_features:
            self.unlocked_features.add("shop_refresh_upgrade")
            new_unlocks.append("shop_refresh_upgrade")
        if self.total_wins >= 8 and "start_accessory" not in self.unlocked_features:
            self.unlocked_features.add("start_accessory")
            new_unlocks.append("start_accessory")
        return new_unlocks
```

### 3.4 修改 village_scene.py

```python
# 1. 渲染村子时检查 unlocked_features
# 2. 炼器坊界面根据 unlocked_features 显示局外成长
# 3. 新增丹阁界面
```

---

## 四、总结

### 核心改动

1. **道韵价格**：梯度明显（0 → 30 → 60），伙伴解锁的免费
2. **成就系统**：新增 achievement.py，成就与法宝关联
3. **渐进式呈现**：根据通关次数逐步解锁功能
4. **丹阁界面**：新增碧落的丹阁，专门用于生命/灵力/丹药成长

### 玩家体验

```
第 1 局：只有基础内容
通关后：「解锁了灵根殿和炼器坊！」✨

第 2 局：可以解锁灵根、法宝
通关后：「解锁了丹阁！可以提升生命上限了！」✨

第 3 局：可以提升生命/灵力
通关后：「解锁了饰品槽扩展！」✨

第 5 局：可以扩展饰品槽
通关后：「解锁了商店刷新！」✨

第 8 局：可以刷新商店
通关后：「解锁了开局饰品！」✨
```

---

**这次是具体的实现方案，可以直接开始写代码了！**




