# Tổng Kết Phiên (Project Wrapup)

Chạy kỹ năng này vào cuối mỗi phiên để lưu session log vào **Second Brain vault**.

Tất cả log của dự án được ghi vào:
`./sessions/`

## ⚡ Tự Động Nhắc Nhở Cuối Phiên (AUTO-REMIND)

**QUAN TRỌNG — Agent PHẢI tuân thủ quy tắc này:**
Khi phát hiện tín hiệu kết thúc phiên, Agent **PHẢI chủ động hỏi**:
> 🧠 *"Có vẻ bạn sắp kết thúc phiên. Bạn có muốn tôi chạy `/wrapup` để lưu lại mọi thứ vào Second Brain trước khi nghỉ không?"*

### Tín hiệu kết thúc phiên:
- "thôi nhé", "xong rồi", "hết việc rồi", "nghỉ thôi"
- "tắt máy", "đi ngủ", "mai làm tiếp", "lát nữa làm tiếp"
- "cảm ơn nha", "ok cảm ơn", "bye", "tạm biệt"

### Quy tắc nhắc nhở:
1. **Chỉ nhắc 1 lần** — Nếu từ chối, KHÔNG nhắc lại.
2. **Không nhắc khi phiên quá ngắn** — 1-2 câu hỏi đơn giản không cần wrapup.
3. **Tự động chạy nếu đồng ý** — Không cần hỏi thêm.

---

## Step 1: Xem xét lại Phiên làm việc & Hot Buffer

1. **Đọc file `sessions/.hot-buffer.md`** (nếu có) để thu thập các quyết định/bài học đã ghi nhận giữa chừng.
2. **Đọc lại toàn bộ hội thoại** và tổng hợp cùng dữ liệu Hot Buffer để bóc tách:
   - **Quyết định đã đưa ra** — chốt phương án gì và tại sao
   - **Công việc đã xong** — code, fix, deploy, config
   - **Bài học rút ra** — trick mới, kinh nghiệm
   - **Việc dang dở** — cần tiếp tục phiên sau

## Step 2: Viết Tóm tắt Phiên (Archive)

Tạo file markdown tóm tắt chi tiết:

```markdown
# Session Summary — YYYY-MM-DD

## What We Did
- Bullet points công việc đã hoàn thành

## Decisions Made
- Quyết định quan trọng và lý do

## Key Learnings
- Bài học không hiển nhiên

## Open Threads
- Việc cần tiếp tục phiên sau

## Tools & Systems Touched
- Danh sách công cụ, repo, service
```

Lưu tại đường dẫn tương đối:
`./sessions/session-summary-YYYY-MM-DD.md`
Nếu cùng ngày có nhiều phiên: `session-summary-YYYY-MM-DD-2.md`

## Step 3: Cập nhật Rolling Context (Dual-Section)

Sau khi viết session summary, **CẬP NHẬT** file `sessions/current-context.md` theo **Atomic Write Pattern**:
- Ghi nội dung mới vào `current-context.tmp.md`
- Đổi tên (rename) đè lên `current-context.md` để đảm bảo file không bao giờ ở trạng thái nửa chừng (corrupted).

**Đây là file duy nhất mà `/startup` đọc** — nên phải luôn chính xác và cập nhật.

### Quy tắc cập nhật (Dual-Section Pattern):
1. **Đọc `current-context.md` hiện tại** (nếu tồn tại) để lấy `state` cũ.
2. **Giữ nguyên Khu vực `[STABLE FACTS]`:** Copy nguyên vẹn từ file cũ sang file mới. Nếu có phát sinh thêm luật lệ cốt lõi thì thêm vào.
3. **Merge thông minh Khu vực `[ACTIVE STATE]`:**
   - **Open Threads:** THAY THẾ hoàn toàn bằng open threads mới nhất từ phiên vừa kết thúc.
   - **Recent Decisions:** Giữ tối đa **5 gần nhất**.
   - **Key Learnings:** Giữ tối đa **5 gần nhất**.
   - **Last Session:** Thay thế hoàn toàn bằng phiên vừa kết thúc.
4. **KHÔNG append** — File này phải gọn, ~30-50 dòng. Overwrite toàn bộ file với cấu trúc mới.

### Template `current-context.md`:

```markdown
# Current Context

> Rolling summary — cập nhật tự động bởi /wrapup. Chỉ file này được đọc khi /startup.
> Last updated: YYYY-MM-DD

---
## 🏛️ [STABLE FACTS]
> (Khu vực này KẾ THỪA nguyên vẹn qua các phiên. Lưu trữ các cấu hình cố định, luật lệ đặc thù, conventions của dự án).
- Ví dụ: "Luôn deploy lên Vercel", "Dùng Tailwind bản 3.4"...

---
## 🚀 [ACTIVE STATE]
> (Khu vực này ĐƯỢC RESET và merge mỗi phiên. Chỉ lưu trạng thái công việc hiện tại).

### 🔥 Open Threads
1. [Việc dang dở 1]
2. [Việc dang dở 2]

### 📋 Recent Decisions (5 gần nhất)
- [YYYY-MM-DD] Quyết định 1 — lý do ngắn

### 💡 Key Learnings (5 gần nhất)
- [YYYY-MM-DD] Bài học 1

### 📋 Last Session (YYYY-MM-DD)
- [Tóm tắt 2-3 dòng công việc phiên cuối]

### 📊 Stats
- Total sessions: [N]
```

## Step 4: Dọn dẹp & Báo cáo

**4.1 Xóa Hot Buffer:**
Sử dụng lệnh shell để xóa file `sessions/.hot-buffer.md` (nếu có), vì toàn bộ dữ liệu đã được tổng hợp an toàn vào Archive và Rolling Context.

**4.2 Báo người dùng ngắn gọn:**
- Session log (archive) đã lưu
- Rolling context đã cập nhật ✅ (Đã dọn dẹp Hot Buffer)
- Việc dang dở cho phiên sau

## Khi nào Skill này kích hoạt?
**Lệnh trực tiếp:** `/wrapup`, `tổng kết`, `wrap up`, `save this session`, `end of session`.
