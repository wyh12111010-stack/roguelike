# 人物美术流程与模板

> 修仙肉鸽项目的人物像素动画全流程，按步骤执行即可。

---

## 流程总览

```
Step 1: MJ 生成原图 → Step 2: 转像素图 → Step 3: 生成各状态帧 → Step 4: 预览与接入游戏
```

---

## Step 1：MJ 生成原图（1 张）

**目标**：得到 1 张角色基础图，用于后续转像素和生成各状态。

**操作**：

1. 打开 Midjourney，输入 `/imagine`
2. 粘贴以下提示词（不要修改参数）：

```
A young Chinese male cultivator in xianxia style, floating in mid-air with legs naturally bent, robes and sleeves flowing downward, wearing traditional daoist robes in vibrant light blue and white, long wide sleeves, black hair in a simple topknot, no weapon, empty hands, arms relaxed at sides, calm serene expression, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, soft diffused lighting, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

3. 确认 MJ 设置中 **没有** `--p` 后缀（否则会报 "Not enough ratings"）
4. 选一张满意的图，下载

**验收**：全身、正面、居中、纯色背景、颜色饱满、无特效光晕。

---

## Step 2：转像素图

**目标**：把原图转成像素风格，作为后续各状态帧的参考图。

**操作**：

1. 使用 Nano Banana 或同类 AI 图生图工具
2. 上传 Step 1 的 MJ 原图
3. 粘贴 `docs/NANOBANANA_PROMPTS.md` 第二节的转像素提示词（推荐方案 A 粗像素）
4. **在工具的「输出尺寸」设置中**指定 64×64、64×128 或 128×128（提示词内数字常被忽略）；或生成后用 Aseprite 等缩放

**验收**：主体清晰、像素风、透明背景、角色正面、无抗锯齿。

---

## Step 3：生成各状态帧（精灵图）

**目标**：用参考图 + 提示词，生成待机、死亡等状态的 2×2 精灵图。

**操作**：

### 3.1 准备参考图

- 使用 Step 2 的像素图作为参考图
- 人物形象以参考图为准，提示词只描述格式与动作

### 3.2 选择状态模板

| 状态 | 模板位置 | 帧逻辑 |
|------|----------|--------|
| 待机 | 见下方「待机模板」 | 最低→上升→最高→下降（悬浮 bobbing） |
| 死亡 | 见下方「死亡模板」 | 站立→后仰→下落→倒地 |

### 3.3 待机模板（复制到 Nano Banana / 图生图）

```
[Overall Format]
A 2D game sprite sheet layout, arranged in a 2×2 grid (4 distinct frames: top-left, top-right, bottom-left, bottom-right). Pure transparent background (PNG alpha channel). Pixel art style.

[Character Reference]
Use the provided reference image for the character design. Match the character's appearance, clothing, hair, and style exactly from the reference. Do not alter or redesign the character. CRITICAL: Preserve the pixel art style of the reference. No anti-aliasing, no smooth gradients, no high-resolution rendering. Keep crisp pixel edges and the same pixel density.

[Crucial: Frame-by-Frame Physical Description]
The character is FLOATING in ALL 4 frames—never sitting, never standing on ground. Each frame shows a different vertical position within the float cycle. Vertical order: Frame 1 (lowest) < Frame 2 (rising) < Frame 3 (highest) > Frame 4 (descending). Frame 4 must be LOWER than Frame 2 for smooth loop.
* Frame 1 (Top-left): Character at the LOWEST point of the float cycle. Still FLOATING, legs bent as if hovering—NOT sitting on ground. Body slightly lower than Frame 2. Robes pooled upwards.
* Frame 2 (Top-right): Character RISING. Body higher than Frame 1. Robes trailing downwards.
* Frame 3 (Bottom-left): Character at the HIGHEST point. Weightless. Robes spread out.
* Frame 4 (Bottom-right): Character DESCENDING. Body LOWER than Frame 2. Robes puffed upwards.

[Liveliness and Material Detail]
The fabric of the robes must have different waving folds and flowing shapes in EVERY frame to convey gentle air movement and liveliness. No stiff fabric. Pixel art style, crisp pixel edges, no anti-aliasing.
```

### 3.4 死亡模板（复制到 Nano Banana / 图生图）

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

### 3.5 新状态（敌人、NPC 等）

使用通用模板，替换 `{逐帧描述}` 和 `{材质细节}`，详见 `docs/SPRITE_FRAME_PROMPT_TEMPLATE.md`。

**验收**：2×2 网格、4 帧、PNG 透明背景、像素风、每帧有明显差异。

---

## Step 4：预览与接入游戏

**目标**：确认精灵图正确，并放入游戏生效。

**操作**：

### 4.1 预览

```bash
python tools/sprite_preview.py
```

- 拖放或选择精灵图
- 按 A 键切换中间轴对齐（AI 生成各帧可能位置不一致）
- 空格暂停，左右键切帧

### 4.2 复制到 assets

1. 把 Nano Banana 导出的图放入 `nanobanana_in` 文件夹
2. 运行：

```bash
python tools/copy_sprites_to_assets.py
```

脚本按文件名时间自动识别：第 1 个→待机，第 2 个→死亡。

### 4.3 主角命名规范

| 文件名 | 用途 |
|--------|------|
| `assets/player_idle.png` | 待机 |
| `assets/player_death.png` | 死亡 |

### 4.4 运行游戏

```bash
python main.py
```

**验收**：游戏中能看到待机悬浮动画和死亡倒地动画。

---

## 约束与注意

| 项目 | 约束 |
|------|------|
| 精灵图布局 | 固定 2×2 网格，顺序：左上、右上、左下、右下 |
| 帧数 | 每状态 4 帧 |
| 中间轴 | AI 生成各帧可能质心不一致，游戏用 `sprite_loader.get_content_center()` 对齐 |
| MJ 参数 | 不要加 `--p` |

---

## 相关文档

| 文档 | 用途 |
|------|------|
| `docs/NANOBANANA_PROMPTS.md` | 完整提示词与参数说明 |
| `docs/SPRITE_FRAME_PROMPT_TEMPLATE.md` | 通用模板与新状态示例 |
| `docs/PARTNER_ART_WORKFLOW.md` | **伙伴**美术流程（状态少，仅村子站立） |
