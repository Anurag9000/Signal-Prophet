import React, { useState } from 'react';
import { Activity, CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react';
import axios from 'axios';
import Visualizer from './Visualizer';

const SystemAnalyzer = () => {
    const [domain, setDomain] = useState('continuous');
    const [systemEq, setSystemEq] = useState('2*x(t)');
    const [inputEq, setInputEq] = useState('u(t)');
    const [loading, setLoading] = useState(false);
    const [properties, setProperties] = useState(null);
    const [plotData, setPlotData] = useState(null);
    const [inputPlotData, setInputPlotData] = useState(null);
    const [impulsePlotData, setImpulsePlotData] = useState(null);
    const [outputEquation, setOutputEquation] = useState('');

    const handleAnalyze = async () => {
        setLoading(true);
        try {
            const res = await axios.post('http://localhost:8000/analyze_system', {
                equation: systemEq,
                input_equation: inputEq,
                domain: domain
            });

            setProperties(res.data.properties);
            setPlotData(res.data.plot);
            setInputPlotData(res.data.input_plot);
            setImpulsePlotData(res.data.impulse_plot);
            setOutputEquation(res.data.output_equation);
        } catch (error) {
            console.error('Analysis failed:', error);

            let msg = 'Unknown error';

            if (error.message === 'Network Error') {
                msg = 'Cannot connect to server. Is the Python backend running?';
            } else if (error.response?.data?.detail) {
                msg = error.response.data.detail;
            } else if (error.message) {
                msg = error.message;
            }

            alert(`Analysis Error: ${msg}`);
        }
        setLoading(false);
    };

    const PropertyRow = ({ name, status, explanation }) => (
        <tr className="border-b border-slate-200 hover:bg-slate-50 transition">
            <td className="px-6 py-4 font-semibold text-slate-700">{name}</td>
            <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                    {status === 'yes' && <CheckCircle size={20} className="text-green-600" />}
                    {status === 'no' && <XCircle size={20} className="text-red-600" />}
                    {status === 'unknown' && <AlertCircle size={20} className="text-yellow-600" />}
                    <span className={`font-medium ${status === 'yes' ? 'text-green-700' :
                        status === 'no' ? 'text-red-700' : 'text-yellow-700'
                        }`}>
                        {status === 'yes' ? 'YES' : status === 'no' ? 'NO' : 'UNKNOWN'}
                    </span>
                </div>
            </td>
            <td className="px-6 py-4 text-sm text-slate-600">{explanation}</td>
        </tr>
    );

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center gap-3 mb-4">
                        <Activity size={32} className="text-indigo-600" />
                        <h1 className="text-4xl font-bold text-slate-800">System Analyzer</h1>
                    </div>
                    <p className="text-slate-600 text-lg">
                        Analyze system properties: Linearity, Time-Invariance, Causality, Memory, Stability, Invertibility
                    </p>
                </div>

                {/* Input Section */}
                <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8 mb-8">
                    <div className="grid md:grid-cols-3 gap-6">
                        {/* Domain Selector */}
                        <div>
                            <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                                Signal Type
                            </label>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => {
                                        setDomain('continuous');
                                        setSystemEq('2*x(t)');
                                        setInputEq('u(t)');
                                    }}
                                    className={`flex-1 py-2.5 rounded-xl font-bold transition ${domain === 'continuous'
                                        ? 'bg-indigo-600 text-white'
                                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                                        }`}
                                >
                                    CT
                                </button>
                                <button
                                    onClick={() => {
                                        setDomain('discrete');
                                        setSystemEq('2*x[n]');
                                        setInputEq('u[n]');
                                    }}
                                    className={`flex-1 py-2.5 rounded-xl font-bold transition ${domain === 'discrete'
                                        ? 'bg-indigo-600 text-white'
                                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                                        }`}
                                >
                                    DT
                                </button>
                            </div>
                        </div>

                        {/* System Equation Input */}
                        <div className="md:col-span-2 space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                                    System Equation y({domain === 'continuous' ? 't' : 'n'}) =
                                </label>
                                <input
                                    type="text"
                                    value={systemEq}
                                    onChange={(e) => setSystemEq(e.target.value)}
                                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-mono text-base focus:ring-2 focus:ring-indigo-500 outline-none transition"
                                    placeholder={domain === 'continuous' ? 'e.g., 2*x(t) + 3 or t*x(t)' : 'e.g., x[n-1] + 0.5*x[n]'}
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                                    Input Signal x({domain === 'continuous' ? 't' : 'n'}) = <span className="text-slate-400 font-normal">(Optional, default: δ)</span>
                                </label>
                                <input
                                    type="text"
                                    value={inputEq}
                                    onChange={(e) => setInputEq(e.target.value)}
                                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-mono text-base focus:ring-2 focus:ring-indigo-500 outline-none transition"
                                    placeholder={domain === 'continuous' ? 'e.g., delta(t), u(t), cos(t)' : 'e.g., delta[n], u[n]'}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Analyze Button */}
                    <button
                        onClick={handleAnalyze}
                        disabled={loading || !systemEq}
                        className="w-full mt-6 py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Analyzing...' : 'Analyze System'}
                    </button>
                </div>

                {/* Results */}
                {properties && (
                    <div className="space-y-6">
                        {/* Properties Table */}
                        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 overflow-hidden">
                            <div className="bg-gradient-to-r from-indigo-600 to-blue-600 px-6 py-4 flex justify-between items-center">
                                <h2 className="text-xl font-bold text-white">System Properties</h2>
                                <div className="flex flex-col gap-2 items-end">
                                    {properties.impulse_response && (
                                        <div className="text-white/90 text-sm font-mono bg-white/10 px-3 py-1 rounded-lg border border-white/20">
                                            h({domain === 'continuous' ? 't' : 'n'}) = {properties.impulse_response}
                                        </div>
                                    )}
                                    {outputEquation && (
                                        <div className="text-white/90 text-sm font-mono bg-white/10 px-3 py-1 rounded-lg border border-white/20">
                                            y({domain === 'continuous' ? 't' : 'n'}) = {outputEquation}
                                        </div>
                                    )}
                                </div>
                            </div>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-slate-100">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-bold text-slate-600 uppercase">Property</th>
                                            <th className="px-6 py-3 text-left text-xs font-bold text-slate-600 uppercase">Status</th>
                                            <th className="px-6 py-3 text-left text-xs font-bold text-slate-600 uppercase">Explanation</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <PropertyRow
                                            name="Linearity"
                                            status={properties.linearity.status}
                                            explanation={properties.linearity.explanation}
                                        />
                                        <PropertyRow
                                            name="Time-Invariance"
                                            status={properties.time_invariance.status}
                                            explanation={properties.time_invariance.explanation}
                                        />
                                        <PropertyRow
                                            name="Causality"
                                            status={properties.causality.status}
                                            explanation={properties.causality.explanation}
                                        />
                                        <PropertyRow
                                            name="Memoryless"
                                            status={properties.memory.status}
                                            explanation={properties.memory.explanation}
                                        />
                                        <PropertyRow
                                            name="Stability (BIBO)"
                                            status={properties.stability.status}
                                            explanation={properties.stability.explanation}
                                        />
                                        <PropertyRow
                                            name="Invertibility"
                                            status={properties.invertibility.status}
                                            explanation={properties.invertibility.explanation}
                                        />
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        {/* Plots */}
                        <div className="grid md:grid-cols-3 gap-6">
                            {/* Input Plot */}
                            {inputPlotData && inputPlotData.x && inputPlotData.x.length > 0 && (
                                <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-6">
                                    <h3 className="text-lg font-bold text-slate-800 mb-4">Input Signal x({domain === 'continuous' ? 't' : 'n'})</h3>
                                    <div className="h-64">
                                        <Visualizer
                                            xData={inputPlotData.x}
                                            yData={inputPlotData.y}
                                            title={`Input x${domain === 'continuous' ? '(t)' : '[n]'}`}
                                            xLabel={domain === 'continuous' ? 't' : 'n'}
                                            yLabel="x"
                                            color="#10b981" // Emerald
                                            plotType={domain === 'discrete' ? 'stem' : 'line'}
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Impulse Plot */}
                            {impulsePlotData && impulsePlotData.x && impulsePlotData.x.length > 0 && (
                                <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-6">
                                    <h3 className="text-lg font-bold text-slate-800 mb-4">Impulse Response h({domain === 'continuous' ? 't' : 'n'})</h3>
                                    <div className="h-64">
                                        <Visualizer
                                            xData={impulsePlotData.x}
                                            yData={impulsePlotData.y}
                                            title={`Impulse h(${domain === 'continuous' ? 't' : 'n'})`}
                                            xLabel={domain === 'continuous' ? 't' : 'n'}
                                            yLabel="h"
                                            color="#f59e0b" // Amber
                                            plotType={domain === 'discrete' ? 'stem' : 'line'}
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Output Plot */}
                            {plotData && plotData.x && plotData.x.length > 0 && (
                                <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-6">
                                    <h3 className="text-lg font-bold text-slate-800 mb-2">System Response y({domain === 'continuous' ? 't' : 'n'})</h3>
                                    {outputEquation && (
                                        <div className="text-xs text-slate-500 font-mono mb-4 break-words">
                                            y = {outputEquation}
                                        </div>
                                    )}
                                    <div className="h-64">
                                        <Visualizer
                                            xData={plotData.x}
                                            yData={plotData.y}
                                            title={`Output y(${domain === 'continuous' ? 't' : 'n'})`}
                                            xLabel={domain === 'continuous' ? 't' : 'n'}
                                            yLabel="y"
                                            color="#6366f1" // Indigo
                                            plotType={domain === 'discrete' ? 'stem' : 'line'}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Help Section */}
                <div className="mt-8 bg-blue-50 border border-blue-200 rounded-2xl p-6">
                    <div className="flex items-start gap-3">
                        <Info size={24} className="text-blue-600 flex-shrink-0 mt-1" />
                        <div>
                            <h3 className="font-bold text-blue-900 mb-2">Examples:</h3>
                            <ul className="text-sm text-blue-800 space-y-1">
                                <li><strong>CT Linear:</strong> <code className="bg-blue-100 px-2 py-0.5 rounded">2*x(t)</code></li>
                                <li><strong>CT Non-Linear:</strong> <code className="bg-blue-100 px-2 py-0.5 rounded">x(t)**2</code></li>
                                <li><strong>CT Time-Variant:</strong> <code className="bg-blue-100 px-2 py-0.5 rounded">t*x(t)</code></li>
                                <li><strong>DT With Memory:</strong> <code className="bg-blue-100 px-2 py-0.5 rounded">x[n-1] + 0.5*x[n]</code></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SystemAnalyzer;
