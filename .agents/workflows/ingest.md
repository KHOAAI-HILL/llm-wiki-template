---
description: Nạp dữ liệu mới vào Second Brain — lưu vào raw/ với frontmatter chuẩn
---

# /ingest — Nạp Dữ Liệu Vào Second Brain

Workflow này nạp dữ liệu mới vào vault. Hỗ trợ 2 chế độ: **Agent-assisted** (URL/content) và **Script batch** (file/folder local).

## Kích Hoạt

- `/ingest` hoặc `/nap`
- "Thêm bài này vào Second Brain"
- "Lưu URL này vào raw/"
- "Nạp paper này vào KB"
- Người dùng paste URL hoặc nội dung khi đang ở workspace `Second-brain`

## Chế Độ 1: Agent-Assisted (URL / Content)

Khi người dùng cung cấp URL hoặc paste nội dung trực tiếp.

### 1. Xác định loại nguồn

Hỏi nếu chưa rõ, hoặc tự phát hiện:

| Input | Thư mục đích | Cách xử lý |
|-------|-------------|------------|
| URL bài viết web | `raw/articles/` | Dùng `read_url_content` hoặc Firecrawl để extract |
| URL YouTube | `raw/videos/` | Extract transcript (nếu có) + metadata |
| File PDF | `raw/papers/` | Copy vào thư mục, tạo notes file kèm theo |
| Link X/Twitter thread | `raw/tweets/` | Extract toàn bộ thread + replies nổi bật |
| GitHub repo | `raw/repos/` | Clone/đọc README + structure summary |
| Text thuần | `raw/misc/` | Lưu trực tiếp dưới dạng .md |
| Ảnh/CSV/data | `raw/misc/` | Copy vào thư mục |

### 2. Tạo file markdown với frontmatter chuẩn

```yaml
---
title: "[Tiêu đề mô tả nội dung]"
source: "[URL hoặc đường dẫn gốc]"
date_added: YYYY-MM-DD
tags: [loại nguồn, chủ đề chính]
aliases: []
status: draft
summary: "Tóm tắt 1 dòng"
---
```

### 3. Đặt tên file

- Format: `kebab-case.md`
- Mô tả rõ nội dung: `karpathy-llm-knowledge-bases.md`, không phải `article-1.md`
- Nếu là bài đã có tên: dùng tên gốc (slugified)

### 4. Download ảnh liên quan (nếu có)

- Lưu ảnh cùng thư mục với file .md
- Tên ảnh: `[tên-bài]-img-01.png`, `[tên-bài]-img-02.png`
- Cập nhật link trong markdown để trỏ về ảnh local

### 5. Xác nhận

```
✅ Đã nạp: [tên file]
📂 Lưu tại: raw/[thư mục]/[tên file].md
📊 Kích thước: [X] từ
🏷️ Tags: [danh sách tags]

💡 Chạy /compile để biên dịch vào wiki.
```

### 6. Append Operations Log

// turbo
Append vào `wiki/_ops_log.md`:
```markdown
## [YYYY-MM-DD] ingest | [tên file / tiêu đề nguồn]
```

## Chế Độ 2: Script Batch (File / Folder Local)

Khi người dùng có file hoặc folder trên máy cần nạp hàng loạt.

### Sử dụng script `raw/_ingest.py`

```bash
# Ingest 1 file
python raw/_ingest.py path/to/file.md

# Ingest PDF
python raw/_ingest.py path/to/paper.pdf

# Ingest CSV/data
python raw/_ingest.py data.csv --type data

# Batch ingest folder (Obsidian vault, Notion export)
python raw/_ingest.py ~/Downloads/my-vault/

# Force loại nguồn
python raw/_ingest.py export.json --type tweets

# Preview trước (không tạo file)
python raw/_ingest.py big-folder/ --dry-run
```

### Formats hỗ trợ

| Format | Extension | Parser |
|--------|-----------|--------|
| Markdown | `.md` | Giữ nguyên nội dung, thêm frontmatter chuẩn |
| Plain text | `.txt` | Chuyển thành .md với frontmatter |
| HTML | `.html`, `.htm` | Strip tags, giữ text |
| PDF | `.pdf` | Extract text (cần `pip install PyMuPDF`) |
| JSON | `.json` | Day One journal, hoặc generic array/object |
| CSV/TSV | `.csv`, `.tsv` | Mỗi row → 1 entry, hoặc gộp thành bảng |
| Email | `.eml` | Extract subject, from, to, body |
| Folder | (directory) | Batch scan tất cả file supported |

### Auto-detect

Script tự phát hiện loại nguồn từ tên file và extension:
- `*tweet*`, `*twitter*` → `raw/tweets/`
- `*paper*`, `*arxiv*`, `*.pdf` → `raw/papers/`
- `*repo*`, `*github*` → `raw/repos/`
- `*video*`, `*youtube*` → `raw/videos/`
- Mặc định → `raw/articles/`

Dùng `--type` để override nếu auto-detect sai.

## Quy Tắc Chung

// turbo-all

**Tự động chạy:** Tất cả các bước đọc URL, tạo file, download ảnh, chạy script
**Chờ xác nhận:** Chỉ khi không rõ loại nguồn hoặc thư mục đích

### Quy tắc nội dung
- **KHÔNG sửa nội dung gốc** — Giữ nguyên 100% nội dung source
- **Frontmatter bắt buộc** — Mọi file raw phải có YAML frontmatter chuẩn
- **Tên file mô tả** — Đọc tên file phải hiểu nội dung, không dùng `article-1.md`
- **Idempotent** — Chạy script 2 lần không tạo duplicate (check tên file)

## Xử Lý Đặc Biệt

### URL bài viết web
1. Dùng `read_url_content` để lấy markdown
2. Clean up: bỏ navigation, footer, ads
3. Giữ lại: nội dung chính, ảnh, code blocks, headings

### YouTube
1. Extract video ID từ URL
2. Tìm transcript (API hoặc web scraping)
3. Tạo file với: title, channel, transcript, key timestamps

### X/Twitter thread
1. Extract toàn bộ tweets trong thread
2. Bao gồm replies nổi bật (verified accounts, high engagement)
3. Giữ nguyên metrics (likes, retweets, views)

### PDF
1. Script tự extract text nếu có PyMuPDF
2. Nếu chưa cài: tạo placeholder, hướng dẫn `pip install PyMuPDF`
3. Ảnh/bảng trong PDF không extract được → note trong file

## Xử Lý Lỗi

| Tình huống | Cách xử lý |
|-----------|------------|
| Format không nhận diện | Hỏi người dùng hoặc lưu vào `raw/misc/` |
| File quá lớn (>1MB text) | Cảnh báo, đề xuất chia nhỏ |
| PDF cần PyMuPDF | Tạo placeholder + hướng dẫn cài |
| Duplicate file name | Thêm `-2`, `-3` suffix tự động |
| URL không truy cập được | Báo lỗi, đề xuất paste nội dung thủ công |
