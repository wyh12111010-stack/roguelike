"""
阶段 1 冒烟测试：验证村子→闯关→凯旋/身陨→回村 全流程无报错
用法: python -m tools.smoke_test
不启动 GUI，仅验证模块加载与关键逻辑。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def test_imports():
    """1. 核心模块导入"""
    import pygame
    pygame.init()
    from game import Game
    from levels import get_level_enemies, get_node_type, ROUTE_TREE, _ensure_loaded, NODE_TYPES
    from event_events import pick_random_event, apply_event_effect
    from achievement import unlock_achievement
    from enemy import create_enemy
    from player import Player
    from meta import meta
    from save import persist_meta
    print("  [OK] 核心模块导入")

def test_levels():
    """2. 关卡配置"""
    from levels import get_level_enemies, get_node_type, _ensure_loaded
    _ensure_loaded()
    for i in [0, 5, 10]:
        enemies = get_level_enemies(i)
        nt = get_node_type(i)
        assert len(enemies) > 0 or nt != "combat", f"level {i} has no enemies"
    print("  [OK] 关卡配置 (0,5,10)")

def test_event():
    """3. 事件节点"""
    from event_events import pick_random_event, apply_event_effect
    ev_id, text, options = pick_random_event(0)
    assert text and len(options) > 0
    print("  [OK] 事件池 pick_random_event")

def test_create_enemy():
    """4. 敌人生成"""
    from enemy import create_enemy
    e1 = create_enemy("melee", 100, 100, behavior="chase")
    e2 = create_enemy("melee", 100, 100, behavior="hitrun")
    e2b = create_enemy("ranged", 100, 100, behavior="burst")
    e2c = create_enemy("charge", 100, 100, behavior="feint")
    e2d = create_enemy("aoe", 100, 100, behavior="zoner")
    e3 = create_enemy("charge", 100, 100, boss_id="segment_boss_1", enemy_index=0)
    e4 = create_enemy("melee", 100, 100, boss_id="segment_boss_2", enemy_index=0)
    e5 = create_enemy("aoe", 100, 100, boss_id="segment_boss_3", enemy_index=0)
    e6 = create_enemy("charge", 100, 100, boss_id="final_boss", enemy_index=0)
    assert e1.enemy_type == "melee"
    assert e2.enemy_type == "melee"
    assert hasattr(e2, "_retreat_until")
    assert e2b.__class__.__name__ == "RangedBurstEnemy"
    assert e2c.__class__.__name__ == "ChargeFeintEnemy"
    assert e2d.__class__.__name__ == "AOEZonerEnemy"
    assert e3.__class__.__name__ == "BossYaowang"
    assert hasattr(e3, "SKILL")
    assert "pounce" in e3.SKILL and "double" in e3.SKILL
    assert "segment_boss_1" in __import__("enemy").BOSS_TUNING
    assert e4.__class__.__name__ == "BossJianmo"
    assert "wave_cd" in e4.SKILL and "summon_limit" in e4.SKILL
    assert e5.__class__.__name__ == "BossDanmo"
    assert "toxic_burst" in e5.SKILL and "toxic_ring" in e5.SKILL
    assert e6.__class__.__name__ == "BossHuiyuan"
    assert "dash" in e6.SKILL and "regen" in e6.SKILL
    print("  [OK] create_enemy (chase + hitrun)")


def test_reaction_effect_stack_rules():
    """5. 反应效果叠加规则：同来源 DOT 刷新，不无限叠加"""
    from reaction_effects import _apply_dot, _apply_weaken
    class Dummy:
        pass
    t = Dummy()
    t._dot_list = []
    _apply_dot(t, 2, 3, 0.4, source="fire")
    _apply_dot(t, 1, 2, 0.4, source="fire")
    assert len(t._dot_list) == 1, "same source dot should refresh not stack"
    assert t._dot_list[0]["dmg"] == 2
    _apply_weaken(t, 10, 0.5)
    _apply_weaken(t, 15, 0.3)
    assert t._weaken_pct == 15
    assert t._weaken_until >= 0.5
    print("  [OK] reaction stack rules")


def test_damage_ordering():
    """6. 伤害顺序：死亡后不应继续触发复杂效果"""
    from player import Player
    import pygame
    pygame.init()
    p = Player(100, 100)
    p.health = 1
    p.take_damage(10, None)
    assert p.health == 0
    # 再次受伤应早退，不抛异常
    p.take_damage(10, None)
    assert p.health == 0
    print("  [OK] damage ordering")


def test_boss_mechanics_limits():
    """7. Boss 机制上限：召唤/再生限次 + 丹魔阶段强化"""
    from enemy import create_enemy
    import pygame
    pygame.init()

    class DummyPlayer:
        def __init__(self):
            self.rect = pygame.Rect(200, 200, 32, 32)
            self.hp_taken = 0
        def take_damage(self, dmg, attr=None):
            self.hp_taken += max(0, int(dmg))

    player = DummyPlayer()

    # 剑魔：召唤达到上限时不再召唤
    j = create_enemy("melee", 100, 100, boss_id="segment_boss_2", enemy_index=0)
    j._summon_count = j.SKILL["summon_limit"]
    j._summon_cooldown = 0
    ctx_j = {"enemies": [j], "enemy_projectiles": [], "aoe_zones": []}
    j.update(0.2, player, ctx_j)
    assert len(ctx_j["enemies"]) == 1, "jianmo should not summon after limit"

    # 丹魔：进入 phase2 后强化邪灵
    d = create_enemy("aoe", 100, 100, boss_id="segment_boss_3", enemy_index=0)
    m = create_enemy("homing", 130, 130, boss_id="segment_boss_3", enemy_index=1)
    old_speed, old_damage = m.speed, m.damage
    d.health = int(d.max_health * 0.35)  # 低于 40%
    ctx_d = {"enemies": [d, m], "enemy_projectiles": [], "aoe_zones": []}
    d.update(0.1, player, ctx_d)
    assert getattr(m, "_buffed_by_danmo", False), "danmo minion should be buffed in phase2"
    assert m.speed >= old_speed and m.damage >= old_damage

    # 秽源：再生达到上限时不再再生
    h = create_enemy("charge", 100, 100, boss_id="final_boss", enemy_index=0)
    h._regen_count = h.SKILL["regen"]["limit"]
    h._regen_cd = 0
    ctx_h = {"enemies": [h], "enemy_projectiles": [], "aoe_zones": []}
    h.update(0.2, player, ctx_h)
    assert len(ctx_h["enemies"]) == 1, "huiyuan should not regen after limit"

    print("  [OK] boss mechanics limits")


def test_boss_sanity_check():
    """8. Boss 参数合法性检查"""
    from tools.boss_sanity_check import run
    run()
    print("  [OK] boss sanity check")


def test_boss_practice_entry():
    """9. Boss 试玩入口基础校验"""
    from tools.boss_practice import VALID_BOSSES
    from levels import get_boss_enemies
    assert "final_boss" in VALID_BOSSES
    for bid in VALID_BOSSES:
        assert len(get_boss_enemies(bid)) > 0, f"missing boss config for {bid}"
    print("  [OK] boss practice entry")

def test_game_init():
    """5. Game 初始化（需 display）"""
    import pygame
    pygame.init()
    pygame.display.set_mode((800, 600), pygame.HIDDEN)
    from game import Game
    g = Game(pygame.display.get_surface())
    assert g.scene == "village"
    print("  [OK] Game 初始化")

def main():
    print("=== 阶段 1 冒烟测试 ===\n")
    errors = []
    for name, fn in [
        ("导入", test_imports),
        ("关卡", test_levels),
        ("事件", test_event),
        ("敌人", test_create_enemy),
        ("反应叠加", test_reaction_effect_stack_rules),
        ("结算顺序", test_damage_ordering),
        ("Boss机制", test_boss_mechanics_limits),
        ("Boss参数", test_boss_sanity_check),
        ("Boss试玩", test_boss_practice_entry),
        ("Game", test_game_init),
    ]:
        try:
            print(f"[{name}]", end=" ")
            fn()
        except Exception as e:
            print(f"  [FAIL] {e}")
            errors.append((name, str(e)))
    print()
    if errors:
        print("失败:", errors)
        sys.exit(1)
    print("全部通过")

if __name__ == "__main__":
    main()
