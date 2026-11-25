#!/usr/bin/env python3
"""The model's answers with neuron sets silenced. GPU: about 60 GB of memory (the bf16 weights are 54 GB), about 20 seconds per answer.
For each job of a jobs file (scripts/jobs.py writes them): the question of config.json about the job's text, answered greedily by Qwen3.8-27B at the pinned
revision with thinking off, one text per forward pass, with the job's sets silenced in every layer (config.json "silencing"). One record per answer, in the
format of answers/answers.jsonl without the groups: scripts/compare_answers.py checks the answers against the stored ones, whose groups (config.json
"verdict") they then carry. Written to --out as it completes; a rerun continues where the last one stopped.
Usage: python scripts/run.py --jobs out/jobs.jsonl --out out/answers.jsonl
"""
import argparse, json, os, time, torch
from package import CFG, jl, lines, sets, silenced
ap = argparse.ArgumentParser(); ap.add_argument("--jobs", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
D = CFG["decoding"]; assert D["greedy"] and not D["enable_thinking"] and D["texts_per_forward_pass"] == 1
SETS = sets()
assert {(s["kind"], s["group"]) for s in SETS.values()} == {(k, g) for k in CFG["groups"] for g in CFG["groups"][k]}   # the groups of config.json, each with its sets
jobs = jl(a.jobs); done = {r["job"] for r in jl(a.out)} if os.path.exists(a.out) else set()
todo = [j for j in jobs if j["job"] not in done]; print(f"{len(jobs)} jobs, {len(todo)} to run", flush=True)
for j in todo:
    for s in j["silence"]: assert s["set"] in SETS, f"{j['job']}: no released set for {s}"
    silenced(j, SETS)
if not todo: raise SystemExit(0)
from transformers import AutoModelForCausalLM, AutoTokenizer
tok = AutoTokenizer.from_pretrained(CFG["model"], revision=CFG["revision"])
model = AutoModelForCausalLM.from_pretrained(CFG["model"], revision=CFG["revision"], dtype=getattr(torch, CFG["dtype"])).to("cuda").eval()
for p in model.parameters(): p.requires_grad_(False)
assert len(model.model.layers) == CFG["layers"]
SIL = {}
def hook(b):
    def pre(mod, args):
        x = args[0]
        if b in SIL: x = x.clone(); x[..., SIL[b]] = 0
        return (x,)
    return pre
for b, l in enumerate(model.model.layers): l.mlp.down_proj.register_forward_pre_hook(hook(b))
eos = [tok.eos_token_id] + ([tok.convert_tokens_to_ids("<|im_end|>")] if "<|im_end|>" in tok.get_vocab() else []); t0 = time.time()
with open(a.out, "a") as f:
    for n, j in enumerate(todo):
        SIL.clear()
        for b, v in silenced(j, SETS).items(): SIL[b] = torch.tensor(v, dtype=torch.long, device="cuda")
        chat = tok.apply_chat_template([{"role": "user", "content": CFG["question"].format(text=j["text"])}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        enc = tok([chat], return_tensors="pt").to("cuda")
        with torch.no_grad(): g = model.generate(**enc, max_new_tokens=D["max_new_tokens"], do_sample=False, eos_token_id=eos, pad_token_id=tok.eos_token_id)
        ans = tok.decode(g[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip(); L = lines(ans)
        rec = {"job": j["job"], "text_id": j["text_id"], "condition": j["condition"], "language": j["language"], "silence": j["silence"], "answer": ans, "pattern": L["pattern"][0] if "pattern" in L else "", "subject": L["subject"][0] if "subject" in L else ""}
        f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
        print(f"[{(time.time() - t0) / 60:.1f} min] {n + 1}/{len(todo)} {j['job']} | {ans[:90]!r}", flush=True)
print("ALL DONE", flush=True)
