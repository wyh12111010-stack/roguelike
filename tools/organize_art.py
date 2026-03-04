#!/usr/bin/env python3
"""
自动整理美术素材到 assets 目录
- 自动识别角色
- 去背景
- 重命名
- 缩放到合适尺寸
"""
import os
import sys
from PIL import Image

# 角色映射（文件夹名 -> 目标文件名）
CHARACTER_MAPPING = {
    # 主角
    "主角": "player_idle.png",
    
    # NPC
    "栖霞": "npc_qixia.png",
    "玄真": "npc_xuanzhen.png", 
    "铸心": "npc_zhuxin.png",
    
    # 伙伴
    "玄霄": "partner_xuanxiao.png",
    "青璃": "partner_qingli.png",
    "赤渊": "partner_chiyuan.png",
    "碧落": "partner_biluo.png",
    "墨羽": "partner_moyu.png",
    
    # 敌人
    "近战": "enemy_melee.png",
    "远程": "enemy_ranged.png",
    "突进": "enemy_charge.png",
    "范围": "enemy_aoe.png",
    "追踪": "enemy_homing.png",
    "召唤": "enemy_summon.png",
    
    # Boss
    "妖王": "boss_yaowang.png",
    "剑魔": "boss_jianmo.png",
    "丹魔": "boss_danmo.png",
    "秽源": "boss_huiyuan.png",
}

def remove_background(img):
    """智能去背景"""
    img = img.convert("RGBA")
    width, height = img.size
    pixels = img.load()
    
    # 标记背景
    is_bg = [[False] * height for _ in range(width)]
    
    def flood(x, y, target):
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if cx < 0 or cx >= width or cy < 0 or cy >= height:
                continue
            if is_bg[cx][cy]:
                continue
            
            cur = pixels[cx, cy][:3]
            dist = abs(cur[0]-target[0]) + abs(cur[1]-target[1]) + abs(cur[2]-target[2])
            
            if dist <= 30:
                is_bg[cx][cy] = True
                stack.extend([(cx+1,cy), (cx-1,cy), (cx,cy+1), (cx,cy-1)])
    
    # 从四角开始
    for x, y in [(0,0), (width-1,0), (0,height-1), (width-1,height-1)]:
        flood(x, y, pixels[x, y][:3])
    
    # 应用透明
    for x in range(width):
        for y in range(height):
            if is_bg[x][y]:
                r, g, b, a = pixels[x, y]
                pixels[x, y] = (r, g, b, 0)
    
    return img

def scale_to_target(img, target_frame_size=48, grid_size=6):
    """缩放到目标尺寸"""
    # 如果是 6×6 网格（32 帧动画）
    if img.size[0] > 1000:  # 大图，可能是动画
        target_size = target_frame_size * grid_size
        return img.resize((target_size, target_size), Image.LANCZOS)
    else:
        # 小图，保持原样或适当缩放
        return img

def process_character(source_dir, output_dir):
    """处理单个角色目录"""
    results = []
    
    for folder_name, target_name in CHARACTER_MAPPING.items():
        # 查找匹配的文件夹
        folder_path = None
        for item in os.listdir(source_dir):
            item_path = os.path.join(source_dir, item)
            if os.path.isdir(item_path) and folder_name in item:
                folder_path = item_path
                break
        
        if not folder_path:
            print(f"[WARN] 未找到: {folder_name}")
            continue
        
        # 查找 PNG 文件
        png_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
        if not png_files:
            print(f"[WARN] {folder_name}: 无 PNG 文件")
            continue
        
        # 使用第一个 PNG
        source_file = os.path.join(folder_path, png_files[0])
        output_file = os.path.join(output_dir, target_name)
        
        try:
            print(f"处理: {folder_name} -> {target_name}")
            
            # 加载图片
            img = Image.open(source_file)
            print(f"  原始尺寸: {img.size[0]} × {img.size[1]}")
            
            # 去背景
            img = remove_background(img)
            print(f"  [OK] 去背景")
            
            # 缩放
            img = scale_to_target(img)
            print(f"  [OK] 缩放到: {img.size[0]} × {img.size[1]}")
            
            # 保存
            img.save(output_file, "PNG")
            print(f"  [OK] 保存到: {target_name}")
            
            results.append((folder_name, target_name, "[OK]"))
            
        except Exception as e:
            print(f"  [ERROR] 错误: {e}")
            results.append((folder_name, target_name, f"[ERROR] {e}"))
    
    return results

if __name__ == "__main__":
    source_dir = "F:/游戏/美术素材"
    output_dir = "f:/游戏/assets"
    
    print("=" * 60)
    print("美术素材自动整理工具")
    print("=" * 60)
    print()
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理所有角色
    results = process_character(source_dir, output_dir)
    
    # 总结
    print()
    print("=" * 60)
    print("处理完成！")
    print("=" * 60)
    print()
    
    success = sum(1 for r in results if r[2] == "[OK]")
    total = len(results)
    
    print(f"成功: {success}/{total}")
    print()
    
    for name, file, status in results:
        print(f"{status} {name:10s} -> {file}")
