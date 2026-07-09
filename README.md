# 截图管家 Screenshot Butler

**不是截图工具，是截图的管家——你截，它整理。**

**截图 → AI 自动分类 → 聊天确认 → 自动归档。截图不用再烂在相册里。**

两种使用方式：

| 方式 | 体验 | 适合 |
|---|---|---|
| **Claude Code skill**（推荐） | 完整：读记忆 → 分类 → 交互 → 写记忆 → 定时 | Claude Code 用户 |
| **通用模式** | 脚本 + 任意 LLM，手动 copy-paste | 其他 AI 工具用户 |

---

## 为什么需要这个

你每天截图——报错弹窗、工作消息、设计参考、外卖地址。"截了就截了"，从不再看。

截图管家让每张截图都有"然后呢"：AI 读图、分类、跟你聊、把有用的写入笔记、原图自动删除。

> 截图是便签纸。写下来，纸就可以扔了。

---

## 安装

1. 克隆到本地：
```bash
git clone https://github.com/Waterme1onn/screenshot-butler.git
cd screenshot-butler
```

2. 两种使用方式任选：
   - **直接用这个目录**：`cd screenshot-butler`，然后在 Claude Code 里说"整理截图"
   - **已有项目**：把 skill 复制过去 `cp skill/screenshot-agent.md 你的项目/.claude/skills/`

3. 安装 Python 依赖：
```bash
pip install Pillow pytesseract
```

Tesseract OCR（可选，非视觉模型的回退方案）：
- Windows：`winget install UB-Mannheim.TesseractOCR`
- macOS：`brew install tesseract`
- Linux：`apt install tesseract-ocr`

## 项目结构

```
screenshot-butler/
├── screenshot_agent.py       # 核心脚本
├── skill/
│   └── screenshot-agent.md   # Claude Code skill 定义
├── config.default.json       # 默认配置
├── README.md
└── .gitignore
```

---

## 首次使用

在 Claude Code 里说：

```
整理截图
```

Agent 会检测到你是第一次使用，引导你完成设置：

1. **截图放哪？** — Agent 帮你建文件夹，告诉你怎么改截图工具的保存路径
2. **微信导入？** — 手机截图 → 发微信文件助手 → 电脑端自动整理（不需要装任何同步软件）
3. **自动整理？** — 设定每天早上 9 点自动整理
4. **分类确认** — 五个分类够用吗？可以增减

全在对话里完成，不需要手动改配置文件。

### 各系统截图快捷键

| 系统 | 快捷键 | 说明 |
|---|---|---|
| Windows 11 | `Win + Shift + S` | 截图工具设置里改保存路径即可 |
| Windows 10 | `Win + Shift + S` 或 `Win + PrintScreen` | 推荐装新版截图工具（Microsoft Store） |
| macOS | `Cmd + Shift + 5` | 选项里改保存位置 |

---

## 日常使用

```
整理截图
```

Agent 会：
1. 读取你的记忆（了解你是谁、在做什么）
2. 扫描截图 → 全部分类展示
3. 你挑想聊的深入讨论
4. 有用的自动写入笔记，原图移入 `.cold-storage/` 7 天后自动删除

### 五个分类

| 分类 | 一句话 | AI 做什么 |
|---|---|---|
| 🔍 **解惑** | "帮我搞懂这是什么" | 解释报错、翻译外文、分析数据 |
| 📋 **待办** | "帮我整理该做什么" | 提取行动项，拆成下一步 |
| 📝 **备忘** | "帮我记住这个" | 提取关键信息，结构化保存 |
| 🎯 **参考** | "帮我照着这个来" | 存参考库，标注亮点 |
| 🗑️ **误截** | 不小心截的 | 直接清理 |

分类可通过对话修改。

---

## 自动整理

```
每天早上 9 点自动整理截图
```

Agent 会设置定时任务。到点自动扫描、导入微信图片、展示分类、等你确认。

取消：
```
取消自动整理
```

---

## 手机截图

手机截图 → 微信发到"文件传输助手" → PC 端 Agent 自动拉进截图文件夹。

零配置，不需要 Syncthing 或任何同步工具。

---

## 通用模式（非 Claude Code 用户）

脚本本身是纯 Python。搭配任何 LLM（ChatGPT、Claude Web、Gemini、本地模型等）都能用，只是需要手动操作：

**Step 1: 扫描**
```bash
python screenshot_agent.py --list
```

**Step 2: 读图**
把输出的 JSON + 截图发给任意 LLM，用这段 prompt：
```
你是一个截图整理助手。上面是用户未处理的截图列表。
请逐张查看截图，按以下分类整理：
- 🔍 解惑：报错/外文/数据，需要解释
- 📋 待办：任务、请求、待处理
- 📝 备忘：地址、账号、日程等需要记住的信息
- 🎯 参考：设计/排版/风格，照这个来
- 🗑️ 误截：不小心截的

对每张图：分类 → 提取关键信息 → 追问用户（如果需要更多上下文）。
最后给出总结和建议。
```

**Step 3: 标记处理**
```bash
python screenshot_agent.py --mark-done <文件1> <分类1> <文件2> <分类2>
```

**Step 4: 归档**
```bash
python screenshot_agent.py --archive
```

> 通用模式没有"自动写记忆"和"定时整理"——这两个功能是 Claude Code skill 独有的。

---

## 配置

所有配置通过对话完成，不需要手动编辑文件。如果你想知道有什么可以配置的：

| 配置项 | 说明 | 默认值 |
|---|---|---|
| `screenshot_folder` | 截图存放目录 | `./screenshots` |
| `categories` | 分类标签（可自定义） | 五个默认分类 |
| `auto_process_time` | 每日自动整理时间 | `null`（关闭） |
| `wechat_auto_import` | 自动导入微信图片 | `false` |
| `wechat_folder` | 微信图片目录 | 自动探测 |

---

## 命令参考

```bash
python screenshot_agent.py --list          # 列出未处理截图
python screenshot_agent.py --mark-done     # 标记已处理
python screenshot_agent.py --archive       # 归档到 cold storage
python screenshot_agent.py --cleanup       # 清理过期截图
python screenshot_agent.py --stats         # 统计
python screenshot_agent.py --setup         # 首次设置引导
python screenshot_agent.py --process-all   # 自动模式
python screenshot_agent.py --detect-wechat # 探测微信目录
```

---

## 隐私

- Agent **在本地运行**，截图不会自动上传到外部服务器
- 如果使用云端 AI（如 Claude API），截图内容会发送到对应的 AI 服务商
- 截图中的密码、银行卡号等敏感信息请注意保护
- 配置文件 `.screenshot_agent_config.json` 和追踪文件 `.screenshots_processed.json` 建议加入 `.gitignore`

---

## 个人定制版

默认五分类是普适设计。如果你想改成自己的体系（比如"📚 知识 / 🎬 内容素材 / 💡 灵感"），在首次使用时告诉 Agent 就行，或者直接说：

```
把分类改成：任务、知识、备忘、内容素材、灵感、无关
```

Agent 会帮你改好。

---

## License

MIT
