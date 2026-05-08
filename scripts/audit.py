import os, re, glob
from pathlib import Path

# Thư mục chứa wiki
wiki_dir = Path.cwd() / 'wiki'
def run_audit():
    files = []
    for root, dirs, filenames in os.walk(wiki_dir):
        for f in filenames:
            if f.endswith('.md') and f not in ['index.md', 'glossary.md', 'ops-log.md']:
                files.append(os.path.join(root, f))

    valid_targets = [os.path.basename(f).replace('.md', '') for f in files]
    valid_targets += ['index', 'glossary', 'ops-log']

    report = {
        'total': len(files),
        'stubs': [],
        'bloated': [],
        'broken_links': [],
        'missing_frontmatter': []
    }

    link_pattern = re.compile(r'\[\[(.*?)\]\]')

    for fpath in files:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        basename = os.path.basename(fpath).replace('.md', '')
        lines = content.split('\n')
        
        if not content.startswith('---'):
            report['missing_frontmatter'].append(basename)
        else:
            if 'status: stub' in content:
                report['stubs'].append(basename)
                
        in_frontmatter = False
        content_lines = 0
        for line in lines:
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            if not in_frontmatter and line.strip() and not line.startswith('#'):
                content_lines += 1
                
        if content_lines > 120:
            report['bloated'].append(f'{basename} ({content_lines} lines)')
            
        links = link_pattern.findall(content)
        for link in links:
            target = link.split('|')[0].strip()
            if target.startswith('raw/') or target.startswith('outputs/'):
                continue
            target_base = os.path.basename(target).replace('.md', '')
            if target_base not in valid_targets:
                report['broken_links'].append(f'{basename} -> {target_base}')
                
    return report

def main():
    report = run_audit()
    print('--- WIKI AUDIT REPORT ---')
    print(f"Total files scanned: {report['total']}")
    print(f"Stubs remaining: {len(report['stubs'])}")
    print(f"Bloated files (>120 lines): {len(report['bloated'])}")
    for b in report['bloated']: print(f'  - {b}')
    print(f"Broken links: {len(report['broken_links'])}")
    for b in sorted(list(set(report['broken_links']))): print(f'  - {b}')
    print(f"Missing frontmatter: {len(report['missing_frontmatter'])}")

if __name__ == "__main__":
    main()
