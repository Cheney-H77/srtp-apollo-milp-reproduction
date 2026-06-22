from pathlib import Path
import re
import pandas as pd


def main():
    root = Path.home() / "srtp_apollo_mac"
    apollo_repo = root / "code" / "Apollo-MILP"

    log_dirs = sorted(
        (apollo_repo / "logs" / "ca").glob("ca_GRB_Predect&Search_*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not log_dirs:
        raise FileNotFoundError("No Apollo log directory found.")

    latest = log_dirs[0]
    test_log = latest / "test.log"

    lines = test_log.read_text().strip().splitlines()

    # First 16 lines: 4 instances × 4 Apollo steps
    step_rows = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if line.startswith("["):
            continue

        parts = line.split()
        if len(parts) == 3:
            obj, elapsed, nodes = map(float, parts)
            instance_id = i // 4
            step = i % 4
            step_rows.append(
                {
                    "instance": f"mini_ca_test_{instance_id:03d}",
                    "step": step,
                    "objective": obj,
                    "time_sec": elapsed,
                    "nodes": nodes,
                }
            )

    df = pd.DataFrame(step_rows)

    summary = (
        df.groupby("instance")
        .agg(
            best_objective=("objective", "max"),
            total_time_sec=("time_sec", "sum"),
            mean_nodes=("nodes", "mean"),
        )
        .reset_index()
    )

    avg_row = pd.DataFrame(
        [
            {
                "instance": "Average",
                "best_objective": summary["best_objective"].mean(),
                "total_time_sec": summary["total_time_sec"].mean(),
                "mean_nodes": summary["mean_nodes"].mean(),
            }
        ]
    )

    summary = pd.concat([summary, avg_row], ignore_index=True)

    out_dir = root / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    step_csv = out_dir / "apollo_step_results.csv"
    summary_csv = out_dir / "apollo_summary.csv"

    df.to_csv(step_csv, index=False)
    summary.to_csv(summary_csv, index=False)

    print("Latest Apollo log:", latest)
    print("\nStep-level results:")
    print(df.to_string(index=False))

    print("\nSummary:")
    print(summary.to_string(index=False))

    print("\nSaved:")
    print(step_csv)
    print(summary_csv)


if __name__ == "__main__":
    main()