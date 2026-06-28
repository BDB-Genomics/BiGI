"use client";
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

const highlights = [
  "Python",
  "R",
  "Snakemake",
  "Nextflow",
  "Go",
  "Rust",
  "JS / TS",
  "C / C++",
  "Shell",
  "Any codebase"
];

function normalizeRepoInput(raw: string): string | null {
  const value = raw.trim().replace(/^https?:\/\//, "");

  if (!value) {
    return null;
  }

  if (value.includes("github.com/")) {
    const afterHost = value.split("github.com/")[1];
    const [owner, repo] = afterHost.split("/");
    if (owner && repo) {
      return `${owner}/${repo.replace(/\.git$/, "")}`;
    }
  }

  if (value.includes("/")) {
    const [owner, repo] = value.split("/");
    if (owner && repo) {
      return `${owner}/${repo.replace(/\.git$/, "")}`;
    }
  }

  return null;
}

export default function Home() {
  const [repoUrl, setRepoUrl] = useState('');
  const router = useRouter();

  const handleAnalyze = (e: React.FormEvent) => {
    e.preventDefault();

    const normalized = normalizeRepoInput(repoUrl);
    if (!normalized) {
      window.alert("Enter a GitHub URL or an owner/repo pair.");
      return;
    }

    router.push(`/${normalized}`);
  };

  return (
    <main className="relative min-h-screen overflow-hidden px-6 py-10 sm:px-8">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute left-[-12%] top-[-18%] h-[28rem] w-[28rem] rounded-full bg-sky-400/18 blur-3xl" />
        <div className="absolute right-[-10%] top-[12%] h-[24rem] w-[24rem] rounded-full bg-violet-500/18 blur-3xl" />
        <div className="absolute bottom-[-18%] left-[20%] h-[20rem] w-[20rem] rounded-full bg-cyan-300/12 blur-3xl" />
      </div>

      <div className="relative z-10 mx-auto flex min-h-[calc(100vh-5rem)] max-w-6xl flex-col justify-center gap-14">
        <header className="max-w-3xl">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 shadow-[0_0_0_1px_rgba(255,255,255,0.02)]">
            <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(125,211,252,0.8)]" />
            Blast-radius analysis for pipeline repositories
          </div>

          <h1 className="max-w-3xl text-5xl font-semibold tracking-tight text-white sm:text-7xl">
            See the downstream impact before you change the code.
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300 sm:text-xl">
            BiGI builds dependency graphs across any codebase—with deep static AST analysis for Python and R, flow mapping for Snakemake and Nextflow, and universal regex-based parsing for other languages.
          </p>
        </header>

        <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
          <form
            onSubmit={handleAnalyze}
            className="relative overflow-hidden rounded-3xl border border-[var(--surface-border)] bg-[var(--surface)] p-4 shadow-[0_24px_80px_rgba(2,6,23,0.6)] backdrop-blur-xl"
          >
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-300/60 to-transparent" />
            <label className="mb-3 block text-sm font-medium text-slate-300">
              Analyze a repository
            </label>

            <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-slate-950/60 p-3 sm:flex-row sm:items-center">
              <span className="hidden select-none rounded-xl border border-white/10 bg-white/5 px-3 py-3 font-mono text-sm text-slate-400 sm:inline">
                github.com/
              </span>

              <input
                type="text"
                placeholder="AtlasMindAI/bigi"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                className="min-w-0 flex-1 rounded-xl border border-transparent bg-transparent px-3 py-3 font-mono text-base text-white outline-none placeholder:text-slate-500 focus:border-cyan-300/30 focus:bg-white/5"
              />

              <button
                type="submit"
                className="rounded-xl bg-gradient-to-r from-sky-400 to-violet-500 px-5 py-3 font-semibold text-slate-950 shadow-[0_12px_40px_rgba(125,211,252,0.28)] transition hover:brightness-110 active:scale-[0.98]"
              >
                Analyze
              </button>
            </div>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Accepts full GitHub URLs or `owner/repo` notation. Public repos are analyzed directly from source.
            </p>
          </form>

          <aside className="rounded-3xl border border-white/10 bg-white/5 p-6 text-sm text-slate-300 backdrop-blur-xl">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
              Supported layers
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {highlights.map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-white/10 bg-slate-950/60 px-3 py-1.5 text-sm text-slate-200"
                >
                  {item}
                </span>
              ))}
            </div>

            <div className="mt-6 space-y-4 text-slate-400">
              <p>
                Generate an interactive HTML graph, inspect the blast radius of a function or rule,
                or export the index for downstream tools.
              </p>
              <p>
                The local CLI and the web entrypoint share the same graph-building logic, so the same
                repository can be analyzed from the terminal or the browser.
              </p>
            </div>
          </aside>

          <div className="grid gap-4 sm:grid-cols-3 lg:col-span-2">
            {[
              ["Universal Support", "Parse any codebase by automatically detecting non-binary text files and building structured function/call dependencies."],
              ["AST-Level Precision", "Deep AST-level static dependency tracing for Python and R, alongside flow mapping for Snakemake and Nextflow."],
              ["Smart Walk Filtering", "Automatically respects your .gitignore rules during walks, pruning vendor, logs, and build folders from analysis."],
            ].map(([title, body]) => (
              <div
                key={title}
                className="rounded-2xl border border-white/10 bg-slate-950/50 p-5 shadow-[0_10px_30px_rgba(2,6,23,0.28)]"
              >
                <div className="text-base font-semibold text-white">{title}</div>
                <p className="mt-2 text-sm leading-6 text-slate-400">{body}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
