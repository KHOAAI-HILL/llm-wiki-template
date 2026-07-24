import os
import re
import json
import sys
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict, deque

WIKI_DIR = Path(__file__).parent
WORKSPACE = WIKI_DIR.parent
GRAPH_FILE = WIKI_DIR / "_graph.json"
VIEWER_FILE = WIKI_DIR / "_graph_viewer.html"
DB_FILE = WORKSPACE / "sessions" / "brain.db"

# Import brain_db module
sys.path.insert(0, str(WORKSPACE / "scripts"))
import brain_db

def clean_slug(link_text: str) -> str:
    """Clean link text to canonical kebab-case slug."""
    if not link_text:
        return ""
    # Strip wikilink brackets if present
    text = re.sub(r'^\[\[|\]\]$', '', link_text.strip())
    # Strip pipe aliases
    if '|' in text:
        text = text.split('|')[0]
    slug = text.strip().lower().replace(" ", "-")
    if slug.endswith('.md'):
        slug = slug[:-3]
    return slug

def extract_wikilinks(content):
    """Tìm tất cả [[link]] hoặc [[link|alias]] trong nội dung."""
    links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
    cleaned_links = []
    for link in links:
        s = clean_slug(link)
        if s:
            cleaned_links.append(s)
    return cleaned_links

def parse_frontmatter(content):
    """Trích xuất và parse khối YAML frontmatter bằng PyYAML."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)) or {}, content[match.end():]
        except yaml.YAMLError:
            pass
    return {}, content

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
                "predicate": edge.get("predicate", "references"),
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
            "value": n["link_count"] + 1
        })
        
    vis_edges = [
        {
            "from": e["source"],
            "to": e["target"],
            "label": e.get("predicate", "references"),
            "font": {"size": 9, "color": "#aaaaaa"}
        }
        for e in edges
    ]
    
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
    edges_list = []
    triples_list = []
    alias_map = {}
    
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
            
        try:
            content = md_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
            
        meta, body_content = parse_frontmatter(content)
        body_links = extract_wikilinks(body_content)
        
        node_id = md_file.stem.lower().replace(" ", "-")
        category = md_file.parent.name if md_file.parent != WIKI_DIR else "root"
        provenance = str(md_file.relative_to(WORKSPACE)).replace('\\', '/')
        title = meta.get("title", md_file.stem)
        
        # Entity resolution aliases map
        alias_map[node_id] = node_id
        alias_map[title.lower()] = node_id
        for alias in meta.get("aliases", []):
            if isinstance(alias, str) and alias.strip():
                alias_map[alias.strip().lower()] = node_id

        # Edge tracking map to avoid duplicate edges per source-target pair
        added_targets = set()
        
        # 1. Frontmatter triples (highest priority)
        custom_triples = meta.get("triples", [])
        if isinstance(custom_triples, list):
            for t in custom_triples:
                if isinstance(t, dict) and "target" in t:
                    tgt_slug = clean_slug(t["target"])
                    pred = t.get("predicate", "references").strip()
                    if tgt_slug:
                        edges_list.append({"source": node_id, "target": tgt_slug, "predicate": pred})
                        triples_list.append({
                            "source": node_id,
                            "predicate": pred,
                            "target": tgt_slug,
                            "provenance": provenance,
                            "extraction_method": "frontmatter_triple"
                        })
                        added_targets.add(tgt_slug)

        # 2. Related field in frontmatter
        related_links = meta.get("related", [])
        if isinstance(related_links, list):
            for rel in related_links:
                if isinstance(rel, str):
                    rel_slug = clean_slug(rel)
                    if rel_slug and rel_slug not in added_targets:
                        edges_list.append({"source": node_id, "target": rel_slug, "predicate": "references"})
                        triples_list.append({
                            "source": node_id,
                            "predicate": "references",
                            "target": rel_slug,
                            "provenance": provenance,
                            "extraction_method": "related_field"
                        })
                        added_targets.add(rel_slug)

        # 3. Wikilinks in body content
        for link_slug in body_links:
            if link_slug and link_slug not in added_targets:
                edges_list.append({"source": node_id, "target": link_slug, "predicate": "references"})
                triples_list.append({
                    "source": node_id,
                    "predicate": "references",
                    "target": link_slug,
                    "provenance": provenance,
                    "extraction_method": "body_wikilink"
                })
                added_targets.add(link_slug)

        nodes_dict[node_id] = {
            "id": node_id,
            "title": title,
            "category": category,
            "tags": meta.get("tags", []),
            "status": meta.get("status", "draft"),
            "link_count": len(added_targets)
        }

    nodes = list(nodes_dict.values())
    node_ids = {n["id"] for n in nodes}
    valid_edges = [e for e in edges_list if e["target"] in node_ids]
    valid_triples = [t for t in triples_list if t["target"] in node_ids]
    dangling_count = len(edges_list) - len(valid_edges)
    
    stats = compute_metrics(nodes, valid_edges)
    stats["dangling_links"] = dangling_count
    
    output = {
        "nodes": nodes,
        "edges": valid_edges,
        "insights": stats,
        "last_built": datetime.now().isoformat()
    }
    
    GRAPH_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    build_html_viewer(nodes, valid_edges)
    
    # Ghi dữ liệu vào SQLite DB (sessions/brain.db)
    conn = brain_db.init_db(DB_FILE)
    brain_db.save_graph_triples(conn, valid_triples)
    brain_db.save_entity_aliases(conn, alias_map)
    conn.close()

    print(f"Graph rebuilt & saved to SQLite: {stats['total_nodes']} nodes, {stats['total_edges']} edges ({len(valid_triples)} triples saved).")
    print(f"God Nodes: {[n['id'] for n in stats['god_nodes']]}")
    print(f"Aliases mapped: {len(alias_map)} entries.")
    print(f"Viewer generated at: {VIEWER_FILE.relative_to(WIKI_DIR.parent)}")

if __name__ == "__main__":
    main()

