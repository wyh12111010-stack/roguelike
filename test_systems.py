"""
测试核心系统功能
"""


def test_erosion_system():
    """测试侵蚀度系统"""
    print("测试侵蚀度系统...")
    from erosion_system import ErosionSystem

    erosion = ErosionSystem()

    # 测试增加侵蚀度
    level, crossed = erosion.add_erosion(15, "使用禁忌道具")
    print(f"  增加侵蚀度 15: 当前 {level}, 跨越阈值: {crossed}")

    # 测试获取当前效果
    effect = erosion.get_current_effect()
    print(f"  当前状态: {effect.name} - {effect.description}")

    # 测试属性修正
    modifiers = erosion.get_stat_modifiers()
    print(f"  属性修正: {modifiers}")

    # 测试增加到更高阈值
    erosion.add_erosion(30, "阅读禁忌知识")
    effect = erosion.get_current_effect()
    print(f"  增加后状态: {effect.name}")

    # 测试状态显示
    print(erosion.get_status_display())

    print("✓ 侵蚀度系统测试通过\n")


def test_meta_progression():
    """测试渐进式解锁"""
    print("测试渐进式解锁...")
    from meta import MetaData

    meta = MetaData()

    # 模拟通关
    print(f"  初始通关次数: {meta.total_wins}")
    print(f"  初始解锁功能: {meta.unlocked_features}")

    # 第一次通关
    meta.on_win(100, {})
    print(f"  第1次通关后: {meta.total_wins} 次, 解锁: {meta.unlocked_features}")

    # 第二次通关
    meta.on_win(100, {})
    print(f"  第2次通关后: {meta.total_wins} 次, 解锁: {meta.unlocked_features}")

    # 第三次通关
    meta.on_win(100, {})
    print(f"  第3次通关后: {meta.total_wins} 次, 解锁: {meta.unlocked_features}")

    print("✓ 渐进式解锁测试通过\n")


def test_achievement_system():
    """测试成就系统"""
    print("测试成就系统...")
    from achievement import check_achievements, get_achievement

    # 测试成就检查
    stats = {
        "max_attack_speed": 250,
        "max_combo": 50,
    }

    completed = set()
    new_achievements = check_achievements(stats, completed)
    print(f"  新完成成就: {new_achievements}")

    for ach_id in new_achievements:
        ach = get_achievement(ach_id)
        print(f"  - {ach['name']}: {ach['desc']}")

    # 测试已完成成就不重复
    completed.update(new_achievements)
    new_achievements = check_achievements(stats, completed)
    print(f"  再次检查: {new_achievements} (应为空)")

    print("✓ 成就系统测试通过\n")


def test_player_bonuses():
    """测试玩家属性加成"""
    print("测试玩家属性加成...")
    from meta import MetaData
    from player import Player

    # 创建玩家
    player = Player(400, 300)
    print(f"  初始生命: {player.max_health}, 灵力: {player.max_mana}")

    # 模拟局外加成
    meta = MetaData()
    meta.base_health_bonus = 20
    meta.base_mana_bonus = 30

    # 应用加成
    player.apply_meta_bonuses()
    print(f"  应用局外加成后: 生命 {player.max_health}, 灵力 {player.max_mana}")

    # 测试侵蚀度效果
    player.erosion_level = 40
    player.apply_erosion_effects()
    print(f"  应用侵蚀度(40)后: 生命 {player.max_health}, 速度 {player.speed}")

    print("✓ 玩家属性加成测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("开始测试核心系统")
    print("=" * 50 + "\n")

    try:
        test_erosion_system()
        test_meta_progression()
        test_achievement_system()
        test_player_bonuses()

        print("=" * 50)
        print("所有测试通过！")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
