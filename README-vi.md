# 🧠 LLM Wiki Template

> Bộ nhớ AI cá nhân được quản lý bởi AI theo **Phương pháp Karpathy LLM Wiki** — nơi LLM tự viết và duy trì một wiki Obsidian có cấu trúc từ dữ liệu nghiên cứu thô của bạn.

[![Obsidian](https://img.shields.io/badge/Obsidian-7C3AED?logo=obsidian&logoColor=white)](https://obsidian.md/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🌐 **Ngôn ngữ:** [English](README.md) | **Tiếng Việt**

---

## 📺 Video Hướng Dẫn

[![Bộ Nhớ AI Kiểu Karpathy](https://img.youtube.com/vi/8K5bplMrGMw/maxresdefault.jpg)](https://youtu.be/8K5bplMrGMw?si=BvXJBK4emen8xwU1)

**[Bộ Nhớ AI Kiểu Karpathy: 3 Bước Xây Wiki Cho Agent [Miễn Phí]](https://youtu.be/8K5bplMrGMw?si=BvXJBK4emen8xwU1)** — Hướng dẫn chi tiết từ setup đến sử dụng thực tế.

---

## Đây Là Gì?

Đây là **template sẵn sàng dùng** để xây dựng bộ nhớ AI cá nhân, lấy cảm hứng từ [cách tiếp cận của Andrej Karpathy](https://x.com/karpathy/status/2039713585185882267) trong việc sử dụng LLM cho quản lý kiến thức:

> *"Gần đây tôi thấy rất hữu ích: sử dụng LLM để xây dựng bộ nhớ kiến thức cá nhân cho các chủ đề nghiên cứu khác nhau."* — Andrej Karpathy

Thay vì phụ thuộc vào pipeline RAG phức tạp hay vector database, hệ thống này sử dụng cách tiếp cận đơn giản hơn:

1. **Bạn nạp nguồn thô** (bài viết, tweet, paper, video) vào `raw/`
2. **LLM biên dịch** thành các bài wiki có cấu trúc trong `wiki/`
3. **Bạn hỏi đáp** và nhận câu trả lời dựa trên bộ nhớ kiến thức của mình
4. **Kiến thức tích lũy** — mỗi vòng lặp làm wiki phong phú hơn

Kết quả là một hệ thống kiến thức **100% kiểm tra được**, dựa trên file, nơi bạn có thể thấy chính xác AI của mình "biết" những gì.

## Tính Năng Chính

- 📂 **Kiến trúc file** — File Markdown, không database, không phụ thuộc nhà cung cấp
- 🔍 **100% kiểm tra được** — Mọi kiến thức là file `.md` đọc được
- 🔄 **10 workflow tự động** — `/ingest`, `/compile`, `/ask`, `/cleanup`, `/breakdown`, `/autoresearch`, `/save`, `/overview`, `/startup`, `/wrapup`
- 🔬 **Nghiên cứu tự động** — Agent tự tìm kiếm web, đánh giá nguồn, và nạp tự động
- ⚖️ **Phát hiện mâu thuẫn** — Đánh dấu các claim xung đột thay vì ghi đè im lặng
- 💾 **Chat-to-Wiki** — Lưu kiến thức từ cuộc hội thoại trực tiếp vào wiki
- 📊 **Index tự bảo trì** — Master index, glossary, backlinks, executive overview, operations log
- 🛡️ **Cổng chất lượng** — Giới hạn kích thước bài, chống nhồi nhét/mỏng quá, kiểm tra lại trước khi sửa
- 🧹 **Kiểm tra sức khỏe wiki** — Tự động audit giọng văn, cấu trúc, liên kết, và mâu thuẫn tồn đọng
- 📈 **Vòng lặp tích lũy kiến thức** — Mỗi chu kỳ tạo ra kiến thức tốt hơn → kết quả tốt hơn

## Bắt Đầu Nhanh

### 1. Sử Dụng Template

Nhấn **"Use this template"** → **"Create a new repository"** trên GitHub.

Hoặc clone thủ công:

```bash
git clone https://github.com/YOUR_USERNAME/llm-wiki-template.git my-second-brain
```

### 2. Mở Trong Obsidian

1. Tải [Obsidian](https://obsidian.md/) (miễn phí)
2. Mở vault: `File → Open vault → Open folder as vault`
3. Chọn thư mục vừa clone
4. Cài plugin được gợi ý: **Dataview**, **Marp Slides**

### 3. Kết Nối AI Agent

Template này hoạt động với bất kỳ coding agent nào có khả năng đọc file. Đã test với:

- **[Gemini CLI](https://github.com/google-gemini/gemini-cli)** (khuyên dùng)
- **Claude Code / Claude Desktop** với quyền truy cập filesystem
- **Cursor / Windsurf** với quyền truy cập workspace
- **Bất kỳ agent nào** có thể đọc/ghi file Markdown

Agent đọc `AGENTS.md` như sổ tay vận hành — không cần cấu hình thêm.

### 4. Bắt Đầu Xây Dựng Bộ Nhớ Kiến Thức

```
# Bước 1: Nạp nguồn
/ingest https://example.com/bai-viet-hay

# Bước 2: Biên dịch thành wiki
/compile

# Bước 3: Hỏi đáp
/ask Các khái niệm chính từ nguồn của tôi là gì?

# Bước 4: Kiểm tra chất lượng wiki
/cleanup

# Bước 5: Tìm khoảng trống kiến thức
/breakdown

# Bước 6: Nghiên cứu tự động một chủ đề
/autoresearch Large Language Models

# Bước 7: Lưu insight từ chat vào wiki
/save
```

## Kiến Trúc

```
┌─────────────────────────────────────────────────┐
│               NGHIÊN CỨU CỦA BẠN                │
│  Bài viết, Tweet, Paper, Video, Repo, v.v.       │
└──────────────────────┬──────────────────────────┘
                       │ /ingest
                       ▼
┌─────────────────────────────────────────────────┐
│                  raw/                            │
│  Tài liệu gốc — KHÔNG BAO GIỜ sửa, chỉ thêm   │
│  articles/ papers/ repos/ tweets/ videos/ misc/  │
└──────────┬───────────────────────┬──────────────┘
           │ /compile              │ /autoresearch
           ▼                      ▼
┌─────────────────────────────────────────────────┐
│                  wiki/                           │
│  Kiến thức đã biên dịch — wiki do AI duy trì     │
│  concepts/ tools/ people/ comparisons/           │
│  + _index.md, _glossary.md, overview.md          │
│  ⚖️ Kiểm tra mâu thuẫn trước mỗi cập nhật       │
└──────┬─────────┬─────────┬──────────────────────┘
       │ /ask    │ /cleanup │ /save
       ▼        ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────────────────┐
│ câu trả  │ │ sửa chữa │ │ chat → raw → wiki     │
│ lời      │ │ chất lượng│ │ trích xuất kiến thức  │
└──────────┘ └──────────┘ └──────────────────────┘
```

## Các Workflow

| Lệnh | Chức Năng |
|-------|-----------|
| `/ingest` | Nạp nguồn thô (URL, file, PDF) vào `raw/` với frontmatter chuẩn |
| `/compile` | Đọc nguồn thô và tạo/cập nhật bài wiki có cấu trúc (có **phát hiện mâu thuẫn**) |
| `/ask` | Hỏi đáp dựa trên kiến thức wiki, có thể file-back vào wiki |
| `/cleanup` | Kiểm tra chất lượng wiki — giọng văn, cấu trúc, liên kết, kích thước, **backlog mâu thuẫn** |
| `/breakdown` | Quét wiki tìm entity còn thiếu và đề xuất bài mới |
| `/autoresearch` | 🆕 **Nghiên cứu tự động** — tìm kiếm web, đánh giá nguồn, nạp, và tổng hợp báo cáo |
| `/save` | 🆕 **Chat-to-Wiki** — trích xuất kiến thức từ cuộc hội thoại và lưu thẳng vào wiki |
| `/startup` | 🆕 **Khởi động bộ não** — AI tự nhớ lại ngữ cảnh từ các phiên làm việc trước |
| `/wrapup` | 🆕 **Tổng kết phiên** — AI lưu trữ tóm tắt phiên và cập nhật ngữ cảnh làm việc |

Mỗi workflow được định nghĩa trong `.agents/workflows/` và có thể tùy chỉnh.

### AutoResearch — Tự Động Khám Phá Kiến Thức

Workflow `/autoresearch` biến wiki của bạn thành một nhà nghiên cứu tự động:

```
/autoresearch [chủ đề]
```

**Cách hoạt động:**
1. **Phân tích khoảng trống** — Quét wiki hiện tại để xác định thiếu gì
2. **3 Vòng nghiên cứu** — Tìm rộng → Lấp khoảng trống → Xác minh
3. **Tự động nạp** — Tải và xử lý nguồn tự động
4. **Báo cáo tổng hợp** — Tạo executive summary tại `outputs/reports/`
5. **Chờ duyệt** — Bạn phê duyệt trước khi bất cứ thứ gì vào wiki

Cấu hình ràng buộc tìm kiếm trong `raw/_research_program.md`.

### Phát Hiện Mâu Thuẫn

Khi biên dịch nguồn mới, hệ thống **tự động kiểm tra claim xung đột**:

- ✅ **Cập nhật theo thời gian** (v1.0 → v2.0) — Cập nhật bình thường
- ✅ **Thông tin mới** — Tích hợp bình thường
- ⚠️ **Mâu thuẫn thật** — Giữ nguyên cả hai + callout `[!warning]`, đánh dấu `needs-review`

Wiki **không bao giờ ghi đè im lặng** thông tin xung đột. Luôn cần con người duyệt.

## Hệ Thống Chất Lượng

Template áp dụng nhiều cơ chế đảm bảo chất lượng:

- **Đọc lại trước khi cập nhật** — AI phải đọc toàn bộ bài trước khi sửa (bắt buộc)
- **Kiểm tra mâu thuẫn** — So sánh claim mới với wiki hiện có trước khi ghi
- **Giới hạn kích thước bài** — 15–120 dòng; quá ngắn = stub, quá dài = tách
- **Chống nhồi nhét** — Chủ đề phụ có ≥3 đoạn văn sẽ tách thành bài riêng
- **Chống mỏng quá** — Không tạo bài nếu không viết được ≥3 câu có ý nghĩa
- **Giọng bách khoa toàn thư** — Trung lập, dẫn nguồn, không bình luận chủ quan
- **Nhật ký hấp thụ** — Theo dõi nguồn nào đã biên dịch (không trùng lặp)
- **Nhật ký vận hành** — Ghi chép theo thời gian mọi hành động trên vault

## Cấu Trúc Thư Mục

```
llm-wiki-template/
├── AGENTS.md                ← Sổ tay vận hành cho Agent (bộ não)
├── README.md                ← README tiếng Anh
├── README-vi.md             ← File này (tiếng Việt)
├── update.py                ← 🆕 Script cập nhật 1 lệnh
├── .gitignore
│
├── .agents/workflows/       ← 10 workflow tự động
│   ├── ask.md
│   ├── autoresearch.md      ← 🆕 Nghiên cứu tự động
│   ├── breakdown.md
│   ├── cleanup.md           ← Cập nhật: quét mâu thuẫn tồn đọng
│   ├── compile.md           ← Cập nhật: phát hiện mâu thuẫn (Bước 4.5)
│   ├── ingest.md
│   ├── save.md              ← 🆕 Pipeline Chat-to-Wiki
│   ├── startup.md           ← 🆕 Khởi động phiên làm việc
│   └── wrapup.md            ← 🆕 Tổng kết phiên làm việc
│
├── .obsidian/               ← Cấu hình Obsidian (đã thiết lập sẵn)
│
├── sessions/                ← Session logs (AI Memory)
│   ├── current-context.md   ← Ngữ cảnh hiện tại (cập nhật tự động)
│   ├── .hot-buffer.md       ← Bộ đệm quyết định giữa phiên
│   └── session-summary-*.md ← Archive tóm tắt từng phiên
│
├── raw/                     ← Tài liệu gốc của bạn
│   ├── _ingest.py           ← Script nạp hàng loạt (Python)
│   ├── _research_program.md ← 🆕 Cấu hình AutoResearch
│   ├── articles/
│   ├── papers/
│   ├── repos/
│   ├── tweets/
│   ├── videos/
│   └── misc/
│
├── wiki/                    ← Wiki do AI duy trì
│   ├── overview.md          ← 🆕 Tóm tắt tổng quan cho cross-project access
│   ├── _index.md            ← Master catalog
│   ├── _glossary.md         ← Bảng thuật ngữ
│   ├── _absorb_log.json     ← Theo dõi biên dịch
│   ├── _backlinks.json      ← Chỉ mục liên kết ngược
│   ├── _build_backlinks.py  ← Script build backlinks
│   ├── _dashboard.md        ← Dashboard Dataview
│   ├── _ops_log.md          ← Nhật ký vận hành
│   ├── concepts/
│   ├── tools/
│   ├── people/
│   └── comparisons/
│
└── outputs/                 ← Nội dung tạo ra
    ├── reports/             ← Báo cáo tổng hợp AutoResearch
    ├── slides/
    ├── charts/
    └── summaries/
```

## Tùy Chỉnh

### Thay Đổi Ngôn Ngữ

Template mặc định dùng tiếng Anh. Để chuyển:
1. Sửa `AGENTS.md` → cập nhật phần Writing Tone
2. Cập nhật header các file meta wiki (`_index.md`, `_glossary.md`)
3. AI sẽ tuân theo ngôn ngữ bạn chọn từ `AGENTS.md`

### Thêm Loại Entity

Sửa `AGENTS.md` → phần Entity-Type Templates để thêm danh mục mới ngoài concepts/tools/people/comparisons.

### Điều Chỉnh Quy Tắc Chất Lượng

Mọi quy tắc chất lượng nằm trong `AGENTS.md`. Điều chỉnh ngưỡng (kích thước bài, mật độ trích dẫn, v.v.) theo sở thích.

### Cấu Hình AutoResearch

Sửa `raw/_research_program.md` để tùy chỉnh:
- Phạm vi và ràng buộc tìm kiếm
- Ngưỡng đánh giá độ tin cậy
- Danh sách nguồn loại trừ
- Ghi chú và ưu tiên theo lĩnh vực

### Thêm Plugin Obsidian

Template đã cấu hình sẵn **Dataview** (bảng/truy vấn) và **Marp Slides** (thuyết trình). Thêm plugin khác qua trình duyệt community plugin của Obsidian.

## Script Nạp Hàng Loạt

Để nạp số lượng lớn, dùng script Python đi kèm:

```bash
# Một file
python raw/_ingest.py path/to/article.md

# PDF (cần PyMuPDF: pip install PyMuPDF)
python raw/_ingest.py paper.pdf

# Cả thư mục
python raw/_ingest.py ~/Downloads/research-notes/

# Xem trước không tạo file
python raw/_ingest.py big-folder/ --dry-run
```

## Cập Nhật Vault

Đã dùng template từ trước? Cập nhật lên phiên bản mới nhất chỉ với 1 lệnh:

```bash
# Xem trước thay đổi (an toàn, không ghi file)
python update.py --dry-run

# Áp dụng cập nhật (có hỏi xác nhận)
python update.py

# Áp dụng không hỏi
python update.py --force
```

Script chỉ cập nhật **file hệ thống** (workflows, `AGENTS.md`). Dữ liệu cá nhân (`raw/`, `wiki/`, `sessions/`, `outputs/`) **không bao giờ bị chạm vào**.

Nếu chưa có script, tải về:

```bash
curl -o update.py https://raw.githubusercontent.com/KHOAAI-HILL/llm-wiki-template/master/update.py
```

## Triết Lý

Template này được xây dựng trên ba nguyên tắc:

1. **File hơn database** — File Markdown có thể di chuyển, kiểm tra, và quản lý phiên bản. Không cần vector DB, không phụ thuộc cloud.

2. **Biên dịch một lần, truy vấn mãi mãi** — Thay vì truy xuất chunk thô mỗi lần hỏi (RAG), AI biên dịch sẵn bài wiki sạch. Truy vấn đọc kiến thức đã tinh chế, không phải dữ liệu thô.

3. **Kiến thức tích lũy** — Mỗi chu kỳ nạp-biên dịch-hỏi làm wiki phong phú hơn. Wiki tốt hơn → câu trả lời tốt hơn → câu hỏi hay hơn → wiki giàu hơn.

## Ghi Công

- **[Andrej Karpathy](https://x.com/karpathy)** — Khởi xướng khái niệm LLM Knowledge Base
- **[Farzaa](https://gist.github.com/farzaa/c35ac0cfbeb957788650e36aabea836d)** — Triển khai `wiki-gen-skill`, ảnh hưởng lớn đến cổng chất lượng
- **[DataChaz](https://x.com/DataChaz/status/2039963758790156555)** — Phân tích và phổ biến trong cộng đồng

## Giấy Phép

MIT — Sử dụng tự do, chỉnh sửa tùy ý, chia sẻ với mọi người.
