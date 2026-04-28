---
name: second-brain
description: >
  Read and query your personal AI Knowledge Base (Second Brain wiki).
  Lookup concepts, tools, people, and comparisons from the wiki.
  Activated by: "search brain", "wiki lookup", "what does my brain say about X"
---

# Second Brain — Hermes Skill

## Wiki Location
Your Second Brain wiki is at: `$HERMES_HOME/second-brain/wiki/`

## How to Use

### Lookup a topic
1. Read `$HERMES_HOME/second-brain/wiki/_index.md` (master catalog)
2. Read `$HERMES_HOME/second-brain/wiki/_graph.json` to see relationships and related concepts
3. Find the article matching the user's query (check aliases column in index)
4. Read the full article with `file_read`
5. Also read connected nodes (1-hop neighbors from graph) if context is needed
6. Respond using the wiki content as grounding

### If topic not found
1. Check `$HERMES_HOME/second-brain/wiki/_glossary.md`
2. Search raw sources: `$HERMES_HOME/second-brain/raw/`
3. If still not found: tell the user and suggest they use `/ingest` on their local Second Brain.

## Rules
- **NEVER modify wiki files.** Read-only access.
- Always cite the article name when using wiki knowledge.
- If information seems outdated, mention the `date_added` from the YAML frontmatter.

## Understanding the Graph
The file `wiki/_graph.json` contains a structured representation of how concepts connect. 
Use it to provide comprehensive answers that span multiple related articles.
