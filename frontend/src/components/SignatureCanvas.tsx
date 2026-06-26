import { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowUturnLeftIcon } from '@heroicons/react/24/outline';

interface SignatureCanvasProps {
  onSignatureChange: (isEmpty: boolean) => void;
  width?: number;
  height?: number;
}

export default function SignatureCanvas({
  onSignatureChange,
  width = 600,
  height = 200,
}: SignatureCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasDrawn, setHasDrawn] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = 3;
    ctx.strokeStyle = '#1F2937';

    ctx.beginPath();
    ctx.moveTo(40, height - 50);
    ctx.lineTo(width - 40, height - 50);
    ctx.strokeStyle = '#E5E7EB';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = '#9CA3AF';
    ctx.font = '16px Inter';
    ctx.fillText('✕', 20, height - 45);

    ctx.strokeStyle = '#1F2937';
    ctx.lineWidth = 3;
  }, [width, height]);

  const getCoordinates = (
    e: React.MouseEvent | React.TouchEvent
  ): { x: number; y: number } | null => {
    const canvas = canvasRef.current;
    if (!canvas) return null;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    if ('touches' in e) {
      return {
        x: (e.touches[0].clientX - rect.left) * scaleX,
        y: (e.touches[0].clientY - rect.top) * scaleY,
      };
    }

    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  };

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!ctx || !canvas) return;

    const coords = getCoordinates(e);
    if (!coords) return;

    ctx.beginPath();
    ctx.moveTo(coords.x, coords.y);
    setIsDrawing(true);
    setHasDrawn(true);
    onSignatureChange(false);
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing) return;

    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!ctx) return;

    const coords = getCoordinates(e);
    if (!coords) return;

    ctx.lineTo(coords.x, coords.y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!ctx || !canvas) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.beginPath();
    ctx.moveTo(40, height - 50);
    ctx.lineTo(width - 40, height - 50);
    ctx.strokeStyle = '#E5E7EB';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = '#9CA3AF';
    ctx.font = '16px Inter';
    ctx.fillText('✕', 20, height - 45);

    ctx.strokeStyle = '#1F2937';
    ctx.lineWidth = 3;

    setHasDrawn(false);
    onSignatureChange(true);
  };

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="w-full border-2 border-gray-300 rounded-xl bg-white cursor-crosshair touch-none"
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
        onTouchStart={startDrawing}
        onTouchMove={draw}
        onTouchEnd={stopDrawing}
      />

      {hasDrawn && (
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          onClick={clearCanvas}
          className="absolute top-3 right-3 p-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
          title="Clear signature"
        >
          <ArrowUturnLeftIcon className="w-5 h-5 text-gray-600" />
        </motion.button>
      )}

      {!hasDrawn && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <p className="text-gray-400 text-sm italic">
            Sign here with your finger or mouse
          </p>
        </div>
      )}
    </div>
  );
}
