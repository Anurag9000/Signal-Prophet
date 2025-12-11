import sys
import os

sys.path.append(os.getcwd())
from api.core.symbolic import parse_transfer_function, compute_laplace, compute_inverse_laplace

def test_complex_inputs():
    cases = [
        ("1/((s+1)*(s+2))", "Multiple distinct poles"),
        ("1/(s+1)^2", "Repeated poles (power)"),
        ("1/(s^2 + 2*s + 1)", "Repeated poles (expanded)"),
        ("(s-5)/(s+5)", "Opposing signs / Non-minimum phase"),
        ("1/(s+100)", "Large magnitude pole"),
        ("1/(s+1)*(s-2)*(s+3)", "Three poles mixed signs")
    ]
    
    for expr, desc in cases:
        print(f"\n--- Testing: {desc} : {expr} ---")
        try:
            # Test Parsing
            res = parse_transfer_function(expr, 's')
            poles = res.get('poles', [])
            zeros = res.get('zeros', [])
            
            print(f"Poles ({len(poles)}): {poles}")
            print(f"Zeros ({len(zeros)}): {zeros}")
            
            # Test Transform (Inverse Laplace for X(s))
            inv = compute_inverse_laplace(expr)
            print(f"Inverse Laplace: {inv}")
            
        except Exception as e:
            print(f"FAILED: {e}")

if __name__ == "__main__":
    test_complex_inputs()
