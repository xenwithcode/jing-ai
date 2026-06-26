import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CheckCircleIcon, XMarkIcon, SparklesIcon } from '@heroicons/react/24/outline';

interface DigitalSignatureProps {
  clientName: string;
  budgetTotal: string;
  budgetNumber: string;
  onSign: (signatureDataUrl: string) => void;
  onDecline: () => void;
  onBack: () => void;
}

export default function DigitalSignature({
  clientName,
  budgetTotal,
  budgetNumber,
  onSign,
  onDecline,
  onBack,
}: DigitalSignatureProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasSignature, setHasSignature] = useState(false);
  const [isSigned, setIsSigned] = useState(false);
  const [confirmed, setConfirmed] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.strokeStyle = '#1f2937';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
  }, []);

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    setIsDrawing(true);
    const rect = canvas.getBoundingClientRect();
    const x = 'touches' in e ? e.touches[0].clientX - rect.left : e.clientX - rect.left;
    const y = 'touches' in e ? e.touches[0].clientY - rect.top : e.clientY - rect.top;
    ctx.beginPath();
    ctx.moveTo(x, y);
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const rect = canvas.getBoundingClientRect();
    const x = 'touches' in e ? e.touches[0].clientX - rect.left : e.clientX - rect.left;
    const y = 'touches' in e ? e.touches[0].clientY - rect.top : e.clientY - rect.top;
    ctx.lineTo(x, y);
    ctx.stroke();
    setHasSignature(true);
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const clearSignature = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    setHasSignature(false);
  };

  const handleSign = () => {
    const canvas = canvasRef.current;
    if (!canvas || !hasSignature) return;
    const dataUrl = canvas.toDataURL('image/png');
    setIsSigned(true);
    setTimeout(() => {
      setConfirmed(true);
      onSign(dataUrl);
    }, 1500);
  };

  if (confirmed) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 200 }}
        >
          <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircleIcon className="w-14 h-14 text-green-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Signed & Approved!</h2>
          <p className="text-gray-600">
            Budget {budgetNumber} for <strong>{clientName}</strong> has been signed.
          </p>
          <p className="text-2xl font-bold text-jing-primary mt-4">{budgetTotal}</p>
          <p className="text-sm text-gray-500 mt-2">Signed with digital timestamp</p>
        </motion.div>
      </div>
    );
  }

  if (isSigned) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-16 h-16 mx-auto mb-6"
          >
            <SparklesIcon className="w-full h-full text-jing-primary" />
          </motion.div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Processing Signature...</h2>
          <p className="text-gray-600">Saving your signed document</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        {/* Budget info */}
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Sign Budget</h2>
          <p className="text-gray-600">{budgetNumber}</p>
        </div>

        <div className="bg-gray-50 rounded-xl p-4 mb-6 flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-600">Client</p>
            <p className="font-semibold text-gray-900">{clientName}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Total</p>
            <p className="font-semibold text-jing-primary text-xl">{budgetTotal}</p>
          </div>
        </div>

        {/* Signature pad */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sign here with your finger or mouse
          </label>
          <div className="relative">
            <canvas
              ref={canvasRef}
              width={500}
              height={200}
              className="w-full h-48 border-2 border-dashed border-gray-300 rounded-xl cursor-crosshair bg-white"
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseLeave={stopDrawing}
              onTouchStart={startDrawing}
              onTouchMove={draw}
              onTouchEnd={stopDrawing}
            />
            {!hasSignature && (
              <p className="absolute bottom-4 left-1/2 -translate-x-1/2 text-sm text-gray-400 pointer-events-none">
                Draw your signature above
              </p>
            )}
          </div>
          {hasSignature && (
            <button
              onClick={clearSignature}
              className="text-sm text-red-600 hover:text-red-800 mt-2 flex items-center gap-1"
            >
              <XMarkIcon className="w-4 h-4" />
              Clear signature
            </button>
          )}
        </div>

        {/* Legal text */}
        <p className="text-xs text-gray-500 mb-6 leading-relaxed">
          By signing above, you authorize the work described in budget {budgetNumber}
          for a total of {budgetTotal}. You agree to the payment terms and warranty
          conditions outlined in the budget document.
        </p>

        {/* Actions */}
        <div className="space-y-3">
          <button
            onClick={handleSign}
            disabled={!hasSignature}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="flex items-center justify-center gap-2">
              <CheckCircleIcon className="w-5 h-5" />
              Accept & Sign
            </span>
          </button>
          <button
            onClick={onDecline}
            className="btn-secondary w-full"
          >
            Decline
          </button>
          <button
            onClick={onBack}
            className="w-full text-sm text-gray-500 hover:text-gray-700"
          >
            Back to budget
          </button>
        </div>
      </motion.div>
    </div>
  );
}
