
import React, { useState } from 'react';
import { Layers, Box, Waves, Activity, Zap } from 'lucide-react';
import ROCExplorer from './components/ROCExplorer';
import ConvolutionLab from './components/ConvolutionLab';
import FrequencyLab from './components/FrequencyLab';
import SystemAnalyzer from './components/SystemAnalyzer';
import FourierSeries from './components/FourierSeries';
import 'katex/dist/katex.min.css';

function App() {
  const [activeTab, setActiveTab] = useState('home');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 font-sans text-slate-800">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50 shadow-sm transition-all duration-300">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div
              className="flex items-center space-x-3 cursor-pointer group"
              onClick={() => setActiveTab('home')}
            >
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-violet-600 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-lg group-hover:shadow-indigo-500/30 transition-all duration-300 group-hover:scale-105">
                S
              </div>
              <div>
                <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-violet-600">SignalProphet</h1>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Engineering Suite</p>
              </div>
            </div>

            <nav className="flex items-center space-x-1 bg-slate-100/50 p-1 rounded-xl border border-slate-200/50 hidden md:flex">
              {[
                { id: 'system', label: 'Systems', icon: Activity },
                { id: 'roc', label: 'ROC', icon: Layers },
                { id: 'conv', label: 'Convolution', icon: Box },
                { id: 'series', label: 'Series', icon: Waves },
                { id: 'freq', label: 'Transform', icon: Zap },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-bold transition flex items-center gap-2 ${activeTab === tab.id
                    ? 'bg-white text-indigo-600 shadow-sm ring-1 ring-black/5'
                    : 'text-slate-500 hover:text-slate-900 hover:bg-white/50'
                    }`}
                >
                  <tab.icon size={16} strokeWidth={2.5} />
                  {tab.label}
                </button>
              ))}
            </nav>
            {/* Mobile simplified nav could go here */}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8 animate-fade-in min-h-[calc(100vh-200px)]">
        {activeTab === 'home' && (
          <div className="max-w-7xl mx-auto px-6 py-12">
            {/* Hero */}
            <div className="text-center space-y-8 py-16 mb-12">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-600 font-bold text-sm mb-4">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
                </span>
                v2.0 Now with Fourier Engine
              </div>
              <h1 className="text-6xl md:text-7xl font-extrabold text-slate-900 tracking-tight leading-tight">
                Master <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-500">Signals</span> & <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">Systems</span>
              </h1>
              <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
                The ultimate interactive playground for electrical engineering students and professionals. Analyze, visualize, and calculate in real-time.
              </p>
            </div>

            {/* Feature Grid */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              <div onClick={() => setActiveTab('system')} className="group bg-white rounded-3xl p-8 shadow-xl shadow-slate-200/50 border border-slate-100 hover:border-indigo-200 hover:shadow-2xl hover:shadow-indigo-500/10 transition-all duration-300 cursor-pointer relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-50 rounded-bl-full -mr-16 -mt-16 transition-transform group-hover:scale-110"></div>
                <Activity className="text-indigo-600 w-12 h-12 mb-6 relative z-10" strokeWidth={1.5} />
                <h3 className="text-2xl font-bold text-slate-900 mb-3">System Analyzer</h3>
                <p className="text-slate-500 leading-relaxed">Analyze linearity, output response $y(t)$, stability, and causality with step-by-step verification.</p>
              </div>

              <div onClick={() => setActiveTab('series')} className="group bg-white rounded-3xl p-8 shadow-xl shadow-slate-200/50 border border-slate-100 hover:border-blue-200 hover:shadow-2xl hover:shadow-blue-500/10 transition-all duration-300 cursor-pointer relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-bl-full -mr-16 -mt-16 transition-transform group-hover:scale-110"></div>
                <Waves className="text-blue-600 w-12 h-12 mb-6 relative z-10" strokeWidth={1.5} />
                <h3 className="text-2xl font-bold text-slate-900 mb-3">Fourier Series</h3>
                <p className="text-slate-500 leading-relaxed">Decompose periodic signals into harmonics. Visualize magnitude and phase spectra $a_k$.</p>
              </div>

              <div onClick={() => setActiveTab('freq')} className="group bg-white rounded-3xl p-8 shadow-xl shadow-slate-200/50 border border-slate-100 hover:border-violet-200 hover:shadow-2xl hover:shadow-violet-500/10 transition-all duration-300 cursor-pointer relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-violet-50 rounded-bl-full -mr-16 -mt-16 transition-transform group-hover:scale-110"></div>
                <Zap className="text-violet-600 w-12 h-12 mb-6 relative z-10" strokeWidth={1.5} />
                <h3 className="text-2xl font-bold text-slate-900 mb-3">Fourier Transform</h3>
                <p className="text-slate-500 leading-relaxed">Analyze non-periodic signals. Compute CTFT/DTFT symbolic expressions and plots.</p>
              </div>

              <div onClick={() => setActiveTab('roc')} className="group bg-white rounded-3xl p-8 shadow-xl shadow-slate-200/50 border border-slate-100 hover:border-purple-200 hover:shadow-2xl hover:shadow-purple-500/10 transition-all duration-300 cursor-pointer relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-purple-50 rounded-bl-full -mr-16 -mt-16 transition-transform group-hover:scale-110"></div>
                <Layers className="text-purple-600 w-12 h-12 mb-6 relative z-10" strokeWidth={1.5} />
                <h3 className="text-2xl font-bold text-slate-900 mb-3">ROC Explorer</h3>
                <p className="text-slate-600 leading-relaxed">Visualize poles, zeros, and Regions of Convergence (ROC) for Laplace & Z-Transform.</p>
              </div>

              <div onClick={() => setActiveTab('conv')} className="group bg-white rounded-3xl p-8 shadow-xl shadow-slate-200/50 border border-slate-100 hover:border-emerald-200 hover:shadow-2xl hover:shadow-emerald-500/10 transition-all duration-300 cursor-pointer relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-50 rounded-bl-full -mr-16 -mt-16 transition-transform group-hover:scale-110"></div>
                <Box className="text-emerald-600 w-12 h-12 mb-6 relative z-10" strokeWidth={1.5} />
                <h3 className="text-2xl font-bold text-slate-900 mb-3">Convolution Lab</h3>
                <p className="text-slate-600 leading-relaxed">Interactive "Fold-Shift-Multiply-Add" animation for understanding convolution $x * h$.</p>
              </div>
            </div>

            {/* References Section */}
            <div className="mt-20 border-t border-slate-200 pt-12">
              <h2 className="text-3xl font-bold text-slate-900 text-center mb-10">Recommended Resources</h2>
              <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                {/* Lectures */}
                <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm hover:shadow-md transition">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center text-red-600 font-bold">
                      <svg viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6"><path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z" /></svg>
                    </div>
                    <h3 className="text-xl font-bold text-slate-800">Video Lectures</h3>
                  </div>
                  <ul className="space-y-3 text-sm">
                    <li>
                      <a href="https://www.youtube.com/watch?v=-FHm2pQmiSM&list=PLUl4u3cNGP61kdPAOC7CzFjJZ8f1eMUxs" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline font-medium flex items-center gap-2">
                        MIT OpenCourseWare Use <span className="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full">Classic</span>
                      </a>
                      <p className="text-slate-500 mt-1">Signals and Systems (Oppenheim)</p>
                    </li>
                    <li>
                      <a href="https://www.youtube.com/watch?v=KJnAy6hzetw&list=PL41692B571DD0AF9B" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline font-medium">
                        NPTEL Series
                      </a>
                      <p className="text-slate-500 mt-1">Comprehensive lecture series on Signals & Systems</p>
                    </li>
                  </ul>
                </div>

                {/* Books */}
                <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm hover:shadow-md transition">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center text-emerald-600 font-bold">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                    </div>
                    <h3 className="text-xl font-bold text-slate-800">Textbooks</h3>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <a href="http://materias.df.uba.ar/l5a2021c1/files/2021/05/Alan-V.-Oppenheim-Alan-S.-Willsky-with-S.-Hamid-Signals-and-Systems-Prentice-Hall-1996.pdf" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline font-bold block">
                        Signals and Systems (2nd Ed)
                      </a>
                      <p className="text-slate-600 text-sm">Alan V. Oppenheim & Alan S. Willsky</p>
                      <p className="text-slate-400 text-xs mt-1">The definitive guide. PDF Available.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'system' && <SystemAnalyzer />}

        {activeTab === 'roc' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center max-w-2xl mx-auto pt-8">
              <h1 className="text-3xl font-bold text-slate-900 mb-2">ROC Explorer</h1>
              <p className="text-slate-600">Laplace & Z-Transform Analysis</p>
            </div>
            <ROCExplorer />
          </div>
        )}

        {activeTab === 'conv' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center max-w-2xl mx-auto pt-8">
              <h1 className="text-3xl font-bold text-slate-900 mb-2">Convolution Lab</h1>
              <p className="text-slate-600">Visualizing the Convolution Integral/Sum</p>
            </div>
            <ConvolutionLab />
          </div>
        )}

        {activeTab === 'series' && <FourierSeries />}

        {activeTab === 'freq' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center max-w-2xl mx-auto pt-8">
              <h1 className="text-3xl font-bold text-slate-900 mb-2">Fourier Transform Lab</h1>
              <p className="text-slate-600">Continuous & Discrete Time Fourier Transforms</p>
            </div>
            <FrequencyLab />
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="bg-slate-50 border-t border-slate-200 mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center text-white font-bold text-lg">S</div>
                <span className="font-bold text-slate-900">SignalProphet</span>
              </div>
              <p className="text-slate-500 text-sm max-w-sm">
                Built for students and engineers to visualize the mathematics of signal processing.
              </p>
            </div>
            <div className="text-right text-sm text-slate-400">
              <p>© 2025 SignalProphet Inc.</p>
              <p>Powered by Python (SymPy) & React</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
