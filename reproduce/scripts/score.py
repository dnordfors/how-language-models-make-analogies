#!/usr/bin/env python3
"""From an answers file: Table S1 of the supplementary material (for each of the nine texts, the name the model gives in place of the silenced archetype and
in place of the silenced topic), each text checked against the test, and the same check for the French text of Figure S11. Written to --out as markdown; with
--expected, the table's entries are compared with the supplement's and the run fails on any difference (letter case and a leading "the" aside, as the table
prints the names in lower case).
The test, from the answers alone (config.json "verdict"): a line keeps its group when its group is the one the untouched model's line to the same text had; it
is lost when the group changes or the line is missing. A text passes when the archetype's set loses the archetype line and keeps the topic line, the topic's
set loses the topic line and keeps the archetype line, and each random twin keeps both lines.
Usage: python scripts/score.py --answers answers/answers.jsonl --out out/table_s1.md [--expected expected/numbers.json]
"""
import argparse, json, os, re
from package import LANG, answers, texts, exhibits, nearest
ap = argparse.ArgumentParser(); ap.add_argument("--answers", required=True); ap.add_argument("--out", required=True); ap.add_argument("--expected", default=""); a = ap.parse_args()
T = texts(); EX = exhibits(); BY = answers(a.answers)
for tid in BY: assert tid in T, tid
WANT = {"own archetype": ["lost", "kept"], "own topic": ["kept", "lost"], "archetype random": ["kept", "kept"], "topic random": ["kept", "kept"]}
def test(tid):
    """the text's four silenced answers against the test; fails loudly when one does not pass"""
    v = BY[tid]; u = v["untouched"]
    K = {c: ["kept" if nearest(v[c], k) is not None and nearest(v[c], k) == nearest(u, k) else "lost" for k in ("archetype", "topic")] for c in WANT}
    assert K == WANT, (tid, K)
    return v
out = ["## Table S1: what the model names in place of the silenced archetype and of the silenced topic", "",
       "Every text passes the test: the archetype's set takes the archetype line and leaves the topic line, the topic's set does the reverse, and each random twin leaves both.", "",
       "| text | figure | archetype | topic | untouched | in place of the archetype | in place of the topic |", "|---|---|---|---|---|---|---|"]
got = {}
for x in EX["table_s1"]["texts"]:
    t = T[x["text_id"]]; assert (t["archetype"], t["topic"]) == (x["archetype"], x["topic"]), x
    v = test(x["text_id"]); u = v["untouched"]; ia, it = v["own archetype"]["pattern"], v["own topic"]["subject"]
    got.setdefault(t["archetype"], {})[t["topic"]] = {"in_place_of_the_archetype": ia, "in_place_of_the_topic": it}
    out.append(f"| {x['text_id']} | {x['figure']} | {t['archetype']} | {t['topic']} | {u['pattern']}; {u['subject']} | {ia} | {it} |")
x = EX["figure_s11"]; t = T[x["text_id"]]; assert LANG[t["language"]] == x["language"], x
v = test(x["text_id"]); u = v["untouched"]
out += ["", f"## Figure {x['figure']}: the text in {x['language']} ({t['archetype']} in {t['topic']}) passes the test", "",
        f"- untouched: {u['pattern']}; {u['subject']}", f"- the archetype's set silenced: {v['own archetype']['pattern']}; {v['own archetype']['subject']}",
        f"- the topic's set silenced: {v['own topic']['pattern']}; {v['own topic']['subject']}", ""]
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); open(a.out, "w").write("\n".join(out)); print("\n".join(out))
if a.expected:
    E = json.load(open(a.expected)); bad = []
    def norm(s): return re.sub(r"^the ", "", s.strip().lower())
    for arch, row in E["table_s1"].items():
        for topic, cell in row.items():
            for k, e in cell.items():
                g = got[arch][topic][k]
                if norm(g) != norm(e): bad.append(f"{arch} / {topic} / {k}: got {g!r}, the supplement states {e!r}")
    if sum(map(len, got.values())) != sum(map(len, E["table_s1"].values())): bad.append("the table's texts are not the supplement's")
    if bad: raise SystemExit("MISMATCH with the supplement:\n" + "\n".join(bad))
    print(f"every entry equals the supplement's ({E['source']})")
