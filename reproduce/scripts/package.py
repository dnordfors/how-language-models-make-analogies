"""Shared by the package's scripts: the package root and config.json, the texts and the exhibits, an answers file grouped by text and condition, the released
groups' names, the neuron sets and the neurons a job silences, the answer-line parser (the one the runner applies; the stored answers were parsed by it), and
the kept-or-lost rule."""
import glob, json, os, re
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*p): return os.path.join(PKG, *p)
CFG = json.load(open(P("config.json"))); NAMES = CFG["groups"]                              # kind -> group (the name's slug) -> the released name
LANG = {"en": "English", "fr": "French"}
def jl(path): return [json.loads(l) for l in open(path)]
def texts(): return {t["id"]: t for t in jl(P("texts", "test_texts.jsonl"))}
def exhibits(): return json.load(open(P("texts", "exhibits.json")))
def answers(path):
    """text id -> condition -> record"""
    by = {}
    for r in jl(path): by.setdefault(r["text_id"], {})[r["condition"]] = r
    return by
def sets():
    """set name -> the set's record, for every file of sets/"""
    return {s["name"]: s for s in (json.load(open(f)) for f in sorted(glob.glob(P("sets", "*.json"))))}
def silenced(job, SETS):
    """layer -> the sorted neurons a job silences: the union of its sets (config.json "silencing")"""
    out = {}
    for s in job["silence"]:
        rec = SETS[s["set"]]; assert (rec["kind"], rec["group"], "twin_of" in rec) == (s["kind"], s["group"], s["random"]), f"{job['job']}: {s} is not the set {rec['name']!r}"
        for b, v in rec["layers"].items(): out[int(b)] = sorted(set(out.get(int(b), [])) | set(v))
    return out
GROUP = {"archetype": "pattern_group", "topic": "subject_group"}
def nearest(r, kind):
    """the group stored for the line of this kind (config.json "verdict"); None when the line is missing"""
    x = r[GROUP[kind]]; return x["nearest"] if x else None
def parts(ans):
    ans = re.sub(r",?\s*a colon,?\s*", ": ", ans.strip().strip("*"), count=1); m = re.split(r":\s*|\n", ans, maxsplit=1)
    if len(m) > 1 and m[1].strip(): return (m[0].strip().strip("*"), m[1].strip())
    m = re.split(r",\s+", ans, maxsplit=1)
    if len(m) > 1 and m[1].strip(): return (m[0].strip().strip("*"), m[1].strip())
    return (ans.strip(), ans.strip())
def lines(ans):
    """the pattern line and the subject line of an answer, each split into its name and its explanation"""
    out = {}
    for line in ans.splitlines():
        l = line.strip().strip("*")
        for key in ("pattern", "subject"):
            if l.lower().startswith(key) and key not in out: out[key] = parts(l.split(":", 1)[1].strip()) if ":" in l else ("", "")
    return out
