import sys
sys.path.insert(0, 'D:/SnS_App')

from api.core import symbolic

# Test the evaluate_frequency_response function
result = symbolic.evaluate_frequency_response("1/(1 + I*w)", w_min=-10, w_max=10, num_points=10, type='fourier')

print("Result:", result)
if result:
    print("Magnitude x:", result['magnitude']['x'][:5])
    print("Magnitude y:", result['magnitude']['y'][:5])
else:
    print("ERROR: Function returned None or empty")
