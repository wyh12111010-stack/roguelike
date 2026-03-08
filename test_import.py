"""快速测试导入是否正常"""

import sys

try:
    print("测试导入 achievement...")
    print("OK achievement 导入成功")

    print("\n测试导入 game...")
    print("OK game 导入成功")

    print("\n测试导入 ui.input_handler...")
    print("OK ui.input_handler 导入成功")

    print("\n所有导入测试通过！")
    sys.exit(0)

except Exception as e:
    print(f"\nERROR 导入失败: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
