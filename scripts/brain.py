import click
import json
import sys

from search_sessions import run_search
from build_search_index import build_index
from audit import run_audit
from resolve_orphans import find_orphans
from mark_duplicates import mark_dupes
from ingest_codebase import ingest_repo

def output_json(status, data=None, message=None, code=None):
    out = {"status": status}
    if data is not None:
        out["data"] = data
    if message is not None:
        out["message"] = message
    if code is not None:
        out["code"] = code
    click.echo(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0 if status == "ok" else 1)

@click.group()
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON format')
@click.pass_context
def cli(ctx, as_json):
    """Brain CLI - Centralized Agent Tooling for Second Brain"""
    ctx.ensure_object(dict)
    ctx.obj['JSON'] = as_json

@cli.command()
@click.argument('query')
@click.option('--project', default=None, help='Filter by project name')
@click.option('--source', type=click.Choice(['session', 'wiki']), default=None, help='Filter by source type')
@click.option('--limit', default=10, type=int, help='Max results to return')
@click.pass_context
def search(ctx, query, project, source, limit):
    """Search FTS5 Index"""
    try:
        results = run_search(query, project, source, limit)
        if ctx.obj['JSON']:
            output_json("ok", data=results)
        else:
            if not results:
                click.echo(f"Không tìm thấy kết quả cho '{query}'")
                return
            click.echo(f"--- Tìm thấy {len(results)} kết quả cho '{query}' ---")
            for i, res in enumerate(results, 1):
                click.echo(f"\n{i}. [{res['source_type'].upper()}] {res['file_path']} (Score: {res['relevance_score']})")
                click.echo(f"   Date: {res['date']} | Project: {res['project']}")
                click.echo(f"   Summary: {res['summary']}")
                click.echo(f"   Match: {res['match_context']}")
    except FileNotFoundError as e:
        if ctx.obj['JSON']:
            output_json("error", message=str(e), code="DB_NOT_FOUND")
        else:
            click.echo(f"Error: {e}")
    except Exception as e:
        if ctx.obj['JSON']:
            output_json("error", message=str(e), code="SEARCH_ERROR")
        else:
            click.echo(f"Lỗi tìm kiếm: {e}")

@cli.command()
@click.option('--full', is_flag=True, help='Rebuild entire index')
@click.pass_context
def index(ctx, full):
    """Build or rebuild search index"""
    try:
        res = build_index(full=full)
        if ctx.obj['JSON']:
            output_json("ok", data=res)
        else:
            click.echo(f"Index updated. Processed {res['processed']} files, Updated {res['updated']} files, Removed {res['removed']} deleted files.")
    except Exception as e:
        if ctx.obj['JSON']:
            output_json("error", message=str(e), code="INDEX_ERROR")
        else:
            click.echo(f"Lỗi build index: {e}")

@cli.command()
@click.pass_context
def health(ctx):
    """Run wiki health analysis"""
    try:
        report = run_audit()
        
        data = {
            "audit": report
        }
        
        if ctx.obj['JSON']:
            output_json("ok", data=data)
        else:
            click.echo("--- WIKI AUDIT REPORT ---")
            click.echo(f"Total files: {report['total']}")
            click.echo(f"Stubs: {len(report['stubs'])}")
            click.echo(f"Bloated: {len(report['bloated'])}")
            click.echo(f"Broken links: {len(report['broken_links'])}")
    except Exception as e:
        if ctx.obj['JSON']:
            output_json("error", message=str(e), code="HEALTH_ERROR")
        else:
            click.echo(f"Lỗi health check: {e}")

@cli.command()
@click.option('--apply', is_flag=True, help='Apply orphan resolution to files')
@click.option('--dry-run', is_flag=True, help='Simulate orphan resolution without writing')
@click.pass_context
def orphans(ctx, apply, dry_run):
    """Identify and resolve orphans"""
    try:
        # If dry_run is true, apply is always false
        actual_apply = apply and not dry_run
        res = find_orphans(apply_mode=actual_apply)
        
        if ctx.obj['JSON']:
            output_json("ok", data=res)
        else:
            click.echo(f"Total real orphans: {res['orphans']}")
            click.echo(f"Total matched orphans: {res['matched']}")
            click.echo(f"Total modified parents: {res['modified_parents']}")
            if dry_run or not apply:
                click.echo("\n[!] DRY RUN ONLY. Use --apply to write changes.")
    except Exception as e:
        if ctx.obj['JSON']:
            output_json("error", message=str(e), code="ORPHAN_ERROR")
        else:
            click.echo(f"Lỗi orphans: {e}")

@cli.command()
@click.option('--dry-run', is_flag=True, help='Simulate marking duplicates without writing')
@click.pass_context
def duplicates(ctx, dry_run):
    """Mark suffix duplicates in absorb-log"""
    try:
        res = mark_dupes(dry_run=dry_run)
        if ctx.obj['JSON']:
            output_json("ok", data=res)
        else:
            click.echo(f"Marked {res['marked']} duplicates.")
            if dry_run:
                click.echo("[DRY-RUN] No changes written.")
    except FileNotFoundError as e:
        if ctx.obj['JSON']:
            output_json("error", message=str(e), code="LOG_NOT_FOUND")
        else:
            click.echo(f"Error: {e}")
    except Exception as e:
        if ctx.obj['JSON']:
            output_json("error", message=str(e), code="DUPLICATE_ERROR")
        else:
            click.echo(f"Lỗi duplicates: {e}")

@cli.command('ingest-code')
@click.argument('repo_path')
@click.pass_context
def ingest_code(ctx, repo_path):
    """Extract Python AST into Markdown"""
    try:
        res = ingest_repo(repo_path)
        if ctx.obj['JSON']:
            output_json("ok", data=res)
        else:
            click.echo(f"Found {res['found']} python files in {res['repo']}.")
            click.echo(f"Extracted AST for {res['processed']} files.")
    except FileNotFoundError as e:
        if ctx.obj['JSON']:
            output_json("error", message=str(e), code="PATH_NOT_FOUND")
        else:
            click.echo(f"Error: {e}")
    except Exception as e:
        if ctx.obj['JSON']:
            output_json("error", message=str(e), code="INGEST_ERROR")
        else:
            click.echo(f"Lỗi ingest: {e}")

if __name__ == '__main__':
    cli(obj={})
