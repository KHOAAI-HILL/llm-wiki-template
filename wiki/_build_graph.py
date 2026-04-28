import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, deque

WIKI_DIR = Path(__file__).parent
GRAPH_FILE = WIKI_DIR / "_graph.json"

def extract_wikilinks(content):
    """Tìm tất cả [[link]] hoặc [[link|alias]] trong nội dung."""
    links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
    # Chuẩn hóa link: chữ thường, đổi khoảng trắng thành gạch nối, bỏ .md nếu có
    cleaned_links = []
    for link in links:
        l = link.strip().lower().replace(" ", "-")
        if l.endswith('.md'):
            l = l[:-3]
        if l:
            cleaned_links.append(l)
    return cleaned_links

def parse_frontmatter(content):
    """Trích xuất YAML frontmatter bằng regex để tránh dependency PyYAML."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    meta = {}
    if match:
        lines = match.group(1).strip().split('\n')
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip()
                val = parts[1].strip()
                
                # Bỏ dấu nháy kép/đơn nếu có
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                
                # Xử lý list dạng [a, b, c]
                if val.startswith('[') and val.endswith(']'):
                    items = [i.strip().strip('"').strip("'") for i in val[1:-1].split(',')]
                    meta[key] = [i for i in items if i]
                else:
                    meta[key] = val
    return meta

def compute_metrics(nodes, edges):
    """Tính toán các chỉ số graph: hub score, isolated nodes, clusters."""
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    adj = defaultdict(set)
    
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        out_degree[source] += 1
        in_degree[target] += 1
        adj[source].add(target)
        adj[target].add(source)

    node_ids = {n["id"] for n in nodes}
    
    # Hub nodes (top 5 bài có in_degree cao nhất)
    hubs = sorted([(n, d) for n, d in in_degree.items() if n in node_ids], key=lambda x: x[1], reverse=True)[:5]
    hub_nodes = [{"id": n, "in_degree": d, "out_degree": out_degree[n]} for n, d in hubs]
    
    # Isolated nodes (0 in, 0 out)
    isolated = [n["id"] for n in nodes if out_degree[n["id"]] == 0 and in_degree[n["id"]] == 0]
    
    # Clusters (Connected Components bằng BFS)
    visited = set()
    clusters = []
    
    for n_id in node_ids:
        if n_id not in visited:
            q = deque([n_id])
            visited.add(n_id)
            comp = []
            while q:
                curr = q.popleft()
                comp.append(curr)
                for neighbor in adj[curr]:
                    if neighbor in node_ids and neighbor not in visited:
                        visited.add(neighbor)
                        q.append(neighbor)
            # Chỉ ghi nhận cluster nếu có >= 2 bài
            if len(comp) > 1:
                clusters.append(comp)
                
    clusters = sorted(clusters, key=len, reverse=True)
    cluster_stats = [{"size": len(c), "members": c[:5] + (["..."] if len(c) > 5 else [])} for c in clusters]
    
    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "hub_nodes": hub_nodes,
        "isolated_nodes": isolated,
        "clusters": cluster_stats
    }

def main():
    nodes = []
    edges = []
    
    # Quét toàn bộ file .md trong wiki, trừ thư mục/file ẩn (như _index.md)
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
            
        try:
            content = md_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
            
        meta = parse_frontmatter(content)
        links = extract_wikilinks(content)
        
        node_id = md_file.stem.lower().replace(" ", "-")
        category = md_file.parent.name if md_file.parent != WIKI_DIR else "root"
        
        nodes.append({
            "id": node_id,
            "title": meta.get("title", md_file.stem),
            "category": category,
            "tags": meta.get("tags", []),
            "status": meta.get("status", "draft"),
            "link_count": len(links)
        })
        
        for link in links:
            edges.append({"source": node_id, "target": link, "type": "wikilink"})
    
    # Filter: chỉ giữ edges trỏ đến node thực sự tồn tại trong wiki
    node_ids = {n["id"] for n in nodes}
    valid_edges = [e for e in edges if e["target"] in node_ids]
    dangling_count = len(edges) - len(valid_edges)
    
    # Tính metrics trên valid edges
    stats = compute_metrics(nodes, valid_edges)
    stats["dangling_links"] = dangling_count
    
    # Tạo output object
    output = {
        "nodes": nodes,
        "edges": edges,
        "insights": stats,
        "last_built": datetime.now().isoformat()
    }
    
    # Ghi file
    GRAPH_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Graph rebuilt: {stats['total_nodes']} nodes, {stats['total_edges']} edges, {len(stats['isolated_nodes'])} isolated, {stats.get('dangling_links', 0)} dangling filtered.")

if __name__ == "__main__":
    main()
