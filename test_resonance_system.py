"""
秽源共鸣系统测试
测试共鸣系统的核心功能
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resonance_system import ResonanceLevel, ResonanceSystem, ResonanceType, get_all_pacts, get_pact


def test_resonance_system():
    """测试共鸣系统基础功能"""
    print("=" * 60)
    print("测试 1：共鸣系统基础功能")
    print("=" * 60)

    system = ResonanceSystem()

    # 测试添加契约
    fury_minor = get_pact(ResonanceType.FURY, ResonanceLevel.MINOR)
    assert fury_minor is not None, "获取轻度狂暴契约失败"

    system.add_pact(fury_minor)
    assert len(system.active_pacts) == 1, "添加契约失败"
    assert system.get_total_intensity() == 1, "共鸣强度计算错误"

    print("✓ 添加契约成功")
    print(f"  当前契约：{fury_minor.name}")
    print(f"  共鸣强度：{system.get_total_intensity()}")
    print(f"  道韵倍率：{system.get_daoyun_multiplier():.1f}x")

    # 测试同类互斥
    fury_moderate = get_pact(ResonanceType.FURY, ResonanceLevel.MODERATE)
    system.add_pact(fury_moderate)
    assert len(system.active_pacts) == 1, "同类互斥失败"
    assert system.get_total_intensity() == 2, "替换后共鸣强度错误"

    print("\n✓ 同类互斥成功")
    print(f"  当前契约：{fury_moderate.name}")
    print(f"  共鸣强度：{system.get_total_intensity()}")

    # 测试多个不同类型
    tenacity_minor = get_pact(ResonanceType.TENACITY, ResonanceLevel.MINOR)
    swift_extreme = get_pact(ResonanceType.SWIFT, ResonanceLevel.EXTREME)
    system.add_pact(tenacity_minor)
    system.add_pact(swift_extreme)

    assert len(system.active_pacts) == 3, "添加多个契约失败"
    assert system.get_total_intensity() == 6, "多契约共鸣强度错误 (2+1+3=6)"

    print("\n✓ 多契约组合成功")
    print(f"  当前契约数：{len(system.active_pacts)}")
    print(f"  共鸣强度：{system.get_total_intensity()}")
    print(f"  道韵倍率：{system.get_daoyun_multiplier():.1f}x")

    # 测试清除
    system.clear_pacts()
    assert len(system.active_pacts) == 0, "清除契约失败"
    assert system.get_total_intensity() == 0, "清除后共鸣强度应为0"

    print("\n✓ 清除契约成功")

    print("\n" + "=" * 60)
    print("测试 1 通过！")
    print("=" * 60 + "\n")


def test_pact_effects():
    """测试契约效果"""
    print("=" * 60)
    print("测试 2：契约效果")
    print("=" * 60)

    system = ResonanceSystem()

    # 测试狂暴效果
    fury_extreme = get_pact(ResonanceType.FURY, ResonanceLevel.EXTREME)
    system.add_pact(fury_extreme)

    effects = system.get_combined_effects()
    assert "enemy_damage_mult" in effects, "狂暴效果缺失"
    assert effects["enemy_damage_mult"] == 1.6, "狂暴伤害倍率错误"
    assert "enemy_crit_rate" in effects, "暴击率效果缺失"

    print("✓ 狂暴效果正确")
    print(f"  敌人伤害倍率：{effects['enemy_damage_mult']:.1f}x")
    print(f"  敌人暴击率：+{effects['enemy_crit_rate'] * 100:.0f}%")

    # 测试坚韧效果
    system.clear_pacts()
    tenacity_extreme = get_pact(ResonanceType.TENACITY, ResonanceLevel.EXTREME)
    system.add_pact(tenacity_extreme)

    effects = system.get_combined_effects()
    assert "enemy_health_mult" in effects, "坚韧效果缺失"
    assert effects["enemy_health_mult"] == 2.0, "坚韧生命倍率错误"

    print("\n✓ 坚韧效果正确")
    print(f"  敌人生命倍率：{effects['enemy_health_mult']:.1f}x")
    print(f"  敌人减伤：+{effects.get('enemy_damage_reduction', 0) * 100:.0f}%")

    # 测试组合效果
    system.add_pact(fury_extreme)
    effects = system.get_combined_effects()

    assert effects["enemy_damage_mult"] == 1.6, "组合后伤害倍率错误"
    assert effects["enemy_health_mult"] == 2.0, "组合后生命倍率错误"

    print("\n✓ 组合效果正确")
    print(f"  敌人伤害倍率：{effects['enemy_damage_mult']:.1f}x")
    print(f"  敌人生命倍率：{effects['enemy_health_mult']:.1f}x")

    print("\n" + "=" * 60)
    print("测试 2 通过！")
    print("=" * 60 + "\n")


def test_unique_drops():
    """测试专属掉落"""
    print("=" * 60)
    print("测试 3：专属掉落")
    print("=" * 60)

    system = ResonanceSystem()

    # 添加几个契约
    fury_minor = get_pact(ResonanceType.FURY, ResonanceLevel.MINOR)
    tenacity_moderate = get_pact(ResonanceType.TENACITY, ResonanceLevel.MODERATE)
    swift_extreme = get_pact(ResonanceType.SWIFT, ResonanceLevel.EXTREME)

    system.add_pact(fury_minor)
    system.add_pact(tenacity_moderate)
    system.add_pact(swift_extreme)

    drops = system.get_unique_drops()

    assert len(drops) == 3, "专属掉落数量错误"
    assert "fury_minor" in drops, "狂暴碎片掉落缺失"
    assert "tenacity_moderate" in drops, "坚韧之核掉落缺失"
    assert "swift_extreme" in drops, "迅捷之翼掉落缺失"

    print("✓ 专属掉落正确")
    print(f"  掉落数量：{len(drops)}")
    print(f"  掉落列表：{', '.join(drops)}")

    print("\n" + "=" * 60)
    print("测试 3 通过！")
    print("=" * 60 + "\n")


def test_all_pacts():
    """测试所有契约"""
    print("=" * 60)
    print("测试 4：所有契约")
    print("=" * 60)

    all_pacts = get_all_pacts()

    assert len(all_pacts) == 18, f"契约数量错误，应为18个，实际{len(all_pacts)}个"

    # 按类型统计
    types = {}
    for pact in all_pacts:
        if pact.type not in types:
            types[pact.type] = []
        types[pact.type].append(pact)

    assert len(types) == 6, "契约类型数量错误，应为6类"

    for res_type, pacts in types.items():
        assert len(pacts) == 3, f"{res_type} 类型契约数量错误，应为3个"

    print("✓ 所有契约数量正确")
    print(f"  总契约数：{len(all_pacts)}")
    print(f"  契约类型数：{len(types)}")

    # 检查每个类型
    type_names = {
        ResonanceType.FURY: "狂暴",
        ResonanceType.TENACITY: "坚韧",
        ResonanceType.SWIFT: "迅捷",
        ResonanceType.SWARM: "增殖",
        ResonanceType.CHAOS: "混沌",
        ResonanceType.BARREN: "贫瘠",
    }

    print("\n契约详情：")
    for res_type, pacts in types.items():
        print(f"\n  {type_names[res_type]}侵蚀：")
        for pact in pacts:
            print(f"    - {pact.name} (+{pact.intensity}): {pact.desc}")

    print("\n" + "=" * 60)
    print("测试 4 通过！")
    print("=" * 60 + "\n")


def test_extreme_scenario():
    """测试极限场景"""
    print("=" * 60)
    print("测试 5：极限场景（共鸣强度 18）")
    print("=" * 60)

    system = ResonanceSystem()

    # 选择所有极度等级
    extreme_pacts = [
        get_pact(ResonanceType.FURY, ResonanceLevel.EXTREME),
        get_pact(ResonanceType.TENACITY, ResonanceLevel.EXTREME),
        get_pact(ResonanceType.SWIFT, ResonanceLevel.EXTREME),
        get_pact(ResonanceType.SWARM, ResonanceLevel.EXTREME),
        get_pact(ResonanceType.CHAOS, ResonanceLevel.EXTREME),
        get_pact(ResonanceType.BARREN, ResonanceLevel.EXTREME),
    ]

    for pact in extreme_pacts:
        system.add_pact(pact)

    intensity = system.get_total_intensity()
    daoyun_mult = system.get_daoyun_multiplier()

    assert intensity == 18, f"极限共鸣强度错误，应为18，实际{intensity}"
    assert daoyun_mult == 4.6, f"极限道韵倍率错误，应为4.6x，实际{daoyun_mult:.1f}x"

    print("✓ 极限场景正确")
    print(f"  共鸣强度：{intensity}")
    print(f"  道韵倍率：{daoyun_mult:.1f}x (+{int((daoyun_mult - 1) * 100)}%)")

    effects = system.get_combined_effects()
    print(f"\n  敌人伤害倍率：{effects.get('enemy_damage_mult', 1.0):.1f}x")
    print(f"  敌人生命倍率：{effects.get('enemy_health_mult', 1.0):.1f}x")
    print(f"  敌人速度倍率：{effects.get('enemy_speed_mult', 1.0):.1f}x")
    print(f"  敌人数量增加：+{effects.get('enemy_count_add', 0)}")
    print(f"  所有敌人精英化：{effects.get('all_enemies_elite', False)}")

    print("\n" + "=" * 60)
    print("测试 5 通过！")
    print("=" * 60 + "\n")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试秽源共鸣系统")
    print("=" * 60 + "\n")

    try:
        test_resonance_system()
        test_pact_effects()
        test_unique_drops()
        test_all_pacts()
        test_extreme_scenario()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60 + "\n")
        return True

    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}\n")
        import traceback

        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ 测试出错：{e}\n")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
