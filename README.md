<div align="center">

# 🌐 BiGI: Blast-radius Impact Graph Indexer
**Universal Software Pipeline Intelligence & Static Analysis**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/BDB-Genomics/BiGI/commits/main)

<img src="assets/hero.jpg" width="800" alt="BiGI Blast Radius Graph">

> **"What breaks if I change this code?"**  
> BiGI maps out your software pipelines. It connects high-level rules (like Snakemake or Nextflow) directly to the code running inside them (Python, Rust, Bash). It builds a beautiful, interactive graph so you can see exactly what breaks if you change a file.

</div>

---

## ✨ Core Features

- 🔗 **See Everything**: We connect your pipeline rules directly to the underlying scripts. You can see the entire flow of your project in one place.
- 📦 **Track Environments**: BiGI finds your Docker and Conda environments. If you upgrade a package, it shows you exactly what parts of your project might break.
- 🚦 **Git Integration**: When you make changes to a file, the graph lights up. Modified files glow **Red**, and everything that depends on them glows **Orange**. 
- 🛠️ **Works With Everything**: We support **Snakemake**, **Nextflow**, **Python**, **R**, **Rust**, **Bash**, **Go**, **C++**, and **JavaScript**.
- 🤖 **GitHub Bot**: BiGI can comment on your Pull Requests. It warns your team if a code change might break something downstream.
- ⚡ **No Setup Needed**: The graph is a single HTML file. You don't need to install any servers or databases to view it.

---

## 🚀 Quickstart

Install BiGI globally so you can use it anywhere:

```bash
git clone https://github.com/BDB-Genomics/BiGI.git
cd BiGI
pip install -e .
```

---

## 📖 How to Use

BiGI is very easy to use. You can analyze local folders or remote GitHub links.

### 1. Analyze a Local Project
```bash
bigi analyze path/to/project --html output.html
```

### 2. Analyze a GitHub Link
BiGI will clone the link, build the graph, and clean up automatically.
```bash
bigi analyze https://github.com/your-org/data-pipeline.git --html output.html
```

### 3. Check What Breaks (CLI)
Ask BiGI what happens if you change a specific function:
```bash
bigi impact log_transform --pipeline-dir my_pipeline
```

### 4. GitHub Actions Bot
Add BiGI to your GitHub Actions. It will automatically check Pull Requests and warn you about broken code:
```bash
bigi pr-report --pipeline-dir .
```

---

## 🧠 How it Works

BiGI does not run your code. Instead, it reads your code incredibly fast:
1. **Reads Pipelines**: It scans your `Snakefiles` and `.nf` files to find inputs and outputs.
2. **Reads Scripts**: It uses smart parsers to find all the functions and commands inside your Python, R, and Bash scripts.
3. **Builds the Graph**: It connects the scripts back to the pipeline rules, giving you a complete map of your project.

---

## 🔭 Future Plans

We are building BiGI into a complete platform. Here is what we are working on next:

1. **Data Schemas**: We want to check your CSV files. If step 1 outputs a column named `sample_id`, but step 2 expects `id`, BiGI will warn you before you even run the code.
2. **Performance Stats**: We want to read your runtime logs. The graph will make slow nodes bigger, so you can see which parts of your code need to be faster.
3. **Graph Search Engine**: We want to let you search your graph using code, just like a database.
