# 截图管家 Screenshot Butler

**不是截图工具，是截图的管家——你截，它整理。**

一个 Python 脚本 + 一份 AI skill 文件。放到一起，你的 AI 助手就变成了截图管家——自动分类、跟你聊、归档整理。任何能执行命令的 AI 工具都能用。

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

## 配置你的 AI 工具

`skill/screenshot-agent.md` 文件告诉 AI 如何当截图管家。放进你用的工具里：

| AI 工具 | 配置方式 |
|---|---|
| **Claude Code** | 复制到 `.claude/skills/`，或直接在这个目录打开 Claude Code |
| **Cursor** | 添加到 `.cursorrules` 或粘贴到 Cursor 的自定义指令 |
| **Cline / Roo Code** | 添加到 `.clinerules` 或粘贴到自定义指令 |
| **Windsurf** | 添加到 `.windsurfrules` |
| **GitHub Copilot** | 粘贴到自定义指令（`.github/copilot-instructions.md`） |
| **ChatGPT / Claude Web** | 把 skill 内容当 system prompt 粘贴到会话开头 |

配置好后，说 **"整理截图"**（或对应工具的触发方式），AI 就会接管一切。

---

## 能做什么

```
你说："整理截图"
                │
AI 先读你的笔记（了解你是谁、在做什么）
                │
扫描截图文件夹 → 逐张读取 → 分类：
   🔍 解惑 — "这是什么报错/外文/数据？"
   📋 待办 — "需要做什么？"
   📝 备忘 — "需要记住什么？"
   🎯 参考 — "留着参考"
   🗑️ 误截 — 不小心截的，扔掉
                │
全部分类展示 → 你挑想聊的深入讨论
                │
有用信息自动存入你的笔记系统
原图移入 .cold-storage/ → 7天后自动删除
```

---

## 五个分类

| 分类 | 一句话 | AI 做什么 |
|---|---|---|
| 🔍 **解惑** | "帮我搞懂这是什么" | 解释报错、翻译外文、分析数据 |
| 📋 **待办** | "帮我整理该做什么" | 提取行动项，拆成下一步 |
| 📝 **备忘** | "帮我记住这个" | 提取关键信息，结构化保存 |
| 🎯 **参考** | "帮我照着这个来" | 存参考库，标注亮点 |
| 🗑️ **误截** | 不小心截的 | 直接清理 |

随时可以改——告诉 AI 就行。

---

## 额外功能：定时 & 微信导入

Skill 加载后，AI 还能帮你设置：

- **定时整理** — "每天早上 9 点自动整理截图。" AI 帮你建好定时任务，到点自动跑。
- **微信导入** — 手机截图 → 发微信文件助手 → AI 自动拉进截图目录。零配置，不用 Syncthing。
- **记忆集成** — AI 分类前先读你的笔记，有上下文（"这张报错跟你的 XX 项目有关"）。
- **首次引导** — 第一次说"整理截图"，AI 引导你完成所有设置：截图文件夹、各系统快捷键、微信配置、定时、分类定制。全程对话。

---

## 手动模式

不想配置 skill？当成纯脚本用也完全没问题：

```bash
python screenshot_agent.py --list              # 扫描文件夹
# → 把 JSON + 截图手动发给任意 LLM
python screenshot_agent.py --mark-done ...     # 标记处理
python screenshot_agent.py --archive            # 归档到 cold storage
```

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

## 配置

通过对话完成（加载 skill 后）或直接编辑 `config.default.json`：

| 配置项 | 说明 | 默认值 |
|---|---|---|
| `screenshot_folder` | 截图存放目录 | `./screenshots` |
| `categories` | 分类标签 | 五个默认分类 |
| `auto_process_time` | 每日自动整理时间 | `null`（关闭） |
| `wechat_auto_import` | 自动导入微信图片 | `false` |
| `wechat_folder` | 微信图片目录 | 自动探测 |

---

## 隐私

- 脚本**在本地运行**，截图不会自动上传到外部服务器
- 如果使用云端 AI（Claude API、ChatGPT 等），截图内容会发送到对应的 AI 服务商
- 配置文件（`.screenshot_agent_config.json`、`.screenshots_processed.json`）包含本地路径，记得 `.gitignore`

---

## License

MIT
