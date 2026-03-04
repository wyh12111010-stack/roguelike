"""输入处理：村子/战斗场景的键盘与鼠标事件"""
import pygame

from core.events import SHOP_ENTER
from levels import get_node_type
from meta import meta
from save import persist_meta, clear_run_save
from setting import POTION_HEAL_PCT
from village import VILLAGE_UI
from controls import action_down


def handle_game_event(event, game):
    """处理游戏输入，game 为 Game 实例。无返回值。"""
    # 村子场景：对话时点击/空格关闭，否则点击选择
    if game.scene == "village":
        _handle_village_event(event, game)
        return

    if getattr(game, "level_clear_pending", False):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            game.level_clear_pending = False
            game._show_route_selection()
            return
        if event.type == pygame.KEYDOWN:
            game.level_clear_pending = False
            game._show_route_selection()
            return

    if game.game_over or game.victory:
        bindings = getattr(meta, "keybinds", {})
        if action_down(event, bindings, "return_village"):
            game._return_to_village()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(game, "_back_rect") and game._back_rect.collidepoint(event.pos):
                game._return_to_village()
        return

    # 开局饰品二选一/三选一
    if getattr(game, "start_accessory_pending", False):
        if _handle_start_accessory_event(event, game):
            return

    # 事件选择
    if getattr(game, "event_pending", False):
        if _handle_event_pending(event, game):
            return

    # 法宝奖励选择
    if getattr(game, "fabao_reward_pending", False):
        if _handle_fabao_reward_event(event, game):
            return

    # 路线选择时，按 1/2/3/4 快速选择
    if game.route_options and not game.in_shop and not getattr(game, "fabao_reward_pending", False):
        if _handle_route_key_event(event, game):
            return

    # 商店内
    if game.in_shop:
        if _handle_shop_event(event, game):
            return
    if getattr(game, "char_panel_open", False) and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        game.char_panel_open = False
        return

    # 战斗快捷键
    if event.type == pygame.KEYDOWN:
        _handle_combat_keys(event, game)


def _handle_village_event(event, game):
    """村子场景事件"""
    # 共鸣面板打开时，处理面板内的点击
    if game.resonance_panel_open:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 确认按钮
            if VILLAGE_UI.get("resonance_confirm_rect") and VILLAGE_UI["resonance_confirm_rect"].collidepoint(event.pos):
                game.resonance_panel_open = False
                return
            
            # 取消按钮
            if VILLAGE_UI.get("resonance_cancel_rect") and VILLAGE_UI["resonance_cancel_rect"].collidepoint(event.pos):
                game.resonance_panel_open = False
                return
            
            # 共鸣选项
            for rect, pact in VILLAGE_UI.get("resonance_panel_rects", []):
                if rect.collidepoint(event.pos):
                    game.resonance_system.add_pact(pact)
                    return
        
        # ESC 键关闭面板
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            game.resonance_panel_open = False
            return
        
        return  # 面板打开时不处理其他点击
    
    # 共鸣设置按钮
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if VILLAGE_UI.get("resonance_button_rect") and VILLAGE_UI["resonance_button_rect"].collidepoint(event.pos):
            game.resonance_panel_open = True
            return
    
    if game.village_dialogue:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            game.village_dialogue = None
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game.village_dialogue = None
            return
    for rect, zone in VILLAGE_UI.get("dialogue_rects", []):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and rect.collidepoint(event.pos):
            game.village_dialogue = zone
            return
    for rect, action in VILLAGE_UI.get("center_rects", []):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and rect.collidepoint(event.pos):
            game.village_dialogue = "qixia" if action == "dialogue" else "achievement"
            return
    for rect, partner_id, action in VILLAGE_UI.get("partner_rects", []):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and rect.collidepoint(event.pos):
            if action == "heal":
                game._heal_partner(partner_id)
            elif action == "select":
                meta.selected_partner_id = partner_id if meta.selected_partner_id != partner_id else None
                persist_meta()
            else:
                # 检查特殊对话
                from partner import get_resonance_dialogue
                resonance_intensity = game.resonance_system.get_total_intensity()
                special_dialogue = get_resonance_dialogue(partner_id, resonance_intensity)
                if special_dialogue:
                    game.village_dialogue = f"{partner_id}_resonance"
                    game.village_dialogue_text = special_dialogue
                else:
                    game.village_dialogue = partner_id
            return
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mx, my = event.pos
        for i, (rect, _) in enumerate(VILLAGE_UI.get("linggen_rects", [])):
            if rect.collidepoint(mx, my):
                game.linggen_choice = i
                return
        for i, (rect, _) in enumerate(VILLAGE_UI.get("fabao_rects", [])):
            if rect.collidepoint(mx, my):
                game.fabao_choice = i
                return
        for rect, gtype, cost in VILLAGE_UI.get("growth_rects", []):
            if rect.collidepoint(mx, my) and meta.daoyun >= cost:
                _apply_growth(game, gtype, cost)
                return
        for rect, item_id, item_type, cost in VILLAGE_UI.get("unlock_rects", []):
            if rect.collidepoint(mx, my) and meta.daoyun >= cost:
                _apply_unlock(game, item_id, item_type, cost)
                return
        if VILLAGE_UI.get("new_game_rect") and VILLAGE_UI["new_game_rect"].collidepoint(mx, my):
            clear_run_save()
            game._init_village()
            return


def _apply_growth(game, gtype, cost):
    if gtype == "health":
        meta.daoyun -= cost
        meta.base_health_bonus += 10
    elif gtype == "mana":
        meta.daoyun -= cost
        meta.base_mana_bonus += 10
    elif gtype == "potion_cap" and meta.potion_cap < 4:
        meta.daoyun -= cost
        meta.potion_cap += 1
        meta.potion_stock = meta.potion_cap
    elif gtype == "accessory_slot" and meta.accessory_slots < 9:
        meta.daoyun -= cost
        meta.accessory_slots += 1
    elif gtype == "shop_refresh" and meta.shop_refresh_count < 3:
        meta.daoyun -= cost
        meta.shop_refresh_count += 1
    elif gtype == "start_accessory" and meta.start_accessory_mode < 3:
        meta.daoyun -= cost
        meta.start_accessory_mode += 1
    else:
        return
    persist_meta()


def _apply_unlock(game, item_id, item_type, cost):
    from achievement import unlock_achievement
    if item_type == "linggen" and item_id not in meta.unlocked_linggen:
        meta.daoyun -= cost
        meta.unlocked_linggen.append(item_id)
        unlock_achievement("unlock_linggen")
        game._init_village()
    elif item_type == "fabao" and item_id not in meta.unlocked_fabao:
        meta.daoyun -= cost
        meta.unlocked_fabao.append(item_id)
        unlock_achievement("unlock_fabao")
        game._init_village()
    elif item_type == "accessory" and item_id not in meta.unlocked_accessories:
        meta.daoyun -= cost
        meta.unlocked_accessories.append(item_id)
        game._init_village()
    else:
        return
    persist_meta()


def _handle_start_accessory_event(event, game):
    opts = getattr(game, "start_accessory_options", [])
    rects = getattr(game, "start_accessory_rects", [])
    if event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_9:
        idx = event.key - pygame.K_1
        if 0 <= idx < len(opts):
            game.player.add_accessory(opts[idx], 1)
            game.start_accessory_pending = False
            game._load_level(0)
            return True
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for rect, acc in rects:
            if rect.collidepoint(event.pos):
                game.player.add_accessory(acc, 1)
                game.start_accessory_pending = False
                game._load_level(0)
                return True
    return False


def _handle_event_pending(event, game):
    if event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_9:
        idx = event.key - pygame.K_1
        if 0 <= idx < len(getattr(game, "event_options", [])):
            game._finish_event(idx)
            return True
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for i, rect in enumerate(getattr(game, "event_option_rects", [])):
            if rect.collidepoint(event.pos):
                game._finish_event(i)
                return True
    return False


def _handle_fabao_reward_event(event, game):
    if event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_3 and getattr(game, "fabao_reward_replace_step", 0) == 0:
        idx = event.key - pygame.K_1
        opts = getattr(game, "fabao_reward_options", [])
        if idx < len(opts):
            fb = opts[idx]
            game.fabao_reward_selected = fb
            if len(game.player.fabao_list) >= 2:
                game.fabao_reward_replace_step = 1
            else:
                game._apply_fabao_reward(fb, replace_slot=None)
                game.fabao_reward_pending = False
                game._show_route_selection()
            return True
    if event.type == pygame.KEYDOWN and getattr(game, "fabao_reward_replace_step", 0) == 1:
        if event.key == pygame.K_1:
            game._apply_fabao_reward(game.fabao_reward_selected, replace_slot=0)
            game.fabao_reward_pending = False
            game._show_route_selection()
            return True
        elif event.key == pygame.K_2:
            game._apply_fabao_reward(game.fabao_reward_selected, replace_slot=1)
            game.fabao_reward_pending = False
            game._show_route_selection()
            return True
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        replace_step = getattr(game, "fabao_reward_replace_step", 0)
        if replace_step == 0:
            for rect, fb in getattr(game, "fabao_reward_rects", []):
                if rect.collidepoint(event.pos):
                    game.fabao_reward_selected = fb
                    if len(game.player.fabao_list) >= 2:
                        game.fabao_reward_replace_step = 1
                    else:
                        game._apply_fabao_reward(fb, replace_slot=None)
                        game.fabao_reward_pending = False
                        game._show_route_selection()
                    return True
        else:
            for rect, slot in getattr(game, "fabao_reward_replace_rects", []):
                if rect.collidepoint(event.pos):
                    game._apply_fabao_reward(game.fabao_reward_selected, replace_slot=slot)
                    game.fabao_reward_pending = False
                    game._show_route_selection()
                    return True
    return False


def _handle_route_key_event(event, game):
    if event.type != pygame.KEYDOWN or not (pygame.K_1 <= event.key <= pygame.K_9):
        return False
    idx = event.key - pygame.K_1
    if idx >= len(game.route_options):
        return False
    opt = game.route_options[idx]
    level_id, reward_type = opt[0], (opt[3] if len(opt) > 3 else None)
    game.current_level_reward_type = reward_type
    nt = get_node_type(level_id)
    if nt == "shop":
        game.in_shop = True
        from core import EventBus
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
    return True


def _handle_shop_event(event, game):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        from shop import SHOP_UI
        mx, my = event.pos
        for item in SHOP_UI.get("item_rects", []):
            rect, itype, iid, cost = item[0], item[1], item[2], item[3]
            if rect.collidepoint(mx, my) and game.player.lingshi >= cost:
                game._buy_item(itype, iid, cost)
                return True
        if SHOP_UI.get("exit_rect") and SHOP_UI["exit_rect"].collidepoint(mx, my):
            game.in_shop = False
            return True
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        game.in_shop = False
        return True
    return False


def _handle_combat_keys(event, game):
    bindings = getattr(meta, "keybinds", {})
    if action_down(event, bindings, "switch_fabao") and game.scene == "combat" and not game.game_over and not game.victory and not game.in_shop and game.player:
        game.player.switch_fabao()
    elif action_down(event, bindings, "cast_spell") and game.scene == "combat" and not game.game_over and not game.victory and not game.in_shop and game.player and game.player.can_cast_spell():
        ctx = {"projectiles": game.projectiles, "spell_zones": game.spell_zones, "earth_walls": game.earth_walls}
        game.player.cast_spell(ctx)
    elif action_down(event, bindings, "dash") and game.scene == "combat" and not game.game_over and not game.victory and not game.in_shop and game.player:
        from config import ARENA_X, ARENA_Y, ARENA_W, ARENA_H
        arena = pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
        game.player._keybinds = bindings
        game.player.try_dash(arena)
    elif action_down(event, bindings, "partner_skill") and game.scene == "combat" and not game.game_over and not game.victory and not game.in_shop and game.player:
        from partner_skills import can_cast_partner_skill, cast_partner_skill
        if can_cast_partner_skill(game.player):
            ctx = {"projectiles": game.projectiles, "spell_zones": game.spell_zones, "earth_walls": game.earth_walls, "enemies": game.enemies}
            cast_partner_skill(game.player, ctx)
    elif action_down(event, bindings, "use_potion") and game.scene == "combat" and not game.game_over and not game.victory and not game.in_shop:
        run_p = getattr(game, "run_potions", 0)
        if run_p > 0 and game.player and game.player.health < game.player.max_health:
            game.run_potions -= 1
            heal = max(1, game.player.max_health * POTION_HEAL_PCT // 100)
            game.player.health = min(game.player.max_health, game.player.health + heal)
    elif action_down(event, bindings, "char_panel") and game.scene == "combat" and not game.game_over and not game.victory:
        game.char_panel_open = not game.char_panel_open
