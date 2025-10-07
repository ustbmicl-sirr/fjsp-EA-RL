from typing import List, Dict


def makespan(schedule: List[List[int]]) -> int:
    """Placeholder makespan computation from a schedule representation."""
    return 0


def summarize_objectives(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
    import numpy as np
    arr = np.array(values, dtype=float)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }

