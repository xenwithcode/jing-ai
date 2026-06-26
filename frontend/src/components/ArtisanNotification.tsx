import { motion, AnimatePresence } from 'framer-motion';
import { 
  BellIcon, 
  CheckCircleIcon, 
  DocumentTextIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline';

interface ArtisanNotificationProps {
  show: boolean;
  clientName: string;
  budgetNumber: string;
  timestamp: string;
  onClose: () => void;
}

export default function ArtisanNotification({
  show,
  clientName,
  budgetNumber,
  timestamp,
  onClose,
}: ArtisanNotificationProps) {
  const formattedTime = new Date(timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0, y: -100, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -100, scale: 0.9 }}
          transition={{ type: 'spring', duration: 0.6 }}
          className="fixed top-4 right-4 z-50 max-w-sm w-full"
        >
          <div className="bg-white rounded-2xl shadow-2xl border-2 border-green-200 overflow-hidden">
            <div className="bg-gradient-to-r from-green-400 to-emerald-500 p-3 flex items-center space-x-2">
              <CheckCircleIcon className="w-5 h-5 text-white" />
              <span className="text-white font-semibold text-sm">
                New Signature Received
              </span>
            </div>

            <div className="p-4">
              <div className="flex items-start space-x-3">
                <div className="w-12 h-12 bg-gradient-to-br from-jing-primary to-jing-secondary rounded-xl flex items-center justify-center flex-shrink-0">
                  <DocumentTextIcon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <p className="font-bold text-gray-900 mb-1">
                    {clientName} signed the budget!
                  </p>
                  <p className="text-sm text-gray-600 mb-2">
                    Budget #{budgetNumber}
                  </p>
                  <div className="flex items-center space-x-3 text-xs text-gray-500">
                    <span className="flex items-center space-x-1">
                      <BellIcon className="w-3 h-3" />
                      <span>{formattedTime}</span>
                    </span>
                    <span>•</span>
                    <span className="text-green-600 font-semibold">
                      Ready to proceed
                    </span>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <XMarkIcon className="w-5 h-5 text-gray-400" />
                </button>
              </div>

              <button
                onClick={onClose}
                className="mt-4 w-full py-2 bg-jing-primary text-white rounded-lg text-sm font-semibold hover:bg-red-700 transition-colors"
              >
                View Signed Document
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
