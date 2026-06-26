import { motion } from 'framer-motion';
import { CheckCircleIcon, LightBulbIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import type { Insights } from '../types';

interface InsightsPanelProps {
  insights: Insights;
}

export default function InsightsPanel({ insights }: InsightsPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="card"
    >
      <div className="flex items-center space-x-3 mb-6">
        <LightBulbIcon className="w-8 h-8 text-jing-accent" />
        <h2 className="text-2xl font-bold text-gray-900">Insights & Recommendations</h2>
      </div>

      {insights.what_went_well.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-green-700 mb-3 flex items-center space-x-2">
            <CheckCircleIcon className="w-5 h-5" />
            <span>What Went Well</span>
          </h3>
          <ul className="space-y-2">
            {insights.what_went_well.map((item, idx) => (
              <motion.li key={idx} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 + idx * 0.1 }}
                className="flex items-start space-x-2"
              >
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                <span className="text-gray-700">{item}</span>
              </motion.li>
            ))}
          </ul>
        </div>
      )}

      {insights.what_to_improve.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-blue-700 mb-3 flex items-center space-x-2">
            <LightBulbIcon className="w-5 h-5" />
            <span>Areas for Improvement</span>
          </h3>
          <ul className="space-y-2">
            {insights.what_to_improve.map((item, idx) => (
              <motion.li key={idx} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.6 + idx * 0.1 }}
                className="flex items-start space-x-2"
              >
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                <span className="text-gray-700">{item}</span>
              </motion.li>
            ))}
          </ul>
        </div>
      )}

      {insights.pricing_recommendation && (
        <div className="mb-6 bg-gradient-to-r from-jing-primary/5 to-jing-secondary/5 rounded-xl p-4 border border-jing-primary/20">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">💰 Pricing Recommendation</h3>
          <p className="text-gray-700">{insights.pricing_recommendation}</p>
        </div>
      )}

      {insights.red_flags.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-red-700 mb-3 flex items-center space-x-2">
            <ExclamationTriangleIcon className="w-5 h-5" />
            <span>Red Flags</span>
          </h3>
          <ul className="space-y-2">
            {insights.red_flags.map((item, idx) => (
              <motion.li key={idx} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.7 + idx * 0.1 }}
                className="flex items-start space-x-2 bg-red-50 rounded-lg p-3"
              >
                <ExclamationTriangleIcon className="w-5 h-5 text-red-600 flex-shrink-0" />
                <span className="text-red-800">{item}</span>
              </motion.li>
            ))}
          </ul>
        </div>
      )}
    </motion.div>
  );
}
