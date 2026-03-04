"""
资源路径配置
统一管理所有游戏资源的加载路径
"""
import os
from pathlib import Path

# 基础路径
ASSETS_DIR = Path("assets")

# 角色资源路径
CHARACTERS = {
    "player": ASSETS_DIR / "characters/player",
    "npc": ASSETS_DIR / "characters/npc",
    "partner": ASSETS_DIR / "characters/partner",
    "enemy": ASSETS_DIR / "characters/enemy",
    "boss": ASSETS_DIR / "characters/boss",
}

# 图标资源路径
ICONS = {
    "fabao": ASSETS_DIR / "icons/fabao",
    "accessory": ASSETS_DIR / "icons/accessory",
    "linggen": ASSETS_DIR / "icons/linggen",
}

# 场景资源路径
SCENES = ASSETS_DIR / "scenes"

# UI资源路径
UI = ASSETS_DIR / "ui"

# 获取资源路径的辅助函数
def get_character_sprite(category: str, name: str) -> str:
    """获取角色精灵路径"""
    return str(CHARACTERS[category] / f"{name}.png")

def get_icon(category: str, icon_id: str) -> str:
    """获取图标路径"""
    # 法宝图标需要映射
    if category == "fabao":
        from fabao_icons import get_fabao_icon_name
        icon_id = get_fabao_icon_name(icon_id)
    
    return str(ICONS[category] / f"{icon_id}.png")

def get_scene(scene_name: str) -> str:
    """获取场景背景路径"""
    return str(SCENES / f"{scene_name}.png")

# 检查资源是否存在
def check_resource(path: str) -> bool:
    """检查资源文件是否存在"""
    return os.path.exists(path)

# 列出某类资源的所有文件
def list_resources(category: str, subcategory: str = None) -> list:
    """列出某类资源的所有文件"""
    if category == "characters" and subcategory:
        path = CHARACTERS[subcategory]
    elif category == "icons" and subcategory:
        path = ICONS[subcategory]
    elif category == "scenes":
        path = SCENES
    elif category == "ui":
        path = UI
    else:
        return []
    
    if not path.exists():
        return []
    
    return [f.stem for f in path.glob("*.png")]

if __name__ == "__main__":
    # 测试资源路径
    print("资源路径配置测试")
    print("=" * 50)
    
    # 测试角色路径
    print("\n角色资源：")
    for cat, path in CHARACTERS.items():
        count = len(list(path.glob("*.png"))) if path.exists() else 0
        print(f"  {cat}: {count} 个文件")
    
    # 测试图标路径
    print("\n图标资源：")
    for cat, path in ICONS.items():
        count = len(list(path.glob("*.png"))) if path.exists() else 0
        print(f"  {cat}: {count} 个文件")
    
    # 测试场景路径
    print("\n场景资源：")
    count = len(list(SCENES.glob("*.png"))) if SCENES.exists() else 0
    print(f"  scenes: {count} 个文件")
    
    print("\n" + "=" * 50)
    print("配置完成！")
