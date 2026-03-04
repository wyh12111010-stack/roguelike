# 项目测试与运行指南

> 解决 "python main.py 打不开" 的问题

---

## 🚀 快速开始

### 方法 1：使用批处理脚本（推荐）⭐⭐⭐⭐⭐

**双击运行**：
- `test_project.bat` - 测试项目完整性
- `run_game.bat` - 启动游戏

**优点**：
- ✅ 自动查找 Python
- ✅ 自动检测问题
- ✅ 显示详细错误信息

---

### 方法 2：手动运行

**1. 打开命令行**
- 按 `Win + R`
- 输入 `cmd`
- 回车

**2. 进入项目目录**
```cmd
cd /d f:\游戏
```

**3. 运行测试**
```cmd
python test_project.py
```

**4. 运行游戏**
```cmd
python main.py
```

---

## 🔍 常见问题

### 问题 1：找不到 Python

**现象**：
```
'python' 不是内部或外部命令
```

**解决方法**：

**方法 A：使用 py 命令**
```cmd
py test_project.py
py main.py
```

**方法 B：使用完整路径**
```cmd
D:\texlive\2023\bin\windows\python.exe test_project.py
```

**方法 C：添加 Python 到 PATH**
1. 找到 Python 安装路径
2. 右键"此电脑" → 属性 → 高级系统设置
3. 环境变量 → 系统变量 → Path → 编辑
4. 添加 Python 路径
5. 重启命令行

---

### 问题 2：缺少依赖

**现象**：
```
ModuleNotFoundError: No module named 'pygame'
```

**解决方法**：
```cmd
pip install pygame
```

或
```cmd
py -m pip install pygame
```

---

### 问题 3：导入错误

**现象**：
```
ImportError: cannot import name 'xxx'
```

**解决方法**：
1. 运行 `test_project.bat` 查看详细错误
2. 检查是否在正确的目录
3. 检查文件是否完整

---

## 📊 测试项目

### 运行完整测试

**双击运行**：
```
test_project.bat
```

**或手动运行**：
```cmd
python test_project.py
```

### 测试内容

测试脚本会检查：
1. ✓ Python 版本 (需要 3.8+)
2. ✓ pygame 库
3. ✓ 核心文件 (main.py, game.py, player.py 等)
4. ✓ 核心目录 (core, systems, scenes 等)
5. ✓ 核心模块导入
6. ✓ 新增文件 (resonance_system.py 等)
7. ✓ 新增模块导入
8. ✓ 游戏初始化
9. ✓ 数据文件
10. ✓ 工具脚本

### 测试结果

**全部通过**：
```
测试完成: 30 通过, 0 失败
✓ 所有测试通过！项目可以正常运行。
```

**有失败**：
```
测试完成: 25 通过, 5 失败

失败的测试:
  - 模块导入: resonance_system
  - ...
```

---

## 🎮 运行游戏

### 方法 1：批处理脚本（推荐）

**双击运行**：
```
run_game.bat
```

### 方法 2：手动运行

```cmd
cd /d f:\游戏
python main.py
```

### 方法 3：使用 py 命令

```cmd
cd /d f:\游戏
py main.py
```

---

## 🔧 故障排除

### 步骤 1：运行测试

```cmd
test_project.bat
```

### 步骤 2：查看错误

测试脚本会显示详细的错误信息。

### 步骤 3：根据错误修复

**缺少文件**：
- 检查文件是否存在
- 检查文件名是否正确

**导入错误**：
- 检查模块是否完整
- 检查是否有语法错误

**依赖缺失**：
- 安装缺失的依赖

---

## 📝 文件说明

| 文件 | 说明 |
|------|------|
| `test_project.py` | 项目测试脚本（Python） |
| `test_project.bat` | 项目测试脚本（批处理） |
| `run_game.bat` | 游戏启动脚本（批处理） |
| `main.py` | 游戏主程序 |

---

## 💡 建议

### 开发时

1. **先运行测试**
   ```
   test_project.bat
   ```

2. **确认全部通过**
   ```
   ✓ 所有测试通过！
   ```

3. **再运行游戏**
   ```
   run_game.bat
   ```

### 遇到问题时

1. **运行测试**
2. **查看错误信息**
3. **根据提示修复**
4. **重新测试**

---

## 🚀 下一步

**测试通过后**：
1. 运行游戏
2. 测试美术资源
3. 测试共鸣系统
4. 测试新功能

**测试失败时**：
1. 查看错误信息
2. 修复问题
3. 重新测试

---

**现在请双击运行 `test_project.bat` 测试项目！** 😊
