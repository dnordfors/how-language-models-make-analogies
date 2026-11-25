#!/usr/bin/env python3
"""A run's answers against the stored ones, job by job, character for character; an identical answer carries the stored answer's groups. A job id with a
repeat suffix (|1, |2, from jobs.py --repeat) is compared with the stored job it repeats and with its other repeats. Prints every difference; fails if any.
Usage: python scripts/compare_answers.py --run out/answers.jsonl --stored answers/answers.jsonl
"""
import argparse, collections, re
from package import jl
ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); ap.add_argument("--stored", required=True); a = ap.parse_args()
S = {r["job"]: r for r in jl(a.stored)}; R = jl(a.run); bad = []; reps = collections.defaultdict(list)
for r in R:
    base = re.sub(r"\|\d+$", "", r["job"]); reps[base].append(r)
    if base not in S: print(f"{r['job']}: no stored answer to compare with"); continue
    s = S[base]; same = r["answer"] == s["answer"]
    print(f"{r['job']}: {'identical to the stored answer' if same else 'DIFFERS'}")
    if not same: bad.append(r["job"]); print(f"  run:    {r['answer']!r}\n  stored: {s['answer']!r}")
for base, rs in reps.items():
    if len(rs) > 1 and len({x["answer"] for x in rs}) != 1: bad.append(base); print(f"{base}: the repeats differ from each other")
print(f"{len(R)} answers, {len(bad)} differ"); raise SystemExit(1 if bad else 0)
