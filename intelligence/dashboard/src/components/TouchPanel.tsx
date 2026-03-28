// arifosmcp.intelligence/dashboard/src/components/TouchPanel.tsx
import React from 'react';
import { Fingerprint, Cpu, HardDrive, Network } from 'lucide-react';

interface TouchPanelProps {
  mcpStatus: {
    processes: number;
    tools: number;
    latency_avg: number;
  };
}

const TouchPanel: React.FC<TouchPanelProps> = ({ mcpStatus }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 shadow-xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-orange-900/30 rounded-lg">
          <Fingerprint className="w-5 h-5 text-orange-400" />
        </div>
        <h3 className="text-lg font-semibold text-slate-100 italic">Touch — Infrastructure Load</h3>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/30">
          <div className="flex items-center gap-2 text-slate-400 mb-2">
            <Cpu className="w-4 h-4" />
            <span className="text-xs font-mono uppercase tracking-wider">Kernels</span>
          </div>
          <div className="text-2xl font-bold text-slate-100">{mcpStatus.processes}</div>
          <div className="text-[10px] text-slate-500 mt-1 italic">Active Brain Adapters</div>
        </div>

        <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/30">
          <div className="flex items-center gap-2 text-slate-400 mb-2">
            <Network className="w-4 h-4" />
            <span className="text-xs font-mono uppercase tracking-wider">Senses</span>
          </div>
          <div className="text-2xl font-bold text-slate-100">{mcpStatus.tools}</div>
          <div className="text-[10px] text-slate-500 mt-1 italic">9-Sense MCP Tools</div>
        </div>

        <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/30 col-span-2">
          <div className="flex justify-between items-center mb-2">
            <div className="flex items-center gap-2 text-slate-400">
              <HardDrive className="w-4 h-4" />
              <span className="text-xs font-mono uppercase tracking-wider">Avg Latency</span>
            </div>
            <span className="text-teal-400 text-xs font-bold">{mcpStatus.latency_avg}ms</span>
          </div>
          <div className="w-full bg-slate-950 rounded-full h-1">
            <div 
              className="bg-teal-500 h-full rounded-full"
              style={{ width: `${Math.min(100, (mcpStatus.latency_avg / 200) * 100)}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-slate-700/50 text-[10px] text-slate-500 uppercase tracking-widest font-bold text-center">
        Sensory Pressure: <span className="text-teal-500">Nominal</span>
      </div>
    </div>
  );
};

export default TouchPanel;
