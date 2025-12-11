import sys
import os

# Ensure api module is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.core import symbolic

def separator(name):
    print("\n" + "="*30)
    print(f" TESTING: {name}")
    print("="*30)

def test_parsing():
    separator("PARSING")
    signals = [
        "u(t)",
        "u(t) - u(t-2)",
        "exp(-t)*u(t)",
        "sin(2*pi*t)",
        "d(t)",
        "(t+1)*(u(t+1)-u(t-1))"
    ]
    for s in signals:
        try:
            expr = symbolic.parse_signal(s, 'continuous')
            print(f"✅ Parsed '{s}': {expr}")
        except Exception as e:
            print(f"❌ Failed '{s}': {e}")

def test_spectrum():
    separator("SPECTRUM")
    s = "exp(-abs(t))"
    print(f"Signal: {s}")
    data = symbolic.compute_spectrum(s)
    if data:
        print(f"✅ Spectrum computed. Points: {len(data['magnitude']['x'])}")
        print(f"   Mag[0]: {data['magnitude']['y'][0]}")
    else:
        print("❌ Spectrum failed.")

def test_series():
    separator("FOURIER SERIES")
    s = "1" # DC signal
    print(f"Signal: {s} (Period 2pi)")
    coeffs = symbolic.compute_fourier_series_coeffs(s)
    if coeffs:
        print(f"✅ Series computed. Coeffs: {len(coeffs)}")
        print(f"   c[0]: {coeffs[len(coeffs)//2]}")
    else:
        print("❌ Series failed.")

def test_convolution():
    separator("CONVOLUTION")
    x = "u(t) - u(t-2)"
    h = "u(t)"
    print(f"x(t): {x}, h(t): {h}")
    data = symbolic.compute_convolution(x, h)
    if data:
        print(f"✅ Convolution computed.")
        print(f"   Frames: {len(data['frames'])}")
        print(f"   y(final): {data['y'][-1]}")
    else:
        print("❌ Convolution failed.")

if __name__ == "__main__":
    test_parsing()
    test_spectrum()
    test_series()
    test_convolution()
