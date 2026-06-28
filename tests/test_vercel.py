import importlib
import json
import sys
import types
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_vercel_module():
    if "api.index" in sys.modules:
        return sys.modules["api.index"]

    fake_flask = types.ModuleType("flask")

    class FakeResponse:
        def __init__(self, content, status=200, mimetype="text/html"):
            self.data = content
            self.status_code = status
            self.mimetype = mimetype

    class FakeFlask:
        def __init__(self, name):
            self.name = name

        def route(self, *args, **kwargs):
            def decorator(fn):
                return fn

            return decorator

    fake_flask.Flask = FakeFlask
    fake_flask.Response = FakeResponse
    sys.modules["flask"] = fake_flask
    return importlib.import_module("api.index")


def test_resolve_default_branch_reads_github_api(monkeypatch):
    vercel = load_vercel_module()

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({"default_branch": "trunk"}).encode("utf-8")

    def fake_urlopen(request, timeout=10):
        assert "api.github.com/repos/alice/demo" in request.full_url
        return FakeResponse()

    monkeypatch.setattr(vercel.urllib.request, "urlopen", fake_urlopen)

    assert vercel.resolve_default_branch("alice", "demo") == "trunk"


def test_catch_all_uses_default_branch(monkeypatch, tmp_path):
    vercel = load_vercel_module()
    captured = {}

    def fake_resolve_default_branch(owner, repo):
        return "trunk"

    def fake_urlretrieve(url, zip_path):
        captured["url"] = url
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("demo-trunk/", "")
            zf.writestr("demo-trunk/README.md", "# demo\n")
        return zip_path, None

    def fake_build_graph(repo_dir):
        captured["repo_dir"] = repo_dir
        return {"nodes": {}, "edges": []}

    def fake_export_html(graph_data, output_path, selected_node_id=None):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("<html><body>ok</body></html>")

    monkeypatch.setattr(vercel, "resolve_default_branch", fake_resolve_default_branch)
    monkeypatch.setattr(vercel.urllib.request, "urlretrieve", fake_urlretrieve)
    monkeypatch.setattr(vercel, "build_graph", fake_build_graph)
    monkeypatch.setattr(vercel, "export_html", fake_export_html)

    response = vercel.catch_all("alice/demo")

    assert response.status_code == 200
    assert captured["url"] == "https://github.com/alice/demo/archive/refs/heads/trunk.zip"
    assert captured["repo_dir"]


def test_catch_all_invalid_parameters():
    vercel = load_vercel_module()
    response = vercel.catch_all("alice/demo-malicious-repo-with-spaces ")
    assert response.status_code == 400
    assert "Invalid parameters" in response.data

    response = vercel.catch_all("<script>alert(1)</script>/demo")
    assert response.status_code == 400
    assert "Invalid parameters" in response.data
    assert "&lt;script&gt;alert(1)&lt;" in response.data
    assert "script&gt;" in response.data


def test_catch_all_zip_slip(monkeypatch):
    vercel = load_vercel_module()

    def fake_resolve_default_branch(owner, repo):
        return "trunk"

    def fake_urlretrieve(url, zip_path):
        with zipfile.ZipFile(zip_path, "w") as zf:
            # Attempt directory traversal out of target extract directory
            zf.writestr("../traversal.txt", "malicious payload")
        return zip_path, None

    monkeypatch.setattr(vercel, "resolve_default_branch", fake_resolve_default_branch)
    monkeypatch.setattr(vercel.urllib.request, "urlretrieve", fake_urlretrieve)

    response = vercel.catch_all("alice/demo")
    # Should catch the Exception / RuntimeError from zip slip check and return 500
    assert response.status_code == 500
    assert "Attempted Path Traversal in Zip File" in response.data
