
import subprocess
import os

def run_tests():
    files = ["api/tests/test_api.py", "api/tests/test_symbolic.py"]
    for f in files:
        print(f"Running {f}...")
        res = subprocess.run(["python", "-m", "pytest", f, "-vv"], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"FAILURES in {f}:")
            print(res.stdout)
            print(res.stderr)
        else:
            print(f"{f} PASSED")

if __name__ == "__main__":
    run_tests()
