# Research Program — Cấu Hình Nghiên Cứu

Workflow `/autoresearch` sẽ đọc file này trước mỗi phiên để xác định mục tiêu, giới hạn và quy tắc đánh giá nguồn. Cập nhật file này để phù hợp với lĩnh vực (domain) của bạn.

---

## 🎯 Mục Tiêu Tìm Kiếm

- **Nguồn ưu tiên:** Tài liệu chính thức (official docs), bài viết từ tác giả gốc, báo cáo học thuật, bài viết phân tích chuyên sâu.
- **Dữ liệu cần trích xuất:** Concepts cốt lõi, công cụ/frameworks, nhân vật quan trọng, và các giới hạn/nhược điểm.
- **Tiêu chí:** Luôn ghi nhận mâu thuẫn giữa các nguồn. Ưu tiên nguồn xuất bản trong vòng 2 năm gần nhất (trừ khi là kiến thức nền tảng).

---

## ⚖️ Confidence Scoring (Đánh Giá Độ Tin Cậy)

Khi nạp dữ liệu vào `raw/`, agent phải gán tag `confidence:` vào frontmatter:

- **`high`**: Nhiều nguồn uy tín độc lập đồng thuận, tài liệu chính thức, hoặc nghiên cứu peer-reviewed.
- **`medium`**: Một nguồn phân tích tốt, hoặc nhiều nguồn đồng thuận nhưng thiếu số liệu gốc.
- **`low`**: Ý kiến cá nhân (forum, mạng xã hội), bài viết tổng hợp sơ sài, hoặc claim chưa được kiểm chứng.

*Lưu ý: Đánh dấu các thông tin từ nguồn cũ (>3 năm) là có khả năng lỗi thời.*

---

## 🛑 Giới Hạn Vòng Lặp

- **Max vòng search mỗi phiên:** 3 vòng
- **Max nguồn fetch mỗi vòng:** 5 URLs
- Nếu đạt giới hạn mà vẫn chưa trả lời hết câu hỏi, ghi nhận phần thiếu vào phần "Câu Hỏi Mở" trong báo cáo.

---

## 🚫 Nguồn Cấm / Loại Trừ

- Không dùng diễn đàn (Reddit, Quora) làm nguồn xác thực (chỉ dùng để tìm link đến primary sources).
- Bỏ qua các trang nội dung SEO rác, spam.
- Không trích dẫn nguồn từ bài báo không rõ ngày tháng xuất bản.

---

## 🏷️ Domain Notes (Hướng Dẫn Theo Lĩnh Vực)

*(Sửa phần này theo dự án hiện tại của bạn)*

**Software Engineering / AI:**
- Ưu tiên: arXiv, GitHub repos chính thức (đọc README), HackerNews (chỉ lấy top comments), tài liệu từ các lab AI lớn (OpenAI, Anthropic, DeepMind).
- Thận trọng: Các bài benchmark trên mạng xã hội thường có bias. Cần xác minh chéo.

**Business / Startup:**
- Ưu tiên: Y Combinator essays, báo cáo tài chính (SEC filings), Paul Graham essays, Lenny's Newsletter.
- Thận trọng: Thông cáo báo chí (Press Releases) thường mang tính PR, đánh giá `low` confidence nếu không có số liệu độc lập.
