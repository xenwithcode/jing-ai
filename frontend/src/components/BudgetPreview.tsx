import { motion } from 'framer-motion';
import {
  XMarkIcon,
  DocumentTextIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';
import type { Budget } from '../types';

interface BudgetPreviewProps {
  budget: Budget;
  onClose: () => void;
}

export default function BudgetPreview({ budget, onClose }: BudgetPreviewProps) {
  const cb = budget.cost_breakdown;
  const today = new Date().toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  });

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="sticky top-0 bg-white z-10 flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-jing-primary to-jing-secondary rounded-xl flex items-center justify-center">
              <DocumentTextIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">Budget Preview</h2>
              <p className="text-sm text-gray-500">{budget.budget_metadata.budget_number}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center hover:bg-gray-200 transition-colors"
          >
            <XMarkIcon className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        {/* Document content */}
        <div className="p-8">
          {/* Letterhead */}
          <div className="text-center mb-8 pb-8 border-b border-gray-200">
            <div className="w-16 h-16 bg-gradient-to-br from-jing-primary to-jing-secondary rounded-2xl flex items-center justify-center mx-auto mb-3">
              <span className="text-3xl font-bold text-white">匠</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900">JING Professional Services</h1>
            <p className="text-gray-500">Your Trusted Repair Specialists</p>
          </div>

          {/* Document title */}
          <div className="flex justify-between items-start mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-1">ESTIMATE</h2>
              <p className="text-gray-500">{budget.budget_metadata.job_title}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Date: {today}</p>
              <p className="text-sm text-gray-500">
                Valid until: {new Date(budget.budget_metadata.valid_until).toLocaleDateString()}
              </p>
            </div>
          </div>

          {/* Bill to */}
          <div className="mb-8 p-4 bg-gray-50 rounded-xl">
            <p className="text-sm font-semibold text-gray-500 uppercase mb-1">Bill To</p>
            <p className="text-lg font-bold text-gray-900">{budget.client_info.name}</p>
            {budget.client_info.address && (
              <p className="text-gray-600">{budget.client_info.address}</p>
            )}
          </div>

          {/* Job description */}
          <div className="mb-8">
            <p className="text-gray-700 mb-4">{budget.job_description.summary}</p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-semibold text-gray-500 uppercase mb-2">Included</p>
                <ul className="space-y-1">
                  {budget.job_description.scope.map((s, i) => (
                    <li key={i} className="flex items-start space-x-2 text-sm text-gray-700">
                      <CheckCircleIcon className="w-4 h-4 text-green-500 mt-0.5 shrink-0" />
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
              {budget.job_description.exclusions.length > 0 && (
                <div>
                  <p className="text-sm font-semibold text-gray-500 uppercase mb-2">Excluded</p>
                  <ul className="space-y-1">
                    {budget.job_description.exclusions.map((s, i) => (
                      <li key={i} className="text-sm text-gray-600">• {s}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Line items */}
          <table className="w-full mb-8">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left py-3 text-sm font-semibold text-gray-500 uppercase">Description</th>
                <th className="text-center py-3 text-sm font-semibold text-gray-500 uppercase">Qty</th>
                <th className="text-right py-3 text-sm font-semibold text-gray-500 uppercase">Rate</th>
                <th className="text-right py-3 text-sm font-semibold text-gray-500 uppercase">Amount</th>
              </tr>
            </thead>
            <tbody>
              {cb.parts.map((part, i) => (
                <tr key={i} className="border-b border-gray-100">
                  <td className="py-3 text-gray-900">{part.item}</td>
                  <td className="py-3 text-center text-gray-700">{part.quantity}</td>
                  <td className="py-3 text-right text-gray-700">${part.unit_price.toFixed(2)}</td>
                  <td className="py-3 text-right font-semibold text-gray-900">${part.total.toFixed(2)}</td>
                </tr>
              ))}
              <tr className="border-b border-gray-100">
                <td className="py-3 text-gray-900 font-medium">Labor — {cb.labor.estimated_hours}h × ${cb.labor.hourly_rate}/h</td>
                <td className="py-3 text-center">1</td>
                <td className="py-3 text-right">${cb.labor.hourly_rate.toFixed(2)}</td>
                <td className="py-3 text-right font-semibold">${cb.labor.total.toFixed(2)}</td>
              </tr>
            </tbody>
          </table>

          {/* Totals */}
          <div className="flex justify-end mb-8">
            <div className="w-72 space-y-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Parts Subtotal</span>
                <span>${cb.parts_subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>Labor</span>
                <span>${cb.labor.total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>Subtotal</span>
                <span>${cb.subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>Margin ({cb.margin_percentage}%)</span>
                <span className="text-green-600">${cb.margin_amount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>Tax ({cb.tax_percentage}%)</span>
                <span>${cb.tax_amount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-lg font-bold text-gray-900 border-t-2 border-gray-300 pt-2">
                <span>Total</span>
                <span className="text-jing-primary">{budget.client_friendly_total}</span>
              </div>
            </div>
          </div>

          {/* Payment terms & warranty */}
          <div className="grid grid-cols-2 gap-8 mb-8 p-6 bg-gray-50 rounded-xl text-sm">
            <div>
              <p className="font-bold text-gray-900 mb-2">Payment Terms</p>
              <p className="text-gray-600">
                {budget.payment_terms.deposit_percentage > 0
                  ? `${budget.payment_terms.deposit_percentage}% deposit required`
                  : 'No deposit required'}
              </p>
              <p className="text-gray-600 capitalize">
                Balance due: {budget.payment_terms.balance_due.replace(/_/g, ' ')}
              </p>
            </div>
            <div>
              <p className="font-bold text-gray-900 mb-2">Warranty</p>
              <p className="text-gray-600">Parts: {budget.warranty.parts_warranty}</p>
              <p className="text-gray-600">Labor: {budget.warranty.labor_warranty}</p>
            </div>
          </div>

          {/* Signature area */}
          <div className="border-t-2 border-gray-200 pt-8">
            <div className="grid grid-cols-2 gap-12">
              <div>
                <p className="text-sm font-semibold text-gray-500 uppercase mb-2">Client Signature</p>
                <div className="border-b border-gray-400 h-12 mb-2"></div>
                <p className="text-xs text-gray-400">By signing, you approve this estimate</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-500 uppercase mb-2">Authorized By</p>
                <div className="border-b border-gray-400 h-12 mb-2"></div>
                <p className="text-xs text-gray-400">JING Professional Services</p>
              </div>
            </div>
            <p className="text-center text-xs text-gray-400 mt-8">
              This is a computer-generated document. Signature is legally binding.
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
