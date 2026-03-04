# 📦 上传到GitHub指南

## 🎯 步骤1：在GitHub创建仓库

1. 打开 https://github.com
2. 点击右上角的 "+" → "New repository"
3. 填写信息：
   - Repository name: `修仙肉鸽` 或 `xiuxian-roguelike`
   - Description: `修仙题材的Roguelike游戏`
   - Public 或 Private（你选择）
   - **不要**勾选 "Add a README file"（我们已经有了）
   - **不要**勾选 "Add .gitignore"（我们已经有了）
4. 点击 "Create repository"

---

## 🎯 步骤2：初始化Git仓库

在你的项目文件夹中打开终端（PowerShell或CMD），执行：

```bash
# 进入项目目录
cd "f:\游戏"

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 查看将要提交的文件
git status

# 提交
git commit -m "Initial commit: 修仙肉鸽游戏"
```

---

## 🎯 步骤3：连接到GitHub

```bash
# 添加远程仓库（替换成你的GitHub用户名）
git remote add origin https://github.com/你的用户名/修仙肉鸽.git

# 推送到GitHub
git push -u origin master
```

如果提示需要登录，输入你的GitHub用户名和密码（或Personal Access Token）。

---

## 🎯 步骤4：验证

1. 刷新GitHub仓库页面
2. 应该能看到所有文件已上传
3. README.md会自动显示在首页

---

## 📝 注意事项

### 已自动忽略的文件（.gitignore）：
- ✅ 美术素材文件夹（太大）
- ✅ Python缓存（__pycache__）
- ✅ 所有图片文件（.png, .jpg等）
- ✅ 视频文件（.mp4）
- ✅ 存档文件

### 会上传的文件：
- ✅ 所有Python代码（.py）
- ✅ 配置文件
- ✅ 文档（docs/）
- ✅ README.md
- ✅ requirements.txt
- ✅ .gitignore

---

## 🔧 常见问题

### Q1: 文件太大无法上传
**A**: 已经通过.gitignore忽略了大文件。如果还是太大，检查是否有其他大文件。

### Q2: 需要Personal Access Token
**A**: 
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token
3. 勾选 "repo" 权限
4. 复制token，在推送时用它代替密码

### Q3: 想要上传美术素材
**A**: 
1. 从.gitignore中删除对应行
2. 或者使用Git LFS（大文件存储）
3. 或者把素材放到其他地方（如云盘）

---

## 📊 预计上传大小

删除美术素材后，项目大小约：**3-5 MB**

这个大小完全可以上传到GitHub（单个文件限制100MB，仓库建议<1GB）。

---

## 🎉 完成后

你的项目就在GitHub上了！可以：
- 分享给其他人
- 在其他电脑上克隆
- 协作开发
- 使用GitHub Actions自动化

---

## 🚀 快速命令（复制粘贴）

```bash
cd "f:\游戏"
git init
git add .
git commit -m "Initial commit: 修仙肉鸽游戏"
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin master
```

**记得替换 "你的用户名" 和 "仓库名"！**
