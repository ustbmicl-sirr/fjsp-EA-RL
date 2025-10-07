from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import numpy as np


@dataclass
class Candidate:
    name: str
    metrics: Dict[str, float]
    meta: Dict[str, Any]


def similarity_weighted_selection(target_feat: Dict[str, float], 
                                  pool: List[Tuple[Dict[str, float], Candidate]], 
                                  top_k: int = 5) -> List[Candidate]:
    names: List[Tuple[float, Candidate]] = []
    tf = np.array(list(target_feat.values()), dtype=float)
    for feats, cand in pool:
        cf = np.array(list(feats.values()), dtype=float)
        n = min(tf.size, cf.size)
        if n == 0:
            score = 0.0
        else:
            score = float(np.dot(tf[:n], cf[:n]) / (np.linalg.norm(tf[:n]) * np.linalg.norm(cf[:n]) + 1e-8))
        names.append((score, cand))
    names.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in names[:top_k]]


def pareto_front_selection(cands: List[Candidate], objectives: List[str]) -> List[Candidate]:
    front: List[Candidate] = []
    for i, a in enumerate(cands):
        dominated = False
        for j, b in enumerate(cands):
            if i == j:
                continue
            if _dominates(b, a, objectives):
                dominated = True
                break
        if not dominated:
            front.append(a)
    return front


def _dominates(a: Candidate, b: Candidate, objectives: List[str]) -> bool:
    better_or_equal = all(a.metrics[obj] <= b.metrics[obj] for obj in objectives)
    strictly_better = any(a.metrics[obj] < b.metrics[obj] for obj in objectives)
    return better_or_equal and strictly_better


class ThompsonWeight:
    def __init__(self, alpha: float = 1.0, beta: float = 1.0) -> None:
        self.alpha = alpha
        self.beta = beta

    def sample(self) -> float:
        return np.random.beta(self.alpha, self.beta)

    def update(self, success: bool) -> None:
        self.alpha += 1.0 if success else 0.0
        self.beta += 0.0 if success else 1.0

