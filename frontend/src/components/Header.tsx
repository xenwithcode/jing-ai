import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ChartBarIcon } from '@heroicons/react/24/outline';

export default function Header() {
  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="bg-white shadow-md sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-jing-primary to-jing-secondary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">匠</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">JING</h1>
              <p className="text-xs text-gray-500">The Expert Spirit for the Modern Artisan</p>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center space-x-4">
            <Link
              to="/dashboard"
              className="hidden sm:flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl transition-colors text-sm font-medium"
            >
              <ChartBarIcon className="w-4 h-4" />
              Dashboard
            </Link>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">System Online</span>
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
}
