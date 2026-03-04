# 提示词（修仙肉鸽）

> 流程：MJ 生成 1 张原图 → 转像素图 → 根据提示词转成各状态的帧。

---

## 一、原图提示词（MJ 生成）

用于 MJ 生成 1 张原图（角色基础图）。MJ 格式：**描述内容 + 参数**，参数放末尾，用 `--` 前缀。

**完整提示词（复制到 /imagine 后）**

> 开头为参考图 URL，用于保持风格一致。MJ 会以该图作为风格/形象参考生成新图。

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A young Chinese male cultivator in xianxia style, floating in mid-air with legs naturally bent, robes and sleeves flowing downward, wearing traditional daoist robes in vibrant light blue and white, long wide sleeves, black hair in a simple topknot, no weapon, empty hands, arms relaxed at sides, calm serene expression, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, soft diffused lighting, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

**参数说明**

| 参数 | 含义 | 本提示词取值 |
|------|------|--------------|
| --ar | 宽高比 | 1:1（方形，便于转像素） |
| --niji 7 | Niji 动漫模型 V7 | 启用 |
| --s | 风格化强度 | 250（颜色更饱满） |
| --no | 排除元素 | glow, aura, energy effects, sparkles, particles, swirling, tendrils |

**注意**：不要加 `--p`（个人化风格需先评分 40+ 张图才能用，否则会报错 "Not enough ratings"）。若 MJ 设置里 suffix 含 `--p`，请先去掉。

**中文参考**（MJ 需英文，此供理解）：修仙少年，男性，漂浮半空，穿浅蓝白道袍，不拿武器，空手，全身正面，纯色背景，颜色饱满，动漫风格，无特效、无灵气光晕、无粒子。

**关键点**：正面、全身、居中、颜色饱满、背景干净、边缘留白。

---

## 二、转像素提示词

用于把 MJ 原图转成像素图（Image to Pixel Art）。**先上传原图作为参考**，再将下方提示词复制到 Nano Banana 或同类 AI 图生图工具。

> **重要**：多数 AI 工具会忽略提示词中的「64×64」等数字。若 64×64 和 128×128 生成结果相同，请：
> 1. 在工具的**输出尺寸/分辨率设置**中单独指定（非提示词内）
> 2. 或生成后用 Aseprite/Photoshop 等按目标尺寸裁剪/缩放
> 3. 用下方「像素密度描述」区分粗细风格，而非依赖数字

---

### 方案 A：粗像素（约 64×64 效果，8-bit 风格）

```
Convert the provided reference image into pixel art. CRITICAL requirements:
- EXTREMELY LOW RESOLUTION: 8-bit NES/Game Boy style. Each pixel block must be 3-5 pixels wide—very chunky, blocky, minimal detail
- Total character should fit in roughly 32-48 pixels width, 64-80 pixels height. Very few pixels to define each feature
- NO anti-aliasing, NO smooth gradients, NO high-resolution rendering—only crisp blocky pixel edges
- Preserve the character's appearance, clothing, hair, pose, colors from the reference—simplified into chunky blocks
- Style: extremely chunky retro pixel art, vivid saturated colors, high contrast
- Background: fully transparent (PNG alpha channel)
- Character centered, full body visible, facing front
- No glow, no aura, no particles—clean minimal pixel art only
```

### 方案 B：细像素（约 128×128 效果，16-bit 风格）

```
Convert the provided reference image into pixel art. CRITICAL requirements:
- LOW-MEDIUM RESOLUTION: 16-bit SNES/Genesis style. Each pixel block 1-2 pixels—more detail, readable fabric folds
- Total character roughly 60-70 pixels wide, 100-110 pixels tall. Moderate pixel density
- NO anti-aliasing, NO smooth gradients—crisp pixel edges, consistent pixel density
- Preserve the character's exact appearance, clothing, hair, pose, colors from the reference
- Style: 16-bit retro game aesthetic, chunky but readable pixels, vivid saturated colors, high contrast
- Background: fully transparent (PNG alpha channel)
- Character centered with padding, full body visible, facing front
- No glow, no aura, no particles—clean minimal pixel art only
- Fabric and hair retain readable shapes with clear pixel boundaries
```

**参数速查**：

| 目标 | 提示词方案 | 工具输出设置 | 视觉区别 |
|------|------------|--------------|----------|
| **粗/少像素（推荐）** | 方案 A | 64×64 或 64×128 | 每块 3-5 像素宽，极简 |
| 细/多像素 | 方案 B | 128×128 | 每块 1-2 像素，细节更多 |

**验收**：主体清晰、对比度够、颜色饱满、角色正面、边缘留白、无抗锯齿、透明背景。

---

## 三、转成各状态的帧的提示词

用于把像素图转成各状态的动画帧。**先提供参考图**，人物形象以参考图为准；提示词只描述格式与动作。

**输出要求**：精灵图（sprite sheet）格式，PNG，透明背景，**保持像素风**（与参考图一致）。**布局**：2×2 网格。

**预览工具**：`python tools/sprite_preview.py`，程序按 2×2 网格解析。

---

### 通用模板（主角、敌人、NPC 均适用）

**用法**：先提供参考图，再将下方模板中的 `{逐帧描述}` 和 `{材质细节}` 替换为具体状态内容。

```
[Overall Format]
A 2D game sprite sheet layout, arranged in a 2×2 grid (4 distinct frames: top-left, top-right, bottom-left, bottom-right). Pure transparent background (PNG alpha channel). Pixel art style.

[Character Reference]
Use the provided reference image for the character design. Match the character's appearance, clothing, hair, and style exactly from the reference. Do not alter or redesign the character. CRITICAL: Preserve the pixel art style of the reference. No anti-aliasing, no smooth gradients, no high-resolution rendering. Keep crisp pixel edges and the same pixel density.

[Crucial: Frame-by-Frame Physical Description]
{逐帧描述}
* Frame 1 (Top-left): ...
* Frame 2 (Top-right): ...
* Frame 3 (Bottom-left): ...
* Frame 4 (Bottom-right): ...

[Liveliness and Material Detail]
{材质细节}
```

**要点**：每帧必须有明显差异；保持像素风；人物以参考图为准。

> 完整模板与更多状态示例见 [docs/SPRITE_FRAME_PROMPT_TEMPLATE.md](SPRITE_FRAME_PROMPT_TEMPLATE.md)，敌人、NPC 等新角色可直接套用。

---

### 待机（主角）

| 项目 | 说明 |
|------|------|
| 帧数 | 4 帧 |
| 输出格式 | 精灵图（sprite sheet），2×2 网格，PNG 透明背景 |

**英文**
```
[Overall Format]
A 2D game sprite sheet layout, arranged in a 2×2 grid (4 distinct frames: top-left, top-right, bottom-left, bottom-right). Pure transparent background (PNG alpha channel). Pixel art style.

[Character Reference]
Use the provided reference image for the character design. Match the character's appearance, clothing, hair, and style exactly from the reference. Do not alter or redesign the character. CRITICAL: Preserve the pixel art style of the reference. No anti-aliasing, no smooth gradients, no high-resolution rendering. Keep crisp pixel edges and the same pixel density.

[Crucial: Frame-by-Frame Physical Description]
The character is FLOATING in ALL 4 frames—never sitting, never standing on ground. Each frame shows a different vertical position within the float cycle. Vertical order: Frame 1 (lowest) < Frame 2 (rising) < Frame 3 (highest) > Frame 4 (descending). Frame 4 must be LOWER than Frame 2 for smooth loop. They must NOT be identical.
* Frame 1 (Top-left): Character at the LOWEST point of the float cycle. Still FLOATING, legs bent as if hovering—NOT sitting on ground. Body slightly lower than Frame 2. Robes pooled upwards.
* Frame 2 (Top-right): Character RISING. Body higher than Frame 1. Robes trailing downwards.
* Frame 3 (Bottom-left): Character at the HIGHEST point. Weightless. Robes spread out.
* Frame 4 (Bottom-right): Character DESCENDING. Body LOWER than Frame 2. Robes puffed upwards.

[Liveliness and Material Detail]
The fabric of the robes must have different waving folds and flowing shapes in EVERY frame to convey gentle air movement and liveliness. No stiff fabric. Pixel art style, crisp pixel edges, no anti-aliasing.
```

**中文参考**：整体格式 + 人物以参考图为准 + 4 帧逐帧物理描述（最低→上升→最高→下降）+ 道袍每帧不同褶皱。

---

### 死亡（主角）

| 项目 | 说明 |
|------|------|
| 帧数 | 4 帧 |
| 输出格式 | 精灵图（sprite sheet），2×2 网格，PNG 透明背景 |

**英文**
```
[Overall Format]
A 2D game sprite sheet layout, arranged in a 2×2 grid (4 distinct frames: top-left, top-right, bottom-left, bottom-right). Pure transparent background (PNG alpha channel). Pixel art style.

[Character Reference]
Use the provided reference image for the character design. Match the character's appearance, clothing, hair, and style exactly from the reference. Do not alter or redesign the character. CRITICAL: Preserve the pixel art style of the reference. No anti-aliasing, no smooth gradients, no high-resolution rendering. Keep crisp pixel edges and the same pixel density.

[Crucial: Frame-by-Frame Physical Description]
Each of the 4 frames MUST show the character in a DIFFERENT pose to create a collapse sequence. They must NOT be identical.
* Frame 1 (Top-left): Character standing upright, intact. Calm pose, robes hanging normally.
* Frame 2 (Top-right): Beginning to collapse. Body leaning backward. Arms starting to fall. Robes and hair beginning to scatter.
* Frame 3 (Bottom-left): Mid-fall. Body tilting sharply. Robes and hair disheveled, flying outward from the impact.
* Frame 4 (Bottom-right): Fully collapsed. Body on ground or dissipating. Robes and hair fully scattered, spirit energy fading.

[Liveliness and Material Detail]
The fabric and hair must show progressive disruption in EVERY frame. Pixel art style, crisp pixel edges, no anti-aliasing.
```

**中文参考**：整体格式 + 人物以参考图为准 + 4 帧逐帧物理描述（站立→后仰→下落→倒地）+ 道袍与头发逐帧散开。

---

### 待机（伙伴，4 帧站立呼吸）

伙伴在村子展示，站立于地面，轻微呼吸循环。**先提供该伙伴的像素参考图**，再复制下方提示词。

| 项目 | 说明 |
|------|------|
| 帧数 | 4 帧 |
| 输出格式 | 精灵图（sprite sheet），2×2 网格，PNG 透明背景 |
| 适用 | 玄霄、青璃、赤渊、碧落、墨羽 等伙伴 |

**英文**
```
[Overall Format]
A 2D game sprite sheet layout, arranged in a 2×2 grid (4 distinct frames: top-left, top-right, bottom-left, bottom-right). Pure transparent background (PNG alpha channel). Pixel art style.

[Character Reference]
Use the provided reference image for the character design. Match the character's appearance, clothing, hair, and style exactly from the reference. Do not alter or redesign the character. CRITICAL: Preserve the pixel art style of the reference. No anti-aliasing, no smooth gradients, no high-resolution rendering. Keep crisp pixel edges and the same pixel density.

[Crucial: Frame-by-Frame Physical Description]
The character is STANDING on ground in ALL 4 frames. Minimal movement—gentle breathing cycle only. Vertical order: Frame 1 (lowest) < Frame 2 (rising) < Frame 3 (highest) > Frame 4 (descending). Frame 4 must be LOWER than Frame 2 for smooth loop.
* Frame 1 (Top-left): Character standing, neutral pose. Chest contracted (exhale complete). Body at LOWEST point of breath cycle. Robes/clothing relaxed, hanging down.
* Frame 2 (Top-right): Character standing, same pose. Chest expanding (inhale). Body RISING. Robes/clothing beginning to lift slightly.
* Frame 3 (Bottom-left): Character standing, same pose. Chest fully expanded (inhale complete). Body at HIGHEST point. Robes/clothing lifted, fabric slightly puffed.
* Frame 4 (Bottom-right): Character standing, same pose. Chest contracting (exhale). Body DESCENDING. Robes/clothing relaxing. Body LOWER than Frame 2 for smooth loop.

[Liveliness and Material Detail]
The fabric of robes/clothing must have subtle different shapes in EVERY frame to convey gentle breathing. Very subtle difference between frames—no exaggerated movement. Pixel art style, crisp pixel edges, no anti-aliasing.
```

**中文参考**：整体格式 + 人物以参考图为准 + 4 帧站立呼吸（最低→上升→最高→下降）+ 布料每帧轻微差异。

> 伙伴完整流程见 [docs/PARTNER_ART_WORKFLOW.md](PARTNER_ART_WORKFLOW.md)。
