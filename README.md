# 修仙肉鸽 - MVP

一个基于Pygame的修仙题材Roguelike游戏。

## 游戏特色

- 修仙题材的Roguelike玩法
- 灵根系统（金木水火土）
- 法宝系统（不同攻击方式）
- 饰品系统（特殊效果）
- 村子系统（升级和购买）
- 关卡挑战（9层+Boss）

## 技术栈

- Python 3.11+
- Pygame 2.6+

## 安装和运行

### 1. 克隆仓库
```bash
git clone https://github.com/你的用户名/修仙肉鸽.git
cd 修仙肉鸽
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行游戏
```bash
python main.py
```

## 游戏操作

- **WASD** - 移动
- **鼠标左键** - 攻击
- **E** - 使用技能
- **空格/Shift** - 闪避
- **F10** - 设置
- **ESC** - 返回

## 项目结构

```
修仙肉鸽/
├── main.py              # 游戏入口
├── game.py              # 游戏主逻辑
├── player.py            # 玩家类
├── enemy.py             # 敌人类
├── config.py            # 配置文件
├── core/                # 核心系统
├── systems/             # 游戏系统
├── ui/                  # UI组件
├── nodes/               # 节点系统
└── docs/                # 文档

```

## 开发状态

- [x] 基础游戏循环
- [x] 玩家移动和攻击
- [x] 敌人AI
- [x] 灵根系统
- [x] 法宝系统
- [x] 饰品系统
- [x] 村子系统
- [x] 关卡系统
- [x] Boss战
- [x] 存档系统
- [ ] 音频系统（待完善）
- [ ] 更多内容

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 致谢

- 参考了Tiny Rogues的设计
- 使用Pygame框架
