import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  ShieldCheckIcon, 
  ClockIcon, 
  MapPinIcon,
  DocumentTextIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import SignatureCanvas from './SignatureCanvas';
import type { Budget } from '../types';

interface ClientSignViewProps {
  budget: Budget;
  onSign: (signatureData: {
    signature: string;
    timestamp: string;
    clientName: string;
    location?: { lat: number; lng: number };
  }) => void;
  onCancel: () => void;
}

export default function ClientSignView({
  budget,
  onSign,
  onCancel,
}: ClientSignViewProps) {
  const [isSignatureEmpty, setIsSignatureEmpty] = useState(true);
  const [clientName, setClientName] = useState(
    budget.client_info.name === 'New Client' ? '' : budget.client_info.name
  );
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [isGettingLocation, setIsGettingLocation] = useState(false);

  const handleGetLocation = () => {
    setIsGettingLocation(true);
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      setIsGettingLocation(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
        setIsGettingLocation(false);
      },
      (error) => {
        console.error('Geolocation error:', error);
        setIsGettingLocation(false);
      }
    );
  };

  const handleSign = () => {
    if (isSignatureEmpty || !clientName || !agreedToTerms) {
      alert('Please complete all fields and sign the document');
      return;
    }

    const canvas = document.querySelector('canvas');
    if (!canvas) return;

    const signature = canvas.toDataURL('image/png');
    const timestamp = new Date().toISOString();

    onSign({
      signature,
      timestamp,
      clientName,
      location: location || undefined,
    });
  };

  const isFormValid = !isSignatureEmpty && clientName && agreedToTerms;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-jing-primary to-jing-secondary rounded-2xl mb-4">
            <DocumentTextIcon className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Budget Approval
          </h1>
          <p className="text-gray-600">
            Please review and sign the budget below
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card mb-6"
        >
          <div className="flex justify-between items-start mb-6">
            <div>
              <p className="text-sm text-gray-600 mb-1">Budget Number</p>
              <p className="font-mono font-semibold text-gray-900">
                {budget.budget_metadata.budget_number}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600 mb-1">Valid Until</p>
              <p className="font-semibold text-gray-900">
                {new Date(budget.budget_metadata.valid_until).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div className="border-t border-gray-200 pt-6">
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              {budget.job_description.summary}
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Estimated duration: {budget.job_description.estimated_duration}
            </p>

            <div className="space-y-2 mb-6">
              <p className="text-sm font-semibold text-gray-700">What's included:</p>
              <ul className="space-y-1">
                {budget.job_description.scope.slice(0, 4).map((item, idx) => (
                  <li key={idx} className="flex items-start space-x-2 text-sm text-gray-700">
                    <CheckCircleIcon className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-gradient-to-r from-jing-primary to-jing-secondary rounded-xl p-6 text-white">
              <p className="text-sm opacity-90 mb-1">Total Investment</p>
              <p className="text-4xl font-bold">
                {budget.client_friendly_total}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card mb-6"
        >
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Your Full Name
          </label>
          <input
            type="text"
            value={clientName}
            onChange={(e) => setClientName(e.target.value)}
            placeholder="John Smith"
            className="input-field"
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card mb-6"
        >
          <label className="block text-sm font-semibold text-gray-700 mb-3">
            Your Signature
          </label>
          <SignatureCanvas onSignatureChange={setIsSignatureEmpty} />
          <p className="text-xs text-gray-500 mt-2">
            By signing, you approve this budget and authorize the work to proceed.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card mb-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <MapPinIcon className="w-6 h-6 text-jing-primary" />
              <div>
                <p className="font-semibold text-gray-900">Add Location</p>
                <p className="text-sm text-gray-600">
                  Optional: Adds security to the signature
                </p>
              </div>
            </div>
            {location ? (
              <div className="flex items-center space-x-2 text-green-600">
                <CheckCircleIcon className="w-5 h-5" />
                <span className="text-sm font-semibold">Added</span>
              </div>
            ) : (
              <button
                onClick={handleGetLocation}
                disabled={isGettingLocation}
                className="px-4 py-2 bg-jing-primary text-white rounded-lg text-sm font-semibold hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {isGettingLocation ? 'Getting...' : 'Add'}
              </button>
            )}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card mb-6"
        >
          <label className="flex items-start space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={agreedToTerms}
              onChange={(e) => setAgreedToTerms(e.target.checked)}
              className="mt-1 w-5 h-5 text-jing-primary rounded border-gray-300 focus:ring-jing-primary"
            />
            <span className="text-sm text-gray-700">
              I have read and agree to the budget terms, including the scope of work,
              pricing, payment terms, and warranty conditions. I understand that this
              signature constitutes a binding agreement.
            </span>
          </label>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="flex items-center justify-center space-x-6 text-xs text-gray-500 mb-6"
        >
          <div className="flex items-center space-x-1">
            <ShieldCheckIcon className="w-4 h-4" />
            <span>Secure & Encrypted</span>
          </div>
          <div className="flex items-center space-x-1">
            <ClockIcon className="w-4 h-4" />
            <span>Timestamped</span>
          </div>
          {location && (
            <div className="flex items-center space-x-1">
              <MapPinIcon className="w-4 h-4" />
              <span>Geolocated</span>
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="space-y-3"
        >
          <button
            onClick={handleSign}
            disabled={!isFormValid}
            className="btn-primary w-full text-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Approve & Sign Budget
          </button>
          <button
            onClick={onCancel}
            className="w-full py-3 text-gray-600 hover:text-gray-900 transition-colors"
          >
            Cancel
          </button>
        </motion.div>
      </div>
    </div>
  );
}
