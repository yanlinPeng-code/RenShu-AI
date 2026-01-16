import React, { useState } from 'react';
import { User, AVAILABLE_MODELS } from '../../types';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';

interface AdminPortalProps {
  user: User;
  onLogout: () => void;
}

type AdminView = 'dashboard' | 'models' | 'stats' | 'knowledge';

const AdminPortal: React.FC<AdminPortalProps> = ({ user, onLogout }) => {
  const [activeView, setActiveView] = useState<AdminView>('dashboard');
  const [isSidebarOpen, setSidebarOpen] = useState(true);

  // --- 模拟数据 ---
  const [models, setModels] = useState(AVAILABLE_MODELS.map(m => ({ ...m, usageCount: Math.floor(Math.random() * 5000) })));

  // --- 子模块组件 ---

  const DashboardHome = () => (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard label="Total Requests" value="284,102" trend="+12.5%" icon={Icons.Zap} color="text-blue-500" />
        <StatCard label="Avg Latency" value="1.24s" trend="-5%" icon={Icons.Activity} color="text-emerald-500" />
        <StatCard label="Token Ingested" value="1.4M" trend="+8%" icon={Icons.BrainCircuit} color="text-indigo-500" />
        <StatCard label="System Health" value="99.98%" trend="Optimal" icon={Icons.Check} color="text-tcm-gold" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            Real-time Traffic Monitor
          </h3>
          <div className="h-64 flex items-end gap-1.5 px-2">
            {[30, 45, 25, 60, 80, 40, 55, 90, 70, 40, 60, 85, 30, 50, 75, 40, 60, 30, 20, 45].map((h, i) => (
              <div key={i} className="flex-1 bg-gradient-to-t from-blue-600/20 to-blue-500/80 hover:to-blue-400 transition-all rounded-t-sm" style={{ height: `${h}%` }}></div>
            ))}
          </div>
          <div className="flex justify-between mt-4 text-[10px] text-slate-600 font-bold font-mono">
            <span>T-20min</span><span>Current</span>
          </div>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
           <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-6">Critical System Logs</h3>
           <div className="space-y-3 font-mono">
              <LogLine time="14:20:01" type="INFO" msg="Model 'gemini-3-pro' updated to rev.0925" />
              <LogLine time="14:15:22" type="WARN" msg="Latency spike detected in Region-Asia" />
              <LogLine time="14:02:45" type="AUTH" msg="Admin 'Root' modified knowledge base: TCM_Core" />
              <LogLine time="13:55:10" type="SUCCESS" msg="Scheduled vector re-indexing completed" />
              <LogLine time="13:40:02" type="INFO" msg="System heartbeat pulse: 62ms" />
           </div>
        </div>
      </div>
    </div>
  );

  const ModelConfig = () => (
    <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden animate-in slide-in-from-bottom-4 duration-500">
      <div className="p-6 border-b border-slate-800 flex justify-between items-center">
         <h3 className="text-sm font-bold text-white uppercase tracking-widest">AI Engine Orchestration</h3>
         <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-[10px] font-bold rounded-lg uppercase tracking-widest flex items-center gap-2 transition-colors">
           <Icons.Plus size={14} /> Add Model
         </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-400">
          <thead className="bg-slate-950 text-slate-500 font-bold uppercase tracking-widest">
            <tr>
              <th className="p-6">Model Identifier</th>
              <th className="p-6">Architecture</th>
              <th className="p-6">Thinking Budget</th>
              <th className="p-6">Vision</th>
              <th className="p-6">Lifetime Calls</th>
              <th className="p-6">Status</th>
              <th className="p-6">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {models.map(model => (
              <tr key={model.id} className="hover:bg-blue-500/5 transition-colors group">
                <td className="p-6">
                  <div className="font-bold text-white group-hover:text-blue-400 transition-colors">{model.name}</div>
                  <div className="text-[10px] opacity-40 font-mono mt-1">{model.id}</div>
                </td>
                <td className="p-6"><span className="px-2 py-0.5 bg-slate-800 rounded text-[9px] uppercase font-bold tracking-tighter">Transformer v4</span></td>
                <td className="p-6">
                   <div className="flex items-center gap-2 text-indigo-400 font-mono">
                     <Icons.BrainCircuit size={14} /> 1,024 Tokens
                   </div>
                </td>
                <td className="p-6">
                   {model.supportsVision ? <Icons.Image size={14} className="text-pink-500" /> : <Icons.X size={14} className="text-slate-700" />}
                </td>
                <td className="p-6 font-mono">{model.usageCount.toLocaleString()}</td>
                <td className="p-6">
                  <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase ${model.status === 'active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
                    {model.status}
                  </span>
                </td>
                <td className="p-6">
                  <div className="flex gap-3">
                    <button className="text-slate-500 hover:text-white transition-colors"><Icons.Edit3 size={14}/></button>
                    <button className="text-slate-500 hover:text-red-500 transition-colors"><Icons.Trash2 size={14}/></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const UsageStats = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-500">
      <div className="lg:col-span-2 bg-slate-900/50 border border-slate-800 p-8 rounded-2xl">
        <div className="flex justify-between items-center mb-10">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Compute Usage Statistics</h3>
          <select className="bg-slate-950 border border-slate-800 text-[10px] text-white px-3 py-1 rounded focus:outline-none">
            <option>Last 7 Days</option>
            <option>Last 30 Days</option>
          </select>
        </div>
        <div className="space-y-8">
           <UsageBar label="Gemini 3.0 Pro" percent={85} color="bg-blue-500" val="2.4M Tokens" />
           <UsageBar label="Gemini 3.0 Flash" percent={60} color="bg-emerald-500" val="1.8M Tokens" />
           <UsageBar label="Gemini 2.5 Flash" percent={30} color="bg-indigo-500" val="0.5M Tokens" />
           <UsageBar label="Legacy Engines" percent={10} color="bg-slate-600" val="0.1M Tokens" />
        </div>
      </div>

      <div className="bg-slate-900/50 border border-slate-800 p-8 rounded-2xl flex flex-col">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-10">Cost Distribution</h3>
        <div className="flex-1 flex flex-col justify-center items-center">
           <div className="relative w-40 h-40">
             <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#1e293b" strokeWidth="15" />
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#3b82f6" strokeWidth="15" strokeDasharray="251" strokeDashoffset="60" />
             </svg>
             <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="text-[10px] font-bold text-slate-500 uppercase">Total Est.</span>
                <span className="text-xl font-bold text-white">$4,120</span>
             </div>
           </div>
           <div className="mt-8 grid grid-cols-2 gap-4 w-full text-[10px] font-bold uppercase">
              <div className="flex items-center gap-2"><div className="w-2 h-2 bg-blue-500"></div> API Cost (75%)</div>
              <div className="flex items-center gap-2"><div className="w-2 h-2 bg-slate-700"></div> Infra (25%)</div>
           </div>
        </div>
      </div>
    </div>
  );

  const KnowledgeBase = () => (
    <div className="space-y-6 animate-in fade-in duration-500">
       <div className="flex justify-between items-center">
          <div>
            <h2 className="text-lg font-bold text-white uppercase tracking-widest flex items-center gap-2">
              <Icons.ShieldPlus className="text-tcm-gold" size={20} />
              Knowledge Retrieval Store
            </h2>
            <p className="text-[10px] text-slate-500 font-bold uppercase mt-1">Managed Vector Database Indices</p>
          </div>
          <button className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2 rounded-lg text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 transition-all">
            <Icons.UploadCloud size={14} /> New Corpus
          </button>
       </div>

       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <KBFolder name="TCM Classics Vector" docs={142} size="842 MB" status="Optimized" date="2024-10-01" />
          <KBFolder name="Clinical Guidelines V2" docs={85} size="1.2 GB" status="Indexed" date="2024-09-28" />
          <KBFolder name="Research Papers (2024)" docs={310} size="4.8 GB" status="Syncing..." date="Live" active={true} />
          <KBFolder name="Anonymized Case Data" docs={1200} size="12.4 GB" status="Optimized" date="2024-09-15" />
          <KBFolder name="Drug Interaction Data" docs={52} size="120 MB" status="Deprecated" date="2023-12-10" />
       </div>
    </div>
  );

  return (
    <div className="w-full h-screen flex bg-[#020617] text-slate-300 font-sans selection:bg-blue-500/30">

      {/* 侧边栏 */}
      <aside className={`${isSidebarOpen ? 'w-64' : 'w-20'} flex-shrink-0 bg-slate-900/50 border-r border-slate-800 transition-all duration-300 flex flex-col z-50`}>
        <div className="h-20 flex items-center px-6 border-b border-slate-800 shrink-0">
          <BrandLogo size="md" variant="dark" showText={isSidebarOpen} />
        </div>

        <nav className="flex-1 py-8 px-4 space-y-4">
          <AdminNavItem icon={Icons.Bot} label="Dashboard" active={activeView === 'dashboard'} onClick={() => setActiveView('dashboard')} minimized={!isSidebarOpen} />
          <AdminNavItem icon={Icons.Settings} label="Model Orchestration" active={activeView === 'models'} onClick={() => setActiveView('models')} minimized={!isSidebarOpen} />
          <AdminNavItem icon={Icons.Activity} label="Performance Analytics" active={activeView === 'stats'} onClick={() => setActiveView('stats')} minimized={!isSidebarOpen} />
          <AdminNavItem icon={Icons.ShieldPlus} label="Vector Knowledge" active={activeView === 'knowledge'} onClick={() => setActiveView('knowledge')} minimized={!isSidebarOpen} />
        </nav>

        <div className="p-4 border-t border-slate-800">
          <button onClick={onLogout} className="w-full flex items-center justify-center gap-2 py-3 text-[10px] font-bold text-red-400 hover:bg-red-500/10 rounded-xl transition-all uppercase tracking-[0.2em]">
            <Icons.LogOut size={16} /> {isSidebarOpen && "Shutdown Access"}
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-20 border-b border-slate-800 bg-slate-950/50 backdrop-blur-xl flex items-center justify-between px-8 sticky top-0 z-40 transition-colors">
           <div className="flex items-center gap-4">
              <button onClick={() => setSidebarOpen(!isSidebarOpen)} className="p-2 text-slate-500 hover:text-white transition-colors">
                <Icons.PanelLeft size={20} />
              </button>
              <div className="h-4 w-px bg-slate-800"></div>
              <h2 className="text-xl font-bold text-white font-serif-sc tracking-widest uppercase">
                {activeView === 'dashboard' ? 'Control Panel' : activeView.replace('-', ' ')}
              </h2>
           </div>

           <div className="flex items-center gap-8">
              <div className="hidden md:flex items-center gap-3 bg-slate-900 border border-slate-800 px-4 py-2 rounded-full">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_#10b981]"></div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Core Engine: Stable</span>
              </div>

              <div className="flex items-center gap-4">
                 <div className="text-right">
                    <div className="text-xs font-bold text-white uppercase tracking-wider">{user.name}</div>
                    <div className="text-[10px] text-blue-500 font-bold uppercase tracking-tighter">Root Privileges</div>
                 </div>
                 <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center border border-blue-400/20 shadow-lg">
                    <Icons.User size={20} className="text-white" />
                 </div>
              </div>
           </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar bg-[radial-gradient(circle_at_top_right,#1e293b,transparent_500px)]">
           {activeView === 'dashboard' && <DashboardHome />}
           {activeView === 'models' && <ModelConfig />}
           {activeView === 'stats' && <UsageStats />}
           {activeView === 'knowledge' && <KnowledgeBase />}
        </div>
      </main>
    </div>
  );
};

// --- 工具组件 ---

const AdminNavItem = ({ icon: Icon, label, active, onClick, minimized }: any) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-4 p-3 rounded-xl transition-all group relative overflow-hidden ${
      active 
        ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/40' 
        : 'text-slate-500 hover:bg-white/5 hover:text-white'
    }`}
  >
    {active && <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-100%] animate-shine"></div>}
    <Icon size={20} className={active ? 'text-white' : 'group-hover:text-blue-400 transition-colors'} />
    {!minimized && <span className="text-[10px] font-bold uppercase tracking-widest whitespace-nowrap">{label}</span>}
  </button>
);

const StatCard = ({ label, value, trend, icon: Icon, color }: any) => (
  <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl shadow-sm hover:border-blue-500/30 transition-all group relative overflow-hidden">
    <div className="absolute top-0 right-0 w-20 h-20 bg-blue-500/5 rounded-full -mr-10 -mt-10 group-hover:scale-110 transition-transform"></div>
    <div className="flex justify-between items-start mb-4">
       <div className={`p-2.5 rounded-lg bg-slate-950 border border-slate-800 ${color}`}>
         <Icon size={18} />
       </div>
       <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${trend.includes('+') ? 'bg-emerald-500/10 text-emerald-500' : 'bg-slate-800 text-slate-500'}`}>
         {trend}
       </span>
    </div>
    <div className="text-xl font-bold text-white mb-1 font-mono tracking-tighter">{value}</div>
    <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">{label}</div>
  </div>
);

const LogLine = ({ time, type, msg }: any) => (
  <div className="flex items-center gap-3 p-1.5 hover:bg-white/5 rounded text-[10px] transition-colors group">
    <span className="text-slate-600 font-bold">{time}</span>
    <span className={`px-1.5 py-0.5 rounded w-16 text-center font-bold tracking-tighter ${
      type === 'WARN' ? 'text-yellow-500 bg-yellow-500/10' : 
      type === 'AUTH' ? 'text-purple-500 bg-purple-500/10' :
      type === 'SUCCESS' ? 'text-emerald-500 bg-emerald-500/10' : 'text-blue-500 bg-blue-500/10'
    }`}>{type}</span>
    <span className="text-slate-400 group-hover:text-slate-200 transition-colors truncate">{msg}</span>
  </div>
);

const UsageBar = ({ label, percent, color, val }: any) => (
  <div className="space-y-2">
     <div className="flex justify-between text-[10px] font-bold uppercase">
        <span className="text-slate-400">{label}</span>
        <span className="text-white font-mono">{val}</span>
     </div>
     <div className="h-1.5 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-800/50">
        <div className={`h-full ${color} transition-all duration-1000 shadow-[0_0_10px_currentColor]`} style={{ width: `${percent}%` }}></div>
     </div>
  </div>
);

const KBFolder = ({ name, docs, size, status, date, active = false }: any) => (
  <div className={`bg-slate-900/50 border p-6 rounded-2xl hover:shadow-xl transition-all group cursor-pointer ${active ? 'border-blue-500 shadow-blue-500/10' : 'border-slate-800 hover:border-blue-500/30'}`}>
     <div className="flex justify-between items-start mb-6">
        <div className={`p-3 rounded-xl bg-slate-950 border border-slate-800 ${active ? 'text-blue-500' : 'text-slate-500 group-hover:text-blue-400'}`}>
          <Icons.FileText size={20} />
        </div>
        <span className={`text-[9px] font-bold px-2 py-0.5 rounded ${status === 'Syncing...' ? 'bg-blue-500 text-white animate-pulse' : 'bg-slate-800 text-slate-400'}`}>
          {status}
        </span>
     </div>
     <h4 className="text-xs font-bold text-white mb-2 uppercase tracking-wider">{name}</h4>
     <div className="flex justify-between items-center text-[9px] text-slate-600 font-bold uppercase">
        <div className="flex gap-3">
          <span>{docs} Files</span>
          <span>{size}</span>
        </div>
        <span>{date}</span>
     </div>
  </div>
);

export default AdminPortal;