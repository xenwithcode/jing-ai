import { motion } from 'framer-motion';
import { TrophyIcon, CurrencyDollarIcon, ClockIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import type { Profitability, PerformanceMetrics } from '../types';

interface ProfitabilityCardProps {
  profitability: Profitability;
  performance: PerformanceMetrics;
}

function getGradeColor(grade: string): string {
  switch (grade) {
    case 'A': return 'from-green-400 to-emerald-600';
    case 'B': return 'from-blue-400 to-blue-600';
    case 'C': return 'from-yellow-400 to-yellow-600';
    case 'D': return 'from-orange-400 to-orange-600';
    case 'F': return 'from-red-400 to-red-600';
    default: return 'from-gray-400 to-gray-600';
  }
}

function getScoreColor(score: number): string {
  if (score >= 90) return 'text-green-600';
  if (score >= 75) return 'text-blue-600';
  if (score >= 60) return 'text-yellow-600';
  if (score >= 40) return 'text-orange-600';
  return 'text-red-600';
}

export default function ProfitabilityCard({ profitability, performance }: ProfitabilityCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="card bg-gradient-to-br from-white to-gray-50"
    >
      <div className="flex items-center space-x-3 mb-6">
        <TrophyIcon className="w-8 h-8 text-jing-accent" />
        <h2 className="text-2xl font-bold text-gray-900">Job Performance</h2>
      </div>

      <div className="flex justify-center mb-6">
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', duration: 0.8, delay: 0.2 }}
          className="relative"
        >
          <div className={`w-32 h-32 rounded-full bg-gradient-to-br ${getGradeColor(profitability.profitability_grade)} flex items-center justify-center shadow-2xl`}>
            <div className="text-center text-white">
              <p className="text-5xl font-bold">{profitability.profitability_grade}</p>
              <p className="text-xs opacity-90">Grade</p>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="flex items-center space-x-2 mb-2">
            <CurrencyDollarIcon className="w-5 h-5 text-green-600" />
            <p className="text-sm text-gray-600">Gross Profit</p>
          </div>
          <p className="text-2xl font-bold text-gray-900">${profitability.gross_profit.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="flex items-center space-x-2 mb-2">
            <ChartBarIcon className="w-5 h-5 text-blue-600" />
            <p className="text-sm text-gray-600">Net Margin</p>
          </div>
          <p className="text-2xl font-bold text-gray-900">{profitability.net_margin_percentage.toFixed(1)}%</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="flex items-center space-x-2 mb-2">
            <ClockIcon className="w-5 h-5 text-purple-600" />
            <p className="text-sm text-gray-600">Effective Rate</p>
          </div>
          <p className="text-2xl font-bold text-gray-900">${profitability.effective_hourly_rate.toFixed(2)}/h</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="flex items-center space-x-2 mb-2">
            <TrophyIcon className="w-5 h-5 text-jing-accent" />
            <p className="text-sm text-gray-600">Score</p>
          </div>
          <p className={`text-2xl font-bold ${getScoreColor(performance.overall_score)}`}>{performance.overall_score}/100</p>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Time Efficiency:</span>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${performance.time_efficiency === 'under' ? 'bg-green-100 text-green-800' : performance.time_efficiency === 'on' ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'}`}>
            {performance.time_efficiency.toUpperCase()}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Cost Efficiency:</span>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${performance.cost_efficiency === 'under' ? 'bg-green-100 text-green-800' : performance.cost_efficiency === 'on' ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'}`}>
            {performance.cost_efficiency.toUpperCase()}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Margin vs Target:</span>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${performance.margin_vs_target === 'above' ? 'bg-green-100 text-green-800' : performance.margin_vs_target === 'at' ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'}`}>
            {performance.margin_vs_target.toUpperCase()}
          </span>
        </div>
      </div>
    </motion.div>
  );
}
