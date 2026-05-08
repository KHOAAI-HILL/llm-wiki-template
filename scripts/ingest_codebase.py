import os
import ast
import argparse
import datetime
from pathlib import Path

WORKSPACE = Path.cwd()
RAW_REPOS_DIR = WORKSPACE / "raw" / "repos"

def parse_python_file(filepath):
    try:
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content, filename=str(filepath))
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None

    classes = []
    functions = []
    imports = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
            docstring = ast.get_docstring(node)
            classes.append({
                "name": node.name,
                "methods": methods,
                "doc": docstring.strip() if docstring else "No docstring"
            })
        elif isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            functions.append({
                "name": node.name,
                "doc": docstring.strip() if docstring else "No docstring"
            })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")

    return {
        "classes": classes,
        "functions": functions,
        "imports": imports
    }

def generate_markdown(repo_name, module_name, data, filepath):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Generate Frontmatter
    md = f"""---
title: "{repo_name.capitalize()} - {module_name.capitalize()} Architecture"
source: "local://{filepath}"
date_added: {date_str}
tags: [repo, code-architecture, python]
aliases: ["{repo_name}-{module_name}"]
status: draft
summary: "AST extraction for module {module_name} in {repo_name}"
---

## Tổng Quan Module
Module `{module_name}` thuộc repository `{repo_name}`.

### Dependencies (Imports)
"""
    if data['imports']:
        for imp in set(data['imports']):
            md += f"- `{imp}`\n"
    else:
        md += "- Không có external imports\n"

    md += "\n## Cấu Trúc Classes\n"
    if data['classes']:
        for cls in data['classes']:
            md += f"### Class `{cls['name']}`\n"
            md += f"**Mô tả:** {cls['doc']}\n\n"
            if cls['methods']:
                md += "**Methods:**\n"
                for m in cls['methods']:
                    md += f"- `{m}()`\n"
            md += "\n"
    else:
        md += "- Không có classes\n"

    md += "\n## Cấu Trúc Functions\n"
    if data['functions']:
        for func in data['functions']:
            md += f"### Function `{func['name']}`\n"
            md += f"**Mô tả:** {func['doc']}\n\n"
    else:
        md += "- Không có standalone functions\n"

    return md

def ingest_repo(repo_path_str: str):
    repo_path = Path(repo_path_str).resolve()
    
    if not repo_path.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_path}")

    RAW_REPOS_DIR.mkdir(parents=True, exist_ok=True)

    if repo_path.is_file() and repo_path.suffix == '.py':
        files_to_process = [repo_path]
        repo_name = repo_path.parent.name
    else:
        files_to_process = list(repo_path.rglob("*.py"))
        repo_name = repo_path.name

    processed_count = 0
    generated_files = []
    
    for filepath in files_to_process:
        if "venv" in filepath.parts or "__pycache__" in filepath.parts or filepath.name.startswith("__"):
            continue

        data = parse_python_file(filepath)
        if not data or (not data['classes'] and not data['functions']):
            continue

        module_name = filepath.stem.lower()
        out_filename = f"{repo_name.lower()}-{module_name}.md"
        out_path = RAW_REPOS_DIR / out_filename

        md_content = generate_markdown(repo_name, module_name, data, filepath)
        out_path.write_text(md_content, encoding='utf-8')
        
        generated_files.append(str(out_path.relative_to(WORKSPACE)).replace('\\', '/'))
        processed_count += 1

    return {
        "repo": repo_name,
        "found": len(files_to_process),
        "processed": processed_count,
        "files": generated_files
    }

def main():
    parser = argparse.ArgumentParser(description="Extract Python AST into Second Brain Markdown")
    parser.add_argument("repo_path", help="Path to the repository folder or python file")
    args = parser.parse_args()

    try:
        res = ingest_repo(args.repo_path)
    except Exception as e:
        print(e)
        return

    print(f"Found {res['found']} python files in {res['repo']}.")
    for f in res['files']:
        print(f"Generated: {f}")

    print(f"Done! Extracted AST for {res['processed']} files into raw/repos/.")

if __name__ == "__main__":
    main()
