#!/usr/bin/env python3
"""
LLM Wiki Template — Update Script
===================================
Cập nhật vault hiện tại với workflows và cấu hình mới nhất từ template gốc.
Chỉ cập nhật các file hệ thống — KHÔNG BAO GIỜ chạm vào dữ liệu cá nhân.

Sử dụng:
    python update.py              # Cập nhật workflows + AGENTS.md
    python update.py --dry-run    # Xem trước thay đổi (không ghi file)
    python update.py --force      # Ghi đè không hỏi
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# ─── Cấu hình ──────────────────────────────────────────────
TEMPLATE_REPO = "KHOAAI-HILL/llm-wiki-template"
BRANCH = "master"
RAW_BASE = f"https://raw.githubusercontent.com/{TEMPLATE_REPO}/{BRANCH}"
API_BASE = f"https://api.github.com/repos/{TEMPLATE_REPO}/contents"

# File/thư mục SẼ được cập nhật
UPDATE_TARGETS = [
    ".agents/workflows/",   # Tất cả workflow files
    "AGENTS.md",            # Sổ tay Agent
]

# File/thư mục KHÔNG BAO GIỜ bị ghi đè
PROTECTED = [
    "raw/",
    "wiki/",
    "sessions/",
    "outputs/",
    "integrations/",
    ".obsidian/",
    "README.md",
    "README-vi.md",
    ".gitignore",
    ".env",
    ".env.local",
]

# Thư mục cần tạo nếu chưa có
ENSURE_DIRS = [
    "sessions",
    ".agents/workflows",
]


def get_vault_root():
    """Tìm thư mục gốc của vault (chứa AGENTS.md)."""
    current = Path.cwd()
    # Tìm ngược lên tối đa 3 cấp
    for _ in range(4):
        if (current / "AGENTS.md").exists():
            return current
        current = current.parent
    # Fallback: dùng thư mục hiện tại
    return Path.cwd()


def fetch_json(url):
    """Fetch JSON từ GitHub API."""
    req = urllib.request.Request(url, headers={"User-Agent": "llm-wiki-updater"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  ❌ Lỗi HTTP {e.code}: {url}")
        return None
    except urllib.error.URLError as e:
        print(f"  ❌ Lỗi kết nối: {e.reason}")
        return None


def fetch_text(url):
    """Fetch nội dung text từ GitHub raw."""
    req = urllib.request.Request(url, headers={"User-Agent": "llm-wiki-updater"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"  ❌ Không tải được: {url}")
        return None


def get_remote_files(path):
    """Lấy danh sách file từ một thư mục trên GitHub."""
    url = f"{API_BASE}/{path}"
    data = fetch_json(url)
    if not data or not isinstance(data, list):
        return []
    return [item for item in data if item.get("type") == "file"]


def compare_content(local_path, remote_content):
    """So sánh nội dung local vs remote. Trả về True nếu khác nhau."""
    if not local_path.exists():
        return True  # File mới
    local_content = local_path.read_text(encoding="utf-8")
    # Normalize line endings
    return local_content.replace("\r\n", "\n").strip() != remote_content.replace("\r\n", "\n").strip()


def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    vault_root = get_vault_root()

    print("=" * 55)
    print("  🧠 LLM Wiki Template — Cập Nhật Tự Động")
    print("=" * 55)
    print(f"  📂 Vault: {vault_root}")
    print(f"  🔗 Template: {TEMPLATE_REPO} ({BRANCH})")
    if dry_run:
        print("  ⚠️  Chế độ DRY-RUN — không ghi file")
    print("-" * 55)

    # ─── Bước 1: Tạo thư mục thiếu ─────────────────────────
    print("\n📁 Kiểm tra cấu trúc thư mục...")
    for d in ENSURE_DIRS:
        dir_path = vault_root / d
        if not dir_path.exists():
            if not dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Tạo thư mục: {d}/")
        else:
            print(f"  ✓  Đã có: {d}/")

    # ─── Bước 2: Cập nhật workflows ─────────────────────────
    print("\n📥 Kiểm tra workflows mới...")
    changes = []

    # Lấy danh sách workflow từ remote
    remote_workflows = get_remote_files(".agents/workflows")
    if not remote_workflows:
        print("  ❌ Không lấy được danh sách workflows từ GitHub.")
        print("     Kiểm tra kết nối mạng và thử lại.")
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
            print(f"  📄 [{status}] {remote_path}")
        else:
            print(f"  ✓  Đã mới nhất: {remote_path}")

    # ─── Bước 3: Cập nhật AGENTS.md ─────────────────────────
    print("\n📥 Kiểm tra AGENTS.md...")
    agents_content = fetch_text(f"{RAW_BASE}/AGENTS.md")
    if agents_content:
        local_agents = vault_root / "AGENTS.md"
        if compare_content(local_agents, agents_content):
            changes.append(("AGENTS.md", agents_content, "CẬP NHẬT"))
            print(f"  📄 [CẬP NHẬT] AGENTS.md")
        else:
            print(f"  ✓  Đã mới nhất: AGENTS.md")

    # ─── Bước 4: Tổng kết và áp dụng ───────────────────────
    print("\n" + "=" * 55)
    if not changes:
        print("  ✅ Vault đã cập nhật mới nhất! Không có thay đổi.")
        return 0

    print(f"  📊 Tìm thấy {len(changes)} thay đổi:")
    for path, _, status in changes:
        print(f"     [{status}] {path}")

    if dry_run:
        print("\n  ⚠️  DRY-RUN: Không ghi file. Bỏ --dry-run để áp dụng.")
        return 0

    if not force:
        print()
        answer = input("  ❓ Áp dụng thay đổi? (y/N): ").strip().lower()
        if answer not in ("y", "yes"):
            print("  ⏹  Đã hủy.")
            return 0

    # Ghi file
    for path, content, status in changes:
        file_path = vault_root / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        print(f"  ✅ Đã ghi: {path}")

    # Ghi log
    log_path = vault_root / "sessions" / ".update-log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_entry = f"\n## [{datetime.now().strftime('%Y-%m-%d %H:%M')}] Update from template\n"
    for path, _, status in changes:
        log_entry += f"- [{status}] `{path}`\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"\n  🎉 Đã cập nhật {len(changes)} file thành công!")
    print(f"  📝 Log đã ghi tại: sessions/.update-log.md")
    print("\n" + "=" * 55)
    return 0


if __name__ == "__main__":
    sys.exit(main())
