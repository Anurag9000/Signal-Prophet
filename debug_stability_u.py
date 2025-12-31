from sympy import symbols, Heaviside, Abs, exp, oo, integrate, simplify

t = symbols('t', real=True)
h_expr = Heaviside(t)
abs_h = simplify(Abs(h_expr))
stability_integral = integrate(abs_h, (t, -oo, oo))
print(f"Integrate result: {stability_integral}")
print(f"Is finite: {stability_integral.is_finite}")
