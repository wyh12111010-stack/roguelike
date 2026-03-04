# 🚀 快速开始：使用 Stable Diffusion 生成图标

> 5 步完成所有图标生成
> 预计总时间：6-8 小时

---

## 📋 准备清单

- [ ] Windows 10/11
- [ ] NVIDIA 显卡（GTX 1060 6GB 或更高）
- [ ] 20GB+ 硬盘空间
- [ ] 稳定的网络连接（首次安装需要下载）

---

## 🎯 5 步完成

### 第 1 步：下载 Stable Diffusion WebUI（30 分钟）

1. **下载安装包**
   ```
   访问：https://github.com/AUTOMATIC1111/stable-diffusion-webui/releases
   下载：sd.webui.zip（约 500MB）
   ```

2. **解压**
   ```
   解压到：D:\stable-diffusion-webui
   （路径不要有中文和空格）
   ```

3. **首次启动**
   ```
   双击运行：webui-user.bat
   等待自动安装（10-20 分钟）
   ```

4. **验证**
   ```
   浏览器自动打开：http://127.0.0.1:7860
   看到 WebUI 界面说明安装成功
   ```

---

### 第 2 步：下载像素艺术模型（30 分钟）

1. **下载模型**
   ```
   访问：https://civitai.com/models/120096/pixel-art-xl
   点击 Download 下载 .safetensors 文件（约 6GB）
   ```

2. **安装模型**
   ```
   将下载的文件放到：
   D:\stable-diffusion-webui\models\Stable-diffusion\
   ```

3. **重启 WebUI**
   ```
   关闭 CMD 窗口
   重新运行 webui-user.bat
   在 WebUI 左上角选择新模型
   ```

---

### 第 3 步：启用 API（5 分钟）

1. **编辑启动脚本**
   ```
   打开：D:\stable-diffusion-webui\webui-user.bat
   
   找到：set COMMANDLINE_ARGS=
   改为：set COMMANDLINE_ARGS=--api --listen
   
   保存并关闭
   ```

2. **重启 WebUI**
   ```
   关闭 CMD 窗口
   重新运行 webui-user.bat
   ```

3. **验证 API**
   ```
   访问：http://127.0.0.1:7860/docs
   看到 API 文档说明启用成功
   ```

---

### 第 4 步：批量生成图标（4-6 小时）

1. **确保 WebUI 正在运行**
   ```
   webui-user.bat 窗口保持打开
   ```

2. **生成法宝图标（13 个）**
   ```bash
   cd f:\游戏
   python scripts/batch_generate_icons.py --category fabao
   ```
   预计时间：30-60 分钟

3. **生成饰品图标（73 个）**
   ```bash
   python scripts/batch_generate_icons.py --category accessory
   ```
   预计时间：3-4 小时
   
   ⚠️ 注意：饰品配置文件还需要创建

4. **生成灵根图标（5 个）**
   ```bash
   python scripts/batch_generate_icons.py --category linggen
   ```
   预计时间：15-30 分钟
   
   ⚠️ 注意：灵根配置文件还需要创建

---

### 第 5 步：验证和接入（30 分钟）

1. **检查生成的图标**
   ```
   查看目录：
   f:\游戏\assets\icons\fabao\
   f:\游戏\assets\icons\accessory\
   f:\游戏\assets\icons\linggen\
   ```

2. **运行游戏测试**
   ```bash
   cd f:\游戏
   python main.py
   ```

3. **验证图标显示**
   - 进入战斗
   - 查看法宝图标
   - 查看饰品图标

---

## ⚙️ 优化设置（可选）

### 如果显卡性能不足

编辑 `webui-user.bat`：
```bash
set COMMANDLINE_ARGS=--api --listen --medvram
```

### 如果生成速度太慢

修改配置文件中的参数：
```json
{
  "steps": 20,  // 从 25 改为 20
  "cfg_scale": 7  // 从 8 改为 7
}
```

### 如果生成质量不满意

1. 增加采样步数：`steps: 25 → 30`
2. 调整 CFG Scale：`cfg_scale: 8 → 9`
3. 更换模型（尝试其他像素艺术模型）

---

## 🐛 常见问题

### Q1: 显存不足（Out of Memory）
**A**: 在 `webui-user.bat` 中添加 `--medvram` 或 `--lowvram`

### Q2: API 连接失败
**A**: 确保 WebUI 启动时添加了 `--api` 参数

### Q3: 生成结果不是像素风格
**A**: 确保选择了像素艺术模型（左上角下拉菜单）

### Q4: 生成速度太慢
**A**: 降低分辨率或减少采样步数

### Q5: 模型下载失败
**A**: 使用代理或从其他镜像站下载

---

## 📊 当前状态

### ✅ 已准备
- ✅ 批量生成脚本
- ✅ 法宝图标配置（13 个）
- ✅ 完整的操作指南

### ⏳ 待完成
- ⏳ 饰品图标配置（73 个）
- ⏳ 灵根图标配置（5 个）
- ⏳ 安装 Stable Diffusion
- ⏳ 下载像素艺术模型
- ⏳ 批量生成图标

---

## 🎯 下一步

### 立即开始

1. **下载 SD WebUI**
   - https://github.com/AUTOMATIC1111/stable-diffusion-webui/releases
   - 下载 `sd.webui.zip`

2. **按照上面的 5 步操作**
   - 第 1 步：安装 SD WebUI
   - 第 2 步：下载模型
   - 第 3 步：启用 API
   - 第 4 步：批量生成
   - 第 5 步：验证接入

3. **遇到问题随时告诉我**
   - 我会帮你解决

---

## 💡 提示

### 时间安排建议
- **今天**：完成第 1-3 步（安装和配置）
- **明天**：完成第 4 步（批量生成）
- **后天**：完成第 5 步（验证接入）

### 注意事项
- ⚠️ 生成过程中不要关闭 WebUI
- ⚠️ 确保电脑不会自动休眠
- ⚠️ 建议在晚上或不用电脑时运行
- ⚠️ 定期检查生成进度

---

**准备好了吗？开始第 1 步！** 🚀

下载地址：https://github.com/AUTOMATIC1111/stable-diffusion-webui/releases
