"""
整理 assets 目录结构
将所有美术资源移动到正确的目录
"""

import shutil
from pathlib import Path

# 基础路径
ASSETS_DIR = Path("f:/游戏/assets")

# 标准目录结构
DIRS = {
    "characters": ["player", "npc", "partner", "enemy", "boss"],
    "icons": ["fabao", "accessory", "linggen"],
    "scenes": [],
    "ui": [],
}


def create_structure():
    """创建标准目录结构"""
    print("创建目录结构...")

    for category, subdirs in DIRS.items():
        category_path = ASSETS_DIR / category
        category_path.mkdir(exist_ok=True)
        print(f"  [OK] {category}/")

        for subdir in subdirs:
            subdir_path = category_path / subdir
            subdir_path.mkdir(exist_ok=True)
            print(f"  [OK] {category}/{subdir}/")


def move_files():
    """移动文件到正确目录"""
    print("\n移动文件...")

    # 文件映射规则
    moves = []

    # 角色文件
    for file in ASSETS_DIR.glob("player_*.png"):
        moves.append((file, ASSETS_DIR / "characters/player" / file.name))

    for file in ASSETS_DIR.glob("npc_*.png"):
        moves.append((file, ASSETS_DIR / "characters/npc" / file.name))

    for file in ASSETS_DIR.glob("partner_*.png"):
        moves.append((file, ASSETS_DIR / "characters/partner" / file.name))

    for file in ASSETS_DIR.glob("enemy_*.png"):
        moves.append((file, ASSETS_DIR / "characters/enemy" / file.name))

    for file in ASSETS_DIR.glob("boss_*.png"):
        moves.append((file, ASSETS_DIR / "characters/boss" / file.name))

    # 法宝图标（已在子目录）
    fabao_dir = ASSETS_DIR / "法宝"
    if fabao_dir.exists():
        for file in fabao_dir.glob("*.png"):
            moves.append((file, ASSETS_DIR / "icons/fabao" / file.name))

    # 饰品图标（已在子目录）
    accessory_dir = ASSETS_DIR / "饰品"
    if accessory_dir.exists():
        for file in accessory_dir.glob("*.png"):
            moves.append((file, ASSETS_DIR / "icons/accessory" / file.name))

    # 灵根图标（已在子目录）
    linggen_dir = ASSETS_DIR / "灵根"
    if linggen_dir.exists():
        for file in linggen_dir.glob("*.png"):
            moves.append((file, ASSETS_DIR / "icons/linggen" / file.name))
        for file in linggen_dir.glob("*.jfif"):
            # JFIF 需要转换
            moves.append((file, ASSETS_DIR / "icons/linggen" / (file.stem + ".png")))

    # 场景（已在子目录）
    scene_dir = ASSETS_DIR / "场景"
    if scene_dir.exists():
        for file in scene_dir.glob("*.jfif"):
            moves.append((file, ASSETS_DIR / "scenes" / (file.stem + ".png")))

    # 执行移动
    moved = 0
    for src, dst in moves:
        try:
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)

                # 如果是 JFIF，需要转换
                if src.suffix.lower() == ".jfif":
                    try:
                        from PIL import Image

                        img = Image.open(src)
                        img.save(dst, "PNG")
                        print(f"  [转换] {src.name} → {dst.relative_to(ASSETS_DIR)}")
                    except:
                        shutil.copy2(src, dst)
                        print(f"  [复制] {src.name} → {dst.relative_to(ASSETS_DIR)}")
                else:
                    shutil.move(str(src), str(dst))
                    print(f"  [移动] {src.name} → {dst.relative_to(ASSETS_DIR)}")
                moved += 1
        except Exception as e:
            print(f"  [错误] {src.name}: {e!s}")

    print(f"\n移动完成：{moved} 个文件")


def check_resources():
    """检查资源完整性"""
    print("\n检查资源...")

    # 预期的资源
    expected = {
        "角色/玩家": 1,
        "角色/NPC": 3,
        "角色/伙伴": 5,
        "角色/敌人": 6,
        "角色/Boss": 4,
        "图标/法宝": 21,
        "图标/饰品": 73,
        "图标/灵根": 5,
        "场景": 3,
    }

    # 实际的资源
    actual = {
        "角色/玩家": len(list((ASSETS_DIR / "characters/player").glob("*.png"))),
        "角色/NPC": len(list((ASSETS_DIR / "characters/npc").glob("*.png"))),
        "角色/伙伴": len(list((ASSETS_DIR / "characters/partner").glob("*.png"))),
        "角色/敌人": len(list((ASSETS_DIR / "characters/enemy").glob("*.png"))),
        "角色/Boss": len(list((ASSETS_DIR / "characters/boss").glob("*.png"))),
        "图标/法宝": len(list((ASSETS_DIR / "icons/fabao").glob("*.png"))),
        "图标/饰品": len(list((ASSETS_DIR / "icons/accessory").glob("*.png"))),
        "图标/灵根": len(list((ASSETS_DIR / "icons/linggen").glob("*.png"))),
        "场景": len(list((ASSETS_DIR / "scenes").glob("*.png"))),
    }

    print("\n资源统计：")
    print("-" * 50)
    for category in expected:
        exp = expected[category]
        act = actual[category]
        status = "[OK]" if act >= exp else "[!!]"
        print(f"{status} {category}: {act}/{exp}")

    total_expected = sum(expected.values())
    total_actual = sum(actual.values())
    print("-" * 50)
    print(f"总计: {total_actual}/{total_expected}")

    if total_actual < total_expected:
        print(f"\n[!!] 缺失 {total_expected - total_actual} 个资源")
    else:
        print("\n[OK] 所有资源已就位！")


def cleanup():
    """清理旧目录"""
    print("\n清理旧目录...")

    old_dirs = ["法宝", "饰品", "灵根", "场景"]
    for dirname in old_dirs:
        old_dir = ASSETS_DIR / dirname
        if old_dir.exists() and not any(old_dir.iterdir()):
            old_dir.rmdir()
            print(f"  [删除] {dirname}/")


def main():
    print("=" * 50)
    print("整理 assets 目录")
    print("=" * 50)

    # 1. 创建目录结构
    create_structure()

    # 2. 移动文件
    move_files()

    # 3. 检查资源
    check_resources()

    # 4. 清理
    cleanup()

    print("\n" + "=" * 50)
    print("整理完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
