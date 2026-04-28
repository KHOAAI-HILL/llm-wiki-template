---
description: Biên dịch dữ liệu thô (raw/) thành bài wiki có cấu trúc (wiki/)
---

# /compile — Biên Dịch Wiki Từ Dữ Liệu Thô

Workflow này đọc tài liệu trong `raw/`, phân tích khái niệm, và tạo/cập nhật bài wiki tương ứng.

## Kích Hoạt

- `/compile` hoặc `/bien-dich`
- "Biên dịch bài mới vào wiki"
- "Compile raw vào wiki"
- "Cập nhật wiki từ raw/"

## Bước Thực Hiện

### 1. Đọc trạng thái hiện tại

// turbo
Đọc `wiki/_index.md` để biết wiki đang có những bài nào.

### 2. Quét raw/ — dùng Absorption Log

// turbo
Đọc `wiki/_absorb_log.json` để biết file raw nào đã compile và lưu hash của chúng.
Tính mã SHA256 cho từng file thực tế trong `raw/`. So sánh hash thực tế với hash lưu trong `_absorb_log.json`.
Liệt kê các file raw/ **chưa có** trong log, hoặc có hash **khác** với hash đã lưu (nghĩa là file raw đã bị cập nhật).

Nếu không có file mới → báo "Wiki đã cập nhật, không có dữ liệu mới."

### 3. Classify nguồn (Classify-Before-Extract)

Cho mỗi tài liệu raw/ chưa biên dịch, **phân loại trước**:

| Source Type | Nhận dạng | Extraction Strategy |
|-------------|----------|--------------------|
| Tweet/Thread | `raw/tweets/` | Extract assertions chính + notable replies |
| Article/Gist | `raw/articles/` | Extract theo sections, thesis + arguments |
| Paper/Report | `raw/papers/` | Extract abstract → findings → implications |
| Diagram/Image | `raw/misc/` + ảnh | Bóc tách layers, components, flows |
| Video/Transcript | `raw/videos/` | Tìm key moments, quotes, bỏ filler |
| Repo/Code | `raw/repos/` | Extract architecture, patterns, API surface |

### 4. Phân tích nội dung theo strategy

Cho mỗi tài liệu (đã classify):

1. **Đọc toàn bộ nội dung**
2. **Xác định các thực thể:**
   - **Concepts** (khái niệm) → `wiki/concepts/`
   - **Tools** (công cụ, sản phẩm) → `wiki/tools/`
   - **People** (nhân vật đáng chú ý) → `wiki/people/`
   - **Comparisons** (so sánh A vs B) → `wiki/comparisons/`

3. **Cho mỗi thực thể — áp dụng Concrete Noun Test:**
   - "X là một ___" — chỉ tạo bài cho thực thể cụ thể, có đủ chất liệu
   - Kiểm tra wiki article đã tồn tại chưa
   - Nếu **chưa có** VÀ viết được ≥3 câu có ý nghĩa → Tạo bài mới (dùng Entity-Type Template từ AGENTS.md)
   - Nếu **chưa có** VÀ chưa đủ chất liệu → Ghi nhận, chờ raw mới
   - Nếu **đã có** → Chuyển sang bước 4.5

### 4.5. Contradiction Check (TRƯỚC KHI cập nhật)

Khi bài wiki **đã tồn tại** và raw mới chứa thông tin về cùng chủ đề:

1. **Extract claims** từ raw mới — liệt kê các khẳng định cụ thể (số liệu, quy trình, attribute).
2. **So sánh với wiki hiện có** — đọc bài wiki, tìm claims tương ứng.
3. **Phân loại khác biệt:**
   - **Temporal update** (phiên bản mới, ngày mới) → Không phải mâu thuẫn. Cập nhật bình thường ở Bước 5.
   - **Bổ sung** (wiki chưa có thông tin này) → Không phải mâu thuẫn. Integrate ở Bước 5.
   - **Mâu thuẫn thật** (cùng attribute, khác giá trị, cùng thời điểm) → Tiếp bước 4.
4. **Xử lý mâu thuẫn:**
   - **KHÔNG ghi đè** claim cũ
   - Thêm callout Obsidian ngay dưới đoạn liên quan trong bài wiki:
     ```markdown
     > [!warning] Mâu Thuẫn Chưa Giải Quyết
     > **Claim mới:** [nội dung] (Nguồn: [[raw/path]])
     > **Claim cũ:** [nội dung] (Nguồn: [[raw/path]])
     > **Cần review:** [gợi ý cách xác minh]
     ```
   - Đổi frontmatter `status:` thành `needs-review`
   - Ghi nhận vào danh sách contradictions cho báo cáo (Bước 12)

### 5. Re-read — TRƯỚC KHI cập nhật bài wiki (NON-NEGOTIABLE)

**Quy trình bắt buộc cho MỌI bài wiki cần cập nhật:**

1. **Đọc lại toàn bộ bài wiki** — không chỉ frontmatter, đọc HẾT nội dung
2. **Tự hỏi:** "Entry mới bổ sung chiều sâu gì mà bài chưa có?"
   - Nếu câu trả lời là "không gì mới" → **KHÔNG sửa bài**
   - Nếu có insight mới → tiếp tục
3. **Integrate** nội dung mới vào mạch viết hiện có:
   - KHÔNG chỉ append bullet point ở cuối
   - Tìm đúng section phù hợp, viết thêm đoạn văn hoặc bổ sung vào đoạn hiện có
   - Bài phải đọc lại mạch lạc như một bài viết thống nhất
4. **Kiểm tra Article Size Guardrails:**
   - Bài > 120 dòng? → Xem xét tách sub-topic thành bài con (Anti-Cramming)
   - Sub-topic xuất hiện ≥3 đoạn? → Tách thành bài riêng
   - Bài < 15 dòng? → Tag `status: stub`, ưu tiên bổ sung

### 6. Viết bài wiki mới (nếu có)

Dùng **Entity-Type Template** phù hợp (xem AGENTS.md → Entity-Type Templates):

Mỗi bài wiki phải tuân thủ:

```yaml
---
title: "Tên bài"
sources: ["[[raw/file-1.md]]", "[[raw/file-2.md]]"]
date_added: YYYY-MM-DD
tags: [loại, chủ đề]
status: draft
related:
  - "[[bài-liên-quan-1]]"
  - "[[bài-liên-quan-2]]"
summary: "Tóm tắt 1 dòng cho _index.md"
---
```

**Quy tắc nội dung:**
- Tối thiểu 200 từ cho concept articles
- Sử dụng `[[wikilinks]]` cho internal links
- Dùng tiếng Việt cho nội dung, tiếng Anh cho thuật ngữ kỹ thuật
- Headers bắt đầu từ `##` (h2), vì h1 = title trong frontmatter
- Mỗi bài phải link đến ≥2 bài wiki khác
- Self-contained: đọc một bài phải hiểu được, không phụ thuộc bài khác

**Quy tắc giọng văn (Bách Khoa Toàn Thư):**
- Viết giọng trung lập, dẫn chứng cụ thể. Không phải blog.
- 1 ý = 1 câu. Câu ngắn. Viết đoạn văn thay vì bullet-point (trừ khi liệt kê).
- Attribution thay vì assertion: "Karpathy mô tả..." thay vì "Nó rất..."
- Cảm xúc truyền qua direct quotes từ raw source, không qua lời viết.

### 7. Cập nhật backlinks

Kiểm tra toàn bộ bài wiki hiện có. Nếu bài mới đề cập đến bài cũ, thêm backlink vào phần `related:` của bài cũ.

### 8. Cập nhật _index.md

// turbo
Thêm entry cho mỗi bài wiki mới vào `wiki/_index.md`:
- Đúng section (Concepts / Tools / People / Comparisons)
- Cập nhật tổng số bài
- Cập nhật ngày cập nhật
- Thêm source mới vào bảng Raw Sources

### 9. Cập nhật _glossary.md

Nếu phát hiện thuật ngữ mới quan trọng → thêm vào `wiki/_glossary.md` theo format:
```markdown
## Term Name
**Tiếng Việt:** Bản dịch
**Định nghĩa:** Giải thích ngắn gọn
**Xem thêm:** [[related-article]]
```

### 10. Cập nhật Absorption Log

// turbo
Thêm entry mới vào `wiki/_absorb_log.json`:
```json
{
  "raw/[thư-mục]/[tên-file].md": {
    "hash": "[sha256_hash_của_file]",
    "absorbed_at": "YYYY-MM-DD",
    "wiki_articles": ["article-1", "article-2"]
  }
}
```
Cập nhật field `last_updated` ở root.

### 11. Append Operations Log

// turbo
Append vào `wiki/_ops_log.md`:
```markdown
## [YYYY-MM-DD] compile | [X] bài mới, [Y] cập nhật từ [tên raw source]
```

### 12. Báo cáo kết quả

```
📚 Biên dịch hoàn tất từ [X] tài liệu raw/

### Bài wiki mới:
- [[concept-1]] — tóm tắt
- [[tool-1]] — tóm tắt

### Bài wiki đã cập nhật:
- [[existing-article]] — thêm [nội dung gì]

### Bài KHÔNG cập nhật (không có gì mới):
- [[article]] — lý do skip

### ⚠️ Mâu thuẫn phát hiện:
- [[bài-wiki]] — [claim mới] vs [claim cũ] — cần review

### Thuật ngữ mới:
- Term 1, Term 2

### Thống kê:
- Tổng bài wiki: [N]
- Tổng thuật ngữ: [N]
- Contradictions: [C]
- Raw đã compile: [M]/[Total raw files]
```

### 12.5. Rebuild Knowledge Graph

// turbo
Sau khi compile và cập nhật mọi metadata, tự động chạy script tạo đồ thị tri thức:
```bash
python wiki/_build_graph.py
```
Log kết quả: "Graph rebuilt: X nodes, Y edges, Z isolated."

## Quy Tắc Biên Dịch Quan Trọng

1. **KHÔNG BAO GIỜ sửa raw/** — chỉ đọc
2. **KHÔNG xóa nội dung cũ** trong wiki — chỉ refine và integrate
3. **1 concept = 1 file** — không gộp nhiều khái niệm vào 1 bài
4. **Liên kết chéo** — mỗi bài mới phải link đến ≥2 bài hiện có
5. **Nguồn minh bạch** — luôn ghi rõ dữ liệu đến từ raw/ nào
6. **Tiếng Việt & English** — Nội dung tiếng Việt, thuật ngữ kỹ thuật giữ nguyên tiếng Anh
7. **RE-READ trước khi update** — Đọc lại toàn bộ bài trước khi sửa bất kỳ dòng nào
8. **Integrate, không append** — Tích hợp vào mạch viết, không đổ thêm ở cuối

## Xử Lý Lỗi

| Tình huống | Cách xử lý |
|-----------|------------|
| Không rõ concept thuộc category nào | Hỏi người dùng |
| Tài liệu quá ngắn (< 100 từ) | Tạo bài ngắn + tag `status: stub` |
| Trùng nội dung với bài có sẵn | Merge vào bài cũ, không tạo bài mới |
| Bài wiki > 120 dòng sau update | Xem xét tách sub-topic thành bài con |
| `_absorb_log.json` bị hỏng | Rebuild từ `_index.md` Raw Sources table |
