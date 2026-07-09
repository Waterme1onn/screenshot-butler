"""
Screenshot Agent v2 — 截图管家
截图 → AI 读取 → 分类 → 交互 → 写记忆 → 归档 → 定期清理

面向 GitHub 的普适版本：五分类体系，支持 Claude 原生视觉 + OCR 回退，
首次使用对话式引导，微信文件助手自动导入，定时自动整理。

用法:
  python screenshot_agent.py --list                    列出未处理截图
  python screenshot_agent.py --mark-done <file> <cat>   标记已处理（cat: explain/todo/memo/ref/junk）
  python screenshot_agent.py --archive                  归档已处理截图到 cold storage
  python screenshot_agent.py --cleanup                  清理过期 cold storage
  python screenshot_agent.py --stats                    统计信息
  python screenshot_agent.py --setup                    首次设置引导（返回 OS 信息和推荐配置）
  python screenshot_agent.py --detect-wechat            探测微信文件助手目录
  python screenshot_agent.py --config                   查看当前配置
  python screenshot_agent.py --set-folder <path>        设置截图文件夹
  python screenshot_agent.py --set-cron <time>          设置自动整理时间（如 "09:00"）
  python screenshot_agent.py --reset [file]             重置处理状态
"""

import os
import sys
import json
import hashlib
import shutil
import platform
import subprocess
from datetime import datetime, timedelta

# ── Paths ──────────────────────────────────────────────────────────
# 脚本所在目录即为仓库根目录
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
TRACKING_FILE = os.path.join(REPO_ROOT, ".screenshots_processed.json")
CONFIG_FILE = os.path.join(REPO_ROOT, ".screenshot_agent_config.json")
DEFAULT_CONFIG_FILE = os.path.join(REPO_ROOT, "config.default.json")
COLD_STORAGE_DIR = os.path.join(REPO_ROOT, "screenshots", ".cold-storage")

# ── Constants ──────────────────────────────────────────────────────
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}
COLD_RETENTION_DAYS = 7
COLD_RETENTION_JUNK_DAYS = 3

DEFAULT_CATEGORIES = [
    {"key": "explain", "label": "解惑", "icon": "🔍",
     "description": "帮我搞懂这是什么", "action": "explain"},
    {"key": "todo", "label": "待办", "icon": "📋",
     "description": "帮我整理该做什么", "action": "extract_tasks"},
    {"key": "memo", "label": "备忘", "icon": "📝",
     "description": "帮我记住这个", "action": "save_note"},
    {"key": "ref", "label": "参考", "icon": "🎯",
     "description": "帮我照着这个来", "action": "save_reference"},
    {"key": "junk", "label": "误截", "icon": "🗑️",
     "description": "不小心截的", "action": "discard"},
]


# ── Helpers ─────────────────────────────────────────────────────────
def _t(path):
    """Translate a Windows path to forward slashes."""
    return path.replace("\\", "/")


def _is_image(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    return ext in IMAGE_EXTENSIONS


def _get_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ── Config ──────────────────────────────────────────────────────────
def load_config():
    """Load config, merging defaults for any missing keys."""
    defaults = {
        "screenshot_folder": _t(os.path.join(REPO_ROOT, "screenshots")),
        "categories": DEFAULT_CATEGORIES,
        "auto_process_time": None,
        "wechat_auto_import": False,
        "wechat_folder": None,
        "watch_folders": [],
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user = json.load(f)
        for k, v in defaults.items():
            if k not in user:
                user[k] = v
        return user
    return defaults


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


# ── Tracking ────────────────────────────────────────────────────────
def load_tracking():
    if not os.path.exists(TRACKING_FILE):
        return {"processed": {}, "last_scan": None}
    with open(TRACKING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tracking(data):
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── OS Detection ───────────────────────────────────────────────────
def detect_os():
    system = platform.system()
    if system == "Windows":
        try:
            ver = platform.version()
            build = int(ver.split(".")[-1]) if ver else 0
            if build >= 22000:
                return {"os": "windows", "version": "11", "build": build}
            return {"os": "windows", "version": "10", "build": build}
        except Exception:
            return {"os": "windows", "version": "unknown"}
    elif system == "Darwin":
        return {"os": "macos", "version": platform.mac_ver()[0]}
    return {"os": system.lower(), "version": "unknown"}


def get_screenshot_setup_guide():
    """Return the easiest screenshot setup instructions for the user's OS."""
    info = detect_os()
    os_name = info["os"]
    version = info["version"]

    if os_name == "windows" and version == "11":
        return {
            "method": "snipping_tool",
            "title": "Windows 11 截图工具（推荐）",
            "shortcut": "Win + Shift + S",
            "steps": [
                '打开「截图工具」App（按 Win 键搜索"截图工具"）',
                '点击右上角「…」→「设置」',
                '在「保存截图到」中，选择我给你建的文件夹',
                '以后按 Win+Shift+S 截图就会自动保存到这个文件夹',
            ],
            "note": "Win+Shift+S 截图后会自动保存，不需要手动粘贴。",
        }
    elif os_name == "windows":
        return {
            "method": "snipping_tool_or_printscreen",
            "title": "Windows 截图工具 或 Win + PrintScreen",
            "shortcut": "Win + Shift + S（截图工具）或 Win + PrintScreen（全屏自动保存）",
            "steps": [
                "方法一：安装新版截图工具（Microsoft Store 搜「Snipping Tool」），设置保存路径",
                '方法二：按 Win+PrintScreen，截图自动保存到「图片\\屏幕截图」文件夹——把这个文件夹路径给我',
            ],
            "note": "推荐方法一，可以直接设置保存路径",
        }
    elif os_name == "macos":
        return {
            "method": "screenshot_app",
            "title": "macOS 截图工具",
            "shortcut": "Cmd + Shift + 5",
            "steps": [
                "按 Cmd+Shift+5 打开截图工具栏",
                '点击「选项」→「其他位置」',
                "选择我给你建的文件夹",
                "以后截图都会保存到这里",
            ],
            "note": "Cmd+Shift+4 选区截图，Cmd+Shift+3 全屏截图——保存位置是一样的。",
        }
    return {
        "method": "manual",
        "title": "手动设置",
        "shortcut": "视系统而定",
        "steps": ["请告诉我你的操作系统和截图工具"],
        "note": None,
    }


# ── WeChat Detection ────────────────────────────────────────────────
def _get_drive_roots():
    """Return list of available drive roots on Windows."""
    drives = []
    for letter in "CDEFGH":
        path = letter + ":\\"
        if os.path.exists(path):
            drives.append(path)
    return drives


def _find_wx_dirs(search_roots):
    """Search under each root for WeChat data directories.
    Returns list of (base_path, wxid_dir, structure_type) tuples.
    structure_type: 'old' = WeChat Files, 'new' = xwechat_files.
    """
    results = []
    for root in search_roots:
        if not os.path.isdir(root):
            continue
        # Old WeChat structure: <root>/WeChat Files/<wxid>/
        old_base = os.path.join(root, "WeChat Files")
        if os.path.isdir(old_base):
            for d in os.listdir(old_base):
                wxid_path = os.path.join(old_base, d)
                if os.path.isdir(wxid_path) and d.startswith("wxid_"):
                    results.append((_t(old_base), _t(wxid_path), "old"))
        # New WeChat structure: <root>/xwechat_files/<wxid_xxx>/
        new_base = os.path.join(root, "xwechat_files")
        if os.path.isdir(new_base):
            for d in os.listdir(new_base):
                wxid_path = os.path.join(new_base, d)
                if os.path.isdir(wxid_path) and d.startswith("wxid_"):
                    results.append((_t(new_base), _t(wxid_path), "new"))
    return results


def detect_wechat_folder():
    """Try to detect WeChat directories that might contain images/files
    from File Transfer Assistant and regular chats.

    Searches common locations across all available drives, supports both
    old (WeChat Files) and new (xwechat_files) WeChat data structures.
    """
    info = detect_os()
    candidates = []

    if info["os"] == "windows":
        # Build list of directories to search
        search_roots = []

        # Documents folder (most common default)
        try:
            docs = os.path.expandvars(r"%USERPROFILE%\Documents")
            search_roots.append(docs)
        except Exception:
            pass

        # Desktop
        try:
            desktop = os.path.expandvars(r"%USERPROFILE%\Desktop")
            search_roots.append(desktop)
        except Exception:
            pass

        # Common custom paths on D: and E: drives
        for drive in _get_drive_roots():
            for sub in ["chat", "wechat", "WeChat", "微信"]:
                p = os.path.join(drive, sub)
                if os.path.isdir(p):
                    search_roots.append(p)

        # Also search drive roots directly (some people put it right on D:\)
        for drive in _get_drive_roots():
            search_roots.append(drive.rstrip("\\"))

        # Remove duplicates while preserving order
        seen = set()
        unique_roots = []
        for r in search_roots:
            r_norm = os.path.normpath(r).lower()
            if r_norm not in seen:
                seen.add(r_norm)
                unique_roots.append(r)
        search_roots = unique_roots

        # Find all WeChat directories
        wx_dirs = _find_wx_dirs(search_roots)

        for base_path, wxid_path, stype in wx_dirs:
            if stype == "old":
                # Old WeChat: FileStorage/Image/ for chat images
                img_dir = os.path.join(wxid_path, "FileStorage", "Image")
                if os.path.isdir(img_dir):
                    candidates.append({
                        "path": _t(img_dir),
                        "label": f"微信聊天图片 (旧版, {os.path.basename(wxid_path)})",
                        "type": "wechat_chat_images",
                    })
                # FileStorage/File/ for transferred files
                file_dir = os.path.join(wxid_path, "FileStorage", "File")
                if os.path.isdir(file_dir):
                    candidates.append({
                        "path": _t(file_dir),
                        "label": f"微信聊天文件 (旧版, {os.path.basename(wxid_path)})",
                        "type": "wechat_chat_files",
                    })
            elif stype == "new":
                # New WeChat: msg/video/ for chat images/videos
                video_dir = os.path.join(wxid_path, "msg", "video")
                if os.path.isdir(video_dir):
                    candidates.append({
                        "path": _t(video_dir),
                        "label": f"微信聊天图片 (新版, {os.path.basename(wxid_path)})",
                        "type": "wechat_chat_images",
                    })
                # msg/file/ for transferred files
                file_dir = os.path.join(wxid_path, "msg", "file")
                if os.path.isdir(file_dir):
                    candidates.append({
                        "path": _t(file_dir),
                        "label": f"微信聊天文件 (新版, {os.path.basename(wxid_path)})",
                        "type": "wechat_chat_files",
                    })
                # msg/attach/<hash>/Image/ for message attachments
                attach_dir = os.path.join(wxid_path, "msg", "attach")
                if os.path.isdir(attach_dir):
                    # Check if any subdirectory contains Image files
                    has_images = False
                    try:
                        for ad in os.listdir(attach_dir):
                            ad_path = os.path.join(attach_dir, ad, "Image")
                            if os.path.isdir(ad_path):
                                has_images = True
                                break
                    except Exception:
                        pass
                    if has_images:
                        candidates.append({
                            "path": _t(attach_dir),
                            "label": f"微信消息附件 (新版, {os.path.basename(wxid_path)})",
                            "type": "wechat_attachments",
                        })

    elif info["os"] == "macos":
        try:
            home = os.path.expanduser("~")
            wx_base = os.path.join(home, "Library", "Containers",
                                   "com.tencent.xinWeChat", "Data",
                                   "Library", "Application Support",
                                   "com.tencent.xinWeChat")
            if os.path.isdir(wx_base):
                candidates.append({
                    "path": _t(wx_base),
                    "label": "微信数据目录 (macOS)",
                    "type": "wechat_macos",
                })
        except Exception:
            pass

    return {
        "found": len(candidates) > 0,
        "candidates": candidates,
        "note": (
            f"找到 {len(candidates)} 个微信相关目录。"
            if candidates
            else "未自动检测到微信目录。如果安装了微信，可以手动指定路径。搜索范围：Documents、常用自定义路径、各盘符下的 chat/wechat 目录。"
        ),
    }


def import_wechat_images(cfg):
    """Copy new images from WeChat folder to screenshot folder.
    Recursively scans dated subdirectories (e.g. msg/video/2026-07/)."""
    wx_folder = cfg.get("wechat_folder")
    if not wx_folder or not os.path.isdir(wx_folder):
        return {"imported": 0, "error": "微信目录不存在或未配置"}

    dest_folder = cfg["screenshot_folder"]
    os.makedirs(dest_folder, exist_ok=True)

    tracking = load_tracking()
    processed_hashes = set(tracking.get("processed", {}).keys())
    imported = 0

    # Walk the WeChat directory recursively (handles dated subdirs like 2026-07/)
    for dirpath, _, filenames in os.walk(wx_folder):
        for fname in sorted(filenames):
            src = os.path.join(dirpath, fname)
            if not _is_image(src):
                continue
            fhash = _get_hash(src)
            if fhash in processed_hashes:
                continue
            # Only import from dated subdirectories or known structure
            # (skip Thumb/ subdirectories and cache dirs)
            rel = os.path.relpath(dirpath, wx_folder).lower()
            if "thumb" in rel or "cache" in rel:
                continue
            dest_name = f"wx_{fname}"
            dest = os.path.join(dest_folder, dest_name)
            # Skip if a file with this name already exists (different hash = different image)
            if os.path.exists(dest):
                base, ext = os.path.splitext(dest_name)
                dest = os.path.join(dest_folder, f"{base}_{fhash[:8]}{ext}")
            shutil.copy2(src, dest)
            imported += 1

    return {"imported": imported}


# ── List & Filter ──────────────────────────────────────────────────
def list_unprocessed(folder):
    """List all unprocessed screenshots."""
    if not os.path.isdir(folder):
        return {"error": f"文件夹不存在: {folder}", "images": [], "count": 0}

    tracking = load_tracking()
    processed = tracking.get("processed", {})
    images = []

    try:
        files = os.listdir(folder)
    except PermissionError:
        return {"error": f"没有权限读取文件夹: {folder}", "images": [], "count": 0}

    for fname in sorted(files):
        fpath = os.path.join(folder, fname)
        if not os.path.isfile(fpath) or not _is_image(fpath):
            continue
        if ".cold-storage" in fpath:
            continue
        fhash = _get_hash(fpath)
        if fhash in processed:
            continue

        stat = os.stat(fpath)
        images.append({
            "filename": fname,
            "path": _t(fpath),
            "size_kb": round(stat.st_size / 1024, 1),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"),
            "hash": fhash,
        })

    return {
        "folder": _t(folder),
        "count": len(images),
        "images": images,
    }


# ── Mark & Archive ─────────────────────────────────────────────────
def mark_processed(filenames, folder, category=None):
    """Mark screenshots as processed with an optional category."""
    tracking = load_tracking()
    processed = tracking.get("processed", {})

    for fname in filenames:
        fpath = os.path.join(folder, fname)
        if os.path.isfile(fpath):
            fhash = _get_hash(fpath)
            processed[fhash] = {
                "filename": fname,
                "processed_at": _now(),
                "category": category if category else "unclassified",
                "archived": False,
            }

    tracking["processed"] = processed
    tracking["last_scan"] = _now()
    save_tracking(tracking)
    return {"marked": len(filenames)}


def archive_processed(folder):
    """Move processed screenshots to cold storage."""
    tracking = load_tracking()
    processed = tracking.get("processed", {})
    cold = os.path.join(folder, ".cold-storage")
    os.makedirs(cold, exist_ok=True)

    archived = 0
    for fhash, info in processed.items():
        if info.get("archived"):
            continue
        fname = info.get("filename")
        src = os.path.join(folder, fname)
        if os.path.isfile(src):
            dst = os.path.join(cold, fname)
            shutil.move(src, dst)
            info["archived"] = True
            info["archived_at"] = _now()
            archived += 1

    tracking["processed"] = processed
    save_tracking(tracking)
    return {"archived": archived, "cold_storage": _t(cold)}


def cleanup_cold_storage(folder):
    """Delete expired screenshots from cold storage."""
    cold = os.path.join(folder, ".cold-storage")
    if not os.path.isdir(cold):
        return {"cleaned": 0, "cold_storage": _t(cold)}

    tracking = load_tracking()
    processed = tracking.get("processed", {})
    now = datetime.now()
    cleaned = 0

    for fname in os.listdir(cold):
        fpath = os.path.join(cold, fname)
        if not os.path.isfile(fpath) or not _is_image(fpath):
            continue

        fhash = None
        for h, info in processed.items():
            if info.get("filename") == fname:
                fhash = h
                break

        category = processed.get(fhash, {}).get("category", "unclassified") if fhash else "unclassified"
        retention = COLD_RETENTION_JUNK_DAYS if category == "junk" else COLD_RETENTION_DAYS

        mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
        if (now - mtime).days >= retention:
            os.remove(fpath)
            if fhash and fhash in processed:
                processed[fhash]["deleted"] = True
                processed[fhash]["deleted_at"] = _now()
            cleaned += 1

    tracking["processed"] = processed
    save_tracking(tracking)
    return {"cleaned": cleaned, "cold_storage": _t(cold)}


# ── Stats ──────────────────────────────────────────────────────────
def stats():
    tracking = load_tracking()
    cfg = load_config()
    folder = cfg["screenshot_folder"]

    processed = tracking.get("processed", {})
    total_processed = len(processed)
    archived = sum(1 for v in processed.values() if v.get("archived"))
    deleted = sum(1 for v in processed.values() if v.get("deleted"))

    by_category = {}
    for v in processed.values():
        cat = v.get("category", "unclassified")
        by_category[cat] = by_category.get(cat, 0) + 1

    total_in_folder = 0
    unprocessed_count = 0
    if os.path.isdir(folder):
        processed_hashes = set(processed.keys())
        for f in os.listdir(folder):
            fpath = os.path.join(folder, f)
            if os.path.isfile(fpath) and _is_image(fpath) and ".cold-storage" not in fpath:
                total_in_folder += 1
                if _get_hash(fpath) not in processed_hashes:
                    unprocessed_count += 1

    return {
        "folder": _t(folder),
        "total_in_folder": total_in_folder,
        "unprocessed": max(0, unprocessed_count),
        "total_processed": total_processed,
        "archived": archived,
        "deleted": deleted,
        "by_category": by_category,
    }


# ── Setup ──────────────────────────────────────────────────────────
def setup():
    """Return structured setup info for first-time use."""
    os_info = detect_os()
    guide = get_screenshot_setup_guide()
    wechat = detect_wechat_folder()
    cfg = load_config()

    return {
        "os": os_info,
        "screenshot_guide": guide,
        "wechat": wechat,
        "current_config": {
            "screenshot_folder": cfg["screenshot_folder"],
            "categories": cfg["categories"],
            "auto_process_time": cfg.get("auto_process_time"),
            "wechat_auto_import": cfg.get("wechat_auto_import"),
        },
        "setup_questions": [
            {
                "id": "screenshot_folder",
                "question": "截图放在哪个文件夹？",
                "default": cfg["screenshot_folder"],
                "note": guide.get("note", ""),
            },
            {
                "id": "wechat",
                "question": "要不要自动导入微信文件助手的图片？",
                "wechat_paths": wechat["candidates"],
                "note": "手机截图 → 发微信文件助手 → 电脑端自动整理，不需要装任何同步软件。",
            },
            {
                "id": "cron",
                "question": "想固定每天几点自动整理吗？（输入时间如 09:00，或跳过）",
                "default": cfg.get("auto_process_time"),
            },
            {
                "id": "categories",
                "question": "这五个分类够用吗？可以增减或改名。",
                "current": cfg["categories"],
            },
        ],
    }


# ── Process All (for cron / auto mode) ─────────────────────────────
def process_all():
    """Auto-mode: import wechat, list, clean up. Does NOT classify
    (the agent does that)."""
    cfg = load_config()
    folder = cfg["screenshot_folder"]
    os.makedirs(folder, exist_ok=True)

    result = {"imported": 0, "unprocessed": [], "cold_cleaned": 0}

    if cfg.get("wechat_auto_import") and cfg.get("wechat_folder"):
        wx_result = import_wechat_images(cfg)
        result["imported"] = wx_result.get("imported", 0)

    listing = list_unprocessed(folder)
    result["unprocessed"] = listing

    cc = cleanup_cold_storage(folder)
    result["cold_cleaned"] = cc.get("cleaned", 0)

    return result


# ── CLI ────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        _print_help()
        return

    cfg = load_config()
    folder = cfg["screenshot_folder"]
    cmd = sys.argv[1]

    if cmd == "--list":
        target = sys.argv[2] if len(sys.argv) > 2 else folder
        result = list_unprocessed(target)
        _print(result)

    elif cmd == "--mark-done":
        if len(sys.argv) < 3:
            _print({"error": "请指定文件名和分类"})
            return
        filenames = []
        category = None
        for arg in sys.argv[2:]:
            valid_keys = [c["key"] for c in cfg["categories"]]
            if arg in valid_keys:
                category = arg
            else:
                filenames.append(arg)
        result = mark_processed(filenames, folder, category)
        _print(result)

    elif cmd == "--archive":
        result = archive_processed(folder)
        _print(result)

    elif cmd == "--cleanup":
        result = cleanup_cold_storage(folder)
        _print(result)

    elif cmd == "--stats":
        result = stats()
        _print(result)

    elif cmd == "--setup":
        result = setup()
        _print(result)

    elif cmd == "--detect-wechat":
        result = detect_wechat_folder()
        _print(result)

    elif cmd == "--process-all":
        result = process_all()
        _print(result)

    elif cmd == "--needs-setup":
        # Returns {"needs_setup": true} if config file doesn't exist
        needs = not os.path.exists(CONFIG_FILE)
        _print({"needs_setup": needs})

    elif cmd == "--config":
        _print(cfg)

    elif cmd == "--set-folder":
        if len(sys.argv) < 3:
            _print({"error": "请指定文件夹路径"})
            return
        new_folder = os.path.abspath(sys.argv[2])
        if not os.path.isdir(new_folder):
            os.makedirs(new_folder, exist_ok=True)
        cfg["screenshot_folder"] = _t(new_folder)
        save_config(cfg)
        _print({"ok": True, "screenshot_folder": _t(new_folder)})

    elif cmd == "--set-cron":
        time_val = sys.argv[2] if len(sys.argv) > 2 else None
        cfg["auto_process_time"] = time_val
        save_config(cfg)
        _print({"ok": True, "auto_process_time": time_val})

    elif cmd == "--set-wechat":
        path = sys.argv[2] if len(sys.argv) > 2 else None
        if path and not os.path.isdir(path):
            _print({"error": f"目录不存在: {path}"})
            return
        cfg["wechat_folder"] = _t(path) if path else None
        cfg["wechat_auto_import"] = bool(path)
        save_config(cfg)
        _print({"ok": True, "wechat_folder": cfg["wechat_folder"],
                "wechat_auto_import": cfg["wechat_auto_import"]})

    elif cmd == "--reset":
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        result = _reset(filename, folder)
        _print(result)

    else:
        _print({"error": f"未知命令: {cmd}"})
        _print_help()


def _print(data):
    """Print JSON with UTF-8 encoding."""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json_str)


def _print_help():
    sys.stdout.reconfigure(encoding="utf-8")
    print(__doc__)


def _reset(filename, folder):
    """Reset processed state."""
    tracking = load_tracking()
    if filename:
        removed = 0
        fpath = os.path.join(folder, filename)
        if os.path.isfile(fpath):
            fhash = _get_hash(fpath)
            if fhash in tracking.get("processed", {}):
                del tracking["processed"][fhash]
                removed = 1
        save_tracking(tracking)
        return {"reset": removed, "filename": filename}
    else:
        save_tracking({"processed": {}, "last_scan": None})
        return {"reset": "all"}


if __name__ == "__main__":
    main()
