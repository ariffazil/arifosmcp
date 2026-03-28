// arifosmcp.intelligence/dashboard/src/components/BalancePanel.tsx
import React from 'react';
import { Scale, Zap, Wind, AlertCircle } from 'lucide-react';

interface BalancePanelProps {
  thermo: {
    avg_delta_s: number;
    peace2: number;
    omega_0: number;
    genius: number;
  };
}

const BalancePanel: React.FC<BalancePanelProps> = ({ thermo }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 shadow-xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-teal-900/30 rounded-lg">
          <Scale className="w-5 h-5 text-teal-400" />
        </div>
        <h3 className="text-lg font-semibold text-slate-100 italic">Balance — Thermodynamics</h3>
      </div>
      
      <div className="space-y-5">
        <div>
          <div className="flex justify-between items-center mb-2">
            <div className="flex items-center gap-2 text-slate-400">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span className="text-xs font-mono uppercase tracking-wider">Genius Score (G)</span>
            </div>
            <span className={`text-sm font-bold ${thermo.genius >= 0.8 ? 'text-teal-400' : 'text-red-400'}`}>
              {thermo.genius.toFixed(3)}
            </span>
          </div>
          <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-700/50">
            <div 
              className={`h-full transition-all duration-700 ${thermo.genius >= 0.8 ? 'bg-teal-500 shadow-[0_0_10px_rgba(20,184,166,0.5)]' : 'bg-red-500'}`}
              style={{ width: `${thermo.genius * 100}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-[9px] mt-1 text-slate-600 font-mono">
            <span>Threshold: 0.800</span>
            <span>Current: {thermo.genius >= 0.8 ? 'PASS' : 'VOID'}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-900/30 p-3 rounded border border-slate-700/20">
            <div className="flex items-center gap-2 text-slate-500 mb-1">
              <Wind className="w-3 h-3" />
              <span className="text-[10px] uppercase font-bold">Δ Entropy</span>
            </div>
            <div className={`text-lg font-mono font-bold ${thermo.avg_delta_s <= 0 ? 'text-teal-400' : 'text-orange-400'}`}>
              {thermo.avg_delta_s > 0 ? '+' : ''}{thermo.avg_delta_s.toFixed(3)}
            </div>
          </div>

          <div className="bg-slate-900/30 p-3 rounded border border-slate-700/20">
            <div className="flex items-center gap-2 text-slate-500 mb-1">
              <AlertCircle className="w-3 h-3" />
              <span className="text-[10px] uppercase font-bold">Uncertainty Ω₀</span>
            </div>
            <div className={`text-lg font-mono font-bold ${thermo.omega_0 >= 0.03 && thermo.omega_0 <= 0.15 ? 'text-teal-400' : 'text-red-400'}`}>
              {thermo.omega_0.toFixed(3)}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-slate-700/50 text-[10px] text-slate-500 uppercase tracking-widest font-bold flex justify-between">
        <span>Stability (P²)</span>
        <span className="text-teal-500">{thermo.peace2.toFixed(2)}</span>
      </div>
    </div>
  );
};

export default BalancePanel;
