# Boss 美术流程（4 个）

> 妖王、剑魔、丹魔、秽源 完整美术流程

---

## 目标

为 4 个 Boss 各制作 2 种状态：
- **待机**：1 帧静态（或 2 帧轻微晃动）
- **死亡**：4 帧倒地序列

---

## 约束

| 项目 | 约束 |
|------|------|
| 状态数量 | 每个 2 种（待机、死亡） |
| 帧数 | 待机 1 帧，死亡 4 帧 |
| 输出格式 | 待机单张 PNG，死亡 2×2 网格精灵图 |
| 风格 | 像素风，粗像素（约 64×64 效果） |
| 尺寸 | 比普通敌人略大（约 1.2~1.5 倍） |

---

## 流程总览

```
Step 1: MJ 生成原图（每个 1 张）
  → Step 2: 转像素图
  → Step 3: 生成待机图（1 帧）
  → Step 4: 生成死亡帧（2×2 精灵图）
  → Step 5: 放入 assets
```

---

## Step 1：MJ 生成原图（每个 1 张）

**目标**：得到每个 Boss 的 1 张基础图，用于转像素和生成各状态。

**操作**：在 MJ 中 `/imagine` 后，先粘贴参考图 URL（主角图，用于保持风格一致），再粘贴下方对应 Boss 的完整提示词。

**主角参考图 URL**（每个 Boss 提示词前都要加）：
```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc&
```

---

### 妖王（segment_boss_1）MJ 提示词

**身份**：被污染的妖兽王者（虎形），火属性

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A corrupted tiger beast king, massive muscular quadruped, dark red and black fur with corruption marks and fire motifs, sharp fangs and claws, fierce aggressive stance, corruption energy visible on body, imposing and menacing, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

---

### 剑魔（segment_boss_2）MJ 提示词

**身份**：被污染的剑修，持剑

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A corrupted sword master, male, wearing tattered dark grey and crimson robes with corruption marks, holding a large corrupted sword, menacing battle stance, dark red and black corruption veins visible on clothing and sword, disheveled long hair, fierce expression, imposing presence, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

---

### 丹魔（segment_boss_3）MJ 提示词

**身份**：被污染的丹修/毒修

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A corrupted alchemist master, male or female, wearing tattered dark purple and green robes with corruption marks and poison motifs, holding a corrupted pill or vial, casting pose with one hand raised, dark purple and black corruption veins visible on clothing and hands, disheveled hair, sinister expression, imposing presence, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

---

### 秽源（final_boss）MJ 提示词

**身份**：污染源本体，终极 Boss

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A corrupted source entity, humanoid or semi-humanoid form, massive imposing figure, dark purple and black body with corruption energy forming its essence, multiple corruption tendrils or appendages, menacing stance, eerie glowing eyes, corruption symbols visible on body, ultimate evil presence, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

---

**验收**：全身、正面、居中、纯色背景、颜色饱满、无特效、与主角风格一致、比普通敌人更有气势。

---

## Step 2：转像素图（每个 1 张）

**目标**：把 Step 1 的 MJ 原图转成像素风格，作为 Step 3/4 的参考图。

**操作**：上传原图到 Nano Banana，粘贴下方提示词。

### 转像素提示词（粗像素，约 64×64 效果，Boss 可略大）

```
Convert the provided reference image into pixel art. CRITICAL requirements:
- EXTREMELY LOW RESOLUTION: 8-bit NES/Game Boy style. Each pixel block must be 3-5 pixels wide—very chunky, blocky, minimal detail
- Total character should fit in roughly 40-60 pixels width, 80-100 pixels height (slightly larger than normal enemies). Very few pixels to define each feature
- NO anti-aliasing, NO smooth gradients, NO high-resolution rendering—only crisp blocky pixel edges
- Preserve the character's appearance, clothing, hair, pose, colors from the reference—simplified into chunky blocks
- Style: extremely chunky retro pixel art, vivid saturated colors, high contrast
- Background: fully transparent (PNG alpha channel)
- Character centered, full body visible, facing front
- No glow, no aura, no particles—clean minimal pixel art only
```

**注意**：若工具忽略提示词中的数字，请在「输出尺寸」设置中单独指定 64×128 或 128×128。

**验收**：主体清晰、像素风、透明背景、与主角风格一致、比普通敌人略大。

---

## Step 3：生成待机图（1 帧）

**目标**：用参考图生成待机静态图。

**操作**：直接使用 Step 2 的像素图，无需再生成。重命名为对应文件名即可。

**验收**：单张 PNG、透明背景、像素风。

---

## Step 4：生成死亡帧（2×2 精灵图）

**目标**：用参考图 + 提示词，生成死亡 4 帧（倒地序列）。

**操作**：上传 Step 2 的像素图到 Nano Banana，粘贴下方提示词。

### 死亡帧提示词（完整，4 个 Boss 通用）

```
[Overall Format]
A 2D game sprite sheet layout, arranged in a 2×2 grid (4 distinct frames: top-left, top-right, bottom-left, bottom-right). Pure transparent background (PNG alpha channel). Pixel art style.

[Character Reference]
Use the provided reference image for the character design. Match the character's appearance, clothing, hair, and style exactly from the reference. Do not alter or redesign the character. CRITICAL: Preserve the pixel art style of the reference. No anti-aliasing, no smooth gradients, no high-resolution rendering. Keep crisp pixel edges and the same pixel density.

[Crucial: Frame-by-Frame Physical Description]
Each of the 4 frames MUST show the character in a DIFFERENT pose to create a collapse sequence. They must NOT be identical. This is a BOSS character, so the collapse should be dramatic and impactful.
* Frame 1 (Top-left): Boss standing upright, intact. Imposing pose, full power stance, clothing/body in normal state.
* Frame 2 (Top-right): Beginning to collapse. Body leaning backward or staggering. Arms starting to fall. Clothing and hair beginning to scatter. Corruption energy starting to fade.
* Frame 3 (Bottom-left): Mid-fall. Body tilting sharply or kneeling. Clothing and hair disheveled, flying outward from the impact. Corruption energy dissipating rapidly.
* Frame 4 (Bottom-right): Fully collapsed. Body on ground or fully dissipating. Clothing and hair fully scattered, corruption energy completely fading. Dramatic final pose.

[Liveliness and Material Detail]
The fabric and hair (if any) must show progressive disruption in EVERY frame. For beast/entity types, show body disintegration or fading with dramatic effect. Corruption energy must visibly fade across frames. Pixel art style, crisp pixel edges, no anti-aliasing.
```

**验收**：2×2 网格、4 帧、PNG 透明背景、像素风、每帧有明显差异（站立→后仰→下落→倒地）、比普通敌人更有冲击力。

---

## Step 5：放入 assets 与命名

| 文件名 | Boss |
|--------|------|
| `assets/boss_yaowang_idle.png` | 妖王待机 |
| `assets/boss_yaowang_death.png` | 妖王死亡 |
| `assets/boss_jianmo_idle.png` | 剑魔待机 |
| `assets/boss_jianmo_death.png` | 剑魔死亡 |
| `assets/boss_danmo_idle.png` | 丹魔待机 |
| `assets/boss_danmo_death.png` | 丹魔死亡 |
| `assets/boss_huiyuan_idle.png` | 秽源待机 |
| `assets/boss_huiyuan_death.png` | 秽源死亡 |

**验收**：文件存在、透明背景、像素风、比普通敌人略大。

---

## 制作顺序建议

1. **妖王** — 首个 Boss，先验证流程
2. **剑魔** — 第二个 Boss
3. **丹魔** — 第三个 Boss
4. **秽源** — 终极 Boss，最后制作

---

## 相关文档

| 文档 | 用途 |
|------|------|
| `docs/BOSS_DESIGN.md` | Boss 身份与战斗设计 |
| `docs/SPRITE_FRAME_PROMPT_TEMPLATE.md` | 通用模板结构 |
