# Second Brain — Agent Schema

> This file is the **single source of truth** for any LLM operating on this vault.
> Read this FIRST before making any changes.

## Purpose

This Obsidian vault is an **AI-managed knowledge base** following the [Karpathy LLM Knowledge Base](https://x.com/karpathy/status/2039713585185882267) methodology. The LLM writes and maintains all wiki content. The human rarely edits directly — they ingest raw data, ask questions, and review outputs.

## Directory Structure

```
llm-wiki-template/
├── raw/                 ← Source documents. NEVER modify, only ADD.
│   ├── articles/        ← Web articles (clipped or pasted)
│   ├── papers/          ← Academic papers, PDF notes
│   ├── repos/           ← GitHub repo notes, README summaries
│   ├── videos/          ← YouTube transcripts, video notes
│   ├── tweets/          ← X/Twitter threads, social posts
│   └── misc/            ← Images, CSV, datasets, other
│
├── wiki/                ← Compiled knowledge. AI-maintained.
│   ├── _index.md        ← Master index (MUST stay updated)
│   ├── _glossary.md     ← Key terms and definitions
│   ├── concepts/        ← Concept articles (the core)
│   ├── tools/           ← Tool/product evaluations
│   ├── people/          ← Notable people profiles
│   └── comparisons/     ← A vs B analysis articles
│
├── outputs/             ← Query results, generated content
│   ├── reports/         ← Deep-dive research reports
│   ├── slides/          ← Marp-format slide decks
│   ├── charts/          ← Generated visualizations
│   └── summaries/       ← Quick summaries on demand
│
└── AGENTS.md            ← THIS FILE — vault schema
```

## File Conventions

### Naming
- **kebab-case**: `retrieval-augmented-generation.md`
- **No spaces**: Use hyphens
- **Descriptive**: Name should convey content at a glance

### Frontmatter (YAML) — Required for ALL files

```yaml
---
title: "Human-readable title"
source: "URL, file path, or 'compiled'"  
date_added: 2025-01-01
tags: [concept, ai, rag]
aliases: [alias1, alias2]
status: draft | reviewed | canonical
related:
  - "[[other-article]]"
  - "[[another-one]]"
summary: "One-line summary for _index.md"
---
```

### Content Rules
- Use `[[wikilinks]]` for internal links (Obsidian-native)
- Images: Store in same directory as the .md referencing them
- Code blocks: Always specify language (```python, ```bash, etc.)
- Headers: Start at ## (h2) inside articles (h1 = title in frontmatter)

### Writing Tone — Encyclopedia Style
- Neutral, evidence-based tone. Not a blog, not personal notes.
- Avoid: "interestingly", "importantly", "it should be noted", "groundbreaking", "legendary"
- Structure articles by theme, not chronologically
- Convey emotion/opinions through direct quotes from raw sources
- Prefer impactful quotes sparingly over scattered ones
- 1 idea = 1 sentence. Short sentences. Write paragraphs, limit bullet-points to enumerations only.
- Attribution over assertion: "Karpathy describes it as..." instead of "It is very..."

## Index Maintenance

The file `wiki/_index.md` is the **master catalog**. Rules:
1. MUST list every article in `wiki/` with one-line summary
2. Group by subdirectory (concepts, tools, people, comparisons)
3. Update `_index.md` EVERY time a wiki article is added/removed
4. Include article count and last-updated timestamp

## Compilation Rules

When compiling from `raw/` to `wiki/`:
1. Read the raw source completely
2. Check `wiki/_absorb_log.json` to see which raw sources have been compiled
3. Identify key concepts, tools, and people mentioned
4. For each:
   - Check if wiki article already exists → UPDATE
   - If not → CREATE new article
5. **Re-read the entire wiki article BEFORE updating — non-negotiable**
6. After re-reading, ask: "What new depth does this entry add that the article doesn't already have?"
   - If the answer is "nothing new" → DO NOT edit the article
7. When updating, **integrate** new content into existing narrative flow — don't just append bullet points at the end
8. Add `[[backlinks]]` to related existing articles
9. Update `_index.md`
10. Update `wiki/_absorb_log.json` — record the compiled raw source
11. Never delete content from existing articles — refine and integrate

## Quality Standards

- Each wiki article should be **self-contained** (understandable alone)
- Minimum 200 words per concept article
- Each article should link to ≥2 other wiki articles
- Avoid duplicating content — link instead

### Article Size Guardrails
- **Limits:** 15–120 lines of content (excluding frontmatter)
  - Under 15 lines → tag `status: stub`, prioritize expansion when new raw is available
  - Over 120 lines → consider splitting sub-topics into separate articles
- **Anti-Cramming:** If a sub-topic appears in ≥3 paragraphs within one article → split into a child article
- **Anti-Thinning:** Don't create an article if you can't write ≥3 meaningful sentences. Every touch must make the article richer.

### Entity-Type Templates

Each wiki article type has its own structure. Use the correct template:

**Concept** (`wiki/concepts/`):
- `## Definition` — 1 clear paragraph
- `## [Thematic Sections]` — varies by topic (Architecture, Mechanism, Examples...)
- `## Applications / Connections` — real-world context
- `## References`

**Tool** (`wiki/tools/`):
- `## Overview` — what it is, who made it, purpose
- `## Role In [Context]` — how it's used in the system
- `## Advantages / Limitations` — neutral assessment
- `## References`

**Person** (`wiki/people/`):
- `## Biography` — 2-3 sentences of background
- `## Contributions to This Wiki's Knowledge` — direct connection to wiki topics
- `## References`

**Comparison** (`wiki/comparisons/`):
- `## Context` — why the comparison matters
- `## Comparison Table` — clear criteria table
- `## Analysis` — assessment across dimensions
- `## Conclusion`

**Report/Summary** (`outputs/`):
- `## Context` — background of the request
- `## Analysis` — main content
- `## Conclusion / Actions`
- `## Sources`

## Classify-Before-Extract

Before compiling raw/ into wiki, **classify sources by type** to apply the right extraction strategy:

| Source Type | Characteristics | Extraction Strategy |
|-------------|----------------|-------------------|
| **Tweet/Thread** | Short, dense, has replies | Extract main assertions + notable replies. Each valuable reply = 1 data point |
| **Article/Gist** | Long, structured | Extract by sections. Find main thesis + supporting arguments |
| **Paper/Report** | Formal, has abstract/methodology | Extract abstract → findings → implications. Note evidence-backed claims |
| **Diagram/Image** | Visual | Decompose layers, components, flows. Describe in text + tables |
| **Video/Transcript** | Long, conversational | Find key moments, impactful quotes. Skip filler/tangents |
| **Repo/Code** | Technical | Extract architecture, patterns, API surface. README is starting point |

**Rule:** Don't treat all raw sources the same. A 50-page report needs a different strategy than a 5-tweet thread.

## Operations Log

File `wiki/_ops_log.md` records **all operations** chronologically:
- Append one line `## [YYYY-MM-DD] action | title` after each ingest, compile, ask, cleanup
- NEVER edit old entries — only append
- Workflows `/ingest`, `/compile`, `/ask`, `/cleanup` MUST append to the log

## Dual Output Rule

Any task that produces knowledge (Q&A, analysis, comparison) should consider producing **2 outputs**:
1. **Output 1:** Direct answer to the user
2. **Output 2:** Update wiki if the answer contains new insights not yet in wiki

Rule: If `/ask` generates a valuable synthesis → ask the user if they want to file it back into the wiki.
