
import sys
import os

# Ensure api module is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.core import symbolic, system_analyzer

def assert_in(substring, string, name):
    if substring not in string:
        print(f"FAILED {name}: '{substring}' not in '{string}'")
        return False
    return True

def run_tests():
    print("Running Tests...\n")
    failed = False
    
    # Test 1: Regex
    try:
        res = symbolic.parse_signal("x[n]", "discrete")
        s = str(res)
        if "x" in s and "n" in s:
            print("PASS Regex Safety")
        else:
            print(f"FAIL Regex Safety: Got {s}")
            failed = True
    except Exception as e:
        print(f"FAIL Regex Safety Exception: {e}")
        failed = True

    # Test 2: Inverse Z - Delay
    try:
        res, _ = symbolic.compute_inverse_z("z**-1")
        if "\\delta" in res or "delta" in res:
             print(f"PASS Inverse Z Delay: {res}")
        else:
             print(f"FAIL Inverse Z Delay: Got {res}")
             failed = True
    except Exception as e:
        print(f"FAIL Inverse Z Delay Exception: {e}")
        failed = True
        
    # Test 3: Inverse Z - Step
    try:
        res, _ = symbolic.compute_inverse_z("z/(z-1)")
        # normalize
        res = res.replace('theta', 'u')
        if "u[n]" in res or "u(n)" in res:
            print(f"PASS Inverse Z Step: {res}")
        else: 
            print(f"FAIL Inverse Z Step: Got {res}")
            failed = True
    except Exception as e:
        print(f"FAIL Inverse Z Step Exception: {e}")
        failed = True

    # Test 4: Inverse Z - Repeated Pole
    try:
        res, expr = symbolic.compute_inverse_z("z/(z-0.5)**2")
        if expr is None:
            print("FAIL Inverse Z Repeated: expr is None")
            failed = True
        else:
            print(f"INFO Inverse Z Repeated Result: {res}")
            print("PASS Inverse Z Repeated")
    except Exception as e:
        print(f"FAIL Inverse Z Repeated Exception: {e}")
        failed = True

    # Test 5: Stability
    try:
        h = symbolic.parse_signal("exp(t)*Heaviside(t)", "continuous")
        res = system_analyzer.check_stability_bibo(h, "continuous")
        if res['status'] == 'no':
             print("PASS Stability Unstable")
        else:
             print(f"FAIL Stability Unstable: Got {res}")
             failed = True
    except Exception as e:
        print(f"FAIL Stability Exception: {e}")
        failed = True
        
    if failed:
        sys.exit(1)
    else:
        print("\nALL VERIFICATION TESTS PASSED")

if __name__ == '__main__':
    run_tests()
