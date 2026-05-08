import sqlite3
import json
from pathlib import Path

def init_db(db_path: Path):
    """Khởi tạo cấu trúc Database và các bảng FTS5."""
    # Đảm bảo thư mục tồn tại
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Bảng docs chứa nội dung gốc
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS docs (
            id TEXT PRIMARY KEY,
            type TEXT,
            project TEXT,
            date TEXT,
            title TEXT,
            summary TEXT,
            searchable_text TEXT,
            tags TEXT,
            aliases TEXT,
            last_modified REAL
        )
    ''')

    # Bảng FTS5 contentless-delete mode
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
            id UNINDEXED,
            title,
            searchable_text,
            content='',
            contentless_delete=1,
            tokenize='unicode61'
        )
    ''')

    conn.commit()
    return conn

def get_last_modified(conn: sqlite3.Connection, doc_id: str):
    """Lấy thời gian sửa đổi cuối cùng của một file từ DB."""
    cursor = conn.cursor()
    cursor.execute('SELECT last_modified FROM docs WHERE id = ?', (doc_id,))
    row = cursor.fetchone()
    return row['last_modified'] if row else None

def upsert_doc(conn: sqlite3.Connection, doc_dict: dict, mtime: float):
    """Cập nhật hoặc thêm mới một tài liệu vào DB."""
    cursor = conn.cursor()
    
    doc_id = doc_dict['file_path']
    title = doc_dict.get('title', Path(doc_id).stem.replace('-', ' '))
    tags = json.dumps(doc_dict.get('sections', {}).get('tags', []), ensure_ascii=False)
    aliases = json.dumps(doc_dict.get('sections', {}).get('aliases', []), ensure_ascii=False)
    
    # Bắt đầu Transaction
    try:
        # Xóa bản ghi cũ trong bảng docs_fts (nếu có)
        cursor.execute('DELETE FROM docs_fts WHERE rowid = (SELECT rowid FROM docs WHERE id = ?)', (doc_id,))
        
        # INSERT OR REPLACE vào bảng docs
        cursor.execute('''
            INSERT OR REPLACE INTO docs 
            (id, type, project, date, title, summary, searchable_text, tags, aliases, last_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            doc_id,
            doc_dict['source_type'],
            doc_dict['project'],
            doc_dict['date'],
            title,
            doc_dict['summary'],
            doc_dict['searchable_text'],
            tags,
            aliases,
            mtime
        ))
        
        # Lấy rowid vừa insert
        new_rowid = cursor.lastrowid
        
        # Insert vào bảng docs_fts
        cursor.execute('''
            INSERT INTO docs_fts(rowid, id, title, searchable_text)
            VALUES (?, ?, ?, ?)
        ''', (new_rowid, doc_id, title, doc_dict['searchable_text']))
        
    except Exception as e:
        print(f"Error upserting doc {doc_id}: {e}")
        conn.rollback()
        raise

def remove_docs(conn: sqlite3.Connection, valid_ids: set):
    """Xóa các bản ghi không còn tồn tại trên file system."""
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, rowid FROM docs')
    rows = cursor.fetchall()
    
    ids_to_remove = []
    rowids_to_remove = []
    
    for row in rows:
        if row['id'] not in valid_ids:
            ids_to_remove.append(row['id'])
            rowids_to_remove.append(row['rowid'])
            
    if ids_to_remove:
        try:
            # Xóa khỏi docs_fts trước
            for rowid in rowids_to_remove:
                cursor.execute('DELETE FROM docs_fts WHERE rowid = ?', (rowid,))
                
            # Xóa khỏi docs
            for doc_id in ids_to_remove:
                cursor.execute('DELETE FROM docs WHERE id = ?', (doc_id,))
                
        except Exception as e:
            print(f"Error removing docs: {e}")
            conn.rollback()
            raise
            
    return len(ids_to_remove)
