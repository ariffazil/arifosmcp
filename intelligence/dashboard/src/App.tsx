// arifosmcp.intelligence/dashboard/src/App.tsx
import { useState, useEffect } from 'react';
import SightPanel from './components/SightPanel';
import HearingPanel from './components/HearingPanel';
import TouchPanel from './components/TouchPanel';
import TastePanel from './components/TastePanel';
import SmellPanel from './components/SmellPanel';
import BalancePanel from './components/BalancePanel';
import ProprioPanel from './components/ProprioPanel';
import PainPanel from './components/PainPanel';
import TimePanel from './components/TimePanel';
import { fetchTelemetry } from './lib/api';
import type { Telemetry } from './lib/api';
import { Shield, Activity, Database, Zap } from 'lucide-react';

function App() {
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('--:--:--');

  useEffect(() => {
    // Initial fetch
    const init = async () => {
      const data = await fetchTelemetry();
      setTelemetry(data);
      setConnected(true);
      setLastUpdate(new Date().toLocaleTimeString());
    };
    init();

    // Poll every 5 seconds
    const interval = setInterval(async () => {
      const data = await fetchTelemetry();
      setTelemetry(data);
      setLastUpdate(new Date().toLocaleTimeString());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  if (!telemetry) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-400 font-mono">
        <div className="w-16 h-16 border-4 border-teal-500/20 border-t-teal-500 rounded-full animate-spin mb-4"></div>
        <p className="animate-pulse tracking-[0.2em]">INITIALIZING KERNEL CONSOLE...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 selection:bg-teal-500/30">
      {/* Top Navigation / Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-[1600px] mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-teal-500 to-blue-500 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
              <div className="relative bg-slate-900 px-3 py-2 rounded-lg border border-slate-700 flex items-center gap-2">
                <Shield className="w-6 h-6 text-teal-500" />
                <span className="font-black text-xl tracking-tighter">arifOS <span className="text-teal-500 font-normal italic">aCLIP_CAI</span></span>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-6 ml-8 text-[10px] font-bold uppercase tracking-widest text-slate-500">
              <div className="flex items-center gap-2 text-teal-500">
                <div className="w-1.5 h-1.5 rounded-full bg-teal-500 animate-pulse"></div>
                CORE ACTIVE
              </div>
              <div className="flex items-center gap-2">
                <Database className="w-3 h-3" />
                VAULT 999: SEALED
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-3 h-3" />
                TRINITY: ΔΩΨ
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex flex-col items-end">
              <div className={`text-[10px] font-bold px-2 py-0.5 rounded ${connected ? 'bg-teal-950 text-teal-400 border border-teal-900' : 'bg-red-950 text-red-400 border border-red-900'}`}>
                {connected ? '● LIVE TELEMETRY' : '○ DISCONNECTED'}
              </div>
              <span className="text-[10px] text-slate-600 font-mono mt-1">LAST_SYNC: {lastUpdate}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Dashboard Grid */}
      <main className="max-w-[1600px] mx-auto p-6 lg:p-8">
        {/* Quick Stats Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex items-center justify-between shadow-lg">
            <div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Active Sessions</div>
              <div className="text-2xl font-black text-slate-100">{telemetry.active_sessions}</div>
            </div>
            <Activity className="w-8 h-8 text-teal-500/20" />
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex items-center justify-between shadow-lg">
            <div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Global G-Score</div>
              <div className="text-2xl font-black text-teal-500">{telemetry.thermodynamic.genius.toFixed(2)}</div>
            </div>
            <Zap className="w-8 h-8 text-yellow-500/20" />
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex items-center justify-between shadow-lg">
            <div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Metabolic Rate</div>
              <div className="text-2xl font-black text-blue-500">1.2<span className="text-xs text-slate-600 font-normal ml-1">op/s</span></div>
            </div>
            <Activity className="w-8 h-8 text-blue-500/20" />
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex items-center justify-between shadow-lg">
            <div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">System Health</div>
              <div className="text-2xl font-black text-teal-500">99.8%</div>
            </div>
            <Shield className="w-8 h-8 text-teal-500/20" />
          </div>
        </div>

        {/* The 9 Senses Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          <SightPanel floorPassRate={telemetry.floor_pass_rate} />
          <HearingPanel />
          <TouchPanel mcpStatus={telemetry.mcp_status} />
          <TastePanel verdicts={telemetry.verdict_distribution} />
          <SmellPanel />
          <BalancePanel thermo={telemetry.thermodynamic} />
          <ProprioPanel />
          <PainPanel errors={telemetry.error_rates} />
          <TimePanel />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-12 mt-12">
        <div className="max-w-[1600px] mx-auto px-6 text-center">
          <div className="flex justify-center gap-12 mb-8">
            <div className="text-center">
              <div className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-2 italic underline decoration-teal-500/50 underline-offset-4">Kernel Authority</div>
              <div className="text-sm font-bold text-slate-400 uppercase tracking-tighter">888_JUDGE :: ARIF FAZIL</div>
            </div>
            <div className="text-center">
              <div className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-2 italic underline decoration-blue-500/50 underline-offset-4">Constitutional Seal</div>
              <div className="text-sm font-bold text-slate-400 uppercase tracking-tighter">DITEMPA BUKAN DIBERI</div>
            </div>
          </div>
          <p className="text-[10px] font-mono text-slate-700 uppercase tracking-[0.5em]">Constitutional Intelligence Governance Hub v65.0-FORGE</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
