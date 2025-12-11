# SignalProphet: The Signals & Systems Explorer

**SignalProphet** is a comprehensive, interactive web application designed to help students and engineers visualize and analyze signals in both Continuous Time (CT) and Discrete Time (DT). 

Built based on the curriculum of *Signals and Systems* by Oppenheim & Willsky.

![Status](https://img.shields.io/badge/Status-Active-success)
![Stack](https://img.shields.io/badge/Stack-React%20%7C%20FastAPI%20%7C%20SymPy-blue)

## ✨ Features

- **System Analyzer**:
    - Check properties: **Linearity**, **Time-Invariance**, **Causality**, **Memory**, **Stability** (BIBO), **Invertibility**.
    - Calculate **Impulse Response** $h(t)$.
    - Visualize Input $x(t)$, Impulse $h(t)$, and Output $y(t)$.

- **Fourier Series Engine**:
    - **Analysis**: Decompose periodic signals into harmonics ($a_k$).
    - **Visualization**: View Magnitude $|a_k|$ and Phase $\angle a_k$ spectra.
    - Supports both **CTFS** (Continuous) and **DTFS** (Discrete).

- **Fourier Transform Lab**:
    - Compute **CTFT** and **DTFT** symbolically.
    - Visualize Time $\leftrightarrow$ Frequency domains.

- **ROC Explorer**:
    - Interactive **S-Plane** (Laplace) and **Z-Plane** (Z-Transform).
    - Visualize Poles, Zeros, and **Region of Convergence (ROC)**.
    - Auto-determine stability based on ROC location.

- **Convolution Lab**:
    - Animated "Fold, Shift, Multiply, Add" visualization.
    - Step-by-step understanding of the convolution integral/sum.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js & npm

### Installation

1.  **Clone/Open the Repository**
    ```bash
    cd D:\SnS_App
    ```

2.  **Backend Setup**
    ```bash
    # Install Python dependencies
    pip install -r api/requirements.txt
    
    # Start the analysis engine
    python -m api.main
    ```
    *Server will start at `http://localhost:8000`*

3.  **Frontend Setup** (In a new terminal)
    ```bash
    cd web
    
    # Install dependencies
    npm install
    
    # Run the interface
    npm run dev
    ```
    *Open `http://localhost:5173` in your browser.*

## 📂 Project Structure

```
D:\SnS_App/
├── api/                    # Python Analysis Engine
│   ├── core/               # Symbolic math logic (SymPy)
│   │   ├── symbolic.py     # General transforms & parsing
│   │   ├── system_analyzer.py # System properties logic
│   │   └── fourier.py      # Fourier Series engine
│   └── main.py             # FastAPI Routes
├── web/                    # React Frontend
│   ├── src/
│   │   ├── components/     # UI Tools (SystemAnalyzer, FourierSeries, etc.)
│   │   └── App.jsx         # Main Logic & Routing
└── README.md
```

## 📚 References
- **Signals and Systems** (2nd Ed), Oppenheim & Willsky.
- **MIT OpenCourseWare**: 6.003 Signals and Systems.
