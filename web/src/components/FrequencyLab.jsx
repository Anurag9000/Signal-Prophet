import React, { useState } from 'react';
import axios from 'axios';
import { BlockMath } from 'react-katex';
import { ArrowRight, Waves, Activity } from 'lucide-react';
import Visualizer from './Visualizer';
import { API_URL } from '../config';

const FrequencyLab = () => {
    const [domain, setDomain] = useState('continuous'); // 'continuous' | 'discrete'
    const [direction, setDirection] = useState('forward'); // 'forward' (time->freq) | 'inverse' (freq->time)
    const [expression, setExpression] = useState('exp(-t)*u(t)');
    const [loading, setLoading] = useState(false);

    // Results
    const [symbolicResult, setSymbolicResult] = useState(null);
    const [inputPlot, setInputPlot] = useState(null);
    const [outputPlot, setOutputPlot] = useState(null);

    const handleCompute = async () => {
        setLoading(true);
        setSymbolicResult(null);
        setInputPlot(null);
        setOutputPlot(null);

        try {
            if (direction === 'forward') {
                // Time Domain Input -> Frequency Domain Output
                // 1. Plot input time signal
                const timePlotRes = await axios.post(`${API_URL}/plot`, {
                    expression,
                    t_min: -5,
                    t_max: 5,
                    domain
                });
                setInputPlot(timePlotRes.data);

                // 2. Compute symbolic transform
                const transformRes = await axios.post(`${API_URL}/transform`, {
                    expression,
                    type: 'fourier' // Always Fourier for CTFT/DTFT
                });
                setSymbolicResult(transformRes.data.latex);

                // 3. Compute frequency spectrum
                const spectrumRes = await axios.post(`${API_URL}/spectrum`, {
                    expression,
                    domain,
                    w_min: -10,
                    w_max: 10
                });
                console.log("Spectrum response:", spectrumRes.data);
                if (spectrumRes.data && spectrumRes.data.magnitude) {
                    setOutputPlot(spectrumRes.data.magnitude);
                } else {
                    console.error("No magnitude data in spectrum response");
                }
            } else {
                // Frequency Domain Input -> Time Domain Output
                // 1. Plot input frequency response
                console.log("Calling /inverse with expression:", expression);
                const freqRes = await axios.post(`${API_URL}/inverse`, {
                    expression,
                    type: 'fourier',
                    domain: domain
                });

                console.log("Full /inverse response:", freqRes.data);

                if (freqRes.data.spectrum) {
                    console.log("Spectrum data:", freqRes.data.spectrum);
                    setInputPlot(freqRes.data.spectrum.magnitude);
                } else {
                    console.error("No spectrum in response");
                }
                if (freqRes.data.latex) {
                    setSymbolicResult(freqRes.data.latex);
                }
                if (freqRes.data.time_plot) {
                    setOutputPlot(freqRes.data.time_plot);
                } else {
                    console.error("No time_plot in response");
                }
            }
        } catch (e) {
            console.error(e);
            setSymbolicResult("\\text{Error: " + e.message + "}");
        } finally {
            setLoading(false);
        }
    };

    // Update defaults when domain/direction changes
    const handleDomainChange = (newDomain) => {
        setDomain(newDomain);
        if (direction === 'forward') {
            setExpression(newDomain === 'continuous' ? 'exp(-t)*u(t)' : '(0.8)**n * u[n]');
        } else {
            setExpression(newDomain === 'continuous' ? '1/(1 + I*w)' : '1/(1 - 0.8*exp(-I*w))');
        }
        setSymbolicResult(null);
        setInputPlot(null);
        setOutputPlot(null);
    };

    const handleDirectionChange = (newDirection) => {
        setDirection(newDirection);
        if (newDirection === 'forward') {
            setExpression(domain === 'continuous' ? 'exp(-t)*u(t)' : '(0.8)**n * u[n]');
        } else {
            setExpression(domain === 'continuous' ? '1/(1 + I*w)' : '1/(1 - 0.8*exp(-I*w))');
        }
        setSymbolicResult(null);
        setInputPlot(null);
        setOutputPlot(null);
    };

    const inputLabel = direction === 'forward'
        ? (domain === 'continuous' ? 'x(t)' : 'x[n]')
        : (domain === 'continuous' ? 'X(jω)' : 'X(e^jω)');

    const outputLabel = direction === 'forward'
        ? (domain === 'continuous' ? 'X(jω)' : 'X(e^jω)')
        : (domain === 'continuous' ? 'x(t)' : 'x[n]');

    return (
        <div className="space-y-8 min-h-[500px]">
            {/* Input Section */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
                        <Waves size={24} />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-slate-800">Fourier Transform Analysis</h2>
                        <p className="text-sm text-slate-500">Analyze signals in Time and Frequency domains (CTFT/DTFT).</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-end">
                    {/* Domain Selector */}
                    <div className="md:col-span-2">
                        <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Signal Type</label>
                        <div className="flex flex-col bg-slate-50 p-1 rounded-lg gap-1">
                            <button
                                onClick={() => handleDomainChange('continuous')}
                                className={`py-2 text-xs font-bold rounded-md transition ${domain === 'continuous' ? 'bg-white shadow text-indigo-600' : 'text-slate-500 hover:bg-slate-100'}`}
                            >
                                CT (CTFT)
                            </button>
                            <button
                                onClick={() => handleDomainChange('discrete')}
                                className={`py-2 text-xs font-bold rounded-md transition ${domain === 'discrete' ? 'bg-white shadow text-emerald-600' : 'text-slate-500 hover:bg-slate-100'}`}
                            >
                                DT (DTFT)
                            </button>
                        </div>
                    </div>

                    {/* Direction Selector */}
                    <div className="md:col-span-2">
                        <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Direction</label>
                        <div className="flex flex-col bg-slate-50 p-1 rounded-lg gap-1">
                            <button
                                onClick={() => handleDirectionChange('forward')}
                                className={`py-2 text-xs font-bold rounded-md transition ${direction === 'forward' ? 'bg-white shadow text-blue-600' : 'text-slate-500 hover:bg-slate-100'}`}
                            >
                                Time → Freq
                            </button>
                            <button
                                onClick={() => handleDirectionChange('inverse')}
                                className={`py-2 text-xs font-bold rounded-md transition ${direction === 'inverse' ? 'bg-white shadow text-pink-600' : 'text-slate-500 hover:bg-slate-100'}`}
                            >
                                Freq → Time
                            </button>
                        </div>
                    </div>

                    {/* Expression Input */}
                    <div className="md:col-span-5">
                        <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                            Input Expression {inputLabel}
                        </label>
                        <input
                            type="text"
                            value={expression}
                            onChange={(e) => setExpression(e.target.value)}
                            className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-mono text-base focus:ring-2 focus:ring-indigo-500 outline-none transition"
                            placeholder={direction === 'forward'
                                ? (domain === 'continuous' ? 'e.g., rect(t), sinc(t), exp(-t)*u(t)' : 'e.g., (0.8)^n * u[n]')
                                : (domain === 'continuous' ? 'e.g., 1/(1 + I*w), rect(w)' : 'e.g., 1/(1 - 0.8*exp(-I*w))')
                            }
                        />
                    </div>

                    {/* Compute Button */}
                    <div className="md:col-span-3">
                        <button
                            onClick={handleCompute}
                            disabled={loading}
                            className="w-full py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition flex justify-center items-center gap-2"
                        >
                            {loading ? "Computing..." : (
                                <>
                                    Compute <ArrowRight size={18} />
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Results Grid */}
            {(symbolicResult || inputPlot || outputPlot) && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                    {/* Symbolic Result */}
                    <div className="lg:col-span-2 bg-slate-900 p-8 rounded-2xl shadow-lg text-white flex flex-col justify-center items-center relative overflow-hidden min-h-[180px]">
                        <div className="absolute top-0 right-0 p-32 bg-indigo-500 rounded-full blur-[100px] opacity-20"></div>
                        <div className="absolute bottom-0 left-0 p-32 bg-pink-500 rounded-full blur-[100px] opacity-20"></div>
                        <h3 className="text-slate-400 font-bold uppercase tracking-widest text-xs mb-4 z-10">
                            {direction === 'forward' ? 'Fourier Transform' : 'Inverse Fourier Transform'}
                        </h3>
                        <div className="text-2xl z-10 w-full overflow-x-auto flex justify-center py-4">
                            <BlockMath math={`${outputLabel} = ${symbolicResult || '...'}`} />
                        </div>
                    </div>

                    {/* Input Plot */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-2">
                            {direction === 'forward' ? <Activity size={18} className="text-blue-600" /> : <Waves size={18} className="text-indigo-600" />}
                            <h3 className="font-bold text-slate-800">
                                Input: {direction === 'forward' ? 'Time Domain' : 'Frequency Domain'}
                            </h3>
                        </div>
                        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-2 h-80">
                            {inputPlot ? (
                                <Visualizer
                                    xData={inputPlot.x}
                                    yData={inputPlot.y}
                                    title={direction === 'forward' ? `Signal ${inputLabel}` : `Magnitude ${inputLabel}`}
                                    xLabel={direction === 'forward' ? (domain === 'continuous' ? 't' : 'n') : 'ω'}
                                    yLabel={inputLabel}
                                    color="#3b82f6"
                                    plotType={domain === 'discrete' && direction === 'forward' ? 'stem' : 'line'}
                                />
                            ) : (
                                <div className="h-full flex items-center justify-center text-slate-300">No Input Plot</div>
                            )}
                        </div>
                    </div>

                    {/* Output Plot */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-2">
                            {direction === 'forward' ? <Waves size={18} className="text-emerald-600" /> : <Activity size={18} className="text-pink-600" />}
                            <h3 className="font-bold text-slate-800">
                                Output: {direction === 'forward' ? 'Frequency Domain' : 'Time Domain'}
                            </h3>
                        </div>
                        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-2 h-80">
                            {outputPlot ? (
                                <Visualizer
                                    xData={outputPlot.x}
                                    yData={outputPlot.y}
                                    title={direction === 'forward' ? `Magnitude ${outputLabel}` : `Signal ${outputLabel}`}
                                    xLabel={direction === 'forward' ? 'ω' : (domain === 'continuous' ? 't' : 'n')}
                                    yLabel={outputLabel}
                                    color="#10b981"
                                    plotType={domain === 'discrete' && direction === 'inverse' ? 'stem' : 'line'}
                                />
                            ) : (
                                <div className="h-full flex items-center justify-center text-slate-300">
                                    {symbolicResult && symbolicResult.includes("Error") ? "Could not plot" : "No Output Plot"}
                                </div>
                            )}
                        </div>
                    </div>

                </div>
            )}
        </div>
    );
};

export default FrequencyLab;
