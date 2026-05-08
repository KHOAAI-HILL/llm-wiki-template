import sys
from pathlib import Path

# Đảm bảo import được các module cùng thư mục scripts/ (Fix lỗi relative import khi gọi từ nơi khác)
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP

from search_sessions import run_search
from build_search_index import build_index
from audit import run_audit
from resolve_orphans import find_orphans
from mark_duplicates import mark_dupes
from ingest_codebase import ingest_repo

WORKSPACE = Path.cwd()
WIKI_INDEX = WORKSPACE / "wiki" / "index.md"
GRAPH_JSON = WORKSPACE / "wiki" / "_graph.json"

# Parse arguments trước khi khởi tạo FastMCP (host/port nằm trong constructor)
import argparse
_parser = argparse.ArgumentParser()
_parser.add_argument("--transport", default="stdio", choices=["stdio", "streamable-http"])
_parser.add_argument("--port", type=int, default=8787)
_parser.add_argument("--host", type=str, default="127.0.0.1",
                     help="Host IP to bind (use 0.0.0.0 for public access)")
_args = _parser.parse_args()

# Khởi tạo MCP Server
mcp = FastMCP("second-brain", host=_args.host, port=_args.port)

# ═══════════════════════════════
# TOOLS — Hành động có side-effect
# ═══════════════════════════════

@mcp.tool()
def search_knowledge(query: str, project: str | None = None,
                     source: str | None = None, limit: int = 10) -> list[dict]:
    """Tìm kiếm FTS5 Index của Second Brain (sessions + wiki).
    
    Args:
        query: Từ khóa tìm kiếm (FTS5 syntax)
        project: Lọc theo tên project (ví dụ: 'crm-cli', 'hermes-agent')
        source: Lọc theo loại ('session' hoặc 'wiki')
        limit: Số kết quả tối đa (mặc định 10)
    """
    return run_search(query, project, source, limit)


@mcp.tool()
def rebuild_index(full: bool = False) -> dict:
    """Rebuild SQLite FTS5 search index.
    
    Args:
        full: True = xóa toàn bộ index rồi build lại. False = incremental update.
    """
    return build_index(full=full)


@mcp.tool()
def check_health() -> dict:
    """Chạy Wiki Audit + Health Score analysis.
    
    Trả về audit report (stubs, bloated, broken links).
    """
    audit = run_audit()
    return {
        "audit": audit
    }


@mcp.tool()
def find_wiki_orphans(apply: bool = False) -> dict:
    """Tìm các bài wiki mồ côi (không có bài nào link tới).
    [DESTRUCTIVE HINT]: Nếu apply=True, tool này sẽ SỬA ĐỔI FILE markdown để tự động thêm backlink.
    
    Args:
        apply: True = tự động thêm backlink vào parent. False = dry-run chỉ báo cáo.
    """
    return find_orphans(apply_mode=apply)


@mcp.tool()
def mark_duplicate_raws(dry_run: bool = True) -> dict:
    """Đánh dấu các raw source trùng lặp trong absorb-log.
    [DESTRUCTIVE HINT]: Nếu dry_run=False, tool này sẽ SỬA ĐỔI FILE absorb-log.json.
    
    Args:
        dry_run: True = chỉ báo cáo, không ghi file. False = ghi thay đổi.
    """
    return mark_dupes(dry_run=dry_run)


@mcp.tool()
def ingest_codebase(repo_path: str) -> dict:
    """Trích xuất Python AST từ một repository thành file Markdown nạp vào raw/.
    [DESTRUCTIVE HINT]: Sẽ tạo mới các file markdown trong thư mục raw/repos.
    
    Args:
        repo_path: Đường dẫn tuyệt đối tới thư mục repository.
    """
    return ingest_repo(repo_path)


@mcp.tool()
def get_graph_insights() -> dict:
    """Trả về phân tích Knowledge Graph: God Nodes, Surprising Connections, Isolated Nodes.
    
    Yêu cầu: Chạy `python wiki/_build_graph.py` trước để sinh dữ liệu.
    Dữ liệu này giúp Agent phát hiện knowledge gaps và gợi ý chủ đề nghiên cứu.
    """
    if not GRAPH_JSON.exists():
        return {"error": "File _graph.json chưa tồn tại. Chạy: python wiki/_build_graph.py"}
    import json
    try:
        graph = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
        return graph.get("insights", {})
    except Exception as e:
        return {"error": f"Lỗi đọc graph data: {str(e)}"}

# ═══════════════════════════════
# RESOURCES — Dữ liệu đọc trực tiếp (Read-only)
# ═══════════════════════════════

@mcp.resource("brain://wiki/index")
def get_wiki_index() -> str:
    """Master catalog của toàn bộ wiki — danh sách bài, aliases, tóm tắt."""
    if WIKI_INDEX.exists():
        return WIKI_INDEX.read_text(encoding="utf-8")
    return "Lỗi: Không tìm thấy file index.md"


@mcp.resource("brain://wiki/{article}")
def get_wiki_article(article: str) -> str:
    """Đọc nội dung một bài wiki theo tên (không cần đuôi .md)."""
    base = WORKSPACE / "wiki"
    for subdir in ["concepts", "tools", "people", "comparisons", ""]:
        candidate = base / subdir / f"{article}.md"
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Wiki article '{article}' not found")


# ═══════════════════════════════
# ENTRYPOINT
# ═══════════════════════════════

if __name__ == "__main__":
    mcp.run(transport=_args.transport)
