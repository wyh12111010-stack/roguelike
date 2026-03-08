"""
集成测试 - 核心玩法循环
覆盖：EventBus、GameState、NodeSystem、SceneManager、StatisticsTracker、balance_config
无需 pygame display，纯逻辑测试。
"""

import pytest

# ─── Fixtures ───


@pytest.fixture(autouse=True)
def _isolate_eventbus():
    """每个测试隔离 EventBus 全局状态"""
    from core.event_bus import EventBus

    EventBus.reset_global()
    yield
    EventBus.reset_global()


@pytest.fixture(autouse=True)
def _isolate_gamestate():
    """每个测试隔离 GameState 单例"""
    from core.game_state import GameState

    GameState.reset()
    yield
    GameState.reset()


# ═══════════════════════════════════════════
# 1. EventBus 集成
# ═══════════════════════════════════════════


class TestEventBusIntegration:
    """EventBus 实例隔离 + 全局兼容"""

    def test_instance_isolation(self):
        from core.event_bus import EventBus

        bus_a = EventBus()
        bus_b = EventBus()
        results = []

        bus_a.subscribe("hit", lambda **kw: results.append("a"))
        bus_b.subscribe("hit", lambda **kw: results.append("b"))

        bus_a.publish("hit")
        assert results == ["a"], "bus_a publish should only trigger bus_a listeners"

        bus_b.publish("hit")
        assert results == ["a", "b"]

    def test_global_backward_compat(self):
        from core.event_bus import EventBus

        received = []
        EventBus.on("test_event", lambda **kw: received.append(kw))
        EventBus.emit("test_event", damage=42)

        assert len(received) == 1
        assert received[0]["damage"] == 42

    def test_unsubscribe(self):
        from core.event_bus import EventBus

        count = [0]

        def handler(**kw):
            count[0] += 1

        EventBus.on("x", handler)
        EventBus.emit("x")
        assert count[0] == 1

        EventBus.off("x", handler)
        EventBus.emit("x")
        assert count[0] == 1, "handler should not fire after unsubscribe"

    def test_error_in_callback_does_not_break_others(self):
        from core.event_bus import EventBus

        results = []

        def bad(**kw):
            raise ValueError("boom")

        def good(**kw):
            results.append("ok")

        EventBus.on("e", bad)
        EventBus.on("e", good)
        EventBus.emit("e")

        assert results == ["ok"], "good callback should still fire after bad one raises"

    def test_clear_specific_event(self):
        from core.event_bus import EventBus

        a_count = [0]
        b_count = [0]
        EventBus.on("a", lambda **kw: a_count.__setitem__(0, a_count[0] + 1))
        EventBus.on("b", lambda **kw: b_count.__setitem__(0, b_count[0] + 1))

        EventBus.clear("a")
        EventBus.emit("a")
        EventBus.emit("b")

        assert a_count[0] == 0
        assert b_count[0] == 1

    def test_multi_subscriber_event_chain(self):
        """模拟战斗事件链: enemy_killed -> combo_update -> achievement_check"""
        from core.event_bus import EventBus

        chain = []

        EventBus.on("enemy_killed", lambda **kw: chain.append("kill"))
        EventBus.on("enemy_killed", lambda **kw: chain.append("combo"))
        EventBus.on("enemy_killed", lambda **kw: chain.append("achievement"))

        EventBus.emit("enemy_killed", enemy_id=1)
        assert chain == ["kill", "combo", "achievement"]


# ═══════════════════════════════════════════
# 2. GameState + RunData
# ═══════════════════════════════════════════


class TestGameState:
    def test_singleton(self):
        from core.game_state import GameState

        gs1 = GameState.get()
        gs2 = GameState.get()
        assert gs1 is gs2

    def test_reset_creates_new_instance(self):
        from core.game_state import GameState

        gs1 = GameState.get()
        GameState.reset()
        gs2 = GameState.get()
        assert gs1 is not gs2

    def test_run_data_defaults(self):
        from core.game_state import GameState

        gs = GameState.get()
        assert gs.run_data.kill_count == 0
        assert gs.run_data.lingshi == 0
        assert gs.run_data.current_node_index == 0
        assert gs.run_data.route_history == []

    def test_run_data_mutation(self):
        from core.game_state import GameState

        gs = GameState.get()
        gs.run_data.kill_count += 5
        gs.run_data.lingshi += 50
        gs.run_data.route_history.append(3)

        assert gs.run_data.kill_count == 5
        assert gs.run_data.lingshi == 50
        assert gs.run_data.route_history == [3]

    def test_combat_data_ephemeral(self):
        from core.game_state import GameState

        gs = GameState.get()
        gs.set_combat_data(enemies=[1, 2, 3], wave=1)
        assert gs.get_combat_data("enemies") == [1, 2, 3]
        assert gs.get_combat_data("wave") == 1
        assert gs.get_combat_data("missing", "default") == "default"

        gs.clear_combat_data()
        assert gs.get_combat_data("enemies") is None


# ═══════════════════════════════════════════
# 3. Node System
# ═══════════════════════════════════════════


class TestNodeSystem:
    def test_registry_register_and_create(self):
        from nodes.base import NodeHandler
        from nodes.registry import NodeRegistry

        class TestNode(NodeHandler):
            node_type = "test"

            def enter(self, ctx):
                ctx.extra["entered"] = True

        NodeRegistry.register("test", TestNode)
        handler = NodeRegistry.create("test")
        assert handler is not None
        assert isinstance(handler, TestNode)

        # Clean up
        NodeRegistry._handlers.pop("test", None)

    def test_node_lifecycle(self):
        """enter -> update (CONTINUE) -> update (COMPLETE) -> exit"""
        from nodes.base import NodeContext, NodeHandler, NodeStatus

        class CountdownNode(NodeHandler):
            node_type = "countdown"

            def __init__(self):
                self._ticks = 0

            def enter(self, ctx):
                ctx.extra["started"] = True

            def update(self, dt, ctx):
                self._ticks += 1
                if self._ticks >= 3:
                    return NodeStatus.COMPLETE
                return NodeStatus.CONTINUE

            def exit(self, ctx):
                return {"ticks": self._ticks}

        ctx = NodeContext(
            node_index=0,
            node_type="countdown",
            node_config={},
            player=None,
            run_data=None,
            meta=None,
        )

        node = CountdownNode()
        node.enter(ctx)
        assert ctx.extra["started"] is True

        assert node.update(0.016, ctx) == NodeStatus.CONTINUE
        assert node.update(0.016, ctx) == NodeStatus.CONTINUE
        assert node.update(0.016, ctx) == NodeStatus.COMPLETE

        result = node.exit(ctx)
        assert result["ticks"] == 3

    def test_node_fail_status(self):
        from nodes.base import NodeContext, NodeHandler, NodeStatus

        class DeathNode(NodeHandler):
            node_type = "death"

            def enter(self, ctx):
                pass

            def update(self, dt, ctx):
                if ctx.extra.get("health", 100) <= 0:
                    return NodeStatus.FAIL
                return NodeStatus.CONTINUE

        ctx = NodeContext(
            node_index=5,
            node_type="death",
            node_config={},
            player=None,
            run_data=None,
            meta=None,
            extra={"health": 0},
        )

        node = DeathNode()
        node.enter(ctx)
        assert node.update(0.016, ctx) == NodeStatus.FAIL


# ═══════════════════════════════════════════
# 4. SceneManager
# ═══════════════════════════════════════════


class TestSceneManager:
    @pytest.fixture(autouse=True)
    def _clean_scenes(self):
        from core.scene_manager import SceneManager

        old_scenes = SceneManager._scenes.copy()
        old_current = SceneManager._current
        old_name = SceneManager._current_name
        yield
        SceneManager._scenes = old_scenes
        SceneManager._current = old_current
        SceneManager._current_name = old_name

    def test_register_and_switch(self):
        from core.scene_manager import SceneManager

        lifecycle = []

        class MockScene:
            def __init__(self, **kw):
                self.kw = kw

            def enter(self):
                lifecycle.append("enter")

            def exit(self):
                lifecycle.append("exit")

        SceneManager.register("mock", MockScene)
        assert SceneManager.switch("mock") is True
        assert SceneManager.get_current_name() == "mock"
        assert "enter" in lifecycle

    def test_switch_calls_exit_on_previous(self):
        from core.scene_manager import SceneManager

        lifecycle = []

        class SceneA:
            def enter(self):
                lifecycle.append("a_enter")

            def exit(self):
                lifecycle.append("a_exit")

        class SceneB:
            def enter(self):
                lifecycle.append("b_enter")

            def exit(self):
                lifecycle.append("b_exit")

        SceneManager.register("a", SceneA)
        SceneManager.register("b", SceneB)

        SceneManager.switch("a")
        SceneManager.switch("b")

        assert lifecycle == ["a_enter", "a_exit", "b_enter"]

    def test_switch_nonexistent_returns_false(self):
        from core.scene_manager import SceneManager

        assert SceneManager.switch("nonexistent") is False

    def test_update_delegates(self):
        from core.scene_manager import SceneManager

        updated = []

        class UpdatableScene:
            def enter(self):
                pass

            def exit(self):
                pass

            def update(self, dt):
                updated.append(dt)

        SceneManager.register("upd", UpdatableScene)
        SceneManager.switch("upd")
        SceneManager.update(0.016)

        assert updated == [0.016]


# ═══════════════════════════════════════════
# 5. StatisticsTracker
# ═══════════════════════════════════════════


class TestStatisticsTracker:
    def test_combo_tracking(self):
        from systems.statistics import StatisticsTracker

        tracker = StatisticsTracker()
        tracker.on_enemy_killed()
        tracker.on_enemy_killed()
        tracker.on_enemy_killed()
        assert tracker.max_combo == 3
        assert tracker.current_combo == 3

    def test_combo_timeout(self):
        from systems.statistics import StatisticsTracker

        tracker = StatisticsTracker()
        tracker.on_enemy_killed()
        tracker.on_enemy_killed()

        # Simulate 3 seconds passing (combo_timer = 2.0)
        tracker.update(3.0, None)
        assert tracker.current_combo == 0
        assert tracker.max_combo == 2  # max preserved

    def test_damage_tracking(self):
        from systems.statistics import StatisticsTracker

        tracker = StatisticsTracker()
        tracker.on_damage_dealt(100)
        tracker.on_damage_dealt(250)
        tracker.on_damage_dealt(50)

        assert tracker.total_damage == 400
        assert tracker.max_single_damage == 250

    def test_reaction_tracking(self):
        from systems.statistics import StatisticsTracker

        tracker = StatisticsTracker()
        tracker.on_reaction_triggered("vaporize")
        tracker.on_reaction_triggered("melt")
        tracker.on_reaction_triggered("vaporize")
        tracker.on_reaction_triggered("overload")

        assert tracker.total_reactions == 4
        assert tracker.vaporize_count == 2
        assert tracker.melt_count == 1
        assert tracker.overload_count == 1

    def test_shop_purchase_count(self):
        from systems.statistics import StatisticsTracker

        tracker = StatisticsTracker()
        tracker.on_shop_purchase()
        tracker.on_shop_purchase()
        assert tracker.shop_purchases == 2

    def test_boss_flags(self):
        from systems.statistics import StatisticsTracker

        tracker = StatisticsTracker()
        assert tracker.boss_defeated_flags["boss_1"] is False
        tracker.boss_defeated_flags["boss_1"] = True
        assert tracker.boss_defeated_flags["boss_1"] is True


# ═══════════════════════════════════════════
# 6. balance_config
# ═══════════════════════════════════════════


class TestHitstop:
    """帧冻结系统测试"""

    def test_freeze_blocks_update(self):
        from game_juice import Hitstop

        hs = Hitstop()
        hs.freeze(0.05)
        assert hs.active is True
        assert hs.update(0.01) is True  # still frozen

    def test_freeze_expires(self):
        from game_juice import Hitstop

        hs = Hitstop()
        hs.freeze(0.03)
        hs.update(0.04)  # exceeds freeze
        assert hs.active is False
        assert hs.update(0.016) is False

    def test_longer_freeze_takes_priority(self):
        from game_juice import Hitstop

        hs = Hitstop()
        hs.freeze(0.02)
        hs.freeze(0.08)  # longer freeze should win
        assert hs.update(0.03) is True  # still frozen (0.08 - 0.03 = 0.05)
        assert hs.active is True


class TestBalanceConfig:
    def test_loads_yaml_values(self):
        from balance_config import cfg

        assert cfg("player.base_speed") == 200
        assert cfg("economy.lingshi_per_kill") == 5
        assert cfg("shop.fabao_cost") == 65

    def test_nested_access(self):
        from balance_config import cfg

        colors = cfg("colors.player")
        assert isinstance(colors, list)
        assert len(colors) == 3

    def test_missing_key_returns_default(self):
        from balance_config import cfg

        assert cfg("nonexistent.key") is None
        assert cfg("nonexistent.key", 42) == 42

    def test_reload_works(self):
        import balance_config

        balance_config.reload()
        assert balance_config.cfg("player.base_speed") == 200

    def test_list_values(self):
        from balance_config import cfg

        boss_daoyun = cfg("economy.daoyun_boss")
        assert isinstance(boss_daoyun, list)
        assert boss_daoyun == [8, 12, 16]


# ═══════════════════════════════════════════
# 7. 全流程集成：模拟一局玩法循环
# ═══════════════════════════════════════════


class TestGameplayLoopIntegration:
    """模拟简化的一局玩法循环（无 pygame 依赖）"""

    def test_full_run_simulation(self):
        """
        村庄 → 战斗节点(击杀+灵石) → 商店节点 → Boss节点 → 胜利
        全流程验证：GameState + EventBus + StatisticsTracker + RunData
        """
        from core.event_bus import EventBus
        from core.events import COMBAT_END, ENEMY_KILLED, VICTORY
        from core.game_state import GameState
        from systems.statistics import StatisticsTracker

        # ── Setup ──
        gs = GameState.get()
        tracker = StatisticsTracker()
        events_log = []

        EventBus.on(ENEMY_KILLED, lambda **kw: events_log.append("kill"))
        EventBus.on(COMBAT_END, lambda **kw: events_log.append("combat_end"))
        EventBus.on(VICTORY, lambda **kw: events_log.append("victory"))

        # ── Phase 1: Combat Node ──
        gs.run_data.current_node_index = 1

        # Simulate killing 5 enemies
        for i in range(5):
            EventBus.emit(ENEMY_KILLED, enemy_id=i)
            tracker.on_enemy_killed()
            gs.run_data.kill_count += 1
            gs.run_data.lingshi += 5  # LINGSHI_PER_KILL

        assert gs.run_data.kill_count == 5
        assert gs.run_data.lingshi == 25
        assert tracker.max_combo == 5
        assert events_log.count("kill") == 5

        # Level complete
        gs.run_data.lingshi += 10  # LINGSHI_PER_LEVEL
        gs.run_data.current_node_index = 2
        gs.run_data.route_history.append(1)

        # Combo times out between nodes (simulate 3s idle)
        tracker.update(3.0, None)
        assert tracker.current_combo == 0
        assert tracker.max_combo == 5

        # ── Phase 2: Shop Node ──
        # Player buys a fabao (cost 65), but only has 35
        initial_lingshi = gs.run_data.lingshi  # 35
        assert initial_lingshi == 35
        # Can't afford fabao (65), skip

        # ── Phase 3: More Combat ──
        gs.run_data.current_node_index = 3
        for i in range(10):
            tracker.on_enemy_killed()
            gs.run_data.kill_count += 1
            gs.run_data.lingshi += 5

        assert gs.run_data.kill_count == 15
        assert gs.run_data.lingshi == 85  # 35 + 50

        # ── Phase 4: Boss ──
        tracker.on_damage_dealt(500)
        tracker.on_reaction_triggered("vaporize")
        tracker.boss_defeated_flags["boss_1"] = True

        # ── Phase 5: Victory ──
        EventBus.emit(VICTORY)
        assert "victory" in events_log

        # ── Verify Final State ──
        assert gs.run_data.kill_count == 15
        assert tracker.max_combo == 10  # second streak was 10
        assert tracker.total_damage == 500
        assert tracker.boss_defeated_flags["boss_1"] is True
        assert tracker.vaporize_count == 1

    def test_death_resets_run_data(self):
        """模拟身陨→轮回：RunData 重置，meta 保留"""
        from core.game_state import GameState

        gs = GameState.get()

        # Simulate some progress
        gs.run_data.kill_count = 20
        gs.run_data.lingshi = 100
        gs.run_data.route_history = [1, 2, 3]

        # Death → reincarnation: reset run data
        from core.game_state import RunData

        gs.run_data = RunData()

        assert gs.run_data.kill_count == 0
        assert gs.run_data.lingshi == 0
        assert gs.run_data.route_history == []
