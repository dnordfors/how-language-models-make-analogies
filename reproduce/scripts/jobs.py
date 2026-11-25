#!/usr/bin/env python3
"""The jobs of the test: which text is answered with which sets silenced (scripts/run.py answers them).
Default: every text of texts/test_texts.jsonl untouched, under its archetype's set, under that set's random twin, under another archetype's set (drawn among
the others with a seed from the text id), under its topic's set, under that set's random twin and under another topic's set.
--as-stored answers/answers.jsonl: exactly the (text, condition, sets) of the stored answers. --texts restricts either to the texts named. --repeat n
writes every job n times (job ids suffixed |1, |2, ...), the smoke test of a run: the answers must be identical.
Usage: python scripts/jobs.py --out out/jobs.jsonl [--texts t01,t02] [--as-stored answers/answers.jsonl] [--repeat 2]
"""
import argparse, json, os, zlib, numpy as np
from package import NAMES, jl, texts, sets
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--texts", default=""); ap.add_argument("--as-stored", default=""); ap.add_argument("--repeat", type=int, default=1); a = ap.parse_args()
T = texts(); want = a.texts.split(",") if a.texts else list(T)
for t in want: assert t in T, t
SETS = sets()
def silence(kind, name, random): s = SETS[f"random twin of {name}" if random else name]; assert s["kind"] == kind, (kind, name); return {"kind": kind, "set": s["name"], "group": s["group"], "random": random}
jobs = []
if a.as_stored:
    for r in jl(a.as_stored):
        if r["text_id"] not in want: continue
        assert all(s["set"] in SETS for s in r["silence"]), r["job"]
        jobs.append({"job": r["job"], "text_id": r["text_id"], "text": T[r["text_id"]]["text"], "condition": r["condition"], "language": r["language"], "silence": r["silence"]})
else:
    for tid in want:
        t = T[tid]; others = {k: [n for n in NAMES[k].values() if n != t[k]] for k in ("archetype", "topic")}; rng = np.random.default_rng(zlib.crc32(tid.encode()))
        oa, ot = str(rng.choice(others["archetype"])), str(rng.choice(others["topic"]))
        conds = [("untouched", []), ("own archetype", [silence("archetype", t["archetype"], False)]), ("archetype random", [silence("archetype", t["archetype"], True)]), ("other archetype", [silence("archetype", oa, False)]),
                 ("own topic", [silence("topic", t["topic"], False)]), ("topic random", [silence("topic", t["topic"], True)]), ("other topic", [silence("topic", ot, False)])]
        for cond, sil in conds:
            jobs.append({"job": f"{tid}|{cond}", "text_id": tid, "text": t["text"], "condition": cond, "language": t["language"], "silence": sil})
if a.repeat > 1: jobs = [{**j, "job": f"{j['job']}|{k}"} for j in jobs for k in range(1, a.repeat + 1)]
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); open(a.out, "w").write("".join(json.dumps(j, ensure_ascii=False) + "\n" for j in jobs))
print(f"{len(want)} texts, {len(jobs)} jobs")
