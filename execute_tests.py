"""执行自动化测试"""

import os
import sys

# 添加项目路径
project_root = r"f:\游戏"
sys.path.insert(0, project_root)
os.chdir(project_root)

# 导入并运行测试系统
from automated_test_system import generate_test_report, run_automated_tests

if __name__ == "__main__":
    print("开始执行自动化测试...\n")

    # 运行测试
    success = run_automated_tests(project_root)

    # 生成报告
    print("\n生成详细报告...\n")
    report = generate_test_report(project_root)
    print(report)

    # 保存报告
    try:
        report_path = os.path.join(project_root, "TEST_REPORT.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n报告已保存到: {report_path}")
    except Exception as e:
        print(f"\n保存报告失败: {e}")

    sys.exit(0 if success else 1)
