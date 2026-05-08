import os
import re
import argparse
import yaml
from pathlib import Path
import brain_db

WORKSPACE = Path.cwd()
SESSIONS_DIR = WORKSPACE / "sessions"
WIKI_DIR = WORKSPACE / "wiki"
DB_FILE = SESSIONS_DIR / "brain.db"

def parse_yaml_frontmatter(content):
    """Trích xuất và parse khối YAML frontmatter."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)) or {}, content[match.end():]
        except yaml.YAMLError:
            pass
    return {}, content

def parse_session_summary(filepath: Path, content: str):
    """Phân tích nội dung file session summary."""
    # Lấy project từ tên thư mục chứa file
    project = filepath.parent.name
    
    # Extract date from filename: session-summary-YYYY-MM-DD.md
    date_match = re.search(r'session-summary-(\d{4}-\d{2}-\d{2})', filepath.name)
    date = date_match.group(1) if date_match else "unknown"
    
    # Extract sections
    sections = {}
    current_section = None
    section_content = []
    
    lines = content.split('\n')
    for line in lines:
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(section_content).strip()
            current_section = line[3:].strip()
            section_content = []
        elif current_section:
            section_content.append(line)
            
    if current_section:
        sections[current_section] = '\n'.join(section_content).strip()

    # Extract Decisions and Tools
    decisions = [line.strip('- ').strip() for line in sections.get('Decisions Made', '').split('\n') if line.strip().startswith('-')]
    tools = [line.strip('- ').strip() for line in sections.get('Tools & Systems Touched', '').split('\n') if line.strip().startswith('-')]
    
    summary_text = sections.get('What We Did', '')
    summary = summary_text.split('\n')[0].strip('- ') if summary_text else "Không có tóm tắt"
    
    # Gộp toàn bộ text để index keyword (chỉ cần chữ, loại bỏ markdown cơ bản)
    all_text = re.sub(r'#+\s', '', content)
    
    return {
        "file_path": str(filepath.relative_to(WORKSPACE)).replace('\\', '/'),
        "source_type": "session",
        "project": project,
        "date": date,
        "summary": summary,
        "sections": {
            "decisions": decisions,
            "tools": tools
        },
        "searchable_text": all_text
    }

def parse_wiki_article(filepath: Path, content: str):
    """Phân tích nội dung file wiki."""
    frontmatter, body_content = parse_yaml_frontmatter(content)
    
    title = frontmatter.get('title', filepath.stem.replace('-', ' '))
    tags = frontmatter.get('tags', [])
    aliases = frontmatter.get('aliases', [])
    summary = frontmatter.get('summary', 'Không có tóm tắt')
    date_added = frontmatter.get('date_added', 'unknown')
    
    # Xây dựng searchable text (từ frontmatter + content)
    all_text = f"{title}\n" + "\n".join(tags) + "\n" + "\n".join(aliases) + "\n" + body_content
    
    return {
        "file_path": str(filepath.relative_to(WORKSPACE)).replace('\\', '/'),
        "source_type": "wiki",
        "project": "wiki", # Chung project "wiki" để filter
        "date": str(date_added),
        "summary": summary,
        "sections": {
            "tags": tags,
            "aliases": aliases
        },
        "searchable_text": all_text,
        "title": title
    }

def build_index(full: bool = False):
    """
    Builds or updates the SQLite FTS5 search index.
    Returns a dict with processed, updated, and removed counts.
    """
    conn = brain_db.init_db(DB_FILE)
    
    if full:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM docs_fts")
        cursor.execute("DELETE FROM docs")
        conn.commit()

    processed_count = 0
    updated_count = 0
    current_files = set()
    
    if SESSIONS_DIR.exists():
        for filepath in SESSIONS_DIR.rglob("session-summary-*.md"):
            mtime = filepath.stat().st_mtime
            str_path = str(filepath.relative_to(WORKSPACE)).replace('\\', '/')
            current_files.add(str_path)
            
            if not full:
                last_mod = brain_db.get_last_modified(conn, str_path)
                if last_mod is not None and last_mod >= mtime:
                    continue
            
            try:
                content = filepath.read_text(encoding='utf-8')
                doc_data = parse_session_summary(filepath, content)
                brain_db.upsert_doc(conn, doc_data, mtime)
                updated_count += 1
            except Exception as e:
                print(f"Error parsing {filepath}: {e}")
            
            processed_count += 1

    if WIKI_DIR.exists():
        for filepath in WIKI_DIR.rglob("*.md"):
            mtime = filepath.stat().st_mtime
            str_path = str(filepath.relative_to(WORKSPACE)).replace('\\', '/')
            current_files.add(str_path)
            
            if not full:
                last_mod = brain_db.get_last_modified(conn, str_path)
                if last_mod is not None and last_mod >= mtime:
                    continue
                    
            try:
                content = filepath.read_text(encoding='utf-8')
                doc_data = parse_wiki_article(filepath, content)
                brain_db.upsert_doc(conn, doc_data, mtime)
                updated_count += 1
            except Exception as e:
                print(f"Error parsing {filepath}: {e}")
                
            processed_count += 1

    removed_count = brain_db.remove_docs(conn, current_files)
    conn.commit()
    conn.close()
    
    return {
        "processed": processed_count,
        "updated": updated_count,
        "removed": removed_count
    }

def main():
    parser = argparse.ArgumentParser(description="Build Session Search Index")
    parser.add_argument("--full", action="store_true", help="Rebuild entire index")
    args = parser.parse_args()
    
    res = build_index(full=args.full)
    print(f"Index updated. Processed {res['processed']} files, Updated {res['updated']} files, Removed {res['removed']} deleted files.")

if __name__ == "__main__":
    main()
