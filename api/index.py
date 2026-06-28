"""Vercel serverless function for BiGI web interface.

Downloads GitHub repositories as zip archives (no git binary needed)
and runs BiGI analysis using Python imports directly.
"""

from flask import Flask, Response
import json
import tempfile
import os
import zipfile
import urllib.request
import traceback
from urllib.error import HTTPError
from typing import Optional
import html
import re

def safe_extract(zf, target_dir):
    target_dir = os.path.abspath(target_dir)
    for member in zf.infolist():
        target_path = os.path.abspath(os.path.join(target_dir, member.filename))
        try:
            common = os.path.commonpath([target_dir, target_path])
        except ValueError:
            raise RuntimeError(f"Attempted Path Traversal in Zip File: {member.filename}")
        if common != target_dir:
            raise RuntimeError(f"Attempted Path Traversal in Zip File: {member.filename}")
        zf.extract(member, target_dir)


from bigi.graph import build_graph
from bigi.cli import export_html

app = Flask(__name__)


def resolve_default_branch(owner: str, repo: str) -> Optional[str]:
    """Return the repository default branch, or ``None`` if it cannot be resolved."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    request = urllib.request.Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "BiGI",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
            default_branch = payload.get("default_branch")
            return default_branch if isinstance(default_branch, str) and default_branch else None
    except Exception:
        return None


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if not path:
        return landing_page()

    parts = path.strip('/').split('/')
    if len(parts) < 2:
        return landing_page()

    owner = parts[0]
    repo = parts[1]

    # Validate owner and repo to prevent XSS, SSRF, and command injection
    if not re.match(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,38}[a-zA-Z0-9])?$", owner) or \
       not re.match(r"^[a-zA-Z0-9._-]{1,100}$", repo):
        safe_owner = html.escape(owner)
        safe_repo = html.escape(repo)
        err_html = f"""
        <html><body style="font-family:sans-serif;padding:2rem;background:#0a0a0f;color:white;">
          <h1 style="color:#f87171;">Invalid parameters</h1>
          <p>The owner <strong>{safe_owner}</strong> or repository <strong>{safe_repo}</strong> contains invalid characters.</p>
          <a href="/" style="color:#818cf8;">← Back to home</a>
        </body></html>
        """
        return Response(err_html, status=400, mimetype='text/html')

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Download repo as zip archive (no git binary required)
            zip_path = os.path.join(tmpdir, "repo.zip")
            extract_dir = os.path.join(tmpdir, "repo")

            default_branch = resolve_default_branch(owner, repo)
            zip_url_candidates = [
                f"https://github.com/{owner}/{repo}/archive/refs/heads/{default_branch}.zip"
                if default_branch
                else None,
                f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip",
                f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip",
            ]
            last_error = None
            for zip_url in zip_url_candidates:
                if not zip_url:
                    continue
                try:
                    urllib.request.urlretrieve(zip_url, zip_path)
                    last_error = None
                    break
                except HTTPError as exc:
                    last_error = exc
                    if exc.code != 404:
                        raise
            if last_error is not None:
                raise last_error

            with zipfile.ZipFile(zip_path, 'r') as zf:
                safe_extract(zf, extract_dir)

            # GitHub zips have a single top-level folder like "repo-main/"
            contents = os.listdir(extract_dir)
            if len(contents) == 1 and os.path.isdir(
                os.path.join(extract_dir, contents[0])
            ):
                repo_dir = os.path.join(extract_dir, contents[0])
            else:
                repo_dir = extract_dir

            # Run BiGI analysis directly via Python API
            graph_data = build_graph(repo_dir)

            # Export to HTML
            html_out = os.path.join(tmpdir, "out.html")
            export_html(graph_data, html_out)

            with open(html_out, "r", encoding="utf-8") as f:
                html_content = f.read()

            return Response(html_content, mimetype='text/html')

        except HTTPError as e:
            safe_owner = html.escape(owner)
            safe_repo = html.escape(repo)
            if e.code == 404:
                err_html = f"""
                <html><body style="font-family:sans-serif;padding:2rem;background:#0a0a0f;color:white;">
                  <h1 style="color:#f87171;">Repository not found</h1>
                  <p>Could not find <strong>github.com/{safe_owner}/{safe_repo}</strong>.</p>
                  <p style="color:#9ca3af;">Make sure the repository exists, is public, and has a reachable default branch.</p>
                  <a href="/" style="color:#818cf8;">← Back to home</a>
                </body></html>
                """
            else:
                err_html = f"""
                <html><body style="font-family:sans-serif;padding:2rem;background:#0a0a0f;color:white;">
                  <h1 style="color:#f87171;">GitHub error (HTTP {e.code})</h1>
                  <p>Failed to download <strong>github.com/{safe_owner}/{safe_repo}</strong>.</p>
                  <a href="/" style="color:#818cf8;">← Back to home</a>
                </body></html>
                """
            return Response(err_html, status=e.code, mimetype='text/html')

        except Exception as e:
            safe_owner = html.escape(owner)
            safe_repo = html.escape(repo)
            err_html = f"""
            <html><body style="font-family:sans-serif;padding:2rem;background:#0a0a0f;color:white;">
              <h1 style="color:#f87171;">Error analyzing repository</h1>
              <p>Could not analyze <strong>github.com/{safe_owner}/{safe_repo}</strong>.</p>
              <pre style="background:#1a1a2e;padding:1rem;border-radius:8px;overflow-x:auto;color:#fbbf24;">{traceback.format_exc()}</pre>
              <a href="/" style="color:#818cf8;">← Back to home</a>
            </body></html>
            """
            return Response(err_html, status=500, mimetype='text/html')


def landing_page():
    return Response("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BiGI - Blast-radius Impact Graph Indexer</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="relative min-h-screen bg-[#050508] text-slate-200 font-['Inter',sans-serif] overflow-x-hidden flex items-center justify-center">
        <!-- Glow accents -->
        <div class="absolute inset-0 pointer-events-none overflow-hidden">
            <div class="absolute left-[-10%] top-[-10%] h-[30rem] w-[30rem] rounded-full bg-blue-500/10 blur-[120px]"></div>
            <div class="absolute right-[-10%] bottom-[-10%] h-[30rem] w-[30rem] rounded-full bg-purple-500/10 blur-[120px]"></div>
        </div>

        <div class="relative z-10 max-w-4xl mx-auto px-6 py-16 text-center flex flex-col items-center">
            <div class="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs uppercase tracking-wider text-slate-300 font-['Outfit']">
                <span class="h-2 w-2 rounded-full bg-cyan-400 shadow-[0_0_12px_rgba(34,211,238,0.8)]"></span>
                Blast-Radius Impact Graph Indexer
            </div>
            
            <h1 class="text-6xl font-bold tracking-tight text-white mb-6 font-['Outfit'] bg-gradient-to-r from-cyan-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent sm:text-7xl">
                BiGI
            </h1>
            
            <p class="text-lg sm:text-xl text-slate-300 max-w-2xl mb-8 leading-relaxed">
                Instantly visualize downstream impact in any public GitHub codebase. Builds dependency graphs across Python, R, Snakemake, Nextflow, Go, Rust, JS/TS, Shell, and more.
            </p>

            <div class="w-full max-w-md bg-slate-950/60 border border-white/10 p-6 rounded-3xl shadow-2xl backdrop-blur-xl mb-10">
                <div class="text-left mb-4">
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">To start analysis</label>
                    <p class="text-sm text-slate-300">Append <code class="bg-white/5 border border-white/10 px-2 py-1 rounded font-mono text-cyan-300">/owner/repo</code> directly to the URL path.</p>
                </div>
                <div class="flex items-center justify-between bg-slate-900 border border-white/10 rounded-2xl p-4 font-mono text-sm">
                    <span class="text-slate-400 select-none">Example:</span>
                    <a href="/AtlasMindAI/bigi" class="text-cyan-400 hover:text-cyan-300 transition underline decoration-cyan-400/30">/AtlasMindAI/bigi</a>
                </div>
            </div>

            <div class="flex flex-wrap justify-center gap-2 max-w-xl">
                <span class="px-3.5 py-1.5 rounded-full bg-white/5 border border-white/5 text-xs text-slate-300">Python AST</span>
                <span class="px-3.5 py-1.5 rounded-full bg-white/5 border border-white/5 text-xs text-slate-300">R AST</span>
                <span class="px-3.5 py-1.5 rounded-full bg-white/5 border border-white/5 text-xs text-slate-300">Snakemake</span>
                <span class="px-3.5 py-1.5 rounded-full bg-white/5 border border-white/5 text-xs text-slate-300">Nextflow</span>
                <span class="px-3.5 py-1.5 rounded-full bg-white/5 border border-white/5 text-xs text-slate-300">Go</span>
                <span class="px-3.5 py-1.5 rounded-full bg-white/5 border border-white/5 text-xs text-slate-300">Rust</span>
                <span class="px-3.5 py-1.5 rounded-full bg-white/5 border border-white/5 text-xs text-slate-300">JS / TS</span>
                <span class="px-3.5 py-1.5 rounded-full bg-white/5 border border-white/5 text-xs text-slate-300">C / C++</span>
                <span class="px-3.5 py-1.5 rounded-full bg-white/5 border border-white/5 text-xs text-slate-300">Shell</span>
            </div>
        </div>
    </body>
    </html>
    """, mimetype='text/html')
