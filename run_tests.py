"""
简化的测试运行器 - 避免编码问题
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """测试所有模块是否可以正常导入"""
    print("=" * 50)
    print("测试模块导入")
    print("=" * 50)

    modules = [
        "erosion_system",
        "meta",
        "player",
        "achievement",
        "game",
    ]

    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            failed.append((module, e))

    return len(failed) == 0, failed


def test_erosion_basic():
    """测试侵蚀度系统基础功能"""
    print("\n" + "=" * 50)
    print("测试侵蚀度系统")
    print("=" * 50)

    try:
        from erosion_system import ErosionSystem

        erosion = ErosionSystem()

        # 测试初始状态
        assert erosion.erosion_level == 0, "初始侵蚀度应为 0"
        print("✓ 初始状态正确")

        # 测试增加侵蚀度
        level, crossed = erosion.add_erosion(15)
        assert level == 15, f"侵蚀度应为 15，实际为 {level}"
        print(f"✓ 增加侵蚀度: {level}")

        # 测试获取效果
        effect = erosion.get_current_effect()
        assert effect.name == "纯净", f"15 侵蚀度应为'纯净'，实际为 {effect.name}"
        print(f"✓ 当前状态: {effect.name}")

        # 测试跨越阈值
        level, crossed = erosion.add_erosion(10)
        assert level == 25, f"侵蚀度应为 25，实际为 {level}"
        assert crossed, "应该跨越阈值"
        effect = erosion.get_current_effect()
        assert effect.name == "轻度侵蚀", f"25 侵蚀度应为'轻度侵蚀'，实际为 {effect.name}"
        print(f"✓ 跨越阈值: {effect.name}")

        # 测试属性修正
        modifiers = erosion.get_stat_modifiers()
        assert "max_hp" in modifiers, "应该有生命修正"
        assert "attack" in modifiers, "应该有攻击修正"
        print(f"✓ 属性修正: {modifiers}")

        return True, None
    except Exception:
        import traceback

        return False, traceback.format_exc()


def test_meta_unlock():
    """测试渐进式解锁"""
    print("\n" + "=" * 50)
    print("测试渐进式解锁")
    print("=" * 50)

    try:
        from meta import MetaData

        meta = MetaData()

        # 测试初始状态
        initial_features = len(meta.unlocked_features)
        print(f"✓ 初始解锁功能数: {initial_features}")

        # 测试第一次通关
        meta.on_win(100, {})
        assert meta.total_wins == 1, "通关次数应为 1"
        assert "accessory_unlock" in meta.unlocked_features, "应解锁饰品系统"
        print(f"✓ 第 1 次通关: {meta.unlocked_features}")

        # 测试第二次通关
        meta.on_win(100, {})
        assert meta.total_wins == 2, "通关次数应为 2"
        assert "meta_growth" in meta.unlocked_features, "应解锁局外成长"
        print(f"✓ 第 2 次通关: {meta.unlocked_features}")

        # 测试第三次通关
        meta.on_win(100, {})
        assert meta.total_wins == 3, "通关次数应为 3"
        assert "erosion_system" in meta.unlocked_features, "应解锁侵蚀度系统"
        print(f"✓ 第 3 次通关: {meta.unlocked_features}")

        return True, None
    except Exception:
        import traceback

        return False, traceback.format_exc()


def test_achievement_check():
    """测试成就检查"""
    print("\n" + "=" * 50)
    print("测试成就系统")
    print("=" * 50)

    try:
        from achievement import check_achievements, get_achievement

        # 测试成就检查
        stats = {"max_attack_speed": 250}
        completed = set()

        new_achievements = check_achievements(stats, completed)
        assert len(new_achievements) > 0, "应该有新成就"
        print(f"✓ 检测到新成就: {new_achievements}")

        # 测试获取成就信息
        for ach_id in new_achievements:
            ach = get_achievement(ach_id)
            assert ach is not None, f"应该能获取成就 {ach_id}"
            print(f"✓ 成就信息: {ach['name']} - {ach['desc']}")

        # 测试不重复解锁
        completed.update(new_achievements)
        new_achievements = check_achievements(stats, completed)
        assert len(new_achievements) == 0, "不应该重复解锁"
        print("✓ 不重复解锁")

        return True, None
    except Exception:
        import traceback

        return False, traceback.format_exc()


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始自动化测试")
    print("=" * 60 + "\n")

    results = []

    # 测试导入
    success, error = test_imports()
    results.append(("模块导入", success, error))

    if not success:
        print("\n✗ 模块导入失败，停止后续测试")
        return False

    # 测试侵蚀度系统
    success, error = test_erosion_basic()
    results.append(("侵蚀度系统", success, error))

    # 测试渐进式解锁
    success, error = test_meta_unlock()
    results.append(("渐进式解锁", success, error))

    # 测试成就系统
    success, error = test_achievement_check()
    results.append(("成就系统", success, error))

    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    all_passed = True
    for name, success, error in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{status} - {name}")
        if not success and error:
            print(f"  错误: {error}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("所有测试通过！")
    else:
        print("部分测试失败，请检查错误信息")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n测试运行器出错: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
