"""
快速验收脚本 - 运行所有 gate 检查
用法: python quick_check.py
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CHECKS = [
    ("冒烟测试", ["python", "-m", "tools.smoke_test"]),
    ("战斗可读性检查", ["python", "-m", "tools.fairness_gate"]),
    ("数值与经济验收", ["python", "-m", "tools.phase2_gate"]),
]


def run_check(name, cmd):
    """运行单个检查"""
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print('=' * 60)
    
    result = subprocess.run(cmd, cwd=ROOT)
    
    if result.returncode != 0:
        print(f"\n✗ {name} 失败")
        return False
    
    print(f"\n✓ {name} 通过")
    return True


def main():
    print("=" * 60)
    print("  修仙肉鸽 - 快速验收")
    print("=" * 60)
    
    results = []
    for name, cmd in CHECKS:
        success = run_check(name, cmd)
        results.append((name, success))
    
    print("\n" + "=" * 60)
    print("  验收结果")
    print("=" * 60)
    
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {status} - {name}")
    
    all_passed = all(success for _, success in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("  所有检查通过！项目状态良好。")
    else:
        print("  部分检查失败，请修复后重试。")
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()




