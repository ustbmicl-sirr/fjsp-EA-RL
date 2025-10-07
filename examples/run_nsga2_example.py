from pathlib import Path
from fjsp.experiments.run_experiment import run_single


def main() -> None:
    # Replace with a local instance path
    path = Path("./Mk01.fjs")
    if not path.exists():
        print("Provide a valid FJSP instance file path.")
        return
    res = run_single(path)
    print(res)


if __name__ == "__main__":
    main()

