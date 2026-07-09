# Screenshot Butler

**Not a screenshot tool — a screenshot butler. You snap, it organizes.**

A Python script + an AI skill file. Put them together, and your AI assistant becomes a screenshot organizer — classifying, discussing, and archiving every screenshot you take. Works with any AI tool that can run commands.

> A screenshot is a sticky note. Write it down, then toss the paper.

---

## Quick Start

```bash
git clone https://github.com/Waterme1onn/screenshot-butler.git
cd screenshot-butler
pip install Pillow pytesseract
```

**Tesseract OCR** (optional — fallback if your AI can't read images natively):
- Windows: `winget install UB-Mannheim.TesseractOCR`
- macOS: `brew install tesseract`
- Linux: `apt install tesseract-ocr`

---

## Setup for Your AI Tool

The `skill/screenshot-agent.md` file tells your AI how to be a screenshot butler. Load it into whichever tool you use:

| AI Tool | How to Set Up |
|---|---|
| **Claude Code** | Copy to `.claude/skills/` — or just open this directory in Claude Code |
| **Cursor** | Add to `.cursorrules` or paste into Cursor's custom instructions |
| **Cline / Roo Code** | Add to `.clinerules` or paste into custom instructions |
| **Windsurf** | Add to `.windsurfrules` |
| **GitHub Copilot** | Paste into custom instructions (`.github/copilot-instructions.md`) |
| **ChatGPT / Claude Web** | Paste the skill content as a system prompt at the start of a session |

Once set up, say **"organize screenshots"** (or your tool's equivalent trigger) and the AI handles the rest.

---

## What It Does

```
You say: "organize screenshots"
                │
AI reads your notes (learns who you are, what you're working on)
                │
Scans screenshot folder → reads each image → classifies:
   🔍 Explain — "What is this error / foreign text / data?"
   📋 To-Do   — "What do I need to do?"
   📝 Memo    — "What should I remember?"
   🎯 Reference — "Keep this as a reference"
   🗑️ Junk    — Accidental screenshot, toss it
                │
Presents everything to you → you pick which to discuss
                │
Useful info gets saved to your notes
Originals move to .cold-storage/ → auto-deleted after 7 days
```

---

## The Five Categories

| Category | In One Sentence | AI Does |
|---|---|---|
| 🔍 **Explain** | "Help me understand this" | Explain errors, translate, analyze data |
| 📋 **To-Do** | "Help me know what to do" | Extract action items, break into next steps |
| 📝 **Memo** | "Help me remember this" | Extract key info, structure it |
| 🎯 **Reference** | "Help me copy this" | Save to reference library, note highlights |
| 🗑️ **Junk** | Accidental screenshot | Straight to trash |

Customize categories anytime — just tell your AI what to change.

---

## Bonus: Auto-Organize & WeChat Import

Once the skill is loaded, your AI can set up:

- **Scheduled runs** — "Organize screenshots every day at 9 AM." Your AI sets up a cron job and it happens automatically.
- **WeChat import** — Phone screenshot → send to WeChat File Transfer → AI auto-imports it into the screenshot folder. Zero setup. No Syncthing.
- **Memory integration** — AI reads your existing notes before classifying, so suggestions are context-aware ("this error screenshot looks related to your current project").
- **First-time setup wizard** — Say "organize screenshots" once, and your AI walks you through: screenshot folder setup (with OS-specific shortcut guides), WeChat config, scheduling, and category customization.

---

## Manual Mode

Don't want to set up a skill? Just want a script? That works too:

```bash
python screenshot_agent.py --list              # Scan folder
# → Send the JSON + images to any LLM manually
python screenshot_agent.py --mark-done ...     # Mark processed
python screenshot_agent.py --archive            # Archive to cold storage
```

---

## Commands

```bash
python screenshot_agent.py --list           # List unprocessed screenshots
python screenshot_agent.py --mark-done ...  # Mark as processed
python screenshot_agent.py --archive        # Archive to cold storage
python screenshot_agent.py --cleanup        # Purge expired cold storage
python screenshot_agent.py --stats          # Show statistics
python screenshot_agent.py --setup          # First-time setup guide
python screenshot_agent.py --process-all    # Auto mode (import + scan + cleanup)
python screenshot_agent.py --detect-wechat  # Detect WeChat image folder
```

---

## Configuration

Config is done through conversation (with the skill loaded) or by editing `config.default.json`:

| Config | Description | Default |
|---|---|---|
| `screenshot_folder` | Where screenshots live | `./screenshots` |
| `categories` | Classification labels | Five defaults |
| `auto_process_time` | Daily auto-organize time | `null` (off) |
| `wechat_auto_import` | Auto-import from WeChat | `false` |
| `wechat_folder` | WeChat image directory | Auto-detected |

---

## Privacy

- The script runs **locally**. Screenshots are not uploaded anywhere unless your AI tool sends them to a cloud provider.
- If using cloud AI (Claude API, ChatGPT, etc.), screenshot content is sent to the respective provider.
- Config files (`.screenshot_agent_config.json`, `.screenshots_processed.json`) contain local paths — add them to `.gitignore`.

---

## License

MIT
