---
description: Hỏi đáp trực tiếp trên vault Second Brain — không cần NotebookLM
---

# /ask — Hỏi Đáp Trên Vault

Workflow này cho phép người dùng hỏi bất kỳ câu hỏi nào về kiến thức trong vault Second Brain. Agent đọc trực tiếp các file `.md` để trả lời, không phụ thuộc NotebookLM.

## Kích Hoạt

- `/ask [câu hỏi]` hoặc `/hoi [câu hỏi]`
- "Hỏi Second Brain về [chủ đề]"
- "Tìm kiếm trong wiki về [khái niệm]"
- "Knowledge base nói gì về [chủ đề]?"

## Bước Thực Hiện

### 1. Phân tích câu hỏi

Xác định:
- **Chủ đề chính** — concept, tool, person, hay comparison?
- **Mức độ chi tiết** — tóm tắt nhanh hay phân tích sâu?
- **Phạm vi** — chỉ wiki, hay bao gồm cả raw/?

### 2. Tìm kiếm kiến thức (3 nguồn)

// turbo-all

#### 2a. Đọc Index + Backlinks (ưu tiên cao nhất)
1. Đọc `wiki/_index.md` — scan tên bài + tóm tắt
2. Đọc `wiki/_backlinks.json` — tìm bài có nhiều backlinks liên quan đến câu hỏi (high backlink count = central topic)
3. **Match qua aliases:** Đọc frontmatter `aliases:` của bài tiềm năng. Ví dụ: câu hỏi "RAG" → match `retrieval-augmented-generation.md` (alias: RAG)

#### 2b. Đọc bài wiki liên quan
1. Đọc 3-8 bài wiki tìm được ở bước 2a
2. Theo dõi `[[wikilinks]]` và `related:` sâu 2-3 tầng nếu cần
3. Đọc `wiki/_glossary.md` nếu câu hỏi liên quan đến định nghĩa thuật ngữ

#### 2c. Tìm trong Raw & Sessions (nếu wiki chưa đủ)
- Dùng `grep_search` tìm trong `raw/` để bổ sung thông tin chưa được biên dịch
- Đọc `sessions/` nếu câu hỏi liên quan đến lịch sử làm việc

### 3. Tổng hợp câu trả lời

**Quy tắc trả lời:**
- Lead với câu trả lời trực tiếp, không vòng vo
- Trích dẫn tên bài wiki bằng `[[wikilinks]]`
- Dùng direct quotes từ wiki/raw một cách tiết chế (chỉ khi câu quote thật đắt giá)
- Kết nối các ý từ nhiều bài — đây là giá trị chính của wiki
- Thừa nhận lỗ hổng nếu wiki chưa cover đủ
- Nếu thông tin chưa có trong vault → nói rõ và đề xuất `/ingest`
- Nếu thông tin chỉ có trong raw/ (chưa compile) → đề xuất `/compile`

Format trả lời:

```markdown
## 🧠 Trả lời: [câu hỏi tóm tắt]

[Nội dung trả lời, tổng hợp từ các bài wiki]

### 📎 Nguồn tham khảo:
- [[wiki-article-1]] — mô tả ngắn
- [[wiki-article-2]] — mô tả ngắn
```

### 4. Đánh giá File-back (Dual Output Rule)

Sau khi trả lời, đánh giá câu trả lời:

**Tiêu chí file-back** — câu trả lời nên được file back nếu:
- Tổng hợp (synthesis) từ ≥3 bài wiki thành insight mới
- Tạo ra so sánh có cấu trúc (bảng, phân tích) chưa có trong wiki
- Phát hiện connection/contradiction mới giữa các bài
- Người dùng hỏi chủ đề mà wiki chưa cover → câu trả lời dùng kiến thức chung có giá trị

**Nếu đủ tiêu chí → hỏi user:**
```
💡 Câu trả lời này chứa synthesis có giá trị. Bạn muốn file back vào wiki không?
   1. Tạo bài mới trong outputs/summaries/ (giữ nguyên dạng Q&A)
   2. Integrate vào bài wiki liên quan (cập nhật bài hiện có)
   3. Không, bỏ qua
```

**Nếu user chọn 1:** Tạo file `outputs/summaries/[chủ-đề]-[YYYY-MM-DD].md` với frontmatter chuẩn.
**Nếu user chọn 2:** Chạy quy trình update wiki (re-read → integrate → update index).
**Nếu không đủ tiêu chí:** Bỏ qua, không hỏi.

### 5. Gợi ý hành động tiếp theo (tùy ngữ cảnh)

- "💡 Chủ đề này chưa có trong wiki. Muốn tôi `/ingest` và `/compile` không?"
- "📝 Bài wiki [[X]] có thể cần cập nhật thêm thông tin này."
- "🔗 Có 3 bài wiki liên quan — muốn tôi tổng hợp thành report không?"

### 6. Append Operations Log

// turbo
Append vào `wiki/_ops_log.md`:
```markdown
## [YYYY-MM-DD] ask | [câu hỏi tóm tắt]
```
Nếu có file-back, thêm dòng tiếp:
```markdown
## [YYYY-MM-DD] file-back | [tên bài tạo/cập nhật]
```

## Quy Tắc

// turbo-all

- **Không đọc raw entries khi đã có wiki** — Wiki là knowledge base, raw là source of truth
- **Không đoán** — Nếu wiki không cover, nói rõ
- **Không đọc toàn bộ wiki** — Dùng index + backlinks + aliases để surgical
- **Không sửa wiki trong bước trả lời** — Query là read-only. Chỉ sửa nếu user chấp nhận file-back ở bước 4
- Tất cả bước tìm kiếm và đọc file: tự động chạy

## Xử Lý Đặc Biệt

### Câu hỏi tổng quan
- "Wiki đang có gì?" → Đọc `_index.md` và trình bày tổng quan
- "Có bao nhiêu bài wiki?" → Đếm từ `_index.md`

### Câu hỏi so sánh
- "A khác gì B?" → Tìm cả 2 bài wiki, tổng hợp so sánh
- Nếu chưa có bài comparison → đề xuất tạo mới trong `wiki/comparisons/`

### Câu hỏi về lịch sử
- "Phiên trước làm gì?" → Đọc session logs trong `sessions/`
- "Đã ingest bài nào?" → Đọc bảng Raw Sources trong `_index.md`

## Xử Lý Lỗi

| Tình huống | Cách xử lý |
|-----------|------------|
| Không tìm thấy thông tin | Nói rõ, đề xuất `/ingest` nguồn mới |
| Wiki chưa biên dịch raw/ mới | Đề xuất `/compile` |
| Câu hỏi ngoài phạm vi vault | Trả lời từ kiến thức chung + đề xuất nạp tài liệu |
| `_backlinks.json` cũ hoặc thiếu | Chạy `python wiki/_build_backlinks.py` rồi thử lại |

