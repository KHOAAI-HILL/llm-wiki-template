import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, deque

WIKI_DIR = Path(__file__).parent
GRAPH_FILE = WIKI_DIR / "_graph.json"
VIEWER_FILE = WIKI_DIR / "_graph_viewer.html"

def extract_wikilinks(content):
    """Tìm tất cả [[link]] hoặc [[link|alias]] trong nội dung."""
    links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
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
                
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                
                if val.startswith('[') and val.endswith(']'):
                    items = [i.strip().strip('"').strip("'") for i in val[1:-1].split(',')]
                    meta[key] = [i for i in items if i]
                else:
                    meta[key] = val
    return meta

def compute_metrics(nodes, edges):
    """Tính toán các chỉ số graph: God nodes, surprising connections, isolated, clusters."""
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    adj = defaultdict(set)
    node_categories = {n["id"]: n["category"] for n in nodes}
    node_ids = {n["id"] for n in nodes}
    
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        out_degree[source] += 1
        in_degree[target] += 1
        adj[source].add(target)
        adj[target].add(source)

    # God nodes (top 5 bài có in_degree cao nhất)
    hubs = sorted([(n, d) for n, d in in_degree.items() if n in node_ids], key=lambda x: x[1], reverse=True)[:5]
    god_nodes = [{"id": n, "in_degree": d, "out_degree": out_degree[n]} for n, d in hubs]
    
    # Surprising Connections (Edges between different categories)
    surprising_edges = []
    for edge in edges:
        src_cat = node_categories.get(edge["source"])
        tgt_cat = node_categories.get(edge["target"])
        if src_cat and tgt_cat and src_cat != tgt_cat and src_cat != "root" and tgt_cat != "root":
            surprising_edges.append({
                "source": edge["source"],
                "target": edge["target"],
                "reason": f"Cross-category link ({src_cat} -> {tgt_cat})"
            })
    
    # Isolated nodes
    isolated = [n["id"] for n in nodes if out_degree[n["id"]] == 0 and in_degree[n["id"]] == 0]
    
    # Clusters (Connected Components)
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
            if len(comp) > 1:
                clusters.append(comp)
                
    clusters = sorted(clusters, key=len, reverse=True)
    cluster_stats = [{"size": len(c), "members": c[:5] + (["..."] if len(c) > 5 else [])} for c in clusters]
    
    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "god_nodes": god_nodes,
        "surprising_connections": surprising_edges[:10], # Top 10
        "isolated_nodes": isolated,
        "clusters": cluster_stats
    }

def build_html_viewer(nodes, edges):
    """Tạo file HTML tĩnh sử dụng vis-network để vẽ đồ thị."""
    # Convert nodes to vis.js format
    vis_nodes = []
    for n in nodes:
        group = n["category"]
        if group == "root":
            color = "#97C2FC"
        elif group == "concepts":
            color = "#FB7E81"
        elif group == "tools":
            color = "#7BE141"
        elif group == "people":
            color = "#EB7DF4"
        else:
            color = "#FFC0CB"
            
        vis_nodes.append({
            "id": n["id"],
            "label": n["title"],
            "title": f"Category: {group}<br>Links: {n['link_count']}",
            "color": color,
            "group": group,
            "value": n["link_count"] + 1 # Tự động scale độ lớn dựa vào số link
        })
        
    vis_edges = [{"from": e["source"], "to": e["target"]} for e in edges]
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>Second Brain - Knowledge Graph</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; font-family: sans-serif; background-color: #1e1e1e; color: white; overflow: hidden; }}
        #mynetwork {{ width: 100%; height: 100vh; border: none; outline: none; }}
        #legend {{ position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); z-index: 100; }}
        .legend-item {{ margin-bottom: 8px; display: flex; align-items: center; font-size: 14px; }}
        .color-box {{ width: 16px; height: 16px; margin-right: 10px; display: inline-block; border-radius: 50%; }}
        h3 {{ margin-top: 0; font-size: 16px; border-bottom: 1px solid #444; padding-bottom: 8px; margin-bottom: 12px; }}
    </style>
</head>
<body>
    <div id="legend">
        <h3>Second Brain Graph</h3>
        <div class="legend-item"><span class="color-box" style="background:#FB7E81;"></span>Concepts</div>
        <div class="legend-item"><span class="color-box" style="background:#7BE141;"></span>Tools</div>
        <div class="legend-item"><span class="color-box" style="background:#EB7DF4;"></span>People</div>
        <div class="legend-item"><span class="color-box" style="background:#97C2FC;"></span>Root</div>
    </div>
    <div id="mynetwork"></div>
    <script type="text/javascript">
        var nodes = new vis.DataSet({json.dumps(vis_nodes)});
        var edges = new vis.DataSet({json.dumps(vis_edges)});
        var container = document.getElementById('mynetwork');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            nodes: {{
                shape: 'dot',
                scaling: {{
                    min: 10,
                    max: 40,
                    label: {{
                        enabled: true,
                        min: 11,
                        max: 20
                    }}
                }},
                font: {{ 
                    color: '#e0e0e0', 
                    size: 12, 
                    strokeWidth: 3, 
                    strokeColor: '#1e1e1e' 
                }}
            }},
            edges: {{
                color: {{ color: '#555555', opacity: 0.4 }},
                arrows: {{ to: {{ scaleFactor: 0.5 }} }},
                smooth: {{ type: 'continuous' }}
            }},
            physics: {{
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {{
                    gravitationalConstant: -120,
                    centralGravity: 0.015,
                    springConstant: 0.05,
                    springLength: 150,
                    damping: 0.4,
                    avoidOverlap: 0.6
                }},
                stabilization: {{ iterations: 200 }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                hideEdgesOnDrag: true
            }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""
    VIEWER_FILE.write_text(html_template, encoding="utf-8")

def main():
    nodes_dict = {}
    edges = []
    
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
        
        # Dùng dictionary để tự động ghi đè/deduplicate ID nếu có 2 file cùng tên
        nodes_dict[node_id] = {
            "id": node_id,
            "title": meta.get("title", md_file.stem),
            "category": category,
            "tags": meta.get("tags", []),
            "status": meta.get("status", "draft"),
            "link_count": len(links)
        }
        
        for link in links:
            edges.append({"source": node_id, "target": link, "type": "wikilink"})
    
    nodes = list(nodes_dict.values())
    
    node_ids = {n["id"] for n in nodes}
    valid_edges = [e for e in edges if e["target"] in node_ids]
    dangling_count = len(edges) - len(valid_edges)
    
    stats = compute_metrics(nodes, valid_edges)
    stats["dangling_links"] = dangling_count
    
    output = {
        "nodes": nodes,
        "edges": edges,
        "insights": stats,
        "last_built": datetime.now().isoformat()
    }
    
    GRAPH_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    build_html_viewer(nodes, valid_edges)
    
    print(f"Graph rebuilt: {stats['total_nodes']} nodes, {stats['total_edges']} edges, {len(stats['isolated_nodes'])} isolated.")
    print(f"God Nodes: {[n['id'] for n in stats['god_nodes']]}")
    print(f"Found {len(stats['surprising_connections'])} surprising connections.")
    print(f"Viewer generated at: {VIEWER_FILE.relative_to(WIKI_DIR.parent)}")

if __name__ == "__main__":
    main()
