# Second Brain MCP Server

Thư mục này chứa cấu hình mẫu để kết nối các AI Agent (Cline, Claude Desktop, v.v.) với Second Brain thông qua Model Context Protocol (MCP).

## 1. Cài đặt Dependency
Đảm bảo đã cài đặt package `mcp` trong môi trường Python của bạn:
```bash
cd /path/to/Second-brain
pip install -r requirements-mcp.txt
```

## 2. Cấu hình Client
Thêm nội dung từ `config-sample.json` vào file cấu hình MCP của client tương ứng. 
Lưu ý: Thay thế `/absolute/path/to/llm-wiki-template` bằng đường dẫn tuyệt đối thực tế trên máy của bạn.

Ví dụ vị trí file cấu hình MCP của một số client:
- **Cline (VS Code)**: `~/AppData/Roaming/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` (Windows)
- **Claude Desktop**: `~/AppData/Roaming/Claude/claude_desktop_config.json` (Windows)

## 3. Các Tính Năng (Tools & Resources)
MCP Server `second-brain` cung cấp:
- **Tools**:
  - `search_knowledge`: Tìm kiếm FTS5 trong wiki/sessions.
  - `rebuild_index`: Xây dựng lại index tìm kiếm.
  - `check_health`: Đánh giá sức khỏe và xuất báo cáo audit wiki.
  - `find_wiki_orphans`: (Có cảnh báo destructive) Tìm và nối bài mồ côi.
  - `mark_duplicate_raws`: (Có cảnh báo destructive) Đánh dấu tài liệu thô trùng lặp.
  - `ingest_codebase`: (Có cảnh báo destructive) Chuyển cấu trúc repo thành file markdown nạp vào wiki raw/.
- **Resources**:
  - `brain://wiki/index`: Nội dung của Master Index.
  - `brain://wiki/{article}`: Nội dung chi tiết của một bài viết cụ thể (không cần đuôi .md).
