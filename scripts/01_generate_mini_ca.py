from pathlib import Path
import random
import gurobipy as gp
from gurobipy import GRB


def generate_ca_instance(
    out_path: Path,
    seed: int,
    n_items: int = 25,
    n_bids: int = 80,
    min_bundle_size: int = 1,
    max_bundle_size: int = 5,
) -> None:
    """
    Generate a small combinatorial-auction-like MILP.

    Variables:
        x_j = 1 means bid j is accepted.

    Objective:
        maximize total accepted bid value.

    Constraints:
        each item can be allocated at most once.
    """
    rng = random.Random(seed)

    # Each item has a base private value.
    item_values = [rng.uniform(5.0, 30.0) for _ in range(n_items)]

    bids = []
    for j in range(n_bids):
        bundle_size = rng.randint(min_bundle_size, max_bundle_size)
        bundle = sorted(rng.sample(range(n_items), bundle_size))

        # Bid price = sum of item values + mild synergy + noise
        base_value = sum(item_values[i] for i in bundle)
        synergy = rng.uniform(0.0, 8.0) * (bundle_size ** 0.5)
        noise = rng.uniform(-3.0, 3.0)
        price = max(1.0, base_value + synergy + noise)

        bids.append((bundle, price))

    model = gp.Model("mini_ca")
    model.Params.OutputFlag = 0

    x = []
    for j in range(n_bids):
        x_j = model.addVar(vtype=GRB.BINARY, name=f"x{j:04d}")
        x.append(x_j)

    # Maximize accepted bid values.
    model.setObjective(
        gp.quicksum(price * x[j] for j, (_, price) in enumerate(bids)),
        GRB.MAXIMIZE,
    )

    # Each item can be used at most once.
    for item in range(n_items):
        covering_bids = [j for j, (bundle, _) in enumerate(bids) if item in bundle]
        if covering_bids:
            model.addConstr(
                gp.quicksum(x[j] for j in covering_bids) <= 1,
                name=f"item_{item:03d}",
            )

    model.update()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    model.write(str(out_path))


def clean_old_mini_files(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for path in folder.glob("mini_ca_*.lp"):
        path.unlink()


def main() -> None:
    root = Path.home() / "srtp_apollo_mac"
    ps_repo = root / "code" / "Predict-and-Search_MILP_method"

    train_dir = ps_repo / "instance" / "train" / "CA"
    test_dir = ps_repo / "instance" / "CA"

    clean_old_mini_files(train_dir)
    clean_old_mini_files(test_dir)

    # Mac mini reproduction setting.
    n_train = 12
    n_test = 4

    for i in range(n_train):
        generate_ca_instance(
            train_dir / f"mini_ca_train_{i:03d}.lp",
            seed=1000 + i,
            n_items=25,
            n_bids=80,
        )

    for i in range(n_test):
        generate_ca_instance(
            test_dir / f"mini_ca_test_{i:03d}.lp",
            seed=2000 + i,
            n_items=25,
            n_bids=80,
        )

    print("Mini CA instances generated.")
    print(f"Train directory: {train_dir}")
    print(f"Test directory:  {test_dir}")
    print(f"Train files: {len(list(train_dir.glob('mini_ca_*.lp')))}")
    print(f"Test files:  {len(list(test_dir.glob('mini_ca_*.lp')))}")


if __name__ == "__main__":
    main()