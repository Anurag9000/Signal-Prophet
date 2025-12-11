import sys
sys.path.insert(0, 'D:/SnS_App')

from api.core import symbolic

# Test the compute_inverse_fourier function
result = symbolic.compute_inverse_fourier("1/(1 + I*w)")

print("\n=== RESULT ===")
print(result)
