from pathlib import Path
import pandas as pd


def main():
    root = Path.home() / "srtp_apollo_mac"
    results_dir = root / "results"

    ps_path = results_dir / "ps_summary.csv"
    apollo_path = results_dir / "apollo_summary.csv"

    ps = pd.read_csv(ps_path)
    apollo = pd.read_csv(apollo_path)

    merged = ps.merge(
        apollo,
        on="instance",
        how="inner",
    )

    merged = merged.rename(
        columns={
            "best_objective": "apollo_best_objective",
            "total_time_sec": "apollo_total_time_sec",
            "mean_nodes": "apollo_mean_nodes",
        }
    )

    merged["objective_gap_apollo_minus_ps"] = (
        merged["apollo_best_objective"] - merged["ps_objective"]
    )

    merged["apollo_better"] = merged["objective_gap_apollo_minus_ps"] > 1e-6

    out_path = results_dir / "ps_vs_apollo_summary.csv"
    merged.to_csv(out_path, index=False)

    print("PS vs Apollo Summary:")
    print(merged.to_string(index=False))

    print("\nSaved:")
    print(out_path)


if __name__ == "__main__":
    main()