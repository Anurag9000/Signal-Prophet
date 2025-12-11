"""
Convolution Visualizer (Continuous-Time, Numeric)

- Parses symbolic inputs x(t), h(t) entered as strings (restricted safe syntax).
- Supports implicit multiplication (e.g., 2d(t+1), (t+1)(u(t)-u(t-1))).
- Approximates the Dirac delta δ(t) by a rectangle whose width equals the τ-grid step,
  ensuring ∫ δ(t) dt ≈ 1 under the trapezoidal rule.
- Automatically selects t, τ ranges to cover supports of x, h, and y = x*h,
  with optional user overrides at the prompt.
- Produces an animated GIF that shows sliding functions and the building of y(t).

Author: (you)
"""

from __future__ import annotations

import os
import sys
import re
import platform
import subprocess
import time
import webbrowser
from typing import Callable, Optional, Tuple

import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


# =============================================================================
# Signal primitives
# =============================================================================

def u(t: np.ndarray | float) -> np.ndarray:
    """
    Unit step function with u(0) = 1.

    Parameters
    ----------
    t : array-like or float
        Input variable.

    Returns
    -------
    ndarray
        Array of 0/1 with u(0) = 1.
    """
    t = np.asarray(t)
    out = np.zeros_like(t, dtype=float)
    out[t > 0] = 1.0
    out[t == 0] = 1.0
    return out


# Global delta width set from the τ-grid; used by d(t).
DELTA_WIDTH: Optional[float] = None


def configure_delta_from_grid(tau: np.ndarray) -> None:
    """
    Configure the Dirac approximation width from the τ-grid.

    The rectangle width equals the sampling step so that the trapezoidal
    integration of δ approximates area 1 independent of resolution.

    Parameters
    ----------
    tau : ndarray
        τ-grid used for numeric integration.
    """
    global DELTA_WIDTH
    DELTA_WIDTH = float(abs(tau[1] - tau[0]))


def d(t: np.ndarray | float, width: Optional[float] = None) -> np.ndarray:
    """
    Dirac delta approximation suitable for numeric integration.

    A rectangle of width `width` (default: global DELTA_WIDTH) and height 1/width,
    centered at zero: returns 1/width for |t| <= width/2, else 0.
    With trapezoidal integration, ∫ δ(t) dt ≈ 1.

    Parameters
    ----------
    t : array-like or float
        Input variable.
    width : float, optional
        Rectangle width. If None, uses the configured DELTA_WIDTH.

    Returns
    -------
    ndarray
        Samples of the approximate δ(t).
    """
    w = width if width is not None else DELTA_WIDTH
    if w is None:
        raise RuntimeError("Call configure_delta_from_grid(tau) after creating τ-grid before using d(t).")
    t = np.asarray(t, dtype=float)
    return (np.abs(t) <= (0.5 * w)).astype(float) / w


# =============================================================================
# System utilities
# =============================================================================

def open_file(path: str) -> None:
    """
    Cross-platform attempt to open a file with the default viewer.

    Parameters
    ----------
    path : str
        File path to open.
    """
    abs_path = os.path.abspath(path)
    print(f"[open_file] Attempting to open: {abs_path}")
    time.sleep(0.25)
    if not os.path.exists(abs_path):
        print(f"[open_file] File does not exist: {abs_path}")
        return

    try:
        sysname = platform.system()
        if sysname == "Windows":
            try:
                os.startfile(abs_path)  # type: ignore[attr-defined]
                return
            except Exception as e1:
                print(f"[open_file] os.startfile failed: {e1}")
            try:
                subprocess.run(["cmd", "/c", "start", "", abs_path],
                               check=False, shell=False,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                return
            except Exception as e2:
                print(f"[open_file] cmd start failed: {e2}")
            webbrowser.open(f"file:///{abs_path.replace(os.sep, '/')}")
        elif sysname == "Darwin":
            subprocess.Popen(["open", abs_path])
        else:
            try:
                subprocess.Popen(["xdg-open", abs_path])
            except Exception as e3:
                print(f"[open_file] xdg-open failed: {e3}")
                webbrowser.open(f"file://{abs_path}")
    except Exception as e:
        print(f"[open_file] Unhandled open error: {e}")
        print(f"[open_file] You can open it manually: {abs_path}")


# =============================================================================
# Expression parsing and safe evaluation
# =============================================================================

ALLOWED_NAMES = {
    # Math / signals exposed to the user
    "exp": np.exp,
    "u": u,
    "d": d,
    "pi": np.pi,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "arctan": np.arctan,
    "log": np.log,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "sign": np.sign,
}

SAFE_GLOBALS = {"__builtins__": {}}


def preprocess_expr(expr: str) -> str:
    """
    Preprocess a 1D expression string for safe eval and friendlier syntax.

    Normalizes:
    - Forbids 'np.' usage (use the provided names instead).
    - '^' to '**' for exponentiation.
    - Implicit multiplication in the following cases ONLY:
        * 2t, -3t                -> 2*t, -3*t
        * )t                     -> )*t
        * t(                     -> t*(
        * t2                     -> t*2   (NOTE: no sign; won't touch t+2 or t-2)
        * number or ')' before function/constant name (2d(...), )u(...), 2pi -> insert '*'
        * ')('                   -> ')*('
    """
    if "np." in expr:
        raise ValueError("Use exp(...), u(...), d(...); 'np.*' is not allowed.")

    s = expr.strip()
    s = s.replace("^", "**")

    # number (optionally signed) directly before 't' -> insert '*', e.g., 3t -> 3*t, -2t -> -2*t
    s = re.sub(r'(?<![A-Za-z0-9_\.])([+-]?\d+(?:\.\d+)?)(\s*)t\b', r'\1*\2t', s)

    # ')t' -> ')*t'
    s = re.sub(r'\)(\s*)t\b', r')*\1t', s)

    # 't(' -> 't*('
    s = re.sub(r'\bt(\s*)\(', r't*\1(', s)

    # 't2' (no sign!) -> 't*2'.  DO NOT touch t+2 or t-2.
    s = re.sub(r'\bt(\s*)(\d+(?:\.\d+)?)\b', r't*\1\2', s)

    # number or ')' followed by function/constant name -> insert '*'
    func_names = r'(?:u|d|exp|sin|cos|tan|arctan|log|sqrt|abs|sign|pi)'
    s = re.sub(rf'(?<=[0-9\)])\s*(?={func_names}\b)', '*', s)

    # ')(' -> ')*('
    s = re.sub(r'\)\s*\(', ')*(', s)

    return s

def make_fn(expr: str):
    try:
        pre = preprocess_expr(expr)
        print(f"[parse] {expr}  ->  {pre}")   # DEBUG: see the exact expression Python will eval
        code = compile(f"lambda t: {pre}", "<expr>", "eval")
        safe_globals = {"__builtins__": {}}
        safe_globals.update(ALLOWED_NAMES)
        return eval(code, safe_globals, {})
    except Exception as e:
        print(f"Invalid function: {expr}\n{e}")
        sys.exit(1)


# =============================================================================
# Auto range selection
# =============================================================================

def _estimate_support_of(fn: Callable[[np.ndarray], np.ndarray],
                         lo: float = -20.0, hi: float = 20.0,
                         N: int = 4000, tol: float = 1e-6,
                         temp_delta: float = 1e-2) -> Optional[Tuple[float, float]]:
    """
    Estimate finite support of a function by thresholding |f| > tol on [lo, hi].

    Uses a temporary DELTA_WIDTH so that d(·) evaluates meaningfully.

    Parameters
    ----------
    fn : callable
        Function of one variable.
    lo, hi : float
        Scan interval.
    N : int
        Number of samples.
    tol : float
        Magnitude threshold for 'non-zero'.
    temp_delta : float
        Temporary width for Dirac approximation during scanning.

    Returns
    -------
    (a, b) or None
        Bounds where function appears nonzero; None if no samples exceed tol.
    """
    global DELTA_WIDTH
    old = DELTA_WIDTH
    DELTA_WIDTH = temp_delta
    grid = np.linspace(lo, hi, N)
    try:
        vals = np.asarray(fn(grid), dtype=float)
    finally:
        DELTA_WIDTH = old

    idx = np.where(np.abs(vals) > tol)[0]
    if idx.size == 0:
        return None
    return float(grid[int(idx[0])]), float(grid[int(idx[-1])])


def _expand(a: float, b: float, frac: float = 0.12, min_pad: float = 0.5) -> Tuple[float, float]:
    """
    Expand an interval [a, b] by a relative fraction and/or minimum padding.
    """
    span = max(1e-9, b - a)
    pad = max(min_pad, frac * span)
    return a - pad, b + pad


def pick_ranges_auto(x_fn: Callable[[np.ndarray], np.ndarray],
                     h_fn: Callable[[np.ndarray], np.ndarray]) -> Tuple[float, float, float, float]:
    """
    Choose plotting/integration ranges automatically.

    τ-range covers the union of supports of x(τ) and h(τ).
    t-range covers the Minkowski sum of supports: supp(y) ⊆ supp(x) + supp(h).

    Parameters
    ----------
    x_fn, h_fn : callable
        Signal functions.

    Returns
    -------
    T_MIN, T_MAX, TAU_MIN, TAU_MAX : floats
        Suggested bounds with safety margins. If no support detected,
        defaults to (-2, 6, -2, 6).
    """
    sx = _estimate_support_of(x_fn)
    sh = _estimate_support_of(h_fn)

    if sx is None and sh is None:
        return -2.0, 6.0, -2.0, 6.0

    ax, bx = (0.0, 0.0) if sx is None else sx
    ah, bh = (0.0, 0.0) if sh is None else sh

    tau_min, tau_max = _expand(min(ax, ah), max(bx, bh))
    t_min_raw, t_max_raw = ax + ah, bx + bh
    t_min, t_max = _expand(t_min_raw, t_max_raw)

    return t_min, t_max, tau_min, tau_max


# =============================================================================
# Main program
# =============================================================================

def main() -> None:
    """Command-line entry point."""
    X_EXPR = input("x(t): ").strip()
    H_EXPR = input("h(t): ").strip()

    # Compile once
    x_fn = make_fn(X_EXPR)
    h_fn = make_fn(H_EXPR)
    # DEBUG: probe values to confirm windowing
    probe = np.array([-1.0, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0])
    print("[probe] t:", probe)
    print("[probe] x(t):", x_fn(probe))

    # Auto ranges with optional user override
    auto_T_MIN, auto_T_MAX, auto_TAU_MIN, auto_TAU_MAX = pick_ranges_auto(x_fn, h_fn)

    def read_float_with_default(prompt: str, default: float) -> float:
        s = input(f"{prompt} [auto {default:.3f}]: ").strip()
        return float(s) if s else default

    fps_in = input("FPS for GIF [default 12]: ").strip()
    FPS = int(fps_in) if fps_in else 12

    T_MIN = read_float_with_default("tmin", auto_T_MIN)
    T_MAX = read_float_with_default("tmax", auto_T_MAX)
    TAU_MIN = read_float_with_default("taumin", auto_TAU_MIN)
    TAU_MAX = read_float_with_default("taumax", auto_TAU_MAX)

    if not (T_MIN < T_MAX and TAU_MIN < TAU_MAX):
        print("Range error: require tmin < tmax and taumin < taumax")
        sys.exit(1)

    # Discretization
    N_T = 240
    N_TAU = 800
    FRAMES = 120

    # Grids
    t = np.linspace(T_MIN, T_MAX, N_T)
    tau = np.linspace(TAU_MIN, TAU_MAX, N_TAU)

    # Configure δ width from τ-grid
    configure_delta_from_grid(tau)

    # Pre-evaluate on τ
    X_tau = x_fn(tau)
    H_tau = h_fn(tau)

    # Convolution via trapezoidal integration (two equivalent forms)
    y = np.zeros_like(t)
    for i, ti in enumerate(t):
        y[i] = np.trapezoid(X_tau * h_fn(ti - tau), tau)
        # The alternative symmetric form below is numerically similar:
        # y[i] = np.trapezoid(H_tau * x_fn(ti - tau), tau)

    # Prepare animation
    idx = np.linspace(0, len(t) - 1, FRAMES).astype(int)
    t_anim = t[idx]

    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 2)
    axA = fig.add_subplot(gs[0, 0])
    axB = fig.add_subplot(gs[0, 1])
    axY = fig.add_subplot(gs[1, :])

    # Panel A: x(τ) and sliding h(t-τ)
    axA.plot(tau, X_tau, label="x(τ)")
    line_hA, = axA.plot([], [], label="h(t-τ)")
    axA.legend()
    axA.set_title("x(τ) and sliding h(t-τ)")
    axA.grid(True)

    # Panel B: h(τ) and sliding x(t-τ)
    axB.plot(tau, H_tau, label="h(τ)")
    line_xB, = axB.plot([], [], label="x(t-τ)")
    axB.legend()
    axB.set_title("h(τ) and sliding x(t-τ)")
    axB.grid(True)

    # Panel C: output y(t)
    axY.plot(t, y, label="y(t)")
    prog, = axY.plot([], [], "--", label="forming")
    dot, = axY.plot([], [], "o")
    axY.legend()
    axY.set_title("Convolution output y(t)")
    axY.grid(True)

    def update(k: int):
        """Animation step for time index k."""
        ti = t_anim[k]
        line_hA.set_data(tau, h_fn(ti - tau))
        line_xB.set_data(tau, x_fn(ti - tau))
        j = np.searchsorted(t, ti)
        prog.set_data(t[:j + 1], y[:j + 1])
        dot.set_data([ti], [y[j]])
        return line_hA, line_xB, prog, dot

    anim = FuncAnimation(fig, update, frames=len(t_anim),
                         interval=1000 / FPS, blit=False)

    # Output
    out_dir = "results"
    os.makedirs(out_dir, exist_ok=True)
    gif_path = os.path.join(out_dir, "conv.gif")
    anim.save(gif_path, writer=PillowWriter(fps=FPS))
    plt.close(fig)

    print(f"Saved GIF to {gif_path}")
    open_file(gif_path)


if __name__ == "__main__":
    main()
