import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { motion } from 'framer-motion';
import type { ChartData } from '../../types';

interface CostBreakdownChartProps {
  data: ChartData['cost_breakdown'];
}

const COLORS = ['#DC2626', '#1E40AF', '#10B981', '#F59E0B'];

export default function CostBreakdownChart({ data }: CostBreakdownChartProps) {
  const chartData = [
    { name: 'Parts', value: data.parts, color: COLORS[0] },
    { name: 'Labor', value: data.labor, color: COLORS[1] },
    { name: 'Margin', value: data.margin, color: COLORS[2] },
    { name: 'Taxes', value: data.taxes, color: COLORS[3] },
  ];

  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      const pct = ((d.value / total) * 100).toFixed(1);
      return (
        <div className="bg-white px-4 py-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-900">{d.name}</p>
          <p className="text-sm text-gray-600">${d.value.toFixed(2)} ({pct}%)</p>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.2 }}
      className="card"
    >
      <h3 className="text-xl font-bold text-gray-900 mb-4">Cost Distribution</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={chartData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="grid grid-cols-2 gap-3 mt-4">
        {chartData.map((item, idx) => (
          <div key={idx} className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: item.color }} />
            <div className="flex-1">
              <p className="text-sm font-semibold text-gray-900">{item.name}</p>
              <p className="text-xs text-gray-600">${item.value.toFixed(2)} ({((item.value / total) * 100).toFixed(1)}%)</p>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
