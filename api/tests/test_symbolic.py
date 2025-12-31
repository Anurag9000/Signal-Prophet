import pytest
import numpy as np
from sympy import symbols, Heaviside, DiracDelta, exp, sin, pi, Abs
from api.core.symbolic import parse_signal, generate_plot_data, compute_laplace, compute_fourier, compute_inverse_fourier, evaluate_frequency_response

def test_parse_signal_standard():
    # Test standard functions
    expr = parse_signal("sin(t)", "continuous")
    assert str(expr) == "sin(t)"
    
    expr = parse_signal("exp(-t)", "continuous")
    assert str(expr) == "exp(-t)"

def test_parse_signal_abs_notation():
    # Test absolute value notation
    expr = parse_signal("|t|", "continuous")
    assert str(expr) == "Abs(t)"
    
    expr = parse_signal("|sin(t)|", "continuous")
    assert str(expr) == "Abs(sin(t))"
    
    expr = parse_signal("||t|-1|", "continuous")
    assert str(expr) == "Abs(Abs(t) - 1)"

def test_parse_signal_imaginary_units():
    # Test j, i, J, I as imaginary unit
    expr = parse_signal("1 + j*w", "continuous")
    assert "I" in str(expr)
    
    expr = parse_signal("i*w", "continuous")
    assert "I" in str(expr)

def test_parse_signal_aliases():
    # Test u(t) and d(t) aliases
    expr = parse_signal("u(t)", "continuous")
    assert "Heaviside(t)" in str(expr)
    
    expr = parse_signal("d(t)", "continuous")
    assert "DiracDelta(t)" in str(expr)
    
    expr = parse_signal("u[n]", "discrete")
    assert "Heaviside(n)" in str(expr)

def test_parse_signal_new_functions():
    # Test rect, tri, sinc
    expr = parse_signal("rect(t)", "continuous")
    assert "Heaviside" in str(expr)
    
    expr = parse_signal("tri(t)", "continuous")
    assert "Max(0, 1 - Abs(t))" in str(expr)
    
    expr = parse_signal("sinc(t)", "continuous")
    assert "sinc(t)" in str(expr)

def test_generate_plot_data_ct():
    x, y = generate_plot_data("sin(t)", -5, 5, num_points=100)
    assert len(x) == 100
    assert len(y) == 100
    assert np.isclose(y[50], 0, atol=0.1) # sin(0) = 0 (middle point)

def test_generate_plot_data_dt():
    x, y = generate_plot_data("u[n]", -5, 5, domain="discrete")
    # n = -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5 -> 11 points
    assert len(x) == 11
    assert y[5] == 1.0 # u[0]
    assert y[4] == 0.0 # u[-1]

def test_compute_laplace():
    res = compute_laplace("exp(-t)*u(t)")
    # L{e^-t u(t)} = 1/(s+1)
    assert "1/(s + 1)" in res

def test_compute_fourier():
    res = compute_fourier("exp(-t)*u(t)")
    # F{e^-t u(t)} = 1/(1 + jw)
    assert "1/" in res
    assert "j" in res # We replace I with j in the function

def test_compute_inverse_fourier_ct():
    # Test standard form detection
    res = compute_inverse_fourier("1/(j*w + 1)", "continuous")
    assert "exp(-t)" in res
    assert "u(t)" in res

def test_evaluate_frequency_response():
    resp = evaluate_frequency_response("1/(1 + j*w)", w_min=-5, w_max=5)
    assert "magnitude" in resp
    assert "phase" in resp
    assert len(resp["magnitude"]["x"]) == 400
    # At w=0, 1/(1+0) = 1
    assert pytest.approx(resp["magnitude"]["y"][200], 0.01) == 1.0
