---
name: image-analysis
description: Analyzes images (sprite sheets, pixel art) to check dimensions, format, pixel density, and suitability for game assets. Use when checking if artwork meets specifications.
---

# 图像分析 Skill

## 能力范围

分析图像文件的规格和质量，特别是精灵图和像素画：
- 图像尺寸（宽×高）
- 文件格式和透明度
- 单帧尺寸（对于精灵表）
- 像素密度估算
- 是否符合项目规格

## 使用场景

- 检查精灵图是否符合 Tiny Rogues 规格（32-48px 高度）
- 验证是否是粗像素风格
- 确认 2×2 网格布局
- 检查透明背景

## 工具脚本

### analyze_sprite.py

```python
#!/usr/bin/env python3
"""分析精灵图规格"""
import sys
from PIL import Image

def analyze_image(path):
    try:
        img = Image.open(path)
        
        print(f"📊 图像分析: {path}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"尺寸: {img.size[0]} × {img.size[1]} 像素")
        print(f"模式: {img.mode}")
        print(f"透明背景: {'✅ 是' if img.mode == 'RGBA' else '❌ 否'}")
        
        # 假设是 2×2 精灵表
        frame_w = img.size[0] // 2
        frame_h = img.size[1] // 2
        print(f"\n如果是 2×2 精灵表:")
        print(f"  单帧尺寸: {frame_w} × {frame_h} 像素")
        
        # 检查是否符合规格
        print(f"\n✅ 规格检查:")
        if 32 <= frame_h <= 48:
            print(f"  ✅ 高度符合 (32-48px): {frame_h}px")
        elif 28 <= frame_h <= 40:
            print(f"  ⚠️  敌人尺寸 (28-40px): {frame_h}px")
        elif 48 <= frame_h <= 64:
            print(f"  ⚠️  Boss 尺寸 (48-64px): {frame_h}px")
        else:
            print(f"  ❌ 高度不符合: {frame_h}px (需要 32-48px)")
        
        # 估算像素密度
        if frame_h <= 48:
            pixel_block_size = frame_h / 8  # 假设 8 个块
            print(f"  估算像素块: ~{pixel_block_size:.1f}px/块")
            if 5 <= pixel_block_size <= 8:
                print(f"  ✅ 像素密度合适 (5-8px/块)")
            else:
                print(f"  ⚠️  像素可能太细或太粗")
        
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python analyze_sprite.py <图像路径>")
        sys.exit(1)
    
    analyze_image(sys.argv[1])
```

## 使用方法

```bash
# 分析精灵图
python .cursor/skills/image-analysis/analyze_sprite.py "path/to/sprite.png"
```

## 输出示例

```
📊 图像分析: sprite_sheet.png
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
尺寸: 128 × 128 像素
模式: RGBA
透明背景: ✅ 是

如果是 2×2 精灵表:
  单帧尺寸: 64 × 64 像素

✅ 规格检查:
  ❌ 高度不符合: 64px (需要 32-48px)
  估算像素块: ~8.0px/块
  ✅ 像素密度合适 (5-8px/块)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 集成到项目

此 Skill 已集成到项目中，当需要检查图像规格时会自动调用。
