import pytest
import numpy as np
from api.core.fourier import calculate_ctfs, calculate_dtfs, calculate_inverse_ctfs

def test_calculate_ctfs():
    # Test CTFS for sin(t) with T = 2*pi
    # x(t) = sin(t) = (e^jt - e^-jt)/(2j)
    # a_1 = 1/(2j) = -0.5j, a_-1 = -1/(2j) = 0.5j
    coeffs = calculate_ctfs("sin(t)", float(2*np.pi), k_min=-2, k_max=2)
    
    assert len(coeffs) == 5 # -2, -1, 0, 1, 2
    
    # k = 1
    a1 = next(c for c in coeffs if c["k"] == 1)
    assert pytest.approx(a1["magnitude"], 0.01) == 0.5
    
    # k = 0
    a0 = next(c for c in coeffs if c["k"] == 0)
    assert pytest.approx(a0["magnitude"], 0.01) == 0

def test_calculate_dtfs():
    # Test DTFS for cos(2*pi*n/4) with N = 4
    # x[n] = cos(pi*n/2) = [1, 0, -1, 0]
    # a_k = 1/4 * sum(x[n] * e^-jk*pi*n/2)
    # a_1 = 1/4 * (1*e^0 + 0 - 1*e^-j*pi + 0) = 1/4 * (1 + 1) = 0.5
    # a_3 = a_-1 = 0.5
    coeffs = calculate_dtfs("cos(2*pi*n/4)", 4)
    
    assert len(coeffs) == 4
    
    a1 = next(c for c in coeffs if c["k"] == 1)
    assert np.isclose(a1["magnitude"], 0.5)
    
    a3 = next(c for c in coeffs if c["k"] == 3)
    assert np.isclose(a3["magnitude"], 0.5)

def test_calculate_inverse_ctfs():
    # Test synthesis from ak = 1 for k=0 and 0 otherwise
    # x(t) = 1
    xt_expr = calculate_inverse_ctfs("1", 6.28, k_min=0, k_max=0)
    assert "1" in str(xt_expr)
    
    # Test synthesis from ak = (1 if k==1 else 0)
    # x(t) = exp(j*w0*t)
    xt_expr = calculate_inverse_ctfs("k", 6.28, k_min=1, k_max=1)
    assert "exp" in str(xt_expr)
    assert "I" in str(xt_expr)
    assert "t" in str(xt_expr)
