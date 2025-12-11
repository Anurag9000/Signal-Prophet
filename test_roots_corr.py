from sympy import symbols, parse_expr, roots, fraction, Poly

def test_roots_corrected():
    s = symbols('s')
    # Test case: (s+1)^2 -> multiplicity 2
    expr_str = "1/(s+1)**2"
    expr = parse_expr(expr_str)
    numer, denom = fraction(expr)
    
    print(f"Denom: {denom}")
    
    try:
        # Use simple function call
        r = roots(denom, s)
        print(f"Roots (func): {r}")
        # Expected: {-1: 2}
        
    except Exception as e:
        print(f"Roots func failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_roots_corrected()
