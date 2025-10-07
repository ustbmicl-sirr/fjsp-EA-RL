from typing import Dict, Any
import numpy as np
import networkx as nx

from fjsp.data.instances import Instance


def basic_instance_features(inst: Instance) -> Dict[str, Any]:
    """Compute basic scalar features from an instance."""
    ops = inst.operations
    avail_counts = [len(op.machines) for op in ops]
    times = np.array([t for op in ops for t in op.times], dtype=float)
    return {
        "num_jobs": inst.jobs,
        "num_machines": inst.machines,
        "total_operations": len(ops),
        "avg_available_machines": float(np.mean(avail_counts)) if avail_counts else 0.0,
        "std_available_machines": float(np.std(avail_counts)) if avail_counts else 0.0,
        "processing_time_mean": float(np.mean(times)) if times.size else 0.0,
        "processing_time_std": float(np.std(times)) if times.size else 0.0,
        "processing_time_min": float(np.min(times)) if times.size else 0.0,
        "processing_time_max": float(np.max(times)) if times.size else 0.0,
    }


def disjunctive_graph_features(inst: Instance) -> Dict[str, Any]:
    """Compute simple graph features over a disjunctive-like graph skeleton."""
    g = nx.DiGraph()
    for op in inst.operations:
        node = (op.job_id, op.op_id)
        g.add_node(node)
    for op in inst.operations:
        if op.op_id + 1 < max(o.op_id for o in inst.operations if o.job_id == op.job_id) + 1:
            g.add_edge((op.job_id, op.op_id), (op.job_id, op.op_id + 1))
    degs = [deg for _, deg in g.out_degree()] if g.number_of_nodes() else [0]
    return {
        "graph_num_nodes": g.number_of_nodes(),
        "graph_num_edges": g.number_of_edges(),
        "graph_out_degree_mean": float(np.mean(degs)),
        "graph_out_degree_std": float(np.std(degs)),
    }

