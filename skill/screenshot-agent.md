# 截图管家 Screenshot Agent

把截图变成 AI 的输入。省去打字描述上下文的麻烦。

## 触发词

"处理截图" / "整理截图" / "截图管家" / "screenshot" / "看看截图"

---

## 工作流程

### Step 0: 同步 & 准备

1. **检查是否首次使用**：
   ```bash
   python screenshot_agent.py --needs-setup
   ```
   如果返回 `"needs_setup": true` → **必须进入首次引导，不能跳过**
   - 首次引导流程：
     1. 帮用户建截图文件夹（如 `./screenshots`）
     2. 运行 `python screenshot_agent.py --setup`，拿到 `screenshot_guide`，按 OS 告诉用户截图快捷键和怎么改保存路径
     3. 问用户要不要设定时自动整理（"每天早上 9 点自动整理截图？"）
     4. 展示默认五分类，问要不要增减
     5. **每确认一项立刻执行对应的 `--set-*` 命令写入配置**——不要等到最后
   - 首次引导完成后，配置文件和截图文件夹都已就位，继续 Step 0.2

2. **同步 & 清理**：
   ```bash
   python screenshot_agent.py --process-all
   ```
   这一步会：① 清理过期的 cold storage ② 返回未处理截图列表。

3. **读取用户记忆**：用 Read 读取 `memory/MEMORY.md` 和所有 `.md` 记忆文件，了解用户是谁、在做什么、有什么项目。这些上下文用于 Step 2 的分类和追问。

### Step 1: 扫描截图

如果 Step 0 已通过 `--process-all` 获取了未处理列表，直接使用。否则：

```bash
python screenshot_agent.py --list
```

- 如果 `count: 0`，告诉用户"没有新截图，去截点什么吧"
- 如果 `count > 15`，进入**批量模式**：只展示文件名、时间、大小摘要，让用户挑想深入聊的，其余快速分类
- 正常数量：逐张处理

### Step 2: 读取 & 分类展示

**读取每张截图**：
- 首选：用 Read 工具直接读取图片（Claude 原生视觉）
- 如果 Read 返回 `[Unsupported Image]` 或不返回内容 → **自动切 OCR 回退**：
  ```bash
  python -c "
  import pytesseract
  from PIL import Image
  pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
  img = Image.open('<文件路径>')
  text = pytesseract.image_to_string(img, lang='chi_sim+eng')
  print(text)
  "
  ```
  - 不要告诉用户"模型不支持视觉"——OCR 回退对用户透明
  - 如果 OCR 也没有可用工具，才告诉用户"当前环境无法读取图片，请切换到 Claude 模型或安装 tesseract"

**分类展示**（不要逐张追问，全部展示后让用户选）：

结合 Step 0 读取的用户记忆，用以下五个分类整理所有截图：

| 分类 | 关键词 | 处理原则 |
|---|---|---|
| 🔍 **解惑** | "这是什么？"怎么操作？报错、外文、数据 | 解释/翻译/分析，帮用户搞懂 |
| 📋 **待办** | 任务、请求、待处理 | 提取行动项，追问上下文和优先级 |
| 📝 **备忘** | 账号、地址、价格、日程 | 提取关键信息，结构化呈现 |
| 🎯 **参考** | 设计、排版、风格"照这个来" | 标注亮点和来源，存参考 |
| 🗑️ **误截** | 不小心截的、重复的 | 直接跳过 |

展示格式：
> 📸 你的 5 张截图：
> 🔍 解惑（2张）：报错弹窗、英文菜单
> 📋 待办（1张）：工作群消息，跟你的 XX 项目有关
> 📝 备忘（1张）：物流单号
> 🗑️ 误截（1张）：桌面空白
>
> 想聊哪张？还是全交给我处理？

**关联提醒**：如果某张截图明显跟已有记忆/项目有关，主动点出——"这张截图说的 XX，跟你之前提到的 YY 有关系，要展开聊聊吗？"

### Step 3: 交互追问

用户挑着想聊的截图深入处理：

- **解惑类**：直接给答案，不需要追问
- **待办类**：追问优先级、DDL、关联项目，帮用户拆成可执行的下一步
- **备忘类**：精炼关键信息（时间/地点/数字），确认无误
- **参考类**：追问"想参考它什么？用在哪儿？"
- **误截类**：跳过

**处理原则**：
- 每张图都要有"然后呢"——不是识别完就结束，要推进到行动
- 追问优于猜测——截图的上下文只有用户知道
- 关联优于孤立——每条新信息都尝试跟已有记忆建立连接
- 用户说不聊的图不要纠缠，快速过

### Step 4: 写入记忆 & 归档

用户确认或跳过所有截图后：

1. **写记忆**：把有用的信息写入 `memory/` 目录，格式跟现有记忆一致（frontmatter + body），链接到相关记忆。只写用户确认过的内容。

2. **标记处理**：
   ```bash
   python screenshot_agent.py --mark-done <file1> <category1> <file2> <category2> ...
   ```
   文件名和分类交替传入。分类用 key：`explain`/`todo`/`memo`/`ref`/`junk`

3. **归档原图**：
   ```bash
   python screenshot_agent.py --archive
   ```
   已处理截图移入 `.cold-storage/`，7 天后自动清理（误截 3 天）。

4. **汇报收尾**：
   > ✅ 5 张处理完：新记了 1 条备忘、1 条参考，其他 3 张跳过。截图已归档，7 天后自动删除。

---

## 定时自动整理

用户说"每天早上 9 点自动整理截图"时：

1. 设置配置：
   ```bash
   python screenshot_agent.py --set-cron "09:00"
   ```

2. 创建 Cron 定时任务（Claude Code 内置）：
   ```
   CronCreate: cron "0 9 * * *", prompt "使用截图管家 skill 处理截图", durable true
   ```

3. 告诉用户：
   > 已设置每天早上 9:00 自动整理。到时 Agent 会自动扫描、整理分类、等你确认。
   > 随时说"取消自动整理"来停止。

---

## 辅助命令速查

| 命令 | 作用 |
|---|---|
| `--list` | 列出未处理截图 |
| `--mark-done <files...> <category>` | 标记已处理 |
| `--archive` | 归档到 cold storage |
| `--cleanup` | 清理过期 cold storage |
| `--stats` | 统计信息 |
| `--setup` | 首次设置引导 |
| `--process-all` | 自动模式（扫描+清理） |
| `--config` | 查看当前配置 |
| `--set-folder <path>` | 设置截图文件夹 |
| `--set-cron <time>` | 设置自动整理时间 |
| `--reset [file]` | 重置处理状态 |

---

## ⚠️ 隐私提醒

截图可能包含密码、银行卡号、聊天记录等敏感信息。Agent 在本地运行，不会上传到外部服务器。但请用户注意：如果通过云端 AI 服务（Claude API 等）处理截图，截图内容会发送到对应的 AI 服务商。
