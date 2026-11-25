# Supplementary material

For "How Language Models Make Analogies: Their neurons keep abstract ideas apart from topics", D. Nordfors, Communications of the ACM.

The article silences the neurons of one abstract idea at a time in Qwen3.8-27B and reads what the model still says. This folder holds what a reader needs to check it: the map of every model, the nine texts of the test in full, and the neuron patterns, texts, answers and code to repeat the test.

## Contents

| File | What it holds | Where the article uses it |
|---------------------|-------------------|-----------|
| `paper_neuron_cacm_supplement.pdf` | S1, the map of every model: thirty models from eleven makers. S2, the double dissociation test on nine texts: Table S1, the nine texts with their answers in full (Figures S2 to S10; S2 and S6 are the article's Figures 5a and 5b), and one further text in French (Figure S11). S3, how the neurons are silenced. S4, the exact versions of the fifteen models in Figure 4. | Sections 2 and 3, Figures 4 and 5 |
| `reproduce/README.md` | How to run the package. | |
| `reproduce/sets/` | The neuron patterns of the four archetypes and three topics, and random twins of them, as neuron numbers per layer of Qwen3.8-27B. | Section 3, Figure 5, S2, S3 |
| `reproduce/texts/test_texts.jsonl` | The ten texts: the nine of Table S1 and the French text. | Figure 5, S2 |
| `reproduce/texts/exhibits.json` | Which text appears in which figure, and which map shows which pattern. | |
| `reproduce/answers/answers.jsonl` | The model's 50 answers: every text untouched, with its archetype's pattern silenced, with its topic's pattern silenced, and with a random twin of each silenced. Each line carries its verdict. | Figure 5, S2 |
| `reproduce/config.json` | The model and its revision, the question, the decoding and the silencing rule. | S3 |
| `reproduce/expected/numbers.json` | The entries of Table S1, which a rerun is checked against. | S2 |
| `reproduce/maps/` | The map of the model and the maps of the seven patterns, as the figures draw them. | Figure 5, S2 |
| `reproduce/scripts/`, `reproduce/reproduce.sh` | Code that rebuilds Table S1 from the answers (CPU), and reruns the answers with the patterns silenced (GPU, about 60 GB). | |
| `reproduce/environment.yml` | The software the answers were made with. | |
| `reproduce/LICENSE` | CC BY 4.0. | |
