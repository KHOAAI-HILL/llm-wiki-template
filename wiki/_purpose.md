---
title: "Wiki Purpose & Principles"
description: "Kim chỉ nam định hướng việc xây dựng và duy trì Second Brain"
status: canonical
tags: [meta, rule]
---

# 🎯 Mục Đích Của Second Brain (Wiki Purpose)

Second Brain này là một **Hệ Cơ Sở Tri Thức AI (AI Knowledge Base)** cá nhân, được thiết kế theo tư duy "LLM là người đọc chính, con người là người kiểm duyệt".

Nó không phải là một blog cá nhân, không phải là nơi lưu trữ ghi chú lộn xộn (scratchpad), mà là một **Bách Khoa Toàn Thư** được biên dịch tinh gọn từ dữ liệu thô (raw sources) nhằm phục vụ việc RAG (Retrieval-Augmented Generation) cho các AI Agent (như Hermes, OpenClaw).

## 🧭 Nguyên Tắc Cốt Lõi (Core Principles)

1. **Self-Contained (Độc lập)**: Một AI Agent khi đọc một bài viết bất kỳ phải hiểu được ngữ cảnh mà không cần suy đoán. Mọi khái niệm lạ phải được liên kết (`[[wikilink]]`).
2. **Attribution (Truy xuất nguồn gốc)**: Mọi thông tin, số liệu, quan điểm trong wiki đều phải chỉ rõ nguồn gốc (ví dụ: "Theo Karpathy...", "Theo bài viết X..."). **Luôn khai báo mảng `sources: []` trong frontmatter.**
3. **Thematic, Not Chronological**: Sắp xếp kiến thức theo chủ đề (Concepts, Tools, People), không theo dòng thời gian. Khi có thông tin mới về một khái niệm cũ, ta *cập nhật và hòa trộn* vào bài viết cũ thay vì tạo một bản ghi mới.
4. **Trọng Tâm & Tinh Gọn**: 
   - 1 ý = 1 câu. Tránh dùng từ ngữ thừa thãi (filler words).
   - Không dùng giọng văn cảm xúc ("thú vị là", "tuyệt vời"), chỉ dùng giọng văn trung lập.
5. **Classify Before Extract**: Không phải nguồn dữ liệu nào cũng xử lý giống nhau. Một bài tweet cần bóc tách khác với một bài nghiên cứu dài 50 trang.

## 🤖 Hướng Dẫn Dành Cho AI Agents

Nếu bạn là một AI Agent đang đọc file này:
- Bạn **KHÔNG ĐƯỢC** tự ý xóa thông tin có sẵn trong wiki. Bạn chỉ được phép bổ sung (refine & integrate).
- Nếu phát hiện thông tin mới **mâu thuẫn** với thông tin cũ trong cùng một chủ đề, bạn phải bảo lưu cả hai và đặt thẻ cảnh báo `> [!warning] Mâu Thuẫn Chưa Giải Quyết` để con người phân xử.
- Luôn kiểm tra file `_graph.json` để hiểu sự liên kết giữa các node trước khi đưa ra câu trả lời tổng hợp.
