---
description: Lưu kiến thức từ cuộc hội thoại hiện tại trực tiếp vào wiki — rút ngắn Filing-back Loop
---

# /save — Lưu Cuộc Hội Thoại Thành Wiki

Workflow này trích xuất kiến thức đắt giá từ cuộc hội thoại đang diễn ra và lưu thẳng vào vault. Khác với `/wrapup` (lưu session state), `/save` tập trung vào **knowledge extraction** — biến discussion thành bài wiki.

## Kích Hoạt

- `/save` hoặc `/save [tên-tùy-chọn]`
- "Lưu kiến thức này vào wiki"
- "File back vào brain"
- "Ghi nhớ phần thảo luận này"

## So Sánh Với /wrapup

| Tiêu chí | `/save` | `/wrapup` |
|-----------|---------|-----------|
| Mục đích | Lưu **kiến thức** (concepts, decisions, patterns) | Lưu **trạng thái phiên** (pending tasks, context) |
| Output | File raw + compile wiki (nếu đủ chất liệu) | Session summary log |
| Khi nào dùng | Giữa phiên, khi phát hiện insight đáng lưu | Cuối phiên, khi kết thúc làm việc |
| Tần suất | Bất cứ lúc nào | 1 lần cuối phiên |

## Bước Thực Hiện

### 1. Phân tích cuộc hội thoại

// turbo

Quét lại cuộc hội thoại hiện tại (hoặc phần được chỉ định). Tìm:
- **Concepts mới** — Khái niệm, pattern, kiến trúc được thảo luận mà wiki chưa có
- **Decisions + Reasoning** — Quyết định quan trọng kèm lý do (architecture decision records)
- **Discoveries** — Phát hiện kỹ thuật, bug patterns, workarounds
- **Tool evaluations** — Đánh giá công cụ/framework mới
- **Comparisons** — So sánh A vs B đã thảo luận chi tiết

### 2. Kiểm tra giá trị

Tự hỏi 3 câu trước khi lưu:
1. **Novelty:** Wiki đã có thông tin này chưa? (Đọc `wiki/index.md` kiểm tra)
2. **Durability:** Thông tin này còn đúng sau 6 tháng không? (Bỏ qua thông tin thời vụ)
3. **Substance:** Viết được ≥3 câu có ý nghĩa không? (Bỏ qua nếu quá mỏng)

Nếu không đạt cả 3 → báo cho người dùng: "Cuộc hội thoại này chưa có kiến thức đủ đắt để lưu riêng. Thông tin sẽ được ghi nhận trong `/wrapup`."

### 3. Tạo file raw

// turbo

Tạo file `raw/misc/conversation-[YYYY-MM-DD]-[tên].md` với frontmatter chuẩn:

```yaml
---
title: "[Tóm tắt chủ đề thảo luận]"
source: "conversation"
date_added: YYYY-MM-DD
tags: [conversation, save, chủ-đề]
aliases: []
status: draft
summary: "[Tóm tắt 1 câu]"
---
```

Nội dung: Trích xuất kiến thức ở dạng structured (đoạn văn, không phải transcript). Giữ lại quotes đắt giá từ cuộc trao đổi nếu có.

### 4. Auto-compile (nếu đủ chất liệu)

// turbo-all

Nếu kiến thức đủ dày (≥200 từ, concept rõ ràng):
1. Chạy pipeline compile nhanh:
   - Kiểm tra wiki article đã tồn tại chưa
   - Nếu đã có → integrate (tuân thủ Bước 4.5 Contradiction Check + Bước 5 Re-read)
   - Nếu chưa có → tạo bài mới theo Entity-Type Template
2. Cập nhật `wiki/index.md`, `absorb-log.json`

Nếu chưa đủ chất liệu:
- Chỉ lưu raw, báo cho người dùng chạy `/compile` sau khi có thêm nguồn.

### 5. Báo cáo kết quả

```
💾 Đã lưu kiến thức từ cuộc hội thoại!

📂 Raw: raw/misc/conversation-[date]-[name].md
📝 Wiki: [[bài-wiki-mới-hoặc-cập-nhật]] (nếu compile thành công)

🔍 Kiến thức đã trích xuất:
- [Concept/Decision/Pattern 1]
- [Concept/Decision/Pattern 2]

📊 Trạng thái: Đã compile vào wiki / Chỉ lưu raw (chờ compile)
```

### 6. Append Operations Log

// turbo
Append vào `wiki/_ops_log.md`:
```markdown
## [YYYY-MM-DD] save | [tên chủ đề] — [compile/raw-only]
```

## Quy Tắc

// turbo-all

- **Không lưu transcript thô** — Trích xuất kiến thức, không copy-paste hội thoại
- **Tuân thủ Compilation Rules** — Nếu auto-compile, áp dụng đầy đủ Re-read + Contradiction Check
- **Dual Output nếu cần** — Nếu `/save` tạo bài wiki mới, vẫn trả lời câu hỏi đang dở cho user
- **Idempotent** — Gọi `/save` 2 lần không tạo duplicate (kiểm tra tên file + nội dung)
