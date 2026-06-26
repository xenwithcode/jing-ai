import { motion } from 'framer-motion';
import { ArrowPathIcon, DocumentArrowDownIcon, ShareIcon } from '@heroicons/react/24/outline';
import CostBreakdownChart from './charts/CostBreakdownChart';
import BudgetVsActualChart from './charts/BudgetVsActualChart';
import ProfitabilityCard from './ProfitabilityCard';
import InsightsPanel from './InsightsPanel';
import type { FinancialSummary } from '../types';

interface FinancialSummaryViewProps {
  summary: FinancialSummary;
  onReset: () => void;
}

export default function FinancialSummaryView({ summary, onReset }: FinancialSummaryViewProps) {
  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Financial Summary</h1>
        <p className="text-gray-600">
          Job #{summary.job_info.job_id} • {summary.job_info.client_name} •{' '}
          {new Date(summary.job_info.date).toLocaleDateString()}
        </p>
      </motion.div>

      {summary.celebration_message && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-2xl p-6 mb-8"
        >
          <p className="text-lg text-green-900 font-semibold mb-2">🎉 {summary.celebration_message}</p>
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-gradient-to-r from-jing-primary to-jing-secondary rounded-2xl p-8 mb-8 text-white"
      >
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm opacity-90 mb-1">Net Profit</p>
            <p className="text-5xl font-bold">${summary.profitability.gross_profit.toFixed(2)}</p>
            <p className="text-sm opacity-90 mt-2">
              {summary.profitability.net_margin_percentage.toFixed(1)}% margin • $
              {summary.profitability.effective_hourly_rate.toFixed(2)}/hour
            </p>
          </div>
          <div className="text-right">
            <div className="inline-block bg-white/20 backdrop-blur-sm rounded-xl px-6 py-4">
              <p className="text-sm opacity-90 mb-1">Grade</p>
              <p className="text-4xl font-bold">{summary.profitability.profitability_grade}</p>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <CostBreakdownChart data={summary.chart_data.cost_breakdown} />
        <BudgetVsActualChart data={summary.chart_data.budget_vs_actual} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <ProfitabilityCard profitability={summary.profitability} performance={summary.performance_metrics} />
        <InsightsPanel insights={summary.insights} />
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="card mb-8">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Budget Comparison</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-sm text-gray-600 mb-1">Budgeted Total</p>
            <p className="text-2xl font-bold text-gray-900">${summary.comparison.budgeted_total.toFixed(2)}</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-sm text-gray-600 mb-1">Actual Total</p>
            <p className="text-2xl font-bold text-gray-900">${summary.comparison.actual_total.toFixed(2)}</p>
          </div>
          <div className={`rounded-xl p-4 ${summary.comparison.variance >= 0 ? 'bg-green-50' : 'bg-red-50'}`}>
            <p className="text-sm text-gray-600 mb-1">Variance</p>
            <p className={`text-2xl font-bold ${summary.comparison.variance >= 0 ? 'text-green-900' : 'text-red-900'}`}>
              {summary.comparison.variance >= 0 ? '+' : ''}${summary.comparison.variance.toFixed(2)}
            </p>
            <p className="text-xs text-gray-600 mt-1">({summary.comparison.variance_percentage.toFixed(1)}%)</p>
          </div>
        </div>
        {summary.comparison.variance_reason && (
          <p className="text-sm text-gray-600 mt-4 italic">💡 {summary.comparison.variance_reason}</p>
        )}
      </motion.div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}
        className="flex flex-col sm:flex-row gap-4"
      >
        <button className="btn-secondary flex-1 flex items-center justify-center space-x-2">
          <DocumentArrowDownIcon className="w-5 h-5" />
          <span>Download Report</span>
        </button>
        <button className="btn-secondary flex-1 flex items-center justify-center space-x-2">
          <ShareIcon className="w-5 h-5" />
          <span>Share Results</span>
        </button>
        <button onClick={onReset} className="btn-primary flex-1 flex items-center justify-center space-x-2">
          <ArrowPathIcon className="w-5 h-5" />
          <span>New Diagnosis</span>
        </button>
      </motion.div>
    </div>
  );
}
