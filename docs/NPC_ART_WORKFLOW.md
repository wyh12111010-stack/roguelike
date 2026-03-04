# 村子 NPC 美术流程（栖霞、玄真、铸心）

> 3 位功能性 NPC：栖霞（引导）、玄真（灵根）、铸心（法宝）。流程与伙伴一致，每人 1 张站立图。

---

## 目标

- 为栖霞、玄真、铸心制作村子立绘
- 每人 **1 种状态**：站立（单帧或 4 帧轻微呼吸）
- 展示于灵根殿、炼器坊、中央广场

---

## 约束

| 项目 | 约束 |
|------|------|
| 状态数量 | 每人 1 种（站立） |
| 帧数 | 1 帧或 4 帧（站立呼吸） |
| 展示场景 | 灵根殿、炼器坊、中央广场 |
| 输出尺寸 | 与伙伴一致，32×32 或 64×64 单帧 |
| 风格 | 与主角、伙伴一致的像素风 |

---

## 流程

```
Step 1: MJ 生成原图（每人 1 张）
  → Step 2: 转像素图（见 docs/NANOBANANA_PROMPTS.md 方案 A）
  → Step 3: 可选 4 帧站立呼吸（见 docs/SPRITE_FRAME_PROMPT_TEMPLATE.md）
  → Step 4: 放入 assets，命名 npc_{id}.png
```

---

## Step 1：MJ 生成原图

**主角参考图 URL**（保持风格一致）：
```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc&
```

### 栖霞（村中守护者）

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A serene Chinese female village guardian, wise and gentle, wearing flowing white and pale gold robes, long dark hair with simple ornament, calm expression, no weapon, arms relaxed, standing calmly, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

### 玄真（灵根殿主）

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A scholarly Chinese male elder, spirit root hall master, wearing grey and white daoist robes with subtle elemental motifs, grey beard, dignified expression, holding a spirit root scroll or jade slip, standing calmly, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

### 铸心（炼器宗师）

```
https://cdn.discordapp.com/attachments/1475335738768756769/1475451016378843199/gutinhooof7870_A_young_Chinese_male_cultivator_in_xianxia_style_bb1b02cc-7d50-419b-99c0-f60ecfd7e656.png?ex=699e3116&is=699cdf96&hm=b4432f589c34b2dc4a499cac114f850efac94e3cfc5d9319168231e13a9e46bc& A rugged Chinese male blacksmith, forging master, wearing dark brown and copper-toned robes, short hair, soot-smudged face, strong arms, holding a hammer or forging tool (optional), determined expression, standing calmly, full body shot, facing front, character centered with padding from edges, plain solid color background, vivid saturated colors, anime style, clean lines, no special effects, no aura, no glow, no particles --ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils
```

**MJ 参数**：`--ar 1:1 --niji 7 --s 250 --no glow aura energy effects sparkles particles swirling tendrils`。不要加 `--p`。

---

## Step 2：转像素图

与伙伴流程相同，见 `docs/NANOBANANA_PROMPTS.md` 第二节（推荐方案 A 粗像素）。

---

## Step 3：站立图

- **方案 A**：直接使用 Step 2 的像素图，重命名为 `npc_{id}.png`
- **方案 B**：用 4 帧站立呼吸模板生成 2×2 精灵图，见 `docs/NANOBANANA_PROMPTS.md` 第三节「待机（伙伴，4 帧站立呼吸）」

---

## Step 4：放入 assets 与命名

| 文件名 | NPC |
|--------|-----|
| `assets/npc_qixia.png` | 栖霞 |
| `assets/npc_xuanzhen.png` | 玄真 |
| `assets/npc_zhuxin.png` | 铸心 |

**注意**：当前村子代码仅绘制伙伴立绘，NPC 立绘需在 `village.py` 中接入（与伙伴类似）。接入前可先放入 assets。

---

## 相关文档

| 文档 | 用途 |
|------|------|
| `docs/PARTNER_ART_WORKFLOW.md` | 伙伴美术流程（同结构） |
| `docs/NANOBANANA_PROMPTS.md` | 转像素与帧模板 |
| `docs/PARTNER_VILLAGER_INITIAL.md` | 村民身份设定 |
