#!/usr/bin/env python3
"""创建敌人和Boss的彩色占位符"""
from PIL import Image, ImageDraw, ImageFont
import os

# 敌人配置（颜色 + 标签）
ENEMIES = {
    "enemy_melee.png": ((255, 100, 100), "近战"),
    "enemy_ranged.png": ((255, 180, 80), "远程"),
    "enemy_charge.png": ((200, 80, 200), "突进"),
    "enemy_aoe.png": ((255, 100, 255), "范围"),
    "enemy_homing.png": ((100, 200, 255), "追踪"),
    "enemy_summon.png": ((100, 255, 150), "召唤"),
}

# Boss配置
BOSSES = {
    "boss_yaowang.png": ((255, 50, 50), "妖王"),
    "boss_jianmo.png": ((150, 50, 150), "剑魔"),
    "boss_danmo.png": ((100, 255, 100), "丹魔"),
    "boss_huiyuan.png": ((50, 50, 50), "秽源"),
}

def create_placeholder(filename, color, label, size=64):
    """创建占位符图片"""
    # 创建图片
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形
    margin = 4
    draw.ellipse([margin, margin, size-margin, size-margin], fill=color, outline=(255, 255, 255), width=2)
    
    # 绘制标签（简单文字）
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("msyh.ttc", 16)  # 微软雅黑
    except:
        font = ImageFont.load_default()
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (size - text_w) // 2
    text_y = (size - text_h) // 2
    
    # 绘制文字（白色，带黑色描边）
    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
        draw.text((text_x+dx, text_y+dy), label, fill=(0, 0, 0), font=font)
    draw.text((text_x, text_y), label, fill=(255, 255, 255), font=font)
    
    return img

def main():
    output_dir = "f:/游戏/assets"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("创建敌人/Boss占位符")
    print("=" * 60)
    print()
    
    # 创建敌人占位符
    print("敌人占位符:")
    for filename, (color, label) in ENEMIES.items():
        output_path = os.path.join(output_dir, filename)
        img = create_placeholder(filename, color, label, size=48)
        img.save(output_path, "PNG")
        print(f"  [OK] {filename} - {label}")
    
    print()
    
    # 创建Boss占位符
    print("Boss占位符:")
    for filename, (color, label) in BOSSES.items():
        output_path = os.path.join(output_dir, filename)
        img = create_placeholder(filename, color, label, size=64)
        img.save(output_path, "PNG")
        print(f"  [OK] {filename} - {label}")
    
    print()
    print("=" * 60)
    print(f"完成！共创建 {len(ENEMIES) + len(BOSSES)} 个占位符")
    print("=" * 60)

if __name__ == "__main__":
    main()
