import pytest
from api.core.period_detection import detect_period_ct, detect_period_dt
from sympy import pi

def test_detect_period_ct_basic():
    period, msg = detect_period_ct("sin(t)")
    assert pytest.approx(period, 0.01) == 2 * float(pi.evalf())
    
    period, msg = detect_period_ct("sin(2*t)")
    assert pytest.approx(period, 0.01) == float(pi.evalf())

def test_detect_period_ct_abs():
    # |sin(t)| has period pi
    period, msg = detect_period_ct("|sin(t)|")
    assert pytest.approx(period, 0.01) == float(pi.evalf())

def test_detect_period_ct_aperiodic():
    period, msg = detect_period_ct("exp(t)")
    assert period is None
    assert "aperiodic" in msg.lower()

def test_detect_period_dt_basic():
    period, msg = detect_period_dt("cos(2*pi*n/10)")
    assert period == 10
    
    period, msg = detect_period_dt("sin(pi*n/4)")
    assert period == 8

def test_detect_period_dt_complex():
    # (-1)**n is periodic with N=2
    period, msg = detect_period_dt("(-1)**n")
    assert period == 2

def test_detect_period_dt_aperiodic():
    period, msg = detect_period_dt("n")
    assert period is None
