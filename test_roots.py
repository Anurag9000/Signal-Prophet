from sympy import symbols, parse_expr, roots, fraction

def test_roots():
    s = symbols('s')
    expr_str = "1/(s+1)**2"
    expr = parse_expr(expr_str)
    numer, denom = fraction(expr)
    
    print(f"Expression: {expr}")
    print(f"Denom: {denom}")
    
    try:
        from sympy import Poly
        p = Poly(denom, s)
        r = p.roots()
        print(f"Roots (Poly): {r}")
        # Expected: {-1: 2}
        
        flat_roots = []
        for root, count in r.items():
            flat_roots.extend([root] * count)
        print(f"Flat Roots: {flat_roots}")
        
    except Exception as e:
        print(f"Poly failed: {e}")
        
    from sympy import solve
    s_roots = solve(denom, s)
    print(f"Solve Roots: {s_roots}")

if __name__ == "__main__":
    test_roots()
