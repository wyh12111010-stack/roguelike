"""玩家"""
import math
import os
import pygame

from config import ARENA_X, ARENA_Y, ARENA_W, ARENA_H, COLOR_PLAYER, COLOR_HP_BAR, COLOR_HP_BG, COLOR_MP_BAR, COLOR_MP_BG, PLAYER_BASE_SPEED
from core import EventBus
from core.events import PLAYER_HIT
from controls import action_pressed

# 精灵图路径（2×2 网格）
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_SCRIPT_DIR, "assets")
PLAYER_IDLE_PATH = os.path.join(ASSETS_DIR, "player_idle.png")
PLAYER_DEATH_PATH = os.path.join(ASSETS_DIR, "player_death.png")
PLAYER_SPRITE_SCALE = 0.075  # 显示缩放倍数（640px -> 48px）


def _find_sprite_paths():
    """优先用标准命名，否则在 assets 中查找 nanobanana-edited-*.png 按文件名排序取前两个。"""
    idle, death = PLAYER_IDLE_PATH, PLAYER_DEATH_PATH
    if os.path.exists(idle) and os.path.exists(death):
        return idle, death
    nb_files = sorted(
        (os.path.join(ASSETS_DIR, f) for f in os.listdir(ASSETS_DIR or "")
         if f.startswith("nanobanana-edited-") and f.lower().endswith(".png")),
        key=os.path.basename,
    )
    if len(nb_files) >= 2:
        return nb_files[0], nb_files[1]
    return idle, death


def _load_player_sprites():
    """加载主角精灵图，失败则返回 None。主角是静态图。"""
    try:
        from tools.sprite_loader import get_content_center
        
        # 主角是单张静态图
        if os.path.exists(PLAYER_IDLE_PATH):
            img = pygame.image.load(PLAYER_IDLE_PATH).convert_alpha()
            
            # 单张静态图
            idle_frames = [img]
            idle_pivots = [get_content_center(img)]
            
            # 死亡也用同一张图
            death_frames = idle_frames
            death_pivots = idle_pivots
            
            return {
                "idle": idle_frames,
                "death": death_frames,
                "idle_pivots": idle_pivots,
                "death_pivots": death_pivots,
            }
    except Exception as e:
        print(f"加载主角精灵图失败: {e}")
    return None


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 16, y - 16, 32, 32)
        self.anim_timer = 0.0
        self._death_anim_start = None  # 死亡时记录，用于播放死亡动画
        self._sprites = _load_player_sprites()
        self.facing = 0  # 朝向角度（弧度）
        self.attack_cooldown = 0
        self.invincible_timer = 0  # 受伤后无敌时间
        self.opening_grace_timer = 0  # 关卡开场保护窗（读招缓冲）
        self.dash_cooldown = 0     # 冲刺冷却
        self._dash_cooldown_max = 0.8
        self._dash_dist = 55
        self._dash_invincible = 0.12
        self._flash_timer = 0  # HP 减少时红色闪烁计时器
        self._last_health = 100  # 上一帧的血量
        
        # 属性（来源于自身 + 可被加成修改）
        self.max_health = 100
        self.health = 100
        self.max_mana = 100
        self.mana = 100
        self.speed = PLAYER_BASE_SPEED
        self.lingshi = 0   # 局内货币，身陨/凯旋后清零
        
        # 灵根、双法宝
        self.linggen = None
        self.fabao_list = []       # [主法宝, 副法宝]，最多 2 个
        self.current_fabao_index = 0  # 当前手持 0 或 1
        self._gongfa = None       # 兼容旧逻辑
        # 局内：饰品、法宝强化
        self.accessories = []
        self.fabao_damage_pct = 0
        self.fabao_speed_pct = 0
        self.spell_cooldowns = {}  # {spell_id: 剩余冷却秒数}
        # 伙伴（治疗解锁后带入战斗，羁绊等级影响 Buff 强度）
        self.partner_id = None
        self.partner_bond_level = 0
        self.partner_charge = 0
        self.partner_charge_max = 100
        self._attack_chain_index = 0  # 普攻节奏序号（用于做法宝手感差异）
    
    @property
    def fabao(self):
        """当前手持法宝，兼容旧代码"""
        if not self.fabao_list:
            return None
        i = self.current_fabao_index % len(self.fabao_list)
        return self.fabao_list[i]
    
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

    def try_dash(self, arena_rect):
        """Shift 冲刺：朝朝向方向短距位移 + 短暂无敌。CD 0.8s。"""
        if self.dash_cooldown > 0 or self.health <= 0:
            return False
        keys = pygame.key.get_pressed()
        bindings = getattr(self, "_keybinds", None) or {}
        dx = dy = 0
        if action_pressed(keys, bindings, "move_up") or keys[pygame.K_UP]:
            dy -= 1
        if action_pressed(keys, bindings, "move_down") or keys[pygame.K_DOWN]:
            dy += 1
        if action_pressed(keys, bindings, "move_left") or keys[pygame.K_LEFT]:
            dx -= 1
        if action_pressed(keys, bindings, "move_right") or keys[pygame.K_RIGHT]:
            dx += 1
        if dx or dy:
            length = math.sqrt(dx*dx + dy*dy)
            dx, dy = dx / length, dy / length
        else:
            dx = math.cos(self.facing)
            dy = math.sin(self.facing)
        self.rect.x += int(dx * self._dash_dist)
        self.rect.y += int(dy * self._dash_dist)
        self.rect.clamp_ip(arena_rect)
        self.invincible_timer = self._dash_invincible
        
        # 计算闪避冷却（考虑饰品效果）
        cd = self._dash_cooldown_max
        for acc, lv in self.accessories:
            acc_id = getattr(acc, 'id', '')
            if acc_id == "dodge_cost":
                cd *= max(0.5, 1 - 0.2 * lv)  # -20% 每级
            elif acc_id == "swift_minor":
                cd *= max(0.5, 1 - 0.2 * lv)  # 迅捷碎片：闪避冷却-20%
        self.dash_cooldown = cd
        
        # 迅捷之翼：闪避后2秒内伤害+40%
        for acc, lv in self.accessories:
            if getattr(acc, 'id', '') == "swift_extreme":
                self._swift_wing_until = 2.0
        
        return True
    
    def can_cast_spell(self):
        """当前法宝法术是否可释放（灵力够 + CD 好）"""
        fb = self.fabao
        if not fb or not fb.spell_id or fb.spell_mana <= 0:
            return False
        if self.mana < fb.spell_mana:
            return False
        cd = self.spell_cooldowns.get(fb.spell_id, 0)
        return cd <= 0
    
    def cast_spell(self, ctx):
        """E 键释放当前法宝独有法术。ctx: {projectiles, spell_zones, earth_walls}"""
        if not self.can_cast_spell():
            return
        fb = self.fabao
        self.mana -= fb.spell_mana
        self.spell_cooldowns[fb.spell_id] = fb.spell_cooldown
        from spell_effects import SPELL_HANDLERS
        handler = SPELL_HANDLERS.get(fb.spell_id)
        if handler:
            handler(self, ctx)

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
        erosion.erosion_level = getattr(self, 'erosion_level', 0)
        
        modifiers = erosion.get_stat_modifiers()
        for stat, change in modifiers.items():
            if stat == "max_hp":
                self.max_health = max(1, self.max_health + int(change))
                self.health = min(self.max_health, self.health)
            elif stat == "attack":
                # 攻击力加成通过饰品系统应用
                pass
            elif stat == "defense":
                # 防御力加成通过饰品系统应用
                pass
            elif stat == "speed":
                self.speed = max(50, self.speed + int(change))
    
    def add_accessory(self, acc, level=1):
        """装备饰品，应用生命/灵力上限。acc 为 Accessory 实例"""
        self.accessories.append((acc, level))
        self.max_health += (getattr(acc, 'health_bonus', 0) or 0) * level
        self.max_health = max(1, self.max_health)
        self.health = min(self.max_health, self.health + (getattr(acc, 'health_bonus', 0) or 0) * level)
        self.max_mana += (getattr(acc, 'mana_bonus', 0) or 0) * level
        self.max_mana = max(1, self.max_mana)
        self.mana = min(self.max_mana, self.mana + (getattr(acc, 'mana_bonus', 0) or 0) * level)
        return True

    def upgrade_accessory(self, index):
        """升级已装备饰品，返回是否成功"""
        if index < 0 or index >= len(self.accessories):
            return False
        acc, lv = self.accessories[index]
        if lv >= acc.max_level:
            return False
        self.accessories[index] = (acc, lv + 1)
        self.max_health += getattr(acc, 'health_bonus', 0) or 0
        self.max_health = max(1, self.max_health)
        self.health = min(self.max_health, self.health + (getattr(acc, 'health_bonus', 0) or 0))
        self.max_mana += getattr(acc, 'mana_bonus', 0) or 0
        self.max_mana = max(1, self.max_mana)
        self.mana = min(self.max_mana, self.mana + (getattr(acc, 'mana_bonus', 0) or 0))
        return True
    
    def _effective_speed(self):
        """当前有效移速（减速 debuff + 伙伴 buff + 幻步 + 饰品加成）"""
        spd = self.speed
        
        # 伙伴加成
        pid = getattr(self, "partner_id", None)
        blv = getattr(self, "partner_bond_level", 0)
        if pid in ("qingli", "moyu") and blv > 0:
            from partner import get_buff_val
            pct = get_buff_val(pid, blv, "speed") / 100
            spd = int(spd * (1 + pct))
        
        # 幻步加成
        if getattr(self, "_partner_huanbu_until", 0) > 0:
            spd = int(spd * getattr(self, "_partner_huanbu_speed", 1.3))  # 幻步 +30%
        
        # 饰品移速加成
        from accessory_effects import get_speed_multiplier
        speed_mult = get_speed_multiplier(self)
        spd = int(spd * speed_mult)
        
        # 减速debuff
        if getattr(self, "_player_slow_until", 0) <= 0:
            return spd
        pct = min(40, getattr(self, "_player_slow_pct", 10)) / 100
        return max(50, int(spd * (1 - pct)))

    def _get_attack_source(self):
        """获取当前攻击来源：优先法宝，否则功法"""
        return self.fabao if self.fabao else self._gongfa
    
    def update(self, dt, enemies, projectiles):
        # 更新闪烁计时器
        if self._flash_timer > 0:
            self._flash_timer -= dt
        
        # 检测血量变化
        if self.health < self._last_health:
            self._flash_timer = 0.3  # 闪烁 0.3 秒
        self._last_health = self.health
        
        # 移动（WASD 或 方向键）
        keys = pygame.key.get_pressed()
        bindings = getattr(self, "_keybinds", None) or {}
        dx = dy = 0
        if action_pressed(keys, bindings, "move_up") or keys[pygame.K_UP]:
            dy -= 1
        if action_pressed(keys, bindings, "move_down") or keys[pygame.K_DOWN]:
            dy += 1
        if action_pressed(keys, bindings, "move_left") or keys[pygame.K_LEFT]:
            dx -= 1
        if action_pressed(keys, bindings, "move_right") or keys[pygame.K_RIGHT]:
            dx += 1
        
        if dx or dy:
            length = math.sqrt(dx*dx + dy*dy)
            dx /= length
            dy /= length
            spd = self._effective_speed()
            self.rect.x += dx * spd * dt
            self.rect.y += dy * spd * dt
            self.facing = math.atan2(dy, dx)
        
        # 限制在框内
        self.rect.clamp_ip(pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H))
        
        # 朝向鼠标
        mx, my = pygame.mouse.get_pos()
        self.facing = math.atan2(my - self.rect.centery, mx - self.rect.centerx)
        
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
        if self.opening_grace_timer > 0:
            self.opening_grace_timer -= dt
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt

        # 虚弱
        if getattr(self, "_weaken_until", 0) > 0:
            self._weaken_until -= dt

        # 减速（敌人土/水基础效果）
        if getattr(self, "_player_slow_until", 0) > 0:
            self._player_slow_until -= dt
        # 幻步（青璃技能）
        if getattr(self, "_partner_huanbu_until", 0) > 0:
            self._partner_huanbu_until -= dt
        
        # 迅捷之翼效果计时
        if getattr(self, "_swift_wing_until", 0) > 0:
            self._swift_wing_until -= dt

        # 持续伤害
        for dot in getattr(self, "_dot_list", [])[:]:
            dot["timer"] += dt
            if dot["timer"] >= dot["interval"]:
                dot["timer"] = 0
                self.health = max(0, self.health - dot["dmg"])
                dot["ticks_left"] -= 1
                if dot["ticks_left"] <= 0:
                    self._dot_list.remove(dot)
        
        self.anim_timer += dt
        if self.health <= 0 and self._death_anim_start is None:
            self._death_anim_start = self.anim_timer

        # 灵力恢复
        if self.mana < self.max_mana:
            base_regen = 3
            # 迅捷之核：每次攻击回复1灵力（在攻击时处理）
            # 饰品回灵效果
            from accessory_effects import trigger_mana_regen
            trigger_mana_regen(self, dt)
            self.mana = min(self.max_mana, self.mana + base_regen * dt)
        # 法术 CD
        for sid in list(self.spell_cooldowns):
            self.spell_cooldowns[sid] -= dt
            if self.spell_cooldowns[sid] <= 0:
                del self.spell_cooldowns[sid]
        
        # 攻击
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        src = self._get_attack_source()
        if pygame.mouse.get_pressed()[0] and self.attack_cooldown <= 0 and src:
            self._attack(projectiles)
            base_cd = getattr(src, 'attack_cooldown', 0.4)
            self.attack_cooldown = self._get_attack_cooldown(base_cd)
            
            # 迅捷之核：每次攻击回复1灵力
            for acc, lv in self.accessories:
                if getattr(acc, 'id', '') == "swift_moderate":
                    self.mana = min(self.max_mana, self.mana + 1 * lv)
    
    def _attack(self, projectiles):
        """按法宝 attack_form 分发，对标 Tiny Rogues：爽点在弹道、射速、范围"""
        from attribute import get_self_reaction
        from particles import spawn_particles
        from fx_audio import play_player_attack
        src = self._get_attack_source()
        if not src:
            return
        damage = getattr(src, 'damage', 20)
        form = getattr(src, 'attack_form', '') or ('arc' if getattr(src, 'is_melee', True) else 'pierce')
        proj_speed = getattr(src, 'projectile_speed', 0)
        is_melee = form in ("arc", "heavy") or (form == "" and getattr(src, 'is_melee', True))
        final_damage = self._calc_damage(damage, is_melee=is_melee)
        attr = src.attr if hasattr(src, 'attr') else None
        
        # 混沌碎片：攻击附带随机元素
        for acc, lv in self.accessories:
            if getattr(acc, 'id', '') == "chaos_minor":
                import random
                from attribute import Attr
                elements = [Attr.FIRE, Attr.WATER, Attr.WOOD, Attr.METAL, Attr.EARTH]
                attr = random.choice(elements)
                break
        
        self_reaction = get_self_reaction(self)
        cx, cy = self.rect.centerx, self.rect.centery
        r = getattr(src, 'attack_range', 60)
        seq = self._attack_chain_index
        self._attack_chain_index += 1
        
        if form == "arc":
            from projectile import MeleeSlash
            # 赤炎剑：交替宽弧与前压半弧，形成“贴身连斩”体感
            slash_ang = self.facing + (0.18 if (seq % 2 == 0) else -0.18)
            slash_arc = 2.1 if (seq % 2 == 0) else 1.5
            slash = MeleeSlash(cx, cy, slash_ang, r, 0.2, final_damage, attr=attr, arc_half=slash_arc, self_reaction=self_reaction)
            projectiles.append(slash)
        elif form == "heavy":
            from projectile import MeleeSlash, Projectile
            # 庚金刃：慢重斩 + 轻量短射程剑气余波
            heavy_dmg = int(final_damage * 1.4)
            slash = MeleeSlash(cx, cy, self.facing, r, 0.35, heavy_dmg, attr=attr, arc_half=1.2, self_reaction=self_reaction)
            projectiles.append(slash)
            vx = math.cos(self.facing) * 220
            vy = math.sin(self.facing) * 220
            wave = Projectile(cx, cy, vx, vy, max(1, int(final_damage * 0.45)), 0.35, pierce=False, attr=attr, self_reaction=self_reaction)
            projectiles.append(wave)
        elif form == "pierce":
            from projectile import Projectile
            # 玄水符：高速度直线穿透，强调“对位打线”
            speed = max(proj_speed, 420)
            dx = math.cos(self.facing) * speed
            dy = math.sin(self.facing) * speed
            proj = Projectile(cx, cy, dx, dy, final_damage, 0.8, pierce=True, attr=attr, self_reaction=self_reaction)
            projectiles.append(proj)
        elif form == "fan":
            from projectile import Projectile
            multi = self._get_multi_shot()
            # 青木杖：基础扇形更宽，强调“控面覆盖”
            n = 3 + min(multi, 2)
            spread = 0.35
            base = self.facing - spread * (n - 1) / 2
            for i in range(n):
                ang = base + spread * i
                vx = math.cos(ang) * proj_speed
                vy = math.sin(ang) * proj_speed
                proj = Projectile(cx, cy, vx, vy, final_damage, 0.6, pierce=self._has_pierce(), attr=attr, self_reaction=self_reaction)
                projectiles.append(proj)
        elif form == "parabolic":
            from projectile import ParabolicProjectile
            speed = proj_speed or 380
            # 厚土印：左右交替抛掷角，形成节奏化落点压制
            launch = self.facing - 0.45 if (seq % 2 == 0) else self.facing - 0.6
            vx = math.cos(launch) * speed
            vy = math.sin(launch) * speed
            proj = ParabolicProjectile(cx, cy, vx, vy, final_damage, aoe_radius=70, attr=attr, self_reaction=self_reaction)
            projectiles.append(proj)
        else:
            from projectile import MeleeSlash, Projectile
            is_melee = getattr(src, 'is_melee', True)
            if is_melee:
                slash = MeleeSlash(cx, cy, self.facing, r, 0.2, final_damage, attr=attr, self_reaction=self_reaction)
                projectiles.append(slash)
            else:
                dx = math.cos(self.facing) * proj_speed
                dy = math.sin(self.facing) * proj_speed
                proj = Projectile(cx, cy, dx, dy, final_damage, 0.6, pierce=self._has_pierce(), attr=attr, self_reaction=self_reaction)
                projectiles.append(proj)
        # 近战在身前短距反馈，远程在中距反馈，避免覆盖角色本体
        fx_dist = 18 if form in ("arc", "heavy") else 34
        fx_x = cx + math.cos(self.facing) * fx_dist
        fx_y = cy + math.sin(self.facing) * fx_dist
        fx_key = {
            "arc": "player_arc",
            "pierce": "player_pierce",
            "fan": "player_fan",
            "heavy": "player_heavy",
            "parabolic": "player_parabolic",
        }.get(form, "player_arc")
        spawn_particles(fx_x, fx_y, fx_key)
        play_player_attack(form=form, attr=attr)
    
    def _calc_damage(self, base_damage, is_melee=False):
        """伤害计算：灵根+法宝 相合/反应 + 饰品 + 法宝强化 + 伙伴 buff + 特殊效果"""
        from attribute import check_resonance, get_reaction, get_resonance_bonus, get_element_harmony_bonus
        from setting import DAMAGE_RESONANCE_MULT, DAMAGE_REACTION_MULT
        d = base_damage
        fb = self.fabao
        has_reaction = False
        
        if self.linggen and fb:
            lg_attr = self.linggen.attr
            fb_attr = fb.attr
            
            # 基础相合/相克
            if check_resonance(lg_attr, fb_attr):
                d = int(d * DAMAGE_RESONANCE_MULT)
            elif get_reaction(lg_attr, fb_attr):
                d = int(d * DAMAGE_REACTION_MULT)
                has_reaction = True
            
            # 新增：相合加成（共鸣核心饰品）
            resonance_bonus = get_resonance_bonus(lg_attr, fb_attr, self)
            if resonance_bonus:
                d = int(d * (1 + resonance_bonus.get("damage_pct", 0) / 100))
            
            # 新增：五行调和加成
            harmony_bonus = get_element_harmony_bonus(lg_attr, fb_attr, self)
            if harmony_bonus:
                d = int(d * (1 + harmony_bonus.get("damage_pct", 0) / 100))
        
        d += self.fabao_damage_pct * base_damage // 100
        
        # 基础饰品加成
        for acc, lv in self.accessories:
            d += (getattr(acc, 'damage_bonus', 0) or 0) * lv
            d += int(base_damage * (getattr(acc, 'damage_pct', 0) or 0) * lv // 100)
        
        # 特殊效果：条件触发类
        d = self._apply_conditional_damage_bonuses(d, base_damage, is_melee, has_reaction)
        
        # 伙伴 buff
        pid = getattr(self, "partner_id", None)
        blv = getattr(self, "partner_bond_level", 0)
        if pid == "xuanxiao" and has_reaction and blv > 0:
            from partner import get_buff_val
            pct = get_buff_val(pid, blv, "reaction_dmg") / 100
            d = int(d * (1 + pct))
        if pid == "chiyuan" and is_melee and blv > 0:
            from partner import get_buff_val
            pct = get_buff_val(pid, blv, "melee_dmg") / 100
            d = int(d * (1 + pct))
        return max(1, d)
    
    def _apply_conditional_damage_bonuses(self, damage, base_damage, is_melee, has_reaction):
        """应用条件触发类饰品的伤害加成"""
        multiplier = 1.0
        
        for acc, lv in self.accessories:
            acc_id = getattr(acc, 'id', '')
            
            # 低血狂暴：生命<30% 时伤害+40%
            if acc_id == "low_hp_power" and self.health < self.max_health * 0.3:
                multiplier += 0.4 * lv
            
            # 高灵力爆发：灵力>80% 时伤害+25%
            elif acc_id == "high_mana_power" and self.mana > self.max_mana * 0.8:
                multiplier += 0.25 * lv
            
            # 连击赌博：连击>20 时伤害+35%
            elif acc_id == "combo_risk":
                game = getattr(self, '_game_ref', None)
                if game and getattr(game, 'current_combo', 0) > 20:
                    multiplier += 0.35 * lv
            
            # 近战宗师：近战伤害+15%
            elif acc_id == "melee_master" and is_melee:
                multiplier += 0.15 * lv
            
            # 远程专精：远程伤害+12%
            elif acc_id == "ranged_focus" and not is_melee:
                multiplier += 0.12 * lv
            
            # 疾风节奏：攻速<0.4s时额外伤害+12%
            elif acc_id == "fast_rhythm" and self.fabao and self.fabao.attack_cooldown < 0.4:
                multiplier += 0.12 * lv
            
            # 重击冲击：攻速>0.6s时伤害+18%
            elif acc_id == "heavy_impact" and self.fabao and self.fabao.attack_cooldown > 0.6:
                multiplier += 0.18 * lv
            
            # 元素强化：对应属性伤害+18%
            elif acc_id == "fire_core" and self.fabao and self.fabao.attr.name == "FIRE":
                multiplier += 0.18 * lv
            elif acc_id == "water_soul" and self.fabao and self.fabao.attr.name == "WATER":
                multiplier += 0.18 * lv
            elif acc_id == "wood_spirit" and self.fabao and self.fabao.attr.name == "WOOD":
                multiplier += 0.18 * lv
            elif acc_id == "metal_edge" and self.fabao and self.fabao.attr.name == "METAL":
                multiplier += 0.18 * lv
            elif acc_id == "earth_shield" and self.fabao and self.fabao.attr.name == "EARTH":
                multiplier += 0.18 * lv
            
            # === 秽源共鸣专属饰品 ===
            # 狂暴之心：连击>10时伤害+30%
            elif acc_id == "fury_extreme":
                game = getattr(self, '_game_ref', None)
                if game and getattr(game, 'current_combo', 0) > 10:
                    multiplier += 0.3 * lv
            
            # 坚韧之盾：生命<30%时减伤+40%（在 take_damage 中处理）
            # 迅捷之翼：闪避后2秒内伤害+40%
            elif acc_id == "swift_extreme" and getattr(self, '_swift_wing_until', 0) > 0:
                multiplier += 0.4 * lv
            
            # 混沌之心：触发任意反应时伤害+50%（简化版）
            elif acc_id == "chaos_extreme" and has_reaction:
                multiplier += 0.5 * lv
            
            # 贫瘠碎片：每100灵石转化为+5%伤害
            elif acc_id == "barren_minor":
                lingshi_bonus = (self.lingshi // 100) * 0.05 * lv
                multiplier += lingshi_bonus
            
            # 贫瘠之心：每个空饰品槽+15%伤害
            elif acc_id == "barren_extreme":
                from meta import meta
                max_slots = getattr(meta, 'accessory_slots', 6)
                empty_slots = max_slots - len(self.accessories)
                multiplier += 0.15 * empty_slots * lv
        
        return int(damage * multiplier)

    def _get_attack_cooldown(self, base_cd):
        """攻速：法宝 + 饰品 + 相合/调和加成 + 特殊效果"""
        from attribute import get_resonance_bonus, get_element_harmony_bonus
        cd = base_cd
        form = getattr(self.fabao, "attack_form", "") if self.fabao else ""
        # 法宝基础节奏差异：不改数值表，仅塑造手感层次
        form_mul = {
            "arc": 0.92,
            "pierce": 0.9,
            "fan": 1.0,
            "heavy": 1.18,
            "parabolic": 1.08,
        }.get(form, 1.0)
        cd *= form_mul
        
        # 新增：相合加成（共鸣核心饰品）
        if self.linggen and self.fabao:
            resonance_bonus = get_resonance_bonus(self.linggen.attr, self.fabao.attr, self)
            if resonance_bonus:
                cd *= max(0.5, 1 - resonance_bonus.get("attack_speed_pct", 0) / 100)
            
            # 新增：五行调和加成
            harmony_bonus = get_element_harmony_bonus(self.linggen.attr, self.fabao.attr, self)
            if harmony_bonus:
                cd *= max(0.5, 1 - harmony_bonus.get("attack_speed_pct", 0) / 100)
        
        # 基础饰品加成
        for acc, lv in self.accessories:
            pct = getattr(acc, 'attack_speed_pct', 0) or 0
            cd *= max(0.5, 1 - pct * lv / 100)
        
        cd *= max(0.5, 1 - self.fabao_speed_pct / 100)
        
        # 特殊效果：闪避代价（闪避冷却-20%）
        for acc, lv in self.accessories:
            if getattr(acc, 'id', '') == "dodge_cost":
                # 这个效果应用在 dash_cooldown 上，不在这里
                pass
        
        return max(0.1, cd)

    def _has_pierce(self):
        for acc, _ in self.accessories:
            if getattr(acc, 'pierce', False):
                return True
        return False

    def _get_multi_shot(self):
        n = 0
        for acc, lv in self.accessories:
            n += (getattr(acc, 'multi_shot', 0) or 0) * lv
        return n
    
    def take_damage(self, amount, attacker_attr=None):
        if self.health <= 0:
            return
        if self.opening_grace_timer > 0:
            return
        if self.invincible_timer > 0:
            return
        amount = int(amount)
        if amount <= 0:
            return
        if getattr(self, "_weaken_until", 0) > 0:
            amount = int(amount * (1 + getattr(self, "_weaken_pct", 15) / 100))
        pid = getattr(self, "partner_id", None)
        blv = getattr(self, "partner_bond_level", 0)
        if pid == "biluo" and blv > 0:
            from partner import get_buff_val
            pct = get_buff_val(pid, blv, "damage_reduce") / 100
            amount = int(amount * (1 - pct))
        self.health = max(0, self.health - amount)
        
        # 计算反弹伤害（在扣血后）
        reflect_dmg = 0
        from accessory_effects import get_reflect_damage
        reflect_dmg = get_reflect_damage(self, amount)
        
        if self.health <= 0:
            # 死亡结算优先：不再施加新 debuff / 反应
            EventBus.emit(PLAYER_HIT, damage=amount)
            return
        inv = 0.8
        if pid == "moyu" and blv > 0:
            from partner import get_buff_val
            pct = get_buff_val(pid, blv, "speed_invincible") / 100
            inv = 0.8 + pct * 0.4  # 每级约 +0.4s 无敌
        self.invincible_timer = inv
        cx, cy = self.rect.centerx, self.rect.centery
        from attribute import get_reaction_for_hit, Attr
        from particles import spawn_particles
        lg_attr = self.linggen.attr if self.linggen else Attr.NONE
        reaction = get_reaction_for_hit(attacker_attr or Attr.NONE, lg_attr) if attacker_attr else None
        if reaction:
            from reaction_effects import emit_reaction
            emit_reaction(reaction, amount, self, (cx, cy), attacker_type="enemy")
        elif attacker_attr and attacker_attr != Attr.NONE:
            from attribute_effects import apply_base_attr_effect_enemy_vs_player
            apply_base_attr_effect_enemy_vs_player(attacker_attr, amount, self)
            spawn_particles(cx, cy, attacker_attr.name.lower())
        else:
            spawn_particles(cx, cy, "hit")
        EventBus.emit(PLAYER_HIT, damage=amount)
    
    def draw(self, screen):
        sp = self._sprites
        if sp and self.health > 0 and sp["idle"] and len(sp["idle"]) > 0:
            from tools.sprite_loader import play_animation
            frames = sp["idle"]
            pivots = sp["idle_pivots"]
            idx = play_animation(frames, self.anim_timer, fps=8)
            f = frames[idx]
            cx, cy = pivots[idx]
            fw, fh = f.get_size()
            scale = PLAYER_SPRITE_SCALE
            sw, sh = int(fw * scale), int(fh * scale)
            scaled = pygame.transform.scale(f, (sw, sh))
            # 以质心为锚点对齐到 rect 中心
            sx = self.rect.centerx - int(cx * scale)
            sy = self.rect.centery - int(cy * scale)
            
            # 受击抖动效果
            if self.invincible_timer > 0:
                import random
                shake_x = random.randint(-2, 2)
                shake_y = random.randint(-2, 2)
                sx += shake_x
                sy += shake_y
                # 受击闪烁（红色叠加）
                if int(self.invincible_timer * 20) % 2 == 0:
                    red_overlay = scaled.copy()
                    red_overlay.fill((255, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
                    screen.blit(red_overlay, (sx, sy))
                else:
                    screen.blit(scaled, (sx, sy))
            else:
                screen.blit(scaled, (sx, sy))
        elif sp and self.health <= 0:
            # 死亡粒子效果
            if self._death_anim_start is None:
                self._death_anim_start = self.anim_timer
                # 生成死亡粒子
                from particles import spawn_particles
                cx, cy = self.rect.centerx, self.rect.centery
                for _ in range(20):  # 20 个粒子
                    spawn_particles(cx, cy, "death")
            
            # 死亡后不再绘制角色（粒子消失效果）
            # 如果需要死亡动画，可以在这里添加
            idx = min(3, int(elapsed * 6))  # 死亡动画约 0.67 秒播完
            f = frames[idx]
            cx, cy = pivots[idx]
            fw, fh = f.get_size()
            scale = PLAYER_SPRITE_SCALE
            sw, sh = int(fw * scale), int(fh * scale)
            scaled = pygame.transform.scale(f, (sw, sh))
            sx = self.rect.centerx - int(cx * scale)
            sy = self.rect.centery - int(cy * scale)
            screen.blit(scaled, (sx, sy))
        else:
            pygame.draw.rect(screen, COLOR_PLAYER, self.rect)
            end_x = self.rect.centerx + math.cos(self.facing) * 25
            end_y = self.rect.centery + math.sin(self.facing) * 25
            pygame.draw.line(screen, (255, 255, 255), self.rect.center, (end_x, end_y), 2)
        # Debuff 边框
        has_dot = bool(getattr(self, "_dot_list", []))
        has_slow = getattr(self, "_player_slow_until", 0) > 0
        has_weaken = getattr(self, "_weaken_until", 0) > 0
        if has_dot:
            pygame.draw.rect(screen, (255, 100, 50), self.rect.inflate(6, 6), 2)
        if has_slow:
            pygame.draw.rect(screen, (100, 180, 255), self.rect.inflate(8, 8), 1)
        if has_weaken:
            pygame.draw.rect(screen, (180, 100, 180), self.rect.inflate(10, 10), 1)
        
        # 血条、蓝条（角色下方）
        bar_w, bar_h = 40, 5
        x = self.rect.centerx - bar_w // 2
        y = self.rect.bottom + 4
        # 血条（受伤时闪烁）
        pygame.draw.rect(screen, COLOR_HP_BG, (x, y, bar_w, bar_h))
        hp_color = COLOR_HP_BAR
        if self._flash_timer > 0:
            # 闪烁效果：红色更亮
            hp_color = (255, 100, 100)
        pygame.draw.rect(screen, hp_color, (x, y, int(bar_w * self.health / self.max_health), bar_h))
        # 蓝条
        y += bar_h + 2
        pygame.draw.rect(screen, COLOR_MP_BG, (x, y, bar_w, bar_h))
        pygame.draw.rect(screen, COLOR_MP_BAR, (x, y, int(bar_w * self.mana / self.max_mana), bar_h))
