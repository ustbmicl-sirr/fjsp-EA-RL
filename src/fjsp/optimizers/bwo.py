from typing import Any, Dict


class BWORunner:
    def __init__(self, pop_size: int = 50, n_gen: int = 200) -> None:
        self.pop_size = pop_size
        self.n_gen = n_gen

    def run(self, init: Any) -> Dict[str, Any]:
        """Skeleton for discrete BWO adapted to FJSP encoding.

        To implement: reproduction, cannibalism with elitism, mutation, and selection.
        """
        return {"best_f": None, "history": [], "pop_size": self.pop_size, "n_gen": self.n_gen}

