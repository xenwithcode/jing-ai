import { Link } from 'react-router-dom';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import MermaidChart from '../components/MermaidChart';

const DETAILED_ARCHITECTURE = `
graph TB
    subgraph USER_LAYER["📱 USER LAYER"]
        direction TB
        A1["👨‍🔧 Artisan Mobile"]
        A2["👤 Client Browser"]
        A3["📝 Signature Canvas"]
    end

    subgraph FRONTEND_LAYER["🎨 FRONTEND (Vercel)"]
        direction TB
        B1["React + TypeScript"]
        B2["TailwindCSS + Framer Motion"]
        B3["Recharts + Mermaid"]
    end

    subgraph API_LAYER["⚡ API LAYER (Alibaba Cloud Function Compute)"]
        direction TB
        C1["FastAPI REST Endpoints"]
        C2["MCP Server (Model Context Protocol)"]
        C3["WebSocket Streaming"]
    end

    subgraph ORCHESTRATION_LAYER["🎯 ORCHESTRATION LAYER"]
        direction TB
        D1["🧠 JING-MASTER<br/>(Qwen-Max)<br/>Strategic Planner"]
        D2["👷 JING-FOREMAN<br/>(Qwen-Plus)<br/>Coordinator"]
        D3["📋 Execution Plan<br/>(Pydantic Models)"]
    end

    subgraph AGENT_SOCIETY["🤖 AGENT SOCIETY (Workers)"]
        direction LR
        E1["👁️ JING-EYE<br/>Qwen-VL-Max<br/>Vision"]
        E2["📖 JING-SCRIBE<br/>Qwen-Plus<br/>Manuals"]
        E3["🧰 JING-KIT<br/>Qwen-Plus<br/>Logistics"]
        E6["⚖️ JING-REFEREE<br/>Qwen-Plus<br/>Debate Arbiter"]
        E4["💼 JING-STEWARD<br/>Qwen-Plus<br/>Finance"]
        E5["🔊 JING-VOICE<br/>Qwen-Audio<br/>Speech"]
    end

    subgraph MEMORY_LAYER["💾 MEMORY LAYER (Persistent JSON)"]
        direction TB
        G1["📁 Jobs (data/memory/jobs.json)"]
        G2["👤 Clients (data/memory/clients.json)"]
    end

    subgraph DASHBOARD_LAYER["📊 DASHBOARD (Business Intelligence)"]
        direction TB
        H1["📈 Stats Cards<br/>Total Jobs / Revenue"]
        H2["🍩 Status Pie Chart<br/>Completed / Active / Pending"]
        H3["📋 Jobs Table<br/>Filterable + Color-coded"]
        H4["🤖 Steward Suggestion<br/>AI Financial Advice"]
    end

    subgraph INFRA_LAYER["☁️ INFRASTRUCTURE"]
        direction TB
        F1["🌩️ Qwen Cloud API<br/>(Alibaba Cloud)"]
        F2["💾 File Storage<br/>(OSS)"]
        F3["🧠 Vector DB<br/>(Future RAG)"]
        F4["🔐 Auth & Logs"]
    end

    A1 -->|"Upload image + voice"| B1
    A2 -->|"Browse showcase"| B1
    A3 -->|"Digital signature"| B1
    
    B1 -->|"HTTPS REST"| C1
    B1 -->|"WebSocket"| C3
    C2 -->|"External Integration"| B1

    C1 -->|"Create plan"| D1
    D1 -->|"Execution Plan"| D3
    D3 -->|"Execute"| D2
    
    D2 -->|"Wave 1"| E1
    D2 -->|"Wave 2"| E2
    D2 -->|"Wave 2"| E3
    E2 & E3 -->|"Debate Phase"| E6
    E6 -->|"Consensus"| E4
    D2 -->|"Wave 4"| E5

    E4 -->|"Save job results"| G1
    E4 -->|"Update client history"| G2

    C1 -->|"Dashboard endpoints"| G1
    C1 -->|"Client history API"| G2
    C1 -->|"Steward suggestion API"| E4

    B1 -->|"Dashboard page<br/>/dashboard?trade=X"| H1
    H1 --> H2
    H2 --> H3
    H3 --> H4

    E1 -->|"Vision API"| F1
    E2 -->|"Text API"| F1
    E3 -->|"Text API"| F1
    E6 -->|"Text API"| F1
    E4 -->|"Text API"| F1
    E5 -->|"Audio API"| F1
    
    E1 -->|"Store images"| F2
    E4 -->|"Save signatures & PDFs"| F2
    E2 -->|"Search manuals"| F3

    classDef userLayer fill:#1F2937,stroke:#F59E0B,stroke-width:2px,color:#fff
    classDef frontendLayer fill:#1E40AF,stroke:#60A5FA,stroke-width:2px,color:#fff
    classDef apiLayer fill:#DC2626,stroke:#FCA5A5,stroke-width:2px,color:#fff
    classDef orchestrationLayer fill:#7C3AED,stroke:#C4B5FD,stroke-width:2px,color:#fff
    classDef agentLayer fill:#10B981,stroke:#6EE7B7,stroke-width:2px,color:#fff
    classDef debateLayer fill:#F59E0B,stroke:#FCD34D,stroke-width:2px,color:#000
    classDef memoryLayer fill:#06B6D4,stroke:#67E8F9,stroke-width:2px,color:#fff
    classDef dashboardLayer fill:#8B5CF6,stroke:#C4B5FD,stroke-width:2px,color:#fff
    classDef infraLayer fill:#374151,stroke:#9CA3AF,stroke-width:2px,color:#fff

    class A1,A2,A3 userLayer
    class B1,B2,B3 frontendLayer
    class C1,C2,C3 apiLayer
    class D1,D2,D3 orchestrationLayer
    class E1,E2,E3,E4,E5 agentLayer
    class E6 debateLayer
    class G1,G2 memoryLayer
    class H1,H2,H3,H4 dashboardLayer
    class F1,F2,F3,F4 infraLayer
`;

export default function ArchitecturePage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link 
            to="/" 
            className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeftIcon className="w-5 h-5" />
            <span>Back to Showcase</span>
          </Link>
          <h1 className="font-bold text-lg">JING Architecture</h1>
          <div className="w-24"></div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">System Architecture</h2>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            A 6-layer architecture designed for production-grade multi-agent orchestration 
            on Qwen Cloud infrastructure.
          </p>
        </div>

        {/* Diagram Container */}
        <div className="bg-gray-900 border border-gray-800 rounded-3xl p-8 mb-12">
          <MermaidChart chart={DETAILED_ARCHITECTURE} />
        </div>

        {/* Legend */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <h3 className="font-bold text-jing-primary mb-2">🎯 Orchestration Pattern</h3>
            <p className="text-sm text-gray-400">
              3-layer hierarchy: MASTER plans → FOREMAN coordinates → Workers execute in waves with debate phase.
            </p>
          </div>
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <h3 className="font-bold text-jing-secondary mb-2">⚡ Async Execution</h3>
            <p className="text-sm text-gray-400">
              All agent calls are async with Tenacity retry logic, exponential backoff, and fallback strategies.
            </p>
          </div>
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <h3 className="font-bold text-jing-accent mb-2">🔗 MCP Integration</h3>
            <p className="text-sm text-gray-400">
              Exposed as MCP tools for external systems. Claude Desktop, Cursor, and custom clients can interact with JING.
            </p>
          </div>
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <h3 className="font-bold text-cyan-400 mb-2">💾 Persistent Memory</h3>
            <p className="text-sm text-gray-400">
              Every job and client interaction is saved to local JSON. JING learns across sessions — no database required, zero infrastructure cost.
            </p>
          </div>
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <h3 className="font-bold text-violet-400 mb-2">📊 Artisan Dashboard</h3>
            <p className="text-sm text-gray-400">
              Real-time business intelligence: stats cards, charts, jobs table, and AI-powered suggestions from JING-STEWARD. Filter by trade for a focused view.
            </p>
          </div>
        </div>

        {/* Data Flow */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-3xl p-8">
          <h3 className="text-2xl font-bold mb-6 text-center">Data Flow: Technician → Diagnosis → Dashboard</h3>
          <div className="space-y-4">
            {[
              { step: "1", title: "Input Capture", desc: "Artisan uploads photo + voice description via mobile PWA", agent: "Frontend" },
              { step: "2", title: "Planning Phase", desc: "JING-MASTER analyzes request and creates execution plan with dependencies", agent: "JING-MASTER" },
              { step: "3", title: "Wave 1: Vision", desc: "JING-EYE processes image via Qwen-VL-Max, returns diagnosis", agent: "JING-EYE" },
              { step: "4", title: "Wave 2: Research", desc: "JING-SCRIBE finds manual + JING-KIT lists tools (in parallel)", agent: "SCRIBE + KIT" },
              { step: "5", title: "Debate Phase", desc: "JING-REFEREE resolves conflicts between agents, builds consensus before financial analysis", agent: "JING-REFEREE" },
              { step: "6", title: "Wave 3: Finance", desc: "JING-STEWARD generates professional budget with fair pricing", agent: "JING-STEWARD" },
              { step: "7", title: "Wave 4: Delivery", desc: "JING-VOICE synthesizes spoken response under 30 seconds", agent: "JING-VOICE" },
              { step: "8", title: "Client Signature", desc: "Client signs budget digitally with timestamp + geolocation", agent: "Frontend" },
              { step: "9", title: "Post-Job Analysis", desc: "JING-STEWARD generates financial summary with charts + insights", agent: "JING-STEWARD" },
              { step: "10", title: "Memory Persistence", desc: "Job results and client data saved to JSON — JING remembers every interaction", agent: "Memory Service" },
              { step: "11", title: "Artisan Dashboard", desc: "Real-time business dashboard with stats, charts, jobs table, and AI financial advice", agent: "Dashboard" },
            ].map((item, idx) => (
              <div key={idx} className="flex items-start space-x-4 bg-gray-800/30 rounded-xl p-4">
                <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-jing-primary to-jing-secondary rounded-full flex items-center justify-center font-bold">
                  {item.step}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-bold">{item.title}</h4>
                    <span className="text-xs text-gray-500 font-mono">{item.agent}</span>
                  </div>
                  <p className="text-sm text-gray-400">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
