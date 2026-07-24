import sqlite3
import re
from pathlib import Path
from collections import deque

WORKSPACE = Path(__file__).resolve().parent.parent
DB_FILE = WORKSPACE / "sessions" / "brain.db"

def slugify(text: str) -> str:
    """Tạo kebab-case slug từ text."""
    if not text:
        return ""
    clean = text.strip().lower().replace(" ", "-")
    if clean.endswith(".md"):
        clean = clean[:-3]
    return clean

def resolve_entity(query: str, db_path: Path = DB_FILE) -> str:
    """Chuẩn hóa tên thực thể hoặc alias về canonical slug trong DB."""
    if not query:
        return ""
    
    slug_candidate = slugify(query)
    
    if not db_path.exists():
        return slug_candidate
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Kiểm tra trực tiếp bảng entity_aliases
    cursor.execute('SELECT canonical_id FROM entity_aliases WHERE alias = ?', (query.strip().lower(),))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row['canonical_id']
        
    cursor.execute('SELECT canonical_id FROM entity_aliases WHERE alias = ?', (slug_candidate,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row['canonical_id']
        
    # 2. Kiểm tra nếu slug_candidate trùng id trong docs
    cursor.execute('SELECT id FROM docs WHERE id LIKE ? OR id LIKE ?', (f"%/{slug_candidate}.md", f"%/{query}.md"))
    row = cursor.fetchone()
    if row:
        conn.close()
        return slug_candidate
        
    conn.close()
    return slug_candidate

def get_subgraph(seed_entity: str, hops: int = 2, db_path: Path = DB_FILE) -> dict:
    """Duyệt đồ thị từ nút seed_entity bằng thuật toán BFS trong k bước nhảy (hops)."""
    canonical_seed = resolve_entity(seed_entity, db_path)
    
    if not db_path.exists():
        return {"error": "Database chưa tồn tại. Chạy python wiki/_build_graph.py trước.", "seed": canonical_seed, "triples": []}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    visited_nodes = {canonical_seed}
    frontier = {canonical_seed}
    collected_triples = []
    seen_triple_keys = set()

    for _ in range(hops):
        if not frontier:
            break
        next_frontier = set()
        
        # Lấy tất cả cạnh hướng ra và hướng vào của frontier
        placeholders = ','.join('?' * len(frontier))
        nodes_list = list(frontier)
        
        query_sql = f'''
            SELECT source_id, predicate, target_id, provenance, extraction_method 
            FROM graph_triples 
            WHERE source_id IN ({placeholders}) OR target_id IN ({placeholders})
        '''
        cursor.execute(query_sql, nodes_list + nodes_list)
        rows = cursor.fetchall()

        for row in rows:
            src = row['source_id']
            pred = row['predicate']
            tgt = row['target_id']
            triple_key = (src, pred, tgt)

            if triple_key not in seen_triple_keys:
                seen_triple_keys.add(triple_key)
                collected_triples.append({
                    "source": src,
                    "predicate": pred,
                    "target": tgt,
                    "provenance": row['provenance'],
                    "method": row['extraction_method']
                })

            if src not in visited_nodes:
                visited_nodes.add(src)
                next_frontier.add(src)
            if tgt not in visited_nodes:
                visited_nodes.add(tgt)
                next_frontier.add(tgt)

        frontier = next_frontier

    conn.close()
    
    return {
        "seed": canonical_seed,
        "input_query": seed_entity,
        "hops": hops,
        "total_nodes": len(visited_nodes),
        "total_triples": len(collected_triples),
        "nodes": sorted(list(visited_nodes)),
        "triples": collected_triples
    }

def serialize_subgraph(subgraph_data: dict) -> str:
    """Chuyển đổi subgraph dict thành chuỗi text gọn cho LLM đọc."""
    if "error" in subgraph_data:
        return f"Lỗi: {subgraph_data['error']}"
        
    seed = subgraph_data.get("seed", "unknown")
    triples = subgraph_data.get("triples", [])
    
    if not triples:
        return f"Không tìm thấy liên kết đồ thị nào cho nút '{seed}' trong bán kính {subgraph_data.get('hops', 2)} bước."

    lines = [f"=== Subgraph từ '{seed}' ({subgraph_data.get('hops', 2)}-hop, {len(triples)} cạnh) ==="]
    
    # Sort triples để nhất quán
    sorted_triples = sorted(triples, key=lambda x: (x['source'], x['predicate'], x['target']))
    
    for t in sorted_triples:
        lines.append(f"({t['source']}) --[{t['predicate']}]--> ({t['target']})")
        
    return "\n".join(lines)

def find_path(entity_a: str, entity_b: str, max_depth: int = 4, db_path: Path = DB_FILE) -> dict:
    """Tìm đường đi ngắn nhất giữa 2 thực thể bằng BFS."""
    start_node = resolve_entity(entity_a, db_path)
    end_node = resolve_entity(entity_b, db_path)
    
    if not db_path.exists():
        return {"error": "Database chưa tồn tại."}

    if start_node == end_node:
        return {"start": start_node, "end": end_node, "path": [start_node], "triples": []}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Queue chứa tuple: (current_node, path_nodes, path_triples)
    queue = deque([(start_node, [start_node], [])])
    visited = {start_node}

    found_path_triples = None
    found_path_nodes = None

    while queue:
        curr_node, path_nodes, path_triples = queue.popleft()

        if len(path_nodes) - 1 >= max_depth:
            continue

        cursor.execute('''
            SELECT source_id, predicate, target_id 
            FROM graph_triples 
            WHERE source_id = ? OR target_id = ?
        ''', (curr_node, curr_node))
        
        rows = cursor.fetchall()
        for row in rows:
            src = row['source_id']
            pred = row['predicate']
            tgt = row['target_id']
            next_node = tgt if src == curr_node else src

            if next_node not in visited:
                visited.add(next_node)
                new_nodes = path_nodes + [next_node]
                new_triples = path_triples + [{"source": src, "predicate": pred, "target": tgt}]

                if next_node == end_node:
                    found_path_nodes = new_nodes
                    found_path_triples = new_triples
                    queue.clear()
                    break

                queue.append((next_node, new_nodes, new_triples))

    conn.close()

    if found_path_triples:
        serialized_lines = [f"({t['source']}) --[{t['predicate']}]--> ({t['target']})" for t in found_path_triples]
        return {
            "start": start_node,
            "end": end_node,
            "found": True,
            "length": len(found_path_triples),
            "nodes": found_path_nodes,
            "triples": found_path_triples,
            "serialized": "\n".join(serialized_lines)
        }
    else:
        return {
            "start": start_node,
            "end": end_node,
            "found": False,
            "message": f"Không tìm thấy đường đi giữa '{start_node}' và '{end_node}' trong khoảng cách {max_depth} bước."
        }

if __name__ == "__main__":
    sub = get_subgraph("hermes-agent", hops=2)
    print(serialize_subgraph(sub))
