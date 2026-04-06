# 🧠 LLM Wiki Template

> An AI-managed personal knowledge base using the **Karpathy LLM Wiki Pattern** — where LLMs write and maintain a structured Obsidian wiki from your raw research data.

[![Obsidian](https://img.shields.io/badge/Obsidian-7C3AED?logo=obsidian&logoColor=white)](https://obsidian.md/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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
- 🔄 **5 automated workflows** — `/ingest`, `/compile`, `/ask`, `/cleanup`, `/breakdown`
- 📊 **Self-maintaining indexes** — Master index, glossary, backlinks, operations log
- ⚖️ **Quality gates** — Article size guardrails, anti-cramming/thinning rules, re-read checks
- 🧹 **Wiki health checks** — Automated tone, structure, and link auditing
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
└──────────────────────┬──────────────────────────┘
                       │ /compile
                       ▼
┌─────────────────────────────────────────────────┐
│                  wiki/                           │
│  Compiled knowledge — AI-maintained wiki          │
│  concepts/ tools/ people/ comparisons/           │
│  + _index.md, _glossary.md, _backlinks.json      │
└──────────┬───────────────────────┬──────────────┘
           │ /ask                  │ /cleanup
           ▼                      ▼
┌──────────────────┐  ┌──────────────────────────┐
│    answers +     │  │  quality fixes, tone      │
│    file-back     │  │  corrections, backlinks   │
└──────────────────┘  └──────────────────────────┘
```

## Workflows

| Command | What It Does |
|---------|-------------|
| `/ingest` | Imports raw sources (URLs, files, PDFs) into `raw/` with proper frontmatter |
| `/compile` | Reads raw sources and creates/updates structured wiki articles |
| `/ask` | Answers questions using wiki knowledge, with optional file-back |
| `/cleanup` | Audits wiki quality — tone, structure, links, size — and auto-fixes issues |
| `/breakdown` | Scans wiki for missing entities and proposes new articles |

Each workflow is defined in `.agents/workflows/` and can be customized.

## Quality System

The template enforces several quality mechanisms:

- **Re-read before update** — The AI must read the full article before editing (non-negotiable)
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
├── .agents/workflows/       ← 5 automated workflows
│   ├── ask.md
│   ├── breakdown.md
│   ├── cleanup.md
│   ├── compile.md
│   └── ingest.md
│
├── .obsidian/               ← Obsidian config (pre-configured)
│
├── raw/                     ← Your source documents
│   ├── _ingest.py           ← Batch ingest script (Python)
│   ├── articles/
│   ├── papers/
│   ├── repos/
│   ├── tweets/
│   ├── videos/
│   └── misc/
│
├── wiki/                    ← AI-maintained wiki
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
    ├── reports/
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
