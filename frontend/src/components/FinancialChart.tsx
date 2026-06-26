import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { motion } from 'framer-motion';
import { SparklesIcon } from '@heroicons/react/24/outline';
import type { FinancialSummary } from '../types';

interface FinancialChartProps {
  summary: FinancialSummary;
}

const COLORS = {
  parts: '#EF4444',
  labor: '#3B82F6',
  margin: '#22C55E',
  taxes: '#F59E0B',
};

function CostBreakdownPie({ data }: { data: Record<string, number> }) {
  const chartData = [
    { name: 'Parts', value: data.parts || 0, color: COLORS.parts },
    { name: 'Labor', value: data.labor || 0, color: COLORS.labor },
    { name: 'Margin', value: data.margin || 0, color: COLORS.margin },
    { name: 'Taxes', value: data.taxes || 0, color: COLORS.taxes },
  ].filter(d => d.value > 0);

  if (chartData.length === 0) return null;

  const total = chartData.reduce((s, d) => s + d.value, 0);

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
          >
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.color} stroke="transparent" />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: any) => `$${Number(value).toFixed(2)}`}
            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex justify-center gap-4 text-xs mt-2">
        {chartData.map(d => (
          <div key={d.name} className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: d.color }} />
            <span className="text-gray-600">{d.name}</span>
            <span className="font-medium text-gray-900">
              {((d.value / total) * 100).toFixed(0)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function BudgetVsActualBar({ data }: { data: Record<string, number> }) {
  const chartData = [
    {
      name: 'Parts',
      Budgeted: data.budgeted_parts || 0,
      Actual: data.actual_parts || 0,
    },
    {
      name: 'Labor',
      Budgeted: data.budgeted_labor || 0,
      Actual: data.actual_labor || 0,
    },
    {
      name: 'Total',
      Budgeted: data.budgeted_total || 0,
      Actual: data.actual_total || 0,
    },
  ];

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} barGap={4}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}`} />
          <Tooltip
            formatter={(value: any) => `$${Number(value).toFixed(2)}`}
            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
          />
          <Bar dataKey="Budgeted" fill="#3B82F6" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Actual" fill="#22C55E" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
      <div className="flex justify-center gap-6 text-xs mt-2">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-blue-500" />
          <span className="text-gray-600">Budgeted</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-green-500" />
          <span className="text-gray-600">Actual</span>
        </div>
      </div>
    </div>
  );
}

function ScoreGauge({ score }: { score: number }) {
  const color = score >= 90 ? '#22C55E' : score >= 70 ? '#3B82F6' : score >= 50 ? '#F59E0B' : '#EF4444';
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="#e5e7eb" strokeWidth="10" />
        <motion.circle
          cx="70" cy="70" r={radius}
          fill="none" stroke={color} strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
          transform="rotate(-90 70 70)"
        />
        <text x="70" y="65" textAnchor="middle" className="text-3xl font-bold" fill="#111827">
          {score}
        </text>
        <text x="70" y="85" textAnchor="middle" className="text-xs" fill="#6b7280">
          /100
        </text>
      </svg>
    </div>
  );
}

export default function FinancialChart({ summary }: FinancialChartProps) {
  const { chart_data: chartData, profitability: p, performance_metrics: pm } = summary;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card bg-gradient-to-br from-gray-50 to-white"
    >
      <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center">
        <SparklesIcon className="w-5 h-5 mr-2 text-jing-secondary" />
        Financial Performance
      </h3>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Donut Chart */}
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3">Cost Breakdown</h4>
          <CostBreakdownPie data={chartData.cost_breakdown} />
        </div>

        {/* Bar Chart */}
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3">Budget vs Actual</h4>
          <BudgetVsActualBar data={chartData.budget_vs_actual} />
        </div>

        {/* Score Gauge + Metrics */}
        <div className="bg-white rounded-xl p-4 shadow-sm flex flex-col items-center justify-center">
          <ScoreGauge score={pm.overall_score} />
          <div className="mt-3 text-center">
            <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${
              p.profitability_grade === 'A' ? 'bg-green-100 text-green-800' :
              p.profitability_grade === 'B' ? 'bg-blue-100 text-blue-800' :
              p.profitability_grade === 'C' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              Grade {p.profitability_grade}
            </span>
            <p className="text-xs text-gray-500 mt-1">{pm.score_label}</p>
          </div>
        </div>
      </div>

      {/* Quick metrics row */}
      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="text-center p-3 bg-green-50 rounded-xl">
          <p className="text-xs text-green-600">Revenue</p>
          <p className="text-lg font-bold text-green-800">${p.gross_revenue.toFixed(2)}</p>
        </div>
        <div className="text-center p-3 bg-blue-50 rounded-xl">
          <p className="text-xs text-blue-600">Profit</p>
          <p className="text-lg font-bold text-blue-800">${p.gross_profit.toFixed(2)}</p>
        </div>
        <div className="text-center p-3 bg-amber-50 rounded-xl">
          <p className="text-xs text-amber-600">Rate</p>
          <p className="text-lg font-bold text-amber-800">${p.effective_hourly_rate.toFixed(2)}/h</p>
        </div>
      </div>

      {/* Celebration */}
      {summary.celebration_message && (
        <div className="mt-6 bg-green-100 rounded-xl p-4 flex items-start gap-3">
          <SparklesIcon className="w-5 h-5 text-green-600 mt-0.5 shrink-0" />
          <div>
            <p className="font-semibold text-green-900">Job Performance</p>
            <p className="text-sm text-green-700 mt-1">{summary.celebration_message}</p>
          </div>
        </div>
      )}
    </motion.div>
  );
}
