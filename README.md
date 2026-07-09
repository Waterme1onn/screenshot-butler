# Screenshot Butler

**Not a screenshot tool — a screenshot butler. You snap, it organizes.**

A Python script that scans your screenshot folder, hands them to AI for classification, then archives the originals. Works with any LLM — Claude, ChatGPT, Gemini, or local models.

> A screenshot is a sticky note. Write it down, then toss the paper.

---

## Quick Start

```bash
git clone https://github.com/Waterme1onn/screenshot-butler.git
cd screenshot-butler
pip install Pillow pytesseract
```

**Tesseract OCR** (optional — fallback if your AI can't read images directly):
- Windows: `winget install UB-Mannheim.TesseractOCR`
- macOS: `brew install tesseract`
- Linux: `apt install tesseract-ocr`

---

## How It Works

### 1. Scan your screenshot folder

```bash
python screenshot_agent.py --list
```

Returns a JSON list of unprocessed screenshots. Never processes the same image twice (hash-based dedup).

### 2. Send to any AI

Take the JSON output + your screenshot images, send them to any LLM. Use this prompt:

```
You are a screenshot organizer. Review each image and classify it:

🔍 Explain — errors, foreign text, data that needs explanation
📋 To-Do  — tasks, requests, things to act on
📝 Memo   — addresses, accounts, schedules worth remembering
🎯 Reference — designs, layouts, styles to save as reference
🗑️ Junk   — accidental screenshots

For each: classify → extract key info → suggest next actions.
```

### 3. Mark & archive

```bash
python screenshot_agent.py --mark-done screenshot1.png explain screenshot2.png memo
python screenshot_agent.py --archive
```

Processed screenshots move to `.cold-storage/`, auto-deleted after 7 days (3 days for junk).

---

## Use with Claude Code

If you use [Claude Code](https://claude.ai/code), add the skill file and everything becomes conversational:

```
organize screenshots
```

The Agent handles the full flow — scanning, reading images, classifying, discussing with you, writing useful info to your notes, and archiving. No manual commands needed.

**Extra features with Claude Code:**

- **Memory-aware** — Agent reads your existing notes before classifying, so suggestions are context-aware ("this error screenshot looks related to your current project")
- **Auto-write notes** — useful info from screenshots gets saved to your note system automatically
- **Scheduled runs** — set a daily time and it happens without you
- **WeChat import** — phone screenshots sent to WeChat File Transfer are auto-imported

### First-time setup

Say "organize screenshots" once. The Agent walks you through:
- Where to save screenshots (with OS-specific shortcut guides)
- Whether to auto-import from WeChat
- Whether to schedule daily runs
- Category customization

All in conversation. No config files to edit.

---

## Phone Screenshots

Phone → send to WeChat File Transfer → PC Agent auto-imports into the screenshot folder.

Zero setup. WeChat is on every Chinese user's phone. No Syncthing needed.

---

## The Five Categories

| Category | In One Sentence | What AI Does |
|---|---|---|
| 🔍 **Explain** | "Help me understand this" | Explain errors, translate, analyze data |
| 📋 **To-Do** | "Help me know what to do" | Extract action items, break into next steps |
| 📝 **Memo** | "Help me remember this" | Extract key info, structure it |
| 🎯 **Reference** | "Help me copy this" | Save to reference library, note highlights |
| 🗑️ **Junk** | Accidental screenshot | Straight to trash |

Customizable — change labels, add or remove categories through conversation or config.

---

## Configuration

All config is done through conversation (Claude Code) or by editing `config.default.json`:

| Config | Description | Default |
|---|---|---|
| `screenshot_folder` | Where screenshots live | `./screenshots` |
| `categories` | Classification labels | Five defaults |
| `auto_process_time` | Daily auto-organize time | `null` (off) |
| `wechat_auto_import` | Auto-import from WeChat | `false` |
| `wechat_folder` | WeChat image directory | Auto-detected |

---

## Commands

```bash
python screenshot_agent.py --list           # List unprocessed screenshots
python screenshot_agent.py --mark-done ...  # Mark as processed
python screenshot_agent.py --archive        # Archive to cold storage
python screenshot_agent.py --cleanup        # Purge expired cold storage
python screenshot_agent.py --stats          # Statistics
python screenshot_agent.py --setup          # First-time setup guide
python screenshot_agent.py --process-all    # Auto mode (import + scan + cleanup)
python screenshot_agent.py --detect-wechat  # Detect WeChat folder
```

---

## Privacy

- The script runs **locally**. Screenshots are not uploaded anywhere unless you send them to a cloud AI.
- If using cloud AI (Claude API, ChatGPT, etc.), screenshot content is sent to the respective provider.
- Config files (`.screenshot_agent_config.json`, `.screenshots_processed.json`) contain local paths and should be `.gitignore`d.

---

## License

MIT
