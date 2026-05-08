import os
import re
import sys
from collections import defaultdict

from pathlib import Path
WIKI_DIR = Path.cwd() / 'wiki'
EXCLUDE_FILES = ['index.md', 'glossary.md', 'ops-log.md']
INTERNAL_FILES = ['_purpose', '_ops_log', 'dashboard', 'overview', 'operations-log']

link_pattern = re.compile(r'\[\[(.*?)\]\]')

def get_frontmatter_tags(content):
    in_fm = False
    tags = set()
    for line in content.split('\n'):
        if line.strip() == '---':
            in_fm = not in_fm
            if not in_fm:
                break
            continue
        if in_fm and line.startswith('tags:'):
            tag_str = line.split(':', 1)[1].strip().strip('[]')
            extracted = [t.strip().lower() for t in tag_str.split(',') if t.strip()]
            tags.update(extracted)
    return tags

def get_frontmatter_end_line(lines):
    in_fm = False
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_fm:
                in_fm = True
            else:
                return i
    return -1

def find_orphans(apply_mode=False):
    files = []
    for root, dirs, filenames in os.walk(WIKI_DIR):
        for f in filenames:
            if f.endswith('.md') and f not in EXCLUDE_FILES:
                files.append(os.path.join(root, f))
                
    nodes = {}
    in_degree = defaultdict(int)
    
    # 1. Parse all files
    for fpath in files:
        basename = os.path.basename(fpath).replace('.md', '')
        folder = os.path.basename(os.path.dirname(fpath))
        
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        tags = get_frontmatter_tags(content)
        links = link_pattern.findall(content)
        
        nodes[basename] = {
            'fpath': fpath,
            'tags': tags,
            'folder': folder,
            'content': content,
            'lines': content.split('\n')
        }
        
        for link in links:
            target = link.split('|')[0].strip()
            if target.startswith('raw/') or target.startswith('outputs/'):
                continue
            target_base = os.path.basename(target).replace('.md', '')
            in_degree[target_base] += 1

    # 2. Identify orphans
    orphans = []
    for n in nodes:
        if n not in INTERNAL_FILES and in_degree[n] == 0:
            orphans.append(n)
            
    orphans.sort()
    
    # 3. Match orphans to parents
    parent_assignments = defaultdict(list)
    potential_parents = [n for n in nodes if n not in INTERNAL_FILES and n not in orphans]
    
    for orphan in orphans:
        orphan_node = nodes[orphan]
        best_parent = None
        best_score = -1
        
        for parent in potential_parents:
            if len(parent_assignments[parent]) >= 5:
                continue
                
            parent_node = nodes[parent]
            score = 0
            
            shared_tags = orphan_node['tags'].intersection(parent_node['tags'])
            score += len(shared_tags) * 3
            
            if in_degree[parent] >= 5:
                score += 5
                
            if orphan_node['folder'] == parent_node['folder']:
                score += 2
                
            if score > best_score:
                best_score = score
                best_parent = parent
                
        if best_parent:
            parent_assignments[best_parent].append(orphan)
            
    # 4. Apply
    modified_count = 0
    for parent, assigned_orphans in parent_assignments.items():
        if not assigned_orphans:
            continue
        modified_count += 1
            
        if apply_mode:
            p_node = nodes[parent]
            lines = p_node['lines']
            fm_end = get_frontmatter_end_line(lines)
            
            if fm_end != -1:
                related_idx = -1
                for i in range(1, fm_end):
                    if lines[i].startswith('related:'):
                        related_idx = i
                        break
                        
                new_lines = []
                if related_idx != -1:
                    for i in range(len(lines)):
                        new_lines.append(lines[i])
                        if i == related_idx:
                            for o in assigned_orphans:
                                new_lines.append(f'  - "[[{o}]]"')
                else:
                    for i in range(len(lines)):
                        if i == fm_end:
                            new_lines.append('related:')
                            for o in assigned_orphans:
                                new_lines.append(f'  - "[[{o}]]"')
                        new_lines.append(lines[i])
                
                with open(p_node['fpath'], 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                    
    return {
        "orphans": len(orphans),
        "matched": sum(len(o) for o in parent_assignments.values()),
        "modified_parents": modified_count,
        "assignments": dict(parent_assignments),
        "nodes_info": {n: {"tags": list(v["tags"]), "hub": in_degree[n] >= 5} for n, v in nodes.items()}
    }

def main():
    apply_mode = '--apply' in sys.argv
    res = find_orphans(apply_mode)
    
    print(f"Total real orphans: {res['orphans']}")
    print("\n--- MATCHING RESULTS ---")
    
    nodes = res.get("nodes_info", {})
    for parent, assigned_orphans in res["assignments"].items():
        hub_str = nodes.get(parent, {}).get("hub", False)
        tags_str = ", ".join(nodes.get(parent, {}).get("tags", []))
        print(f"\nParent: {parent} (Hub: {hub_str}, Tags: {tags_str})")
        
        for o in assigned_orphans:
            p_tags = set(nodes.get(parent, {}).get("tags", []))
            o_tags = set(nodes.get(o, {}).get("tags", []))
            shared = o_tags.intersection(p_tags)
            print(f"  <- {o} (Shared tags: {len(shared)})")
            
    print(f"\nTotal parents modified: {res['modified_parents']}")
    if not apply_mode:
        print("\n[!] DRY RUN ONLY. Run with --apply to write changes.")
    else:
        print("\n[+] APPLIED changes to markdown files.")

if __name__ == '__main__':
    main()
