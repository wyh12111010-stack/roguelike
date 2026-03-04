# 技术架构设计

> 扩展性强、解耦性强，便于后续添加新功能。

---

## 一、分层结构

```
┌─────────────────────────────────────────────────────────┐
│  表现层 (Presentation)                                   │
│  main.py → 场景 draw / UI 绘制                          │
├─────────────────────────────────────────────────────────┤
│  场景层 (Scenes)                                         │
│  VillageScene, CombatScene, NodeScene(战斗/商店/事件…)   │
├─────────────────────────────────────────────────────────┤
│  节点层 (Nodes)                                          │
│  节点类型注册表 + 各类型 Handler 实现                     │
├─────────────────────────────────────────────────────────┤
│  系统层 (Systems)                                        │
│  路线系统、战斗系统、商店系统、事件系统…                  │
├─────────────────────────────────────────────────────────┤
│  核心层 (Core)                                           │
│  GameState、EventBus、SceneManager                       │
├─────────────────────────────────────────────────────────┤
│  数据层 (Data)                                           │
│  levels.py、config、setting、unlock、meta               │
└─────────────────────────────────────────────────────────┘
```

---

## 二、核心层 (core/)

### 2.1 EventBus - 事件总线

**职责**：模块间解耦通信，发布/订阅模式。

```python
# 用法
EventBus.emit("node_complete", node_id=3, result={"lingshi": 50})
EventBus.on("node_complete", callback)
```

**事件类型**（可扩展）：
- `scene_change` - 场景切换
- `node_enter` - 进入节点
- `node_complete` - 节点完成
- `player_damage` - 玩家受伤
- `player_death` - 玩家死亡
- `enemy_kill` - 击杀敌人
- `route_select` - 路线选择

### 2.2 GameState - 游戏状态

**职责**：集中管理全局状态，单例。

```python
state = GameState.get()
state.current_scene
state.current_node_index
state.player
state.run_data  # 本局数据：灵石、击杀数、关卡进度等
state.meta     # 局外数据：道韵、解锁等
```

### 2.3 SceneManager - 场景管理

**职责**：场景注册、切换、当前场景 update/draw。

```python
SceneManager.register("village", VillageScene)
SceneManager.register("combat", CombatScene)
SceneManager.switch("village")
SceneManager.update(dt)
SceneManager.draw(screen)
```

---

## 三、节点层 (nodes/)

### 3.1 设计原则

- **节点类型**：combat、shop、event、rest、chest、elite、boss
- **统一接口**：每个类型实现 `NodeHandler` 基类
- **注册表**：`NODE_REGISTRY` 注册类型 → Handler 类

### 3.2 NodeHandler 接口

```python
class NodeHandler:
    node_type: str  # combat/shop/event/rest/chest/elite/boss
    
    def enter(self, ctx: NodeContext) -> None:
        """进入节点时调用"""
    
    def update(self, dt: float, ctx: NodeContext) -> NodeStatus:
        """每帧更新，返回 NodeStatus.CONTINUE / COMPLETE / FAIL"""
    
    def draw(self, screen, ctx: NodeContext) -> None:
        """绘制"""
    
    def handle_event(self, event, ctx: NodeContext) -> bool:
        """处理输入，返回 True 表示已消费"""
    
    def exit(self, ctx: NodeContext) -> dict:
        """离开节点时返回结果（奖励/消耗等）"""
```

### 3.3 NodeContext

```python
@dataclass
class NodeContext:
    node_index: int      # 当前节点索引
    node_type: str       # 节点类型
    node_config: dict    # 节点配置（可选）
    player: Player
    run_data: RunData    # 本局数据
    meta: MetaData       # 局外数据
```

### 3.4 扩展新节点

只需：
1. 新建 `nodes/xxx.py`，继承 `NodeHandler`
2. 在 `nodes/registry.py` 中 `register("xxx", XxxHandler)`
3. 在路线配置中指定节点类型

---

## 四、系统层 (systems/)

### 4.1 RouteSystem - 路线系统

**职责**：根据路线树、当前节点，返回可选下一节点列表。

```python
options = RouteSystem.get_next_options(current_node_index, route_tree)
# 返回 [(node_id, node_type, rect, name, difficulty, reward_hint), ...]
```

### 4.2 CombatSystem - 战斗系统

**职责**：敌人生成、碰撞检测、伤害结算、奖励发放。可抽离自 game.py。

### 4.3 ShopSystem - 商店系统

**职责**：商品列表、购买逻辑、刷新逻辑。

---

## 五、场景层 (scenes/)

### 5.1 场景接口

```python
class Scene:
    def enter(self) -> None: ...
    def update(self, dt: float) -> None: ...
    def draw(self, screen) -> None: ...
    def handle_event(self, event) -> bool: ...
    def exit(self) -> None: ...
```

### 5.2 场景列表

| 场景 | 职责 |
|------|------|
| VillageScene | 村子：选灵根、选法宝、解锁、外出 |
| CombatScene | 战斗：承载节点执行，当节点为 combat 时运行战斗 |
| NodeScene | 通用节点场景：根据当前节点类型委托给对应 Handler |

**简化**：CombatScene 可合并为 NodeScene 的一种，当 node_type=combat 时执行战斗逻辑。

---

## 六、数据流

```
配置(levels.py) → RouteTree → RouteSystem.get_next_options
                                    ↓
GameState → 当前节点 → NodeRegistry.get_handler(node_type) → Handler.enter/update/draw
                                    ↓
NodeHandler.exit → 结果 → EventBus.emit("node_complete") → 更新 RunData
                                    ↓
RouteSystem.get_next_options → 选路 → 进入下一节点
```

---

## 七、目录结构

```
f:\游戏\
├── main.py              # 入口
├── config.py            # 屏幕、颜色等
├── setting.py           # 世界观、货币
├── core/                # 核心层
│   ├── __init__.py
│   ├── event_bus.py     # 事件总线
│   ├── game_state.py    # 游戏状态
│   └── scene_manager.py # 场景管理
├── nodes/               # 节点层
│   ├── __init__.py
│   ├── base.py          # NodeHandler 基类、NodeContext
│   ├── registry.py      # 节点类型注册表
│   ├── combat.py        # 战斗节点
│   ├── shop.py          # 商店节点
│   └── ...              # 后续：event, rest, chest, elite, boss
├── scenes/              # 场景层
│   ├── __init__.py
│   ├── base.py          # Scene 基类
│   ├── village.py       # 村子场景
│   └── run.py           # 闯关场景（含节点执行）
├── systems/             # 系统层（可选，后续抽离）
│   ├── __init__.py
│   └── route.py         # 路线系统
├── player.py
├── enemy.py
├── levels.py
├── linggen.py
├── fabao.py
├── meta.py
├── save.py
└── ...
```

---

## 八、扩展新功能示例

### 添加新节点类型「事件」

1. `nodes/event.py`：实现 `EventNodeHandler`
2. `nodes/registry.py`：`register("event", EventNodeHandler)`
3. 路线配置中：`{3: [{"type": "event", "id": "event_01"}, ...]}`

### 添加新场景

1. `scenes/xxx.py`：实现 `XxxScene`
2. `SceneManager.register("xxx", XxxScene)`
3. `EventBus.emit("scene_change", scene="xxx")`

---

## 九、实现状态

| 模块 | 状态 |
|------|------|
| core/ | ✓ EventBus、GameState、SceneManager |
| nodes/ | ✓ base、registry、combat、shop 注册 |
| scenes/ | ✓ base Scene 接口 |
| systems/ | ✓ RouteSystem |
| game.py | ✓ 接入 EventBus、GameState，保持可运行 |

**扩展新节点**：新建 `nodes/xxx.py`，`@register_node("xxx")`，在路线配置中指定即可。
