# 截图管家 Screenshot Butler

**不是截图工具，是截图的管家——你截，它整理。**

一个 Python 脚本：扫描你的截图文件夹，交给 AI 分类整理，然后自动归档原图。跟任何 LLM 都能用——Claude、ChatGPT、Gemini、本地模型都行。

> 截图是便签纸。写下来，纸就可以扔了。

---

## 快速开始

```bash
git clone https://github.com/Waterme1onn/screenshot-butler.git
cd screenshot-butler
pip install Pillow pytesseract
```

**Tesseract OCR**（可选——AI 无法直接读图时的回退方案）：
- Windows：`winget install UB-Mannheim.TesseractOCR`
- macOS：`brew install tesseract`
- Linux：`apt install tesseract-ocr`

---

## 怎么用

### 1. 扫描截图文件夹

```bash
python screenshot_agent.py --list
```

返回未处理截图的 JSON 列表。哈希去重，同一张图不会重复处理。

### 2. 发给任意 AI

把 JSON 输出 + 截图发给任意 LLM，用这段 prompt：

```
你是一个截图整理助手。请逐张查看截图，按以下分类整理：

🔍 解惑 — 报错、外文、数据，需要解释
📋 待办 — 任务、请求，需要行动
📝 备忘 — 地址、账号、日程，值得记住
🎯 参考 — 设计、排版、风格，留着参考
🗑️ 误截 — 不小心截的

对每张图：分类 → 提取关键信息 → 给出下一步建议。
```

### 3. 标记 & 归档

```bash
python screenshot_agent.py --mark-done 截图1.png explain 截图2.png memo
python screenshot_agent.py --archive
```

处理完的截图移入 `.cold-storage/`，7 天后自动删除（误截 3 天）。

---

## 配合 Claude Code 使用

如果你用 [Claude Code](https://claude.ai/code)，把 skill 文件放进去，所有操作变成对话式：

```
整理截图
```

Agent 会处理全流程——扫描、读图、分类、跟你聊、把有用的写入笔记、归档。不需要手动敲命令。

**Claude Code 下的额外功能：**

- **记忆驱动** — Agent 分类前先读你的笔记，有上下文（"这张报错跟你的 XX 项目有关"）
- **自动写笔记** — 截图里的有用信息自动存进你的笔记系统
- **定时整理** — 设好时间，每天自动跑
- **微信导入** — 手机截图发文件助手，PC 端自动拉进截图目录

### 首次设置

第一次说"整理截图"，Agent 会引导你完成：
- 截图放哪（附各系统快捷键说明）
- 要不要导入微信文件助手
- 要不要设定时整理
- 分类要不要改

全程对话，不用手动改配置文件。

---

## 手机截图

手机截图 → 微信发到"文件传输助手" → PC 端自动拉进截图文件夹。

零配置。不用 Syncthing，不用任何同步工具。

---

## 五个分类

| 分类 | 一句话 | AI 做什么 |
|---|---|---|
| 🔍 **解惑** | "帮我搞懂这是什么" | 解释报错、翻译外文、分析数据 |
| 📋 **待办** | "帮我整理该做什么" | 提取行动项，拆成下一步 |
| 📝 **备忘** | "帮我记住这个" | 提取关键信息，结构化保存 |
| 🎯 **参考** | "帮我照着这个来" | 存参考库，标注亮点 |
| 🗑️ **误截** | 不小心截的 | 直接清理 |

可通过对话或配置文件自定义。

---

## 配置

所有配置通过对话完成（Claude Code）或编辑 `config.default.json`：

| 配置项 | 说明 | 默认值 |
|---|---|---|
| `screenshot_folder` | 截图存放目录 | `./screenshots` |
| `categories` | 分类标签 | 五个默认分类 |
| `auto_process_time` | 每日自动整理时间 | `null`（关闭） |
| `wechat_auto_import` | 自动导入微信图片 | `false` |
| `wechat_folder` | 微信图片目录 | 自动探测 |

---

## 命令参考

```bash
python screenshot_agent.py --list           # 列出未处理截图
python screenshot_agent.py --mark-done ...  # 标记已处理
python screenshot_agent.py --archive        # 归档到 cold storage
python screenshot_agent.py --cleanup        # 清理过期截图
python screenshot_agent.py --stats          # 统计
python screenshot_agent.py --setup          # 首次设置引导
python screenshot_agent.py --process-all    # 自动模式（导入+扫描+清理）
python screenshot_agent.py --detect-wechat  # 探测微信目录
```

---

## 隐私

- 脚本**在本地运行**，截图不会自动上传到外部服务器
- 如果使用云端 AI（Claude API、ChatGPT 等），截图内容会发送到对应的 AI 服务商
- 配置文件（`.screenshot_agent_config.json`、`.screenshots_processed.json`）包含本地路径，记得 `.gitignore`

---

## License

MIT
