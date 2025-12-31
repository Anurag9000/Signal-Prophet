import React from 'react';
import { Info, HelpCircle, Variable, Calculator, Zap, Activity } from 'lucide-react';
import { InlineMath, BlockMath } from 'react-katex';

const MathHelp = () => {
    const sections = [
        {
            title: "Core Symbols & Constants",
            icon: <Variable className="text-indigo-600" />,
            items: [
                { label: "Imaginary Unit", notation: "j, i, I, J", description: "All treated as the imaginary unit √-1." },
                { label: "Pi", notation: "pi, PI", description: "Mathematical constant π (3.14159...)." },
                { label: "Euler's Number", notation: "e", description: "Mathematical constant e (2.71828...)." },
                { label: "Infinity", notation: "oo, inf", description: "Represent infinity ∞." },
            ]
        },
        {
            title: "Variables & Domains",
            icon: <Activity className="text-blue-600" />,
            items: [
                { label: "Continuous Time", notation: "t", description: "Independent variable for CT signals, e.g., x(t)." },
                { label: "Discrete Time", notation: "n", description: "Independent variable for DT signals, e.g., x[n]." },
                { label: "Frequency (Omega)", notation: "w, omega", description: "Angular frequency ω." },
                { label: "Laplace Variable", notation: "s", description: "Complex frequency variable s = σ + jω." },
                { label: "Z-Transform Variable", notation: "z", description: "Complex variable for Z-domain." },
            ]
        },
        {
            title: "Signal Functions",
            icon: <Zap className="text-amber-600" />,
            items: [
                { label: "Unit Step", notation: "u(t), u[n]", description: "Heaviside step function. 1 for t ≥ 0, 0 for t < 0." },
                { label: "Unit Impulse", notation: "d(t), d[n], delta(t)", description: "Dirac delta (CT) or Kronecker delta (DT)." },
                { label: "Rectangular Pulse", notation: "rect(t)", description: "Rectangular pulse of width 1 centered at 0." },
                { label: "Triangular Pulse", notation: "tri(t)", description: "Triangular pulse of width 2 (from -1 to 1) centered at 0." },
                { label: "Sinc Function", notation: "sinc(t)", description: "Normalized sinc: sin(πt)/(πt) in evaluation, sin(t)/t in symbolic." },
                { label: "Signum", notation: "sign(t)", description: "1 for t > 0, -1 for t < 0, 0 at t = 0." },
            ]
        },
        {
            title: "Mathematical Functions",
            icon: <Calculator className="text-emerald-600" />,
            items: [
                { label: "Exponential", notation: "exp(x)", description: "Natural exponential e^x." },
                { label: "Logarithm (Natural)", notation: "log(x), ln(x)", description: "Natural logarithm ln(x)." },
                { label: "Logarithm (Base 10)", notation: "log10(x)", description: "Base-10 logarithm." },
                { label: "Square Root", notation: "sqrt(x)", description: "Square root of x." },
                { label: "Absolute Value", notation: "|x|, abs(x)", description: "Magnitude of x." },
                { label: "Trigonometric", notation: "sin, cos, tan, cot, sec, csc", description: "Standard trigonometric functions." },
                { label: "Hyperbolic", notation: "sinh, cosh, tanh", description: "Hyperbolic trigonometric functions." },
            ]
        }
    ];

    const examples = [
        { title: "Exponential Decay", eq: "exp(-2*t) * u(t)" },
        { title: "Sinc Pulse", eq: "sinc(t/2)" },
        { title: "Phase Shifted Cosine", eq: "cos(2*pi*f*t + pi/4)" },
        { title: "Complex Rational", eq: "1 / (s^2 + 2*s + 5)" },
        { title: "Discrete Moving Average", eq: "0.5*x[n] + 0.5*x[n-1]" },
    ];

    return (
        <div className="max-w-6xl mx-auto p-4 md:p-8 space-y-12">
            <div className="text-center space-y-4">
                <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">
                    How to Input <span className="text-indigo-600">Mathematical</span> Notations
                </h1>
                <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                    SignalProphet uses a robust symbolic parser. Here is the formal list of supported functions and their intended usage.
                </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
                {sections.map((section, idx) => (
                    <div key={idx} className="bg-white rounded-3xl p-8 shadow-xl shadow-slate-200/50 border border-slate-100 hover:shadow-2xl transition-all duration-300">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="p-3 bg-slate-50 rounded-2xl">
                                {section.icon}
                            </div>
                            <h3 className="text-2xl font-bold text-slate-900">{section.title}</h3>
                        </div>
                        <div className="space-y-6">
                            {section.items.map((item, i) => (
                                <div key={i} className="group border-b border-slate-50 last:border-0 pb-4 last:pb-0">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="font-bold text-slate-800">{item.label}</span>
                                        <code className="bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded-lg font-mono text-sm border border-indigo-100 transition-colors group-hover:bg-indigo-100">
                                            {item.notation}
                                        </code>
                                    </div>
                                    <p className="text-sm text-slate-500 leading-relaxed">{item.description}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            <div className="bg-slate-900 rounded-[2.5rem] p-12 text-white overflow-hidden relative">
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500 rounded-full blur-[120px] opacity-20 -mr-32 -mt-32"></div>
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-violet-500 rounded-full blur-[120px] opacity-20 -ml-32 -mb-32"></div>

                <div className="relative z-10 grid md:grid-cols-2 gap-12 items-center">
                    <div className="space-y-6">
                        <h2 className="text-3xl font-bold flex items-center gap-3">
                            <HelpCircle className="text-indigo-400" />
                            Quick Tips
                        </h2>
                        <ul className="space-y-4">
                            <li className="flex gap-4">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs mt-1">1</div>
                                <div>
                                    <p className="font-bold text-slate-100">Implicit Multiplication</p>
                                    <p className="text-slate-400 text-sm">You can type <code>2t</code> instead of <code>2*t</code> for most expressions.</p>
                                </div>
                            </li>
                            <li className="flex gap-4">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs mt-1">2</div>
                                <div>
                                    <p className="font-bold text-slate-100">Brackets</p>
                                    <p className="text-slate-400 text-sm">Use <code>x(t)</code> for continuous and <code>x[n]</code> for discrete, though they are often interchangeable in the parser.</p>
                                </div>
                            </li>
                            <li className="flex gap-4">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs mt-1">3</div>
                                <div>
                                    <p className="font-bold text-slate-100">Exponents</p>
                                    <p className="text-slate-400 text-sm">Use <code>t^2</code> or <code>t**2</code> for power operations.</p>
                                </div>
                            </li>
                        </ul>
                    </div>

                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 space-y-6">
                        <h3 className="text-xl font-bold text-indigo-300">Example Inputs</h3>
                        <div className="space-y-4">
                            {examples.map((ex, i) => (
                                <div key={i} className="flex flex-col gap-1 p-3 rounded-xl hover:bg-white/5 transition border border-transparent hover:border-white/5">
                                    <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">{ex.title}</span>
                                    <code className="text-emerald-400 font-mono text-sm">{ex.eq}</code>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MathHelp;
