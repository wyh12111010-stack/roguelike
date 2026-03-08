"""
自动化打包脚本
用法: python build.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build"
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"

# 版本号
VERSION_FILE = ROOT / "VERSION"
VERSION = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else "0.9.0"

# 应用名称
APP_NAME = "修仙肉鸽"
EXE_NAME = f"{APP_NAME}.exe"


def clean():
    """清理旧的构建文件"""
    print("清理旧的构建文件...")
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
            print(f"  已删除: {d}")


def check_dependencies():
    """检查依赖是否安装"""
    print("检查依赖...")
    try:
        import pygame
        import pymunk

        print("  ✓ pygame")
        print("  ✓ pymunk")
    except ImportError as e:
        print(f"  ✗ 缺少依赖: {e}")
        print("  请运行: pip install -r requirements.txt")
        sys.exit(1)

    try:
        import PyInstaller

        print("  ✓ pyinstaller")
    except ImportError:
        print("  ✗ 缺少 PyInstaller")
        print("  请运行: pip install pyinstaller")
        sys.exit(1)


def build_exe():
    """使用 PyInstaller 打包"""
    print(f"\n开始打包 {APP_NAME} v{VERSION}...")

    # PyInstaller 参数
    args = [
        "pyinstaller",
        "--name",
        APP_NAME,
        "--onefile",  # 单文件模式
        "--windowed",  # 无控制台窗口
        "--icon",
        "NONE",  # 如果有图标可以指定
        # 添加数据文件
        f"--add-data={ASSETS_DIR};assets",
        f"--add-data={DATA_DIR};data",
        f"--add-data={VERSION_FILE};.",
        # 隐藏导入
        "--hidden-import=pygame",
        "--hidden-import=pymunk",
        # 主入口
        str(ROOT / "main.py"),
    ]

    print(f"执行命令: {' '.join(args)}")
    result = subprocess.run(args, cwd=ROOT)

    if result.returncode != 0:
        print("\n✗ 打包失败")
        sys.exit(1)

    print("\n✓ 打包成功！")
    print(f"  可执行文件: {DIST_DIR / EXE_NAME}")


def create_release_package():
    """创建发布包（包含文档等）"""
    print("\n创建发布包...")

    release_dir = DIST_DIR / f"{APP_NAME}-v{VERSION}"
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir(parents=True)

    # 复制可执行文件
    exe_src = DIST_DIR / EXE_NAME
    if exe_src.exists():
        shutil.copy2(exe_src, release_dir / EXE_NAME)
        print("  ✓ 复制可执行文件")

    # 复制文档
    docs_to_copy = ["README.md", "CHANGELOG.md", "VERSION"]
    for doc in docs_to_copy:
        src = ROOT / doc
        if src.exists():
            shutil.copy2(src, release_dir / doc)
            print(f"  ✓ 复制 {doc}")

    # 复制用户手册
    user_guide = DOCS_DIR / "USER_GUIDE.md"
    if user_guide.exists():
        shutil.copy2(user_guide, release_dir / "用户手册.md")
        print("  ✓ 复制用户手册")

    print(f"\n✓ 发布包已创建: {release_dir}")
    print("  可以将此文件夹打包为 ZIP 分发")


def main():
    print("=" * 60)
    print(f"  {APP_NAME} 自动化打包工具")
    print(f"  版本: v{VERSION}")
    print("=" * 60)

    # 检查依赖
    check_dependencies()

    # 清理旧文件
    clean()

    # 打包
    build_exe()

    # 创建发布包
    create_release_package()

    print("\n" + "=" * 60)
    print("  打包完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
