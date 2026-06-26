import { motion } from 'framer-motion';
import { 
  WrenchIcon, 
  CameraIcon, 
  MicrophoneIcon, 
  SparklesIcon,
  DocumentTextIcon,
  CurrencyDollarIcon,
  CheckCircleIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

interface HeroProps {
  onStart: () => void;
}

export default function Hero({ onStart }: HeroProps) {
  return (
    <div className="relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-jing-primary/5 via-transparent to-jing-secondary/5"></div>
      
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(30)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-jing-accent rounded-full opacity-20"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.2, 0.5, 0.2],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center space-x-2 bg-gradient-to-r from-jing-secondary/10 to-jing-primary/10 border border-jing-secondary/20 rounded-full px-4 py-2 mb-8"
          >
            <SparklesIcon className="w-5 h-5 text-jing-secondary" />
            <span className="text-sm font-semibold text-jing-secondary">
              Powered by Qwen Cloud
            </span>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-6"
          >
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-4 leading-tight">
              The artisan's hands
              <span className="block text-jing-primary">shape the world.</span>
            </h1>
            <div className="flex items-center justify-center space-x-4 my-6">
              <div className="h-px w-16 bg-gradient-to-r from-transparent to-jing-primary"></div>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              >
                <span className="text-4xl">匠</span>
              </motion.div>
              <div className="h-px w-16 bg-gradient-to-l from-transparent to-jing-primary"></div>
            </div>
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
              <span className="text-jing-secondary">JING</span> shapes
              <span className="block">the artisan's day.</span>
            </h2>
          </motion.div>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-xl text-gray-600 mb-4 max-w-3xl mx-auto leading-relaxed"
          >
            All the power of <span className="font-semibold text-jing-secondary">Qwen Cloud</span> 
            {' '}at the service of skilled technicians through JING.
          </motion.p>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="text-lg text-gray-500 mb-12 max-w-2xl mx-auto"
          >
            A team of AI agents that diagnoses problems, generates professional 
            budgets, manages signatures, and tracks your financial performance.
          </motion.p>

          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onStart}
            className="btn-primary text-lg px-10 py-5 shadow-2xl mb-16"
          >
            <span className="flex items-center space-x-2">
              <span>Start Diagnosis</span>
              <WrenchIcon className="w-6 h-6" />
            </span>
          </motion.button>

          {/* ═══════════════════════════════════════════════════════════════ */}
          {/* COMPLETE WORKFLOW SHOWCASE */}
          {/* ═══════════════════════════════════════════════════════════════ */}
          
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="max-w-6xl mx-auto mb-20"
          >
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-8">
              The Complete JING Workflow
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 }}
                className="relative"
              >
                <div className="card hover:shadow-2xl transition-all h-full">
                  <div className="absolute -top-3 -left-3 w-10 h-10 bg-jing-primary text-white rounded-full flex items-center justify-center font-bold text-lg shadow-lg">
                    1
                  </div>
                  <CameraIcon className="w-12 h-12 text-jing-primary mx-auto mb-3" />
                  <h4 className="font-bold text-gray-900 mb-2">Visual Diagnosis</h4>
                  <p className="text-sm text-gray-600">
                    JING-EYE analyzes your photo and identifies the exact problem
                  </p>
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-500 font-semibold">AGENT: JING-EYE</p>
                  </div>
                </div>
                <ArrowRightIcon className="hidden md:block absolute -right-4 top-1/2 -translate-y-1/2 w-8 h-8 text-jing-primary z-10" />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.0 }}
                className="relative"
              >
                <div className="card hover:shadow-2xl transition-all h-full bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                  <div className="absolute -top-3 -left-3 w-10 h-10 bg-jing-accent text-white rounded-full flex items-center justify-center font-bold text-lg shadow-lg">
                    2
                  </div>
                  <CurrencyDollarIcon className="w-12 h-12 text-jing-accent mx-auto mb-3" />
                  <h4 className="font-bold text-gray-900 mb-2">Professional Budget</h4>
                  <p className="text-sm text-gray-600">
                    JING-STEWARD generates fair pricing with transparent breakdown
                  </p>
                  <div className="mt-3 pt-3 border-t border-green-200">
                    <p className="text-xs text-green-700 font-semibold">✨ NEW: JING-STEWARD</p>
                  </div>
                </div>
                <ArrowRightIcon className="hidden md:block absolute -right-4 top-1/2 -translate-y-1/2 w-8 h-8 text-jing-primary z-10" />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.1 }}
                className="relative"
              >
                <div className="card hover:shadow-2xl transition-all h-full">
                  <div className="absolute -top-3 -left-3 w-10 h-10 bg-jing-secondary text-white rounded-full flex items-center justify-center font-bold text-lg shadow-lg">
                    3
                  </div>
                  <DocumentTextIcon className="w-12 h-12 text-jing-secondary mx-auto mb-3" />
                  <h4 className="font-bold text-gray-900 mb-2">Digital Signature</h4>
                  <p className="text-sm text-gray-600">
                    Client signs securely from their phone with timestamp & location
                  </p>
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-500 font-semibold">SECURE & LEGAL</p>
                  </div>
                </div>
                <ArrowRightIcon className="hidden md:block absolute -right-4 top-1/2 -translate-y-1/2 w-8 h-8 text-jing-primary z-10" />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2 }}
                className="relative"
              >
                <div className="card hover:shadow-2xl transition-all h-full bg-gradient-to-br from-jing-primary/5 to-jing-secondary/5 border-jing-primary/20">
                  <div className="absolute -top-3 -left-3 w-10 h-10 bg-gradient-to-br from-jing-primary to-jing-secondary text-white rounded-full flex items-center justify-center font-bold text-lg shadow-lg">
                    4
                  </div>
                  <CheckCircleIcon className="w-12 h-12 text-jing-primary mx-auto mb-3" />
                  <h4 className="font-bold text-gray-900 mb-2">Financial Summary</h4>
                  <p className="text-sm text-gray-600">
                    Complete profitability analysis with charts and insights
                  </p>
                  <div className="mt-3 pt-3 border-t border-jing-primary/20">
                    <p className="text-xs text-jing-primary font-semibold">💰 TRACK EVERY DOLLAR</p>
                  </div>
                </div>
              </motion.div>
            </div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1.3 }}
              className="bg-gradient-to-r from-jing-primary to-jing-secondary rounded-2xl p-8 text-white shadow-2xl"
            >
              <div className="flex flex-col md:flex-row items-center justify-between space-y-6 md:space-y-0">
                <div className="text-center md:text-left">
                  <h3 className="text-2xl font-bold mb-2">
                    💰 Financial Clarity for Every Job
                  </h3>
                  <p className="text-lg opacity-90">
                    Know exactly what you earn. Track margins. Build a thriving business.
                  </p>
                </div>
                <div className="grid grid-cols-3 gap-6">
                  <div className="text-center">
                    <p className="text-3xl font-bold">78%</p>
                    <p className="text-sm opacity-90">Avg. Margin</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold">$150/h</p>
                    <p className="text-sm opacity-90">Effective Rate</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold">Grade A</p>
                    <p className="text-sm opacity-90">Performance</p>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-16">
            {[
              {
                icon: CameraIcon,
                title: 'Visual Diagnosis',
                description: 'JING-EYE analyzes your photo with Qwen-VL-Max',
                agent: 'JING-EYE',
                color: 'jing-primary',
                highlight: false,
              },
              {
                icon: CurrencyDollarIcon,
                title: 'Financial Guardian',
                description: 'JING-STEWARD manages budgets & tracks profit',
                agent: 'JING-STEWARD',
                color: 'jing-accent',
                highlight: true,
              },
              {
                icon: WrenchIcon,
                title: 'Precision Tools',
                description: 'JING-KIT lists exact tools and OEM part numbers',
                agent: 'JING-KIT',
                color: 'jing-secondary',
                highlight: false,
              },
              {
                icon: MicrophoneIcon,
                title: 'Hands-Free Mode',
                description: 'JING-VOICE speaks responses while you work',
                agent: 'JING-VOICE',
                color: 'jing-primary',
                highlight: false,
              },
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.4 + index * 0.1 }}
                className={`card hover:shadow-2xl transition-all ${
                  feature.highlight ? 'ring-2 ring-jing-accent ring-offset-2' : ''
                }`}
              >
                <div className="relative">
                  <feature.icon className="w-12 h-12 text-gray-700 mx-auto mb-4" />
                  <div className="absolute -top-2 -right-2 bg-gray-800 text-white text-xs font-bold px-2 py-1 rounded-full">
                    {feature.agent}
                  </div>
                  {feature.highlight && (
                    <div className="absolute -top-2 -left-2 bg-jing-accent text-white text-xs font-bold px-2 py-1 rounded-full animate-pulse">
                      NEW
                    </div>
                  )}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.8 }}
            className="mt-20 text-center"
          >
            <p className="text-lg text-gray-500 italic">
              "The artisan's hands shape the world. JING shapes the artisan's day."
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
