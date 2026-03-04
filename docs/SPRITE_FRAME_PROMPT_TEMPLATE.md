# 转成各状态的帧 · 通用提示词模板

> 主角、敌人、NPC 均适用。**先提供参考图**，人物形象以参考图为准。

---

## 固定结构（复制后替换 { } 内容）

```
[Overall Format]
A 2D game sprite sheet layout, arranged in a 2×2 grid (4 distinct frames: top-left, top-right, bottom-left, bottom-right). Pure transparent background (PNG alpha channel). Pixel art style.

[Character Reference]
Use the provided reference image for the character design. Match the character's appearance, clothing, hair, and style exactly from the reference. Do not alter or redesign the character. CRITICAL: Preserve the pixel art style of the reference. No anti-aliasing, no smooth gradients, no high-resolution rendering. Keep crisp pixel edges and the same pixel density.

[Crucial: Frame-by-Frame Physical Description]
{逐帧描述}

[Liveliness and Material Detail]
{材质细节}
```

---

## 替换规则

| 占位符 | 说明 | 示例 |
|--------|------|------|
| {逐帧描述} | 4 帧的物理/姿态变化，每帧必须不同 | 见下方「状态示例」 |
| {材质细节} | 布料、头发等每帧差异 | 如 "Robes different folds each frame" |

**要点**：每帧有明显差异；保持像素风；人物以参考图为准。

---

## 状态示例

### 待机（悬浮 bobbing）

```
The character is FLOATING in ALL 4 frames—never sitting, never standing on ground. Each frame shows a different vertical position within the float cycle. Vertical order: Frame 1 (lowest) < Frame 2 (rising) < Frame 3 (highest) > Frame 4 (descending). Frame 4 must be LOWER than Frame 2 for smooth loop.
* Frame 1 (Top-left): Character at the LOWEST point of the float cycle. Still FLOATING, legs bent as if hovering—NOT sitting on ground. Body slightly lower than Frame 2. Robes/clothing pooled upwards.
* Frame 2 (Top-right): Character RISING. Body higher than Frame 1. Robes/clothing trailing downwards.
* Frame 3 (Bottom-left): Character at the HIGHEST point. Weightless. Robes/clothing spread out.
* Frame 4 (Bottom-right): Character DESCENDING. Body LOWER than Frame 2. Robes/clothing puffed upwards.

[Liveliness] The fabric must have different waving folds and flowing shapes in EVERY frame. No stiff fabric. Pixel art style, crisp pixel edges, no anti-aliasing.
```

### 站立呼吸（伙伴/NPC，4 帧）

```
The character is STANDING on ground in ALL 4 frames. Minimal movement—gentle breathing cycle only. Vertical order: Frame 1 (lowest) < Frame 2 (rising) < Frame 3 (highest) > Frame 4 (descending). Frame 4 must be LOWER than Frame 2 for smooth loop.
* Frame 1 (Top-left): Character standing, neutral pose. Chest contracted (exhale complete). Body at LOWEST point of breath cycle. Robes/clothing relaxed, hanging down.
* Frame 2 (Top-right): Character standing, same pose. Chest expanding (inhale). Body RISING. Robes/clothing beginning to lift slightly.
* Frame 3 (Bottom-left): Character standing, same pose. Chest fully expanded (inhale complete). Body at HIGHEST point. Robes/clothing lifted, fabric slightly puffed.
* Frame 4 (Bottom-right): Character standing, same pose. Chest contracting (exhale). Body DESCENDING. Robes/clothing relaxing. Body LOWER than Frame 2 for smooth loop.

[Liveliness] The fabric must have subtle different shapes in EVERY frame to convey gentle breathing. Very subtle difference—no exaggerated movement. Pixel art style, crisp pixel edges, no anti-aliasing.
```

**说明**：伙伴、村子 NPC 等用 2×2 布局，与主角待机格式一致。详见 `docs/PARTNER_ART_WORKFLOW.md`。

---

### 死亡（倒地序列）

```
Each of the 4 frames MUST show the character in a DIFFERENT pose to create a collapse sequence.
* Frame 1 (Top-left): Character standing upright, intact. Calm pose.
* Frame 2 (Top-right): Beginning to collapse. Body leaning backward. Arms starting to fall.
* Frame 3 (Bottom-left): Mid-fall. Body tilting sharply. Disheveled, flying outward.
* Frame 4 (Bottom-right): Fully collapsed. Body on ground or dissipating.

[Liveliness] The fabric and hair must show progressive disruption in EVERY frame. Pixel art style, crisp pixel edges, no anti-aliasing.
```

---

## 输出格式

- 精灵图（sprite sheet），2×2 网格
- PNG，透明背景
- 保持像素风（与参考图一致）

---

## 中间轴对齐

AI 生成的精灵图各帧可能出现**中间轴不一致**（角色在每帧中的位置不同）。预览工具和游戏绘制时需做对齐：

- **预览工具**：默认开启「对齐」，按 A 键切换
- **游戏**：使用 `tools/sprite_loader.get_content_center(frame)` 获取每帧质心，绘制时以质心为锚点
