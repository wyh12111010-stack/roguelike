"""游戏主逻辑 - 接入 core/nodes 架构，见 docs/TECH_ARCHITECTURE.md"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, ARENA_X, ARENA_Y, ARENA_W, ARENA_H
from core import EventBus, GameState
from core.events import COMBAT_START, ENEMY_KILLED, LEVEL_CLEAR, SHOP_ENTER, VICTORY, PLAYER_DEATH, PLAYER_HIT, NODE_COMPLETE, ACHIEVEMENT_UNLOCKED
from player import Player
from enemy import Enemy, create_enemy, EnemyProjectile, AOEZone
from levels import get_level_enemies, get_demo_enemies, get_boss_enemies, get_node_type, get_node_display_name, get_level_display, get_node_reward, get_node_reward_type, DEMO_NAMES, DEMO_ROUTE_TREE, LEVELS, ROUTE_TREE
from systems import RouteSystem
from systems.route import assign_combat_rewards_for_options
from linggen import LINGGEN_LIST
from fabao import FABAO_LIST
from meta import meta
from save import persist_meta, RunSaveData, PlayerSaveData, save_run, clear_run_save
from setting import DAOYUN_ELITE, DAOYUN_BOSS, DAOYUN_VICTORY, DAOYUN_COMBAT_REWARD, LINGSHI_PER_KILL, LINGSHI_PER_LEVEL, LINGSHI_ELITE_BONUS, TREASURE_REWARDS
from village import LINGGEN_ZONE, FABAO_ZONE, CENTER_ZONE, PARTNER_ROOMS, EXIT_PORTAL, DEMO_PORTAL, VILLAGE_MAP_RECT, get_camera_offset
from ui import CombatLogUI
from ui.ui_manager import UIManager
from systems.combat import CombatSystem
from scenes import VillageScene


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.scene = "village"  # village | combat
        self.combat_log = CombatLogUI()
        self.village_player = None
        self.particle_mgr = None
        
        # 使用安全加载器加载可选系统
        from utils.safe_loader import SafeModuleLoader, NullDamageText, NullScreenShake
        
        # 伤害飘字系统（可选）
        self.damage_text_mgr = SafeModuleLoader.load_optional_system(
            'damage_text', 
            'init_damage_text_manager',
            fallback=NullDamageText(),
            silent=True
        )
        
        # 屏幕震动系统（可选）
        self.screen_shake = SafeModuleLoader.load_optional_system(
            'screen_shake',
            'init_screen_shake',
            fallback=NullScreenShake(),
            silent=True
        )
        
        self.hit_flash_until = 0.0  # 受击闪红剩余时间（秒）
        self.char_panel_open = False  # 人物页面（灵根/法宝/饰品）
        
        # 新 UI 系统
        self.ui_manager = UIManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.level_clear_pending = False  # 过关结算弹窗
        self.level_clear_timer = 0.0
        self.achievement_toast_until = 0.0  # 成就解锁 Toast
        self.achievement_toast_name = ""
        
        # 秽源共鸣系统
        from resonance_system import ResonanceSystem
        self.resonance_system = ResonanceSystem()
        self.resonance_panel_open = False
        
        # 局内统计（用于成就检查）
        self.max_combo = 0
        self.current_combo = 0
        self.combo_timer = 0.0
        self.total_damage = 0
        self.max_single_damage = 0
        self.total_reactions = 0
        self.vaporize_count = 0
        self.melt_count = 0
        self.overload_count = 0
        self.max_lingshi = 0
        self.shop_purchases = 0
        self.potions_used = 0
        self.max_accessories = 0
        self.max_accessory_level = 0
        self.low_health_survival_time = 0.0
        self.combat_start_time = 0.0
        self.boss_defeated_flags = {
            "boss_1": False,
            "boss_2": False,
            "boss_3": False,
            "final_boss": False,
        }
        
        EventBus.on(PLAYER_HIT, self._on_player_hit)
        EventBus.on(ACHIEVEMENT_UNLOCKED, self._on_achievement_unlocked)
        self._init_village()
    
    def _get_max_attack_speed_pct(self):
        """计算当前最大攻速百分比（用于成就检查）"""
        if not hasattr(self, "player") or not self.player:
            return 0
        
        base_cd = 0.4  # 基础攻击间隔
        current_cd = self.player._get_attack_cooldown(base_cd)
        speed_pct = int((base_cd / current_cd - 1) * 100)
        return speed_pct

    def _on_player_hit(self, damage=0):
        """受击时触发闪红"""
        self.hit_flash_until = 0.12
    
    def _on_enemy_killed(self, enemy=None):
        """敌人被击杀时更新统计"""
        # 更新连击
        self.current_combo += 1
        self.combo_timer = 2.0  # 2秒内不击杀则连击清零
        if self.current_combo > self.max_combo:
            self.max_combo = self.current_combo
    
    def _on_damage_dealt(self, damage=0):
        """造成伤害时更新统计"""
        self.total_damage += damage
        if damage > self.max_single_damage:
            self.max_single_damage = damage
    
    def _on_reaction_triggered(self, reaction_type=""):
        """触发元素反应时更新统计"""
        self.total_reactions += 1
        if reaction_type == "vaporize":
            self.vaporize_count += 1
        elif reaction_type == "melt":
            self.melt_count += 1
        elif reaction_type == "overload":
            self.overload_count += 1
    
    def _update_combat_stats(self, dt):
        """更新战斗统计（每帧调用）"""
        # 更新连击计时器
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.current_combo = 0
        
        # 更新最大灵石
        if hasattr(self, "player") and self.player:
            if self.player.lingshi > self.max_lingshi:
                self.max_lingshi = self.player.lingshi
            
            # 更新最大饰品数
            acc_count = len(getattr(self.player, "accessories", []))
            if acc_count > self.max_accessories:
                self.max_accessories = acc_count
            
            # 更新最大饰品等级
            for acc, lv in getattr(self.player, "accessories", []):
                if lv > self.max_accessory_level:
                    self.max_accessory_level = lv
            
            # 低血生存时间统计
            if self.player.health > 0 and self.player.health < 10:
                self.low_health_survival_time += dt

    def _on_achievement_unlocked(self, achievement_id="", name=""):
        """成就解锁时显示 Toast"""
        self.achievement_toast_name = name or achievement_id
        self.achievement_toast_until = 2.0
    
    def _heal_partner(self, partner_id):
        """治疗伙伴：首次解锁或羁绊升级"""
        from partner import can_heal_partner, get_partner, get_bond_level
        meta_stats = {
            "kills": meta.total_kills, "levels": meta.total_levels_cleared,
            "wins": meta.total_wins, "element_dmg": meta.total_element_damage, "deaths": meta.total_deaths,
        }
        can, action = can_heal_partner(partner_id, meta.daoyun, meta_stats, meta.partner_bond_levels)
        if not can or not action:
            return
        p = get_partner(partner_id)
        if not p:
            return
        if action == "first":
            meta.daoyun -= p.first_cost
            meta.partner_bond_levels[partner_id] = 1
        else:
            from partner import get_upgrade_cost
            cost = get_upgrade_cost(partner_id, meta.partner_bond_levels.get(partner_id, 1))
            meta.daoyun -= cost
            meta.partner_bond_levels[partner_id] = meta.partner_bond_levels.get(partner_id, 1) + 1
        from achievement import unlock_achievement
        unlock_achievement("heal_partner")
        all_ids = [r[2] for r in PARTNER_ROOMS]
        if all(meta.partner_bond_levels.get(pid, 0) >= 1 for pid in all_ids):
            unlock_achievement("heal_all_partners")
        persist_meta()

    def _init_village(self):
        """初始化村子状态"""
        lg_list = [lg for lg in LINGGEN_LIST if lg.id in meta.unlocked_linggen]
        fb_list = [fb for fb in FABAO_LIST if fb.id in meta.unlocked_fabao]
        self._avail_linggen = lg_list if lg_list else LINGGEN_LIST
        self._avail_fabao = fb_list if fb_list else FABAO_LIST
        self.linggen_choice = 0
        self.fabao_choice = 0  # 当前选中的法宝索引（进入战斗前只选一个）
        self.village_dialogue = None
        # 村子内玩家（可移动，大地图中央出生）
        if self.village_player is None:
            self.village_player = pygame.Rect(VILLAGE_MAP_RECT.centerx - 16, VILLAGE_MAP_RECT.centery - 16, 32, 32)
        else:
            self.village_player.centerx = VILLAGE_MAP_RECT.centerx
            self.village_player.centery = VILLAGE_MAP_RECT.centery

    def _return_to_village(self):
        """从死亡/通关返回村子，重置战斗状态"""
        self.scene = "village"
        self.game_over = False
        self._death_started = False
        self.victory = False
        self._init_village()

    def can_save_run(self) -> bool:
        """当前是否可保存局内进度（村子 / 路线选择 / 商店）"""
        if self.scene == "village":
            return True
        if self.scene == "combat" and (self.game_over or self.victory):
            return False
        if self.scene == "combat" and (self.route_options or self.in_shop or getattr(self, "fabao_reward_pending", False)):
            return True
        if self.scene == "combat" and len(self.enemies) == 0 and not self.route_options and not getattr(self, "fabao_reward_pending", False):
            return False  # 刚清完敌，下一帧才显示 route_options
        return False

    def save_run(self) -> bool:
        """保存局内进度到文件"""
        if not self.can_save_run():
            return False
        vpx = self.village_player.centerx if self.village_player else 0
        vpy = self.village_player.centery if self.village_player else 0
        fid = self._avail_fabao[self.fabao_choice].id if self._avail_fabao and 0 <= self.fabao_choice < len(self._avail_fabao) else ""
        data = RunSaveData(
            scene=self.scene,
            linggen_choice=self.linggen_choice,
            fabao_choice=self.fabao_choice,
            fabao_id=fid,
            village_player_x=vpx,
            village_player_y=vpy,
        )
        if self.scene == "combat" and hasattr(self, "player") and self.player:
            data.run_potions = getattr(self, "run_potions", 0)
            p = self.player
            lg_id = p.linggen.id if p.linggen else "fire"
            fb_ids = [f.id for f in getattr(p, "fabao_list", [])] if getattr(p, "fabao_list", []) else ([p.fabao.id] if p.fabao else ["sword"])
            acc_list = [(a.id, lv) for a, lv in getattr(p, "accessories", [])]
            data.player = PlayerSaveData(
                x=p.rect.centerx, y=p.rect.centery,
                health=p.health, max_health=p.max_health,
                mana=p.mana, max_mana=p.max_mana,
                lingshi=p.lingshi,
                linggen_id=lg_id, fabao_id=fb_ids[0] if fb_ids else "sword",
                fabao_ids=fb_ids, current_fabao_index=getattr(p, "current_fabao_index", 0),
                accessories=acc_list,
                fabao_damage_pct=getattr(p, "fabao_damage_pct", 0),
                fabao_speed_pct=getattr(p, "fabao_speed_pct", 0),
                partner_id=getattr(p, "partner_id", None),
                partner_bond_level=getattr(p, "partner_bond_level", 0),
                partner_charge=getattr(p, "partner_charge", 0),
            )
            data.current_level = self.current_level
            data.kill_count = self.kill_count
            data.demo_mode = getattr(self, "demo_mode", False)
            data.demo_level = getattr(self, "demo_level", 0)
            data.in_shop = getattr(self, "in_shop", False)
            data.shop_daoyun_bought = getattr(self, "_shop_daoyun_bought", False)
            data.shop_fabao_id = getattr(self, "_shop_fabao_id", None)
            data.shop_refresh_remaining = getattr(self, "_shop_refresh_remaining", 1)
            data.shop_shown_fabao_ids = getattr(self, "_shop_shown_fabao_ids", [])
            level_ids = [opt[0] for opt in self.route_options] if self.route_options else []
            if data.in_shop and "shop" not in level_ids:
                level_ids.append("shop")
            data.route_options = level_ids
        return save_run(data)

    def load_run(self, data: RunSaveData) -> bool:
        """从局内存档恢复"""
        self.scene = data.scene
        self._init_village()
        self.linggen_choice = data.linggen_choice
        self.fabao_choice = getattr(data, "fabao_choice", 0)
        fid = getattr(data, "fabao_id", "")
        if fid and self._avail_fabao:
            for i, fb in enumerate(self._avail_fabao):
                if fb.id == fid:
                    self.fabao_choice = i
                    break
        if data.scene == "village":
            vpx = getattr(data, "village_player_x", -1)
            vpy = getattr(data, "village_player_y", -1)
            if vpx >= 0 and vpy >= 0:
                self.village_player.centerx = vpx
                self.village_player.centery = vpy
                self.village_player.clamp_ip(VILLAGE_MAP_RECT)
            return True
        # 恢复战斗状态：路线选择或商店（不增加 total_runs，为续玩）
        self.combat_log.clear()
        self.demo_mode = data.demo_mode
        self.demo_level = data.demo_level
        self.game_over = False
        self._death_started = False
        self.victory = False
        self.kill_count = data.kill_count
        self.current_level = data.current_level
        self.in_shop = data.in_shop
        self.run_potions = getattr(data, "run_potions", 0)
        self._shop_daoyun_bought = getattr(data, "shop_daoyun_bought", False)
        self._shop_fabao_id = getattr(data, "shop_fabao_id", None)
        self._shop_refresh_remaining = getattr(data, "shop_refresh_remaining", 1)
        self._shop_shown_fabao_ids = list(getattr(data, "shop_shown_fabao_ids", []))
        self.route_options = []
        self.enemies = []
        self.projectiles = []
        self.enemy_projectiles = []
        self.aoe_zones = []
        self.spell_zones = []
        self.earth_walls = []
        GameState.get().run_data.kill_count = data.kill_count
        GameState.get().run_data.current_node_index = data.current_level
        if data.player:
            from config import ARENA_X, ARENA_Y, ARENA_W, ARENA_H
            self.player = Player(ARENA_X + ARENA_W // 2, ARENA_Y + ARENA_H // 2)
            
            # 设置 UI 管理器的玩家引用
            if hasattr(self, 'ui_manager'):
                self.ui_manager.set_player(self.player)
            
            p = data.player
            self.player.rect.centerx = p.x
            self.player.rect.centery = p.y
            self.player.health = p.health
            self.player.max_health = p.max_health
            self.player.mana = p.mana
            self.player.max_mana = p.max_mana
            self.player.lingshi = p.lingshi
            self.player.max_health = p.max_health
            self.player.max_mana = p.max_mana
            lg = next((x for x in LINGGEN_LIST if x.id == p.linggen_id), LINGGEN_LIST[0])
            self.player.set_linggen(lg)
            fb_ids = getattr(p, "fabao_ids", []) or [getattr(p, "fabao_id", "sword")]
            fb_list = [next((x for x in FABAO_LIST if x.id == fid), FABAO_LIST[0]) for fid in fb_ids[:2]]
            if len(fb_list) >= 2:
                self.player.set_fabao_pair(fb_list[0], fb_list[1])
                self.player.current_fabao_index = getattr(p, "current_fabao_index", 0) % 2
            elif fb_list:
                self.player.set_fabao(fb_list[0])
            from accessory import get_accessory
            self.player.accessories = []
            for aid, lv in getattr(p, "accessories", []):
                acc = get_accessory(aid)
                if acc:
                    self.player.accessories.append((acc, lv))
            self.player.fabao_damage_pct = getattr(p, "fabao_damage_pct", 0)
            self.player.fabao_speed_pct = getattr(p, "fabao_speed_pct", 0)
            self.player.partner_id = getattr(p, "partner_id", None)
            self.player.partner_bond_level = getattr(p, "partner_bond_level", 0)
            self.player.partner_charge = getattr(p, "partner_charge", 0)
            self.player.partner_charge_max = 100
            GameState.get().set_player(self.player)
            if data.route_options:
                self._restore_route_options(data.route_options)
        return True

    def _restore_route_options(self, level_ids):
        """根据 level_ids 恢复路线选择 UI，恢复时重新抽取奖励类型"""
        from levels import get_node_reward_display
        entrance_h = 60
        if len(level_ids) > 7:
            entrance_w, gap = 65, 12
        elif len(level_ids) > 5:
            entrance_w, gap = 80, 20
        else:
            entrance_w, gap = 90, 25
        total_w = entrance_w * len(level_ids) + gap * (len(level_ids) - 1)
        start_x = ARENA_X + (ARENA_W - total_w) // 2
        start_y = ARENA_Y + 15
        self.route_options = []
        node_types = [get_node_type(level_id) for level_id in level_ids]
        reward_types = assign_combat_rewards_for_options(node_types)
        for i, level_id in enumerate(level_ids):
            x = start_x + i * (entrance_w + gap)
            y = start_y
            rect = pygame.Rect(x, y, entrance_w, entrance_h)
            if self.demo_mode and isinstance(level_id, int) and 0 <= level_id < len(DEMO_NAMES):
                name = f"下一关：{DEMO_NAMES[level_id]}"
            else:
                name = get_node_display_name(level_id)
            reward_type = reward_types[i]
            reward_hint = get_node_reward_display(level_id, reward_type)
            self.route_options.append((level_id, rect, name, reward_type, reward_hint))
    
    def _start_combat(self, demo=False):
        """从村子外出，进入战斗阶段"""
        meta.total_runs += 1
        self.scene = "combat"
        
        # 初始化统计数据
        import time
        self.combat_start_time = time.time()
        self.max_combo = 0
        self.current_combo = 0
        self.combo_timer = 0.0
        self.total_damage = 0
        self.max_single_damage = 0
        self.total_reactions = 0
        self.vaporize_count = 0
        self.melt_count = 0
        self.overload_count = 0
        self.max_lingshi = 0
        self.shop_purchases = 0
        self.potions_used = 0
        self.max_accessories = 0
        self.max_accessory_level = 0
        self.low_health_survival_time = 0.0
        self.boss_defeated_flags = {
            "boss_1": False,
            "boss_2": False,
            "boss_3": False,
            "final_boss": False,
        }
        
        self.player = Player(ARENA_X + ARENA_W // 2, ARENA_Y + ARENA_H // 2)
        
        # 设置 UI 管理器的玩家引用
        if hasattr(self, 'ui_manager'):
            self.ui_manager.set_player(self.player)
        
        self.enemies = []
        self.pending_enemies = []
        self.enemy_spawn_timer = 0.0
        self.enemy_spawn_interval = 0.0
        self.projectiles = []
        self.enemy_projectiles = []
        self.aoe_zones = []
        self.spell_zones = []
        self.earth_walls = []
        if self.particle_mgr is None:
            from particles import ParticleManager
            self.particle_mgr = ParticleManager()
        self.particle_mgr.clear()
        if not hasattr(self, "_reaction_handler") or self._reaction_handler is None:
            from reaction_effects import ReactionEffectHandler
            self._reaction_handler = ReactionEffectHandler(
                lambda: {"enemies": self.enemies, "player": self.player}
            )
        self.demo_mode = demo
        self.demo_level = 0
        self.game_over = False
        self._death_started = False
        self.victory = False
        self.kill_count = 0
        self.current_level = 0
        self.route_options = []
        GameState.get().run_data.kill_count = 0
        GameState.get().run_data.current_node_index = 0
        GameState.get().run_data.lingshi = 0
        GameState.get().set_player(self.player)
        self.prologue_timer = 0
        self.select_linggen = False
        self.in_shop = False
        self.fabao_reward_pending = False
        self.run_potions = min(meta.potion_stock, meta.potion_cap)  # 局内丹药从存量带入，不超过上限
        # 商店状态（新局重置）
        self._shop_daoyun_bought = False
        self._shop_fabao_id = None
        self._shop_refresh_remaining = getattr(meta, "shop_refresh_count", 1)
        self._shop_shown_fabao_ids = []
        self.combat_log.clear()
        EventBus.emit(COMBAT_START, demo=demo)
        # 局外加成（关卡在设定完玩家后加载）
        self.player.max_health = 100 + meta.base_health_bonus
        self.player.health = self.player.max_health
        self.player.max_mana = 100 + meta.base_mana_bonus
        self.player.mana = self.player.max_mana
        
        # 应用局外永久加成
        self.player.apply_meta_bonuses()
        
        # 应用侵蚀度效果（如果已解锁）
        if "erosion_system" in meta.unlocked_features:
            self.player.erosion_level = meta.erosion_level
            self.player.apply_erosion_effects()
        
        # 使用村子内选择的灵根、法宝（进入战斗前只选一个）
        self.player.set_linggen(self._avail_linggen[self.linggen_choice])
        idx = min(self.fabao_choice, len(self._avail_fabao) - 1) if self._avail_fabao else 0
        self.player.set_fabao(self._avail_fabao[idx] if self._avail_fabao else None)
        # 伙伴（手动选择优先，否则带羁绊最高的）
        bond_levels = meta.partner_bond_levels
        sel_id = getattr(meta, "selected_partner_id", None)
        if sel_id and bond_levels.get(sel_id, 0) >= 1:
            best_id, best_lv = sel_id, bond_levels.get(sel_id, 1)
        else:
            best_id, best_lv = None, 0
            for pid in [p[2] for p in PARTNER_ROOMS]:
                lv = bond_levels.get(pid, 0)
                if lv > best_lv:
                    best_lv = lv
                    best_id = pid
        self.player.partner_id = best_id
        self.player.partner_bond_level = best_lv
        self.player.partner_charge = 0
        self.player.partner_charge_max = 100
        # 开局饰品（局外成长）：0=无 1=随机1个 2=二选一 3=三选一
        import random
        from accessory import ACCESSORY_LIST
        start_mode = getattr(meta, "start_accessory_mode", 0)
        unlocked_acc = set(getattr(meta, "unlocked_accessories", ["dmg_s", "mp"]))
        candidates = [a for a in ACCESSORY_LIST if a.id in unlocked_acc]
        if start_mode == 0 or not candidates:
            pass
        elif start_mode == 1:
            self.player.add_accessory(random.choice(candidates), 1)
        elif start_mode >= 2 and len(candidates) >= 1:
            n_pick = start_mode  # 2=二选一, 3=三选一
            opts = random.sample(candidates, min(n_pick, len(candidates)))
            if len(opts) == 1:
                self.player.add_accessory(opts[0], 1)
            elif demo:
                self.player.add_accessory(random.choice(opts), 1)
            else:
                self.start_accessory_pending = True
                self.start_accessory_options = opts
                return  # 不加载关卡，等选完再 _load_level(0)
        if demo:
            self._load_demo()
        else:
            self._load_level(0)

    def _spawn_enemy_tuple(self, enemy_tuple):
        x, y, health, speed, damage, etype, attr, behavior = enemy_tuple
        self.enemies.append(create_enemy(
            etype, x, y,
            behavior=behavior,
            health=health, speed=speed, damage=damage, attr=attr
        ))
    
    def add_run_potions(self, n: int):
        """局内获得丹药（休息关、Boss关、宝箱关调用）"""
        cap = meta.potion_cap
        current = getattr(self, "run_potions", 0)
        self.run_potions = min(current + n, cap)

    def _enter_rest(self, level_id="rest"):
        """休息关：回复生命/灵力，获得丹药，进入路线选择"""
        self.player.health = self.player.max_health
        self.player.mana = self.player.max_mana
        self.add_run_potions(1)
        self.current_level = level_id
        self.player.rect.centerx = ARENA_X + ARENA_W // 2
        self.player.rect.centery = ARENA_Y + ARENA_H // 2
        self._show_route_selection()

    def _enter_rest_point(self):
        """休整点（回复+商店）：仅大段3段末Boss与最终Boss之间"""
        self.player.health = self.player.max_health
        self.player.mana = self.player.max_mana
        self.add_run_potions(2)
        self.current_level = "rest_point"
        self.route_options = []  # 进入商店，清除选路
        self.in_shop = True
        EventBus.emit(SHOP_ENTER)

    def _show_fabao_reward_selection(self):
        """过关法宝奖励：三选一，可选更换主/副法宝"""
        from fabao import FABAO_LIST
        import random
        avail = [fb for fb in FABAO_LIST if fb.id in meta.unlocked_fabao] or FABAO_LIST
        opts = random.sample(avail, min(3, len(avail)))
        self.fabao_reward_pending = True
        self.fabao_reward_options = opts
        self.fabao_reward_selected = None
        self.fabao_reward_replace_step = 0  # 0=选法宝 1=选替换主/副

    def _apply_fabao_reward(self, fb, replace_slot=None):
        """应用选中的法宝：replace_slot=0 替换主，1 替换副，None 则装备为副"""
        if replace_slot is None:
            if self.player.fabao:
                self.player.set_fabao_pair(self.player.fabao, fb)
            else:
                self.player.set_fabao(fb)
        else:
            lst = list(self.player.fabao_list)
            lst[replace_slot] = fb
            self.player.set_fabao_pair(lst[0], lst[1])

    def _grant_accessory_reward(self):
        """过关奖励：随机获得一个已解锁饰品"""
        from accessory import ACCESSORY_LIST
        import random
        acc_list = getattr(self.player, "accessories", [])
        have_ids = {a.id for a, _ in acc_list}
        unlocked = set(getattr(meta, "unlocked_accessories", ["dmg_s", "mp"]))
        slot_cap = getattr(meta, "accessory_slots", 6)
        candidates = [a for a in ACCESSORY_LIST if a.id not in have_ids and a.id in unlocked and len(acc_list) < slot_cap]
        if not candidates:
            self.player.lingshi += LINGSHI_PER_LEVEL
            return
        acc = random.choice(candidates)
        self.player.add_accessory(acc, 1)

    def _enter_treasure(self):
        """宝箱关：奖励力度相同，随机一种物品类型"""
        import random
        reward_type, value = random.choice(TREASURE_REWARDS)
        if reward_type == "potion":
            self.add_run_potions(value)
        elif reward_type == "lingshi":
            self.player.lingshi += value
        self.current_level = "treasure"
        self.player.rect.centerx = ARENA_X + ARENA_W // 2
        self.player.rect.centery = ARENA_Y + ARENA_H // 2
        self._show_route_selection()

    def _enter_event(self, event_node_id):
        """事件关：随机事件，选项二选一，结算后选路"""
        from achievement import unlock_achievement
        unlock_achievement("enter_event")
        from event_events import pick_random_event, apply_event_effect
        from levels import MAJOR_OF
        major_idx = MAJOR_OF.get(str(event_node_id), 0)
        ev_id, text, options = pick_random_event(major_idx)
        self.event_pending = True
        self.event_node_id = event_node_id
        self.event_text = text
        self.event_options = options  # [(选项文本, effect_dict), ...]
        self.event_option_rects = []
        self.current_level = event_node_id
        self.player.rect.centerx = ARENA_X + ARENA_W // 2
        self.player.rect.centery = ARENA_Y + ARENA_H // 2

    def _finish_event(self, option_index: int):
        """选择事件选项后结算，进入选路"""
        from event_events import apply_event_effect
        opt_text, effect = self.event_options[option_index]
        msgs = apply_event_effect(effect, self.player, self.add_run_potions)
        self.event_pending = False
        self.event_node_id = None
        self.event_text = None
        self.event_options = None
        self.event_option_rects = None
        self._show_route_selection()

    def _ensure_shop_state(self):
        """进入商店时确保商品已生成（首次进店或刷新后）"""
        if getattr(self, "_shop_fabao_id", None) is not None:
            return
        from shop import gen_shop_fabao
        fb = gen_shop_fabao(meta.unlocked_fabao, [])
        if fb:
            self._shop_fabao_id = fb.id
            self._shop_shown_fabao_ids = [fb.id]
        else:
            self._shop_fabao_id = None
            self._shop_shown_fabao_ids = []

    def _shop_refresh(self):
        """商店刷新：重新随机法宝，排除已出现过的"""
        from shop import gen_shop_fabao
        shown = set(getattr(self, "_shop_shown_fabao_ids", []))
        fb = gen_shop_fabao(meta.unlocked_fabao, list(shown))
        if fb:
            self._shop_fabao_id = fb.id
            self._shop_shown_fabao_ids = list(shown) + [fb.id]
        else:
            self._shop_fabao_id = None

    def _buy_item(self, item_type, item_id, cost):
        """商店购买：法宝、道韵碎片、刷新、法宝强化、饰品、饰品升级"""
        if self.player.lingshi < cost:
            return
        if item_type == "fabao_buy":
            have_ids = {f.id for f in getattr(self.player, "fabao_list", [])}
            if item_id in have_ids or len(have_ids) >= 2:
                return
        if item_type == "daoyun_fragment":
            if getattr(self, "_shop_daoyun_bought", False):
                return
        if item_type == "refresh":
            if getattr(self, "_shop_refresh_remaining", 0) <= 0:
                return
        if item_type == "accessory":
            from shop import _has_accessory
            if _has_accessory(self.player, item_id):
                return
            if len(self.player.accessories) >= getattr(meta, "accessory_slots", 6):
                return
        if item_type == "upgrade":
            idx = item_id
            if idx < 0 or idx >= len(self.player.accessories):
                return
            acc, lv = self.player.accessories[idx]
            if lv >= acc.max_level:
                return
        if item_type == "fabao":
            _fid, etype, val = item_id
            from shop import get_fabao_upgrade_offer
            offer = get_fabao_upgrade_offer(self.player, etype)
            if offer is None:
                return
            # 价格与步进必须匹配当前档位，防止异常输入绕过上限/成本曲线
            if int(cost) != int(offer["cost"]) or int(val) != int(offer["step"]):
                return
        
        self.player.lingshi -= cost
        self.shop_purchases += 1  # 更新购买次数统计
        
        if item_type == "fabao_buy":
            from fabao import FABAO_LIST
            fb = next((f for f in FABAO_LIST if f.id == item_id), None)
            if fb:
                if self.player.fabao:
                    self.player.set_fabao_pair(self.player.fabao, fb)
                else:
                    self.player.set_fabao(fb)
            self._shop_fabao_id = None  # 买走后清空展示
        elif item_type == "daoyun_fragment":
            meta.daoyun += 1
            persist_meta()
            self._shop_daoyun_bought = True
        elif item_type == "refresh":
            self._shop_refresh_remaining = getattr(self, "_shop_refresh_remaining", 1) - 1
            self._shop_refresh()
        elif item_type == "fabao":
            fid, etype, val = item_id
            if etype == "damage_pct":
                self.player.fabao_damage_pct = min(50, self.player.fabao_damage_pct + val)
            elif etype == "speed_pct":
                self.player.fabao_speed_pct = min(25, self.player.fabao_speed_pct + val)
        elif item_type == "accessory":
            from accessory import get_accessory
            acc = get_accessory(item_id)
            if acc:
                self.player.add_accessory(acc, 1)
        elif item_type == "upgrade":
            self.player.upgrade_accessory(item_id)
        
        # 贫瘠之核：购买物品时额外获得随机饰品
        from accessory_effects import trigger_barren_moderate
        bonus_acc = trigger_barren_moderate(self.player)
        if bonus_acc:
            # 显示提示（可选）
            pass
    
    def _load_level(self, level_index, elite=False):
        """加载关卡，生成固定敌人。选择路线后玩家重置到中心，敌人立即出现。elite=True 时敌人血攻强化"""
        self.enemies.clear()
        self.pending_enemies = []
        self.enemy_spawn_timer = 0.0
        self.enemy_spawn_interval = 0.0
        self.projectiles.clear()
        self.enemy_projectiles.clear()
        self.aoe_zones.clear()
        self.spell_zones.clear()
        self.earth_walls.clear()
        if self.particle_mgr:
            self.particle_mgr.clear()
        self.route_options = []
        # 玩家传送到地图中心
        self.player.rect.centerx = ARENA_X + ARENA_W // 2
        self.player.rect.centery = ARENA_Y + ARENA_H // 2
        # 凶地段（10+）开场保护窗：给玩家读招与走位起手空间
        self.player.opening_grace_timer = 0.75 if isinstance(level_index, int) and level_index >= 10 else 0.0
        level_enemies = get_level_enemies(level_index, elite=elite)
        # 凶地（10+）启用分批出怪，降低开场同屏压脸，保留中后段节奏压力
        if isinstance(level_index, int) and level_index >= 10 and len(level_enemies) >= 4:
            front_count = 2 if len(level_enemies) >= 5 else 1
            for e in level_enemies[:front_count]:
                self._spawn_enemy_tuple(e)
            self.pending_enemies = list(level_enemies[front_count:])
            self.enemy_spawn_interval = 0.68 if level_index <= 12 else 0.58
            self.enemy_spawn_timer = 0.72
        else:
            for e in level_enemies:
                self._spawn_enemy_tuple(e)
        
        # 应用共鸣效果到所有敌人
        for enemy in self.enemies:
            self.resonance_system.apply_to_enemy(enemy)

    def _load_demo(self, demo_level=0):
        """加载演示关卡：一种形式一关，demo_level 0~5。选择路线后玩家重置到中心，敌人立即出现"""
        self.enemies.clear()
        self.pending_enemies = []
        self.enemy_spawn_timer = 0.0
        self.enemy_spawn_interval = 0.0
        self.projectiles.clear()
        self.enemy_projectiles.clear()
        self.aoe_zones.clear()
        self.spell_zones.clear()
        self.earth_walls.clear()
        if self.particle_mgr:
            self.particle_mgr.clear()
        self.route_options = []
        self.demo_mode = True
        self.demo_level = demo_level
        self.player.opening_grace_timer = 0.0
        # 玩家传送到地图中心
        self.player.rect.centerx = ARENA_X + ARENA_W // 2
        self.player.rect.centery = ARENA_Y + ARENA_H // 2
        for x, y, health, speed, damage, etype, attr, behavior in get_demo_enemies(demo_level):
            self.enemies.append(create_enemy(etype, x, y, behavior=behavior, health=health, speed=speed, damage=damage, attr=attr))

    def _load_boss(self, boss_id):
        """加载 Boss 关卡。选择路线后玩家重置到中心，Boss 立即出现"""
        self.enemies.clear()
        self.pending_enemies = []
        self.enemy_spawn_timer = 0.0
        self.enemy_spawn_interval = 0.0
        self.projectiles.clear()
        self.enemy_projectiles.clear()
        self.aoe_zones.clear()
        self.spell_zones.clear()
        self.earth_walls.clear()
        if self.particle_mgr:
            self.particle_mgr.clear()
        self.route_options = []
        self.current_level = boss_id
        self.player.opening_grace_timer = 0.0
        # 玩家传送到地图中心
        self.player.rect.centerx = ARENA_X + ARENA_W // 2
        self.player.rect.centery = ARENA_Y + ARENA_H // 2
        for i, (x, y, health, speed, damage, etype, attr, behavior) in enumerate(get_boss_enemies(boss_id)):
            self.enemies.append(create_enemy(
                etype, x, y,
                behavior=behavior,
                boss_id=boss_id,
                enemy_index=i,
                health=health, speed=speed, damage=damage, attr=attr
            ))
    
    def _show_demo_route_selection(self):
        """演示关卡：清敌后显示下一关或完成"""
        next_levels = DEMO_ROUTE_TREE.get(self.demo_level, [])
        if not next_levels:
            self.scene = "village"
            self._init_village()
            return
        # 只有一个入口：下一关
        next_level = next_levels[0]
        name = DEMO_NAMES[next_level] if next_level < len(DEMO_NAMES) else f"关卡{next_level + 1}"
        entrance_w, entrance_h = 180, 50
        rect = pygame.Rect(ARENA_X + (ARENA_W - entrance_w) // 2, ARENA_Y + 15, entrance_w, entrance_h)
        self.route_options = [(next_level, rect, f"下一关：{name}")]

    def _show_route_selection(self):
        """关卡结束后，在上方显示入口选择。对标 Tiny Rogues：2/3 选，按层数抽样"""
        sampled = RouteSystem.get_next_options(self.current_level, ROUTE_TREE)
        if not sampled:
            self.victory = True
            
            # 应用共鸣道韵倍率
            daoyun_mult = self.resonance_system.get_daoyun_multiplier()
            self._victory_daoyun = int(DAOYUN_VICTORY * daoyun_mult)
            
            # 收集局内统计数据
            import time
            clear_time = int(time.time() - self.combat_start_time) if self.combat_start_time > 0 else 0
            
            # 收集共鸣数据
            resonance_intensity = self.resonance_system.get_total_intensity()
            active_pacts = [f"{pact.type}_{pact.level}" for pact in self.resonance_system.active_pacts]
            
            stats = {
                # 战斗统计
                "max_attack_speed": self._get_max_attack_speed_pct(),
                "max_combo": self.max_combo,
                "total_damage": self.total_damage,
                "max_single_damage": self.max_single_damage,
                "kill_count": self.kill_count,
                
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
                "clear_time": clear_time,
                "potions_used": self.potions_used,
                "low_health_survival": int(self.low_health_survival_time),
                "final_health": self.player.health if hasattr(self, "player") and self.player else 0,
                
                # Boss 击败标记
                "boss_1_defeated": self.boss_defeated_flags.get("boss_1", False),
                "boss_2_defeated": self.boss_defeated_flags.get("boss_2", False),
                "boss_3_defeated": self.boss_defeated_flags.get("boss_3", False),
                "final_boss_defeated": self.boss_defeated_flags.get("final_boss", False),
                
                # 流派统计
                "linggen": self.player.linggen.id if hasattr(self, "player") and self.player and self.player.linggen else "",
                "victory": True,
                
                # 共鸣统计
                "resonance_intensity": resonance_intensity,
                "active_pacts": active_pacts,
                
                # 局外统计
                "total_wins": meta.total_wins,
                "total_kills": meta.total_kills,
                "total_daoyun": meta.daoyun,
                "linggen_unlocked": len(meta.unlocked_linggen),
                "fabao_unlocked": len(meta.unlocked_fabao),
                "partners_healed": len([pid for pid, lv in meta.partner_bond_levels.items() if lv >= 1]),
            }
            
            # 检查成就并解锁功能
            new_achievements = meta.on_win(self._victory_daoyun, stats)
            
            # 显示新解锁的成就
            for ach_id in new_achievements:
                from achievement import get_achievement
                ach = get_achievement(ach_id)
                if ach:
                    EventBus.emit(ACHIEVEMENT_UNLOCKED, achievement_id=ach_id, name=ach["name"])
            
            meta.potion_stock = min(getattr(self, "run_potions", 0), meta.potion_cap)
            persist_meta()
            clear_run_save()  # 局结束，清除局内存档
            from achievement import unlock_achievement
            unlock_achievement("first_victory")
            EventBus.emit(VICTORY, daoyun=self._victory_daoyun)
            return

        options = sampled  # [(level_id, name, node_type, reward_hint, reward_type), ...]

        # 2～3 个传送门入口，均匀分布，携带 reward_type 用于过关发放
        entrance_h = 60
        entrance_w, gap = 100, 30
        total_w = entrance_w * len(options) + gap * (len(options) - 1)
        start_x = ARENA_X + (ARENA_W - total_w) // 2
        start_y = ARENA_Y + 15

        self.route_options = []
        for i, opt in enumerate(options):
            level_id, name, reward_hint, reward_type = opt[0], opt[1], opt[3], (opt[4] if len(opt) > 4 else None)
            x = start_x + i * (entrance_w + gap)
            y = start_y
            rect = pygame.Rect(x, y, entrance_w, entrance_h)
            self.route_options.append((level_id, rect, name, reward_type, reward_hint))
    
    def handle_event(self, event):
        # UI 管理器优先处理事件
        if hasattr(self, 'ui_manager') and self.scene == "combat":
            if self.ui_manager.handle_event(event):
                return  # UI 已处理，不再传递
        
        from ui.input_handler import handle_game_event
        handle_game_event(event, self)
    def update(self, dt):
        if self.achievement_toast_until > 0:
            self.achievement_toast_until = max(0, self.achievement_toast_until - dt)
        if getattr(self, "level_clear_pending", False):
            self.level_clear_timer = max(0, self.level_clear_timer - dt)
            if self.level_clear_timer <= 0:
                self.level_clear_pending = False
                self._show_route_selection()
        if self.scene == "village":
            VillageScene.update_village(dt, self)
            return

        # 更新战斗统计
        if self.scene == "combat":
            self._update_combat_stats(dt)
            
            # 更新 UI 管理器
            if hasattr(self, 'ui_manager') and hasattr(self, 'player'):
                self.ui_manager.update(dt)
        
        CombatSystem.update_combat(dt, self)

    def draw(self):
        if self.scene == "village":
            VillageScene.draw_village_scene(self.screen, self)
            return
        CombatSystem.draw_combat(self.screen, self)
        
        # 绘制新 UI 系统
        if hasattr(self, 'ui_manager') and hasattr(self, 'player'):
            self.ui_manager.draw(self.screen)

    def set_screen(self, screen):
        """主程序切换分辨率后同步新的渲染目标。"""
        self.screen = screen
