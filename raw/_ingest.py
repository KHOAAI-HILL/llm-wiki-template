"""
Second Brain — Universal Ingest Script
Tự động phát hiện format và chuyển đổi thành .md chuẩn trong raw/

Usage:
    python raw/_ingest.py <path>           # Ingest 1 file hoặc 1 folder
    python raw/_ingest.py <path> --type tweets    # Force loại nguồn
    python raw/_ingest.py <path> --dry-run        # Xem preview, không tạo file

Supported formats:
    - Markdown (.md)
    - Plain text (.txt)
    - HTML (.html, .htm) 
    - PDF (.pdf) — cần PyMuPDF (fitz)
    - JSON (.json) — Day One, generic
    - CSV/TSV (.csv, .tsv)
    - Email (.eml)
    - Obsidian vault (folder of .md)
    - Notion export (folder of .md/.csv)
"""
import argparse
import csv
import email
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Thư mục gốc Second Brain
BRAIN_DIR = Path(__file__).parent.parent
RAW_DIR = BRAIN_DIR / "raw"

# Mapping loại nguồn → thư mục đích
SOURCE_TYPE_MAP = {
    "articles": RAW_DIR / "articles",
    "papers": RAW_DIR / "papers",
    "repos": RAW_DIR / "repos",
    "videos": RAW_DIR / "videos",
    "tweets": RAW_DIR / "tweets",
    "misc": RAW_DIR / "misc",
    "notes": RAW_DIR / "misc",    # Obsidian/Notion notes
    "emails": RAW_DIR / "misc",
    "data": RAW_DIR / "misc",
}


def slugify(text: str) -> str:
    """Convert text to kebab-case slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:80].strip('-')


def detect_format(filepath: Path) -> str:
    """Auto-detect file format."""
    suffix = filepath.suffix.lower()
    format_map = {
        '.md': 'markdown',
        '.txt': 'text',
        '.html': 'html',
        '.htm': 'html',
        '.pdf': 'pdf',
        '.json': 'json',
        '.csv': 'csv',
        '.tsv': 'tsv',
        '.eml': 'email',
    }
    return format_map.get(suffix, 'unknown')


def detect_source_type(filepath: Path, content: str = "") -> str:
    """Guess source type from filename and content."""
    name = filepath.stem.lower()
    
    # Keyword-based detection
    if any(kw in name for kw in ['tweet', 'twitter', 'thread', 'x-post']):
        return 'tweets'
    if any(kw in name for kw in ['paper', 'arxiv', 'research', 'journal']):
        return 'papers'
    if any(kw in name for kw in ['repo', 'github', 'readme']):
        return 'repos'
    if any(kw in name for kw in ['video', 'youtube', 'transcript']):
        return 'videos'
    if filepath.suffix.lower() == '.pdf':
        return 'papers'
    if filepath.suffix.lower() in ['.csv', '.tsv']:
        return 'data'
    if filepath.suffix.lower() == '.eml':
        return 'emails'
    
    return 'articles'  # Default


def extract_title(content: str, filepath: Path) -> str:
    """Extract title from content or filename."""
    # Try first heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    # Try first non-empty line
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('---'):
            return line[:100]
    
    # Fallback to filename
    return filepath.stem.replace('-', ' ').replace('_', ' ').title()


def build_frontmatter(title: str, source: str, source_type: str, 
                       date: str = None, tags: list = None, 
                       extra: dict = None) -> str:
    """Build YAML frontmatter string."""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    if tags is None:
        tags = [source_type]
    
    lines = [
        '---',
        f'title: "{title}"',
        f'source: "{source}"',
        f'date_added: {date}',
        f'tags: [{", ".join(tags)}]',
        'status: draft',
        f'summary: ""',
        '---',
    ]
    
    if extra:
        # Insert extra fields before closing ---
        extra_lines = [f'{k}: "{v}"' for k, v in extra.items()]
        lines = lines[:-1] + extra_lines + [lines[-1]]
    
    return '\n'.join(lines)


def strip_existing_frontmatter(content: str) -> str:
    """Remove existing YAML frontmatter if present."""
    if content.startswith('---'):
        match = re.match(r'^---\n.*?\n---\n?', content, re.DOTALL)
        if match:
            return content[match.end():]
    return content


# ============================================================
# Format-specific parsers
# ============================================================

def parse_markdown(filepath: Path) -> list[dict]:
    """Parse a single markdown file."""
    content = filepath.read_text(encoding='utf-8')
    body = strip_existing_frontmatter(content)
    title = extract_title(content, filepath)
    
    return [{
        'title': title,
        'body': body.strip(),
        'source': str(filepath),
        'date': datetime.now().strftime('%Y-%m-%d'),
    }]


def parse_text(filepath: Path) -> list[dict]:
    """Parse a plain text file."""
    content = filepath.read_text(encoding='utf-8')
    title = extract_title(content, filepath)
    
    return [{
        'title': title,
        'body': content.strip(),
        'source': str(filepath),
        'date': datetime.now().strftime('%Y-%m-%d'),
    }]


def parse_html(filepath: Path) -> list[dict]:
    """Parse HTML file — strip tags, keep text."""
    content = filepath.read_text(encoding='utf-8')
    
    # Extract title from <title> tag
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    title = title_match.group(1) if title_match else filepath.stem
    
    # Strip HTML tags (basic)
    text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Clean up whitespace
    
    return [{
        'title': title.strip(),
        'body': text.strip(),
        'source': str(filepath),
        'date': datetime.now().strftime('%Y-%m-%d'),
    }]


def parse_pdf(filepath: Path) -> list[dict]:
    """Parse PDF file — requires PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print(f"⚠️ PyMuPDF chưa cài. Chạy: pip install PyMuPDF")
        print(f"   Sẽ tạo file placeholder cho: {filepath.name}")
        return [{
            'title': filepath.stem.replace('-', ' ').replace('_', ' ').title(),
            'body': f"[PDF chưa extract — cần cài PyMuPDF]\n\nFile gốc: `{filepath}`",
            'source': str(filepath),
            'date': datetime.now().strftime('%Y-%m-%d'),
        }]
    
    doc = fitz.open(str(filepath))
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    
    title = doc.metadata.get('title', '') or filepath.stem.replace('-', ' ').title()
    body = '\n\n'.join(text_parts)
    
    return [{
        'title': title,
        'body': body.strip(),
        'source': str(filepath),
        'date': datetime.now().strftime('%Y-%m-%d'),
    }]


def parse_json(filepath: Path) -> list[dict]:
    """Parse JSON — supports Day One format and generic."""
    data = json.loads(filepath.read_text(encoding='utf-8'))
    entries = []
    
    # Day One format: {"entries": [...]}
    if isinstance(data, dict) and 'entries' in data:
        for entry in data['entries']:
            text = entry.get('text', '')
            date_str = entry.get('creationDate', '')
            date = date_str[:10] if date_str else datetime.now().strftime('%Y-%m-%d')
            tags = entry.get('tags', [])
            
            title = extract_title(text, filepath)
            
            entries.append({
                'title': title,
                'body': text.strip(),
                'source': str(filepath),
                'date': date,
                'extra': {'original_tags': ', '.join(tags)} if tags else {},
            })
    
    # Generic: list of objects
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                text = item.get('text', item.get('content', item.get('body', json.dumps(item, ensure_ascii=False))))
                title = item.get('title', item.get('name', f'Entry {i+1}'))
                date = item.get('date', item.get('created', datetime.now().strftime('%Y-%m-%d')))
                if len(date) > 10:
                    date = date[:10]
                
                entries.append({
                    'title': title,
                    'body': str(text).strip(),
                    'source': str(filepath),
                    'date': date,
                })
    
    # Single object
    elif isinstance(data, dict):
        text = json.dumps(data, indent=2, ensure_ascii=False)
        entries.append({
            'title': filepath.stem,
            'body': f"```json\n{text}\n```",
            'source': str(filepath),
            'date': datetime.now().strftime('%Y-%m-%d'),
        })
    
    return entries if entries else [{
        'title': filepath.stem,
        'body': json.dumps(data, indent=2, ensure_ascii=False),
        'source': str(filepath),
        'date': datetime.now().strftime('%Y-%m-%d'),
    }]


def parse_csv(filepath: Path, delimiter=',') -> list[dict]:
    """Parse CSV/TSV — each row becomes an entry or combine all."""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
    
    if not rows:
        return []
    
    # If few rows, create one combined entry
    if len(rows) <= 20:
        # Build markdown table
        headers = rows[0].keys()
        table_lines = ['| ' + ' | '.join(headers) + ' |']
        table_lines.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
        for row in rows:
            table_lines.append('| ' + ' | '.join(str(row.get(h, '')) for h in headers) + ' |')
        
        return [{
            'title': filepath.stem.replace('-', ' ').replace('_', ' ').title(),
            'body': '\n'.join(table_lines),
            'source': str(filepath),
            'date': datetime.now().strftime('%Y-%m-%d'),
        }]
    
    # Many rows: create one entry per row
    entries = []
    # Detect date and text columns
    date_col = next((c for c in rows[0].keys() if 'date' in c.lower()), None)
    text_col = next((c for c in rows[0].keys() if c.lower() in ['text', 'content', 'body', 'message', 'note']), None)
    
    for i, row in enumerate(rows):
        date = row.get(date_col, datetime.now().strftime('%Y-%m-%d')) if date_col else datetime.now().strftime('%Y-%m-%d')
        if text_col:
            body = row[text_col]
            title = body[:80] if body else f'Row {i+1}'
        else:
            body = '\n'.join(f"**{k}:** {v}" for k, v in row.items())
            title = f'{filepath.stem} — Row {i+1}'
        
        entries.append({
            'title': title,
            'body': body,
            'source': str(filepath),
            'date': str(date)[:10] if date else datetime.now().strftime('%Y-%m-%d'),
        })
    
    return entries


def parse_email(filepath: Path) -> list[dict]:
    """Parse .eml email file."""
    content = filepath.read_bytes()
    msg = email.message_from_bytes(content)
    
    subject = msg.get('Subject', filepath.stem)
    from_addr = msg.get('From', 'Unknown')
    to_addr = msg.get('To', 'Unknown')
    date_str = msg.get('Date', '')
    
    # Extract body
    body_text = ''
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body_text = part.get_payload(decode=True).decode('utf-8', errors='replace')
                break
    else:
        body_text = msg.get_payload(decode=True).decode('utf-8', errors='replace')
    
    # Parse date
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        date = dt.strftime('%Y-%m-%d')
    except:
        date = datetime.now().strftime('%Y-%m-%d')
    
    formatted = f"**From:** {from_addr}\n**To:** {to_addr}\n**Date:** {date_str}\n\n---\n\n{body_text}"
    
    return [{
        'title': subject,
        'body': formatted.strip(),
        'source': str(filepath),
        'date': date,
    }]


def parse_folder(folder: Path) -> list[dict]:
    """Parse a folder of files (Obsidian vault, Notion export, etc.)."""
    entries = []
    supported = {'.md', '.txt', '.html', '.htm', '.json', '.csv', '.tsv', '.eml', '.pdf'}
    
    for fp in sorted(folder.rglob('*')):
        if fp.is_file() and fp.suffix.lower() in supported:
            fmt = detect_format(fp)
            parser = PARSERS.get(fmt)
            if parser:
                try:
                    result = parser(fp)
                    entries.extend(result)
                except Exception as e:
                    print(f"  ⚠️ Lỗi khi parse {fp.name}: {e}")
    
    return entries


# Parser registry
PARSERS = {
    'markdown': parse_markdown,
    'text': parse_text,
    'html': parse_html,
    'pdf': parse_pdf,
    'json': parse_json,
    'csv': parse_csv,
    'tsv': lambda fp: parse_csv(fp, delimiter='\t'),
    'email': parse_email,
}


def write_entry(entry: dict, source_type: str, dry_run: bool = False) -> Path | None:
    """Write a single entry to raw/ as .md file."""
    dest_dir = SOURCE_TYPE_MAP.get(source_type, RAW_DIR / "misc")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    slug = slugify(entry['title'])
    if not slug:
        slug = f"entry-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    dest_file = dest_dir / f"{slug}.md"
    
    # Handle duplicates
    if dest_file.exists():
        counter = 2
        while dest_file.exists():
            dest_file = dest_dir / f"{slug}-{counter}.md"
            counter += 1
    
    # Build content
    extra = entry.get('extra', {})
    frontmatter = build_frontmatter(
        title=entry['title'],
        source=entry.get('source', 'unknown'),
        source_type=source_type,
        date=entry.get('date'),
        tags=[source_type],
        extra=extra,
    )
    
    full_content = f"{frontmatter}\n\n{entry['body']}"
    
    if dry_run:
        print(f"  [DRY RUN] Would create: {dest_file.relative_to(BRAIN_DIR)}")
        print(f"            Title: {entry['title'][:60]}")
        print(f"            Lines: {len(entry['body'].splitlines())}")
        return None
    
    dest_file.write_text(full_content, encoding='utf-8')
    return dest_file


def ingest(path: str, source_type: str = None, dry_run: bool = False):
    """Main ingest function."""
    filepath = Path(path).resolve()
    
    if not filepath.exists():
        print(f"❌ Không tìm thấy: {filepath}")
        sys.exit(1)
    
    print(f"📂 Đang ingest: {filepath}")
    
    # Folder mode
    if filepath.is_dir():
        print(f"   Mode: Folder scan")
        entries = parse_folder(filepath)
        if not source_type:
            source_type = 'notes'
    else:
        # Single file mode
        fmt = detect_format(filepath)
        print(f"   Format: {fmt}")
        
        if fmt == 'unknown':
            print(f"⚠️ Format không nhận diện được: {filepath.suffix}")
            print(f"   Copy thủ công vào raw/misc/ hoặc thử --type <loại>")
            sys.exit(1)
        
        parser = PARSERS.get(fmt)
        if not parser:
            print(f"❌ Chưa có parser cho format: {fmt}")
            sys.exit(1)
        
        entries = parser(filepath)
        if not source_type:
            source_type = detect_source_type(filepath)
    
    print(f"   Source type: {source_type}")
    print(f"   Entries found: {len(entries)}")
    print()
    
    if not entries:
        print("⚠️ Không tìm thấy entry nào.")
        return
    
    # Write entries
    created = []
    for entry in entries:
        result = write_entry(entry, source_type, dry_run)
        if result:
            created.append(result)
            rel = result.relative_to(BRAIN_DIR)
            print(f"  ✅ {rel} ({len(entry['body'].splitlines())} dòng)")
    
    # Summary
    print()
    if dry_run:
        print(f"🔍 [DRY RUN] Sẽ tạo {len(entries)} file. Chạy lại không có --dry-run để thực hiện.")
    else:
        print(f"✅ Đã nạp {len(created)} file vào raw/{source_type}/")
        print(f"💡 Chạy /compile để biên dịch vào wiki.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Second Brain — Universal Ingest Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python raw/_ingest.py notes.md                    # Ingest 1 file markdown
  python raw/_ingest.py ~/Downloads/paper.pdf       # Ingest PDF
  python raw/_ingest.py data.csv --type data        # Ingest CSV
  python raw/_ingest.py ~/obsidian-vault/           # Batch ingest folder
  python raw/_ingest.py export.json --type tweets   # Force tweet type
  python raw/_ingest.py big-folder/ --dry-run       # Preview only
        """
    )
    parser.add_argument('path', help='Đường dẫn file hoặc folder')
    parser.add_argument('--type', choices=list(SOURCE_TYPE_MAP.keys()),
                       help='Force loại nguồn (articles, papers, tweets, ...)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Chỉ preview, không tạo file')
    
    args = parser.parse_args()
    ingest(args.path, source_type=args.type, dry_run=args.dry_run)
