import json
import argparse
import re
import sqlite3
from pathlib import Path
import brain_db

WORKSPACE = Path.cwd()
DB_FILE = WORKSPACE / "sessions" / "brain.db"

def extract_context(text, query_terms, context_chars=100):
    """Trích xuất đoạn văn bản chứa từ khóa."""
    if not text:
        return ""
        
    lower_text = text.lower()
    best_idx = -1
    
    for term in query_terms:
        # Loại bỏ dấu ngoặc kép khỏi term nếu có
        clean_term = term.replace('"', '')
        idx = lower_text.find(clean_term)
        if idx != -1:
            best_idx = idx
            break
            
    if best_idx == -1:
        return ""
        
    start = max(0, best_idx - context_chars)
    end = min(len(text), best_idx + len(query_terms[0].replace('"', '')) + context_chars)
    
    context = text[start:end].replace('\n', ' ').strip()
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."
        
    return context

def run_search(query: str, project: str = None, source_type: str = None, limit: int = 10):
    """
    Tìm kiếm FTS5 và trả về danh sách kết quả dạng dict.
    Nếu có lỗi kết nối hoặc truy vấn sai, raise Exception.
    """
    if not DB_FILE.exists():
        raise FileNotFoundError("Database not found. Run 'brain.py index' first.")

    raw_terms = query.split()
    query_terms = [t.lower() for t in raw_terms]
    
    safe_terms = [re.sub(r'[^a-zA-Z0-9_\x80-\xFF\s]', '', t) for t in query_terms]
    safe_terms = [t for t in safe_terms if t]
    
    if not safe_terms:
        return []

    fts_query = ' AND '.join(f'"{term}"' for term in safe_terms)

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    sql = '''
        SELECT d.id, d.type, d.project, d.date, d.title, d.summary,
               d.searchable_text, -bm25(docs_fts) as score
        FROM docs_fts f
        JOIN docs d ON d.rowid = f.rowid
        WHERE docs_fts MATCH ?
        AND (? IS NULL OR d.type = ?)
        AND (? IS NULL OR d.project = ?)
        ORDER BY score DESC
        LIMIT ?
    '''
    
    try:
        cursor.execute(sql, (
            fts_query,
            source_type, source_type,
            project, project,
            limit
        ))
        rows = cursor.fetchall()
    except Exception as e:
        conn.close()
        raise e

    results = []
    raw_scores = []
    
    for row in rows:
        context = extract_context(row['searchable_text'], safe_terms)
        raw_scores.append(row['score'])
        results.append({
            "file_path": row['id'],
            "project": row['project'],
            "date": row['date'],
            "source_type": row['type'],
            "relevance_score": row['score'],
            "match_context": context,
            "summary": row['summary']
        })
    
    if raw_scores:
        max_score = max(raw_scores) if max(raw_scores) > 0 else 1
        for i, res in enumerate(results):
            res["relevance_score"] = round((raw_scores[i] / max_score) * 100, 2)
            
    conn.close()
    return results

def main():
    parser = argparse.ArgumentParser(description="Search Session and Wiki Index (SQLite FTS5)")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--project", help="Filter by project name")
    parser.add_argument("--source", choices=["session", "wiki"], help="Filter by source type")
    parser.add_argument("--limit", type=int, default=10, help="Max results to return")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    try:
        results = run_search(args.query, args.project, args.source, args.limit)
    except FileNotFoundError as e:
        if args.format == "json":
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
        return
    except Exception as e:
        if args.format == "json":
            print(json.dumps({"error": f"FTS5 Query Error: {e}"}))
        else:
            print(f"Lỗi truy vấn tìm kiếm: {e}")
        return
    
    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print(f"Không tìm thấy kết quả cho '{args.query}'")
            return
            
        print(f"--- Tìm thấy {len(results)} kết quả cho '{args.query}' ---")
        for i, res in enumerate(results, 1):
            print(f"\n{i}. [{res['source_type'].upper()}] {res['file_path']} (Score: {res['relevance_score']})")
            print(f"   Date: {res['date']} | Project: {res['project']}")
            print(f"   Summary: {res['summary']}")
            print(f"   Match: {res['match_context']}")

if __name__ == "__main__":
    main()
