"""
RAG for spec-driven development using scope.md + prompt.md.

  RAG=.agents/skills/sdd-implement/scripts/rag.py
  python $RAG ask "Implement REQ-003"     # retrieve context, fill prompt.md -> .rag/prompt_out.md
  python $RAG check                       # traceability: approved REQs without code/tests, stale tags
  python $RAG list                        # every REQ/DEC with its status

Indexes: scope.md (+ any scope/*.md), src/, tests/.  Standard library only.
"""
import math, os, re, sys
from collections import Counter
from pathlib import Path

def _find_root():
    # project root = nearest folder (from where you run it, then from this script) that has scope.md
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for d in (start, *start.parents):
            if (d / "scope.md").exists():
                return d
    sys.exit("scope.md not found. Run this from your project folder.")


ROOT = _find_root()
OUT_DIR = ROOT / ".rag"
ID_RE = re.compile(r"\b(?:REQ|DEC)-\d{3}(?:-[a-z]+)?\b")
ALWAYS_INCLUDE = {"overview", "out of scope", "glossary"}
CODE_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".kt", ".cs", ".rb", ".php"}
TOP_K = 4
MIN_RELATIVE_SCORE = 0.35   # drop search hits scoring < 35% of the best hit
ALWAYS_INCLUDE_DECISIONS = True  # decisions are project-wide rules; set False once you have many


# ---------------- INDEX ----------------
def scope_files():
    files = [ROOT / "scope.md"] + sorted((ROOT / "scope").glob("*.md"))
    return [f for f in files if f.exists()]


def chunk_scope(path):
    text = re.sub(r"<!--.*?-->", "", path.read_text(), flags=re.S)
    for sec in re.split(r"(?m)^(?=## )", text):
        if not sec.startswith("## "):
            continue
        heading = sec.splitlines()[0][3:].strip()
        m = ID_RE.match(heading)
        status = re.search(r"(?mi)^status:\s*(\w+)", sec)
        yield {
            "source": str(path.relative_to(ROOT)),
            "kind": ("req" if m.group().startswith("REQ") else "dec") if m else "info",
            "id": m.group() if m else None,
            "title": heading,
            "status": status.group(1).lower() if status else "approved",
            "always": heading.lower() in ALWAYS_INCLUDE
                      or (ALWAYS_INCLUDE_DECISIONS and bool(m) and m.group().startswith("DEC")),
            "text": sec.strip(),
        }


def chunk_code(path):
    blocks = re.split(r"\n\s*\n(?=\s*(?:#|//|def |class |function |export |public |func ))", path.read_text())
    for b in blocks:
        if not b.strip():
            continue
        name = re.search(r"(?:def|class|function|func)\s+(\w+)", b)
        yield {
            "source": str(path.relative_to(ROOT)),
            "kind": "test" if "test" in path.parts[0] or "test" in path.name else "code",
            "id": None,
            "title": name.group(1) if name else path.name,
            "status": "approved",
            "always": False,
            "text": b.strip(),
        }


def build_index():
    chunks = []
    for f in scope_files():
        chunks += chunk_scope(f)
    for folder in ("src", "tests"):
        for f in sorted((ROOT / folder).rglob("*")):
            if f.suffix in CODE_EXT:
                chunks += chunk_code(f)
    for c in chunks:
        c["refs"] = set(ID_RE.findall(c["text"]))
        c["tokens"] = tokenize(c["title"] + " " + c["text"])
    return chunks


# ---------------- RETRIEVE ----------------
STOP = set("a an the and or to of in for on with is are be by it this that as at from can "
           "implement implements add build create make write fix update".split())


def tokenize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    words = [w[:-1] if w.endswith("s") and len(w) > 4 else w for w in words]
    return [w for w in words if w not in STOP]


def bm25(query, pool, k1=1.5, b=0.75):
    q = tokenize(query)
    N = len(pool) or 1
    avgdl = sum(len(c["tokens"]) for c in pool) / N
    df = Counter(t for c in pool for t in set(c["tokens"]))
    q_ids = set(ID_RE.findall(query))
    out = []
    for c in pool:
        tf = Counter(c["tokens"])
        s = sum(math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5))
                * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(c["tokens"]) / avgdl))
                for t in q if t in tf)
        if c["id"] in q_ids:
            s += 10  # asked for this exact requirement
        out.append(s)
    return out


def retrieve(task, chunks):
    usable = [c for c in chunks if c["status"] == "approved"]  # drafts + superseded never reach the AI
    fixed = [c for c in usable if c["always"]]
    pool = [c for c in usable if not c["always"]]
    ranked = sorted(zip(bm25(task, pool), range(len(pool))), reverse=True)
    top = ranked[0][0] if ranked else 0
    hits = [pool[i] for s, i in ranked[:TOP_K] if s > 0 and s >= MIN_RELATIVE_SCORE * top]

    # follow IDs: requirement -> its code/tests ; code -> the decisions it references
    ids = {c["id"] for c in hits if c["id"]} | {r for c in hits for r in c["refs"]}
    linked = [c for c in usable if c not in hits and not c["always"]
              and (c["id"] in ids or (c["kind"] in ("code", "test") and c["refs"] & ids))]

    # second pass: search the CODE using each found requirement's own text
    # (finds existing code a new requirement builds on, even before it is tagged)
    code_pool = [c for c in usable if c["kind"] == "code" and c not in hits and c not in linked]
    for req in [c for c in hits if c["kind"] == "req"]:
        req_text = re.sub(r"(?m)^(status:.*|## .*)$", "", req["text"])
        ranked = sorted(zip(bm25(req_text, code_pool), range(len(code_pool))), reverse=True)
        top = ranked[0][0] if ranked else 0
        for s, i in ranked[:3]:
            if s > 0 and s >= MIN_RELATIVE_SCORE * top and code_pool[i] not in linked:
                linked.append(code_pool[i])
    return fixed, hits, linked


# ---------------- AUGMENT ----------------
def render(task, context):
    template = (ROOT / "prompt.md").read_text()
    # the setup section (which contains this script) is only needed once; drop it from task prompts
    start, end = "<!-- SETUP" + ":START -->", "<!-- SETUP" + ":END -->"  # split so the markers never appear in this code
    template = re.sub(re.escape(start) + ".*?" + re.escape(end) + r"\n?", "", template, flags=re.S)
    blocks = "\n\n".join(
        f'<context source="{c["source"]}" kind="{c["kind"]}">\n{c["text"]}\n</context>' for c in context)
    # replace placeholders only where they stand alone on a line
    template = re.sub(r"(?m)^\{\{CONTEXT\}\}$", lambda _: blocks, template)
    return re.sub(r"(?m)^\{\{TASK\}\}$", lambda _: task, template)


def send_to_claude(prompt):
    import anthropic
    msg = anthropic.Anthropic().messages.create(
        model="claude-sonnet-5-5", max_tokens=4000,
        messages=[{"role": "user", "content": prompt}])
    return msg.content[0].text


# ---------------- COMMANDS ----------------
def cmd_ask(task, send):
    chunks = build_index()
    fixed, hits, linked = retrieve(task, chunks)
    print(f"TASK: {task}\n")
    for label, group in (("always", fixed), ("search", hits), ("linked", linked)):
        for c in group:
            print(f"  [{label:<6}] [{c['kind']:<4}] {c['source']} :: {c['title']}")
    prompt = render(task, fixed + hits + linked)
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "prompt_out.md").write_text(prompt)
    print(f"\nPrompt written to .rag/prompt_out.md ({len(prompt)} chars)")
    if send:
        answer = send_to_claude(prompt)
        (OUT_DIR / "answer.md").write_text(answer)
        print("Claude's answer written to .rag/answer.md")


def cmd_list():
    for c in build_index():
        if c["id"]:
            print(f"  {c['id']:<12} {c['status']:<11} {c['title']}")


def cmd_check():
    chunks = build_index()
    specs = {c["id"]: c for c in chunks if c["id"]}
    code_refs = Counter(r for c in chunks if c["kind"] == "code" for r in c["refs"])
    test_refs = Counter(r for c in chunks if c["kind"] == "test" for r in c["refs"])
    problems = 0
    print(f"{'ID':<12} {'STATUS':<11} {'CODE':<5} {'TESTS':<5}")
    for sid, c in specs.items():
        if c["kind"] != "req":
            continue
        code, tests = code_refs[sid], test_refs[sid]
        flag = ""
        if c["status"] == "approved" and (not code or not tests):
            missing = " and ".join(x for x, n in (("code", code), ("tests", tests)) if not n)
            flag, problems = f"  <- missing {missing}", problems + 1
        if c["status"] != "approved" and (code or tests):
            flag, problems = f"  <- code refers to a {c['status']} requirement", problems + 1
        print(f"{sid:<12} {c['status']:<11} {code:<5} {tests:<5}{flag}")
    unknown = (set(code_refs) | set(test_refs)) - set(specs)
    for u in sorted(unknown):
        print(f"{u:<12} {'UNKNOWN':<11}  <- referenced in code but not in scope.md")
        problems += 1
    print(f"\n{problems} problem(s)")
    return 1 if problems else 0


def main():
    args = sys.argv[1:]
    if not args or args[0] not in ("ask", "check", "list"):
        print(__doc__)
        return 1
    if args[0] == "ask":
        task = " ".join(a for a in args[1:] if not a.startswith("--"))
        return cmd_ask(task, "--send" in args) or 0
    if args[0] == "list":
        return cmd_list() or 0
    return cmd_check()


if __name__ == "__main__":
    sys.exit(main())
