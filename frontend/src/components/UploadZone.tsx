import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { PhotoIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface UploadZoneProps {
  onFileSelected: (file: File, description: string) => void;
}

export default function UploadZone({ onFileSelected }: UploadZoneProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [description, setDescription] = useState('');

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      const file = acceptedFiles[0];
      setFile(file);
      setPreview(URL.createObjectURL(file));
    }
  });

  const handleSubmit = () => {
    if (file && description) {
      onFileSelected(file, description);
    }
  };

  const removeFile = () => {
    setFile(null);
    setPreview(null);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Upload Problem Photo
        </h2>
        <p className="text-gray-600 mb-8">
          Take a clear photo of the issue and describe what's happening
        </p>

        {/* Upload area */}
        {!file ? (
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
              isDragActive
                ? 'border-jing-primary bg-jing-primary/5'
                : 'border-gray-300 hover:border-jing-primary'
            }`}
          >
            <input {...getInputProps()} />
            <PhotoIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-lg text-gray-600 mb-2">
              {isDragActive ? 'Drop the image here' : 'Drag & drop an image here'}
            </p>
            <p className="text-sm text-gray-500">or click to browse (JPEG, PNG, WebP)</p>
          </div>
        ) : (
          <div className="relative">
            <img
              src={preview ?? ''}
              alt="Preview"
              className="w-full h-64 object-cover rounded-xl"
            />
            <button
              onClick={removeFile}
              className="absolute top-4 right-4 bg-white rounded-full p-2 shadow-lg hover:bg-gray-100"
            >
              <XMarkIcon className="w-6 h-6 text-gray-600" />
            </button>
          </div>
        )}

        {/* Description */}
        <div className="mt-8">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Describe the problem
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g., This Moen faucet has been dripping since last night..."
            className="input-field h-32 resize-none"
          />
        </div>

        {/* Submit button */}
        <button
          onClick={handleSubmit}
          disabled={!file || !description}
          className="btn-primary w-full mt-8 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Analyze with JING
        </button>
      </motion.div>
    </div>
  );
}
