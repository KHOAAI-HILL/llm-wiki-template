---
description: Tự động chạy vòng lặp nghiên cứu, tìm kiếm nguồn từ web, đánh giá, nạp vào raw/ và tổng hợp báo cáo.
---

# /autoresearch — Nghiên Cứu Tự Động

Workflow này biến Second Brain thành cỗ máy tìm kiếm chủ động. Trình bày một chủ đề, agent sẽ tự search web, đánh giá nguồn, nạp vào vault và tổng hợp kiến thức.

## Kích Hoạt

- `/autoresearch [chủ đề]`
- "Nghiên cứu sâu về [chủ đề]"
- "Tìm hiểu về [chủ đề] và nạp vào wiki"

## Bước Thực Hiện

### Bước 0: Đọc Cấu Hình Nghiên Cứu

// turbo
1. Đọc file `raw/_research_program.md` để lấy tiêu chí nguồn ưu tiên, giới hạn vòng lặp, và domain constraints.
2. Nếu file không tồn tại, sử dụng cấu hình mặc định: ưu tiên docs chính thức, max 3 rounds, max 5 URLs/round.

### Bước 1: Scan Knowledge Gap

// turbo
1. Đọc `wiki/_index.md` tìm các bài đã có về chủ đề.
2. Đọc 1-2 bài wiki liên quan nhất để xác định những gì wiki **đã biết**.
3. Xác định "Knowledge Gaps" — những khía cạnh wiki chưa có.

### Bước 2: Research Loop (Max 3 vòng)

// turbo-all

**Vòng 1: Broad Search (Tìm diện rộng)**
1. Phân tách chủ đề thành 3-5 keywords/angles khác nhau.
2. Dùng `search_web` tìm kiếm từng angle.
3. Đánh giá kết quả: Chọn ra 3-5 URLs tốt nhất dựa theo Relevance, Authority, Recency (dựa trên program config).
4. Fetch URLs bằng Defuddle (hoặc `read_url_content` nếu thất bại).

**Vòng 2: Gap Fill (Lấp lỗ hổng)**
1. Tổng hợp dữ liệu từ Vòng 1.
2. Xác định những khía cạnh còn thiếu (gaps) hoặc mâu thuẫn (contradictions).
3. Dùng `search_web` tìm kiếm mục tiêu (targeted search) cho các gaps này (max 5 queries).
4. Fetch 1-3 URLs tốt nhất.

**Vòng 3: Verification (Xác minh - Tùy chọn)**
1. Nếu phát hiện mâu thuẫn lớn giữa các nguồn, thực hiện tìm kiếm xác minh lần cuối.

### Bước 3: Auto-Ingest

// turbo-all

Với mỗi source fetch thành công và có giá trị, tạo file trong `raw/articles/` (hoặc thư mục phù hợp):
- **Frontmatter bắt buộc**:
  ```yaml
  ---
  title: "[Tiêu đề bài viết]"
  source: "[URL]"
  date_added: [YYYY-MM-DD]
  tags: [autoresearch, chủ đề]
  aliases: []
  status: draft
  summary: "[Tóm tắt 1 câu]"
  confidence: [high/medium/low]
  ---
  ```
- **Nội dung**: Giữ nguyên nội dung đã fetch (clean markdown).
- Cập nhật log: Thêm 1 dòng vào `wiki/_ops_log.md` cho mỗi file nạp thành công (hành động `ingest`).

### Bước 4: Tạo Synthesis Report

// turbo

Tạo file báo cáo tổng hợp tại `outputs/reports/research-[kebab-case-topic]-[YYYY-MM-DD].md` theo cấu trúc sau:

```markdown
---
title: "Research: [Chủ đề]"
source: "autoresearch"
date_added: [YYYY-MM-DD]
tags: [research, autoresearch]
status: draft
related: []
summary: "Báo cáo nghiên cứu tự động về [chủ đề]"
---

## Bối Cảnh
Mục tiêu nghiên cứu và các khoảng trống kiến thức ban đầu.

## Phát Hiện Chính
- [Phát hiện 1] (Nguồn: [[tên-file-raw]])
- [Phát hiện 2] (Nguồn: [[tên-file-raw]])

## Thực Thể & Khái Niệm Mới
- **Concept:** [Định nghĩa ngắn]
- **Tool/Person:** [Vai trò]

## Mâu Thuẫn (nếu có)
- Nguồn A nói X nhưng Nguồn B nói Y. (Kèm đánh giá confidence)

## Câu Hỏi Mở
Những vấn đề chưa được giải đáp trong giới hạn nghiên cứu.

## Nguồn Đã Nạp
- [[tên-file-raw-1]]
- [[tên-file-raw-2]]
```

### Bước 5: Báo Cáo & Chờ Duyệt

In ra màn hình kết quả cho người dùng:

```
🔬 Nghiên cứu hoàn tất: [Topic]

📊 Kết quả:
- Vòng search: N | Nguồn đã nạp: M
- Báo cáo: outputs/reports/research-[topic]-[date].md

🔥 Phát hiện chính:
1. [Finding 1]
2. [Finding 2]

❓ Bạn muốn:
1. Chạy `/compile` để biên dịch nguồn mới vào wiki ngay
2. Tôi mở báo cáo để bạn review trước
3. Dừng ở đây (giữ nguyên trong raw/)
```

### Bước 6: Append Operations Log

// turbo
Append vào `wiki/_ops_log.md`:
```markdown
## [YYYY-MM-DD] autoresearch | [topic] — [N] vòng, [M] nguồn nạp
```
