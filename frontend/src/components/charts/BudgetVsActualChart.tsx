import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { motion } from 'framer-motion';
import type { ChartData } from '../../types';

interface BudgetVsActualChartProps {
  data: ChartData['budget_vs_actual'];
}

export default function BudgetVsActualChart({ data }: BudgetVsActualChartProps) {
  const chartData = [
    { name: 'Parts', Budgeted: data.budgeted_parts, Actual: data.actual_parts },
    { name: 'Labor', Budgeted: data.budgeted_labor, Actual: data.actual_labor },
    { name: 'Total', Budgeted: data.budgeted_total, Actual: data.actual_total },
  ];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white px-4 py-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-900 mb-2">{label}</p>
          {payload.map((item: any, idx: number) => (
            <p key={idx} className="text-sm" style={{ color: item.color }}>
              {item.name}: ${item.value.toFixed(2)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.3 }}
      className="card"
    >
      <h3 className="text-xl font-bold text-gray-900 mb-4">Budget vs Actual</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="name" stroke="#6B7280" />
            <YAxis stroke="#6B7280" />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="Budgeted" fill="#9CA3AF" radius={[8, 8, 0, 0]} />
            <Bar dataKey="Actual" fill="#DC2626" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
