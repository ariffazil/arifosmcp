// arifosmcp.intelligence/dashboard/src/components/ProprioPanel.tsx
import React from 'react';
import { Activity, Globe, Zap } from 'lucide-react';

const ProprioPanel: React.FC = () => {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 shadow-xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-emerald-900/30 rounded-lg">
          <Activity className="w-5 h-5 text-emerald-400" />
        </div>
        <h3 className="text-lg font-semibold text-slate-100 italic">Proprio — Self Health</h3>
      </div>
      
      <div className="space-y-4">
        <div className="flex items-center gap-4 p-3 bg-slate-900/50 rounded-lg border border-slate-700/20">
          <div className="p-2 bg-teal-500/10 rounded border border-teal-500/20">
            <Globe className="w-4 h-4 text-teal-500" />
          </div>
          <div className="flex-1">
            <div className="text-[10px] font-bold text-slate-500 uppercase">MCP Federation</div>
            <div className="text-sm font-bold text-slate-200">9 Nodes Detected</div>
          </div>
          <div className="text-[10px] text-teal-500 font-bold bg-teal-950/50 px-2 py-0.5 rounded border border-teal-900/50">LIVE</div>
        </div>

        <div className="flex items-center gap-4 p-3 bg-slate-900/50 rounded-lg border border-slate-700/20 opacity-50">
          <div className="p-2 bg-slate-500/10 rounded border border-slate-500/20">
            <Zap className="w-4 h-4 text-slate-500" />
          </div>
          <div className="flex-1">
            <div className="text-[10px] font-bold text-slate-500 uppercase">Quantum Reflex</div>
            <div className="text-sm font-bold text-slate-200">8.7ms Baseline</div>
          </div>
          <div className="text-[10px] text-slate-500 font-bold bg-slate-950/50 px-2 py-0.5 rounded border border-slate-900/50">IDLE</div>
        </div>
      </div>

      <div className="mt-6 flex justify-around">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="w-2 h-8 bg-slate-950 rounded-sm relative overflow-hidden">
            <div className="absolute bottom-0 left-0 right-0 bg-teal-500/40 animate-pulse" style={{ height: `${20 + i * 15}%`, animationDelay: `${i * 0.1}s` }}></div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProprioPanel;
