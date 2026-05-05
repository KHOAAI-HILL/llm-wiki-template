#!/usr/bin/env python3
"""
brain — CLI tool for LLM Wiki Template
========================================
Usage:
    brain update              Cập nhật workflows + AGENTS.md mới nhất
    brain update --dry-run    Xem trước thay đổi (không ghi file)
    brain update --force      Ghi đè không hỏi
    brain version             Hiển thị phiên bản
    brain status              Kiểm tra trạng thái vault
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

from brain_cli import __version__

# ─── Cấu hình ──────────────────────────────────────────────
TEMPLATE_REPO = "KHOAAI-HILL/llm-wiki-template"
BRANCH = "master"
RAW_BASE = f"https://raw.githubusercontent.com/{TEMPLATE_REPO}/{BRANCH}"
API_BASE = f"https://api.github.com/repos/{TEMPLATE_REPO}/contents"

# Thư mục cần tạo nếu chưa có
ENSURE_DIRS = [
    "sessions",
    ".agents/workflows",
]

# ─── Branding ───────────────────────────────────────────────
LOGO = r"""
  ╔══════════════════════════════════════╗
  ║   🧠  LLM Wiki — Second Brain CLI  ║
  ╚══════════════════════════════════════╝
"""


def get_vault_root():
    """Tìm thư mục gốc của vault (chứa AGENTS.md)."""
    current = Path.cwd()
    for _ in range(5):
        if (current / "AGENTS.md").exists():
            return current
        current = current.parent
    return Path.cwd()


def fetch_json(url):
    """Fetch JSON từ GitHub API."""
    req = urllib.request.Request(url, headers={"User-Agent": "brain-cli"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        return None


def fetch_text(url):
    """Fetch nội dung text từ GitHub raw."""
    req = urllib.request.Request(url, headers={"User-Agent": "brain-cli"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None


def get_remote_files(path):
    """Lấy danh sách file từ một thư mục trên GitHub."""
    data = fetch_json(f"{API_BASE}/{path}")
    if not data or not isinstance(data, list):
        return []
    return [item for item in data if item.get("type") == "file"]


def compare_content(local_path, remote_content):
    """So sánh nội dung. True nếu khác nhau hoặc file chưa tồn tại."""
    if not local_path.exists():
        return True
    local = local_path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    remote = remote_content.replace("\r\n", "\n").strip()
    return local != remote


# ─── Commands ───────────────────────────────────────────────


def cmd_update(args):
    """Cập nhật vault với workflows và cấu hình mới nhất."""
    vault_root = get_vault_root()

    print(LOGO)
    print(f"  📂 Vault:    {vault_root}")
    print(f"  🔗 Template: {TEMPLATE_REPO} ({BRANCH})")
    if args.dry_run:
        print("  ⚠️  Chế độ DRY-RUN — không ghi file")
    print("─" * 42)

    # 1. Tạo thư mục thiếu
    print("\n→ Kiểm tra cấu trúc thư mục...")
    for d in ENSURE_DIRS:
        dir_path = vault_root / d
        if not dir_path.exists():
            if not args.dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Tạo: {d}/")
        else:
            print(f"  ✓  {d}/")

    # 2. Kiểm tra workflows
    print("\n→ Fetching workflows...")
    changes = []

    remote_workflows = get_remote_files(".agents/workflows")
    if not remote_workflows:
        print("  ❌ Không kết nối được GitHub. Kiểm tra mạng.")
        return 1

    for item in remote_workflows:
        name = item["name"]
        remote_path = f".agents/workflows/{name}"
        local_path = vault_root / remote_path
        content = fetch_text(f"{RAW_BASE}/{remote_path}")
        if content is None:
            continue
        if compare_content(local_path, content):
            status = "MỚI" if not local_path.exists() else "CẬP NHẬT"
            changes.append((remote_path, content, status))
            print(f"  📄 [{status}] {name}")
        else:
            print(f"  ✓  {name}")

    # 3. Kiểm tra AGENTS.md
    print("\n→ Checking AGENTS.md...")
    agents_content = fetch_text(f"{RAW_BASE}/AGENTS.md")
    if agents_content and compare_content(vault_root / "AGENTS.md", agents_content):
        changes.append(("AGENTS.md", agents_content, "CẬP NHẬT"))
        print("  📄 [CẬP NHẬT] AGENTS.md")
    else:
        print("  ✓  AGENTS.md")

    # 4. Kiểm tra update.py
    update_content = fetch_text(f"{RAW_BASE}/update.py")
    if update_content and compare_content(vault_root / "update.py", update_content):
        changes.append(("update.py", update_content, "CẬP NHẬT"))
        print("  📄 [CẬP NHẬT] update.py")

    # 5. Áp dụng
    print()
    if not changes:
        print("  ✅ Vault đã mới nhất! Không cần cập nhật.")
        return 0

    print(f"  📊 {len(changes)} thay đổi:")
    for path, _, status in changes:
        print(f"     [{status}] {path}")

    if args.dry_run:
        print("\n  ⚠️  DRY-RUN: Bỏ --dry-run để áp dụng.")
        return 0

    if not args.force:
        print()
        try:
            answer = input("  ❓ Áp dụng? (y/N): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  ⏹  Đã hủy.")
            return 0
        if answer not in ("y", "yes"):
            print("  ⏹  Đã hủy.")
            return 0

    print("\n→ Applying updates...")
    for path, content, status in changes:
        file_path = vault_root / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        print(f"  ✅ {path}")

    # Log
    log_path = vault_root / "sessions" / ".update-log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_entry = f"\n## [{datetime.now().strftime('%Y-%m-%d %H:%M')}] brain update\n"
    for path, _, status in changes:
        log_entry += f"- [{status}] `{path}`\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"\n  🎉 Đã cập nhật {len(changes)} file!")
    print(f"  📝 Log: sessions/.update-log.md")
    return 0


def cmd_status(args):
    """Hiển thị trạng thái vault."""
    vault_root = get_vault_root()

    print(LOGO)
    print(f"  📂 Vault: {vault_root}")
    print("─" * 42)

    # Kiểm tra AGENTS.md
    agents = vault_root / "AGENTS.md"
    print(f"\n  {'✅' if agents.exists() else '❌'} AGENTS.md")

    # Đếm workflows
    wf_dir = vault_root / ".agents" / "workflows"
    if wf_dir.exists():
        wfs = list(wf_dir.glob("*.md"))
        print(f"  ✅ {len(wfs)} workflows")
        for wf in sorted(wfs):
            print(f"     • {wf.name}")
    else:
        print("  ❌ Chưa có .agents/workflows/")

    # Đếm sessions
    sess_dir = vault_root / "sessions"
    if sess_dir.exists():
        sessions = list(sess_dir.glob("session-summary-*.md"))
        ctx = sess_dir / "current-context.md"
        print(f"  ✅ sessions/ ({len(sessions)} phiên)")
        print(f"     {'✅' if ctx.exists() else '⬜'} current-context.md")
    else:
        print("  ⬜ Chưa có sessions/ (chạy brain update)")

    # Đếm wiki
    wiki_dir = vault_root / "wiki"
    if wiki_dir.exists():
        articles = list(wiki_dir.rglob("*.md"))
        articles = [a for a in articles if not a.name.startswith("_")]
        print(f"  ✅ wiki/ ({len(articles)} bài)")
    else:
        print("  ⬜ Chưa có wiki/")

    # Đếm raw
    raw_dir = vault_root / "raw"
    if raw_dir.exists():
        raws = list(raw_dir.rglob("*.md"))
        raws = [r for r in raws if not r.name.startswith("_")]
        print(f"  ✅ raw/ ({len(raws)} nguồn)")

    return 0


def cmd_version(args):
    """Hiển thị phiên bản."""
    print(f"brain v{__version__}")
    return 0


# ─── Main entry point ──────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        prog="brain",
        description="🧠 LLM Wiki — Second Brain CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  update        Cập nhật workflows mới nhất từ template
  status        Kiểm tra trạng thái vault
  version       Hiển thị phiên bản

Examples:
  brain update              # Cập nhật (có hỏi xác nhận)
  brain update --dry-run    # Xem trước thay đổi
  brain update --force      # Cập nhật không hỏi
  brain status              # Kiểm tra vault
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Lệnh cần chạy")

    # update
    p_update = subparsers.add_parser("update", help="Cập nhật workflows mới nhất")
    p_update.add_argument("--dry-run", action="store_true", help="Xem trước (không ghi)")
    p_update.add_argument("--force", action="store_true", help="Không hỏi xác nhận")

    # status
    subparsers.add_parser("status", help="Kiểm tra trạng thái vault")

    # version
    subparsers.add_parser("version", help="Hiển thị phiên bản")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    commands = {
        "update": cmd_update,
        "status": cmd_status,
        "version": cmd_version,
    }

    handler = commands.get(args.command)
    if handler:
        sys.exit(handler(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
