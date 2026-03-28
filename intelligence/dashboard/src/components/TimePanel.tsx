// arifosmcp.intelligence/dashboard/src/components/TimePanel.tsx
import React from 'react';
import { Clock, History } from 'lucide-react';

const TimePanel: React.FC = () => {
  const events = [
    { time: '14:22:01', event: 'INIT_000', session: 'S-8821', status: 'PASS' },
    { time: '14:21:45', event: 'VAULT_999', session: 'S-8820', status: 'SEAL' },
    { time: '14:20:12', event: 'EMPATHY_555', session: 'S-8821', status: 'ACTIVE' },
    { time: '14:18:30', event: 'SABAR_72', session: 'S-8819', status: 'WAIT' },
  ];

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 shadow-xl min-h-[350px] flex flex-col">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-indigo-900/30 rounded-lg">
          <Clock className="w-5 h-5 text-indigo-400" />
        </div>
        <h3 className="text-lg font-semibold text-slate-100 italic">Time — Session Timeline</h3>
      </div>
      
      <div className="flex-1 space-y-4 overflow-y-auto pr-2 custom-scrollbar">
        {events.map((e, i) => (
          <div key={i} className="flex gap-4 items-start relative pb-4 last:pb-0">
            {i !== events.length - 1 && (
              <div className="absolute left-[9px] top-6 bottom-0 w-px bg-slate-700"></div>
            )}
            <div className={`mt-1.5 w-5 h-5 rounded-full border-2 border-slate-800 z-10 ${
              e.status === 'PASS' ? 'bg-teal-500' : 
              e.status === 'SEAL' ? 'bg-blue-500' :
              e.status === 'WAIT' ? 'bg-orange-500' : 'bg-indigo-500'
            }`}></div>
            <div className="flex-1 min-w-0">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs font-bold text-slate-200 uppercase tracking-tighter">{e.event}</span>
                <span className="text-[10px] font-mono text-slate-500">{e.time}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[10px] text-slate-400 font-mono">ID: {e.session}</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300 font-bold uppercase">{e.status}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-slate-700/50 flex items-center justify-center gap-2 text-slate-500 hover:text-slate-300 cursor-pointer transition-colors">
        <History className="w-3 h-3" />
        <span className="text-[10px] font-bold uppercase tracking-widest">Full Metabolic Audit</span>
      </div>
    </div>
  );
};

export default TimePanel;
