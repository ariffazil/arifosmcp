// arifosmcp.intelligence/dashboard/src/components/PainPanel.tsx
import React from 'react';
import { Activity, ShieldAlert, XCircle } from 'lucide-react';

interface PainPanelProps {
  errors: {
    f12_blocks: number;
    void_verdicts: number;
  };
}

const PainPanel: React.FC<PainPanelProps> = ({ errors }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 shadow-xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-red-900/30 rounded-lg">
          <Activity className="w-5 h-5 text-red-400" />
        </div>
        <h3 className="text-lg font-semibold text-slate-100 italic">Pain — Sensory Failure</h3>
      </div>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-red-950/20 rounded-lg border border-red-900/20 group hover:bg-red-950/30 transition-colors">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-5 h-5 text-red-500" />
            <div>
              <div className="text-sm font-bold text-slate-200 uppercase tracking-tight">F12 Blocks</div>
              <div className="text-[10px] text-slate-500 italic">Injection Defenses Engaged</div>
            </div>
          </div>
          <div className="text-3xl font-black text-red-500/80 group-hover:text-red-500 transition-colors">{errors.f12_blocks}</div>
        </div>

        <div className="flex items-center justify-between p-4 bg-slate-900/40 rounded-lg border border-slate-700/30 group hover:bg-slate-900/60 transition-colors">
          <div className="flex items-center gap-3">
            <XCircle className="w-5 h-5 text-orange-500" />
            <div>
              <div className="text-sm font-bold text-slate-200 uppercase tracking-tight">VOID Verdicts</div>
              <div className="text-[10px] text-slate-500 italic">Constitutional Breaches</div>
            </div>
          </div>
          <div className="text-3xl font-black text-orange-500/80 group-hover:text-orange-500 transition-colors">{errors.void_verdicts}</div>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-slate-700/50 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-950/30 border border-teal-900/30 text-[10px] font-bold text-teal-500 uppercase tracking-widest">
          <div className="w-1.5 h-1.5 rounded-full bg-teal-500 animate-pulse"></div>
          System Integrity: Stable
        </div>
      </div>
    </div>
  );
};

export default PainPanel;
