"""村子场景：村子内更新与绘制逻辑"""

from meta import meta
from village import (
    CENTER_ZONE,
    DEMO_PORTAL,
    EXIT_PORTAL,
    FABAO_ZONE,
    LINGGEN_ZONE,
    PARTNER_ROOMS,
    VILLAGE_MAP_RECT,
    get_camera_offset,
)
from village import draw as draw_village


class VillageScene:
    """村子场景：更新与绘制"""

    @staticmethod
    def update_village(dt, game):
        """村子内玩家移动，检测传送门。对话时禁止移动"""
        # 更新视觉效果
        from village_visual import update_village_visual

        update_village_visual(dt)

        if game.village_dialogue:
            return
        import pygame

        from controls import action_pressed

        keys = pygame.key.get_pressed()
        bindings = getattr(meta, "keybinds", {})
        speed = 180
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
            import math

            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length
            game.village_player.x += int(dx * speed * dt)
            game.village_player.y += int(dy * speed * dt)
        game.village_player.clamp_ip(VILLAGE_MAP_RECT)
        # 传送门：玩家进入则触发
        if game.village_player.colliderect(EXIT_PORTAL):
            game._start_combat(demo=False)
        elif game.village_player.colliderect(DEMO_PORTAL):
            game._start_combat(demo=True)

    @staticmethod
    def draw_village_scene(screen, game):
        """村子场景绘制（渐进式呈现）"""
        in_lg = game.village_player.colliderect(LINGGEN_ZONE)
        in_fb = game.village_player.colliderect(FABAO_ZONE)
        in_center = game.village_player.colliderect(CENTER_ZONE)
        in_partner = None
        for rect, _, pid in PARTNER_ROOMS:
            if game.village_player.colliderect(rect):
                in_partner = pid
                break
        meta_stats = {
            "kills": meta.total_kills,
            "levels": meta.total_levels_cleared,
            "wins": meta.total_wins,
            "element_dmg": meta.total_element_damage,
            "deaths": meta.total_deaths,
        }
        partner_can_heal = {}
        for pid in [p[2] for p in PARTNER_ROOMS]:
            from partner import can_heal_partner

            can, _ = can_heal_partner(pid, meta.daoyun, meta_stats, meta.partner_bond_levels)
            partner_can_heal[pid] = can
        cam = get_camera_offset(game.village_player)

        # 渐进式呈现：根据解锁功能显示对应区域
        unlocked_features = getattr(meta, "unlocked_features", set())

        draw_village(
            screen,
            game._avail_linggen,
            game._avail_fabao,
            game.linggen_choice,
            game.fabao_choice,
            meta.daoyun,
            meta.unlocked_linggen,
            meta.unlocked_fabao,
            game.village_player,
            in_lg,
            in_fb,
            cam,
            village_dialogue=game.village_dialogue,
            potion_stock=meta.potion_stock,
            potion_cap=meta.potion_cap,
            in_partner_zone=in_partner,
            partner_can_heal=partner_can_heal,
            partner_bond_levels=meta.partner_bond_levels,
            unlocked_accessories=meta.unlocked_accessories if "accessory_unlock" in unlocked_features else [],
            selected_partner_id=getattr(meta, "selected_partner_id", None),
            accessory_slots=getattr(meta, "accessory_slots", 6) if "meta_growth" in unlocked_features else 6,
            shop_refresh_count=getattr(meta, "shop_refresh_count", 1) if "meta_growth" in unlocked_features else 1,
            base_health_bonus=getattr(meta, "base_health_bonus", 0) if "meta_growth" in unlocked_features else 0,
            base_mana_bonus=getattr(meta, "base_mana_bonus", 0) if "meta_growth" in unlocked_features else 0,
            start_accessory_mode=getattr(meta, "start_accessory_mode", 0) if "meta_growth" in unlocked_features else 0,
            in_center_zone=in_center,
            achievements_unlocked=getattr(meta, "achievements", set()),
            resonance_panel_open=game.resonance_panel_open,
            resonance_system=game.resonance_system,
        )
