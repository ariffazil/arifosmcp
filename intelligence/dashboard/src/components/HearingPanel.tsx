// arifosmcp.intelligence/dashboard/src/components/HearingPanel.tsx
import React from 'react';
import { Volume2, Terminal } from 'lucide-react';

const HearingPanel: React.FC = () => {
  const logs = [
    { type: 'IN', msg: 'CALL: syscall_anchor', time: '14:35:01' },
    { type: 'OUT', msg: 'VERDICT: SEAL (pass=1.0)', time: '14:35:02' },
    { type: 'IN', msg: 'CALL: aclip_system_health', time: '14:35:10' },
    { type: 'OUT', msg: 'DATA: cpu=12.5%, mem=88%', time: '14:35:11' },
    { type: 'SYS', msg: 'CLEANUP: Session S-122 expired', time: '14:36:00' },
  ];

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 shadow-xl flex flex-col min-h-[350px]">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-blue-900/30 rounded-lg">
          <Volume2 className="w-5 h-5 text-blue-400" />
        </div>
        <h3 className="text-lg font-semibold text-slate-100 italic">Hearing — Metabolic Logs</h3>
      </div>
      
      <div className="flex-1 bg-slate-950/80 rounded border border-slate-700/50 p-4 font-mono text-[10px] space-y-2 overflow-y-auto max-h-[200px] custom-scrollbar shadow-inner">
        {logs.map((l, i) => (
          <div key={i} className="flex gap-2 group">
            <span className="text-slate-600">[{l.time}]</span>
            <span className={`font-bold ${
              l.type === 'IN' ? 'text-blue-500' : 
              l.type === 'OUT' ? 'text-teal-500' : 'text-slate-500'
            }`}>{l.type}</span>
            <span className="text-slate-300 group-hover:text-slate-100 transition-colors">{l.msg}</span>
          </div>
        ))}
        <div className="animate-pulse flex items-center gap-1">
          <span className="w-1.5 h-3 bg-teal-500"></span>
          <span className="text-teal-500">LISTENING...</span>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-slate-700/50 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Terminal className="w-3 h-3 text-slate-500" />
          <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest underline decoration-dotted">Live Stdout Stream</span>
        </div>
        <span className="text-[9px] font-bold text-teal-500 bg-teal-950 px-2 py-0.5 rounded">v2.4-STABLE</span>
      </div>
    </div>
  );
};

export default HearingPanel;
