# 智能去背景工具使用指南

## 问题

人物中有白色，背景也是白色，如何只去除背景而保留人物中的白色？

## 解决方案

### 方法 1：智能泛洪填充（推荐）

**原理**：
- 从图片四个角开始泛洪填充
- 只标记外围连续的背景区域
- 保留人物内部的所有颜色（包括白色）

**优势**：
- ✅ 保留人物内部的白色
- ✅ 自动识别背景边界
- ✅ 适合像素画

---

## 使用方法

### 单个文件

```bash
# 基本用法
python tools/remove_bg.py input.png output.png

# 调整容差（更激进）
python tools/remove_bg.py input.png output.png 40
```

### 批量处理

```bash
# 处理整个目录
python tools/remove_bg.py nanobanana_in/ assets/

# 自定义容差
python tools/remove_bg.py nanobanana_in/ assets/ 40
```

---

## 参数说明

### tolerance（容差）

控制颜色相似度判断：
- **10-20**：保守，只去除纯白背景
- **30**（默认）：平衡，适合大多数情况
- **40-50**：激进，去除浅灰色背景

**建议**：
- 纯白背景：tolerance=20
- 浅灰背景：tolerance=40
- 有噪点的背景：tolerance=50

---

## 工作原理

### 智能泛洪填充

```
1. 从四个角开始
   ┌─────────┐
   ●         ●  ← 起点
   │  人物   │
   ●         ●
   └─────────┘

2. 向内扩散，遇到人物边缘停止
   ┌─────────┐
   ░░░░░░░░░░  ← 背景（标记）
   ░░┌───┐░░
   ░░│人物│░░  ← 人物（保留）
   ░░└───┘░░
   ░░░░░░░░░░
   └─────────┘

3. 只去除标记的背景
   透明背景
   ┌───┐
   │人物│  ← 内部白色保留
   └───┘
```

---

## 示例

### 示例 1：碧落精灵图

```bash
# 输入：白色背景，人物有白色衣服
python tools/remove_bg.py "F:\游戏\美术素材\碧落（丹道宗师）\sprite_sheet (1).png" "F:\游戏\assets\partner_biluo_transparent.png"
```

### 示例 2：批量处理所有角色

```bash
# 处理整个美术素材目录
python tools/remove_bg.py "F:\游戏\美术素材\" "F:\游戏\assets\" 30
```

---

## 对比：两种方法

### 方法 1：智能泛洪（推荐）

```python
remove_background_smart(input, output, tolerance=30)
```

- ✅ 保留人物内部白色
- ✅ 只去除外围背景
- ✅ 适合像素画

### 方法 2：色键去除（不推荐）

```python
remove_background_color_key(input, output, bg_color=(255,255,255))
```

- ❌ 会去除人物内部的白色
- ❌ 可能破坏人物细节
- ⚠️  仅适合人物完全不含背景色的情况

---

## 常见问题

### Q1：人物边缘有白边

**原因**：容差太小
**解决**：增加 tolerance 到 40-50

```bash
python tools/remove_bg.py input.png output.png 50
```

### Q2：人物内部被挖空

**原因**：人物内部有与背景相连的区域
**解决**：
1. 降低 tolerance 到 20
2. 或手动修复（Photoshop/GIMP）

### Q3：背景没去干净

**原因**：背景颜色不均匀
**解决**：增加 tolerance 或多次处理

---

## 高级用法

### 预览效果（不保存）

```python
from tools.remove_bg import remove_background_smart
from PIL import Image

# 处理
remove_background_smart("input.png", "temp.png", tolerance=30)

# 预览
img = Image.open("temp.png")
img.show()
```

### 自定义起点

如果四个角不是背景，可以修改代码指定其他起点：

```python
# 在 remove_bg.py 中修改
corners = [
    (width // 2, 0),  # 顶部中间
    (width // 2, height - 1),  # 底部中间
]
```

---

## 总结

**推荐流程**：
1. 用智能泛洪填充去背景
2. tolerance 从 30 开始尝试
3. 如果效果不好，调整到 20-50
4. 批量处理所有角色

**优势**：
- 自动保留人物内部白色
- 适合像素画
- 支持批量处理

**现在可以放心去除背景了！** 😊
