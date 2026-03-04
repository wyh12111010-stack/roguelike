"""
直接执行测试 - 内嵌执行
"""
import sys
import os
from pathlib import Path

# 设置项目路径
project_root = Path(r"f:\游戏")
sys.path.insert(0, str(project_root))

# 直接执行测试代码
def main():
    print("=" * 70)
    print("内嵌测试执行器")
    print("=" * 70)
    print(f"项目路径: {project_root}\n")
    
    # 测试 1: 检查文件是否存在
    print("测试 1: 检查核心文件")
    core_files = [
        "erosion_system.py",
        "meta.py", 
        "player.py",
        "achievement.py",
        "game.py",
    ]
    
    all_exist = True
    for file_name in core_files:
        file_path = project_root / file_name
        exists = file_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file_name}")
        if not exists:
            all_exist = False
    
    if not all_exist:
        print("\n✗ 部分文件不存在")
        return False
    
    print("\n✓ 所有核心文件存在\n")
    
    # 测试 2: 检查语法
    print("测试 2: 检查语法")
    import ast
    
    all_syntax_ok = True
    for file_name in core_files:
        file_path = project_root / file_name
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            ast.parse(code)
            print(f"  ✓ {file_name}")
        except SyntaxError as e:
            print(f"  ✗ {file_name}: 行 {e.lineno}: {e.msg}")
            all_syntax_ok = False
        except Exception as e:
            print(f"  ✗ {file_name}: {e}")
            all_syntax_ok = False
    
    if not all_syntax_ok:
        print("\n✗ 部分文件有语法错误")
        return False
    
    print("\n✓ 所有文件语法正确\n")
    
    # 测试 3: 尝试导入模块
    print("测试 3: 导入模块")
    modules = [
        ("erosion_system", "ErosionSystem"),
        ("meta", "MetaData"),
        ("achievement", "check_achievements"),
    ]
    
    all_import_ok = True
    for module_name, check_attr in modules:
        try:
            module = __import__(module_name)
            if hasattr(module, check_attr):
                print(f"  ✓ {module_name}.{check_attr}")
            else:
                print(f"  ✗ {module_name}: 缺少 {check_attr}")
                all_import_ok = False
        except Exception as e:
            print(f"  ✗ {module_name}: {e}")
            all_import_ok = False
    
    if not all_import_ok:
        print("\n✗ 部分模块导入失败")
        return False
    
    print("\n✓ 所有模块导入成功\n")
    
    # 测试 4: 功能测试
    print("测试 4: 功能测试")
    
    try:
        # 测试侵蚀度系统
        from erosion_system import ErosionSystem
        erosion = ErosionSystem()
        level, crossed = erosion.add_erosion(25)
        assert level == 25
        effect = erosion.get_current_effect()
        assert effect.name == "轻度侵蚀"
        print("  ✓ 侵蚀度系统")
    except Exception as e:
        print(f"  ✗ 侵蚀度系统: {e}")
        all_import_ok = False
    
    try:
        # 测试渐进式解锁
        from meta import MetaData
        meta = MetaData()
        meta.on_win(100, {})
        assert meta.total_wins == 1
        assert "accessory_unlock" in meta.unlocked_features
        print("  ✓ 渐进式解锁")
    except Exception as e:
        print(f"  ✗ 渐进式解锁: {e}")
        all_import_ok = False
    
    try:
        # 测试成就系统
        from achievement import check_achievements
        stats = {"max_attack_speed": 250}
        new_achievements = check_achievements(stats, set())
        assert len(new_achievements) > 0
        print("  ✓ 成就系统")
    except Exception as e:
        print(f"  ✗ 成就系统: {e}")
        all_import_ok = False
    
    if not all_import_ok:
        print("\n✗ 部分功能测试失败")
        return False
    
    print("\n✓ 所有功能测试通过\n")
    
    print("=" * 70)
    print("✓ 所有测试通过！")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# 直接执行
main()



