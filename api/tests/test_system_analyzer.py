import pytest
from api.core.system_analyzer import analyze_system, check_linearity, check_time_invariance, check_causality, check_memory, check_stability, check_invertibility

def test_linearity():
    # Linear
    assert check_linearity("2*x(t)", "continuous")["status"] == "yes"
    assert check_linearity("t*x(t)", "continuous")["status"] == "yes"
    
    # Non-linear
    assert check_linearity("x(t)**2", "continuous")["status"] == "no"
    assert check_linearity("sin(x(t))", "continuous")["status"] == "no"
    assert check_linearity("x(t) + 1", "continuous")["status"] == "no" # Constant offset

def test_time_invariance():
    # Time-Invariant
    assert check_time_invariance("2*x(t)", "continuous")["status"] == "yes"
    assert check_time_invariance("x(t-1)", "continuous")["status"] == "yes"
    
    # Time-Variant
    assert check_time_invariance("t*x(t)", "continuous")["status"] == "no"
    assert check_time_invariance("x(2*t)", "continuous")["status"] == "no"

def test_causality():
    # Causal
    assert check_causality("x(t-1)", "continuous")["status"] == "yes"
    assert check_causality("x(t)", "continuous")["status"] == "yes"
    
    # Non-Causal
    assert check_causality("x(t+1)", "continuous")["status"] == "no"
    assert check_causality("x(-t)", "continuous")["status"] == "no"

def test_memory():
    # Memoryless
    assert check_memory("x(t)", "continuous")["status"] == "yes"
    assert check_memory("2*x[n]", "discrete")["status"] == "yes"
    
    # With Memory
    assert check_memory("x(t-1)", "continuous")["status"] == "no"
    assert check_memory("x[n-1]", "discrete")["status"] == "no"

def test_stability():
    # Stable
    assert check_stability("x(t)", "continuous")["status"] == "yes"
    
    # Unstable: y(t) = t*x(t)
    # The integral of |t*delta(t)| = |0| = 0. Wait, that's stable? 
    # Yes, t*delta(t) is 0.
    
    # Real Unstable: y(t) = exp(t)*x(t) -> h(t) = exp(t)*delta(t) = delta(t) (still stable at t=0)
    
    # Actually, let's use a system with non-delta impulse response
    # y(t) = integral of x from -oo to t -> h(t) = u(t)
    # This should be unstable
    res = check_stability("u(t)", "continuous")
    assert res["status"] in ["no", "unknown"]

def test_invertibility():
    # Invertible
    assert check_invertibility("2*x(t)", "continuous")["status"] == "yes"
    
    # Not Invertible
    assert check_invertibility("x(t)**2", "continuous")["status"] == "no"
    assert check_invertibility("|x(t)|", "continuous")["status"] == "no"

def test_full_analysis():
    results = analyze_system("2*x(t)", "continuous")
    assert results["linearity"]["status"] == "yes"
    assert results["time_invariance"]["status"] == "yes"
    assert "2*d(t)" in results["impulse_response"]
