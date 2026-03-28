// arifosmcp.intelligence/dashboard/src/components/SightPanel.tsx
import React from 'react';
import { Eye } from 'lucide-react';

interface SightPanelProps {
  floorPassRate: Record<string, number>;
}

const SightPanel: React.FC<SightPanelProps> = ({ floorPassRate }) => {
  const floors = Object.entries(floorPassRate).sort((a, b) => a[0].localeCompare(b[0]));
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 shadow-xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-blue-900/30 rounded-lg">
          <Eye className="w-5 h-5 text-blue-400" />
        </div>
        <h3 className="text-lg font-semibold text-slate-100 italic">Sight — Floor Pass Rates</h3>
      </div>
      
      <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
        {floors.map(([floor, rate]) => {
          const percentage = (rate * 100).toFixed(1);
          const isHard = ['F1', 'F2', 'F6', 'F7', 'F10', 'F11', 'F12'].includes(floor);
          
          let color = 'bg-teal-500';
          let textColor = 'text-teal-300';
          
          if (rate < 0.85) {
            color = 'bg-red-500';
            textColor = 'text-red-300';
          } else if (rate < 0.95) {
            color = 'bg-yellow-500';
            textColor = 'text-yellow-300';
          }

          return (
            <div key={floor} className="group">
              <div className="flex justify-between text-xs mb-1.5 px-1">
                <span className="text-slate-400 font-mono">
                  {floor} {isHard && <span className="text-[10px] bg-red-950 text-red-400 px-1 rounded ml-1">HARD</span>}
                </span>
                <span className={`${textColor} font-bold`}>{percentage}%</span>
              </div>
              <div className="w-full bg-slate-950 rounded-full h-1.5 border border-slate-700/50">
                <div 
                  className={`${color} h-full rounded-full transition-all duration-500 ease-out shadow-[0_0_8px_rgba(0,0,0,0.5)]`}
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-6 pt-4 border-t border-slate-700/50 flex justify-between items-center text-[10px] text-slate-500 uppercase tracking-widest font-bold">
        <span>Anvil Status</span>
        <span className="text-teal-500">Stability Confirmed</span>
      </div>
    </div>
  );
};

export default SightPanel;
