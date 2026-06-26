import { motion } from 'framer-motion';
import { 
  CheckCircleIcon, 
  WrenchIcon, 
  DocumentTextIcon,
  SpeakerWaveIcon,
  ArrowPathIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';
import type { DiagnosisResult } from '../types';

interface ResultsViewProps {
  result: DiagnosisResult;
  onReset: () => void;
  onGenerateBudget?: () => void;
}

export default function ResultsView({ result, onReset, onGenerateBudget }: ResultsViewProps) {
  const { consolidated_response: response } = result;

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      {/* Success banner */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-green-50 border border-green-200 rounded-xl p-6 mb-8"
      >
        <div className="flex items-center space-x-3">
          <CheckCircleIcon className="w-8 h-8 text-green-600" />
          <div>
            <h2 className="text-2xl font-bold text-green-900">
              Diagnosis Complete
            </h2>
            <p className="text-green-700">
              JING analyzed your problem in {(result.execution_summary.total_duration_ms / 1000).toFixed(1)}s
            </p>
          </div>
        </div>
      </motion.div>

      {/* Main diagnosis */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card mb-6"
      >
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <DocumentTextIcon className="w-6 h-6 mr-2 text-jing-primary" />
          Diagnosis
        </h3>
        <p className="text-lg text-gray-700 mb-4">{response.diagnosis}</p>
        
        <div className="grid grid-cols-2 gap-4 mt-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Severity</p>
            <p className="text-lg font-semibold text-gray-900 capitalize">
              {response.severity}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Estimated Time</p>
            <p className="text-lg font-semibold text-gray-900">
              {response.estimated_time}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Part number */}
      {response.part_number && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card mb-6 bg-gradient-to-br from-jing-primary/5 to-jing-secondary/5"
        >
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            Part Number
          </h3>
          <p className="text-3xl font-mono font-bold text-jing-primary">
            {response.part_number}
          </p>
        </motion.div>
      )}

      {/* Tools */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card mb-6"
      >
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <WrenchIcon className="w-6 h-6 mr-2 text-jing-primary" />
          Tools Required
        </h3>
        <ul className="space-y-2">
          {response.key_tools.map((tool, index) => (
            <li key={index} className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-jing-primary rounded-full"></div>
              <span className="text-gray-700">{tool}</span>
            </li>
          ))}
        </ul>
      </motion.div>

      {/* Cost */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="card mb-6"
      >
        <h3 className="text-xl font-bold text-gray-900 mb-4">
          Estimated Cost
        </h3>
        <p className="text-3xl font-bold text-jing-primary">
          {response.estimated_cost}
        </p>
      </motion.div>

      {/* Safety warnings */}
      {response.safety_warnings.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="card mb-6 bg-red-50 border border-red-200"
        >
          <h3 className="text-xl font-bold text-red-900 mb-4">
            ⚠️ Safety Warnings
          </h3>
          <ul className="space-y-2">
            {response.safety_warnings.map((warning, index) => (
              <li key={index} className="text-red-800">
                • {warning}
              </li>
            ))}
          </ul>
        </motion.div>
      )}

      {/* Voice response */}
      {result.voice_response?.data?.spoken_response && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="card mb-6 bg-blue-50 border border-blue-200"
        >
          <h3 className="text-xl font-bold text-blue-900 mb-4 flex items-center">
            <SpeakerWaveIcon className="w-6 h-6 mr-2" />
            Voice Response
          </h3>
          <p className="text-lg text-blue-800 italic">
            "{result.voice_response.data.spoken_response}"
          </p>
          <p className="text-sm text-blue-600 mt-2">
            Duration: {result.voice_response.data.estimated_duration_seconds}s
          </p>
        </motion.div>
      )}

      {/* Generate Budget Button */}
      {onGenerateBudget && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.75 }}
          onClick={onGenerateBudget}
          className="btn-primary w-full flex items-center justify-center space-x-2 mb-4 py-4 text-lg"
        >
          <CurrencyDollarIcon className="w-6 h-6" />
          <span>Generate Professional Budget</span>
        </motion.button>
      )}

      {/* Action buttons */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.85 }}
      >
        <button
          onClick={onReset}
          className="btn-secondary w-full flex items-center justify-center space-x-2"
        >
          <ArrowPathIcon className="w-5 h-5" />
          <span>New Diagnosis</span>
        </button>
      </motion.div>
    </div>
  );
}
