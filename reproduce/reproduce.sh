#!/usr/bin/env bash
# The CPU part of the package: Table S1 of the supplementary material from the stored answers, every text checked against the test and every entry compared
# with what the supplement states (expected/numbers.json). No model is loaded.
# The model runs are scripts/jobs.py and run.py (README.md). Usage: bash reproduce.sh     (PYTHON=/path/to/python picks the interpreter)
set -euo pipefail; cd "$(dirname "$0")"; PY="${PYTHON:-python3}"
mkdir -p out; echo "interpreter: $PY"
echo; echo "##### Table S1 and Figure S11 (answers/answers.jsonl -> out/table_s1.md) #####"
"$PY" scripts/score.py --answers answers/answers.jsonl --out out/table_s1.md --expected expected/numbers.json
