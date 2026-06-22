# SRTP Apollo-MILP Reproduction Snapshot

This repository records my mini-scale reproduction of Apollo-MILP based on Liu et al. 2024 / ICLR 2025.

Current status:
- Generated mini CA MILP instances.
- Generated BG and solution files using Predict-and-Search gurobi.py.
- Trained the predictor and obtained model_best.pth locally.
- Ran Predict-and-Search with Gurobi.
- Ran Apollo-MILP with Gurobi.
- Parsed PS and Apollo logs into CSV summaries.

Important note:
This repository is a lightweight code snapshot. Large files such as dataset/, pretrain/, logs/, model weights, LP/MPS/SOL files, and Gurobi license files are intentionally excluded.

Mini result:
- PS average objective: 531.600028
- Apollo average objective: 531.600028
- Interpretation: the mini toy dataset is too easy, so this result only verifies that the pipeline works. It does not demonstrate Apollo-MILP's performance advantage.

Next goal:
Move from mini-scale reproduction to full paper reproduction on CA, SC, IP, and WA benchmarks.
