# Stable Diffusion 本地部署和使用指南

> 方案 1：完全本地，免费无限制
> 预计时间：安装 1-2 小时，生成 4-6 小时

---

## 📋 准备工作

### 系统要求
- **操作系统**：Windows 10/11
- **显卡**：NVIDIA GTX 1060 6GB 或更高（推荐 RTX 系列）
- **内存**：16GB RAM（推荐）
- **硬盘空间**：20GB+（模型文件较大）
- **Python**：3.10.6（推荐）

### 检查显卡
```bash
# 打开 CMD，运行
nvidia-smi
```

如果显示显卡信息，说明 NVIDIA 驱动已安装。

---

## 🚀 第一步：安装 Stable Diffusion WebUI

### 方法 A：一键安装包（推荐）

1. **下载安装包**
   - 访问：https://github.com/AUTOMATIC1111/stable-diffusion-webui/releases
   - 下载最新的 `sd.webui.zip`（约 500MB）

2. **解压**
   - 解压到任意目录，如 `D:\stable-diffusion-webui`
   - 路径不要有中文和空格

3. **首次启动**
   ```bash
   # 双击运行
   webui-user.bat
   ```
   
   - 首次启动会自动下载依赖（10-20 分钟）
   - 下载基础模型（约 4GB）
   - 完成后会自动打开浏览器：http://127.0.0.1:7860

### 方法 B：手动安装（备选）

```bash
# 1. 克隆仓库
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui

# 2. 运行安装脚本
webui-user.bat
```

---

## 🎨 第二步：安装像素艺术模型

### 推荐模型：Pixel Art Diffusion XL

1. **下载模型**
   - 访问：https://civitai.com/models/120096/pixel-art-xl
   - 点击 "Download" 下载 `.safetensors` 文件（约 6GB）
   - 或者搜索其他像素艺术模型：
     - "Pixel Art Style"
     - "Retro Diffusion"
     - "16bit Diffusion"

2. **安装模型**
   ```
   # 将下载的 .safetensors 文件放到：
   stable-diffusion-webui/models/Stable-diffusion/
   ```

3. **重启 WebUI**
   - 关闭 CMD 窗口
   - 重新运行 `webui-user.bat`
   - 在 WebUI 左上角选择新安装的模型

---

## 🔧 第三步：配置 API

### 启用 API 模式

1. **编辑启动脚本**
   ```bash
   # 打开 webui-user.bat，找到这行：
   set COMMANDLINE_ARGS=
   
   # 修改为：
   set COMMANDLINE_ARGS=--api --listen
   ```

2. **重启 WebUI**
   ```bash
   webui-user.bat
   ```

3. **测试 API**
   - 打开浏览器：http://127.0.0.1:7860/docs
   - 应该看到 API 文档页面

---

## 🤖 第四步：批量生成图标

### 使用自动化脚本

我已经为你准备了批量生成脚本，现在运行：

```bash
# 1. 确保 SD WebUI 正在运行
# 2. 运行批量生成脚本
cd f:\游戏
python scripts/batch_generate_icons.py
```

### 脚本功能
- ✅ 自动读取配置文件
- ✅ 批量调用 SD API
- ✅ 自动保存图片
- ✅ 进度显示
- ✅ 错误重试

---

## 📊 生成计划

### 第 1 批：法宝图标（21 个）
```bash
python scripts/batch_generate_icons.py --category fabao
```
- 预计时间：1-2 小时
- 输出目录：`assets/icons/fabao/`

### 第 2 批：饰品图标（73 个）
```bash
python scripts/batch_generate_icons.py --category accessory
```
- 预计时间：3-4 小时
- 输出目录：`assets/icons/accessory/`

### 第 3 批：灵根图标（5 个）
```bash
python scripts/batch_generate_icons.py --category linggen
```
- 预计时间：15-30 分钟
- 输出目录：`assets/icons/linggen/`

---

## ⚙️ 优化设置

### 提升生成速度

1. **降低分辨率**（如果显卡性能不足）
   - 在配置文件中将 48x48 改为 32x32
   - 后期可以用工具放大

2. **减少采样步数**
   - Steps: 25 → 20（速度 +20%，质量略降）
   - Steps: 25 → 15（速度 +40%，质量明显降）

3. **使用更快的采样器**
   - Euler a → DPM++ 2M Karras（速度 +30%）

4. **批量生成**
   - Batch size: 1 → 4（如果显存足够）

### 提升生成质量

1. **增加采样步数**
   - Steps: 25 → 30（质量 +10%，速度 -20%）

2. **调整 CFG Scale**
   - CFG Scale: 8 → 7（更自然）
   - CFG Scale: 8 → 9（更符合提示词）

3. **使用高分辨率修复**
   - 启用 Hires.fix
   - Upscaler: Latent
   - Upscale by: 2

---

## 🐛 常见问题

### 问题 1：显存不足（Out of Memory）
**解决方案**：
```bash
# 在 webui-user.bat 中添加：
set COMMANDLINE_ARGS=--api --listen --medvram
# 或者更激进：
set COMMANDLINE_ARGS=--api --listen --lowvram
```

### 问题 2：生成速度太慢
**解决方案**：
- 降低分辨率（48x48 → 32x32）
- 减少采样步数（25 → 20）
- 使用更快的采样器（DPM++ 2M Karras）

### 问题 3：生成结果不理想
**解决方案**：
- 调整提示词（增加细节描述）
- 调整 CFG Scale（7-9 之间）
- 更换模型（尝试其他像素艺术模型）
- 增加采样步数（25 → 30）

### 问题 4：API 连接失败
**解决方案**：
```bash
# 检查 WebUI 是否启用了 API
# 访问：http://127.0.0.1:7860/docs
# 如果无法访问，重新启动 WebUI 并确保添加了 --api 参数
```

### 问题 5：模型加载失败
**解决方案**：
- 检查模型文件是否完整（约 6GB）
- 检查文件路径是否正确
- 尝试重新下载模型

---

## 📈 预计时间表

### 总时间：6-8 小时

| 阶段 | 任务 | 时间 |
|------|------|------|
| 1 | 安装 SD WebUI | 1-2 小时 |
| 2 | 下载和安装模型 | 30 分钟 |
| 3 | 配置和测试 | 30 分钟 |
| 4 | 生成法宝图标（21） | 1-2 小时 |
| 5 | 生成饰品图标（73） | 3-4 小时 |
| 6 | 生成灵根图标（5） | 15-30 分钟 |
| 7 | 后期处理和接入 | 1-2 小时 |

---

## 🎯 下一步

### 立即开始

1. **下载 SD WebUI**
   - https://github.com/AUTOMATIC1111/stable-diffusion-webui/releases
   - 下载 `sd.webui.zip`

2. **解压并启动**
   ```bash
   # 解压到 D:\stable-diffusion-webui
   # 双击运行 webui-user.bat
   ```

3. **等待安装完成**
   - 首次启动需要 10-20 分钟
   - 会自动下载依赖和基础模型

4. **下载像素艺术模型**
   - https://civitai.com/models/120096/pixel-art-xl
   - 放到 `models/Stable-diffusion/` 目录

5. **启用 API 并重启**
   - 编辑 `webui-user.bat`
   - 添加 `--api --listen` 参数

6. **运行批量生成脚本**
   ```bash
   python scripts/batch_generate_icons.py
   ```

---

## 💡 提示

### 优势
- ✅ 完全免费
- ✅ 无限制生成
- ✅ 完全可控
- ✅ 离线使用
- ✅ 隐私安全

### 注意事项
- ⚠️ 首次安装需要时间
- ⚠️ 需要一定的显卡性能
- ⚠️ 需要 20GB+ 硬盘空间
- ⚠️ 生成速度取决于显卡

---

**准备好了吗？开始安装 Stable Diffusion！** 🚀

有任何问题随时告诉我！
