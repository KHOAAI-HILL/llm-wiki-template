# 🧠 LLM Wiki Template

> An AI-managed personal knowledge base using the **Karpathy LLM Wiki Pattern** — where LLMs write and maintain a structured Obsidian wiki from your raw research data.

[![Obsidian](https://img.shields.io/badge/Obsidian-7C3AED?logo=obsidian&logoColor=white)](https://obsidian.md/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🌐 **Language:** **English** | [Tiếng Việt](README-vi.md)
---

## 📺 Video Hướng Dẫn

[![Bộ Nhớ AI Kiểu Karpathy](https://img.youtube.com/vi/8K5bplMrGMw/maxresdefault.jpg)](https://youtu.be/8K5bplMrGMw?si=BvXJBK4emen8xwU1)

**[Bộ Nhớ AI Kiểu Karpathy: 3 Bước Xây Wiki Cho Agent [Miễn Phí]](https://youtu.be/8K5bplMrGMw?si=BvXJBK4emen8xwU1)** — Hướng dẫn chi tiết từ setup đến sử dụng thực tế.

---

## What Is This?

This is a ready-to-use **template** for building an AI-powered personal knowledge base, inspired by [Andrej Karpathy's approach](https://x.com/karpathy/status/2039713585185882267) to using LLMs for knowledge management:

> *"Something I'm finding very useful recently: using LLMs to build personal knowledge bases for various topics of research interest."* — Andrej Karpathy

Instead of relying on complex RAG pipelines or vector databases, this system uses a simpler approach:

1. **You dump raw sources** (articles, tweets, papers, videos) into `raw/`
2. **The LLM compiles** structured wiki articles in `wiki/`
3. **You ask questions** and get answers grounded in your personal knowledge base
4. **Knowledge compounds** — each cycle makes the wiki richer

The result is a **100% inspectable**, file-based knowledge system where you can see exactly what your AI "knows."

## Key Features

- 📂 **File-based architecture** — Markdown files, no databases, no vendor lock-in
- 🔍 **100% inspectable** — Every piece of knowledge is a readable `.md` file
- 🔄 **10 automated workflows** — `/ingest`, `/compile`, `/ask`, `/cleanup`, `/breakdown`, `/autoresearch`, `/save`, `/overview`, `/startup`, `/wrapup`
- 🔬 **Autonomous research** — Agent searches the web, evaluates sources, and ingests automatically
- ⚖️ **Contradiction detection** — Flags conflicting claims instead of silently overwriting
- 💾 **Chat-to-Wiki pipeline** — Save knowledge from conversations directly to wiki
- 📊 **Self-maintaining indexes** — Master index, glossary, backlinks, executive overview, operations log
- 🛡️ **Quality gates** — Article size guardrails, anti-cramming/thinning rules, re-read checks
- 🧹 **Wiki health checks** — Automated tone, structure, link, and contradiction auditing
- 📈 **Compound knowledge loop** — Each cycle produces better knowledge, which produces better outputs

## Quick Start

### 1. Use This Template

Click **"Use this template"** → **"Create a new repository"** on GitHub.

Or clone manually:

```bash
git clone https://github.com/YOUR_USERNAME/llm-wiki-template.git my-second-brain
```

### 2. Open in Obsidian

1. Download [Obsidian](https://obsidian.md/) (free)
2. Open as vault: `File → Open vault → Open folder as vault`
3. Select the cloned directory
4. Install recommended plugins when prompted: **Dataview**, **Marp Slides**

### 3. Connect Your AI Agent

This template works with any LLM-powered coding agent that can read files. Tested with:

- **[Gemini CLI](https://github.com/google-gemini/gemini-cli)** (recommended)
- **Claude Code / Claude Desktop** with filesystem access
- **Cursor / Windsurf** with workspace access
- **Any agent** that can read/write Markdown files

The agent reads `AGENTS.md` as its operating manual — no additional configuration needed.

### 4. Start Building Your Knowledge Base

```
# Step 1: Ingest a source
/ingest https://example.com/interesting-article

# Step 2: Compile into wiki
/compile

# Step 3: Ask questions
/ask What are the key concepts from my sources?

# Step 4: Audit wiki quality
/cleanup

# Step 5: Find knowledge gaps
/breakdown

# Step 6: Auto-research a topic
/autoresearch Large Language Models

# Step 7: Save chat insights to wiki
/save
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 YOUR RESEARCH                    │
│  Articles, Tweets, Papers, Videos, Repos, etc.   │
└──────────────────────┬──────────────────────────┘
                       │ /ingest
                       ▼
┌─────────────────────────────────────────────────┐
│                  raw/                            │
│  Source documents — NEVER modified, only added    │
│  articles/ papers/ repos/ tweets/ videos/ misc/  │
└──────────┬───────────────────────┬──────────────┘
           │ /compile              │ /autoresearch
           ▼                      ▼
┌─────────────────────────────────────────────────┐
│                  wiki/                           │
│  Compiled knowledge — AI-maintained wiki          │
│  concepts/ tools/ people/ comparisons/           │
│  + _index.md, _glossary.md, overview.md          │
│  ⚖️ Contradiction Check before every update      │
└──────┬─────────┬─────────┬──────────────────────┘
       │ /ask    │ /cleanup │ /save
       ▼        ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────────────────┐
│ answers  │ │ quality  │ │ chat → raw → wiki     │
│ + refs   │ │ fixes    │ │ knowledge extraction  │
└──────────┘ └──────────┘ └──────────────────────┘
```

## Workflows

| Command | What It Does |
|---------|-------------|
| `/ingest` | Imports raw sources (URLs, files, PDFs) into `raw/` with proper frontmatter |
| `/compile` | Reads raw sources and creates/updates structured wiki articles (with **contradiction detection**) |
| `/ask` | Answers questions using wiki knowledge, with optional file-back to wiki |
| `/cleanup` | Audits wiki quality — tone, structure, links, size, **contradiction backlog** — and auto-fixes |
| `/breakdown` | Scans wiki for missing entities and proposes new articles |
| `/autoresearch` | 🆕 **Autonomous research** — searches the web, evaluates sources, ingests, and synthesizes reports |
| `/save` | 🆕 **Chat-to-Wiki** — extracts knowledge from conversations and saves directly to wiki |
| `/startup` | 🆕 **Project Brain Startup** — AI recalls context from previous sessions |
| `/wrapup` | 🆕 **Project Wrapup** — AI saves session archive and updates rolling context |

Each workflow is defined in `.agents/workflows/` and can be customized.

### AutoResearch — Autonomous Knowledge Discovery

The `/autoresearch` workflow turns your wiki into an active researcher:

```
/autoresearch [topic]
```

**How it works:**
1. **Gap Analysis** — Scans existing wiki to identify what's missing
2. **3-Round Research Loop** — Broad search → Gap fill → Verify
3. **Auto-Ingest** — Downloads and processes sources automatically
4. **Synthesis Report** — Generates an executive summary at `outputs/reports/`
5. **Human Review** — You approve before anything enters the wiki

Configure search constraints in `raw/_research_program.md`.

### Contradiction Detection

When compiling new sources, the system **automatically checks for conflicting claims**:

- ✅ **Temporal updates** (v1.0 → v2.0) — Updated normally
- ✅ **New information** — Integrated normally
- ⚠️ **Actual contradictions** — Preserved with `[!warning]` callout, tagged `needs-review`

The wiki **never silently overwrites** conflicting information. Human review is always required.

## Quality System

The template enforces several quality mechanisms:

- **Re-read before update** — The AI must read the full article before editing (non-negotiable)
- **Contradiction check** — Compare new claims against existing wiki before writing
- **Article size guardrails** — 15–120 lines; too short = stub, too long = split
- **Anti-cramming** — Sub-topics with ≥3 paragraphs get their own article
- **Anti-thinning** — No article creation unless ≥3 meaningful sentences can be written
- **Encyclopedia tone** — Neutral, attribution-based writing, no editorial voice
- **Absorption log** — Tracks which raw sources have been compiled (no duplicates)
- **Operations log** — Chronological record of every action taken on the vault

## File Structure

```
llm-wiki-template/
├── AGENTS.md                ← Agent operating manual (the brain)
├── README.md                ← This file
├── .gitignore
│
├── .agents/workflows/       ← 10 automated workflows
│   ├── ask.md
│   ├── autoresearch.md      ← 🆕 Autonomous research
│   ├── breakdown.md
│   ├── cleanup.md           ← Updated: contradiction backlog scanning
│   ├── compile.md           ← Updated: contradiction detection (Step 4.5)
│   ├── ingest.md
│   ├── save.md              ← 🆕 Chat-to-Wiki pipeline
│   ├── startup.md           ← 🆕 Session startup
│   └── wrapup.md            ← 🆕 Session wrapup
│
├── .obsidian/               ← Obsidian config (pre-configured)
│
├── sessions/                ← Session logs (AI Memory)
│   ├── current-context.md   ← Rolling context (auto-updated)
│   ├── .hot-buffer.md       ← Mid-session decisions buffer
│   └── session-summary-*.md ← Archive of each session
│
├── raw/                     ← Your source documents
│   ├── _ingest.py           ← Batch ingest script (Python)
│   ├── _research_program.md ← 🆕 AutoResearch configuration
│   ├── articles/
│   ├── papers/
│   ├── repos/
│   ├── tweets/
│   ├── videos/
│   └── misc/
│
├── wiki/                    ← AI-maintained wiki
│   ├── overview.md          ← 🆕 Executive summary for cross-project access
│   ├── _index.md            ← Master catalog
│   ├── _glossary.md         ← Term definitions
│   ├── _absorb_log.json     ← Compilation tracker
│   ├── _backlinks.json      ← Reverse link index
│   ├── _build_backlinks.py  ← Backlinks builder script
│   ├── _dashboard.md        ← Dataview dashboard
│   ├── _ops_log.md          ← Operations log
│   ├── concepts/
│   ├── tools/
│   ├── people/
│   └── comparisons/
│
└── outputs/                 ← Generated content
    ├── reports/             ← AutoResearch synthesis reports
    ├── slides/
    ├── charts/
    └── summaries/
```

## Customization

### Change the Language

The template uses English by default. To switch:
1. Edit `AGENTS.md` → update the Writing Tone section
2. Update wiki meta files (`_index.md`, `_glossary.md`) headers
3. The AI will follow your language preference from `AGENTS.md`

### Add Entity Types

Edit `AGENTS.md` → Entity-Type Templates section to add new categories beyond concepts/tools/people/comparisons.

### Modify Quality Rules

All quality rules are in `AGENTS.md`. Adjust thresholds (article size, quote density, etc.) to match your preferences.

### Configure AutoResearch

Edit `raw/_research_program.md` to customize:
- Search scope and constraints
- Confidence scoring thresholds
- Source exclusion lists
- Domain-specific notes and priorities

### Add Obsidian Plugins

The template includes configs for **Dataview** (tables/queries) and **Marp Slides** (presentations). Add more plugins through Obsidian's community plugin browser.

## Batch Ingest Script

For bulk importing, use the included Python script:

```bash
# Single file
python raw/_ingest.py path/to/article.md

# PDF (requires PyMuPDF: pip install PyMuPDF)
python raw/_ingest.py paper.pdf

# Entire folder
python raw/_ingest.py ~/Downloads/research-notes/

# Preview without creating files
python raw/_ingest.py big-folder/ --dry-run
```

## Philosophy

This template is built on three principles:

1. **Files over databases** — Markdown files are portable, inspectable, and version-controllable. No vector DB, no cloud dependencies.

2. **Compile once, query forever** — Instead of retrieving raw chunks on every query (RAG), the AI pre-compiles clean wiki articles. Queries read refined knowledge, not raw data.

3. **Knowledge compounds** — Each ingest-compile-ask cycle makes the wiki richer. Better wiki → better answers → better questions → richer wiki.

## Credits

- **[Andrej Karpathy](https://x.com/karpathy)** — Originated the LLM Knowledge Base concept
- **[Farzaa](https://gist.github.com/farzaa/c35ac0cfbeb957788650e36aabea836d)** — `wiki-gen-skill` implementation that heavily influenced quality gates
- **[DataChaz](https://x.com/DataChaz/status/2039963758790156555)** — Community breakdown and analysis

## License

MIT — Use freely, modify as you wish, share with others.
