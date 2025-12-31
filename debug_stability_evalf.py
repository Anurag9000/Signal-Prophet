from sympy import symbols, Heaviside, Abs, exp, oo, integrate, simplify

t = symbols('t', real=True)
h_expr = Heaviside(t)
stability_integral = integrate(h_expr, (t, -oo, oo))
print(f"Evalf: {stability_integral.evalf()}")
try:
    f_val = float(stability_integral.evalf())
    print(f"Float val: {f_val}")
except Exception as e:
    print(f"Float failed: {e}")
