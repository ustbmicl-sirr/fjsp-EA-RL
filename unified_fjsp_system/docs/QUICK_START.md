# 🚀 Quick Start Guide

## 📦 Installation

### 1. Basic Installation (Required)
```bash
pip install numpy pandas matplotlib plotly streamlit networkx
```

### 2. Optional Libraries (Enhanced Features)
```bash
# JobShopLib - Constraint programming and metaheuristics
pip install job-shop-lib

# OR-Tools - Advanced constraint programming
pip install ortools

# Reinforcement Learning
pip install gymnasium stable-baselines3

# Graph-JSP-Env (if available)
pip install graph-jsp-env
```

### 3. All Dependencies
```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Quick Test

```bash
# Test if everything works
python test_system.py
```

## 🌐 Web Interface

```bash
# Launch the web application
python run_web_app.py

# Or specify custom port
python run_web_app.py --port 8080
```

Then open your browser to `http://localhost:8501`

## 💻 Command Line Usage

```bash
# Run basic example
python examples/basic_usage.py
```

## 🐍 Python API

```python
from core.data_adapter import InstanceGenerator
from algorithms.unified_solver import UnifiedSolverManager
from visualization.unified_visualizer import UnifiedVisualizer

# 1. Generate FJSP instance
instance = InstanceGenerator.generate_random_fjsp(
    num_jobs=3, 
    num_machines=3, 
    max_operations_per_job=3
)

# 2. Solve with multiple algorithms
manager = UnifiedSolverManager()
results = manager.solve_parallel(
    instance, 
    algorithms=['evolutionary']
)

# 3. Visualize results
visualizer = UnifiedVisualizer()
for alg, result in results.items():
    fig = visualizer.plot_gantt_chart(instance, result)
    fig.show()
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the right directory
   cd unified_fjsp_system
   python test_system.py
   ```

2. **Missing Dependencies**
   ```bash
   # Install basic requirements
   pip install numpy pandas matplotlib plotly streamlit networkx
   ```

3. **Web App Won't Start**
   ```bash
   # Check if streamlit is installed
   pip install streamlit
   
   # Try different port
   python run_web_app.py --port 8080
   ```

### Dependency Check
```bash
# Check what's available
python -c "import unified_fjsp_system; unified_fjsp_system.print_system_info()"
```

## 📊 Features Overview

### ✅ Always Available (Basic Dependencies)
- Random FJSP instance generation
- Evolutionary algorithm solver
- Disjunctive graph construction
- Basic visualization (Gantt charts, graphs)
- Web interface

### 🔧 Enhanced Features (Optional Dependencies)
- JobShopLib integration (constraint programming, metaheuristics)
- OR-Tools CP-SAT solver
- Reinforcement learning environments
- Advanced RL algorithms
- Benchmark instance loading

## 🎯 Next Steps

1. **Try the Web Interface**: `python run_web_app.py`
2. **Run Examples**: `python examples/basic_usage.py`
3. **Read Full Documentation**: See `README.md`
4. **Customize Algorithms**: Modify files in `algorithms/`
5. **Add Visualizations**: Extend `visualization/unified_visualizer.py`

## 📞 Need Help?

- Check `README.md` for detailed documentation
- Run `python test_system.py` to diagnose issues
- Look at examples in `examples/` directory
