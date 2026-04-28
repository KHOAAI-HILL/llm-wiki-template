## Second Brain Integration

You have access to a personal Knowledge Base at `$HERMES_HOME/second-brain/`.

Structure:
- `wiki/_index.md` — Master catalog of all articles
- `wiki/_graph.json` — Knowledge Graph mapping relationships between concepts
- `wiki/concepts/` — Core concept articles
- `wiki/tools/` — Tool evaluations
- `wiki/people/` — Notable people profiles
- `wiki/comparisons/` — A vs B analyses
- `wiki/_glossary.md` — Key term definitions
- `raw/` — Original source documents (immutable)

When the user asks about a topic:
1. First check if wiki has a relevant article (read _index.md and _graph.json)
2. If yes → read the full article and related concepts, then use it as context
3. If no → respond with your own knowledge and suggest they ingest it

You may NOT modify any files in second-brain/. Read-only access only.
