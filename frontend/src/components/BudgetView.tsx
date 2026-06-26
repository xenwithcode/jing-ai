import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  DocumentTextIcon, 
  UserIcon, 
  CurrencyDollarIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import type { Budget } from '../types';
import BudgetPreview from './BudgetPreview';

interface BudgetViewProps {
  budget: Budget;
  onApprove: () => void;
  onEdit: () => void;
  onCompleteJob?: () => void;
}

export default function BudgetView({ budget, onApprove, onEdit, onCompleteJob }: BudgetViewProps) {
  const [showPreview, setShowPreview] = useState(false);

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center space-x-3 mb-2">
          <DocumentTextIcon className="w-8 h-8 text-jing-primary" />
          <h1 className="text-4xl font-bold text-gray-900">
            Professional Budget
          </h1>
        </div>
        <p className="text-gray-600">
          Budget #{budget.budget_metadata.budget_number} • Valid until{' '}
          {new Date(budget.budget_metadata.valid_until).toLocaleDateString()}
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Budget Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Client & Job Info */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <div className="flex items-center space-x-2 mb-4">
              <UserIcon className="w-6 h-6 text-jing-secondary" />
              <h2 className="text-2xl font-bold text-gray-900">
                {budget.job_description.summary}
              </h2>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <p className="text-sm text-gray-600 mb-1">Client</p>
                <p className="text-lg font-semibold text-gray-900">
                  {budget.client_info.name}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Duration</p>
                <p className="text-lg font-semibold text-gray-900">
                  {budget.job_description.estimated_duration}
                </p>
              </div>
            </div>

            <div className="mb-4">
              <p className="text-sm font-semibold text-gray-700 mb-2">
                What's Included:
              </p>
              <ul className="space-y-1">
                {budget.job_description.scope.map((item, idx) => (
                  <li key={idx} className="flex items-start space-x-2 text-gray-700">
                    <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {budget.job_description.exclusions.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-gray-700 mb-2">
                  Not Included:
                </p>
                <ul className="space-y-1">
                  {budget.job_description.exclusions.map((item, idx) => (
                    <li key={idx} className="text-gray-600 text-sm">
                      • {item}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>

          {/* Cost Breakdown */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card"
          >
            <div className="flex items-center space-x-2 mb-6">
              <CurrencyDollarIcon className="w-6 h-6 text-jing-primary" />
              <h2 className="text-2xl font-bold text-gray-900">
                Cost Breakdown
              </h2>
            </div>

            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Parts & Materials
              </h3>
              <div className="space-y-2">
                {budget.cost_breakdown.parts.map((part, idx) => (
                  <div key={idx} className="flex justify-between items-center py-2 border-b border-gray-100">
                    <div>
                      <p className="text-gray-900">{part.item}</p>
                      <p className="text-sm text-gray-600">
                        Qty: {part.quantity} × ${part.unit_price.toFixed(2)}
                      </p>
                    </div>
                    <p className="font-semibold text-gray-900">
                      ${part.total.toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
              <div className="flex justify-between items-center pt-3 text-gray-700">
                <span>Parts Subtotal:</span>
                <span className="font-semibold">
                  ${budget.cost_breakdown.parts_subtotal.toFixed(2)}
                </span>
              </div>
            </div>

            <div className="mb-6 pb-6 border-b border-gray-200">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Labor
              </h3>
              <div className="flex justify-between items-center py-2">
                <div>
                  <p className="text-gray-900">Professional Service</p>
                  <p className="text-sm text-gray-600">
                    {budget.cost_breakdown.labor.estimated_hours}h × $
                    {budget.cost_breakdown.labor.hourly_rate}/h
                  </p>
                </div>
                <p className="font-semibold text-gray-900">
                  ${budget.cost_breakdown.labor.total.toFixed(2)}
                </p>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex justify-between text-gray-700">
                <span>Subtotal:</span>
                <span>${budget.cost_breakdown.subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-gray-700">
                <span>Service Margin ({budget.cost_breakdown.margin_percentage}%):</span>
                <span>${budget.cost_breakdown.margin_amount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-gray-700">
                <span>Tax ({budget.cost_breakdown.tax_percentage}%):</span>
                <span>${budget.cost_breakdown.tax_amount.toFixed(2)}</span>
              </div>
            </div>

            <div className="bg-gradient-to-r from-jing-primary to-jing-secondary rounded-xl p-6 text-white">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm opacity-90 mb-1">Total Investment</p>
                  <p className="text-4xl font-bold">
                    {budget.client_friendly_total}
                  </p>
                </div>
                <div className="text-right">
                  <SparklesIcon className="w-12 h-12 opacity-50" />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Payment Terms & Warranty */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            <div className="card">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                💳 Payment Terms
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Deposit:</span>
                  <span className="font-semibold">
                    {budget.payment_terms.deposit_percentage}% ($
                    {budget.payment_terms.deposit_amount.toFixed(2)})
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Balance Due:</span>
                  <span className="font-semibold capitalize">
                    {budget.payment_terms.balance_due.replace('_', ' ')}
                  </span>
                </div>
                <div className="pt-2 border-t border-gray-100">
                  <p className="text-gray-600 mb-1">Accepted:</p>
                  <div className="flex flex-wrap gap-2">
                    {budget.payment_terms.accepted_methods.map((method, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-gray-100 rounded text-xs capitalize"
                      >
                        {method.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                🛡️ Warranty
              </h3>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-gray-600 mb-1">Parts:</p>
                  <p className="font-semibold">{budget.warranty.parts_warranty}</p>
                </div>
                <div>
                  <p className="text-gray-600 mb-1">Labor:</p>
                  <p className="font-semibold">{budget.warranty.labor_warranty}</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Right Column: Actions & Financial Health */}
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="card bg-gradient-to-br from-green-50 to-emerald-50 border-green-200"
          >
            <h3 className="text-lg font-bold text-green-900 mb-4">
              📊 Your Financial Health
            </h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-green-700 mb-1">Effective Hourly Rate:</p>
                <p className="text-2xl font-bold text-green-900">
                  ${budget.financial_health.effective_hourly_rate.toFixed(2)}/h
                </p>
              </div>
              <div>
                <p className="text-sm text-green-700 mb-1">Profit Margin:</p>
                <p className="text-2xl font-bold text-green-900">
                  {budget.financial_health.profit_margin_percentage}%
                </p>
              </div>
              <div>
                <p className="text-sm text-green-700 mb-1">Risk Level:</p>
                <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
                  budget.financial_health.risk_level === 'low'
                    ? 'bg-green-200 text-green-900'
                    : budget.financial_health.risk_level === 'medium'
                    ? 'bg-yellow-200 text-yellow-900'
                    : 'bg-red-200 text-red-900'
                }`}>
                  {budget.financial_health.risk_level.toUpperCase()}
                </span>
              </div>
              <div className="pt-3 border-t border-green-200">
                <p className="text-sm text-green-800 italic">
                  💡 {budget.financial_health.recommendation}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="card"
          >
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              🚀 Next Steps
            </h3>
            <div className="space-y-3">
              <button
                onClick={() => setShowPreview(true)}
                className="btn-secondary w-full flex items-center justify-center space-x-2"
              >
                <DocumentTextIcon className="w-5 h-5" />
                <span>Preview PDF</span>
              </button>
              
              <button
                onClick={onEdit}
                className="w-full py-3 px-6 border-2 border-gray-300 rounded-lg font-semibold text-gray-700 hover:border-jing-primary hover:text-jing-primary transition-all"
              >
                Edit Budget
              </button>
              
              <button
                onClick={onApprove}
                className="btn-primary w-full flex items-center justify-center space-x-2"
              >
                <span>Send to Client</span>
                <ArrowRightIcon className="w-5 h-5" />
              </button>

              {onCompleteJob && (
                <button
                  onClick={onCompleteJob}
                  className="w-full py-3 px-6 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-semibold hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg"
                >
                  Mark Job Complete & View Summary
                </button>
              )}
            </div>
          </motion.div>
        </div>
      </div>

      <AnimatePresence>
        {showPreview && (
          <BudgetPreview budget={budget} onClose={() => setShowPreview(false)} />
        )}
      </AnimatePresence>
    </div>
  );
}
