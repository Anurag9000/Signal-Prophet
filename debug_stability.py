from sympy import symbols, Heaviside, Abs, exp, oo, integrate, simplify

t = symbols('t', real=True)
h_expr = exp(-t) * Heaviside(t)
abs_h = simplify(Abs(h_expr))
print(f"abs_h: {abs_h}")
stability_integral = integrate(abs_h, (t, -oo, oo))
print(f"Integrate result: {stability_integral}")
print(f"Result type: {type(stability_integral)}")
print(f"Is finite: {stability_integral.is_finite}")
