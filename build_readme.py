"""Regenera las secciones automáticas del README del perfil.

- recent_work: repos públicos propios (sin forks) con push más reciente.
- til: últimas notas añadidas al repo AlbaAsca/til (clonado en ./til por el workflow).
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

USER = "AlbaAsca"
ROOT = Path(__file__).parent
SKIP = {USER.lower(), "til"}
N = 5


def gh(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def recent_work(repos):
    rows = []
    for r in repos:
        if r["fork"] or r["private"] or r["archived"] or r["name"].lower() in SKIP:
            continue
        desc = (r.get("description") or "").strip()
        desc = f" — {desc}" if desc else ""
        rows.append(f"- [{r['name']}]({r['html_url']}){desc} · {r['pushed_at'][:10]}")
        if len(rows) == N:
            break
    return rows or ["- (pronto)"]


def til_entries(til_dir):
    if not (til_dir / ".git").exists():
        return ["- (pronto)"]
    out = subprocess.run(
        ["git", "-C", str(til_dir), "log", "--diff-filter=A", "--format=@%cs", "--name-only", "--", "*/*.md"],
        capture_output=True, text=True, check=True).stdout
    rows, date = [], None
    for line in out.splitlines():
        if line.startswith("@"):
            date = line[1:]
        elif line.strip():
            path = til_dir / line
            if not path.exists():
                continue
            first = path.read_text(encoding="utf-8").splitlines()[0]
            title = first.lstrip("# ").strip() or path.stem
            url = f"https://github.com/{USER}/til/blob/main/{line}"
            rows.append(f"- [{title}]({url}) · {date}")
            if len(rows) == N:
                break
    return rows or ["- (pronto)"]


def replace(text, marker, rows):
    pat = re.compile(rf"(<!-- {marker} starts -->).*?(<!-- {marker} ends -->)", re.S)
    return pat.sub(lambda m: m.group(1) + "\n" + "\n".join(rows) + "\n" + m.group(2), text)


def main():
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    if "--offline" not in sys.argv:
        repos = gh(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed&type=owner")
        text = replace(text, "recent_work", recent_work(repos))
    text = replace(text, "til", til_entries(ROOT / "til"))
    readme.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
