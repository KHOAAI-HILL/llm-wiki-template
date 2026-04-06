---
title: "Dashboard"
date_added: 2025-01-01
status: canonical
---

# 📊 Wiki Dashboard

## All Wiki Articles

```dataview
TABLE status, summary, date_added
FROM "wiki/concepts" OR "wiki/tools" OR "wiki/people" OR "wiki/comparisons"
SORT date_added DESC
```

## Articles by Status

### Draft (needs review)
```dataview
LIST
FROM "wiki"
WHERE status = "draft" AND file.name != "_index" AND file.name != "_glossary" AND file.name != "_ops_log"
SORT file.name ASC
```

### Stub (needs expansion)
```dataview
LIST
FROM "wiki"
WHERE status = "stub"
```

## Uncompiled Raw Sources

```dataview
TABLE source, date_added, tags
FROM "raw"
SORT date_added DESC
```

## Quick Stats

```dataview
TABLE length(rows) as "Count"
FROM "wiki/concepts" OR "wiki/tools" OR "wiki/people" OR "wiki/comparisons"
GROUP BY file.folder
```
