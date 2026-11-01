"""Copy the notebook and its summary outputs into this repo, ready to commit.

Run from this folder:
    python prepare_repo.py --src /path/to/your/project/folder

What it copies
- congress_trading_v7.ipynb -> congress_trading.ipynb, with your contact email replaced by a placeholder
  and your home-folder path (Windows, Mac or Linux) replaced by ~.
- outputs_v6/*.csv -> results/
- outputs_v6/camera/*.png -> figures/

What it leaves out on purpose
- data_congress/ (raw House PDFs, Senate pages, prices). The Ethics in Government Act limits use of these
  reports, so the repo carries code and summary tables only, not a trade-level dataset.
- Tables that list individual trades or name individual members' results:
  v5_pelosi_largest.csv, v6_ticker_name_mismatches.csv, member_leaderboard.csv.
  Pass --include-member-tables to copy them anyway.
- recording_brief.md and any other notes in outputs_v6/ (video prep, not results).

Nothing is deleted from --src. Rerunning overwrites the copies here.
"""
import argparse
import json
import re
import shutil
from pathlib import Path

NOTEBOOK = "congress_trading_v7.ipynb"
OUT_DIR = "outputs_v6"          # the v7 notebook still writes to outputs_v6 (VERSION = "v6" inside)
MEMBER_TABLES = {"v5_pelosi_largest.csv", "v6_ticker_name_mismatches.csv", "member_leaderboard.csv"}
PLACEHOLDER_EMAIL = "your.email@example.com"

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
REAL_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@(?!example\.com)[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Home folders: /home/name, /Users/name, and C:\Users\name in any case, with one or more
# backslashes (plain text has one, Python reprs in outputs have two) or forward slashes.
HOME = re.compile(r"/home/[^/\s'\"]+|/Users/[^/\s'\"]+|(?i:\b[a-z]:(?:\\+|/)users(?:\\+|/)[^\\/\s'\"]+)")


def scrub_notebook(src: Path, dst: Path) -> int:
    nb = json.loads(src.read_text(encoding="utf-8"))
    email, home = EMAIL, HOME
    hits = 0

    def clean(text: str) -> str:
        nonlocal hits
        new = email.sub(PLACEHOLDER_EMAIL, text)
        new = home.sub("~", new)
        hits += new != text
        return new

    for cell in nb["cells"]:
        cell["source"] = [clean(s) for s in cell.get("source", [])]
        for out in cell.get("outputs", []):
            if "text" in out:
                out["text"] = [clean(s) for s in out["text"]]
            data = out.get("data", {})
            for key in ("text/plain", "text/html", "text/markdown"):
                if key in data:
                    data[key] = [clean(s) for s in data[key]]
    dst.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return hits


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, type=Path, help="folder that holds the notebook and outputs_v6/")
    ap.add_argument("--include-member-tables", action="store_true")
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    src = args.src.expanduser().resolve()

    nb = src / NOTEBOOK
    if not nb.exists():
        raise SystemExit(f"not found: {nb}")
    n = scrub_notebook(nb, here / "congress_trading.ipynb")
    print(f"notebook copied; {n} cell lines scrubbed (email / home path)")

    out = src / OUT_DIR
    if not out.exists():
        raise SystemExit(f"not found: {out} (run the notebook first)")
    (here / "results").mkdir(exist_ok=True)
    (here / "figures").mkdir(exist_ok=True)
    copied, skipped = 0, []
    for f in sorted(out.glob("*.csv")):
        if f.name in MEMBER_TABLES and not args.include_member_tables:
            skipped.append(f.name)
            continue
        shutil.copy2(f, here / "results" / f.name)
        copied += 1
    figs = sorted((out / "camera").glob("*.png"))
    for f in figs:
        shutil.copy2(f, here / "figures" / f.name)
    print(f"results: {copied} files; figures: {len(figs)} PNGs")
    if skipped:
        print("left out (pass --include-member-tables to copy):", ", ".join(skipped))

    # Last check: nothing in the repo should still carry an email address or a home-folder path.
    leaks = []
    for p in here.rglob("*"):
        if not p.is_file() or p.suffix not in {".ipynb", ".csv", ".md", ".py"} or p.name == "prepare_repo.py":
            continue
        text = p.read_text(errors="ignore")
        found = [kind for kind, rx in (("email", REAL_EMAIL), ("home path", HOME)) if rx.search(text)]
        if found:
            leaks.append(f"{p.relative_to(here)} ({', '.join(found)})")
    print("privacy check:", "clean" if not leaks else "CHECK THESE: " + "; ".join(leaks))


if __name__ == "__main__":
    main()
