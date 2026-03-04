# 解锁系统完整方案

> 解决三个核心问题：
> 1. 灵根梯度问题
> 2. 法宝专属法术设计
> 3. 属性重要性问题

---

## 一、灵根系统重新设计

### 1.1 问题分析

```
当前问题：
  灵根有道韵梯度（0 → 15 → 18 → 20 → 25）
  
为什么不合理：
  - 灵根只是属性选择，不是强度差异
  - 金木水火土应该平等
  - 无灵根也不是「更强」，只是「不参与反应」
```

### 1.2 解决方案

```python
# 灵根全部免费，初始全部解锁
LINGGEN_COST = {
    "fire": 0,
    "water": 0,
    "wood": 0,
    "metal": 0,
    "earth": 0,
    "none": 0,
}

# 关键：灵根是玩法选择，不是解锁内容
# 玩家每局开始前自由选择灵根
```

---

## 二、法宝专属法术设计

### 2.1 当前状态

```python
# fabao.py 中的法术
"sword": "flame_wave"      # ✓ 已设计
"spell": "water_prison"    # ✓ 已设计
"staff": "vine_bind"       # ✓ 已设计
"blade": "blade_storm"     # ✓ 已设计
"stone": "earth_wall"      # ✓ 已设计
"needle": "flame_wave"     # ✗ 复用了 sword 的
"cauldron": "earth_wall"   # ✗ 复用了 stone 的
```

### 2.2 新增法术设计

#### 离火针（needle）专属法术

```python
# spell_effects.py 新增

def cast_needle_rain(player, ctx):
    """离火针：针雨 - 范围内持续降下火针"""
    cx = player.rect.centerx + math.cos(player.facing) * 100
    cy = player.rect.centery + math.sin(player.facing) * 100
    
    # 创建持续 2.5 秒的针雨区域
    zone = NeedleRainZone(
        cx, cy,
        radius=95,           # 范围
        duration=2.5,        # 持续时间
        tick_interval=0.15,  # 每 0.15 秒降下一波针
        damage_per_tick=player._calc_damage(8),  # 每波伤害
        attr=player.fabao.attr,
        self_reaction=get_self_reaction(player)
    )
    ctx["spell_zones"].append(zone)

# projectile.py 新增

class NeedleRainZone:
    """针雨区域：持续降下火针"""
    def __init__(self, x, y, radius, duration, tick_interval, damage_per_tick, attr, self_reaction):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.tick_interval = tick_interval
        self.damage_per_tick = damage_per_tick
        self.attr = attr
        self.self_reaction = self_reaction
        self.timer = 0
        self.tick_timer = 0
        self.dead = False
    
    def update(self, dt, enemies):
        self.timer += dt
        if self.timer >= self.duration:
            self.dead = True
            return
        
        self.tick_timer += dt
        if self.tick_timer >= self.tick_interval:
            self.tick_timer = 0
            # 对范围内所有敌人造成伤害
            for e in enemies:
                if e.dead:
                    continue
                dx = e.rect.centerx - self.x
                dy = e.rect.centery - self.y
                if dx*dx + dy*dy < self.radius * self.radius:
                    e.take_damage(self.damage_per_tick, self.attr, self.self_reaction)
    
    def draw(self, screen, camera):
        # 绘制红色圆圈表示范围
        sx = int(self.x - camera.x)
        sy = int(self.y - camera.y)
        pygame.draw.circle(screen, (255, 100, 50, 100), (sx, sy), self.radius, 2)
```

#### 玄坤鼎（cauldron）专属法术

```python
# spell_effects.py 新增

def cast_gravity_field(player, ctx):
    """玄坤鼎：重力场 - 范围内敌人被拉向中心 + 持续伤害"""
    cx = player.rect.centerx + math.cos(player.facing) * 100
    cy = player.rect.centery + math.sin(player.facing) * 100
    
    zone = GravityFieldZone(
        cx, cy,
        radius=110,          # 范围
        duration=3.0,        # 持续时间
        pull_strength=150,   # 拉力强度
        tick_interval=0.3,   # 每 0.3 秒造成伤害
        damage_per_tick=player._calc_damage(12),
        attr=player.fabao.attr,
        self_reaction=get_self_reaction(player)
    )
    ctx["spell_zones"].append(zone)

# projectile.py 新增

class GravityFieldZone:
    """重力场：拉扯敌人 + 持续伤害"""
    def __init__(self, x, y, radius, duration, pull_strength, tick_interval, damage_per_tick, attr, self_reaction):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.pull_strength = pull_strength
        self.tick_interval = tick_interval
        self.damage_per_tick = damage_per_tick
        self.attr = attr
        self.self_reaction = self_reaction
        self.timer = 0
        self.tick_timer = 0
        self.dead = False
    
    def update(self, dt, enemies):
        self.timer += dt
        if self.timer >= self.duration:
            self.dead = True
            return
        
        # 拉扯敌人
        for e in enemies:
            if e.dead:
                continue
            dx = e.rect.centerx - self.x
            dy = e.rect.centery - self.y
            dist_sq = dx*dx + dy*dy
            if dist_sq < self.radius * self.radius and dist_sq > 1:
                dist = math.sqrt(dist_sq)
                # 向中心拉
                pull_x = -dx / dist * self.pull_strength * dt
                pull_y = -dy / dist * self.pull_strength * dt
                e.rect.x += pull_x
                e.rect.y += pull_y
        
        # 持续伤害
        self.tick_timer += dt
        if self.tick_timer >= self.tick_interval:
            self.tick_timer = 0
            for e in enemies:
                if e.dead:
                    continue
                dx = e.rect.centerx - self.x
                dy = e.rect.centery - self.y
                if dx*dx + dy*dy < self.radius * self.radius:
                    e.take_damage(self.damage_per_tick, self.attr, self.self_reaction)
    
    def draw(self, screen, camera):
        # 绘制棕色圆圈表示范围
        sx = int(self.x - camera.x)
        sy = int(self.y - camera.y)
        pygame.draw.circle(screen, (160, 120, 80, 100), (sx, sy), self.radius, 2)
```

### 2.3 更新法宝配置

```python
# fabao.py 修改

FABAO_LIST = [
    Fabao("sword", "赤炎剑", Attr.FIRE, True, 25, 0.4, 60, 0, ATTACK_ARC, 
          "flame_wave", 15, 6.0),
    Fabao("spell", "玄水符", Attr.WATER, False, 15, 0.6, 300, 400, ATTACK_PIERCE, 
          "water_prison", 20, 8.0),
    Fabao("staff", "青木杖", Attr.WOOD, False, 18, 0.5, 280, 380, ATTACK_FAN, 
          "vine_bind", 18, 7.0),
    Fabao("blade", "庚金刃", Attr.METAL, True, 22, 0.55, 65, 0, ATTACK_HEAVY, 
          "blade_storm", 25, 10.0),
    Fabao("stone", "厚土印", Attr.EARTH, False, 20, 0.55, 260, 350, ATTACK_PARABOLIC, 
          "earth_wall", 22, 9.0),
    Fabao("needle", "离火针", Attr.FIRE, False, 12, 0.34, 320, 500, ATTACK_PIERCE, 
          "needle_rain", 18, 7.0),  # 改为 needle_rain
    Fabao("cauldron", "玄坤鼎", Attr.EARTH, False, 26, 0.72, 250, 320, ATTACK_PARABOLIC, 
          "gravity_field", 24, 10.0),  # 改为 gravity_field
]
```

### 2.4 更新法术处理器

```python
# spell_effects.py 修改

SPELL_HANDLERS = {
    "flame_wave": cast_flame_wave,
    "water_prison": cast_water_prison,
    "vine_bind": cast_vine_bind,
    "blade_storm": cast_blade_storm,
    "earth_wall": cast_earth_wall,
    "needle_rain": cast_needle_rain,      # 新增
    "gravity_field": cast_gravity_field,  # 新增
}
```

---

## 三、属性重要性提升

### 3.1 问题分析

```
当前问题：
  - 五行反应效果不够明显
  - 玩家感受不到属性的重要性
  - 选什么灵根/法宝都差不多

根本原因：
  1. 反应伤害占比太低（溅射 28%、传导 45%）
  2. 反应触发不够频繁（只有相克才触发）
  3. 相合（共鸣）没有明显收益
```

### 3.2 解决方案

#### 方案 A：提升反应伤害

```python
# reaction_effects.py 修改

REACTION_CONFIG = {
    "jin_mu": {   # 金克木：斩木
        "execute_threshold": 0.30,
        "execute_extra_pct": 80,     # 50 → 80（提升斩杀伤害）
        "splash_radius": 75,         # 65 → 75（扩大范围）
        "splash_damage_pct": 45,     # 28 → 45（提升溅射伤害）
    },
    "mu_tu": {    # 木克土：破土
        "chain_radius": 100,         # 85 → 100（扩大传导范围）
        "chain_damage_pct": 65,      # 45 → 65（提升传导伤害）
        "max_chain": 4,              # 3 → 4（增加传导次数）
        "spread_radius": 80,
        "spread_weaken_pct": 18,     # 12 → 18（提升虚弱）
        "spread_weaken_duration": 1.5,
    },
    "tu_shui": {  # 土克水：堵水
        "slow_pct": 35,              # 22 → 35（提升减速）
        "slow_duration": 1.8,        # 1.2 → 1.8（延长持续）
        "weaken_pct": 22,            # 15 → 22（提升虚弱）
        "weaken_duration": 1.5,
    },
    "shui_huo": { # 水克火：灭火
        "splash_radius": 85,         # 70 → 85
        "splash_damage_pct": 50,     # 30 → 50（提升溅射）
        "dot_damage_pct": 12,        # 8 → 12（提升 DOT）
        "dot_ticks": 4,              # 3 → 4（增加跳数）
        "dot_interval": 0.4,
    },
    "huo_jin": {  # 火克金：熔金
        "dot_damage_pct": 15,        # 10 → 15（提升 DOT）
        "dot_ticks": 4,              # 3 → 4
        "dot_interval": 0.4,
        "self_heal_pct": 4,          # 2.5 → 4（提升回血）
        "self_mana_pct": 3,          # 1.5 → 3（提升回蓝）
    },
}
```

#### 方案 B：新增相合（共鸣）收益

```python
# attribute.py 新增

def get_resonance_bonus(linggen_attr: Attr, fabao_attr: Attr) -> dict:
    """
    相合（共鸣）收益：灵根 = 法宝属性时
    返回加成字典
    """
    if not check_resonance(linggen_attr, fabao_attr):
        return {}
    
    # 相合时：伤害 +25%，攻速 +15%
    return {
        "damage_pct": 25,
        "attack_speed_pct": 15,
    }
```

```python
# player.py 修改

def _calc_damage(self, base):
    """计算最终伤害"""
    dmg = base
    
    # 饰品加成
    for acc, lv in self.accessories:
        dmg += acc.damage_bonus * lv
        dmg = int(dmg * (1 + acc.damage_pct * lv / 100))
    
    # 相合加成（新增）
    if self.linggen and self.fabao:
        resonance = get_resonance_bonus(self.linggen.attr, self.fabao.attr)
        if resonance:
            dmg = int(dmg * (1 + resonance.get("damage_pct", 0) / 100))
    
    return max(1, dmg)

def _get_attack_cooldown(self):
    """计算攻击冷却"""
    cd = self.fabao.attack_cooldown
    
    # 饰品加成
    for acc, lv in self.accessories:
        cd *= (1 - acc.attack_speed_pct * lv / 100)
    
    # 相合加成（新增）
    if self.linggen and self.fabao:
        resonance = get_resonance_bonus(self.linggen.attr, self.fabao.attr)
        if resonance:
            cd *= (1 - resonance.get("attack_speed_pct", 0) / 100)
    
    return max(0.1, cd)
```

#### 方案 C：视觉强化反应提示（无文字）

```python
# particles.py 修改

def spawn_particles(x, y, reaction):
    """生成粒子效果（强化反应视觉）"""
    # 反应粒子配置
    reaction_particles = {
        "jin_mu": {
            "color": (200, 180, 120),
            "count": 15,        # 10 → 15（增加粒子数）
            "speed": 180,       # 120 → 180（加快速度）
            "size": 6,          # 4 → 6（增大粒子）
            "lifetime": 0.8,    # 0.5 → 0.8（延长生命）
        },
        "mu_tu": {
            "color": (80, 160, 80),
            "count": 20,        # 更多粒子表示传导
            "speed": 200,
            "size": 5,
            "lifetime": 0.7,
        },
        "tu_shui": {
            "color": (160, 120, 80),
            "count": 12,
            "speed": 150,
            "size": 7,
            "lifetime": 1.0,    # 持续更久表示减速
        },
        "shui_huo": {
            "color": (80, 150, 255),
            "count": 18,
            "speed": 160,
            "size": 6,
            "lifetime": 0.9,
        },
        "huo_jin": {
            "color": (255, 100, 50),
            "count": 16,
            "speed": 140,
            "size": 5,
            "lifetime": 1.2,    # 持续最久表示 DOT
        },
    }
    
    cfg = reaction_particles.get(reaction, {})
    if not cfg:
        return
    
    # 生成粒子
    for _ in range(cfg["count"]):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(cfg["speed"] * 0.7, cfg["speed"] * 1.3)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        particle = Particle(
            x, y, vx, vy,
            color=cfg["color"],
            size=cfg["size"],
            lifetime=cfg["lifetime"]
        )
        PARTICLES.append(particle)
    
    # 额外：屏幕震动（反应时）
    if hasattr(game, "camera"):
        game.camera.shake(intensity=8, duration=0.15)  # 轻微震动
```

```python
# camera.py 新增

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.shake_timer = 0
        self.shake_intensity = 0
    
    def shake(self, intensity, duration):
        """屏幕震动"""
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_timer = max(self.shake_timer, duration)
    
    def update(self, dt):
        if self.shake_timer > 0:
            self.shake_timer -= dt
            # 随机偏移
            self.x += random.uniform(-self.shake_intensity, self.shake_intensity)
            self.y += random.uniform(-self.shake_intensity, self.shake_intensity)
        else:
            self.shake_intensity = 0
```

#### 方案 D：精简五行流派饰品（3 个）

```python
# accessory.py 新增

# 设计思路：
# 1. 不要为每个五行关系都设计饰品（太多了）
# 2. 只设计 3 个通用饰品，覆盖所有五行关系
# 3. 让玩家自己发现属性组合的价值（涌现式）

ACCESSORY_LIST = [
    # ... 原有 38 个涌现式协同饰品 ...
    
    # === 五行流派饰品（3 个）===
    
    # 1. 相合流派（1 个）
    Accessory("resonance_core", "共鸣核心", "灵根=法宝属性时，伤害+20%，攻速+15%", 45, 3,
              resonance_dmg_bonus=20, resonance_speed_bonus=15),
    # 适用于：火火、水水、木木、金金、土土（5 种组合）
    # 玩法：高伤高速，稳定输出
    
    # 2. 相克流派（1 个）
    Accessory("reaction_master", "五行相克", "触发元素反应时，反应效果+30%", 48, 3,
              reaction_effect_bonus=30),
    # 适用于：所有相克组合（金木、木土、土水、水火、火金）
    # 玩法：强化所有反应（溅射、传导、减速、DOT、回血）
    # 关键：通用，不挑具体哪个反应
    
    # 3. 通用流派（1 个）
    Accessory("element_harmony", "五行调和", "有元素反应时伤害+15%，无反应时伤害+10%攻速+10%", 45, 3,
              with_reaction_dmg=15, no_reaction_dmg=10, no_reaction_speed=10),
    # 适用于：任何组合（相合、相克、相生、无属性）
    # 玩法：万金油，怎么搭配都有用
]
```

### 精简后的五行流派

```
只有 3 个五行饰品：
  1. 共鸣核心：相合时高伤高速
  2. 五行相克：相克时强化反应
  3. 五行调和：任何组合都有用

优势：
  ✅ 不会压缩其他流派空间（只占 3 个位置）
  ✅ 覆盖所有五行关系（相合、相克、相生）
  ✅ 通用性强，不挑具体组合
  ✅ 配合涌现式协同饰品（38 个）
  
总饰品数量：
  38 个涌现式协同饰品
  + 3 个五行流派饰品
  = 41 个饰品（合理数量）
```
```

```python
# reaction_effects.py 修改

def _get_reaction_bonus(self, player, reaction):
    """从玩家饰品获取反应增强"""
    if not player or not getattr(player, "accessories", []):
        return {}
    
    bonus = {}
    for acc, lv in player.accessories:
        # 五行相克饰品（通用反应强化）
        if hasattr(acc, "reaction_effect_bonus"):
            amp = acc.reaction_effect_bonus * lv
            # 对所有反应参数都加成
            bonus["splash_damage_pct"] = bonus.get("splash_damage_pct", 0) + amp
            bonus["splash_radius"] = bonus.get("splash_radius", 0) + amp * 0.5
            bonus["chain_damage_pct"] = bonus.get("chain_damage_pct", 0) + amp
            bonus["chain_radius"] = bonus.get("chain_radius", 0) + amp * 0.5
            bonus["slow_pct"] = bonus.get("slow_pct", 0) + amp * 0.5
            bonus["weaken_pct"] = bonus.get("weaken_pct", 0) + amp * 0.5
            bonus["dot_damage_pct"] = bonus.get("dot_damage_pct", 0) + amp
            bonus["self_heal_pct"] = bonus.get("self_heal_pct", 0) + amp
            bonus["self_mana_pct"] = bonus.get("self_mana_pct", 0) + amp
        
        # 原有的特定反应强化（保留兼容）
        if reaction == "shui_huo" and getattr(acc, "reaction_evaporation_pct", 0):
            bonus["splash_damage_pct"] = bonus.get("splash_damage_pct", 0) + acc.reaction_evaporation_pct * lv
        elif reaction == "mu_tu" and getattr(acc, "reaction_electro_chain", 0):
            bonus["max_chain"] = bonus.get("max_chain", 0) + acc.reaction_electro_chain * lv
        elif reaction == "huo_jin" and getattr(acc, "reaction_melt_heal_pct", 0):
            bonus["self_heal_pct"] = bonus.get("self_heal_pct", 0) + acc.reaction_melt_heal_pct * lv
    
    return bonus
```

```python
# attribute.py 修改

def get_resonance_bonus(linggen_attr: Attr, fabao_attr: Attr, player=None) -> dict:
    """
    相合（共鸣）收益：灵根 = 法宝属性时
    返回加成字典
    """
    if not check_resonance(linggen_attr, fabao_attr):
        return {}
    
    # 基础相合：伤害 +25%，攻速 +15%
    bonus = {
        "damage_pct": 25,
        "attack_speed_pct": 15,
    }
    
    # 共鸣核心饰品额外加成
    if player:
        for acc, lv in getattr(player, "accessories", []):
            if hasattr(acc, "resonance_dmg_bonus"):
                bonus["damage_pct"] += acc.resonance_dmg_bonus * lv
            if hasattr(acc, "resonance_speed_bonus"):
                bonus["attack_speed_pct"] += acc.resonance_speed_bonus * lv
    
    return bonus

def get_element_harmony_bonus(linggen_attr: Attr, fabao_attr: Attr, player=None) -> dict:
    """
    五行调和收益：任何组合都有用
    返回加成字典
    """
    if not player:
        return {}
    
    bonus = {}
    for acc, lv in getattr(player, "accessories", []):
        if hasattr(acc, "with_reaction_dmg"):
            # 检查是否有反应
            has_reaction = get_reaction_for_hit(linggen_attr, fabao_attr) is not None
            if has_reaction:
                bonus["damage_pct"] = bonus.get("damage_pct", 0) + acc.with_reaction_dmg * lv
            else:
                bonus["damage_pct"] = bonus.get("damage_pct", 0) + acc.no_reaction_dmg * lv
                bonus["attack_speed_pct"] = bonus.get("attack_speed_pct", 0) + acc.no_reaction_speed * lv
    
    return bonus
```

---

## 四、完整解锁系统

### 4.1 道韵价格（最终版）

```python
# unlock.py

# 灵根：全部免费
LINGGEN_COST = {
    "fire": 0,
    "water": 0,
    "wood": 0,
    "metal": 0,
    "earth": 0,
    "none": 0,
}

# 法宝：伙伴解锁的免费，成就解锁的需要道韵
FABAO_COST = {
    "sword": 0,     # 初始
    "spell": 0,     # 伙伴解锁（玄霄）
    "staff": 0,     # 伙伴解锁（青璃）
    "blade": 0,     # 伙伴解锁（赤渊）
    "stone": 0,     # 伙伴解锁（碧落）
    "cauldron": 0,  # 伙伴解锁（墨羽）
    "needle": 60,   # 成就解锁（速度大师）
}

# 饰品：伙伴解锁的免费，其他分档
ACCESSORY_UNLOCK_COST = {
    # 基础（15-25）
    "dmg_s": 15,
    "mp": 12,
    "evap_splash": 20,
    "elec_chain": 25,
    "melt_heal": 18,
    
    # 伙伴解锁（免费）
    "dmg_pct": 0,
    "atk_spd": 0,
    "mana_burn": 0,
    "hp": 0,
    "iron_shell": 0,
    
    # 进阶（40-50）
    "pierce": 40,
    "multi": 50,
    
    # 五行流派饰品（45-48，侵蚀度 2 后可见）
    "resonance_core": 45,      # 相合流派
    "reaction_master": 48,     # 相克流派
    "element_harmony": 45,     # 通用流派
    
    # 风险收益（60-70）
    "glass_core": 60,
    "swift_debt": 60,
}

# 总饰品数量：
# 38 个涌现式协同饰品（EMERGENT_SYNERGY_DESIGN.md）
# + 3 个五行流派饰品
# = 41 个饰品
```

### 4.2 解锁条件

```python
# unlock.py

def get_lockable_fabao(unlocked, partner_bond_levels=None, achievements=None):
    """可解锁法宝"""
    from partner import PARTNER_UNLOCKS_FABAO
    
    bond = partner_bond_levels or {}
    achievements = achievements or set()
    allowed = {"sword"}
    
    # 伙伴解锁
    for pid, fid in PARTNER_UNLOCKS_FABAO.items():
        if fid and bond.get(pid, 0) >= 1:
            allowed.add(fid)
    
    # 成就解锁
    if "speed_master" in achievements:
        allowed.add("needle")
    
    return [fb for fb in FABAO_LIST if fb.id not in unlocked and fb.id in allowed]

def get_lockable_accessories(unlocked_ids, partner_bond_levels=None, erosion_level=0):
    """可解锁饰品"""
    from partner import PARTNER_UNLOCKS_ACCESSORY
    
    bond = partner_bond_levels or {}
    allowed = set(ACCESSORY_DEFAULT_ALLOWED)
    
    # 伙伴解锁
    for pid, aid in PARTNER_UNLOCKS_ACCESSORY.items():
        if aid and bond.get(pid, 0) >= 1:
            allowed.add(aid)
    
    # 侵蚀度解锁（五行流派饰品，只有 3 个）
    if erosion_level >= 2:
        allowed.update(["resonance_core", "reaction_master", "element_harmony"])
    
    return [a for a in ACCESSORY_LIST if a.id not in unlocked_ids and a.id in allowed]
```

### 4.3 渐进式呈现

```python
# meta.py

def check_unlock_features(self):
    """根据通关次数解锁功能"""
    new_unlocks = []
    
    if self.total_wins >= 1 and "fabao_forge" not in self.unlocked_features:
        self.unlocked_features.add("fabao_forge")
        new_unlocks.append("fabao_forge")
    
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

---

## 五、总结

### 5.1 三个问题的解决

#### 1. 灵根梯度问题
```
✓ 灵根全部免费
✓ 初始全部解锁
✓ 灵根是玩法选择，不是解锁内容
```

#### 2. 法宝专属法术
```
✓ needle：针雨（范围持续伤害）
✓ cauldron：重力场（拉扯 + 持续伤害）
✓ 每个法宝都有独特法术
```

#### 3. 属性重要性
```
✓ 提升反应伤害（溅射 28%→45%，传导 45%→65%）
✓ 新增相合收益（伤害 +25%，攻速 +15%）
✓ 视觉强化反应（更多粒子 + 屏幕震动，无文字）
✓ 新增五行流派饰品（精简版，只有 3 个）
  - 共鸣核心：相合时高伤高速
  - 五行相克：相克时强化所有反应
  - 五行调和：任何组合都有用
  
流派平衡：
  - 38 个涌现式协同饰品（核心玩法）
  - 3 个五行流派饰品（属性强化）
  - 总计 41 个饰品（合理数量）
  
关键优势：
  ✅ 不会压缩其他流派空间
  ✅ 覆盖所有五行关系（相合、相克、相生）
  ✅ 通用性强，不挑具体组合
  ✅ 配合涌现式协同设计
```

### 5.2 玩家体验

```
选择灵根 + 法宝：
  - 火灵根 + 赤炎剑（火）= 相合流派
    → 基础：伤害 +25%，攻速 +15%
    → 配合「共鸣核心」饰品 → 额外 +20% 伤害，+15% 攻速
    → 配合「五行调和」饰品 → 无反应时 +10% 伤害，+10% 攻速
  
  - 水灵根 + 赤炎剑（火）= 相克流派（灭火）
    → 基础：溅射 50% + DOT
    → 配合「五行相克」饰品 → 所有反应效果 +30%
    → 配合「五行调和」饰品 → 有反应时 +15% 伤害
  
  - 金灵根 + 玄水符（水）= 相生流派
    → 基础：无特殊反应
    → 配合「五行调和」饰品 → 无反应时 +10% 伤害，+10% 攻速
    → 配合涌现式协同饰品 → 自由搭配

流派总结：
  相合流派：高伤高速，稳定输出（共鸣核心强化）
  相克流派：强力反应，爆发伤害（五行相克强化）
  相生/无属性流派：自由搭配（五行调和强化）
  涌现式协同：38 个饰品，无数组合
  
战斗中：
  - 大量粒子效果（15-20 个）
  - 屏幕轻微震动
  - 敌人被溅射 + DOT + 传导
  - 明显感受到属性的重要性
  - 无文字干扰
  - 只有 3 个五行饰品，不会压缩其他流派空间
```

---

**精简完成！现在：**
- ✅ 无文字干扰（只有粒子 + 震动）
- ✅ 只有 3 个五行饰品（不压缩其他流派）
- ✅ 覆盖所有五行关系（相合、相克、相生）
- ✅ 通用性强，不挑具体组合
- ✅ 配合 38 个涌现式协同饰品
- ✅ 总计 41 个饰品（合理数量）

