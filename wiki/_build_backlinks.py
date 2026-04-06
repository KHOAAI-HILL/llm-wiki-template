"""
Build backlinks index for Second Brain wiki.
Scans all .md files in wiki/, extracts [[wikilinks]], builds reverse index.
Output: wiki/_backlinks.json

Usage: python wiki/_build_backlinks.py
"""
import json
import re
import os
from pathlib import Path

WIKI_DIR = Path(__file__).parent
BACKLINKS_FILE = WIKI_DIR / "_backlinks.json"

# Files to skip (not articles)
SKIP_FILES = {"_index.md", "_glossary.md", "_absorb_log.json", "_backlinks.json", "_build_backlinks.py"}

def extract_wikilinks(content: str) -> list[str]:
    """Extract all [[wikilink]] targets from markdown content."""
    # Match [[target]] and [[target|display text]]
    pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
    links = re.findall(pattern, content)
    # Normalize: strip path prefixes, lowercase, strip whitespace
    normalized = []
    for link in links:
        # Handle paths like raw/tweets/filename
        name = link.strip()
        # Extract just the filename (last segment) if it's a path
        if '/' in name:
            name = name.split('/')[-1]
        normalized.append(name)
    return normalized

def build_backlinks() -> dict:
    """Scan wiki directory and build reverse link index."""
    # Forward links: {article -> [links_to]}
    forward = {}
    # Collect all articles
    articles = {}
    
    for root, dirs, files in os.walk(WIKI_DIR):
        for f in files:
            if f in SKIP_FILES or not f.endswith('.md'):
                continue
            filepath = Path(root) / f
            rel_path = filepath.relative_to(WIKI_DIR)
            article_name = f.replace('.md', '')
            
            content = filepath.read_text(encoding='utf-8')
            links = extract_wikilinks(content)
            forward[article_name] = links
            articles[article_name] = str(rel_path)
    
    # Build reverse index: {target -> [articles_that_link_to_it]}
    backlinks = {}
    for source, targets in forward.items():
        for target in targets:
            if target not in backlinks:
                backlinks[target] = []
            if source not in backlinks[target]:
                backlinks[target].append(source)
    
    # Sort by number of backlinks (most linked first)
    sorted_backlinks = dict(
        sorted(backlinks.items(), key=lambda x: len(x[1]), reverse=True)
    )
    
    result = {
        "description": "Reverse link index. Maps article -> list of articles linking TO it.",
        "last_updated": str(Path(__file__).stat().st_mtime),
        "total_articles": len(articles),
        "total_links": sum(len(v) for v in sorted_backlinks.values()),
        "backlinks": sorted_backlinks
    }
    
    return result

if __name__ == "__main__":
    print(f"Scanning wiki at: {WIKI_DIR}")
    result = build_backlinks()
    
    with open(BACKLINKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Built backlinks index: {len(result['backlinks'])} targets, {result['total_links']} total links")
    print(f"📄 Saved to: {BACKLINKS_FILE}")
    
    # Show top linked articles
    print("\n📊 Top linked articles:")
    for target, sources in list(result['backlinks'].items())[:10]:
        print(f"  {target}: {len(sources)} backlinks <- {sources}")
