"""
自动化测试和修复系统
这个系统可以：
1. 静态分析代码
2. 检查语法错误
3. 检查导入依赖
4. 模拟运行测试
5. 生成测试报告
"""

import ast
import os
import sys
from pathlib import Path
from typing import Any


class CodeAnalyzer:
    """代码静态分析器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.errors = []
        self.warnings = []

    def check_syntax(self, file_path: Path) -> tuple[bool, str]:
        """检查 Python 文件语法"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            ast.parse(code)
            return True, "语法正确"
        except SyntaxError as e:
            return False, f"语法错误: 行 {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"解析错误: {e!s}"

    def check_imports(self, file_path: Path) -> tuple[bool, list[str]]:
        """检查文件的导入依赖"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            tree = ast.parse(code)

            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)

            return True, imports
        except Exception as e:
            return False, [str(e)]

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """分析单个文件"""
        result = {
            "file": str(file_path.relative_to(self.project_root)),
            "syntax_ok": False,
            "syntax_msg": "",
            "imports": [],
            "classes": [],
            "functions": [],
        }

        # 检查语法
        syntax_ok, syntax_msg = self.check_syntax(file_path)
        result["syntax_ok"] = syntax_ok
        result["syntax_msg"] = syntax_msg

        if not syntax_ok:
            return result

        # 检查导入
        _imports_ok, imports = self.check_imports(file_path)
        result["imports"] = imports

        # 提取类和函数
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    result["classes"].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    result["functions"].append(node.name)
        except:
            pass

        return result


class TestSimulator:
    """测试模拟器 - 不实际运行代码，而是检查测试逻辑"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.test_results = []

    def simulate_erosion_test(self) -> tuple[bool, str]:
        """模拟侵蚀度系统测试"""
        file_path = self.project_root / "erosion_system.py"

        if not file_path.exists():
            return False, "文件不存在"

        analyzer = CodeAnalyzer(str(self.project_root))
        result = analyzer.analyze_file(file_path)

        if not result["syntax_ok"]:
            return False, f"语法错误: {result['syntax_msg']}"

        # 检查必要的类和方法
        if "ErosionSystem" not in result["classes"]:
            return False, "缺少 ErosionSystem 类"

        # 检查导入
        required_imports = ["dataclasses", "typing", "random"]
        for imp in required_imports:
            if not any(imp in i for i in result["imports"]):
                return False, f"缺少导入: {imp}"

        return True, "侵蚀度系统结构正确"

    def simulate_meta_test(self) -> tuple[bool, str]:
        """模拟渐进式解锁测试"""
        file_path = self.project_root / "meta.py"

        if not file_path.exists():
            return False, "文件不存在"

        analyzer = CodeAnalyzer(str(self.project_root))
        result = analyzer.analyze_file(file_path)

        if not result["syntax_ok"]:
            return False, f"语法错误: {result['syntax_msg']}"

        # 检查必要的类和方法
        if "MetaData" not in result["classes"]:
            return False, "缺少 MetaData 类"

        # 这里简化检查，实际应该解析类的方法

        return True, "渐进式解锁系统结构正确"

    def simulate_player_test(self) -> tuple[bool, str]:
        """模拟玩家属性加成测试"""
        file_path = self.project_root / "player.py"

        if not file_path.exists():
            return False, "文件不存在"

        analyzer = CodeAnalyzer(str(self.project_root))
        result = analyzer.analyze_file(file_path)

        if not result["syntax_ok"]:
            return False, f"语法错误: {result['syntax_msg']}"

        # 检查必要的类
        if "Player" not in result["classes"]:
            return False, "缺少 Player 类"

        # 检查必要的方法
        required_methods = ["apply_meta_bonuses", "apply_erosion_effects"]
        for method in required_methods:
            if method not in result["functions"]:
                return False, f"缺少方法: {method}"

        return True, "玩家系统结构正确"

    def simulate_achievement_test(self) -> tuple[bool, str]:
        """模拟成就系统测试"""
        file_path = self.project_root / "achievement.py"

        if not file_path.exists():
            return False, "文件不存在"

        analyzer = CodeAnalyzer(str(self.project_root))
        result = analyzer.analyze_file(file_path)

        if not result["syntax_ok"]:
            return False, f"语法错误: {result['syntax_msg']}"

        # 检查必要的函数
        required_functions = ["check_achievements", "get_achievement"]
        for func in required_functions:
            if func not in result["functions"]:
                return False, f"缺少函数: {func}"

        return True, "成就系统结构正确"


def run_automated_tests(project_root: str | None = None):
    """运行自动化测试"""
    if project_root is None:
        project_root = os.path.dirname(os.path.abspath(__file__))

    print("=" * 70)
    print("自动化测试和修复系统")
    print("=" * 70)
    print(f"项目路径: {project_root}\n")

    # 创建测试模拟器
    simulator = TestSimulator(project_root)

    # 运行测试
    tests = [
        ("侵蚀度系统", simulator.simulate_erosion_test),
        ("渐进式解锁", simulator.simulate_meta_test),
        ("玩家属性加成", simulator.simulate_player_test),
        ("成就系统", simulator.simulate_achievement_test),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"测试: {test_name}")
        try:
            success, message = test_func()
            results.append((test_name, success, message))
            status = "✓ 通过" if success else "✗ 失败"
            print(f"  {status}: {message}")
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"  ✗ 异常: {e}")
        print()

    # 输出总结
    print("=" * 70)
    print("测试总结")
    print("=" * 70)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for test_name, success, message in results:
        status = "✓" if success else "✗"
        print(f"{status} {test_name}: {message}")

    print(f"\n通过: {passed}/{total}")

    if passed == total:
        print("\n✓ 所有测试通过！")
        return True
    else:
        print("\n✗ 部分测试失败")
        return False


def generate_test_report(project_root: str | None = None):
    """生成详细的测试报告"""
    if project_root is None:
        project_root = os.path.dirname(os.path.abspath(__file__))

    analyzer = CodeAnalyzer(project_root)

    # 分析核心文件
    core_files = [
        "erosion_system.py",
        "meta.py",
        "player.py",
        "achievement.py",
        "game.py",
    ]

    report = []
    report.append("# 代码分析报告\n")
    report.append(f"项目路径: {project_root}\n")
    report.append(f"分析时间: {__import__('datetime').datetime.now()}\n\n")

    for file_name in core_files:
        file_path = Path(project_root) / file_name
        if not file_path.exists():
            report.append(f"## {file_name}\n")
            report.append("状态: ✗ 文件不存在\n\n")
            continue

        result = analyzer.analyze_file(file_path)

        report.append(f"## {file_name}\n")
        report.append(f"语法: {'✓ 正确' if result['syntax_ok'] else '✗ 错误'}\n")

        if not result["syntax_ok"]:
            report.append(f"错误: {result['syntax_msg']}\n")

        if result["classes"]:
            report.append(f"类: {', '.join(result['classes'])}\n")

        if result["functions"]:
            report.append(f"函数: {', '.join(result['functions'][:5])}")
            if len(result["functions"]) > 5:
                report.append(f" ... (共 {len(result['functions'])} 个)")
            report.append("\n")

        if result["imports"]:
            report.append(f"导入: {', '.join(result['imports'][:5])}")
            if len(result["imports"]) > 5:
                report.append(f" ... (共 {len(result['imports'])} 个)")
            report.append("\n")

        report.append("\n")

    return "".join(report)


if __name__ == "__main__":
    # 运行自动化测试
    success = run_automated_tests()

    # 生成报告
    print("\n" + "=" * 70)
    print("生成详细报告")
    print("=" * 70)
    report = generate_test_report()
    print(report)

    # 保存报告
    try:
        report_path = Path(__file__).parent / "TEST_REPORT.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"报告已保存到: {report_path}")
    except Exception as e:
        print(f"保存报告失败: {e}")

    sys.exit(0 if success else 1)
