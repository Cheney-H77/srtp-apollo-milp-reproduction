from pathlib import Path
import re
import pandas as pd


def parse_gurobi_log(log_path: Path):
    text = log_path.read_text(errors="ignore")

    obj_matches = re.findall(
        r"Best objective\s+([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)",
        text,
    )

    time_matches = re.findall(
        r"Explored\s+.*?\s+in\s+([+-]?\d+(?:\.\d+)?)\s+seconds",
        text,
    )

    node_matches = re.findall(
        r"Explored\s+(\d+)\s+nodes",
        text,
    )

    if not obj_matches:
        return None

    return {
        "objective": float(obj_matches[-1]),
        "time_sec": float(time_matches[-1]) if time_matches else None,
        "nodes": int(node_matches[-1]) if node_matches else None,
    }


def main():
    root = Path.home() / "srtp_apollo_mac"
    ps_repo = root / "code" / "Predict-and-Search_MILP_method"

    log_dir = ps_repo / "logs" / "CA" / "CA_GRB_Predect&Search"

    if not log_dir.exists():
        raise FileNotFoundError(f"PS log directory not found: {log_dir}")

    rows = []

    for log_path in sorted(log_dir.glob("mini_ca_test_*.lp.log")):
        parsed = parse_gurobi_log(log_path)
        if parsed is None:
            print(f"Warning: cannot parse {log_path}")
            continue

        instance = log_path.name.replace(".lp.log", "")

        rows.append(
            {
                "instance": instance,
                "ps_objective": parsed["objective"],
                "ps_time_sec": parsed["time_sec"],
                "ps_nodes": parsed["nodes"],
            }
        )

    df = pd.DataFrame(rows)

    avg_row = pd.DataFrame(
        [
            {
                "instance": "Average",
                "ps_objective": df["ps_objective"].mean(),
                "ps_time_sec": df["ps_time_sec"].mean(),
                "ps_nodes": df["ps_nodes"].mean(),
            }
        ]
    )

    summary = pd.concat([df, avg_row], ignore_index=True)

    out_dir = root / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "ps_summary.csv"
    summary.to_csv(out_path, index=False)

    print("PS log directory:", log_dir)
    print("\nPS Summary:")
    print(summary.to_string(index=False))

    print("\nSaved:")
    print(out_path)


if __name__ == "__main__":
    main()