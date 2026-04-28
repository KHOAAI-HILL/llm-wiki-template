# 🔗 Connect Your Second Brain to Hermes Agent

*Scroll down for Vietnamese | Kéo xuống để đọc tiếng Việt*

## 🇺🇸 English

### Prerequisites
- A running [Hermes Agent](https://github.com/NousResearch/hermes-agent) (Local, Docker, or Railway).
- Your Second Brain repo pushed to GitHub (private or public).
- A GitHub Personal Access Token with `repo` scope.

### Step 1: Push Your Second Brain to GitHub
*(Skip if your brain is already on GitHub)*
```bash
cd /path/to/your-second-brain
git init
git add .
git commit -m "Initial brain"
git remote add origin https://github.com/YOUR_USER/my-second-brain.git
git push -u origin main
```

### Step 2: Add the Hermes Skill
Copy the skill file to your Hermes instance:
```bash
cp -r integrations/hermes/SKILL.md ~/.hermes/skills/second-brain/SKILL.md
```

If you are using Docker or Railway, simply set these environment variables in your deployment dashboard:
- `SECOND_BRAIN_REPO=YOUR_USER/my-second-brain`
- `GITHUB_TOKEN=ghp_xxxxxxxxxxxx`

### Step 3: Update SOUL.md
Append the snippet to your Hermes `SOUL.md`:
```bash
cat integrations/hermes/SOUL-snippet.md >> ~/.hermes/SOUL.md
```

### Step 4: Verify
Ask Hermes via Telegram, Discord, or CLI:
> *"What's in my Second Brain wiki?"*

Hermes should read `wiki/_index.md` and respond with the list of your knowledge articles.

---

## 🇻🇳 Tiếng Việt

### Yêu cầu chuẩn bị
- Đang chạy [Hermes Agent](https://github.com/NousResearch/hermes-agent) (Local, Docker, hoặc Railway).
- Repo Second Brain của bạn đã được đẩy lên GitHub.
- Một GitHub Personal Access Token có quyền `repo`.

### Bước 1: Đẩy Second Brain lên GitHub
*(Bỏ qua nếu bạn đã có repo trên GitHub)*
```bash
cd /path/to/your-second-brain
git init
git add .
git commit -m "Khoi tao brain"
git remote add origin https://github.com/YOUR_USER/my-second-brain.git
git push -u origin main
```

### Bước 2: Thêm Skill cho Hermes
Copy file skill vào Hermes của bạn:
```bash
cp -r integrations/hermes/SKILL.md ~/.hermes/skills/second-brain/SKILL.md
```

Nếu bạn dùng Docker hoặc Railway, chỉ cần thêm các biến môi trường sau vào phần quản lý cấu hình:
- `SECOND_BRAIN_REPO=YOUR_USER/my-second-brain`
- `GITHUB_TOKEN=ghp_xxxxxxxxxxxx`

### Bước 3: Cập nhật SOUL.md
Nối thêm đoạn snippet vào file `SOUL.md` của Hermes:
```bash
cat integrations/hermes/SOUL-snippet.md >> ~/.hermes/SOUL.md
```

### Bước 4: Kiểm tra thành quả
Hỏi Hermes qua Telegram, Discord, hoặc CLI:
> *"Có gì trong wiki Second Brain của tôi?"*

Hermes sẽ tự động đọc `wiki/_index.md` và trả lời dựa trên danh sách các bài viết kiến thức của bạn.
