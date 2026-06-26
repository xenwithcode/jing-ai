import { motion } from 'framer-motion';
import { SparklesIcon } from '@heroicons/react/24/outline';

export default function ProcessingView() {
  const agents = [
    { name: 'JING-EYE', status: 'Analyzing image...' },
    { name: 'JING-SCRIBE', status: 'Searching manuals...' },
    { name: 'JING-KIT', status: 'Preparing tool list...' },
    { name: 'JING-VOICE', status: 'Preparing response...' },
  ];

  return (
    <div className="max-w-2xl mx-auto px-4 py-20">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="card text-center"
      >
        {/* Animated icon */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-20 h-20 mx-auto mb-8"
        >
          <SparklesIcon className="w-full h-full text-jing-primary" />
        </motion.div>

        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          JING is Working
        </h2>
        <p className="text-gray-600 mb-8">
          Our AI agents are analyzing your problem...
        </p>

        {/* Agent status */}
        <div className="space-y-4">
          {agents.map((agent, index) => (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.2 }}
              className="flex items-center justify-between bg-gray-50 rounded-lg p-4"
            >
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-jing-primary rounded-full animate-pulse"></div>
                <span className="font-semibold text-gray-900">{agent.name}</span>
              </div>
              <span className="text-sm text-gray-600">{agent.status}</span>
            </motion.div>
          ))}
        </div>

        {/* Progress bar */}
        <div className="mt-8">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 10, ease: "easeInOut" }}
              className="bg-gradient-to-r from-jing-primary to-jing-secondary h-2 rounded-full"
            />
          </div>
        </div>
      </motion.div>
    </div>
  );
}
