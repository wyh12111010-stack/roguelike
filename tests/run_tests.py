"""
单元测试框架 - 不依赖 pytest
直接运行测试
"""

import os
import sys

import pygame

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("单元测试")
    print("=" * 60)

    # 初始化 pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    all_tests = []
    passed = 0
    failed = 0

    # 玩家测试
    print("\n[1/3] 玩家系统测试...")
    tests = test_player(screen)
    all_tests.extend(tests)

    # UI 测试
    print("\n[2/3] UI 系统测试...")
    tests = test_ui(screen)
    all_tests.extend(tests)

    # 游戏系统测试
    print("\n[3/3] 游戏系统测试...")
    tests = test_game(screen)
    all_tests.extend(tests)

    # 统计结果
    for test_name, result, error in all_tests:
        if result:
            passed += 1
        else:
            failed += 1

    # 打印总结
    print("\n" + "=" * 60)
    if failed == 0:
        print(f"[SUCCESS] 所有测试通过！({passed}/{passed + failed})")
    else:
        print(f"[FAILED] {failed} 个测试失败：")
        for test_name, result, error in all_tests:
            if not result:
                print(f"  - {test_name}: {error}")
    print("=" * 60)

    pygame.quit()
    return failed == 0


def test_player(screen):
    """测试玩家系统"""
    from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y
    from player import Player

    tests = []

    # 测试 1: 玩家创建
    try:
        player = Player(ARENA_X + ARENA_W // 2, ARENA_Y + ARENA_H // 2)
        assert player is not None
        assert player.health > 0
        assert player.max_health > 0
        print("  [OK] 玩家创建")
        tests.append(("玩家创建", True, None))
    except Exception as e:
        print(f"  [FAIL] 玩家创建: {e!s}")
        tests.append(("玩家创建", False, str(e)))
        return tests

    # 测试 2: 玩家移动
    try:
        player.update(0.016, [], [])
        print("  [OK] 玩家移动")
        tests.append(("玩家移动", True, None))
    except Exception as e:
        print(f"  [FAIL] 玩家移动: {e!s}")
        tests.append(("玩家移动", False, str(e)))

    # 测试 3: 玩家受伤
    try:
        initial_health = player.health
        player.take_damage(10)
        assert player.health < initial_health
        print("  [OK] 玩家受伤")
        tests.append(("玩家受伤", True, None))
    except Exception as e:
        print(f"  [FAIL] 玩家受伤: {e!s}")
        tests.append(("玩家受伤", False, str(e)))

    # 测试 4: 玩家灵石
    try:
        initial_lingshi = player.lingshi
        player.lingshi += 10
        assert player.lingshi == initial_lingshi + 10
        print("  [OK] 玩家灵石")
        tests.append(("玩家灵石", True, None))
    except Exception as e:
        print(f"  [FAIL] 玩家灵石: {e!s}")
        tests.append(("玩家灵石", False, str(e)))

    return tests


def test_ui(screen):
    """测试 UI 系统"""
    from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y
    from player import Player
    from ui.components import Colors, Panel, ProgressBar
    from ui.ui_manager import UIManager

    tests = []

    # 测试 1: UI 管理器创建
    try:
        ui_manager = UIManager(800, 600)
        assert ui_manager is not None
        assert ui_manager.hud is not None
        print("  [OK] UI 管理器创建")
        tests.append(("UI 管理器创建", True, None))
    except Exception as e:
        print(f"  [FAIL] UI 管理器创建: {e!s}")
        tests.append(("UI 管理器创建", False, str(e)))
        return tests

    # 测试 2: UI 设置玩家
    try:
        player = Player(ARENA_X + ARENA_W // 2, ARENA_Y + ARENA_H // 2)
        ui_manager.set_player(player)
        assert ui_manager.player is not None
        print("  [OK] UI 设置玩家")
        tests.append(("UI 设置玩家", True, None))
    except Exception as e:
        print(f"  [FAIL] UI 设置玩家: {e!s}")
        tests.append(("UI 设置玩家", False, str(e)))
        return tests

    # 测试 3: UI 更新
    try:
        for _ in range(5):
            ui_manager.update(0.016)
        print("  [OK] UI 更新")
        tests.append(("UI 更新", True, None))
    except Exception as e:
        print(f"  [FAIL] UI 更新: {e!s}")
        tests.append(("UI 更新", False, str(e)))

    # 测试 4: UI 绘制
    try:
        ui_manager.draw(screen)
        print("  [OK] UI 绘制")
        tests.append(("UI 绘制", True, None))
    except Exception as e:
        print(f"  [FAIL] UI 绘制: {e!s}")
        tests.append(("UI 绘制", False, str(e)))

    # 测试 5: 进度条组件
    try:
        bar = ProgressBar(10, 10, 100, 20, Colors.HP_RED, Colors.HP_RED_BG)
        bar.set_value(50, 100)
        assert bar.value == 0.5
        bar.update(0.016, (0, 0))
        bar.draw(screen)
        print("  [OK] 进度条组件")
        tests.append(("进度条组件", True, None))
    except Exception as e:
        print(f"  [FAIL] 进度条组件: {e!s}")
        tests.append(("进度条组件", False, str(e)))

    # 测试 6: 面板组件
    try:
        panel = Panel(10, 10, 200, 100)
        panel.draw(screen)
        print("  [OK] 面板组件")
        tests.append(("面板组件", True, None))
    except Exception as e:
        print(f"  [FAIL] 面板组件: {e!s}")
        tests.append(("面板组件", False, str(e)))

    return tests


def test_game(screen):
    """测试游戏系统"""
    from core import EventBus
    from core.events import PLAYER_HIT
    from game import Game

    tests = []

    # 测试 1: 游戏创建
    try:
        game = Game(screen)
        assert game is not None
        assert hasattr(game, "ui_manager")
        print("  [OK] 游戏创建")
        tests.append(("游戏创建", True, None))
    except Exception as e:
        print(f"  [FAIL] 游戏创建: {e!s}")
        tests.append(("游戏创建", False, str(e)))
        return tests

    # 测试 2: 游戏更新
    try:
        for _ in range(5):
            game.update(0.016)
        print("  [OK] 游戏更新")
        tests.append(("游戏更新", True, None))
    except Exception as e:
        print(f"  [FAIL] 游戏更新: {e!s}")
        tests.append(("游戏更新", False, str(e)))

    # 测试 3: 游戏绘制
    try:
        game.draw()
        print("  [OK] 游戏绘制")
        tests.append(("游戏绘制", True, None))
    except Exception as e:
        print(f"  [FAIL] 游戏绘制: {e!s}")
        tests.append(("游戏绘制", False, str(e)))

    # 测试 4: 事件系统
    try:
        called = [False]

        def handler(**kwargs):
            called[0] = True

        EventBus.on(PLAYER_HIT, handler)
        EventBus.emit(PLAYER_HIT, damage=10)

        assert called[0]
        EventBus.off(PLAYER_HIT, handler)
        print("  [OK] 事件系统")
        tests.append(("事件系统", True, None))
    except Exception as e:
        print(f"  [FAIL] 事件系统: {e!s}")
        tests.append(("事件系统", False, str(e)))

    # 测试 5: 存档系统
    try:
        from meta import meta
        from save import RunSaveData

        assert hasattr(meta, "daoyun")
        assert hasattr(meta, "unlocked_linggen")

        save_data = RunSaveData(scene="village", linggen_choice=0, fabao_choice=0)
        assert save_data.scene == "village"
        print("  [OK] 存档系统")
        tests.append(("存档系统", True, None))
    except Exception as e:
        print(f"  [FAIL] 存档系统: {e!s}")
        tests.append(("存档系统", False, str(e)))

    return tests


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
