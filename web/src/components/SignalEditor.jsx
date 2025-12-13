import React, { useState } from 'react';
import axios from 'axios';
import 'katex/dist/katex.min.css';
import { Play, Loader2 } from 'lucide-react';
import clsx from 'clsx';
import { API_URL } from '../config';

const SignalEditor = ({ onPlotData, onTransformData, onSpectrumData, onSeriesData }) => {
    const [expression, setExpression] = useState("u(t) - u(t-2)");
    const [domain, setDomain] = useState("continuous");
    const [loading, setLoading] = useState(false);

    const handleAnalyze = async () => {
        setLoading(true);

        try {
            // 1. Plot
            const plotRes = await axios.post(`${API_URL}/plot`, {
                expression,
                t_min: -5,
                t_max: 5,
                domain
            });
            onPlotData(plotRes.data);

            // 2. Transfroms & Analysis (Both Continuous & Discrete supported now)

            // Transforms
            const lapRes = await axios.post(`${API_URL}/transform`, {
                expression,
                type: domain === 'continuous' ? 'laplace' : 'fourier' // TODO: Add specific Z-transform endpoint later
            });
            const fouRes = await axios.post(`${API_URL}/transform`, { expression, type: 'fourier' });

            onTransformData({
                laplace: domain === 'continuous' ? lapRes.data.latex : "\\text{Z-Transform (WIP in backend)}",
                fourier: fouRes.data.latex
            });

            // Spectrum (Mag/Phase)
            try {
                const specRes = await axios.post(`${API_URL}/spectrum`, {
                    expression,
                    domain: domain
                });
                if (specRes.data) {
                    onSpectrumData(specRes.data);
                }
            } catch (e) { console.warn("Spectrum failed", e); }

            // Series (Discrete/Continuous)
            try {
                const seriesRes = await axios.post(`${API_URL}/series`, { expression });
                if (seriesRes.data && seriesRes.data.coeffs) {
                    onSeriesData(seriesRes.data.coeffs);
                }
            } catch (e) { console.warn("Series failed", e); }

        } catch (err) {
            console.error(err);
            alert("Error analyzing signal. Check syntax.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-slate-800">Signal Definition</h2>
                <div className="flex bg-slate-100 p-1 rounded-lg">
                    <button
                        onClick={() => setDomain('continuous')}
                        className={clsx("px-3 py-1 text-xs font-semibold rounded-md transition", domain === 'continuous' ? "bg-white text-blue-700 shadow-sm" : "text-slate-500 hover:text-slate-700")}
                    >CT x(t)</button>
                    <button
                        onClick={() => setDomain('discrete')}
                        className={clsx("px-3 py-1 text-xs font-semibold rounded-md transition", domain === 'discrete' ? "bg-white text-purple-700 shadow-sm" : "text-slate-500 hover:text-slate-700")}
                    >DT x[n]</button>
                </div>
            </div>

            <div className="space-y-4">
                <div>
                    <label className="block text-xs font-bold uppercase text-slate-400 mb-1.5 tracking-wider">
                        Mathematical Expression
                    </label>
                    <div className="relative">
                        <input
                            type="text"
                            value={expression}
                            onChange={(e) => setExpression(e.target.value)}
                            className="w-full pl-4 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl font-mono text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all placeholder:text-slate-400"
                            placeholder={domain === 'continuous' ? "e.g. exp(-t)*u(t)" : "e.g. (0.5)^n * u[n]"}
                        />
                    </div>
                    <p className="mt-2 text-[11px] text-slate-400 flex gap-2">
                        <span className="font-semibold text-slate-500">Tips:</span>
                        <span>u(t) = Step, d(t) = Impulse, exp(x) = e^x</span>
                    </p>
                </div>

                <button
                    onClick={handleAnalyze}
                    disabled={loading}
                    className="w-full py-3 bg-slate-900 text-white rounded-xl font-semibold hover:bg-slate-800 disabled:opacity-70 disabled:cursor-not-allowed transition-all shadow-lg shadow-slate-900/10 flex items-center justify-center gap-2"
                >
                    {loading ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} fill="currentColor" />}
                    {loading ? 'Computing...' : 'Analyze Signal'}
                </button>
            </div>
        </div>
    );
};

export default SignalEditor;
