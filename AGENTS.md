# Second Brain — Agent Schema

> This file is the **single source of truth** for any LLM operating on this vault.
> Read this FIRST before making any changes.

## ⚠️ KNOWN PLATFORM BUGS (Mẹo Tùy Chọn)

> [!tip] Vấn đề với `grep_search` trên các Vault lớn (như OneDrive)
> Ở một số môi trường có hàng ngàn file hoặc đồng bộ cloud, tool `grep_search` có thể bị timeout.
> Nếu gặp lỗi "context canceled", hãy chuyển sang dùng PowerShell `Select-String` hoặc FTS5.

**Workaround — Dùng PowerShell `Select-String`:**
```powershell
# Tìm kiếm text trong toàn bộ wiki (bao gồm sub-folder, không phân biệt hoa thường)
Get-ChildItem -Path ".\wiki" -Filter "*.md" -Recurse | Select-String -Pattern "từ_khóa" -Encoding utf8

# Tìm trong raw/
Get-ChildItem -Path ".\raw" -Filter "*.md" -Recurse | Select-String -Pattern "từ_khóa" -Encoding utf8
```

**Chiến lược tìm kiếm ưu tiên:**
1. **Ưu tiên 1 (MCP):** Gọi tool `search_knowledge(query="từ_khóa")` — nhanh nhất, chính xác nhất qua FTS5.
2. **Ưu tiên 2 (MCP):** Đọc resource `brain://wiki/index` — lấy Master catalog.
3. **Ưu tiên 3 (MCP):** Đọc resource `brain://wiki/{article}` — lấy bài cụ thể.
4. **Fallback 1 (Khi không có MCP):** `view_file` trên `index.md` → scan aliases/summary → `view_file` bài cụ thể.
5. **Fallback 2 (Khi không có MCP):** `run_command` với PowerShell `Select-String` (như trên).

## MCP Server Integration

Second Brain cung cấp MCP Server (`second-brain`) cho các AI Agent kết nối trực tiếp.

### Cấu hình
Xem `integrations/mcp/config-sample.json` và `integrations/mcp/README.md`.

### Tools khả dụng
| Tool | Mô tả | Read/Write |
|------|--------|-----------|
| `search_knowledge` | FTS5 full-text search (sessions, wiki) | Read |
| `rebuild_index` | Rebuild FTS5 index | Write |
| `check_health` | Wiki audit + health score | Read |
| `find_wiki_orphans` | Tìm bài mồ côi, tùy chọn auto-fix | Read/Write |
| `mark_duplicate_raws`| Đánh dấu raw trùng lặp | Read/Write |
| `ingest_codebase` | Trích xuất AST repo | Write |

### Resources
| URI | Mô tả |
|-----|--------|
| `brain://wiki/index` | Master Index |
| `brain://wiki/{article}` | Bài wiki cụ thể theo tên |

Khi Agent có hỗ trợ MCP, **luôn ưu tiên** dùng tools/resources trên thay vì gọi subprocess.

## Purpose

This Obsidian vault is an **AI-managed knowledge base** following the Karpathy LLM Knowledge Base methodology. The LLM writes and maintains all wiki content. The human rarely edits directly — they ingest raw data, ask questions, and review outputs.

## Directory Structure

```
Second-brain/
├── raw/                 ← Source documents. NEVER modify, only ADD.
│   ├── articles/        ← Web articles (clipped or pasted)
│   ├── papers/          ← Academic papers, PDF notes
│   ├── repos/           ← GitHub repo notes, README summaries
│   ├── videos/          ← YouTube transcripts, video notes
│   ├── tweets/          ← X/Twitter threads, social posts
│   └── misc/            ← Images, CSV, datasets, other
│
├── wiki/                ← Compiled knowledge. AI-maintained.
│   ├── index.md         ← Master index (MUST stay updated)
│   ├── glossary.md      ← Key terms and definitions
│   ├── concepts/        ← Concept articles (the core)
│   ├── tools/           ← Tool/product evaluations
│   ├── people/          ← Notable people profiles
│   └── comparisons/     ← A vs B analysis articles
│
├── outputs/             ← Query results, generated content
│   ├── reports/         ← Deep-dive research reports
│   ├── slides/          ← Marp-format slide decks
│   ├── charts/          ← Generated visualizations
│   └── summaries/       ← Quick summaries on demand
│
├── sessions/            ← Session logs TẬP TRUNG từ tất cả dự án
│   ├── hermes-agent/    ← Sessions từ Hermes-Agent
│   ├── kenh-youtube/    ← Sessions từ kenh-youtube
│   ├── bai-viet-mxh/    ← Sessions từ bai-viet-mxh
│   ├── rag-notebooklm/  ← Sessions từ RAG-notebooklm
│   └── second-brain/    ← Sessions từ Second-brain
│
└── AGENTS.md            ← THIS FILE — vault schema
```

## File Conventions

### Naming
- **kebab-case**: `retrieval-augmented-generation.md`
- **No spaces**: Use hyphens
- **Descriptive**: Name should convey content at a glance

### Frontmatter (YAML) — Required for ALL files

```yaml
---
title: "Human-readable title"
sources: ["[[raw/source-1.md]]", "[[raw/source-2.md]]"]
date_added: 2026-04-03
tags: [concept, ai, rag]
aliases: [alias1, alias2, tên tiếng Việt]
status: draft | reviewed | canonical
related:
  - "[[other-article]]"
  - "[[another-one]]"
summary: "One-line summary for index.md"
---
```

### Content Rules
- Use `[[wikilinks]]` for internal links (Obsidian-native)
- Images: Store in same directory as the .md referencing them
- Code blocks: Always specify language (```python, ```bash, etc.)
- Headers: Start at ## (h2) inside articles (h1 = title in frontmatter)

### Writing Tone — Bách Khoa Toàn Thư
- Viết giọng văn trung lập, dẫn chứng cụ thể. Không phải blog, không phải notes.
- Tránh: "thú vị là", "đáng chú ý", "rất quan trọng", "groundbreaking", "legendary"
- Tránh editorial voice: "interestingly", "importantly", "it should be noted"
- Cấu trúc bài theo chủ đề (thematic), không theo dòng thời gian (chronological)
- Cảm xúc/nhận định truyền qua direct quotes từ raw source
- Ưu tiên quotes đắt giá, tránh quote tràn lan
- 1 ý = 1 câu. Câu ngắn. Viết đoạn văn, hạn chế bullet-point trừ khi liệt kê.
- Attribution thay vì assertion: "Karpathy mô tả nó là..." thay vì "Nó rất..."

## Index Maintenance

The file `wiki/index.md` is the **master catalog**. Rules:
1. MUST list every article in `wiki/` with one-line summary
2. Group by subdirectory (concepts, tools, people, comparisons)
3. Update `index.md` EVERY time a wiki article is added/removed
4. Include article count and last-updated timestamp

## Compilation Rules

When compiling from `raw/` to `wiki/`:
1. Read the raw source completely
2. Check `wiki/absorb-log.json` để xem raw nào đã compile
3. Identify key concepts, tools, and people mentioned
4. For each:
   - Check if wiki article already exists → UPDATE
   - If not → CREATE new article
5. **Re-read toàn bộ bài wiki TRƯỚC KHI cập nhật — non-negotiable**
6. Sau khi đọc lại, tự hỏi: "Entry mới bổ sung chiều sâu gì mà bài chưa có?"
   - Nếu câu trả lời là "không gì mới" → KHÔNG sửa bài
7. **Contradiction Check** — Trước khi ghi đè bất kỳ thông tin nào, kiểm tra xem claim mới có mâu thuẫn với claim cũ không. Nếu mâu thuẫn → KHÔNG ghi đè, thêm callout `[!warning] Mâu Thuẫn Chưa Giải Quyết` và tag `needs-review`.
8. Khi cập nhật, **integrate** nội dung mới vào mạch viết hiện có — không chỉ append bullet point ở cuối
9. Add `[[backlinks]]` to related existing articles
10. Update `index.md`
11. Update `wiki/absorb-log.json` — ghi nhận raw đã compile
12. Never delete content from existing articles — refine and integrate

## Quality Standards

- Each wiki article should be **self-contained** (understandable alone)
- Minimum 200 words per concept article
- Each article should link to ≥2 other wiki articles
- Avoid duplicating content — link instead
- Use Vietnamese for content, English for technical terms

### Article Size Guardrails
- **Giới hạn:** 15–120 dòng nội dung (không tính frontmatter)
  - Dưới 15 dòng → tag `status: stub`, ưu tiên bổ sung khi có raw mới
  - Trên 120 dòng → xem xét tách sub-topic thành bài riêng
- **Anti-Cramming:** Nếu sub-topic xuất hiện ≥3 đoạn trong 1 bài → tách thành bài con
- **Anti-Thinning:** Không tạo bài nếu không viết được ≥3 câu có ý nghĩa. Mỗi lần touch bài → phải làm nó giàu hơn

### Entity-Type Templates

Mỗi loại bài wiki có cấu trúc riêng. Dùng đúng template theo entity type:

**Concept** (`wiki/concepts/`):
- `## Định Nghĩa` — 1 đoạn văn rõ ràng
- `## [Sections thematic]` — tùy chủ đề (Kiến Trúc, Cơ Chế, Ví Dụ...)
- `## Liên Hệ / Ứng Dụng` — context thực tế
- `## Nguồn Tham Khảo`

**Tool** (`wiki/tools/`):
- `## Tổng Quan` — tool là gì, ai tạo, mục đích
- `## Vai Trò Trong [Context]` — cách dùng trong hệ thống
- `## Lợi Thế / Hạn Chế` — đánh giá trung lập
- `## Nguồn Tham Khảo`

**Person** (`wiki/people/`):
- `## Tiểu Sử` — 2-3 câu background
- `## Đóng Góp Cho Kiến Thức Trong Wiki Này` — liên hệ trực tiếp đến wiki
- `## Nguồn Tham Khảo`

**Comparison** (`wiki/comparisons/`):
- `## Bối Cảnh` — tại sao so sánh
- `## Bảng So Sánh` — bảng tiêu chí rõ ràng
- `## Phân Tích` — đánh giá từng chiều
- `## Kết Luận`

**Report/Summary** (`outputs/`):
- `## Context` — bối cảnh yêu cầu
- `## Phân Tích` — nội dung chính
- `## Kết Luận / Hành Động`
- `## Nguồn`

## Classify-Before-Extract

Trước khi compile raw/ thành wiki, **phân loại nguồn theo type** để áp dụng extraction strategy phù hợp:

| Source Type | Đặc điểm | Extraction Strategy |
|-------------|----------|-------------------|
| **Tweet/Thread** | Ngắn, dense, có replies | Extract assertions chính + notable replies. Mỗi reply đáng giá = 1 data point |
| **Article/Gist** | Dài, có cấu trúc | Extract theo sections. Tìm thesis chính + supporting arguments |
| **Paper/Report** | Formal, có abstract/methodology | Extract abstract → findings → implications. Chú ý claims có evidence |
| **Diagram/Image** | Visual | Bóc tách layers, components, flows. Mô tả bằng text + tables |
| **Video/Transcript** | Dài, conversational | Tìm key moments, quotes đắt giá. Bỏ filler/tangents |
| **Repo/Code** | Technical | Extract architecture, patterns, API surface. README là starting point |

**Quy tắc:** Không xử lý mọi raw giống nhau. Report 50 trang cần strategy khác thread 5 tweets.

## Operations Log

File `wiki/ops-log.md` ghi lại **mọi operations** theo thời gian:
- Append 1 dòng `## [YYYY-MM-DD] action | title` sau mỗi ingest, compile, ask, cleanup
- KHÔNG sửa entries cũ — chỉ append
- Các workflows `/ingest`, `/compile`, `/ask`, `/cleanup` PHẢI append vào log

## Dual Output Rule

Mọi task tạo ra kiến thức (hỏi đáp, phân tích, so sánh) phải xem xét produce **2 outputs**:
1. **Output 1:** Trả lời trực tiếp cho user
2. **Output 2:** Cập nhật wiki nếu câu trả lời chứa insight mới chưa có trong wiki

Quy tắc: Nếu `/ask` tạo ra synthesis có giá trị → hỏi user có muốn file-back vào wiki không.

## AutoResearch

Workflow `/autoresearch [chủ đề]` tự động search web, đánh giá nguồn, ingest vào raw/, và tạo báo cáo tổng hợp. Cấu hình tại `raw/_research_program.md`. Output lưu tại `outputs/reports/`. Compile vào wiki CHỈ khi user đồng ý.

## Agent Integrations

This vault can be connected to external AI agents for autonomous access:

### Hermes Agent
See `integrations/hermes/` for:
- `SKILL.md` — Drop-in skill for Hermes to read the wiki
- `SOUL-snippet.md` — System prompt additions
- `scripts/` — Sync scripts (bash + PowerShell + Python wrapper)
- `docker/` — Deployment snippets for Docker/Railway

The integration is read-only by design. Hermes can query the wiki but cannot modify it. All writes go through the local AI agent via `/ingest` and `/compile` workflows.
