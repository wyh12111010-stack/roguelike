"""
自动测试执行器 - 解决路径和编码问题
"""

import os
import subprocess
import sys


def run_tests():
    """运行测试并返回结果"""
    # 获取项目目录
    project_dir = r"F:\游戏"
    test_script = os.path.join(project_dir, "run_tests.py")

    # 检查文件是否存在
    if not os.path.exists(test_script):
        print(f"错误: 测试脚本不存在: {test_script}")
        return False

    # 运行测试
    try:
        result = subprocess.run(
            [sys.executable, test_script],
            cwd=project_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        # 输出结果
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
