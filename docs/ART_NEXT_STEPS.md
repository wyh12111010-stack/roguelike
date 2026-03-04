# 美术资源下一步规划

> 主角、伙伴立绘已完成。本文档规划后续美术资源与待完善项。

---

## 一、当前完成状态

| 资源 | 状态 | 说明 |
|------|------|------|
| 主角待机/死亡 | ✅ 完成 | `player_idle.png`、`player_death.png`，战斗内已接入 |
| 5 位伙伴立绘 | ✅ 已接入 | `partner_xuanxiao.png` 等，村子内已绘制 |

---

## 二、待完善（可选）

### 2.2 村子玩家 sprite（可选，暂缓）

**含义**：村子里的玩家目前用**蓝色矩形**表示；改用玩家角色图显示即「村子玩家 sprite」。

**待做**：复用 `player_idle.png`（与战斗待机相同），替换矩形。**优先级低**，后续再说。

---

## 三、已完成

- ✅ 村子伙伴立绘接入（`village.py`）
- ✅ 其他 NPC 提示词（`docs/NPC_ART_WORKFLOW.md`：栖霞、玄真、铸心）
- ✅ 敌人设计文档（`docs/ENEMY_DESIGN.md`：关卡对应、动画状态、产出清单）

---

## 四、下一批美术资源（按优先级）

### 4.1 敌人精灵图

**现状**：`enemy.py` 中敌人按类型（近战、远程、突进等）用**颜色矩形**区分，无精灵图。

**待做**：
- 为各敌人类型设计/生成像素精灵（待机、死亡或简单 1–2 帧）
- 参考 `docs/CHARACTER_ART_WORKFLOW.md`、`docs/SPRITE_FRAME_PROMPT_TEMPLATE.md` 制作
- 敌人类型见 `data/enemies.json` 或 `enemy.py` 中 `TYPE_COLORS` / `TYPE_LABELS`

**建议**：先做 1–2 种代表性敌人（如近战、远程），验证流程后再扩展。

---

### 4.2 其他村子 NPC 立绘

**现状**：栖霞、玄真、铸心 无立绘，仅有房间标签。**提示词已就绪**（`docs/NPC_ART_WORKFLOW.md`）。

**待做**：按流程生成 3 张立绘，放入 assets，并在 `village.py` 中接入绘制（与伙伴类似）。

**优先级**：中，可排在敌人之后。

---

### 4.3 UI 图标、技能特效

**后续再说**。见原文档规划。

---

## 五、建议执行顺序

```
1. ✅ 村子伙伴立绘接入（已完成）
2. 敌人精灵图（1–2 种先做，验证流程，见 docs/ENEMY_DESIGN.md）
3. 其他村子 NPC 立绘（提示词已有，生成后接入）
4. 村子玩家 sprite（可选，暂缓）
5. UI 图标、技能特效（后续）
```

---

## 六、相关文档

| 文档 | 用途 |
|------|------|
| `docs/CHARACTER_ART_WORKFLOW.md` | 主角美术流程 |
| `docs/PARTNER_ART_WORKFLOW.md` | 伙伴美术流程 |
| `docs/NANOBANANA_PROMPTS.md` | 完整提示词 |
| `docs/SPRITE_FRAME_PROMPT_TEMPLATE.md` | 通用帧模板 |
| `docs/ENEMY_DESIGN.md` | 敌人设计（关卡、动画状态、产出清单） |
| `docs/NPC_ART_WORKFLOW.md` | 栖霞、玄真、铸心 MJ 提示词 |
