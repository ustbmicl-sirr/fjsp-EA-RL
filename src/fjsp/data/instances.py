from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional


@dataclass
class Operation:
    job_id: int
    op_id: int
    machines: List[int]
    times: List[int]


@dataclass
class Instance:
    name: str
    jobs: int
    machines: int
    operations: List[Operation]


def load_fjsp_instances_index(index_path: Path) -> List[Dict]:
    """Load schedulinglab/fjsp-instances instances.json metadata."""
    import json
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_fjsplib(path: Path) -> Instance:
    """Parse a FJSPLIB-like .txt/.fjs file into an Instance.

    This is a minimal placeholder to be extended to full FJSPLIB coverage.
    """
    name = path.stem
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    header = lines[0].split()
    jobs = int(header[0])
    machines = int(header[1])
    operations: List[Operation] = []
    job_id = 0
    for ln in lines[1:]:
        parts = ln.split()
        k = int(parts[0])
        ptr = 1
        for op_idx in range(k):
            mcount = int(parts[ptr]); ptr += 1
            ms: List[int] = []
            ts: List[int] = []
            for _ in range(mcount):
                m = int(parts[ptr]); t = int(parts[ptr + 1]); ptr += 2
                ms.append(m)
                ts.append(t)
            operations.append(Operation(job_id=job_id, op_id=op_idx, machines=ms, times=ts))
        job_id += 1
    return Instance(name=name, jobs=jobs, machines=machines, operations=operations)

