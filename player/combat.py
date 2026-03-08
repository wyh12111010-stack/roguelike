"""
玩家战斗组件 - 从 player.py 提取
负责攻击分发、伤害计算、受击逻辑、法术释放。
"""

import math

try:
    from core import EventBus
    from core.events import PLAYER_HIT
except ImportError:
    # 延迟导入兼容
    EventBus = None
    PLAYER_HIT = "PLAYER_HIT"


class PlayerCombat:
    """战斗相关方法 mixin"""

    def _get_attack_source(self):
        """获取当前攻击来源：优先法宝，否则功法"""
        return self.fabao if self.fabao else self._gongfa

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

    def _attack(self, projectiles):
        """按法宝 attack_form 分发，对标 Tiny Rogues：爽点在弹道、射速、范围"""
        from attribute import get_self_reaction
        from fx_audio import play_player_attack
        from particles import spawn_particles

        src = self._get_attack_source()
        if not src:
            return
        damage = getattr(src, "damage", 20)
        form = getattr(src, "attack_form", "") or ("arc" if getattr(src, "is_melee", True) else "pierce")
        proj_speed = getattr(src, "projectile_speed", 0)
        is_melee = form in ("arc", "heavy") or (form == "" and getattr(src, "is_melee", True))
        final_damage = self._calc_damage(damage, is_melee=is_melee)
        attr = src.attr if hasattr(src, "attr") else None

        # 混沌碎片：攻击附带随机元素
        for acc, _lv in self.accessories:
            if getattr(acc, "id", "") == "chaos_minor":
                import random

                from attribute import Attr

                elements = [Attr.FIRE, Attr.WATER, Attr.WOOD, Attr.METAL, Attr.EARTH]
                attr = random.choice(elements)
                break

        self_reaction = get_self_reaction(self)
        cx, cy = self.rect.centerx, self.rect.centery
        r = getattr(src, "attack_range", 60)
        seq = self._attack_chain_index
        self._attack_chain_index += 1

        self._dispatch_attack_form(
            form, projectiles, cx, cy, r, seq, final_damage, proj_speed, attr, self_reaction, src
        )

        # 粒子与音效
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

    # ── 攻击形态分发 ──

    def _dispatch_attack_form(
        self, form, projectiles, cx, cy, r, seq, final_damage, proj_speed, attr, self_reaction, src
    ):
        if form == "arc":
            from projectile import MeleeSlash

            slash_ang = self.facing + (0.18 if (seq % 2 == 0) else -0.18)
            slash_arc = 2.1 if (seq % 2 == 0) else 1.5
            slash = MeleeSlash(
                cx, cy, slash_ang, r, 0.2, final_damage, attr=attr, arc_half=slash_arc, self_reaction=self_reaction
            )
            projectiles.append(slash)
        elif form == "heavy":
            from projectile import MeleeSlash, Projectile

            heavy_dmg = int(final_damage * 1.4)
            slash = MeleeSlash(
                cx, cy, self.facing, r, 0.35, heavy_dmg, attr=attr, arc_half=1.2, self_reaction=self_reaction
            )
            projectiles.append(slash)
            vx = math.cos(self.facing) * 220
            vy = math.sin(self.facing) * 220
            wave = Projectile(
                cx,
                cy,
                vx,
                vy,
                max(1, int(final_damage * 0.45)),
                0.35,
                pierce=False,
                attr=attr,
                self_reaction=self_reaction,
            )
            projectiles.append(wave)
        elif form == "pierce":
            from projectile import Projectile

            speed = max(proj_speed, 420)
            dx = math.cos(self.facing) * speed
            dy = math.sin(self.facing) * speed
            proj = Projectile(cx, cy, dx, dy, final_damage, 0.8, pierce=True, attr=attr, self_reaction=self_reaction)
            projectiles.append(proj)
        elif form == "fan":
            from projectile import Projectile

            multi = self._get_multi_shot()
            n = 3 + min(multi, 2)
            spread = 0.35
            base = self.facing - spread * (n - 1) / 2
            for i in range(n):
                ang = base + spread * i
                vx = math.cos(ang) * proj_speed
                vy = math.sin(ang) * proj_speed
                proj = Projectile(
                    cx, cy, vx, vy, final_damage, 0.6, pierce=self._has_pierce(), attr=attr, self_reaction=self_reaction
                )
                projectiles.append(proj)
        elif form == "parabolic":
            from projectile import ParabolicProjectile

            speed = proj_speed or 380
            launch = self.facing - 0.45 if (seq % 2 == 0) else self.facing - 0.6
            vx = math.cos(launch) * speed
            vy = math.sin(launch) * speed
            proj = ParabolicProjectile(
                cx, cy, vx, vy, final_damage, aoe_radius=70, attr=attr, self_reaction=self_reaction
            )
            projectiles.append(proj)
        else:
            from projectile import MeleeSlash, Projectile

            is_melee = getattr(src, "is_melee", True)
            if is_melee:
                slash = MeleeSlash(cx, cy, self.facing, r, 0.2, final_damage, attr=attr, self_reaction=self_reaction)
                projectiles.append(slash)
            else:
                dx = math.cos(self.facing) * proj_speed
                dy = math.sin(self.facing) * proj_speed
                proj = Projectile(
                    cx, cy, dx, dy, final_damage, 0.6, pierce=self._has_pierce(), attr=attr, self_reaction=self_reaction
                )
                projectiles.append(proj)

    # ── 伤害计算 ──

    def _calc_damage(self, base_damage, is_melee=False):
        """伤害计算：灵根+法宝 相合/反应 + 饰品 + 法宝强化 + 伙伴 buff + 特殊效果"""
        from attribute import check_resonance, get_element_harmony_bonus, get_reaction, get_resonance_bonus
        from setting import DAMAGE_REACTION_MULT, DAMAGE_RESONANCE_MULT

        d = base_damage
        fb = self.fabao
        has_reaction = False

        if self.linggen and fb:
            lg_attr = self.linggen.attr
            fb_attr = fb.attr
            if check_resonance(lg_attr, fb_attr):
                d = int(d * DAMAGE_RESONANCE_MULT)
            elif get_reaction(lg_attr, fb_attr):
                d = int(d * DAMAGE_REACTION_MULT)
                has_reaction = True
            resonance_bonus = get_resonance_bonus(lg_attr, fb_attr, self)
            if resonance_bonus:
                d = int(d * (1 + resonance_bonus.get("damage_pct", 0) / 100))
            harmony_bonus = get_element_harmony_bonus(lg_attr, fb_attr, self)
            if harmony_bonus:
                d = int(d * (1 + harmony_bonus.get("damage_pct", 0) / 100))

        d += self.fabao_damage_pct * base_damage // 100

        for acc, lv in self.accessories:
            d += (getattr(acc, "damage_bonus", 0) or 0) * lv
            d += int(base_damage * (getattr(acc, "damage_pct", 0) or 0) * lv // 100)

        d = self._apply_conditional_damage_bonuses(d, base_damage, is_melee, has_reaction)

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
            acc_id = getattr(acc, "id", "")
            if acc_id == "low_hp_power" and self.health < self.max_health * 0.3:
                multiplier += 0.4 * lv
            elif acc_id == "high_mana_power" and self.mana > self.max_mana * 0.8:
                multiplier += 0.25 * lv
            elif acc_id == "combo_risk":
                game = getattr(self, "_game_ref", None)
                if game and getattr(game, "current_combo", 0) > 20:
                    multiplier += 0.35 * lv
            elif acc_id == "melee_master" and is_melee:
                multiplier += 0.15 * lv
            elif (acc_id == "ranged_focus" and not is_melee) or (
                acc_id == "fast_rhythm" and self.fabao and self.fabao.attack_cooldown < 0.4
            ):
                multiplier += 0.12 * lv
            elif (
                (acc_id == "heavy_impact" and self.fabao and self.fabao.attack_cooldown > 0.6)
                or (acc_id == "fire_core" and self.fabao and self.fabao.attr.name == "FIRE")
                or (acc_id == "water_soul" and self.fabao and self.fabao.attr.name == "WATER")
                or (acc_id == "wood_spirit" and self.fabao and self.fabao.attr.name == "WOOD")
                or (acc_id == "metal_edge" and self.fabao and self.fabao.attr.name == "METAL")
                or (acc_id == "earth_shield" and self.fabao and self.fabao.attr.name == "EARTH")
            ):
                multiplier += 0.18 * lv
            elif acc_id == "fury_extreme":
                game = getattr(self, "_game_ref", None)
                if game and getattr(game, "current_combo", 0) > 10:
                    multiplier += 0.3 * lv
            elif acc_id == "swift_extreme" and getattr(self, "_swift_wing_until", 0) > 0:
                multiplier += 0.4 * lv
            elif acc_id == "chaos_extreme" and has_reaction:
                multiplier += 0.5 * lv
            elif acc_id == "barren_minor":
                lingshi_bonus = (self.lingshi // 100) * 0.05 * lv
                multiplier += lingshi_bonus
            elif acc_id == "barren_extreme":
                from meta import meta

                max_slots = getattr(meta, "accessory_slots", 6)
                empty_slots = max_slots - len(self.accessories)
                multiplier += 0.15 * empty_slots * lv
        return int(damage * multiplier)

    def _get_attack_cooldown(self, base_cd):
        """攻速：法宝 + 饰品 + 相合/调和加成 + 特殊效果"""
        from attribute import get_element_harmony_bonus, get_resonance_bonus

        cd = base_cd
        form = getattr(self.fabao, "attack_form", "") if self.fabao else ""
        form_mul = {
            "arc": 0.92,
            "pierce": 0.9,
            "fan": 1.0,
            "heavy": 1.18,
            "parabolic": 1.08,
        }.get(form, 1.0)
        cd *= form_mul

        if self.linggen and self.fabao:
            resonance_bonus = get_resonance_bonus(self.linggen.attr, self.fabao.attr, self)
            if resonance_bonus:
                cd *= max(0.5, 1 - resonance_bonus.get("attack_speed_pct", 0) / 100)
            harmony_bonus = get_element_harmony_bonus(self.linggen.attr, self.fabao.attr, self)
            if harmony_bonus:
                cd *= max(0.5, 1 - harmony_bonus.get("attack_speed_pct", 0) / 100)

        for acc, lv in self.accessories:
            pct = getattr(acc, "attack_speed_pct", 0) or 0
            cd *= max(0.5, 1 - pct * lv / 100)
        cd *= max(0.5, 1 - self.fabao_speed_pct / 100)
        return max(0.1, cd)

    def _has_pierce(self):
        return any(getattr(acc, "pierce", False) for acc, _ in self.accessories)

    def _get_multi_shot(self):
        n = 0
        for acc, lv in self.accessories:
            n += (getattr(acc, "multi_shot", 0) or 0) * lv
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

        from accessory_effects import get_reflect_damage

        get_reflect_damage(self, amount)

        if self.health <= 0:
            EventBus.emit(PLAYER_HIT, damage=amount)
            return
        inv = 0.8
        if pid == "moyu" and blv > 0:
            from partner import get_buff_val

            pct = get_buff_val(pid, blv, "speed_invincible") / 100
            inv = 0.8 + pct * 0.4
        self.invincible_timer = inv
        cx, cy = self.rect.centerx, self.rect.centery
        from attribute import Attr, get_reaction_for_hit
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
