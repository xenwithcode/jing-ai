import React, { useEffect, useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useSearchParams } from 'react-router-dom';
import {
  BriefcaseIcon, CurrencyDollarIcon, ChartBarIcon,
  UserGroupIcon, ArrowLeftIcon, SparklesIcon,
  ClockIcon, CheckCircleIcon, ExclamationTriangleIcon,
  ArrowTrendingUpIcon, LightBulbIcon, ChatBubbleLeftRightIcon,
  PaperAirplaneIcon, ShieldCheckIcon,
  BuildingStorefrontIcon, ArrowPathIcon,
} from '@heroicons/react/24/outline';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts';
import { getArtisanJobs, getStewardSuggestion, seedDemoData, askJing } from '../services/api';
import type { DashboardStats, ArtisanJob, StewardSuggestion, StewardSuggestionItem, ChatMessage } from '../types';

const TRADES = [
  { value: '', label: 'All Trades', icon: '🔧' },
  { value: 'plumber', label: 'Plumber', icon: '🔧' },
  { value: 'electrician', label: 'Electrician', icon: '⚡' },
  { value: 'hvac', label: 'HVAC', icon: '❄️' },
];

const STATUS_COLORS = {
  completed: '#22C55E',
  'in-progress': '#3B82F6',
  pending: '#F59E0B',
};

const STATUS_BG = {
  completed: 'bg-green-900/30 text-green-400',
  'in-progress': 'bg-blue-900/30 text-blue-400',
  pending: 'bg-amber-900/30 text-amber-400',
};

const GRADE_COLORS: Record<string, string> = {
  A: 'bg-green-900/30 text-green-400',
  B: 'bg-blue-900/30 text-blue-400',
  C: 'bg-yellow-900/30 text-yellow-400',
  D: 'bg-red-900/30 text-red-400',
  F: 'bg-red-900/50 text-red-300',
};

function StatsCard({ icon: Icon, label, value, sub, color }: {
  icon: any; label: string; value: string; sub?: string; color: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gray-900/50 border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition-all"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-400 font-medium">{label}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
          {sub && <p className="text-xs text-gray-500 mt-0.5">{sub}</p>}
        </div>
        <div className={`p-3 rounded-xl ${color}`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
      </div>
    </motion.div>
  );
}

function StatusPieChart({ data: dist }: { data: DashboardStats['status_distribution'] }) {
  const chartData = [
    { name: 'Completed', value: dist.completed, color: STATUS_COLORS.completed },
    { name: 'In Progress', value: dist['in-progress'], color: STATUS_COLORS['in-progress'] },
    { name: 'Pending', value: dist.pending, color: STATUS_COLORS.pending },
  ].filter(d => d.value > 0);

  if (chartData.length === 0) return null;

  const total = chartData.reduce((s, d) => s + d.value, 0);

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-5">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Job Status</h3>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%" cy="50%"
              innerRadius={55} outerRadius={85}
              paddingAngle={3} dataKey="value"
            >
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.color} stroke="transparent" />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="flex justify-center gap-4 text-xs mt-2">
        {chartData.map(d => (
          <div key={d.name} className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }} />
            <span className="text-gray-400">{d.name}</span>
            <span className="font-semibold text-gray-300">{((d.value / total) * 100).toFixed(0)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function RevenueChart({ data }: { data: DashboardStats['revenue_trend'] }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Monthly Revenue</h3>
        <div className="h-56 flex items-center justify-center text-gray-500 text-sm">
          No revenue data yet
        </div>
      </div>
    );
  }

  const monthLabels: Record<string, string> = {
    '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
    '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
    '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec',
  };

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-5">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Monthly Revenue</h3>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#9CA3AF' }} tickFormatter={(v) => {
              const parts = v.split('-');
              return `${monthLabels[parts[1]] || parts[1]} '${parts[0].slice(2)}`;
            }} />
            <YAxis tick={{ fontSize: 11, fill: '#9CA3AF' }} tickFormatter={(v) => `$${v}`} />
            <Tooltip
              formatter={(value: any) => [`$${Number(value).toFixed(2)}`, 'Revenue']}
              contentStyle={{ borderRadius: '12px', backgroundColor: '#1f2937', border: '1px solid #374151', color: '#F9FAFB' }}
            />
            <Bar dataKey="revenue" fill="#DC2626" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function ProfitChart({ jobs }: { jobs: ArtisanJob[] }) {
  const completed = jobs.filter(j => j.status === 'completed' && j.profit > 0);
  if (completed.length === 0) return null;

  const data = completed.slice(-10).map(j => ({
    name: j.client_name.split(' ')[0],
    profit: j.profit,
    revenue: j.final_cost,
  }));

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-5">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Profit per Job (Last 10)</h3>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis type="number" tick={{ fontSize: 11, fill: '#9CA3AF' }} tickFormatter={(v) => `$${v}`} />
            <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: '#9CA3AF' }} width={70} />
            <Tooltip
              formatter={(value: any) => [`$${Number(value).toFixed(2)}`, 'Profit']}
              contentStyle={{ borderRadius: '12px', backgroundColor: '#1f2937', border: '1px solid #374151', color: '#F9FAFB' }}
            />
            <Bar dataKey="profit" fill="#22C55E" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function JobsTable({ jobs }: { jobs: ArtisanJob[] }) {
  if (jobs.length === 0) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-8 text-center">
        <BriefcaseIcon className="w-12 h-12 text-gray-600 mx-auto mb-3" />
        <p className="text-gray-400">No jobs found</p>
        <p className="text-gray-500 text-sm mt-1">Complete a diagnosis to see your first job here</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-2xl overflow-hidden">
      <div className="p-5 border-b border-gray-800">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Recent Jobs</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              <th className="text-left p-4 text-gray-500 font-medium">Client</th>
              <th className="text-left p-4 text-gray-500 font-medium">Contact</th>
              <th className="text-left p-4 text-gray-500 font-medium">Job</th>
              <th className="text-center p-4 text-gray-500 font-medium">Status</th>
              <th className="text-right p-4 text-gray-500 font-medium">Amount</th>
              <th className="text-right p-4 text-gray-500 font-medium">Profit</th>
              <th className="text-center p-4 text-gray-500 font-medium">Grade</th>
              <th className="text-right p-4 text-gray-500 font-medium">Date</th>
            </tr>
          </thead>
          <tbody>
            {jobs.slice(0, 20).map((job, i) => (
              <motion.tr
                key={job.job_id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                className="border-b border-gray-800/50 hover:bg-white/5 transition-colors"
              >
                <td className="p-4">
                  <div className="font-medium text-gray-200">{job.client_name}</div>
                  <div className="text-xs text-gray-500">{job.client_address?.split(',')[0]}</div>
                </td>
                <td className="p-4">
                  <div className="text-gray-400">{job.client_phone}</div>
                  <div className="text-xs text-gray-500">{job.client_email}</div>
                </td>
                <td className="p-4 max-w-[200px]">
                  <div className="truncate text-gray-300" title={job.description}>{job.description}</div>
                </td>
                <td className="p-4 text-center">
                  <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_BG[job.status as keyof typeof STATUS_BG] || STATUS_BG.pending}`}>
                    {job.status === 'completed' && <CheckCircleIcon className="w-3 h-3" />}
                    {job.status === 'in-progress' && <ClockIcon className="w-3 h-3" />}
                    {job.status === 'pending' && <ExclamationTriangleIcon className="w-3 h-3" />}
                    {job.status === 'completed' ? 'Done' : job.status === 'in-progress' ? 'Active' : 'Pending'}
                  </span>
                </td>
                <td className="p-4 text-right font-medium text-gray-200">${job.final_cost.toFixed(2)}</td>
                <td className="p-4 text-right">
                  <span className={`font-medium ${job.profit > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    ${job.profit.toFixed(2)}
                  </span>
                </td>
                <td className="p-4 text-center">
                  {job.grade ? (
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${GRADE_COLORS[job.grade] || 'bg-gray-800 text-gray-400'}`}>
                      {job.grade}
                    </span>
                  ) : (
                    <span className="text-xs text-gray-600">—</span>
                  )}
                </td>
                <td className="p-4 text-right text-gray-500 text-xs whitespace-nowrap">
                  {new Date(job.date).toLocaleDateString('en-US', { day: '2-digit', month: 'short' })}
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const CATEGORY_META: Record<string, { icon: any; color: string; label: string }> = {
  pricing: { icon: CurrencyDollarIcon, color: 'from-green-600 to-emerald-700', label: 'Pricing' },
  efficiency: { icon: ClockIcon, color: 'from-blue-600 to-indigo-700', label: 'Efficiency' },
  growth: { icon: ArrowTrendingUpIcon, color: 'from-purple-600 to-pink-700', label: 'Growth' },
  clients: { icon: UserGroupIcon, color: 'from-amber-600 to-orange-700', label: 'Clients' },
  operations: { icon: BuildingStorefrontIcon, color: 'from-teal-600 to-cyan-700', label: 'Operations' },
};

const PRIORITY_COLORS: Record<string, string> = {
  pricing: 'bg-green-500/20 text-green-400 border-green-500/30',
  efficiency: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  growth: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  clients: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  operations: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
};

function StewardCard({ suggestion, loading }: { suggestion: StewardSuggestion | null; loading: boolean }) {
  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 animate-pulse">
        <div className="h-4 bg-gray-700 rounded w-1/3 mb-4" />
        <div className="h-3 bg-gray-700 rounded w-full mb-2" />
        <div className="h-3 bg-gray-700 rounded w-3/4 mb-6" />
        <div className="grid md:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-gray-800/50 rounded-xl p-4 h-40" />
          ))}
        </div>
      </div>
    );
  }

  if (!suggestion || !suggestion.suggestions?.length) return null;

  const focusMeta = CATEGORY_META[suggestion.focus_priority] || CATEGORY_META.growth;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Business Health Banner */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gradient-to-r from-jing-primary/10 via-gray-900/80 to-jing-secondary/10 rounded-2xl p-5 border border-jing-primary/20 shadow-lg"
      >
        <div className="flex items-start gap-4">
          <div className="p-3 bg-gradient-to-br from-jing-primary to-jing-secondary rounded-xl shrink-0 shadow-lg shadow-jing-primary/20">
            <SparklesIcon className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-bold text-white text-lg">JING-STEWARD Business Coach</h3>
              <span className="text-xs bg-gradient-to-r from-jing-primary to-red-600 text-white px-2.5 py-0.5 rounded-full font-semibold shadow-sm">AI Advisor</span>
            </div>
            <p className="text-base text-gray-200 mt-1.5 leading-relaxed">{suggestion.business_health}</p>
            <div className="mt-3 flex items-center gap-2">
              <span className="text-xs text-gray-500 uppercase tracking-wider font-medium">Focus Priority:</span>
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${PRIORITY_COLORS[suggestion.focus_priority] || 'bg-gray-700 text-gray-300 border-gray-600'}`}>
                {React.createElement(focusMeta.icon, { className: 'w-3.5 h-3.5' })}
                {focusMeta.label}
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Suggestions Grid */}
      <div className="grid md:grid-cols-3 gap-4">
        {suggestion.suggestions.map((item, index) => {
          const meta = CATEGORY_META[item.category] || { icon: LightBulbIcon, color: 'from-gray-600 to-gray-700', label: item.category };
          const Icon = meta.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-900/60 border border-gray-800 rounded-2xl p-5 hover:border-gray-700 hover:bg-gray-900/80 transition-all group"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className={`p-2 bg-gradient-to-br ${meta.color} rounded-lg shrink-0 shadow-sm`}>
                  <Icon className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <span className={`text-xs font-semibold uppercase tracking-wider ${
                    item.category === 'pricing' ? 'text-green-400' :
                    item.category === 'efficiency' ? 'text-blue-400' :
                    item.category === 'growth' ? 'text-purple-400' :
                    item.category === 'clients' ? 'text-amber-400' : 'text-teal-400'
                  }`}>{meta.label}</span>
                  <p className="text-sm font-bold text-white truncate">{item.title}</p>
                </div>
              </div>
              <p className="text-sm text-gray-300 leading-relaxed mb-3">{item.suggestion}</p>
              <div className="text-xs text-gray-400 italic mb-3 border-l-2 border-gray-700 pl-3">
                {item.reason}
              </div>
              <div className="space-y-2 pt-3 border-t border-gray-800">
                <div className="bg-blue-900/20 border border-blue-800/30 rounded-lg p-2.5">
                  <p className="text-xs text-blue-400 font-semibold uppercase tracking-wider flex items-center gap-1">
                    <ShieldCheckIcon className="w-3 h-3" /> Action Step
                  </p>
                  <p className="text-xs text-blue-200 mt-0.5">{item.action}</p>
                </div>
                <div className="bg-green-900/20 border border-green-800/30 rounded-lg p-2.5">
                  <p className="text-xs text-green-400 font-semibold uppercase tracking-wider flex items-center gap-1">
                    <ArrowTrendingUpIcon className="w-3 h-3" /> Expected Impact
                  </p>
                  <p className="text-xs text-green-200 mt-0.5">{item.potential_impact}</p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}

function AskJingChat({ trade }: { trade?: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hi! I'm JING-STEWARD, your AI business coach. Ask me anything about your business — pricing advice, performance reports, client insights, or tips to grow. What's on your mind?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const question = input.trim();
    if (!question || loading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: question,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await askJing(question, trade);
      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: res.data.answer,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch {
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: "I'm sorry, I had trouble processing that. Please try rephrasing your question or check that the backend is running.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: "Hi! I'm JING-STEWARD, your AI business coach. Ask me anything about your business — pricing advice, performance reports, client insights, or tips to grow. What's on your mind?",
        timestamp: new Date(),
      },
    ]);
  };

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800 bg-gradient-to-r from-jing-primary/5 to-transparent">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-jing-primary to-jing-secondary rounded-lg shadow-sm">
            <ChatBubbleLeftRightIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-white text-sm">Ask JING Anything</h3>
            <p className="text-xs text-gray-500">Your AI business coach — powered by JING-STEWARD</p>
          </div>
        </div>
        <button
          onClick={clearChat}
          className="text-xs text-gray-500 hover:text-gray-300 flex items-center gap-1 px-2.5 py-1.5 rounded-lg hover:bg-gray-800 transition-all"
        >
          <ArrowPathIcon className="w-3.5 h-3.5" />
          Clear
        </button>
      </div>

      {/* Messages */}
      <div className="h-80 overflow-y-auto p-4 space-y-4 bg-gray-950/50">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shadow-sm ${
                msg.role === 'user'
                  ? 'bg-gradient-to-br from-jing-primary to-red-600 text-white'
                  : 'bg-gradient-to-br from-jing-secondary to-blue-700 text-white'
              }`}>
                {msg.role === 'user' ? 'U' : 'S'}
              </div>
              <div className={`max-w-[80%] ${
                msg.role === 'user'
                  ? 'bg-jing-primary/10 border border-jing-primary/20 rounded-2xl rounded-tr-md'
                  : 'bg-gray-800/50 border border-gray-700/50 rounded-2xl rounded-tl-md'
              } p-3.5`}>
                <p className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                <p className="text-xs text-gray-600 mt-1.5">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </motion.div>
          ))}
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3"
            >
              <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-jing-secondary to-blue-700 flex items-center justify-center shadow-sm">
                <SparklesIcon className="w-4 h-4 text-white" />
              </div>
              <div className="bg-gray-800/50 border border-gray-700/50 rounded-2xl rounded-tl-md p-4">
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-800 bg-gray-900/80">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about pricing, performance, clients, or growth..."
            disabled={loading}
            className="flex-1 bg-gray-800 text-white placeholder-gray-500 rounded-xl px-4 py-2.5 text-sm border border-gray-700 focus:outline-none focus:ring-2 focus:ring-jing-primary/50 focus:border-jing-primary/50 transition-all disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="bg-gradient-to-r from-jing-primary to-red-600 text-white px-4 py-2.5 rounded-xl hover:shadow-lg hover:shadow-jing-primary/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
          >
            <PaperAirplaneIcon className="w-4 h-4" />
          </button>
        </div>
        <p className="text-xs text-gray-600 mt-1.5 text-center">
          Ask about pricing strategies, profit analysis, client trends, business growth, or anything trade-related
        </p>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [searchParams] = useSearchParams();
  const tradeParam = searchParams.get('trade') || '';
  const isDemo = searchParams.get('demo') === 'true';

  const [trade, setTrade] = useState(tradeParam);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [jobs, setJobs] = useState<ArtisanJob[]>([]);
  const [suggestion, setSuggestion] = useState<StewardSuggestion | null>(null);
  const [loading, setLoading] = useState(true);
  const [suggestionLoading, setSuggestionLoading] = useState(true);

  const fetchData = useCallback(async (selectedTrade: string) => {
    setLoading(true);
    try {
      const [jobsRes, suggRes] = await Promise.all([
        getArtisanJobs(selectedTrade || undefined),
        getStewardSuggestion(selectedTrade || undefined),
      ]);
      setJobs(jobsRes.data.jobs);
      setStats(jobsRes.data.stats);
      setSuggestion(suggRes.data);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
      setSuggestionLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isDemo && trade) {
      seedDemoData(trade).then(() => fetchData(trade));
    } else {
      fetchData(trade);
    }
  }, [trade, isDemo, fetchData]);

  const handleTradeChange = (newTrade: string) => {
    setTrade(newTrade);
    setSuggestionLoading(true);
    setSuggestion(null);
  };

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <header className="bg-gray-950 border-b border-gray-800 sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link to="/" className="p-2 hover:bg-white/5 rounded-xl transition-colors">
                <ArrowLeftIcon className="w-5 h-5 text-gray-400" />
              </Link>
              <div>
                <h1 className="text-lg font-bold text-white">Artisan Dashboard</h1>
                <p className="text-xs text-gray-500">Business overview at a glance</p>
              </div>
            </div>

            {/* Trade filter */}
            <div className="flex items-center gap-2 bg-gray-900 rounded-xl p-1 border border-gray-800">
              {TRADES.map(t => (
                <button
                  key={t.value}
                  onClick={() => handleTradeChange(t.value)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    trade === t.value
                      ? 'bg-gray-700 text-white shadow-sm'
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  {t.icon} {t.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="bg-gray-900/50 border border-gray-800 rounded-2xl p-5 animate-pulse">
                  <div className="h-3 bg-gray-700 rounded w-16 mb-3" />
                  <div className="h-6 bg-gray-700 rounded w-20" />
                </div>
              ))}
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-5 animate-pulse h-64" />
              <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-5 animate-pulse h-64" />
            </div>
          </div>
        ) : (
          <>
            {/* Stats Cards */}
            {stats && (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                <StatsCard
                  icon={BriefcaseIcon}
                  label="Total Jobs"
                  value={stats.total_jobs.toString()}
                  sub={`${stats.completed_jobs} completed`}
                  color="bg-gradient-to-br from-blue-600 to-blue-700"
                />
                <StatsCard
                  icon={ClockIcon}
                  label="Active Jobs"
                  value={stats.in_progress_jobs.toString()}
                  sub={`${stats.pending_jobs} pending`}
                  color="bg-gradient-to-br from-amber-600 to-amber-700"
                />
                <StatsCard
                  icon={CurrencyDollarIcon}
                  label="Total Revenue"
                  value={`$${stats.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`}
                  sub={`$${stats.total_profit.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })} profit`}
                  color="bg-gradient-to-br from-green-600 to-green-700"
                />
                <StatsCard
                  icon={ChartBarIcon}
                  label="Avg Profit/Job"
                  value={`$${stats.average_profit.toFixed(0)}`}
                  sub={`${stats.average_duration_minutes}min avg`}
                  color="bg-gradient-to-br from-purple-600 to-purple-700"
                />
                <StatsCard
                  icon={UserGroupIcon}
                  label="Avg Grade"
                  value={stats.average_grade}
                  sub={`${stats.total_clients} clients`}
                  color="bg-gradient-to-br from-jing-primary to-red-700"
                />
              </div>
            )}

            {/* Charts */}
            <div className="grid md:grid-cols-3 gap-4 mb-6">
              {stats && <StatusPieChart data={stats.status_distribution} />}
              {stats && <RevenueChart data={stats.revenue_trend} />}
              <ProfitChart jobs={jobs} />
            </div>

            {/* Steward Suggestion */}
            <div className="mb-6">
              <StewardCard suggestion={suggestion} loading={suggestionLoading} />
            </div>

            {/* Jobs Table */}
            <JobsTable jobs={jobs} />

            {/* Ask JING */}
            <div className="mt-6">
              <AskJingChat trade={trade || undefined} />
            </div>
          </>
        )}
      </main>
    </div>
  );
}
