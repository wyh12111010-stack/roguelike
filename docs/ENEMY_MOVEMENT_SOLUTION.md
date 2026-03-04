# 敌人/Boss 移动动画解决方案

## 问题

敌人和 Boss 的移动序列帧很难把控：
- 方向多（8 方向或 360°）
- 帧数多（每个方向 4-8 帧）
- 制作量大（6 种敌人 × 8 方向 × 4 帧 = 192 帧）
- 视觉效果难统一

---

## 🎯 推荐方案：不做移动帧

### 学习 Tiny Rogues

Tiny Rogues 的敌人：
- ✅ 只有待机动画（1-4 帧轻微晃动）
- ❌ 没有移动动画
- ✅ 移动时直接平移待机帧

### 为什么可行？

1. **玩家关注点**：
   - 玩家看的是弹幕轨迹
   - 不是敌人的脚步动作

2. **像素游戏惯例**：
   - 大部分像素 Roguelike 都这样做
   - Enter the Gungeon、Nuclear Throne 等

3. **性能和制作成本**：
   - 节省 90% 的美术工作量
   - 更好的性能

---

## 💡 增强方案：程序化移动效果

如果觉得直接平移太僵硬，可以用代码添加效果：

### 效果 1：上下晃动（模拟走路）

```python
# 移动时轻微上下晃动
bob_offset = math.sin(move_timer * 10) * 2  # 振幅 2 像素
screen.blit(frame, (x, y + bob_offset))
```

### 效果 2：轻微拉伸（模拟步伐）

```python
# 移动时轻微拉伸
stretch = 1 + abs(math.sin(move_timer * 10)) * 0.05  # ±5%
w, h = frame.get_size()
stretched = pygame.transform.scale(frame, (int(w * stretch), h))
```

### 效果 3：残影效果

```python
# 移动时留下淡淡的残影
if is_moving:
    trail_alpha = 100
    trail_frame = frame.copy()
    trail_frame.set_alpha(trail_alpha)
    screen.blit(trail_frame, (prev_x, prev_y))
```

### 效果 4：速度线

```python
# 快速移动时显示速度线
if speed > threshold:
    pygame.draw.line(screen, (255, 255, 255, 100), 
                     (x, y), (x - dx*5, y - dy*5), 2)
```

---

## 🔧 完整实现

已创建 `tools/procedural_movement.py`，包含：
- ✅ 待机动画播放
- ✅ 移动时上下晃动
- ✅ 移动时轻微拉伸
- ✅ 可选的旋转/残影效果

### 使用方法

```python
from tools.procedural_movement import Enemy

enemy = Enemy(x, y)

# 更新
enemy.update(dt, target_x, target_y)

# 绘制（自动处理移动效果）
enemy.draw(screen, idle_frames)
```

---

## 📊 方案对比

| 方案 | 制作量 | 效果 | 性能 | 推荐度 |
|------|--------|------|------|--------|
| **不做移动帧** | 极少 | 简洁 | 最好 | ⭐⭐⭐⭐⭐ |
| **程序化效果** | 少 | 自然 | 好 | ⭐⭐⭐⭐⭐ |
| **8 方向移动帧** | 大 | 精细 | 中 | ⭐⭐ |
| **360° 旋转** | 中 | 流畅 | 中 | ⭐⭐⭐ |

---

## 🎨 最终建议

### 敌人（6 种）
- ✅ 只做待机帧（4 帧或 32 帧）
- ✅ 移动时用程序化效果
- ❌ 不做移动帧

### Boss（4 个）
- ✅ 只做待机帧（4 帧或 32 帧）
- ✅ 移动时用程序化效果
- ✅ 可选：攻击前摇动画（2-3 帧）

### 特殊情况
如果某个 Boss 有特殊移动方式（如飞行、传送），可以单独做：
- 传送：淡入淡出效果（程序化）
- 飞行：上下浮动（程序化）
- 冲刺：残影 + 速度线（程序化）

---

## 🧪 测试

运行测试脚本查看效果：

```bash
python tools/procedural_movement.py
```

- 鼠标移动控制目标点
- 敌人会追踪并显示移动效果
- 观察上下晃动和拉伸效果

---

## 💡 总结

**不做移动帧 + 程序化效果 = 最佳方案**

- 节省 90% 美术工作量
- 效果自然流畅
- 符合像素 Roguelike 惯例
- 性能最优

**现在你只需要专注做好待机动画即可！** 🎉
