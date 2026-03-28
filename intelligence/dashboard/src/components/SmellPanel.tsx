// arifosmcp.intelligence/dashboard/src/components/SmellPanel.tsx
import React from 'react';
import { Radar } from 'lucide-react';

const SmellPanel: React.FC = () => {
  const anomalies = [
    { type: 'DRIFT', score: 0.12, label: 'Constitutional Alignment' },
    { type: 'SPIKE', score: 0.45, label: 'Latent Hallucination' },
    { type: 'NOISE', score: 0.08, label: 'Semantic Entropy' },
  ];

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 shadow-xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-yellow-900/30 rounded-lg">
          <Radar className="w-5 h-5 text-yellow-400" />
        </div>
        <h3 className="text-lg font-semibold text-slate-100 italic">Smell — Anomaly Detection</h3>
      </div>
      
      <div className="space-y-6">
        {anomalies.map((a, i) => (
          <div key={i}>
            <div className="flex justify-between items-center mb-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{a.label}</span>
              <span className="text-[10px] font-mono text-slate-500">{a.type}</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex-1 h-1 bg-slate-950 rounded-full overflow-hidden">
                <div 
                  className={`h-full ${a.score > 0.4 ? 'bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.4)]' : 'bg-teal-500 opacity-50'}`}
                  style={{ width: `${a.score * 100}%` }}
                ></div>
              </div>
              <span className={`text-xs font-mono font-bold ${a.score > 0.4 ? 'text-orange-400' : 'text-slate-500'}`}>
                {(a.score * 10).toFixed(1)}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 relative h-12 bg-slate-900/50 rounded-lg border border-slate-700/30 overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-around opacity-20">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="w-px h-full bg-yellow-500/50 animate-pulse" style={{ animationDelay: `${i * 0.2}s` }}></div>
          ))}
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-[9px] font-black text-slate-500 uppercase tracking-[0.3em]">Scanning Olfactory Latents</span>
        </div>
      </div>
    </div>
  );
};

export default SmellPanel;
