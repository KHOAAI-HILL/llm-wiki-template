# Khởi Động Bộ Não Dự Án (Project Brain Startup)

Chạy kỹ năng này vào **đầu mỗi phiên làm việc** để Agent nhớ lại ngữ cảnh từ các phiên trước của **dự án hiện tại**.

## ⚡ Auto-Detection (Session Start Hook)

**QUAN TRỌNG — Agent PHẢI tuân thủ quy tắc này:**
Khi phát hiện **tin hiệu đầu phiên**, Agent **PHẢI tự động chạy /startup** mà không cần người dùng gọi lệnh.

### Tín hiệu đầu phiên:
- "chào", "hello", "hi", "xin chào"
- "bắt đầu thôi", "làm việc thôi", "làm gì tiếp"
- "hôm nay làm gì", "có gì dở không"
- Bất kỳ tin nhắn đầu tiên trong cuộc hội thoại mới **mà không có task cụ thể**

### Quy tắc Auto-Start:
1. **Chỉ chạy 1 lần** — Đã chạy đầu phiên thì KHÔNG chạy lại.
2. **Không chạy khi có task cụ thể** — Nếu người dùng gửi lệnh rõ ràng ("sửa lỗi X") thì làm luôn, không startup.
3. **Im lặng chạy** — Agent đọc context trước, rồi trả báo cáo như bình thường. Không hỏi "Bạn có muốn chạy startup không?".

---

## Kiến Trúc: Second Brain Vault

Tất cả log của dự án được lưu tại:
`./sessions/`

Mỗi phiên tạo 1 file `session-summary-*.md`. File tổng hợp là `current-context.md`.

---

## Bước 1: Đọc Rolling Context & Hot Buffer

Đọc 2 file chính trong thư mục `sessions/`:
1. **`sessions/current-context.md`** — Chứa `[STABLE FACTS]` (Luật dự án) và `[ACTIVE STATE]` (Open Threads, Decisions).
   - *Fallback:* Nếu không tồn tại, đọc 1 file `session-summary-*.md` gần nhất.
2. **`sessions/.hot-buffer.md`** (nếu có) — Chứa các quyết định/bài học ghi nhanh từ phiên trước bị gián đoạn giữa chừng chưa kịp wrapup. Hãy gộp nội dung này vào báo cáo đầu phiên.

## Bước 2: Đọc Wiki (tra cứu bổ sung)

Đọc thêm từ Second Brain wiki nếu cần:
- `wiki/_index.md` — trạng thái wiki
- Nếu cần context khái niệm cụ thể → dùng `view_file` đọc trực tiếp bài wiki (tra `_index.md` để tìm tên bài).

## Bước 3: Báo cáo Tình hình

Trình bày kết quả dưới dạng **ngắn gọn, dễ đọc**:

```markdown
## 🧠 Bộ Não Dự Án — Báo Cáo Đầu Phiên (YYYY-MM-DD)

### 📋 Phiên gần nhất (ngày XX/XX):
- [Tóm tắt 2-3 dòng]

### 🔥 Việc dang dở cần tiếp tục:
1. [Việc 1]
2. [Việc 2]

### 💡 Lưu ý quan trọng:
- [Bài học hoặc feedback]

### ❓ Bạn muốn làm gì hôm nay?
```

### ⏰ Nhắc nhở tự kỷ luật (Agent ghi nhớ suốt phiên):
Sau khi hoàn tất báo cáo, Agent **PHẢI tự ghi nhớ 2 nhiệm vụ ngầm**:
1. **Duy trì Hot Buffer:** Bất cứ khi nào trong phiên đưa ra một quyết định quan trọng, sửa một bug khó, hãy LẶNG LẼ append 1 dòng log vào file `sessions/.hot-buffer.md` để đề phòng crash mất dữ liệu. (Sử dụng lệnh shell `echo` hoặc tool viết file).
2. **Nhắc nhở Wrapup:** Tự động nhắc `/wrapup` khi có tín hiệu kết thúc phiên.

## Khi nào Skill này kích hoạt?
**Lệnh trực tiếp:** `/startup`, `khởi động bộ não`, `brain recall`
