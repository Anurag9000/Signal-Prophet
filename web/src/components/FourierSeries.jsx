
import React, { useState } from 'react';
import axios from 'axios';
import { InlineMath } from 'react-katex';
import { Waves, Activity } from 'lucide-react';
import Visualizer from './Visualizer';
import { API_URL } from '../config';

const FourierSeries = () => {
    const [domain, setDomain] = useState('continuous'); // 'continuous' | 'discrete'

    // Inputs
    const [signalEq, setSignalEq] = useState('sign(sin(t))'); // Square wave default
    const [period, setPeriod] = useState(6.28); // T
    const [numN, setNumN] = useState(10); // N for DT

    const [loading, setLoading] = useState(false);

    // Results
    const [coefficients, setCoefficients] = useState(null);

    const handleAnalyze = async () => {
        setLoading(true);
        try {
            const res = await axios.post(`${API_URL}/fourier/analyze`, {
                expression: signalEq,
                T: parseFloat(period),
                N: parseInt(numN),
                domain: domain,
                k_min: -7,
                k_max: 7
            });
            setCoefficients(res.data.coeffs);
        } catch (err) {
            console.error(err);
            alert("Analysis failed. See console.");
        }
        setLoading(false);
    };

    const handleAutoDetectPeriod = async () => {
        try {
            const res = await axios.post(`${API_URL}/fourier/detect-period`, {
                expression: signalEq,
                domain: domain
            });

            if (res.data.period !== null) {
                if (domain === 'continuous') {
                    setPeriod(res.data.period);
                } else {
                    setNumN(res.data.period);
                }
                alert(res.data.message);
            } else {
                alert(res.data.message || "Could not detect period");
            }
        } catch (err) {
            console.error(err);
            alert("Period detection failed. See console.");
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            {/* Header */}
            <div className="text-center">
                <div className="flex items-center justify-center gap-3 mb-4">
                    <Waves size={32} className="text-indigo-600" />
                    <h1 className="text-4xl font-bold text-slate-800">Fourier Series Engine</h1>
                </div>
                <p className="text-slate-600">
                    Analyze periodic signals into harmonics (<InlineMath math="a_k" />) and view their spectrum.
                </p>
            </div>

            {/* Main Content Card */}
            <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
                <div className="p-8 border-b border-slate-100 bg-slate-50/50">
                    {/* Domain & Period Controls */}
                    <div className="flex flex-wrap gap-6 mb-6">
                        <div className="flex bg-white rounded-lg p-1 border border-slate-200">
                            <button
                                onClick={() => {
                                    setDomain('continuous');
                                    setSignalEq('sign(sin(t))');
                                    setPeriod(6.28);
                                }}
                                className={`px-4 py-2 rounded-md font-bold text-sm transition ${domain === 'continuous' ? 'bg-blue-100 text-blue-700' : 'text-slate-500'}`}
                            >CT (Period T)</button>
                            <button
                                onClick={() => {
                                    setDomain('discrete');
                                    setSignalEq('cos(2*pi*n/10)');
                                    setNumN(10);
                                }}
                                className={`px-4 py-2 rounded-md font-bold text-sm transition ${domain === 'discrete' ? 'bg-blue-100 text-blue-700' : 'text-slate-500'}`}
                            >DT (Period N)</button>
                        </div>

                        <div className="flex items-center gap-2">
                            <label className="font-bold text-slate-600">{domain === 'continuous' ? 'Period T =' : 'Period N ='}</label>
                            <input
                                type="number"
                                value={domain === 'continuous' ? period : numN}
                                onChange={(e) => domain === 'continuous' ? setPeriod(e.target.value) : setNumN(e.target.value)}
                                className="w-24 px-3 py-2 border border-slate-300 rounded-lg font-mono focus:ring-2 focus:ring-indigo-500 outline-none"
                            />
                            <button
                                onClick={handleAutoDetectPeriod}
                                className="px-3 py-2 bg-green-600 text-white text-xs font-bold rounded-lg hover:bg-green-700 transition"
                                title="Auto-detect period from signal"
                            >
                                Auto-Detect
                            </button>
                        </div>
                    </div>

                    {/* Analysis Inputs */}
                    <div className="flex gap-4">
                        <div className="flex-1">
                            <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Signal x({domain === 'continuous' ? 't' : 'n'})</label>
                            <input
                                type="text"
                                value={signalEq}
                                onChange={(e) => setSignalEq(e.target.value)}
                                className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl font-mono text-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                placeholder={domain === 'continuous' ? "e.g. sign(sin(t)), rect(t/2), cos(t) + 0.5" : "e.g. cos(2*pi*n/10)"}
                            />
                        </div>
                        <button
                            onClick={handleAnalyze}
                            disabled={loading}
                            className="px-8 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition disabled:opacity-50"
                        >
                            {loading ? 'Computing...' : 'Analyze'}
                        </button>
                    </div>
                </div>

                {/* Results Area */}
                <div className="p-8 bg-white min-h-[400px]">
                    {coefficients && (
                        <div className="space-y-8">
                            <h3 className="text-xl font-bold text-slate-800">Frequency Spectrum (Magnitude <InlineMath math="|a_k|" />)</h3>
                            {/* Spectrum Plot */}
                            <div className="h-64 bg-slate-50 rounded-xl border border-slate-200 p-4">
                                <Visualizer
                                    xData={coefficients.map(c => c.k)}
                                    yData={coefficients.map(c => c.magnitude)}
                                    title="Magnitude Spectrum |ak|"
                                    xLabel="k (Harmonic)"
                                    yLabel="|ak|"
                                    plotType="stem"
                                    color="#2cbbd1c3"
                                />
                            </div>

                            {/* Coefficients Table */}
                            <div>
                                <h3 className="text-lg font-bold text-slate-800 mb-4">Calculated Coefficients</h3>
                                <div className="overflow-x-auto border rounded-xl">
                                    <table className="w-full text-sm text-left">
                                        <thead className="bg-slate-50 text-slate-600 uppercase font-bold">
                                            <tr>
                                                <th className="px-6 py-3">k</th>
                                                <th className="px-6 py-3">Magnitude <InlineMath math="|a_k|" /></th>
                                                <th className="px-6 py-3">Phase <InlineMath math="\angle a_k" /></th>
                                                <th className="px-6 py-3">Value (Complex)</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-100">
                                            {coefficients.map((c) => (
                                                <tr key={c.k} className="hover:bg-slate-50">
                                                    <td className="px-6 py-3 font-mono font-bold">{c.k}</td>
                                                    <td className="px-6 py-3 font-mono">{c.magnitude.toFixed(4)}</td>
                                                    <td className="px-6 py-3 font-mono">{c.phase.toFixed(4)}</td>
                                                    <td className="px-6 py-3 font-mono text-slate-500">{c.value_str}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    )}

                    {!coefficients && !loading && (
                        <div className="h-full flex flex-col items-center justify-center text-slate-400">
                            <Waves size={48} className="mb-4 opacity-50" />
                            <p>Enter parameters and compute to see results</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default FourierSeries;
