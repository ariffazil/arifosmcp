// arifosmcp.intelligence/dashboard/src/components/TastePanel.tsx
import React from 'react';
import { Utensils, PieChart } from 'lucide-react';
import { PieChart as RePieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface TastePanelProps {
  verdicts: Record<string, number>;
}

const COLORS = {
  SEAL: '#14b8a6',    // Teal 500
  PARTIAL: '#eab308', // Yellow 500
  SABAR: '#f97316',   // Orange 500
  HOLD: '#ef4444',    // Red 500
  VOID: '#7f1d1d',    // Dark Red
};

const TastePanel: React.FC<TastePanelProps> = ({ verdicts }) => {
  const data = Object.entries(verdicts).map(([name, value]) => ({ name, value }));
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 shadow-xl min-h-[350px] flex flex-col">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-purple-900/30 rounded-lg">
          <Utensils className="w-5 h-5 text-purple-400" />
        </div>
        <h3 className="text-lg font-semibold text-slate-100 italic">Taste — Verdict Digest</h3>
      </div>
      
      <div className="flex-1 min-h-[200px] relative">
        <ResponsiveContainer width="100%" height="100%">
          <RePieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] || '#475569'} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
              itemStyle={{ color: '#f1f5f9' }}
            />
          </RePieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <PieChart className="w-6 h-6 text-slate-600 mx-auto mb-1" />
            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-tighter">Metabolic<br/>Distribution</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 mt-4">
        {data.map((entry) => (
          <div key={entry.name} className="flex flex-col items-center p-2 rounded bg-slate-900/30 border border-slate-700/20">
            <div className={`w-2 h-2 rounded-full mb-1`} style={{ backgroundColor: COLORS[entry.name as keyof typeof COLORS] }}></div>
            <div className="text-[9px] text-slate-500 font-mono font-bold">{entry.name}</div>
            <div className="text-xs font-bold text-slate-200">{(entry.value * 100).toFixed(0)}%</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TastePanel;
