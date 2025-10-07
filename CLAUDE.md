# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a research codebase for Flexible Job Shop Scheduling Problem (FJSP) that combines evolutionary algorithms, reinforcement learning, and meta-learning approaches. The project consists of two main systems:

1. **Core research framework** (`src/fjsp/`): Minimal skeleton for feature engineering, strategy recommendation, and optimization
2. **Unified FJSP system** (`unified_fjsp_system/`): Production-ready system integrating multiple libraries (JobShopLib, Schlably, Graph-JSP-Env) with web visualization

## Commands

### Development & Testing

```bash
# Install core dependencies (required)
pip install numpy pandas matplotlib plotly streamlit networkx

# Install full dependencies including optional libraries
pip install -r unified_fjsp_system/requirements.txt

# Test the unified system
cd unified_fjsp_system
python test_system.py

# Run basic example
python examples/basic_usage.py

# Run NSGA-II example (requires local FJSP instance file)
python examples/run_nsga2_example.py
```

### Web Interface

```bash
# Launch Streamlit web application
cd unified_fjsp_system
streamlit run web/streamlit_app.py

# Alternative: use the launcher script
python run_web_app.py

# Custom port
python run_web_app.py --port 8080
```

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/test_data_adapter.py -v

# Generate coverage report
pytest --cov=unified_fjsp_system tests/
```

## Architecture

### Two-System Design

The codebase is organized into two complementary systems:

**Research Framework (`src/fjsp/`)**: Lightweight skeleton for algorithm development
- `data/`: FJSP instance loading and representation
- `features/`: Feature extractors (basic instance features, disjunctive graph features)
- `recommend/`: Strategy recommendation (similarity-weighted, Pareto front, Thompson Sampling)
- `optimizers/`: Optimization algorithms (NSGA-II via pymoo, BWO)
- `metrics/`: Performance indicators
- `experiments/`: Experiment runners
- `vis/`: Visualization utilities

**Unified System (`unified_fjsp_system/`)**: Integrated production system
- `core/data_adapter.py`: Unified data format and conversion between JobShopLib, Schlably, Graph-JSP-Env
- `algorithms/unified_solver.py`: Multi-algorithm solver manager (evolutionary, RL, constraint programming)
- `visualization/unified_visualizer.py`: Interactive Gantt charts, disjunctive graphs, convergence plots
- `web/`: Streamlit frontend and Flask backend API

### Key Components

**Data Flow**: User input → Instance generation/loading → Unified format → Algorithm solving → Visualization

**DataAdapter** (unified_fjsp_system/core/data_adapter.py):
- Converts between library-specific formats and `UnifiedFJSPInstance`
- Builds disjunctive graphs with NetworkX
- Generates random FJSP instances

**UnifiedSolverManager** (unified_fjsp_system/algorithms/unified_solver.py):
- Base class `BaseSolver` for all algorithms
- Implementations: `EvolutionaryAlgorithmSolver`, `ReinforcementLearningSolver`, `JobShopLibSolver`
- Parallel solving with `solve_parallel()`
- Real-time callbacks for monitoring

**UnifiedVisualizer** (unified_fjsp_system/visualization/unified_visualizer.py):
- Plotly-based interactive visualizations
- Gantt charts, disjunctive graphs, convergence curves
- Algorithm comparison dashboards

### Research Framework Design

The `src/fjsp/` framework follows a pipeline architecture:

1. **Feature Extraction**: Extract instance characteristics (basic features, graph features)
2. **Strategy Recommendation**: Select initialization strategies based on historical performance
3. **Optimization**: Run meta-heuristic algorithms (NSGA-II, BWO) with recommended strategies
4. **Evaluation**: Multi-objective metrics (makespan, convergence, stability)

Key abstractions:
- `Instance`: Core FJSP instance representation (src/fjsp/data/instances.py)
- Feature extractors return `Dict[str, Any]` with numeric features
- Recommenders return `List[Candidate]` with strategy metadata
- Optimizers follow the pattern: `run(init) -> Dict[str, Any]`

## Development Guidelines

### Adding New Algorithms

To add a new solver to the unified system:

```python
from algorithms.unified_solver import BaseSolver, SolutionResult

class CustomSolver(BaseSolver):
    def __init__(self):
        super().__init__("CustomAlgorithm")

    def solve(self, instance: UnifiedFJSPInstance, **kwargs) -> SolutionResult:
        # Implementation here
        return SolutionResult(
            schedule={},
            makespan=0.0,
            objectives={},
            algorithm=self.name,
            computation_time=0.0
        )

# Register in UnifiedSolverManager
manager = UnifiedSolverManager()
manager.solvers['custom'] = CustomSolver()
```

### Working with Data Formats

The system uses `UnifiedFJSPInstance` as the standard format. Convert between formats:

```python
from core.data_adapter import DataAdapter

# JobShopLib → Unified
unified = DataAdapter.from_jobshoplib(jsl_instance)

# Unified → JobShopLib
jsl_instance = DataAdapter.to_jobshoplib(unified)

# Build disjunctive graph
graph = DataAdapter.build_disjunctive_graph(unified)
```

### Optional Dependencies

The system gracefully handles missing dependencies:
- Core functionality works with basic dependencies (numpy, pandas, matplotlib, plotly, streamlit, networkx)
- Advanced features require: `job-shop-lib`, `ortools`, `gymnasium`, `stable-baselines3`, `graph-jsp-env`
- Check availability: `python -c "import unified_fjsp_system; unified_fjsp_system.print_system_info()"`

### File Locations

- FJSP instance files: Typically `.fjs` format (e.g., Mk01.fjs from Brandimarte benchmark)
- Configuration: `unified_fjsp_system/requirements.txt` for dependencies
- Examples: `examples/` (research framework) and `unified_fjsp_system/examples/` (unified system)
- Documentation: `docs/` (Chinese documentation for software design, API reference, project structure)

## Research Context

The project implements a hybrid approach for FJSP:
- **Multi-objective optimization**: Minimize makespan, improve convergence, ensure stability
- **Meta-learning**: Instance feature-based strategy recommendation
- **Hybrid algorithms**: Combines evolutionary algorithms (BWO, NSGA-II) with RL-based initialization
- **Benchmark datasets**: Brandimarte (Mk series), Hurink, Kacem instances

The research explores "evolution + reinforcement learning" where RL/meta-learning provides better initial populations for meta-heuristic algorithms.
