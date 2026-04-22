---
title: "Wiki Overview — Executive Summary"
source: "compiled"
date_added: 2026-04-23
tags: [meta, overview, executive-summary]
aliases: [overview, tổng quan wiki]
status: canonical
related:
  - "[[index]]"
summary: "Bản tóm tắt tổng quan vault cho agent cross-project — đọc 1 file hiểu toàn bộ wiki."
---

## Vault Này Là Gì

Second Brain là **AI-managed knowledge base** theo phương pháp Karpathy LLM Wiki Pattern. LLM viết và duy trì toàn bộ nội dung wiki. Con người nạp dữ liệu thô, đặt câu hỏi, và duyệt kết quả.

## Domain Kiến Thức

Vault tập trung vào các lĩnh vực chính:

1. **[Domain 1]** — [Mô tả ngắn gọn về domain 1]
2. **[Domain 2]** — [Mô tả ngắn gọn về domain 2]
3. **[Domain 3]** — [Mô tả ngắn gọn về domain 3]

## Quy Mô Hiện Tại

- **[X] bài wiki** ([X] concepts, [X] tools, [X] people, [X] comparisons)
- **[X] thuật ngữ** trong glossary
- **[X] raw sources** đã biên dịch
- **Ngôn ngữ:** [Ngôn ngữ chính] (nội dung), [Ngôn ngữ phụ] (thuật ngữ kỹ thuật)

## Cách Truy Cập

- **Từ bất kỳ workspace:** Dùng `/brain lookup [chủ đề]` hoặc `/brain ask [câu hỏi]`
- **Tra cứu nhanh:** Đọc `wiki/_index.md` (danh sách đầy đủ) hoặc `wiki/_glossary.md` (thuật ngữ)
- **Nạp dữ liệu mới:** `/brain ingest [URL]` từ bất kỳ dự án nào
- **Nghiên cứu tự động:** `/brain research [chủ đề]` — agent tự tìm kiếm web và nạp

## Bài Viết Trọng Tâm

Các bài wiki có nhiều backlinks nhất (central nodes trong knowledge graph):

- [[bài-viết-1]] — [Mô tả ngắn]
- [[bài-viết-2]] — [Mô tả ngắn]
- [[bài-viết-3]] — [Mô tả ngắn]

## Quy Trình Vận Hành

```
Nạp dữ liệu → /ingest → raw/
Biên dịch    → /compile → wiki/ (có Contradiction Check)
Hỏi đáp      → /ask → trả lời từ wiki
Nghiên cứu   → /autoresearch → search web → raw/ → wiki/
Lưu nhanh    → /save → conversation → raw/ → wiki/
Dọn dẹp      → /cleanup → audit chất lượng wiki
```
