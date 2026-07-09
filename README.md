# Screenshot Butler

**Not a screenshot tool — a screenshot butler. You snap, it organizes.**

**Snap → AI classifies → chat to confirm → auto-archive. Screenshots that never rot in your camera roll.**

Two ways to use:

| Mode | Experience | For |
|---|---|---|
| **Claude Code Skill** (recommended) | Full: reads your memory → classifies → chats → writes notes → schedules | Claude Code users |
| **Universal Mode** | Script + any LLM, manual copy-paste | Everyone else |

---

## Why

You take screenshots every day — error popups, work messages, design references, delivery addresses. "Snap and forget."

Screenshot Butler gives every screenshot an "and then": AI reads the image, classifies it, discusses it with you, writes useful info into your notes, and auto-deletes the original.

> A screenshot is a sticky note. Write it down, then toss the paper.

---

## Install

1. Clone:
```bash
git clone https://github.com/Waterme1onn/screenshot-butler.git
cd screenshot-butler
```

2. Two ways to use:
   - **Use this directory directly**: `cd screenshot-butler`, then say "organize screenshots" in Claude Code
   - **Add to existing project**: copy the skill file `cp skill/screenshot-agent.md your-project/.claude/skills/`

3. Install Python dependencies:
```bash
pip install Pillow pytesseract
```

Tesseract OCR (optional, fallback for non-vision models):
- Windows: `winget install UB-Mannheim.TesseractOCR`
- macOS: `brew install tesseract`
- Linux: `apt install tesseract-ocr`

## Project Structure

```
screenshot-butler/
├── screenshot_agent.py       # Core script
├── skill/
│   └── screenshot-agent.md   # Claude Code skill definition
├── config.default.json       # Default config
├── README.md
└── .gitignore
```

---

## First-Time Setup

In Claude Code, say:

```
organize screenshots
```

The Agent detects first-time use and walks you through setup:

1. **Where to save?** — Agent creates a folder, tells you how to change your screenshot tool's save path
2. **WeChat import?** — Phone screenshot → send to WeChat File Transfer → auto-imported on PC (zero config, no Syncthing)
3. **Auto-organize?** — Set a daily time like 9:00 AM
4. **Categories okay?** — Five defaults; add, remove, or rename

All done in conversation. No config files to edit.

### Screenshot Shortcuts by OS

| OS | Shortcut | Note |
|---|---|---|
| Windows 11 | `Win + Shift + S` | Change save path in Snipping Tool settings |
| Windows 10 | `Win + Shift + S` or `Win + PrintScreen` | Recommend installing new Snipping Tool from Microsoft Store |
| macOS | `Cmd + Shift + 5` | Change save location in Options |

---

## Daily Use

```
organize screenshots
```

The Agent will:
1. Read your memory (learn who you are and what you're working on)
2. Scan screenshots → present all with classifications
3. You pick which ones to discuss
4. Useful info gets written to your notes; originals move to `.cold-storage/` and auto-delete after 7 days

### The Five Categories

| Category | In One Sentence | What AI Does |
|---|---|---|
| 🔍 **Explain** | "Help me understand this" | Explain errors, translate, analyze data |
| 📋 **To-Do** | "Help me know what to do" | Extract action items, break into next steps |
| 📝 **Memo** | "Help me remember this" | Extract key info, structure it |
| 🎯 **Reference** | "Help me copy this" | Save to reference library, note highlights |
| 🗑️ **Junk** | Accidental screenshot | Straight to trash |

Categories are customizable via conversation.

---

## Auto-Organize

```
auto-organize screenshots every day at 9 AM
```

The Agent sets up a cron task. It auto-scans, imports WeChat images, presents classifications, and waits for your confirmation — every day.

To cancel:
```
cancel auto-organize
```

---

## Phone Screenshots

Phone → send to WeChat File Transfer → PC Agent auto-imports into the screenshot folder.

Zero setup. No Syncthing. No third-party sync tools. WeChat is already on everyone's phone.

---

## Universal Mode (Non-Claude Code Users)

The script is pure Python. Use it with any LLM (ChatGPT, Claude Web, Gemini, local models, etc.) — just a few manual steps:

**Step 1: Scan**
```bash
python screenshot_agent.py --list
```

**Step 2: Read**
Send the JSON output + your screenshots to any LLM with this prompt:
```
You are a screenshot organizer. Above is a list of the user's unprocessed screenshots.
Review each image and classify it:
- 🔍 Explain: errors, foreign text, data — needs explanation
- 📋 To-Do: tasks, requests, things to do
- 📝 Memo: addresses, accounts, schedules — info to remember
- 🎯 Reference: designs, layouts, styles — "copy this"
- 🗑️ Junk: accidental screenshots

For each image: classify → extract key info → ask the user follow-up questions if context is needed.
End with a summary and suggestions.
```

**Step 3: Mark Done**
```bash
python screenshot_agent.py --mark-done <file1> <category1> <file2> <category2>
```

**Step 4: Archive**
```bash
python screenshot_agent.py --archive
```

> Universal mode doesn't include "auto-write to memory" and "scheduled processing" — those are Claude Code skill exclusives.

---

## Configuration

All config is done through conversation. No manual file editing. For reference:

| Config | Description | Default |
|---|---|---|
| `screenshot_folder` | Where screenshots live | `./screenshots` |
| `categories` | Classification labels (customizable) | Five defaults |
| `auto_process_time` | Daily auto-organize time | `null` (off) |
| `wechat_auto_import` | Auto-import from WeChat | `false` |
| `wechat_folder` | WeChat image directory | Auto-detected |

---

## Commands

```bash
python screenshot_agent.py --list          # List unprocessed screenshots
python screenshot_agent.py --mark-done     # Mark as processed
python screenshot_agent.py --archive       # Archive to cold storage
python screenshot_agent.py --cleanup       # Purge expired cold storage
python screenshot_agent.py --stats         # Statistics
python screenshot_agent.py --setup         # First-time setup guide
python screenshot_agent.py --process-all   # Auto mode (import + scan + cleanup)
python screenshot_agent.py --detect-wechat # Detect WeChat folder
```

---

## Privacy

- The Agent runs **locally**. Screenshots are not automatically uploaded to external servers.
- If using cloud AI (e.g., Claude API), screenshot content is sent to the respective AI provider.
- Be mindful of sensitive info in screenshots (passwords, bank cards, etc.).
- Config files `.screenshot_agent_config.json` and `.screenshots_processed.json` should be added to `.gitignore`.

---

## Customization

The five default categories are designed to be universal. To customize:

```
change my categories to: tasks, knowledge, memos, content ideas, inspiration, junk
```

The Agent handles the rest.

---

## License

MIT
