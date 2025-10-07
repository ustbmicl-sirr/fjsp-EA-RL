from pathlib import Path
from typing import Dict, Any

from fjsp.data.instances import parse_fjsplib
from fjsp.optimizers.pymoo_nsga2 import NSGA2Runner


def run_single(instance_path: Path, pop: int = 50, n_gen: int = 200) -> Dict[str, Any]:
    inst = parse_fjsplib(instance_path)

    def objective(sol: Any):
        return [0.0]

    runner = NSGA2Runner(objective=objective, pop_size=pop, n_gen=n_gen)
    result = runner.run(init=None)
    result["instance"] = inst.name
    return result


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("instance", type=str, help="Path to FJSP instance file (.fjs/.txt)")
    p.add_argument("--pop", type=int, default=50)
    p.add_argument("--n_gen", type=int, default=200)
    args = p.parse_args()
    res = run_single(Path(args.instance), pop=args.pop, n_gen=args.n_gen)
    print(res)

