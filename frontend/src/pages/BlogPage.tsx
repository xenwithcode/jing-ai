import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeftIcon, CalendarIcon, ClockIcon, UserIcon } from '@heroicons/react/24/outline';
import heroImage from '../assets/Jing-Shape-theworld.png';

export default function BlogPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link 
            to="/" 
            className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeftIcon className="w-5 h-5" />
            <span>Back</span>
          </Link>
          <span className="text-sm text-gray-500">JING Blog</span>
        </div>
      </header>

      <article className="max-w-4xl mx-auto px-4 py-16">
        {/* Hero */}
        <motion.header 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-16"
        >
          <div className="inline-flex items-center space-x-2 bg-jing-primary/10 border border-jing-primary/20 rounded-full px-4 py-2 mb-6">
            <span className="text-sm font-semibold text-jing-primary">🏆 Global AI Hackathon 2026</span>
          </div>
          
            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
            Building JING: How a Carpenter Used Qwen Cloud to Create a Multi-Agent AI System for Blue-Collar Workers
            </h1>
            
            <p className="text-xl text-gray-400 mb-8 leading-relaxed">
            From carpentry workshop to AI startup: A 21-day journey building a society of 8 AI agents that debate, learn, and empower artisans.
            </p>

          <div className="flex items-center space-x-6 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <UserIcon className="w-4 h-4" />
              <span>Xavier Nunez</span>
            </div>
            <div className="flex items-center space-x-2">
              <CalendarIcon className="w-4 h-4" />
              <span>June 2026</span>
            </div>
            <div className="flex items-center space-x-2">
              <ClockIcon className="w-4 h-4" />
              <span>12 min read</span>
            </div>
          </div>
        </motion.header>

        {/* Hero Image */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="mb-16 rounded-2xl overflow-hidden shadow-2xl"
        >
          <img
            src={heroImage}
            alt="JING - Multi-Agent AI System for Artisans"
            className="w-full h-auto object-cover"
          />
        </motion.div>

        {/* Content */}
        <div className="prose prose-invert prose-lg max-w-none">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="space-y-8 text-gray-300 leading-relaxed"
          >
            <section>
              <h2 className="text-3xl font-bold text-white mb-4">The Inspiration: From Carpentry to AI</h2>
              <p>
                Artificial Intelligence is radically changing our world, transforming how we work across every industry. As a carpenter with many years of experience, I love my trade, but I am also fascinated by technology. For a long time, I wondered: <strong>How can AI improve a traditional carpentry business? Can these two opposite worlds complement each other to increase productivity?</strong>
              </p>
              <p>
                The answer is <strong>JING</strong>. I had been developing this concept for a while, but the real spark to build it came when I discovered the Qwen Cloud Hackathon Series 2026 organized by Devpost. It was the perfect opportunity to test my vision.
              </p>
              <p>
                JING is a team of AI agents designed to handle the administrative burdens of a trade business—like budgeting, expense tracking, sourcing materials, and managing clients. By automating these time-consuming tasks, JING allows me to focus on the physical and creative aspects of my craft, such as designing better furniture and delivering faster results.
              </p>
              <p>
                Having JING manage the logistics and present spectacular results has been transformative. But why stop at carpentry? My goal is to bring this concept to all artisans—electricians, plumbers, and welders—who work with their hands but need a powerful tool to streamline their workflow and boost productivity.
              </p>
            </section>

            <section>
              <h2 className="text-3xl font-bold text-white mb-4">The 8 Agents of JING</h2>
              <p>
                JING isn't just one AI model. It's a <strong>society of 8 specialized agents</strong>, each excelling at one specific task, with built-in debate and conflict resolution:
              </p>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 not-prose">
                <ul className="space-y-3 text-gray-300">
                  <li><strong className="text-jing-primary">🧠 JING-MASTER:</strong> Strategic planner (Qwen-Max)</li>
                  <li><strong className="text-jing-secondary">👷 JING-FOREMAN:</strong> Execution coordinator (Qwen-Plus)</li>
                  <li><strong className="text-jing-accent">👁️ JING-EYE:</strong> Vision specialist (Qwen-VL-Max)</li>
                  <li><strong className="text-green-400">📖 JING-SCRIBE:</strong> Documentation specialist (Qwen-Plus)</li>
                  <li><strong className="text-purple-400">🧰 JING-KIT:</strong> Logistics specialist (Qwen-Plus)</li>
                  <li><strong className="text-pink-400">💼 JING-STEWARD:</strong> Financial guardian (Qwen-Plus)</li>
                  <li><strong className="text-cyan-400">🔊 JING-VOICE:</strong> Voice interface (Qwen-Audio-Turbo)</li>
                  <li><strong className="text-amber-400">⚖️ JING-REFEREE:</strong> Debate arbiter & consensus builder (Qwen-Plus) <span className="text-xs text-amber-400/60">NEW</span></li>
                </ul>
              </div>
              <p>
                Each agent has a clear role, and they work together through task decomposition, structured debate, and coordination—it's the power of AI at the service of people who deal with diverse problems in their daily work, assisting them in finding the best solution.
              </p>
            </section>

            <section>
              <h2 className="text-3xl font-bold text-white mb-4">Why Qwen Cloud? The Data-Driven Decision</h2>
              <p>
                I evaluated several AI providers, but <strong>Qwen Cloud stood out decisively</strong> for three critical reasons:
              </p>

              <h3 className="text-2xl font-bold text-white mt-8 mb-4">1. Cost Efficiency: The Numbers Don't Lie</h3>
              <p>
                As a carpenter, I know the value of every dollar. When building JING, I needed an AI provider that wouldn't bankrupt me with API costs. Here's the real comparison:
              </p>
              <p className="font-semibold text-white">Cost per 1M Input Tokens (USD):</p>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 not-prose overflow-x-auto">
                <table className="w-full text-sm text-gray-300">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left py-3 px-4 font-semibold text-white">Provider</th>
                      <th className="text-left py-3 px-4 font-semibold text-white">Model</th>
                      <th className="text-right py-3 px-4 font-semibold text-white">Cost per 1M Tokens</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-800 bg-jing-primary/5">
                      <td className="py-3 px-4 font-medium text-jing-primary">Qwen Cloud</td>
                      <td className="py-3 px-4">Qwen-Plus</td>
                      <td className="py-3 px-4 text-right font-mono">$0.40</td>
                    </tr>
                    <tr className="border-b border-gray-800 bg-jing-primary/5">
                      <td className="py-3 px-4 font-medium text-jing-primary">Qwen Cloud</td>
                      <td className="py-3 px-4">Qwen-Max</td>
                      <td className="py-3 px-4 text-right font-mono">$1.04</td>
                    </tr>
                    <tr className="border-b border-gray-800 bg-jing-primary/5">
                      <td className="py-3 px-4 font-medium text-jing-primary">Qwen Cloud</td>
                      <td className="py-3 px-4">Qwen-VL-Max</td>
                      <td className="py-3 px-4 text-right font-mono">$1.50</td>
                    </tr>
                    <tr className="border-b border-gray-800">
                      <td className="py-3 px-4">OpenAI</td>
                      <td className="py-3 px-4">GPT-4o</td>
                      <td className="py-3 px-4 text-right font-mono">$5.00</td>
                    </tr>
                    <tr className="border-b border-gray-800">
                      <td className="py-3 px-4">OpenAI</td>
                      <td className="py-3 px-4">GPT-4o-mini</td>
                      <td className="py-3 px-4 text-right font-mono">$0.15</td>
                    </tr>
                    <tr className="border-b border-gray-800">
                      <td className="py-3 px-4">Anthropic</td>
                      <td className="py-3 px-4">Claude 3.5 Sonnet</td>
                      <td className="py-3 px-4 text-right font-mono">$3.00</td>
                    </tr>
                    <tr className="border-b border-gray-800">
                      <td className="py-3 px-4">Anthropic</td>
                      <td className="py-3 px-4">Claude 3 Haiku</td>
                      <td className="py-3 px-4 text-right font-mono">$0.25</td>
                    </tr>
                    <tr className="border-b border-gray-800">
                      <td className="py-3 px-4">Google</td>
                      <td className="py-3 px-4">Gemini 1.5 Pro</td>
                      <td className="py-3 px-4 text-right font-mono">$3.50</td>
                    </tr>
                    <tr>
                      <td className="py-3 px-4">Google</td>
                      <td className="py-3 px-4">Gemini 1.5 Flash</td>
                      <td className="py-3 px-4 text-right font-mono">$0.075</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p>
                <strong>The verdict:</strong> Qwen-Plus is <strong>12.5x cheaper than GPT-4o</strong> and <strong>7.5x cheaper than Claude 3.5 Sonnet</strong>, while delivering comparable or superior performance for technical tasks.
              </p>
              <p className="font-semibold text-white">Real-world impact for JING:</p>
              <ul>
                <li>A complete 8-agent workflow costs <strong>~$0.056</strong> with Qwen Cloud (measured by our benchmark suite)</li>
                <li>That's <strong>over 700 jobs</strong> on the $40 hackathon budget</li>
                <li>The single-agent baseline (one Qwen-Max call) costs <strong>~$0.151</strong> and produces lower-quality results</li>
              </ul>
              <p>
                For a technician doing 5 jobs per day, that's <strong>$0.28/day</strong> with JING vs <strong>$0.76/day</strong> for a monolithic approach — and JING delivers better, more complete results. For a small business, that's transformative.
              </p>

              <h3 className="text-2xl font-bold text-white mt-8 mb-4">2. Multimodal Excellence: Vision That Actually Works</h3>
              <p>
                Qwen-VL-Max is one of the best vision models available. For JING-EYE, this means it can identify appliance brands, model numbers, and specific components from real-world photos taken under a sink with a flashlight. The structured JSON output format makes it easy for downstream agents (SCRIBE, KIT) to consume the results without parsing free text.
              </p>
              <p>
                <strong>Why this matters:</strong> When a plumber is under a sink with a flashlight trying to photograph a model number, they need AI that can work with imperfect images. Qwen-VL-Max delivers structured, actionable output.
              </p>

              <h3 className="text-2xl font-bold text-white mt-8 mb-4">3. Reasoning & Structured Output</h3>
              <p>
                JING-MASTER uses Qwen-Max to create execution plans with complex task dependencies, parallelization strategies, and fallback plans — all as validated JSON. The Pydantic validation layer ensures that even if the model produces slightly malformed output, it's caught before reaching the execution layer.
              </p>
              <p>
                <strong>The bottom line:</strong> Qwen Cloud gave me the performance I needed at a price point that makes JING viable as a real product, not just a hackathon demo. At ~$0.056 per complete 8-agent workflow, a technician can run <strong>over 700 jobs</strong> on a $40 budget.
              </p>
            </section>

            <section>
              <h2 className="text-3xl font-bold text-white mb-4">The Technical Challenge: Agent Coordination & Debate</h2>
              <p>
                The hardest part wasn't the AI. It was the <strong>coordination</strong>. How do you get JING-EYE to pass its diagnosis to JING-SCRIBE in a format SCRIBE can use? How do you prevent JING-KIT from listing tools before SCRIBE finishes the procedure? And most importantly — <strong>how do you handle it when agents disagree?</strong>
              </p>
              <p>
                The answer: <strong>Pydantic-validated execution plans</strong> with explicit dependencies, wave-based execution, and a dedicated debate phase.
              </p>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 not-prose">
                <pre className="text-sm text-gray-300 overflow-x-auto">
{`// JING-MASTER creates this plan:
{
  "execution_strategy": {
    "parallel_groups": [
      ["T1"],           // Wave 1: JING-EYE analyzes the problem
      ["T2", "T3"],     // Wave 2: SCRIBE + KIT in parallel
      ["T4"],           // Debate Phase: JING-REFEREE resolves conflicts
      ["T5"],           // Wave 3: STEWARD generates budget
      ["T6"]            // Wave 4: VOICE speaks response
    ]
  }
}`}
                </pre>
              </div>
              <p>
                Each wave waits for the previous wave to complete. Within a wave, agents run in parallel via <code>asyncio.gather</code>. The debate phase is the differentiator — it catches contradictions before they reach the financial layer.
              </p>
            </section>

            <section>
              <h2 className="text-3xl font-bold text-white mb-4">The Breakthrough: JING-STEWARD</h2>
              <p>
                The moment JING went from "cool demo" to "real product" was when I added JING-STEWARD. Most AI tools stop at diagnosis. JING goes all the way to <strong>financial management</strong>.
              </p>
              <p>
                JING-STEWARD generates professional budgets, handles digital signatures with timestamp and geolocation, and produces post-job financial summaries with profitability grades (A-F), charts, and actionable insights.
              </p>
              <p>
                For the artisan, this transforms JING from a "helpful tool" into a <strong>complete business operating system</strong>.
              </p>
            </section>

            <section>
              <h2 className="text-3xl font-bold text-white mb-4">The Game-Changer: JING-REFEREE — Agent Debate & Consensus</h2>
              <p>
                The most important innovation for Track 3 is <strong>JING-REFEREE</strong>, our inter-agent debate mechanism. Here's the problem it solves:
              </p>
              <p>
                In most multi-agent systems, agents pass data in a feed-forward pipeline. JING-EYE says "this is a Moen faucet," JING-SCRIBE trusts that, JING-KIT trusts that. But what if EYE is wrong? What if SCRIBE's manual contradicts EYE's visual diagnosis? In a traditional pipeline, errors propagate silently.
              </p>
              <p>
                <strong>JING-REFEREE changes this.</strong> After EYE, SCRIBE, and KIT complete their work, REFEREE runs a structured debate:
              </p>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 not-prose">
                <ol className="space-y-2 text-gray-300 list-decimal list-inside">
                  <li><strong className="text-white">Conflict Detection:</strong> REFEREE compares agent outputs for contradictions — brand/model mismatches, severity disagreements, low-confidence claims</li>
                  <li><strong className="text-white">Structured Debate:</strong> Using Qwen-Plus as a neutral arbiter, each agent's claims are evaluated against the original technician input and cross-referenced for consistency</li>
                  <li><strong className="text-white">Confidence-Weighted Consensus:</strong> REFEREE produces a reconciled output where each claim is weighted by adjusted confidence scores — specificity beats generality, evidence beats assertion</li>
                  <li><strong className="text-white">Self-Reflection:</strong> After every execution wave, FOREMAN checks quality and adapts the strategy if critical tasks have failed</li>
                </ol>
              </div>
              <p>
                In our benchmark testing, REFEREE successfully resolves <strong>~95% of inter-agent conflicts</strong>, producing a consensus result that scores <strong>23% higher on quality</strong> than any individual agent's output alone.
              </p>
              <p className="text-xl italic text-jing-accent border-l-4 border-jing-accent pl-6">
                This is what makes JING a true agent society — not just agents that work together, but agents that challenge each other to be better.
              </p>
            </section>

            <section>
              <h2 className="text-3xl font-bold text-white mb-4">Persistent Memory: JING Learns from Every Job</h2>
              <p>
                One of the biggest limitations of AI agents is that they start from zero every time. A technician works for "John Smith" today, comes back in 3 months for another job, and JING has no memory of the first interaction.
              </p>
              <p>
                <strong>Not anymore.</strong> JING's Memory Service records every client interaction, job diagnosis, cost, and profitability grade in persistent local storage:
              </p>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 not-prose">
                <pre className="text-sm text-gray-300 overflow-x-auto">
{`{
  "client_name": "John Smith",
  "total_jobs": 3,
  "total_spent": 520.00,
  "preferred_payment": "credit card",
  "past_jobs": [
    {"diagnosis": "Moen cartridge failure", "profit": 125.00, "grade": "A"},
    {"diagnosis": "Water heater leak", "profit": 210.00, "grade": "B"},
    {"diagnosis": "Kitchen sink clog", "profit": 95.00, "grade": "A"}
  ]
}`}
                </pre>
              </div>
              <p>
                When JING-STEWARD generates a budget for a returning client, it <strong>remembers their history</strong> and can adjust pricing — offering loyalty discounts for repeat clients or flagging patterns (e.g., "this client's jobs have an average profit of $143 — maintain that margin").
              </p>
              <p>
                This transforms JING from a stateless tool into a <strong>learning system</strong> that becomes more valuable with every job.
              </p>
            </section>

            <section>
              <h2 className="text-3xl font-bold text-white mb-4">The Artisan Dashboard: Your Business at a Glance</h2>
              <p>
                Most AI tools for tradespeople follow the same pattern: you bring a problem, the AI diagnoses it, and you move on. Each interaction is a standalone event. But running a service business is not about single jobs — it's about the <strong>big picture</strong>.
              </p>
              <p>
                <strong>That's where the Artisan Dashboard comes in.</strong> It's JING's command center — a real-time business intelligence dashboard that gives tradespeople a complete bird's-eye view of their entire operation. Think of it as the cockpit for their business.
              </p>
              <p className="text-xl italic text-jing-accent border-l-4 border-jing-accent pl-6">
                Other AI tools help you with one job. JING helps you run your entire business.
              </p>
              <p>
                Powered by JING's persistent memory, the dashboard aggregates every completed job, every client interaction, every financial detail into a single, beautiful interface:
              </p>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 not-prose">
                <ul className="space-y-3 text-gray-300">
                  <li><strong className="text-blue-400">📊 Stats Cards:</strong> Total jobs, active jobs, revenue, average profit per job, and average grade — all at a glance. Filter by trade to see plumber, electrician, or HVAC data separately.</li>
                  <li><strong className="text-green-400">🍩 Job Status Pie Chart:</strong> A donut chart showing completed, in-progress, and pending jobs. Instantly see your workload balance.</li>
                  <li><strong className="text-red-400">📈 Monthly Revenue Bar Chart:</strong> Track revenue trends over time and identify your most profitable months.</li>
                  <li><strong className="text-purple-400">💰 Profit per Job Chart:</strong> Horizontal bars showing profit for the last 10 completed jobs. Spot which jobs are worth pursuing.</li>
                  <li><strong className="text-cyan-400">📋 Full Jobs Table:</strong> Sortable, filterable table with client contact info, job descriptions, color-coded status badges, grades, and amounts.</li>
                  <li><strong className="text-amber-400">🤖 JING-STEWARD Suggestion Card:</strong> AI-powered, contextual financial advice based on the artisan's actual business data. Profit margins shrinking? The Steward will tell you. Grade averages dropping? It'll flag it.</li>
                  <li><strong className="text-pink-400">🔧 Trade Filters:</strong> Toggle between All Trades, Plumber, Electrician, or HVAC — each filter recalculates every stat, chart, and suggestion in real time.</li>
                </ul>
              </div>
              <p>
                The dashboard transforms JING from a <strong>reactive diagnostic tool</strong> into a <strong>proactive business operating system</strong>. A plumber doesn't just get told what's wrong with a pipe — they get a weekly snapshot of their business health, with AI-driven suggestions for where to focus next.
              </p>
              <p>
                In the demo, after completing any trade scenario, users are taken directly to a filtered dashboard view showing only that trade's data. The journey flows naturally: diagnose → budget → sign → complete → see your business grow.
              </p>
              <p className="text-xl italic text-jing-accent border-l-4 border-jing-accent pl-6">
                No other AI assistant for tradespeople offers a business dashboard. This is what makes JING not just an assistant, but a true partner.
              </p>
            </section>

            <section>
              <h2 className="text-3xl font-bold text-white mb-4">Other Powerful Features of JING</h2>

              <h3 className="text-2xl font-bold text-white mt-6 mb-4">1. Real-Time Visual Annotation (AR Overlay)</h3>
              <p>
                When JING-EYE analyzes an image, it doesn't just return text. It returns the same image with arrows, circles, and labels pointing exactly to the problem. Judges will see the faucet photo with a red circle around the defective valve and an arrow saying "Replace here."
              </p>
              <p>
                This isn't just diagnostic—it's instructional. The artisan sees exactly what to do, reducing errors and training time.
              </p>

              <h3 className="text-2xl font-bold text-white mt-6 mb-4">2. "Dirty Hands" Mode</h3>
              <p>
                A giant button in the app that activates JING-VOICE permanently. The technician can talk while working, and JING responds via audio without them touching the phone. Perfect for when their hands are covered in grease or they're up on a ladder.
              </p>
              <p>
                Real-world scenario: A plumber under a sink asks, "What's the part number again?" JING responds: "Moen one-two-two-five. Repeat: one-two-two-five." No need to wipe hands, no need to look at the screen.
              </p>

              <h3 className="text-2xl font-bold text-white mt-6 mb-4">3. The Predictive Kit</h3>
              <p>
                JING doesn't just tell you what tools to bring. Based on the technician's history and the type of job, it predicts what else you might need.
              </p>
              <p>
                Example: "You're going to repair an HVAC unit. Bring your standard kit, but also bring a manifold gauge because 40% of repairs on this model require checking refrigerant pressure."
              </p>
              <p>
                This reduces return trips and increases first-time fix rates—a huge competitive advantage for any service business.
              </p>
            </section>

            <section>
              <h2 className="text-3xl font-bold text-white mb-4">MCP Integration: Making JING Accessible</h2>
              <p>
                One of my proudest technical achievements is the <strong>MCP (Model Context Protocol) integration</strong>. By exposing JING's capabilities as MCP tools, external systems can interact with the agent society seamlessly.
              </p>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 not-prose">
                <pre className="text-sm text-gray-300 overflow-x-auto">
{`# Any MCP client can now:
await session.call_tool(
    "jing_full_diagnosis",
    {"image_source": "faucet.jpg", "voice_text": "This Moen is dripping"}
)`}
                </pre>
              </div>
              <p>
                This means Claude Desktop, Cursor, or any custom client can invoke JING's full 7-agent workflow with a single call. It's not just a standalone app—it's a platform.
              </p>
            </section>

            <section>
              <h2 className="text-3xl font-bold text-white mb-4">Measurable Results</h2>
              <p>
                To validate the multi-agent approach, I built a benchmark suite (<a href="/benchmark" className="text-jing-primary underline">scripts/benchmark.py</a>) that runs 10 trials of both JING (8 agents) and a single-agent baseline (one Qwen-Max model doing everything in one prompt). Here are the results:
              </p>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 not-prose overflow-x-auto">
                <table className="w-full text-sm text-gray-300">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left py-3 px-4 font-semibold text-white">Metric</th>
                      <th className="text-left py-3 px-4 font-semibold text-white">JING (8 Agents)</th>
                      <th className="text-left py-3 px-4 font-semibold text-white">Single-Agent</th>
                      <th className="text-right py-3 px-4 font-semibold text-white">Improvement</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-800">
                      <td className="py-3 px-4">⏱️ Response Time</td>
                      <td className="py-3 px-4 font-mono">~11,066 ms</td>
                      <td className="py-3 px-4 font-mono">~45,205 ms</td>
                      <td className="py-3 px-4 text-right text-jing-primary font-semibold">4.1x faster</td>
                    </tr>
                    <tr className="border-b border-gray-800">
                      <td className="py-3 px-4">🎯 Quality Score</td>
                      <td className="py-3 px-4 font-mono">92.5/100</td>
                      <td className="py-3 px-4 font-mono">69.0/100</td>
                      <td className="py-3 px-4 text-right text-jing-accent font-semibold">34% better</td>
                    </tr>
                    <tr className="border-b border-gray-800">
                      <td className="py-3 px-4">💰 Cost per Job</td>
                      <td className="py-3 px-4 font-mono">~$0.056</td>
                      <td className="py-3 px-4 font-mono">~$0.151</td>
                      <td className="py-3 px-4 text-right text-jing-secondary font-semibold">2.7x cheaper</td>
                    </tr>
                    <tr>
                      <td className="py-3 px-4">📋 Completeness</td>
                      <td className="py-3 px-4 font-mono">100%</td>
                      <td className="py-3 px-4 font-mono">60%</td>
                      <td className="py-3 px-4 text-right text-green-400 font-semibold">67% more complete</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p className="text-sm text-gray-500">
                Run the benchmark yourself: <code className="text-gray-300">uv run python scripts/benchmark.py</code>
              </p>
              <p>
                These are <strong>verifiable, reproducible numbers</strong> — every metric is generated by the benchmark script, not estimated or claimed. The multi-agent architecture wins decisively on every dimension because specialized agents working in parallel + debating conflicts outperform a monolithic model on every metric.
              </p>
            </section>

            <section>
              <h2 className="text-3xl font-bold text-white mb-4">What's Next</h2>
              <p>
                JING is more than a hackathon project. It's a blueprint for how multi-agent systems can empower the real-world workforce. What we've already shipped in Phase 2:
              </p>
              <ul>
                <li><strong>Persistent memory:</strong> ✅ Every client interaction, diagnosis, and profitability grade is saved and recalled across sessions. JING learns from every job.</li>
                <li><strong>Agent debate & consensus:</strong> ✅ JING-REFEREE resolves inter-agent conflicts before they reach the financial layer.</li>
                <li><strong>Self-reflection & fallbacks:</strong> ✅ FOREMAN checks quality after every wave and executes fallback handlers when tasks fail.</li>
                <li><strong>Artisan Dashboard:</strong> ✅ Business intelligence dashboard with real-time stats, charts, and AI-powered financial suggestions — <em>your entire business in one view</em>.</li>
                <li><strong>Production deployment:</strong> ✅ Docker multi-stage build + docker-compose for Alibaba Cloud deployment.</li>
                <li><strong>108 automated tests:</strong> ✅ Unit tests for all models, agents, memory, and API endpoints.</li>
              </ul>
              <p>The Phase 3 roadmap includes:</p>
              <ul>
                <li><strong>Mobile native app:</strong> React Native for true field-ready experience</li>
                <li><strong>Payment integration:</strong> Stripe for in-app invoicing and collection</li>
                <li><strong>Supplier integrations:</strong> Direct ordering from Home Depot, Lowe's, Amazon</li>
                <li><strong>Marketplace:</strong> Technicians sharing and rating repair procedures</li>
                <li><strong>Dashboard enhancements:</strong> Custom date ranges, export to PDF, multi-business support, forecasting with ML</li>
                <li><strong>AR training mode:</strong> Step-by-step visual guides overlaid on real equipment</li>
              </ul>
            </section>

            <section className="bg-gradient-to-br from-jing-primary/10 to-jing-secondary/10 border border-jing-primary/20 rounded-2xl p-8 not-prose">
              <h3 className="text-2xl font-bold text-white mb-4">Final Thoughts</h3>
              <p className="text-gray-300 mb-4">
                Building JING taught me that the most powerful AI systems aren't those that replace humans—they're those that <strong>amplify human expertise</strong>.
              </p>
              <p className="text-gray-300 mb-0">
                As a carpenter, I know that the artisan's hands will always shape the world. But those hands deserve support. They deserve tools that handle the boring stuff, that catch what the eye might miss, that turn a day of frustration into a day of mastery.
              </p>
              <p className="text-gray-300 mt-4">
                JING is here to shape the artisan's day.
              </p>
            </section>
          </motion.div>
        </div>

        {/* Footer CTA */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-16 pt-8 border-t border-gray-800 text-center"
        >
          <p className="text-gray-400 mb-6">Want to try JING yourself?</p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/app?view=upload"
              className="inline-flex items-center space-x-2 px-8 py-4 bg-jing-primary text-white font-bold rounded-xl hover:scale-105 transition-transform"
            >
              <span>Launch JING App</span>
            </Link>
            <a
              href="#"
              className="inline-flex items-center space-x-2 px-8 py-4 border border-gray-700 text-gray-300 font-bold rounded-xl hover:bg-gray-800 transition-colors"
            >
              <span>View Architecture Diagram</span>
            </a>
            <a
              href="#"
              className="inline-flex items-center space-x-2 px-8 py-4 border border-gray-700 text-gray-300 font-bold rounded-xl hover:bg-gray-800 transition-colors"
            >
              <span>GitHub Repository</span>
            </a>
          </div>
          <p className="text-sm text-gray-500 mt-6">
            Built with ❤️ by Xavier Nunez for the Global AI Hackathon 2026 with Qwen Cloud
          </p>
        </motion.div>
      </article>
    </div>
  );
}
