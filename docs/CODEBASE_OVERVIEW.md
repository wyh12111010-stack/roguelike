# 代码库概览

> 供 context 紧张时快速回顾。**项目整体太大时**，先读本文再 @ 具体文件。

---

## 快速入口（项目大时优先看）

| 要改什么 | 先看 |
|----------|------|
| 战斗/关卡 | `game.py`、`enemy.py`、`levels.py`、`data/levels.json` |
| **路线图与计划** | `docs/PROJECT_ROADMAP.md` |
| 村子/伙伴 | `village.py`、`partner.py`、`partner_skills.py` |
| 灵根/法宝/饰品 | `linggen.py`、`fabao.py`、`accessory.py`、`unlock.py` |
| 存档/局外成长 | `save.py`、`meta.py` |
| 美术流程 | `docs/CHARACTER_ART_WORKFLOW.md`、`docs/PARTNER_ART_WORKFLOW.md`、`docs/NANOBANANA_PROMPTS.md` |

**大项目使用建议**：一次只 @ 1–2 个相关文件；复杂任务拆成多轮对话；新主题开新对话。

**冒烟测试**：`python -m tools.smoke_test` 验证核心模块与 Game 初始化。

---

**开发惯例**：设计实现时对标 Tiny Rogues（见 `.cursor/rules/tiny-rogues-reference.mdc`），无论 token 是否到上限，写入代码前应包含「Tiny Rogues 怎么做 → 与本项目差异 → 取舍落地」的思考步骤。

---

## 一、核心流程

```
main.py → Game (game.py)
  ├─ scene: village | combat
  ├─ village: 选灵根、选法宝、解锁、外出
  └─ combat: 关卡战斗 → 路线选择 → 商店/下一关 → 身陨/凯旋 → 回村
```

---

## 二、架构目录（见 docs/TECH_ARCHITECTURE.md）

| 目录 | 职责 |
|------|------|
| `core/` | EventBus、GameState、SceneManager |
| `nodes/` | 节点类型注册、NodeHandler 基类、combat/shop |
| `scenes/` | Scene 基类、VillageScene（村子 update/draw） |
| `systems/` | RouteSystem、CombatSystem（战斗 update/draw） |
| `ui/` | CombatLogUI、input_handler（输入处理） |

## 三、关键文件

| 文件 | 职责 |
|------|------|
| `game.py` | 主逻辑：场景切换、事件分发、关卡加载、路线选择（约 684 行） |
| `player.py` | 玩家：移动、攻击、灵根/法宝、受击 |
| `enemy.py` | 敌人：6 种类型 + melee_hitrun 行为、大关专属池、投射物、AOE |
| `levels.py` | 关卡配置、路线树 ROUTE_TREE、DEMO_ROUTE_TREE |
| `village.py` | 村子 UI 绘制、VILLAGE_UI 点击区域 |
| `linggen.py` | 灵根列表（火/水/雷/冰/毒/无） |
| `fabao.py` | 法宝列表（剑/符/杖），攻击方式参数 |
| `attribute.py` | 属性枚举、相合/反应 |
| `meta.py` | 局外数据：道韵、解锁、伙伴羁绊、局外成长、成就 |
| `save.py` | 存档持久化 |
| `unlock.py` | 解锁配置：灵根/法宝/饰品道韵价格、局外成长阶梯 |
| `setting.py` | 世界观、货币、道韵/灵石获取 |
| `shop.py` | 商店商品 |
| `story.py` | 序章、结局文本 |
| `achievement.py` | 成就列表、unlock_achievement |

---

## 四、世界观要点（setting.py）

- **村民**：村中皆是修真界**最顶尖的大能**
- **村子**：栖霞村，世界意念最后反抗，结界内净土
- **反派**：秽源，纯粹恶意，侵染人、妖
- **主角**：轮回之力，不被污染，唯一能自由出入之人

---

## 五、已实现 vs 待实现

| 模块 | 状态 |
|------|------|
| 灵根/法宝选择 | ✓ |
| 路线选择（战斗/商店/休息/宝箱） | ✓ |
| 6 种敌人类型 + hitrun + 大关专属池 | ✓ |
| 演示关卡 | ✓ |
| 村民/伙伴 | ✓（治疗、羁绊、充能技能、手动选择） |
| 局外成长 | ✓（灵根/法宝/饰品解锁、饰品槽、商店刷新、开局饰品、生命/灵力、丹药上限） |
| 休息/宝箱/精英/商店节点 | ✓ |
| 栖霞成就 | ✓（框架已实现，条目待补充） |
| 事件节点 | ✓（event_events.py + _enter_event） |
| Boss 房 | ✓ |
| 难度星级 | 已拍板不做（普通/精英/Boss 即涵盖难度） |

---

## 六、设计文档索引

- `WORLDVIEW_DESIGN.md` - 世界观
- `NODE_ROUTE_DESIGN.md` - 节点与路线（已拍板：事件/休息/宝箱/精英/Boss 房）
- `NODE_TYPES_DESIGN.md` - 六类节点方案（战斗/商店/事件/休息/宝箱/精英）
- `PARTNER_VILLAGER_INITIAL.md` - 村民与伙伴初案（顶尖大能）
- `FABAO_ACCESSORY_DESIGN.md` - 法宝（死亡细胞式）+ 饰品（品质+可升级、局内、槽位局外）
- `META_GROWTH.md` - 局外成长汇总（法宝池、槽位、开局携带、商店刷新等）
- `CURRENCY_DESIGN.md` - 货币
- `PENDING_DIRECTIONS.md` - 待处理方向
- `TECH_ARCHITECTURE.md` - 技术架构（core/nodes/scenes/systems）
- `ACHIEVEMENT_TODO.md` - 成就条目待规划
- `PROJECT_ROADMAP.md` - **从游戏到成熟项目路线图**（敌人状态、架构、分阶段计划）
- `BOSS_DESIGN.md` - **Boss 战斗设计**（专属招式、阶段机制、与小怪差异化）
