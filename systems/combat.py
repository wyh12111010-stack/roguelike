"""战斗系统：战斗更新与绘制逻辑"""

import os

import pygame

from config import (
    ARENA_H,
    ARENA_W,
    ARENA_X,
    ARENA_Y,
    COLOR_ARENA,
    COLOR_ARENA_BORDER,
    COLOR_ENTRANCE,
    COLOR_ENTRANCE_HOVER,
    COLOR_HUD_BORDER,
    COLOR_HUD_HP,
    COLOR_HUD_HP_BG,
    COLOR_HUD_MP,
    COLOR_HUD_MP_BG,
    COLOR_UI,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    get_font,
)
from config_assets import get_scene
from core import EventBus
from core.events import ENEMY_KILLED, LEVEL_CLEAR, NODE_COMPLETE, PLAYER_DEATH, SHOP_ENTER
from levels import DEMO_NAMES, get_level_display, get_node_reward, get_node_type
from meta import meta
from save import clear_run_save, persist_meta
from setting import (
    DAOYUN_BOSS,
    DAOYUN_COMBAT_REWARD,
    DAOYUN_ELITE,
    LINGSHI_ELITE_BONUS,
    LINGSHI_PER_KILL,
    LINGSHI_PER_LEVEL,
)
from story import get_ending


# 场景背景缓存
_scene_bg_cache: dict[str, pygame.Surface | None] = {}


def _load_scene_bg(scene_name: str) -> pygame.Surface | None:
    """加载并缓存场景背景图"""
    if scene_name in _scene_bg_cache:
        return _scene_bg_cache[scene_name]
    try:
        path = get_scene(scene_name)
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            img = pygame.transform.smoothscale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            _scene_bg_cache[scene_name] = img
            return img
    except Exception:
        pass
    _scene_bg_cache[scene_name] = None
    return None


class CombatSystem:
    """战斗系统：更新与绘制逻辑"""

    @staticmethod
    def _trigger_kill_effects(player, enemy):
        """触发击杀时的饰品特殊效果"""
        from accessory_effects import trigger_life_drain, trigger_mana_leech, trigger_swarm_extreme, trigger_swarm_minor

        # 增殖碎片：30%概率额外掉落灵石
        trigger_swarm_minor(player)

        # 生命汲取：击杀回复5%生命
        trigger_life_drain(player)

        # 灵力吸取：击杀回复10灵力
        trigger_mana_leech(player)

        # 增殖之种：击杀敌人时在原地生成毒雾
        game = getattr(player, "_game_ref", None)
        if game:
            trigger_swarm_extreme(player, enemy, game)

    @staticmethod
    def update_combat(dt, game):
        """战斗场景更新逻辑（从 game.update 提取，scene==combat 分支）"""
        # 帧冻结检查：冻结期间只更新视觉效果，跳过游戏逻辑
        if hasattr(game, "hitstop") and game.hitstop.update(dt):
            if game.particle_mgr:
                game.particle_mgr.update(dt)
            if hasattr(game, "damage_text_mgr"):
                game.damage_text_mgr.update(dt)
            if hasattr(game, "screen_shake"):
                game.screen_shake.update(dt)
            return

        game.combat_log.update(dt)
        if game.particle_mgr:
            game.particle_mgr.update(dt)

        # 更新伤害飘字
        if hasattr(game, "damage_text_mgr"):
            game.damage_text_mgr.update(dt)

        # 更新屏幕震动
        if hasattr(game, "screen_shake"):
            game.screen_shake.update(dt)

        if game.game_over or game.victory:
            return

        # 商店内
        if game.in_shop:
            return
        # 过关结算弹窗（等待点击/自动继续）
        if getattr(game, "level_clear_pending", False):
            return
        # 开局饰品三选一（等待选择）
        if getattr(game, "start_accessory_pending", False):
            return
        # 事件选择（等待选择）
        if getattr(game, "event_pending", False):
            return

        # 路线选择模式：只更新玩家移动，检测进入入口
        if game.route_options:
            game.player.update(dt, [], game.projectiles)  # 无敌人
            for opt in game.route_options:
                level_id, rect = opt[0], opt[1]
                reward_type = opt[3] if len(opt) > 3 else None
                if rect.colliderect(game.player.rect):
                    game.current_level_reward_type = reward_type
                    nt = get_node_type(level_id)
                    if nt == "shop":
                        game.in_shop = True
                        EventBus.emit(SHOP_ENTER)
                        game.current_level = level_id
                        game.route_options = [o for o in game.route_options if get_node_type(o[0]) != "shop"]
                    elif game.demo_mode:
                        game.route_options = []
                        game._load_demo(level_id)
                    elif nt == "boss":
                        game.current_level = level_id
                        game.route_options = []
                        game._load_boss(level_id)
                    elif nt == "rest":
                        game.route_options = []
                        game._enter_rest(level_id)
                    elif nt == "rest_point":
                        game.route_options = []
                        game._enter_rest_point()
                    elif nt == "treasure":
                        game.route_options = []
                        game._enter_treasure()
                    elif nt == "event":
                        game.route_options = []
                        game._enter_event(level_id)
                    else:
                        game.current_level = level_id
                        game.route_options = []
                        idx = level_id if isinstance(level_id, int) and level_id >= 0 else 0
                        game._load_level(idx, elite=(nt == "elite"))
                    break
            return

        # 分批出怪（仅战斗关启用）：按间隔补入待出怪队列
        if getattr(game, "pending_enemies", None):
            game.enemy_spawn_timer = max(0.0, getattr(game, "enemy_spawn_timer", 0.0) - dt)
            if game.enemy_spawn_timer <= 0:
                if game.pending_enemies:
                    game._spawn_enemy_tuple(game.pending_enemies.pop(0))
                game.enemy_spawn_timer = max(0.18, getattr(game, "enemy_spawn_interval", 0.0))

        game.player.update(dt, game.enemies, game.projectiles)

        # 更新敌人
        ctx = {"enemies": game.enemies, "enemy_projectiles": game.enemy_projectiles, "aoe_zones": game.aoe_zones}
        for e in game.enemies[:]:
            e.update(dt, game.player, ctx)
            if e.dead:
                EventBus.emit(ENEMY_KILLED, enemy_type=e.enemy_type)
                game.enemies.remove(e)
                game.kill_count += 1
                meta.total_kills += 1
                game.player.lingshi += LINGSHI_PER_KILL

                # 调用游戏统计更新
                game._on_enemy_killed(e)

                # 触发击杀特殊效果
                CombatSystem._trigger_kill_effects(game.player, e)

                from achievement import unlock_achievement

                for aid, thresh in [("kill_10", 10), ("kill_30", 30), ("kill_100", 100)]:
                    if meta.total_kills >= thresh:
                        unlock_achievement(aid)
                from partner_skills import add_partner_charge

                add_partner_charge(game.player, 10)

        # 更新敌人投射物
        for p in game.enemy_projectiles[:]:
            p.update(dt, game.player)
            if p.dead:
                game.enemy_projectiles.remove(p)
            else:
                p.check_hit_player(game.player)

        # 更新土墙（反弹弹道、击退敌人）
        for w in game.earth_walls[:]:
            w.update(dt, game.enemies, game.enemy_projectiles, game.projectiles)
            if w.dead:
                game.earth_walls.remove(w)

        # 更新法术区域（强减速）并作用于敌人
        for z in game.spell_zones[:]:
            z.update(dt)
            if z.dead:
                game.spell_zones.remove(z)
            else:
                z.apply_to_enemies(game.enemies)

        # 更新 AOE 区域
        for z in game.aoe_zones[:]:
            z.update(dt, game.player)
            if z.dead:
                game.aoe_zones.remove(z)

        # 更新玩家弹幕/投射物
        for p in game.projectiles[:]:
            p.update(dt)
            if p.dead:
                game.projectiles.remove(p)
            else:
                p.check_hit(game.enemies)

        # 关卡通关：清空敌人后获得道韵、灵石，显示过关弹窗或路线选择
        if (
            len(game.enemies) == 0
            and len(getattr(game, "pending_enemies", [])) == 0
            and not game.game_over
            and not game.route_options
            and not getattr(game, "level_clear_pending", False)
        ):
            game.projectiles.clear()
            game.enemy_projectiles.clear()
            game.aoe_zones.clear()
            game.spell_zones.clear()
            game.earth_walls.clear()
            if game.demo_mode:
                game._show_demo_route_selection()
                return
            nt = get_node_type(game.current_level)
            daoyun_gain = 0
            if nt == "elite":
                daoyun_gain = DAOYUN_ELITE
            elif isinstance(game.current_level, str) and "boss" in game.current_level:
                bid = game.current_level
                if bid == "final_boss":
                    pass  # victory 分支单独加 DAOYUN_VICTORY
                else:
                    idx = {"segment_boss_1": 0, "segment_boss_2": 1, "segment_boss_3": 2}.get(bid, 0)
                    dao = DAOYUN_BOSS if isinstance(DAOYUN_BOSS, (tuple, list)) else (DAOYUN_ELITE,)
                    daoyun_gain = dao[idx] if idx < len(dao) else DAOYUN_ELITE
                    game.add_run_potions(1)
            meta.daoyun += daoyun_gain
            reward_type = getattr(game, "current_level_reward_type", None) if nt in ("combat", "elite") else None
            if not reward_type:
                reward_type = "lingshi"
            lingshi_gain = 0
            if reward_type == "lingshi":
                lingshi_gain = LINGSHI_PER_LEVEL
                if nt == "elite":
                    lingshi_gain += LINGSHI_ELITE_BONUS
                game.player.lingshi += lingshi_gain
            elif reward_type == "fabao":
                game._show_fabao_reward_selection()
            elif reward_type == "accessory":
                game._grant_accessory_reward()
            elif reward_type == "daoyun":
                meta.daoyun += DAOYUN_COMBAT_REWARD
                daoyun_gain += DAOYUN_COMBAT_REWARD
            else:
                lingshi_gain = LINGSHI_PER_LEVEL
                game.player.lingshi += lingshi_gain
            from core import GameState

            GameState.get().run_data.kill_count = game.kill_count
            GameState.get().run_data.lingshi = game.player.lingshi
            GameState.get().run_data.current_node_index = game.current_level
            meta.total_levels_cleared += 1
            from achievement import unlock_achievement

            for aid, thresh in [("level_5", 5), ("level_10", 10)]:
                if meta.total_levels_cleared >= thresh:
                    unlock_achievement(aid)
            EventBus.emit(LEVEL_CLEAR, lingshi=lingshi_gain, daoyun=daoyun_gain, reward_type=reward_type)
            EventBus.emit(
                NODE_COMPLETE, node_type=nt, node_index=game.current_level, lingshi=lingshi_gain, daoyun=daoyun_gain
            )
            if reward_type != "fabao":
                game.level_clear_pending = True
                game.level_clear_lingshi = lingshi_gain
                game.level_clear_daoyun = daoyun_gain
                game.level_clear_timer = 1.5

        # 检查玩家死亡（死亡动画播完后再 game_over）
        if game.player.health <= 0:
            if not getattr(game, "_death_started", False):
                game._death_started = True
                game._death_anim_timer = 0.0
                game._death_daoyun = 0
                meta.total_deaths += 1
                from achievement import unlock_achievement

                for aid, thresh in [("death_1", 1), ("death_3", 3)]:
                    if meta.total_deaths >= thresh:
                        unlock_achievement(aid)
                meta.potion_stock = min(getattr(game, "run_potions", 0), meta.potion_cap)
                persist_meta()
                clear_run_save()
                EventBus.emit(PLAYER_DEATH, kill_count=game.kill_count, daoyun=game._death_daoyun)
            game._death_anim_timer += dt
            if game._death_anim_timer >= 1.2:  # 死亡动画约 0.67s，留缓冲
                game.game_over = True

    @staticmethod
    def draw_combat(screen, game):
        """战斗场景绘制逻辑（scene==combat 分支）"""
        from config import COLOR_BG

        # 根据节点类型选择场景背景
        node_type = get_node_type(game.current_level) if hasattr(game, "current_level") else "combat"
        if node_type == "boss":
            scene_name = "boss_room"
        elif node_type == "event":
            scene_name = "event"
        else:
            scene_name = "combat_arena"
        bg = _load_scene_bg(scene_name)

        if bg:
            screen.blit(bg, (0, 0))
            # 半透明竞技场覆盖层（让背景不会太亮影响可见度）
            arena_rect = pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
            overlay = pygame.Surface((ARENA_W, ARENA_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80))
            screen.blit(overlay, (ARENA_X, ARENA_Y))
            pygame.draw.rect(screen, COLOR_ARENA_BORDER, arena_rect, 3)
        else:
            screen.fill(COLOR_BG)
            # 绘制战斗框（后备纯色方案）
            arena_rect = pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
            pygame.draw.rect(screen, COLOR_ARENA, arena_rect)
            pygame.draw.rect(screen, COLOR_ARENA_BORDER, arena_rect, 3)

        # 绘制敌人
        for e in game.enemies:
            e.draw(screen)

        # 绘制 AOE 区域
        for z in game.aoe_zones:
            z.draw(screen)

        # 绘制法术区域（水牢、藤蔓）
        for z in game.spell_zones:
            z.draw(screen)

        # 绘制土墙
        for w in game.earth_walls:
            w.draw(screen)

        # 绘制敌人投射物
        for p in game.enemy_projectiles:
            p.draw(screen)

        # 绘制玩家弹幕
        for p in game.projectiles:
            p.draw(screen)

        # 绘制粒子效果
        if game.particle_mgr:
            game.particle_mgr.draw(screen)

        # 绘制商店
        if game.in_shop:
            game._ensure_shop_state()
            CombatSystem._draw_ui(screen, game)
            game.combat_log.draw(screen)
            from shop import draw as draw_shop

            shop_state = {
                "fabao_id": getattr(game, "_shop_fabao_id", None),
                "daoyun_bought": getattr(game, "_shop_daoyun_bought", False),
                "refresh_remaining": getattr(game, "_shop_refresh_remaining", 1),
            }
            draw_shop(
                screen, game.player, game.player.lingshi, shop_state, meta.unlocked_accessories, meta.accessory_slots
            )
            return

        # 开局饰品三选一（外出时）
        if getattr(game, "start_accessory_pending", False):
            CombatSystem._draw_start_accessory_selection(screen, game)
            CombatSystem._draw_ui(screen, game)
            game.combat_log.draw(screen)
            return

        # 法宝奖励选择
        if getattr(game, "fabao_reward_pending", False):
            CombatSystem._draw_fabao_reward_selection(screen, game)
            CombatSystem._draw_ui(screen, game)
            game.combat_log.draw(screen)
            return

        # 事件选择
        if getattr(game, "event_pending", False):
            CombatSystem._draw_event_ui(screen, game)
            CombatSystem._draw_ui(screen, game)
            game.combat_log.draw(screen)
            return

        # 绘制路线选择入口
        if game.route_options:
            CombatSystem._draw_route_selection(screen, game)

        # 绘制玩家
        game.player.draw(screen)

        # UI
        CombatSystem._draw_ui(screen, game)
        game.combat_log.draw(screen)

        # 伤害飘字
        if hasattr(game, "damage_text_mgr"):
            game.damage_text_mgr.draw(screen)

        # 人物页面（C 打开，ESC 关闭）
        if getattr(game, "char_panel_open", False):
            CombatSystem._draw_char_panel(screen, game)
        # 过关结算弹窗
        if getattr(game, "level_clear_pending", False):
            CombatSystem._draw_level_clear_popup(screen, game)
        # 成就解锁 Toast
        if game.achievement_toast_until > 0:
            CombatSystem._draw_achievement_toast(screen, game)

        if game.game_over:
            CombatSystem._draw_game_over(screen, game)
        elif game.victory:
            CombatSystem._draw_victory(screen, game)
        # 受击闪红（修真风格：朱红闪，区别于 TR 的纯白闪）
        if game.hit_flash_until > 0:
            alpha = int(min(1.0, game.hit_flash_until / 0.04) * 120)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(alpha)
            overlay.fill((180, 50, 40))
            screen.blit(overlay, (0, 0))

        # 屏幕震动：最后一步，scroll 整个画面
        if hasattr(game, "screen_shake") and game.screen_shake.is_shaking():
            ox, oy = game.screen_shake.get_offset()
            if ox != 0 or oy != 0:
                screen.scroll(ox, oy)

    @staticmethod
    def _draw_ui(screen, game):
        font = get_font(24)
        font_small = get_font(18)
        # 左侧信息（道韵、灵石、丹药、当前关）
        daoyun_text = font.render(f"道韵: {meta.daoyun}", True, (180, 160, 100))
        lingshi_text = font.render(f"灵石: {game.player.lingshi}", True, (150, 200, 150))
        run_p = getattr(game, "run_potions", 0)
        potion_text = font.render(f"丹药: {run_p} [R]", True, (200, 150, 150))
        level_name = f"演示-{DEMO_NAMES[game.demo_level]}" if game.demo_mode else get_level_display(game.current_level)
        level_text = font.render(f"当前: {level_name}", True, COLOR_UI)
        remaining = len(game.enemies) + len(getattr(game, "pending_enemies", []))
        remain_text = font.render(
            f"剩余敌人: {remaining}" if not game.route_options else "选择路线 [1-3]",
            True,
            (100, 255, 150) if game.demo_mode else COLOR_UI,
        )
        screen.blit(daoyun_text, (10, 10))
        screen.blit(lingshi_text, (10, 30))
        screen.blit(potion_text, (10, 50))
        screen.blit(level_text, (10, 75))
        screen.blit(remain_text, (10, 100))
        grace = getattr(game.player, "opening_grace_timer", 0.0)
        if grace > 0:
            grace_text = font_small.render(f"开场护体: {grace:.1f}s", True, (230, 210, 130))
            screen.blit(grace_text, (10, 145))
        c_hint = font_small.render("[C] 人物  [Shift] 冲刺", True, (120, 120, 130))
        screen.blit(c_hint, (10, 165 if grace > 0 else 125))
        # 伙伴充能条（有伙伴时显示）
        pid = getattr(game.player, "partner_id", None)
        if pid:
            from partner import get_partner

            p = get_partner(pid)
            if p:
                blv = getattr(game.player, "partner_bond_level", 0)
                charge = getattr(game.player, "partner_charge", 0)
                charge_max = getattr(game.player, "partner_charge_max", 100)
                pct = min(1.0, charge / charge_max) if charge_max else 0
                bar_w, bar_h = 120, 8
                pygame.draw.rect(screen, (40, 40, 50), (10, 155, bar_w, bar_h))
                pygame.draw.rect(screen, (120, 200, 255), (10, 155, int(bar_w * pct), bar_h))
                partner_txt = font_small.render(f"{p.name} Lv{blv} [F]", True, (150, 200, 255))
                screen.blit(partner_txt, (10, 165))

        # 底部 HUD 条（修真风格：血条/灵力条并排，对标 TR 底部布局，朱红/青灵+金铜描边）
        bar_w, bar_h = 200, 14
        gap = 16
        pad_bottom = 20
        y = SCREEN_HEIGHT - pad_bottom - bar_h
        total_w = bar_w * 2 + gap
        x1 = (SCREEN_WIDTH - total_w) // 2
        x2 = x1 + bar_w + gap
        # 血条（左）
        hp_pct = game.player.health / game.player.max_health if game.player.max_health else 0
        hp_color = COLOR_HUD_HP
        pygame.draw.rect(screen, COLOR_HUD_HP_BG, (x1, y, bar_w, bar_h))
        pygame.draw.rect(screen, hp_color, (x1, y, int(bar_w * hp_pct), bar_h))
        pygame.draw.rect(screen, COLOR_HUD_BORDER, (x1, y, bar_w, bar_h), 1)
        hp_label = font_small.render("生命", True, (220, 200, 180))
        screen.blit(hp_label, (x1, y - 16))
        # 灵力条（右）
        mp_pct = game.player.mana / game.player.max_mana if game.player.max_mana else 0
        pygame.draw.rect(screen, COLOR_HUD_MP_BG, (x2, y, bar_w, bar_h))
        pygame.draw.rect(screen, COLOR_HUD_MP, (x2, y, int(bar_w * mp_pct), bar_h))
        pygame.draw.rect(screen, COLOR_HUD_BORDER, (x2, y, bar_w, bar_h), 1)
        mp_label = font_small.render("灵力", True, (180, 210, 240))
        screen.blit(mp_label, (x2, y - 16))

        # 技能 CD 条（有法宝法术时显示）
        fb = game.player.fabao
        if fb and fb.spell_id and fb.spell_cooldown > 0:
            cd_remain = game.player.spell_cooldowns.get(fb.spell_id, 0)
            cd_max = fb.spell_cooldown
            cd_pct = 1 - (cd_remain / cd_max) if cd_max else 1  # 就绪时满
            bar_w, bar_h = 120, 8
            cd_x = x1
            cd_y = y + bar_h + 20
            pygame.draw.rect(screen, (40, 45, 55), (cd_x, cd_y, bar_w, bar_h))
            pygame.draw.rect(
                screen, (80, 140, 200) if cd_remain <= 0 else (90, 90, 100), (cd_x, cd_y, int(bar_w * cd_pct), bar_h)
            )
            pygame.draw.rect(screen, COLOR_HUD_BORDER, (cd_x, cd_y, bar_w, bar_h), 1)
            cd_label = "就绪" if cd_remain <= 0 else f"{cd_remain:.1f}s"
            cd_txt = font_small.render(f"E {cd_label}", True, (160, 190, 220))
            screen.blit(cd_txt, (cd_x, cd_y - 14))

        # 连击计数器（右上角）
        tracker = getattr(game, "stats_tracker", None)
        if tracker:
            combo = getattr(tracker, "current_combo", 0)
            if combo >= 2:
                # 字号随连击数增大
                combo_size = min(48, 24 + combo * 2)
                combo_font = get_font(combo_size)
                # 颜色随连击数变化
                if combo >= 20:
                    combo_color = (255, 80, 80)  # 红色
                elif combo >= 10:
                    combo_color = (255, 180, 50)  # 橙色
                elif combo >= 5:
                    combo_color = (255, 255, 80)  # 黄色
                else:
                    combo_color = (200, 200, 200)  # 白色
                combo_txt = combo_font.render(f"{combo} HIT", True, combo_color)
                cx = SCREEN_WIDTH - combo_txt.get_width() - 20
                cy = 20
                # 背景
                bg = pygame.Surface((combo_txt.get_width() + 12, combo_txt.get_height() + 4), pygame.SRCALPHA)
                bg.fill((0, 0, 0, 100))
                screen.blit(bg, (cx - 6, cy - 2))
                screen.blit(combo_txt, (cx, cy))
                # 最大连击（小字）
                max_combo = getattr(tracker, "max_combo", 0)
                if max_combo > combo:
                    mc_txt = font_small.render(f"MAX {max_combo}", True, (140, 140, 140))
                    screen.blit(mc_txt, (cx, cy + combo_txt.get_height() + 2))

    @staticmethod
    def _draw_char_panel(screen, game):
        """人物页面：灵根、法宝、饰品"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((25, 28, 40))
        screen.blit(overlay, (0, 0))

        font = get_font(24)
        font_small = get_font(18)
        title = font.render("人物", True, (220, 200, 150))
        t_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title, t_rect)

        hint = font_small.render("ESC 或 C 关闭", True, (140, 140, 140))
        h_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        screen.blit(hint, h_rect)

        # 内容区域（居中偏上）
        cx = SCREEN_WIDTH // 2
        y = 100
        line_h = 32
        lg = game.player.linggen
        lg_text = font.render(f"灵根: {lg.name}" if lg else "灵根: -", True, COLOR_UI)
        screen.blit(lg_text, (cx - lg_text.get_width() // 2, y))
        y += line_h

        fb_list = getattr(game.player, "fabao_list", [])
        fb = game.player.fabao
        if len(fb_list) >= 2:
            other = fb_list[1 - game.player.current_fabao_index]
            fb_text = font.render(f"法宝: {fb.name} / {other.name} [Q切换 E法术]", True, COLOR_UI)
        else:
            fb_text = font.render(f"法宝: {fb.name} [E法术]" if fb else "法宝: -", True, COLOR_UI)
        screen.blit(fb_text, (cx - fb_text.get_width() // 2, y))
        y += line_h

        acc_list = getattr(game.player, "accessories", [])
        acc_str = "、".join(f"{a.name} Lv{lv}" for a, lv in acc_list) if acc_list else "-"
        acc_text = font_small.render(f"饰品: {acc_str}", True, (160, 180, 200))
        screen.blit(acc_text, (cx - acc_text.get_width() // 2, y))

    @staticmethod
    def _draw_level_clear_popup(screen, game):
        """过关结算弹窗"""
        w, h = 320, 140
        x = (SCREEN_WIDTH - w) // 2
        y = (SCREEN_HEIGHT - h) // 2
        overlay = pygame.Surface((w, h))
        overlay.set_alpha(230)
        overlay.fill((30, 32, 45))
        screen.blit(overlay, (x, y))
        pygame.draw.rect(screen, COLOR_HUD_BORDER, (x, y, w, h), 2)

        font = get_font(24)
        font_small = get_font(18)
        title = font.render("过关", True, (220, 200, 150))
        screen.blit(title, (x + (w - title.get_width()) // 2, y + 20))
        lines = []
        lingshi = getattr(game, "level_clear_lingshi", 0)
        daoyun = getattr(game, "level_clear_daoyun", 0)
        if lingshi > 0:
            lines.append(f"+{lingshi} 灵石")
        if daoyun > 0:
            lines.append(f"+{daoyun} 道韵")
        if not lines:
            lines.append("继续前进")
        text = font_small.render("  ".join(lines), True, (180, 200, 180))
        screen.blit(text, (x + (w - text.get_width()) // 2, y + 60))
        hint = font_small.render("点击或按键继续", True, (140, 140, 140))
        screen.blit(hint, (x + (w - hint.get_width()) // 2, y + h - 35))

    @staticmethod
    def _draw_achievement_toast(screen, game):
        """成就解锁 Toast"""
        if not game.achievement_toast_name:
            return
        font = get_font(20)
        text = font.render(f"解锁成就：{game.achievement_toast_name}", True, (220, 200, 120))
        tw, th = text.get_width() + 24, 40
        x = (SCREEN_WIDTH - tw) // 2
        y = 80
        alpha = int(game.achievement_toast_until / 0.5 * 255) if game.achievement_toast_until < 0.5 else 255
        surf = pygame.Surface((tw, th))
        surf.set_alpha(alpha)
        surf.fill((40, 38, 50))
        screen.blit(surf, (x, y))
        pygame.draw.rect(screen, COLOR_HUD_BORDER, (x, y, tw, th), 1)
        screen.blit(text, (x + (tw - text.get_width()) // 2, y + (th - text.get_height()) // 2))

    @staticmethod
    def _draw_game_over(screen, game):
        ending = get_ending("death")
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        font = get_font(48)
        text = font.render(ending["title"], True, (255, 100, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(text, rect)

        font_small = get_font(24)
        desc = font_small.render(ending["text"], True, COLOR_UI)
        d_rect = desc.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(desc, d_rect)

        kill_count = getattr(game, "kill_count", 0)
        daoyun = getattr(game, "_death_daoyun", 0)
        stats_text = f"击杀 {kill_count} 敌人" + (f" · 获得 {daoyun} 道韵" if daoyun > 0 else "")
        stats = font_small.render(stats_text, True, (180, 160, 100))
        s_rect = stats.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(stats, s_rect)

        game._back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30, 200, 50)
        mx, my = pygame.mouse.get_pos()
        is_hover = game._back_rect.collidepoint(mx, my)
        color = COLOR_ENTRANCE_HOVER if is_hover else COLOR_ENTRANCE
        pygame.draw.rect(screen, color, game._back_rect)
        pygame.draw.rect(screen, COLOR_UI, game._back_rect, 2)
        restart = font_small.render("回村子 (R)", True, (255, 255, 255))
        r_rect = restart.get_rect(center=game._back_rect.center)
        screen.blit(restart, r_rect)

    @staticmethod
    def _draw_fabao_reward_selection(screen, game):
        """过关法宝奖励：三选一，双法宝时可选替换主/副"""
        from attribute import ATTR_COLORS

        """过关法宝奖励：三选一，双法宝时可选替换主/副"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((25, 30, 45))
        screen.blit(overlay, (0, 0))

        font = get_font(28)
        font_small = get_font(20)
        replace_step = getattr(game, "fabao_reward_replace_step", 0)

        if replace_step == 0:
            title = font.render("选择法宝", True, (220, 200, 150))
            opts = getattr(game, "fabao_reward_options", [])
        else:
            title = font.render("替换主法宝还是副法宝？", True, (220, 200, 150))
            opts = []

        t_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, t_rect)

        game.fabao_reward_rects = []
        game.fabao_reward_replace_rects = []

        if replace_step == 0:
            n = len(opts)
            item_r = 40
            gap = 25
            total_w = n * (item_r * 2) + (n - 1) * gap
            start_x = (SCREEN_WIDTH - total_w) // 2 + item_r
            cy = SCREEN_HEIGHT // 2
            for i, fb in enumerate(opts):
                cx = start_x + i * (item_r * 2 + gap)
                rect = pygame.Rect(cx - item_r, cy - item_r, item_r * 2, item_r * 2)
                game.fabao_reward_rects.append((rect, fb))
                pygame.draw.circle(screen, (80, 100, 140), (cx, cy), item_r)
                pygame.draw.circle(screen, (150, 170, 220), (cx, cy), item_r, 2)
                c = ATTR_COLORS.get(fb.attr, (200, 200, 200))
                txt = font_small.render(fb.name, True, c)
                t_rect = txt.get_rect(center=(cx, cy))
                screen.blit(txt, t_rect)
            hint = font_small.render("1/2/3 键或点击选择", True, (160, 160, 160))
        else:
            btn_w, btn_h = 140, 45
            gap = 30
            y = SCREEN_HEIGHT // 2 - 30
            r1 = pygame.Rect(SCREEN_WIDTH // 2 - btn_w - gap // 2, y, btn_w, btn_h)
            r2 = pygame.Rect(SCREEN_WIDTH // 2 + gap // 2, y, btn_w, btn_h)
            game.fabao_reward_replace_rects = [(r1, 0), (r2, 1)]
            for rect, slot in game.fabao_reward_replace_rects:
                pygame.draw.rect(screen, (70, 100, 130), rect)
                pygame.draw.rect(screen, (140, 170, 210), rect, 2)
                lbl = "替换主法宝" if slot == 0 else "替换副法宝"
                txt = font_small.render(lbl, True, (255, 255, 255))
                t_rect = txt.get_rect(center=rect.center)
                screen.blit(txt, t_rect)
            hint = font_small.render("1=替换主 2=替换副  或点击按钮", True, (160, 160, 160))

        h_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(hint, h_rect)

    @staticmethod
    def _draw_event_ui(screen, game):
        """事件选择：文本 + 选项按钮"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((30, 35, 50))
        screen.blit(overlay, (0, 0))

        font = get_font(24)
        font_small = get_font(18)
        title = font.render("奇遇", True, (220, 200, 150))
        t_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 70))
        screen.blit(title, t_rect)

        text = getattr(game, "event_text", "")
        lines = text.split("。") if text else []
        if lines and not lines[-1].strip():
            lines.pop()
        y = 120
        for line in lines:
            if line.strip():
                txt = font_small.render(line.strip() + ("。" if not line.endswith("。") else ""), True, (200, 200, 200))
                screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, y))
                y += 28

        opts = getattr(game, "event_options", [])
        game.event_option_rects = []
        btn_w, btn_h = 320, 44
        gap = 20
        start_y = SCREEN_HEIGHT // 2 - 20
        for i, (opt_text, _) in enumerate(opts):
            rect = pygame.Rect(SCREEN_WIDTH // 2 - btn_w // 2, start_y + i * (btn_h + gap), btn_w, btn_h)
            game.event_option_rects.append(rect)
            mx, my = pygame.mouse.get_pos()
            is_hover = rect.collidepoint(mx, my)
            color = (100, 140, 180) if is_hover else (70, 100, 130)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (140, 170, 210), rect, 2)
            lbl = font_small.render(opt_text, True, (255, 255, 255))
            l_rect = lbl.get_rect(center=rect.center)
            screen.blit(lbl, l_rect)

        hint = font_small.render("1/2 键或点击选择", True, (160, 160, 160))
        h_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(hint, h_rect)

    @staticmethod
    def _draw_start_accessory_selection(screen, game):
        """开局饰品三选一"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((25, 30, 45))
        screen.blit(overlay, (0, 0))
        font = get_font(28)
        font_small = get_font(20)
        title = font.render("选择开局饰品", True, (220, 200, 150))
        t_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, t_rect)
        opts = getattr(game, "start_accessory_options", [])
        game.start_accessory_rects = []
        n = len(opts)
        if n == 0:
            return
        item_w, item_h = 140, 60
        gap = 25
        total_w = n * item_w + (n - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        cy = SCREEN_HEIGHT // 2
        for i, acc in enumerate(opts):
            x = start_x + i * (item_w + gap)
            rect = pygame.Rect(x, cy - item_h // 2, item_w, item_h)
            game.start_accessory_rects.append((rect, acc))
            is_hover = rect.collidepoint(pygame.mouse.get_pos())
            c = (90, 120, 150) if is_hover else (60, 80, 100)
            pygame.draw.rect(screen, c, rect)
            pygame.draw.rect(screen, (150, 170, 200), rect, 2)
            txt = font_small.render(acc.name, True, (255, 255, 255))
            screen.blit(txt, (rect.x + (rect.w - txt.get_width()) // 2, rect.y + 8))
            desc = font_small.render(acc.desc, True, (180, 180, 180))
            screen.blit(desc, (rect.x + (rect.w - desc.get_width()) // 2, rect.y + 32))
        n = len(opts)
        key_hint = "/".join(str(i + 1) for i in range(n)) + " 键或点击选择"
        hint = font_small.render(key_hint, True, (160, 160, 160))
        h_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(hint, h_rect)

    @staticmethod
    def _draw_route_selection(screen, game):
        """绘制传送门样式的路线入口，奖励倾向由选路时抽取（对标星座战士）"""
        from village import PORTAL_COLOR, PORTAL_HOVER, draw_portal

        font = get_font(20)
        for i, opt in enumerate(game.route_options):
            level_id, rect, name = opt[0], opt[1], opt[2]
            opt[3] if len(opt) > 3 else None
            reward_hint = opt[4] if len(opt) > 4 else None
            is_hover = rect.colliderect(game.player.rect)
            nt = get_node_type(level_id)
            if nt == "shop":
                c, h = (70, 140, 90), (120, 220, 150)
            elif nt == "rest":
                c, h = (70, 140, 120), (120, 200, 180)
            elif nt == "treasure":
                c, h = (140, 120, 60), (220, 190, 100)
            elif nt == "boss":
                c, h = (140, 60, 80), (200, 90, 110)
            elif nt == "rest_point":
                c, h = (90, 150, 100), (140, 220, 150)
            elif nt == "elite":
                c, h = (120, 80, 140), (180, 120, 200)
            elif nt == "event":
                c, h = (100, 120, 160), (150, 180, 220)
            else:
                c, h = PORTAL_COLOR, PORTAL_HOVER
            sublabel = reward_hint if reward_hint else get_node_reward(level_id)
            draw_portal(screen, rect, f"{i + 1}.{name}", c, h, is_hover, sublabel=sublabel)

        hint = font.render("走向传送门选择路线 或 按 1-3 键", True, (180, 180, 180))
        screen.blit(hint, (ARENA_X, ARENA_Y + ARENA_H - 25))

    @staticmethod
    def _draw_victory(screen, game):
        ending = get_ending("victory")
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 50, 0))
        screen.blit(overlay, (0, 0))

        font = get_font(48)
        text = font.render(ending["title"], True, (100, 255, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(text, rect)

        font_small = get_font(24)
        desc = font_small.render(ending["text"], True, COLOR_UI)
        d_rect = desc.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(desc, d_rect)

        daoyun = getattr(game, "_victory_daoyun", 0)
        stats = font_small.render(f"获得 {daoyun} 道韵", True, (180, 220, 120))
        s_rect = stats.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(stats, s_rect)

        game._back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30, 200, 50)
        mx, my = pygame.mouse.get_pos()
        is_hover = game._back_rect.collidepoint(mx, my)
        color = COLOR_ENTRANCE_HOVER if is_hover else COLOR_ENTRANCE
        pygame.draw.rect(screen, color, game._back_rect)
        pygame.draw.rect(screen, COLOR_UI, game._back_rect, 2)
        restart = font_small.render("回村子 (R)", True, (255, 255, 255))
        r_rect = restart.get_rect(center=game._back_rect.center)
        screen.blit(restart, r_rect)
