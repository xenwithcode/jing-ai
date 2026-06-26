import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Link, useSearchParams } from 'react-router-dom';
import {
  BriefcaseIcon, CurrencyDollarIcon, ChartBarIcon,
  UserGroupIcon, ArrowLeftIcon, SparklesIcon,
  ClockIcon, CheckCircleIcon, ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts';
import { getArtisanJobs, getStewardSuggestion, seedDemoData } from '../services/api';
import type { DashboardStats, ArtisanJob, StewardSuggestion } from '../types';

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

function StewardCard({ suggestion, loading }: { suggestion: StewardSuggestion | null; loading: boolean }) {
  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 animate-pulse">
        <div className="h-4 bg-gray-700 rounded w-1/3 mb-4" />
        <div className="h-3 bg-gray-700 rounded w-full mb-2" />
        <div className="h-3 bg-gray-700 rounded w-3/4" />
      </div>
    );
  }

  if (!suggestion) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-r from-jing-primary/10 via-gray-900/80 to-jing-secondary/10 rounded-2xl p-6 border border-jing-primary/20 shadow-lg"
    >
      <div className="flex items-start gap-4">
        <div className="p-3 bg-gradient-to-br from-jing-primary to-jing-secondary rounded-xl shrink-0">
          <SparklesIcon className="w-6 h-6 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-bold text-white">JING-STEWARD Suggestion</h3>
            <span className="text-xs bg-jing-primary/20 text-jing-primary px-2 py-0.5 rounded-full font-medium">AI Advisor</span>
          </div>
          <p className="text-lg font-semibold text-white mt-2">{suggestion.suggestion}</p>
          <p className="text-sm text-gray-400 mt-2">{suggestion.reason}</p>
          <div className="mt-4 flex flex-wrap gap-4">
            <div className="bg-blue-900/20 border border-blue-800/30 rounded-xl p-3 flex-1 min-w-[200px]">
              <p className="text-xs text-blue-400 font-medium uppercase tracking-wider">Action</p>
              <p className="text-sm text-blue-300 font-medium mt-0.5">{suggestion.action}</p>
            </div>
            <div className="bg-green-900/20 border border-green-800/30 rounded-xl p-3 flex-1 min-w-[200px]">
              <p className="text-xs text-green-400 font-medium uppercase tracking-wider">Expected Impact</p>
              <p className="text-sm text-green-300 font-medium mt-0.5">{suggestion.potential_impact}</p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
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
          </>
        )}
      </main>
    </div>
  );
}
