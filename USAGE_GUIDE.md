# User Guide: How to Use SignalProphet

This guide details how to utilize every feature currently available in the application.

## 1. The Signal Lab

The Signal Lab is your main workspace for defining and visualizing signals.

### Step 1: Choose Your Domain
Use the toggle buttons at the top of the editor:
- **Continuous Time $x(t)$**: For analog signals defined for all $t$. The variable is `t`.
- **Discrete Time $x[n]$**: For sequences defined only at integer `n`. The variable is `n`.

### Step 2: Input Your Signal
Type your mathematical expression in the input box. The parser supports Python-like syntax and standard signal functions.

**Syntax Reference:**

| Math Concept | Syntax to Type | Example |
| :--- | :--- | :--- |
| Unit Step $u(t)$ | `u(t)` or `Heaviside(t)` | `u(t) - u(t-1)` (Rect pulse) |
| Impulse $\delta(t)$ | `d(t)` or `DiracDelta(t)` | `d(t)` |
| Exponential $e^{at}$ | `exp(a*t)` | `exp(-2*t) * u(t)` |
| Trigonometry | `sin()`, `cos()` | `sin(2*pi*t)` |
| Powers | `**` or `^` | `t^2 * u(t)` |

**Common Examples:**
*   **Rectangular Pulse**: `u(t) - u(t-1)`
*   **Decaying Sinusoid**: `exp(-t) * cos(10*t) * u(t)`
*   **Discrete Sequence**: `(0.5)^n * u[n]`

### Step 3: Analyze
Click the **Analyze** button.
1.  **Plot**: The visualizer on the right will render the signal.
    *   *Controls*: You can zoom in by dragging a box, simple-click to reset, or hover to see exact coordinate values.
2.  **Transforms** (Continuous Mode Only):
    *   The app will call the backend to compute the **Laplace** and **Fourier** transforms symbolically.
    *   The result is shown in the "Analysis Results" panel below the editor.
    *   *Note*: If a transform doesn't exist (diverges), the backend may return an error or complex condition.

## 2. Troubleshooting

**"Error Analyzing Signal"**
*   Check your syntax. Did you multiply variables explicitly? E.g., write `2*t` instead of `2t`.
*   Did you use the correct variable (`t` vs `n`)?
*   Is the backend server running? Check your terminal for `python api/main.py`.

**"Visualizer is Empty"**
*   The signal might be outside the default window (-5 to 5).
*   Future updates will include auto-ranging.
