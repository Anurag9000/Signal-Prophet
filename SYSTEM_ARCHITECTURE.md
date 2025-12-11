# SignalProphet - Complete System Architecture

**Version**: 2.0  
**Last Updated**: 2025-12-11  

---

## System Overview

**SignalProphet** is a web-based educational suite for **Signals & Systems**.

### Core Modules
1.  **System Analyzer**: Determining system properties (Linearity, Stability, etc.).
2.  **Fourier Series**: Harmonic decomposition of periodic signals.
3.  **Transforms**: Laplace, Fourier (CT/DT), Z-Transform.
4.  **Convolution**: Time-domain simulation.

### Tech Stack
-   **Backend**: Python FastAPI, SymPy (Math), NumPy (Numerics).
-   **Frontend**: React (Vite), TailwindCSS, Recharts/Plotly.

---

## Architecture

### Backend Structure (`api/`)

#### 1. `api/main.py`
The API Gateway. Routes requests to specific core modules.
-   `POST /analyze_system` -> `system_analyzer.py`
-   `POST /fourier/analyze` -> `fourier.py`
-   `POST /plot` -> `symbolic.py`

#### 2. `api/core/symbolic.py` (The Mathematical Foundation)
-   `parse_signal(str)`: Converts user strings (e.g., `u(t)`) to SymPy expressions.
-   `generate_plot_data`: Evaluates expressions for plotting.
-   Handles Transforms (Laplace, Fourier, Z).

#### 3. `api/core/system_analyzer.py` (New in v2.0)
-   `analyze_system(equation)`:
    -   Parses `y(t)` vs `x(t)` relationship.
    -   Checks Linearity (Superposition principle).
    -   Checks Time-Invariance (Shift invariance).
    -   Checks Causality (Dependence on future inputs).
    -   **BIBO Stability**: Calculates Impulse Response $h(t)$ and integrates $|h(t)|$.

#### 4. `api/core/fourier.py` (New in v2.0)
-   `calculate_ctfs(x, T)`: Symbolic integration for $a_k$.
-   `calculate_dtfs(x, N)`: Discrete summation for $a_k$.

---

## Frontend Structure (`web/`)

### `App.jsx`
The detailed "Home Page" and Tab Router.
-   Home: Feature cards + References.
-   Tabs: System Analyzer, ROC, Convolution, Fourier Series, Fourier Transform.

### Components
-   `SystemAnalyzer.jsx`: UI for checking properties and plotting $h(t)$, $y(t)$.
-   `FourierSeries.jsx`: Dual-domain Analysis tool (Spectrum visualization).
-   `ROCExplorer.jsx`: Interactive Pole-Zero plot.
-   `Visualizer.jsx`: Reusable charting component.

---

## Data Flow (Example: System Analysis)

1.  **User** enters `y(t) = x(t) + x(t-1)` in `SystemAnalyzer.jsx`.
2.  **Frontend** sends `POST /analyze_system`.
3.  **Backend** (`system_analyzer.py`):
    -   Substitutes $x(t) \to \delta(t)$ to find $h(t) = \delta(t) + \delta(t-1)$.
    -   Checks Stability: $\int |h(t)| dt = 2 < \infty$ -> **Stable**.
    -   Checks Causality: $h(t) = 0$ for $t<0$ -> **Causal**.
4.  **Backend** returns JSON `{ "properties": {...}, "impulse_response": "...", "plots": {...} }`.
5.  **Frontend** renders the Property Table and Impulse Response Graph.

---
