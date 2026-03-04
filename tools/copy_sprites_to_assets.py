#!/usr/bin/env python3
"""
将 Nano Banana 输出的精灵图自动复制到 assets 目录。

用法：把 Nano Banana 导出的所有图都扔进 nanobanana_in 文件夹，然后运行本脚本。
无需指定路径，脚本会自动识别并复制。
"""
import os
import re
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
INPUT_DIR = os.path.join(PROJECT_ROOT, "nanobanana_in")  # 把图放这里
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
IDLE_DEST = os.path.join(ASSETS_DIR, "player_idle.png")
DEATH_DEST = os.path.join(ASSETS_DIR, "player_death.png")

# 文件名格式: nanobanana-edited-HH-MM-SS.png，按时间排序后：第1个=待机，第2个=死亡，第3个=原图参考(不用)
PATTERN = re.compile(r"nanobanana-edited-(\d{2})-(\d{2})-(\d{2})\.png", re.I)


def extract_time(path: str) -> tuple:
    """从文件名提取时间用于排序。"""
    name = os.path.basename(path)
    m = PATTERN.search(name)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return (99, 99, 99)


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(INPUT_DIR, exist_ok=True)

    # 收集所有 nanobanana-edited-*.png
    files = []
    for d in [INPUT_DIR, PROJECT_ROOT]:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if PATTERN.search(f):
                files.append(os.path.join(d, f))

    files = sorted(set(files), key=extract_time)

    if len(files) < 2:
        print(f"在 {INPUT_DIR} 或项目根目录找到 {len(files)} 个 nanobanana 图。")
        print("请把待机图和死亡图都放进 nanobanana_in 文件夹后重试。")
        return

    # 第1个=待机，第2个=死亡（第3个是原图参考，跳过）
    idle_src = files[0]
    death_src = files[1]

    shutil.copy2(idle_src, IDLE_DEST)
    shutil.copy2(death_src, DEATH_DEST)
    print(f"已复制 待机: {os.path.basename(idle_src)} -> assets/player_idle.png")
    print(f"已复制 死亡: {os.path.basename(death_src)} -> assets/player_death.png")
    print("\n完成！运行 python main.py 查看效果。")


if __name__ == "__main__":
    main()
