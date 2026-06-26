import { useEffect } from 'react';
import { motion } from 'framer-motion';
import confetti from 'canvas-confetti';
import { 
  CheckCircleIcon, 
  DocumentCheckIcon,
  ClockIcon,
  MapPinIcon,
  ShareIcon
} from '@heroicons/react/24/outline';

interface SignatureConfirmationProps {
  clientName: string;
  budgetNumber: string;
  timestamp: string;
  location?: { lat: number; lng: number };
  onDone: () => void;
}

export default function SignatureConfirmation({
  clientName,
  budgetNumber,
  timestamp,
  location,
  onDone,
}: SignatureConfirmationProps) {
  useEffect(() => {
    const duration = 3000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 100 };

    const randomInRange = (min: number, max: number) =>
      Math.random() * (max - min) + min;

    const interval = setInterval(() => {
      const timeLeft = animationEnd - Date.now();

      if (timeLeft <= 0) {
        return clearInterval(interval);
      }

      const particleCount = 50 * (timeLeft / duration);

      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.1, 0.3), y: 0 },
        colors: ['#DC2626', '#1E40AF', '#F59E0B'],
      });
      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.7, 0.9), y: 0 },
        colors: ['#DC2626', '#1E40AF', '#F59E0B'],
      });
    }, 250);

    return () => clearInterval(interval);
  }, []);

  const formattedDate = new Date(timestamp).toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 py-12 px-4 flex items-center justify-center">
      <div className="max-w-md w-full">
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', duration: 0.8 }}
          className="text-center mb-8"
        >
          <div className="relative inline-block">
            <motion.div
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.5, 0, 0.5],
              }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute inset-0 bg-green-400 rounded-full blur-xl"
            />
            <div className="relative w-24 h-24 bg-gradient-to-br from-green-400 to-emerald-600 rounded-full flex items-center justify-center shadow-2xl">
              <CheckCircleIcon className="w-16 h-16 text-white" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Budget Approved!
          </h1>
          <p className="text-lg text-gray-700">
            Thank you, <span className="font-semibold">{clientName}</span>
          </p>
          <p className="text-gray-600 mt-2">
            Your signature has been securely recorded
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-2xl shadow-xl p-6 mb-6"
        >
          <div className="flex items-center space-x-3 mb-4">
            <DocumentCheckIcon className="w-6 h-6 text-jing-primary" />
            <h2 className="text-lg font-bold text-gray-900">
              Document Details
            </h2>
          </div>

          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-sm text-gray-600">Budget Number</span>
              <span className="font-mono font-semibold text-gray-900">
                {budgetNumber}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-sm text-gray-600 flex items-center space-x-2">
                <ClockIcon className="w-4 h-4" />
                <span>Signed At</span>
              </span>
              <span className="text-sm font-semibold text-gray-900">
                {formattedDate}
              </span>
            </div>
            {location && (
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-600 flex items-center space-x-2">
                  <MapPinIcon className="w-4 h-4" />
                  <span>Location</span>
                </span>
                <span className="text-sm font-semibold text-gray-900">
                  {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
                </span>
              </div>
            )}
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-gray-600">Status</span>
              <span className="inline-flex items-center space-x-1 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                <CheckCircleIcon className="w-4 h-4" />
                <span>SIGNED</span>
              </span>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="bg-gradient-to-r from-jing-secondary/10 to-jing-primary/10 border border-jing-secondary/20 rounded-xl p-4 mb-6"
        >
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-jing-secondary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">匠</span>
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-900">
                Secured by JING
              </p>
              <p className="text-xs text-gray-600">
                Your signature is encrypted and tamper-proof
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="bg-white rounded-2xl shadow-xl p-6 mb-6"
        >
          <h3 className="font-bold text-gray-900 mb-3">What happens next?</h3>
          <ol className="space-y-3">
            <li className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-jing-primary text-white rounded-full flex items-center justify-center text-xs font-bold">
                1
              </div>
              <p className="text-sm text-gray-700">
                The artisan has been notified and will review your signed budget
              </p>
            </li>
            <li className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-jing-primary text-white rounded-full flex items-center justify-center text-xs font-bold">
                2
              </div>
              <p className="text-sm text-gray-700">
                You'll receive a copy of the signed document by email
              </p>
            </li>
            <li className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-jing-primary text-white rounded-full flex items-center justify-center text-xs font-bold">
                3
              </div>
              <p className="text-sm text-gray-700">
                The artisan will contact you to schedule the work
              </p>
            </li>
          </ol>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.1 }}
          className="space-y-3"
        >
          <button className="btn-secondary w-full flex items-center justify-center space-x-2">
            <ShareIcon className="w-5 h-5" />
            <span>Share Confirmation</span>
          </button>
          <button
            onClick={onDone}
            className="btn-primary w-full"
          >
            Done
          </button>
        </motion.div>
      </div>
    </div>
  );
}
