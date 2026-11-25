# Reproduction package

For "How Language Models Make Analogies: Their neurons keep abstract ideas apart from topics" (D. Nordfors, Communications of the ACM).

- `sets/`: the neuron patterns of the four archetypes and three topics the article and its supplementary material show, and random twins of them, as neuron
  indices per layer of Qwen/Qwen3.8-27B.
- `texts/`: the ten texts shown: the nine of Table S1 and the French text of Figure S11.
- `answers/`: the model's answers to those texts: untouched, with the archetype's pattern silenced, with the topic's pattern silenced, and with a random
  twin of each silenced.
- `maps/`: the map of the model and the maps of the seven patterns, as the figures draw them.
- `config.json`: model, revision, question, decoding and the silencing rule.
- `scripts/`, `reproduce.sh`: rebuild Table S1 from the answers (CPU), and rerun the answers (GPU, about 60 GB).

CPU: `bash reproduce.sh`

GPU: `python scripts/jobs.py --out out/jobs.jsonl --as-stored answers/answers.jsonl`, then `python scripts/run.py --jobs out/jobs.jsonl --out out/answers.jsonl`,
then `python scripts/compare_answers.py --run out/answers.jsonl --stored answers/answers.jsonl`. Without `--as-stored`, `jobs.py` also writes, for every text,
a job with another archetype's pattern silenced and one with another topic's.

The stored answers were made on an NVIDIA DGX Spark (one NVIDIA GB10) with the software of `environment.yml` (`config.json` "made_on" gives the details); a rerun repeats them
character for character on the same hardware and software, and elsewhere can differ in wording where the model's next word is nearly tied.

License: CC BY 4.0, see `LICENSE`.
