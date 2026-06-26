import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  PlayIcon, PauseIcon, ForwardIcon, ArrowLeftIcon,
  CheckCircleIcon, ClockIcon, SparklesIcon, ArrowRightIcon, ChartBarIcon,
} from '@heroicons/react/24/outline';
import { DEMO_SCENARIOS, type DemoScenario, type DemoStep } from '../data/demoData';

type Phase = 'selecting' | 'playing' | 'complete';

const AGENT_ORDER = [
  'JING-MASTER',
  'JING-EYE',
  'JING-SCRIBE',
  'JING-KIT',
  'JING-REFEREE',
  'JING-STEWARD',
  'Client',
  'JING-VOICE',
  'JING-STEWARD',
];

function ProgressDots({ total, current }: { total: number; current: number }) {
  return (
    <div className="flex items-center gap-2">
      {Array.from({ length: total }).map((_, i) => (
        <div
          key={i}
          className={`h-2 rounded-full transition-all duration-500 ${
            i < current ? 'w-6 bg-jing-primary' : i === current ? 'w-6 bg-jing-accent animate-pulse' : 'w-2 bg-gray-700'
          }`}
        />
      ))}
    </div>
  );
}

function AgentTimeline({ steps, currentStep }: { steps: DemoStep[]; currentStep: number }) {
  const stepAgents = steps.map(s => s.agent);
  const allAgents = AGENT_ORDER.filter(a => stepAgents.includes(a) || a === 'Client');

  return (
    <div className="space-y-2">
      {allAgents.map((agent, idx) => {
        const stepIndex = steps.findIndex(s => s.agent === agent);
        const status = stepIndex < currentStep ? 'done' : stepIndex === currentStep ? 'active' : 'pending';
        const step = steps[stepIndex];
        if (!step) return null;

        return (
          <motion.div
            key={agent}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={`flex items-start space-x-3 p-3 rounded-xl transition-all duration-500 ${
              status === 'active' ? 'bg-white/10 border border-white/10 shadow-lg' :
              status === 'done' ? 'bg-white/5 opacity-80' : 'opacity-40'
            }`}
          >
            <div className="flex-shrink-0 mt-0.5">
              {status === 'done' ? (
                <CheckCircleIcon className="w-5 h-5 text-green-400" />
              ) : status === 'active' ? (
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="w-5 h-5 rounded-full bg-jing-accent flex items-center justify-center"
                >
                  <div className="w-2 h-2 bg-white rounded-full" />
                </motion.div>
              ) : (
                <ClockIcon className="w-5 h-5 text-gray-600" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{step.agentEmoji}</span>
                <span className={`font-semibold text-sm ${status === 'active' ? 'text-white' : 'text-gray-400'}`}>
                  {agent}
                </span>
              </div>
              <p className={`text-xs mt-1 ${status === 'active' ? 'text-gray-300' : 'text-gray-600'}`}>
                {step.description}
              </p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

function StepOutput({ step }: { step: DemoStep }) {
  const output = step.output;

  const renderContent = () => {
    switch (output.type) {
      case 'text':
        return (
          <div className="space-y-4">
            <p className="text-gray-300 leading-relaxed">{output.body}</p>
            {output.items && (
              <ul className="space-y-2">
                {output.items.map((item, i) => (
                  <li key={i} className="flex items-start space-x-2 text-sm text-gray-400">
                    <span className="text-jing-primary mt-0.5">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        );

      case 'json':
        return (
          <div className="space-y-3">
            {output.details && Object.entries(output.details).map(([key, val]) => (
              <div key={key} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                <div className="text-xs font-semibold text-jing-accent mb-1">{key}</div>
                <div className="text-sm text-gray-300">{val}</div>
              </div>
            ))}
          </div>
        );

      case 'manual':
        return (
          <div className="space-y-4">
            <div className="bg-gray-900 border border-gray-700 rounded-xl p-5 font-mono text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">
              {output.body}
            </div>
            {output.items && (
              <div className="space-y-2">
                <p className="text-xs font-semibold text-green-400 uppercase tracking-wider">Key Specs</p>
                {output.items.map((item, i) => (
                  <div key={i} className="flex items-start space-x-2 text-sm text-gray-400">
                    <span className="text-green-400 mt-0.5">📋</span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 'tools':
        return (
          <div className="space-y-4">
            <p className="text-sm text-gray-400">{output.body}</p>
            <div className="grid grid-cols-1 gap-2">
              {output.items?.map((item, i) => (
                <div key={i} className="bg-gray-800/50 rounded-lg px-4 py-3 border border-gray-700 text-sm text-gray-300">
                  {item}
                </div>
              ))}
            </div>
          </div>
        );

      case 'consensus':
        return (
          <div className="space-y-3">
            {output.details && Object.entries(output.details).map(([key, val]) => (
              <div
                key={key}
                className={`rounded-xl p-4 border ${
                  key === 'Consensus' || key.startsWith('Confidence')
                    ? 'bg-green-900/20 border-green-500/30'
                    : 'bg-amber-900/20 border-amber-500/30'
                }`}
              >
                <div className={`text-xs font-semibold mb-1 ${
                  key.startsWith('Consensus') || key.startsWith('Confidence')
                    ? 'text-green-400' : 'text-amber-400'
                }`}>{key}</div>
                <div className="text-sm text-gray-300">{val}</div>
              </div>
            ))}
          </div>
        );

      case 'budget':
        return (
          <div className="space-y-3">
            <p className="text-sm font-semibold text-jing-secondary">{output.title}</p>
            <div className="bg-gray-800/50 rounded-xl border border-gray-700 divide-y divide-gray-700">
              {output.details && Object.entries(output.details).map(([key, val]) => (
                <div
                  key={key}
                  className={`flex justify-between px-5 py-2.5 text-sm ${
                    ['Total', 'Deposit (50%)', 'Deposit (40%)'].includes(key)
                      ? 'font-bold text-white bg-jing-primary/10'
                      : ['Subtotal'].includes(key)
                      ? 'font-semibold text-gray-200 border-t border-gray-600'
                      : 'text-gray-400'
                  }`}
                >
                  <span>{key}</span>
                  <span className="font-mono">{val}</span>
                </div>
              ))}
            </div>
          </div>
        );

      case 'signature':
        return (
          <div className="space-y-4 text-center">
            <div className="text-6xl mb-4">✍️</div>
            <div className="bg-green-900/20 border border-green-500/30 rounded-2xl p-8">
              <div className="flex items-center justify-center space-x-2 mb-4">
                <CheckCircleIcon className="w-8 h-8 text-green-400" />
                <span className="text-xl font-bold text-green-400">Budget Approved</span>
              </div>
              <div className="space-y-2 text-sm text-gray-400">
                {output.details && Object.entries(output.details).map(([key, val]) => (
                  <div key={key} className="flex justify-between max-w-xs mx-auto">
                    <span className="text-gray-500">{key}:</span>
                    <span className="text-gray-300 font-medium">{val}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 'voice':
        return (
          <div className="space-y-4">
            <div className="bg-cyan-900/20 border border-cyan-500/30 rounded-2xl p-6">
              <div className="flex items-start space-x-3 mb-4">
                <span className="text-2xl">🎧</span>
                <p className="text-gray-300 leading-relaxed italic">
                  "{output.body}"
                </p>
              </div>
            </div>
          </div>
        );

      case 'charts':
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {output.details && Object.entries(output.details).map(([key, val]) => {
                const isPositive = val.includes('🟢') || val.includes('Excellent') || val.includes('$');
                return (
                  <div
                    key={key}
                    className="bg-gray-800/50 rounded-xl p-4 border border-gray-700"
                  >
                    <div className="text-xs text-gray-500 mb-1">{key}</div>
                    <div className={`text-sm font-semibold ${
                      val.includes('🟢') || val.includes('Excellent')
                        ? 'text-green-400'
                        : isPositive ? 'text-white' : 'text-gray-300'
                    }`}>{val}</div>
                  </div>
                );
              })}
            </div>
            {output.details?.['Recommendation'] && (
              <div className="bg-gradient-to-r from-jing-primary/10 to-jing-secondary/10 border border-jing-primary/20 rounded-xl p-4 mt-4">
                <div className="text-xs font-semibold text-jing-primary mb-1">💡 Recommendation</div>
                <div className="text-sm text-gray-300">{output.details['Recommendation']}</div>
              </div>
            )}
          </div>
        );

      default:
        return <p className="text-gray-400">{output.body}</p>;
    }
  };

  return (
    <motion.div
      key={step.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
    >
      <div className="flex items-center space-x-3 mb-6">
        <span className="text-3xl">{step.agentEmoji}</span>
        <div>
          <h3 className={`text-xl font-bold ${step.agentColor}`}>{step.agent}</h3>
          <p className="text-sm text-gray-500">{step.title}</p>
        </div>
      </div>
      {renderContent()}
    </motion.div>
  );
}

function ScenarioCard({
  scenario,
  onSelect,
  index,
}: {
  scenario: DemoScenario;
  onSelect: () => void;
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.15 }}
      whileHover={{ y: -4, scale: 1.01 }}
      onClick={onSelect}
      className="group cursor-pointer bg-gray-900/50 border border-gray-800 rounded-3xl overflow-hidden hover:border-jing-primary/50 transition-all duration-300"
    >
      <div className="h-48 overflow-hidden relative">
        <img
          src={scenario.problemImage}
          alt={scenario.title}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          onError={(e) => {
            const target = e.currentTarget;
            target.style.display = 'none';
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/50 to-transparent" />
        <div className={`absolute top-4 left-4 bg-gradient-to-r ${scenario.gradient} rounded-full px-4 py-1.5 text-sm font-bold shadow-lg`}>
          {scenario.icon} {scenario.title}
        </div>
      </div>
      <div className="p-6">
        <h3 className="text-xl font-bold mb-2">{scenario.subtitle}</h3>
        <p className="text-sm text-gray-400 mb-4 line-clamp-2">{scenario.problemDescription}</p>
        <div className="flex items-center space-x-2 text-jing-accent text-sm font-medium group-hover:text-white transition-colors">
          <span>Start Demo</span>
          <ArrowRightIcon className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </div>
      </div>
    </motion.div>
  );
}

export default function DemoPage() {
  const [phase, setPhase] = useState<Phase>('selecting');
  const [scenario, setScenario] = useState<DemoScenario | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const totalSteps = scenario?.steps.length || 0;
  const isComplete = currentStep >= totalSteps;

  const stepDurations = scenario?.steps.map(s => {
    switch (s.id) {
      case 'master-plan': return 2500;
      case 'scribe-manual': return 5000;
      case 'steward-budget': return 5500;
      case 'voice-response': return 5500;
      case 'steward-summary': return 4500;
      default: return 4000;
    }
  }) || [];

  const advanceStep = useCallback(() => {
    if (scenario && currentStep < scenario.steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      setPhase('complete');
    }
  }, [scenario, currentStep]);

  useEffect(() => {
    if (phase === 'playing' && !isPaused && !isComplete) {
      timerRef.current = setTimeout(advanceStep, stepDurations[currentStep] || 4000);
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [phase, isPaused, isComplete, currentStep, advanceStep, stepDurations]);

  const handleSelectScenario = (s: DemoScenario) => {
    setScenario(s);
    setCurrentStep(0);
    setPhase('playing');
    setIsPaused(false);
  };

  const handlePauseToggle = () => setIsPaused(!isPaused);

  const handleSkipToEnd = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setPhase('complete');
  };

  const handleReset = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setPhase('selecting');
    setScenario(null);
    setCurrentStep(0);
    setIsPaused(false);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {phase !== 'selecting' ? (
              <button onClick={handleReset} className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors">
                <ArrowLeftIcon className="w-5 h-5" />
                <span>Scenarios</span>
              </button>
            ) : (
              <Link to="/" className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors">
                <ArrowLeftIcon className="w-5 h-5" />
                <span>Home</span>
              </Link>
            )}
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-jing-primary to-jing-secondary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">匠</span>
            </div>
            <span className="font-bold">JING Demo</span>
          </div>
          <div className="flex items-center space-x-3">
            {phase !== 'selecting' && (
              <button
                onClick={handleSkipToEnd}
                className="flex items-center space-x-1 text-xs text-gray-500 hover:text-white transition-colors"
              >
                <ForwardIcon className="w-4 h-4" />
                <span>Skip</span>
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Phase: Selecting */}
        {phase === 'selecting' && (
          <div>
            <div className="text-center mb-12">
              <div className="inline-flex items-center space-x-2 bg-jing-primary/10 border border-jing-primary/20 rounded-full px-4 py-2 mb-6">
                <SparklesIcon className="w-5 h-5 text-jing-primary" />
                <span className="text-sm font-semibold text-jing-primary">Interactive Demo</span>
              </div>
              <h1 className="text-5xl font-bold mb-4">See JING in Action</h1>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                Choose a real-world scenario and watch as 8 AI agents collaborate to diagnose,
                budget, and deliver results — no API key required.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
              {DEMO_SCENARIOS.map((s, idx) => (
                <ScenarioCard key={s.id} scenario={s} onSelect={() => handleSelectScenario(s)} index={idx} />
              ))}
            </div>

            <div className="text-center mt-12">
              <p className="text-sm text-gray-500">
                Each demo walks through the complete JING workflow — from problem input to financial summary.
                All data is simulated for demonstration.
              </p>
            </div>
          </div>
        )}

        {/* Phase: Playing */}
        {phase === 'playing' && scenario && (
          <div>
            {/* Progress Bar */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <span className="text-lg">{scenario.icon}</span>
                  <span className="font-semibold text-sm text-gray-400">{scenario.title}</span>
                  <span className="text-xs text-gray-600">•</span>
                  <span className="text-sm text-gray-500">{scenario.subtitle}</span>
                </div>
                <span className="text-xs text-gray-500">
                  Step {Math.min(currentStep + 1, totalSteps)} of {totalSteps}
                </span>
              </div>
              <ProgressDots total={totalSteps} current={currentStep} />
            </div>

            <div className="grid md:grid-cols-12 gap-8">
              {/* Agent Timeline (left) */}
              <div className="md:col-span-4 lg:col-span-3">
                <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-5 sticky top-24">
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">Agent Activity</h4>
                  <AgentTimeline steps={scenario.steps} currentStep={currentStep} />
                </div>
              </div>

              {/* Step Output (right) */}
              <div className="md:col-span-8 lg:col-span-9">
                <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-8 min-h-[400px]">
                  <AnimatePresence mode="wait">
                    {scenario.steps[currentStep] && (
                      <StepOutput key={currentStep} step={scenario.steps[currentStep]} />
                    )}
                  </AnimatePresence>
                </div>

                {/* Controls */}
                <div className="flex items-center justify-between mt-6">
                  <button
                    onClick={handlePauseToggle}
                    className="flex items-center space-x-2 px-5 py-2.5 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors text-sm"
                  >
                    {isPaused ? (
                      <>
                        <PlayIcon className="w-4 h-4" />
                        <span>Resume</span>
                      </>
                    ) : (
                      <>
                        <PauseIcon className="w-4 h-4" />
                        <span>Pause</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={advanceStep}
                    className="flex items-center space-x-2 px-5 py-2.5 bg-jing-primary text-white rounded-xl hover:scale-105 transition-transform text-sm font-semibold"
                  >
                    <span>Next Step</span>
                    <ArrowRightIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Phase: Complete */}
        {phase === 'complete' && scenario && (
          <div className="max-w-3xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              <div className="text-7xl mb-6">🎉</div>
              <h1 className="text-5xl font-bold mb-4">Demo Complete</h1>
              <p className="text-xl text-gray-400 mb-2">
                You just witnessed the full JING workflow for a <strong className="text-white">{scenario.subtitle}</strong> scenario.
              </p>
              <p className="text-gray-500 mb-12">
                {scenario.icon} {scenario.title} • {scenario.steps.length} steps • 8 AI agents
              </p>

              <div className="grid md:grid-cols-3 gap-6 mb-12">
                <Link
                  to="/"
                  className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 hover:border-jing-primary/50 transition-colors"
                >
                  <div className="text-3xl mb-3">🏠</div>
                  <h3 className="font-bold mb-2">Back to Home</h3>
                  <p className="text-sm text-gray-500">Explore the full JING showcase</p>
                </Link>
                <Link
                  to="/architecture"
                  className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 hover:border-jing-primary/50 transition-colors"
                >
                  <div className="text-3xl mb-3">🏗️</div>
                  <h3 className="font-bold mb-2">Architecture</h3>
                  <p className="text-sm text-gray-500">See how the 8 agents connect</p>
                </Link>
                <Link
                  to="/benchmark"
                  className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 hover:border-jing-primary/50 transition-colors"
                >
                  <div className="text-3xl mb-3">📊</div>
                  <h3 className="font-bold mb-2">Benchmark</h3>
                  <p className="text-sm text-gray-500">Verify the efficiency metrics</p>
                </Link>
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <button
                  onClick={handleReset}
                  className="px-8 py-4 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors font-semibold"
                >
                  ← Try Another Scenario
                </button>
                <Link
                  to={`/dashboard?demo=true&trade=${scenario.id}`}
                  className="px-8 py-4 bg-jing-secondary text-white font-bold rounded-xl hover:scale-105 transition-transform shadow-lg shadow-jing-secondary/25 flex items-center gap-2"
                >
                  <ChartBarIcon className="w-5 h-5" />
                  View Artisan Dashboard
                </Link>
                <Link
                  to="/app?view=upload"
                  className="px-8 py-4 bg-jing-primary text-white font-bold rounded-xl hover:scale-105 transition-transform shadow-lg shadow-jing-primary/25"
                >
                  Launch JING App →
                </Link>
              </div>
            </motion.div>
          </div>
        )}
      </main>
    </div>
  );
}
