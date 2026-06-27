import { motion, useScroll, useTransform } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  CurrencyDollarIcon,
  SparklesIcon, ArrowRightIcon, ClockIcon,
  UserGroupIcon, CodeBracketIcon, ChartBarIcon
} from '@heroicons/react/24/outline';
import MermaidChart from '../components/MermaidChart';

const ARCHITECTURE_CHART = `
graph TD
    A[📸 Technician Input] --> B[🧠 JING-MASTER]
    B -->|Execution Plan| C[👷 JING-FOREMAN]
    C -->|Wave 1| D[👁️ JING-EYE]
    D -->|Wave 2| E[📖 JING-SCRIBE]
    D -->|Wave 2| F[🧰 JING-KIT]
    E & F -->|Debate Phase| R[⚖️ JING-REFEREE]
    R -->|Wave 3| G[💼 JING-STEWARD]
    G -->|Wave 4| H[🔊 JING-VOICE]
    H --> I[✅ Prepared Artisan]

    style A fill:#1F2937,stroke:#DC2626,stroke-width:2px,color:#fff
    style B fill:#DC2626,stroke:#DC2626,stroke-width:2px,color:#fff
    style C fill:#1E40AF,stroke:#1E40AF,stroke-width:2px,color:#fff
    style D fill:#F59E0B,stroke:#F59E0B,stroke-width:2px,color:#000
    style E fill:#10B981,stroke:#10B981,stroke-width:2px,color:#fff
    style F fill:#8B5CF6,stroke:#8B5CF6,stroke-width:2px,color:#fff
    style R fill:#F59E0B,stroke:#F59E0B,stroke-width:2px,color:#000
    style G fill:#EC4899,stroke:#EC4899,stroke-width:2px,color:#fff
    style H fill:#06B6D4,stroke:#06B6D4,stroke-width:2px,color:#fff
    style I fill:#10B981,stroke:#10B981,stroke-width:2px,color:#fff
`;

export default function LandingPage() {
  const { scrollYProgress } = useScroll();
  const scaleX = useTransform(scrollYProgress, [0, 1], [0, 1]);

  return (
    <div className="min-h-screen bg-gray-950 text-white overflow-x-hidden">
      {/* Progress Bar */}
      <motion.div
        className="fixed top-0 left-0 right-0 h-1 bg-gradient-to-r from-jing-primary to-jing-secondary origin-left z-50"
        style={{ scaleX }}
      />

      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-gray-950/80 backdrop-blur-md border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-jing-primary to-jing-secondary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">匠</span>
            </div>
            <span className="font-bold">JING</span>
          </Link>

          <div className="flex items-center space-x-6 text-sm">
            <Link to="/" className="text-white font-medium">Home</Link>
            <Link to="/demo" className="text-gray-400 hover:text-white transition-colors">Demo</Link>
            <Link to="/architecture" className="text-gray-400 hover:text-white transition-colors">Architecture</Link>
            <Link to="/blog" className="text-gray-400 hover:text-white transition-colors">Blog</Link>
          </div>
        </div>
      </nav>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* 1. HERO SECTION */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <section className="relative min-h-screen flex items-center justify-center px-4 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-jing-primary/20 via-gray-950 to-gray-950"></div>
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>

        <div className="relative z-10 max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-flex items-center space-x-2 bg-white/5 border border-white/10 rounded-full px-4 py-2 mb-8 backdrop-blur-sm">
              <SparklesIcon className="w-5 h-5 text-jing-accent" />
              <span className="text-sm font-medium text-gray-300">Powered by Qwen Cloud • Track 3: Agent Society</span>
            </div>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-5xl md:text-7xl font-bold tracking-tight mb-6"
          >
            The artisan's hands <br />
            <span className="bg-gradient-to-r from-jing-primary via-jing-accent to-jing-secondary bg-clip-text text-transparent">
              shape the world.
            </span>
          </motion.h1>

          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.4 }}
            className="flex justify-center my-8"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="text-6xl"
            >
              匠
            </motion.div>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="text-4xl md:text-6xl font-bold tracking-tight mb-8"
          >
            <span className="text-jing-secondary">JING</span> shapes the artisan's day.
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="text-xl text-gray-400 max-w-2xl mx-auto mb-12"
          >
            A multi-agent AI society that diagnoses problems, manages finances,
            and empowers blue-collar technicians with the power of Qwen Cloud.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link
              to="/demo"
              className="group relative px-8 py-4 bg-jing-primary text-white font-bold rounded-xl overflow-hidden transition-all hover:scale-105 shadow-lg shadow-jing-primary/25"
            >
              <span className="relative z-10 flex items-center space-x-2">
                <span>See JING in Action</span>
                <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-jing-secondary to-jing-primary opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </Link>

            <Link
              to="/app?view=upload"
              className="px-8 py-4 bg-white/5 border border-white/10 text-white font-bold rounded-xl hover:bg-white/10 transition-all flex items-center space-x-2"
            >
              <span>Launch JING App</span>
            </Link>

            <a
              href="https://github.com/xenwithcode/jing"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-4 bg-white/5 border border-white/10 text-white font-bold rounded-xl hover:bg-white/10 transition-all flex items-center space-x-2"
            >
              <CodeBracketIcon className="w-5 h-5" />
              <span>Source Code</span>
            </a>
          </motion.div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* 2. PROBLEM SECTION */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <section className="py-24 px-4 bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">The Hidden Crisis in Blue-Collar Work</h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Millions of skilled technicians lose hours every day to administrative friction,
              leaving money on the table and frustrating their customers.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: ClockIcon,
                title: "30-60 Minutes Lost",
                desc: "Per job, searching for manuals, diagnosing unfamiliar equipment, or making return trips for forgotten tools.",
                color: "text-jing-primary"
              },
              {
                icon: CurrencyDollarIcon,
                title: "Unprofitable Hours",
                desc: "Working 60-hour weeks but struggling to track actual margins. Many don't know if they're making money.",
                color: "text-jing-accent"
              },
              {
                icon: UserGroupIcon,
                title: "Frustrated Customers",
                desc: "Lack of professional quotes, unclear timelines, and surprise costs erode trust in the industry.",
                color: "text-jing-secondary"
              }
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.2 }}
                className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8 hover:border-jing-primary/50 transition-colors"
              >
                <item.icon className={`w-12 h-12 ${item.color} mb-6`} />
                <h3 className="text-2xl font-bold mb-3">{item.title}</h3>
                <p className="text-gray-400">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* 3. ARCHITECTURE SECTION (Agent Society) */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <section className="py-24 px-4 bg-gray-950">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <span className="text-jing-accent font-bold tracking-wider uppercase text-sm">Track 3: Agent Society</span>
            <h2 className="text-4xl font-bold mt-2 mb-4">A Society of 8 Specialized Agents</h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              JING isn't a single chatbot. It's a multi-agent system where specialized AI workers
              decompose tasks, negotiate dependencies, and collaborate to solve complex real-world problems.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="bg-gray-900/50 border border-gray-800 rounded-3xl p-8 mb-12"
          >
            <MermaidChart chart={ARCHITECTURE_CHART} />
          </motion.div>

          <div className="grid md:grid-cols-4 gap-6">
            {[
              { name: "JING-MASTER", role: "Strategic Planner", model: "Qwen-Max", color: "bg-jing-primary" },
              { name: "JING-FOREMAN", role: "Execution Coordinator", model: "Qwen-Plus", color: "bg-jing-secondary" },
              { name: "JING-EYE", role: "Vision Specialist", model: "Qwen-VL-Max", color: "bg-jing-accent" },
              { name: "JING-SCRIBE", role: "Documentation Specialist", model: "Qwen-Plus", color: "bg-green-500" },
              { name: "JING-KIT", role: "Logistics Specialist", model: "Qwen-Plus", color: "bg-purple-500" },
              { name: "JING-REFEREE", role: "Debate Arbiter", model: "Qwen-Plus", color: "bg-amber-500" },
              { name: "JING-STEWARD", role: "Financial Guardian", model: "Qwen-Plus", color: "bg-pink-500" },
              { name: "JING-VOICE", role: "Voice Interface", model: "Qwen-Audio-Turbo", color: "bg-cyan-500" },
            ].map((agent, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.08 }}
                className="bg-gray-800/30 border border-gray-700 rounded-xl p-6"
              >
                <div className={`w-3 h-3 ${agent.color} rounded-full mb-4`}></div>
                <h3 className="font-bold text-lg">{agent.name}</h3>
                <p className="text-sm text-gray-400 mb-2">{agent.role}</p>
                <p className="text-xs text-gray-500 font-mono">{agent.model}</p>
              </motion.div>
            ))}
          </div>

          <Link
            to="/architecture"
            className="mt-8 inline-flex items-center space-x-2 text-jing-accent hover:text-white transition-colors"
          >
            <span>View Full Architecture Diagram</span>
            <ArrowRightIcon className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* 4. JOURNEY / BLOG SECTION */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <section className="py-24 px-4 bg-gray-900">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <span className="text-jing-secondary font-bold tracking-wider uppercase text-sm">The Journey</span>
            <h2 className="text-4xl font-bold mt-2 mb-4">Building JING with Qwen Cloud</h2>
          </motion.div>

          <motion.article
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="prose prose-invert prose-lg max-w-none bg-gray-800/30 border border-gray-700 rounded-3xl p-12"
          >
            <p className="text-gray-300 leading-relaxed mb-6">
              When I started building JING, I wanted to solve a problem I saw firsthand: skilled artisans
              are masters of their craft but often struggle with the business and diagnostic side of their work.
              I needed an AI system that could <strong>see</strong> what they see, <strong>know</strong> every manual ever written,
              and <strong>manage</strong> their finances.
            </p>

            <p className="text-gray-300 leading-relaxed mb-6">
              <strong>Why Qwen Cloud?</strong> The multimodal capabilities of Qwen-VL-Max for vision diagnosis,
              combined with the deep reasoning of Qwen-Max for strategic planning, made it the perfect foundation.
              The ability to orchestrate these models through a custom MCP (Model Context Protocol) integration
              allowed me to build a true Agent Society, not just a chain of prompts.
            </p>

            <p className="text-gray-300 leading-relaxed mb-6">
              The biggest challenge was <strong>agent coordination</strong>. Getting JING-MASTER to decompose tasks
              and JING-FOREMAN to handle dependencies without hallucinations required rigorous Pydantic validation
              and fallback strategies. Qwen Cloud's reliability and low latency made the 11-second end-to-end
              diagnosis possible.
            </p>

            <p className="text-gray-300 leading-relaxed">
              JING is more than a hackathon project. It's a blueprint for how multi-agent systems can empower
              the real-world workforce. The artisan's hands shape the world; JING is here to shape their day.
            </p>
          </motion.article>

          <div className="text-center mt-8">
            <a
              href="https://dev.to/xenwithcode/building-jing-how-a-carpenter-used-qwen-cloud-to-create-a-multi-agent-ai-system-for-blue-collar-1imh"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-2 px-6 py-3 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors"
            >
              <span>Read Full Story on Dev.to</span>
              <ArrowRightIcon className="w-5 h-5" />
            </a>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* 5. METRICS SECTION */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <section className="py-24 px-4 bg-gray-950">
        <div className="max-w-6xl mx-auto text-center">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-4xl font-bold mb-16"
          >
            Measurable Efficiency Gains
          </motion.h2>

          <div className="grid md:grid-cols-4 gap-8">
            {[
              { value: "4x", label: "Faster Response", desc: "11s vs 45s single-agent", color: "text-jing-primary" },
              { value: "35%", label: "Better Quality", desc: "92/100 vs 68/100 score", color: "text-jing-accent" },
              { value: "2.7x", label: "Cheaper Cost", desc: "$0.06 vs $0.15 per job", color: "text-jing-secondary" },
              { value: "67%", label: "More Complete", desc: "100% vs 60% task coverage", color: "text-green-500" },
            ].map((metric, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="bg-gray-900/50 border border-gray-800 rounded-2xl p-8"
              >
                <div className={`text-5xl font-bold ${metric.color} mb-2`}>{metric.value}</div>
                <div className="text-xl font-bold mb-1">{metric.label}</div>
                <div className="text-sm text-gray-500">{metric.desc}</div>
              </motion.div>
            ))}
          </div>

          <Link
            to="/benchmark"
            className="mt-8 inline-flex items-center space-x-2 text-jing-accent hover:text-white transition-colors"
          >
            <span>View Full Benchmark Methodology & Source Code</span>
            <ArrowRightIcon className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* 6. CTA & FOOTER */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <section className="py-24 px-4 bg-gradient-to-b from-gray-950 to-jing-primary/10">
        <div className="max-w-4xl mx-auto text-center">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-5xl font-bold mb-8"
          >
            Ready to empower the modern artisan?
          </motion.h2>

          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/demo"
                className="inline-flex items-center space-x-2 px-10 py-5 bg-jing-primary text-white font-bold text-xl rounded-xl hover:scale-105 transition-transform shadow-xl shadow-jing-primary/25"
              >
                <span>See JING in Action</span>
                <ArrowRightIcon className="w-6 h-6" />
              </Link>
              <Link
                to="/dashboard?demo=true&trade=plumber"
                className="inline-flex items-center space-x-2 px-10 py-5 bg-white/5 border border-white/10 text-white font-bold text-xl rounded-xl hover:bg-white/10 transition-all"
              >
                <ChartBarIcon className="w-6 h-6" />
                <span>Artisan Dashboard</span>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      <footer className="py-12 px-4 border-t border-gray-800 bg-gray-950">
        <div className="max-w-6xl mx-auto">
          {/* Top section: Logo + Links */}
          <div className="flex flex-col md:flex-row justify-between items-center gap-6 mb-8">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-jing-primary to-jing-secondary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">匠</span>
              </div>
              <div>
                <h3 className="font-bold text-lg">JING</h3>
                <p className="text-xs text-gray-500">The Expert Spirit for the Modern Artisan</p>
              </div>
            </div>

            <div className="flex flex-wrap justify-center gap-6 text-sm">
              <a
                href="https://github.com/xenwithcode/jing"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors flex items-center space-x-1"
              >
                <span>GitHub</span>
              </a>
              <a
                href="https://qwencloud-ai-hackathon.devpost.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors flex items-center space-x-1"
              >
                <span>Devpost</span>
              </a>
              <a
                href="https://qwen.cloud"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors flex items-center space-x-1"
              >
                <span>Qwen Cloud</span>
              </a>
              <a
                href="/LICENSE"
                className="text-gray-400 hover:text-white transition-colors flex items-center space-x-1"
              >
                <span>MIT License</span>
              </a>
            </div>
          </div>

          {/* Bottom section: Hackathon badge + Copyright */}
          <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center space-x-3">
              <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-jing-primary/10 to-jing-secondary/10 border border-jing-primary/20 rounded-full px-4 py-2">
                <span className="text-xs font-semibold text-jing-primary">🏆 Global AI Hackathon Series</span>
                <span className="text-xs text-gray-400">•</span>
                <span className="text-xs font-semibold text-jing-secondary">Powered by Qwen Cloud</span>
              </div>
            </div>

            <p className="text-sm text-gray-600 text-center md:text-right">
              Built with ❤️ by <span className="text-gray-400 font-semibold">Xavier Nunez</span> • 2026
            </p>
          </div>

          {/* Tagline final */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-500 italic">
              "The artisan's hands shape the world. JING shapes the artisan's day."
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
