import React, { useState, useEffect, useLayoutEffect, useRef } from 'react';
import { User, ChatMessage, AVAILABLE_MODELS, AIModelConfig } from '../../types';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';
import { createProfessionalChat, analyzeMedicalReport } from '../../services/geminiService';
import { Chat } from "@google/genai";

interface ProPortalProps {
  user: User;
  onLogout: () => void;
}

interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  lastModified: Date;
}

// Mock Data for Patients (Used in Patients Tab)
const RECENT_PATIENTS = [
  { id: 1, name: 'Zhang Wei', age: 45, gender: 'Male', condition: 'Hypertension Stage II', date: '2023-10-24', status: 'Stable', avatarColor: 'bg-tcm-lightGreen' },
  { id: 2, name: 'Li Xiuying', age: 62, gender: 'Female', condition: 'Type 2 Diabetes', date: '2023-10-25', status: 'Monitoring', avatarColor: 'bg-tcm-gold' },
  { id: 3, name: 'Wang Qiang', age: 28, gender: 'Male', condition: 'Acute URI', date: '2023-10-26', status: 'Recovering', avatarColor: 'bg-blue-500' },
  { id: 4, name: 'Chen Hui', age: 35, gender: 'Female', condition: 'Migraine', date: '2023-10-27', status: 'Stable', avatarColor: 'bg-purple-500' },
  { id: 5, name: 'Liu Yang', age: 50, gender: 'Male', condition: 'Gastritis', date: '2023-10-28', status: 'Critical', avatarColor: 'bg-red-500' },
  { id: 6, name: 'Zhao Min', age: 41, gender: 'Female', condition: 'Insomnia', date: '2023-10-29', status: 'Stable', avatarColor: 'bg-indigo-500' },
  { id: 7, name: 'Sun Lei', age: 55, gender: 'Male', condition: 'Arthritis', date: '2023-10-30', status: 'Monitoring', avatarColor: 'bg-orange-500' },
];

// Helper to group sessions by date
const groupSessionsByDate = (sessions: ChatSession[]) => {
  const groups: { [key: string]: ChatSession[] } = {
    'Today': [],
    'Yesterday': [],
    'Previous 7 Days': [],
    'Older': []
  };

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const lastWeek = new Date(today);
  lastWeek.setDate(lastWeek.getDate() - 7);

  sessions.forEach(session => {
    const date = new Date(session.lastModified);
    const sessionDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    if (sessionDate.getTime() === today.getTime()) {
      groups['Today'].push(session);
    } else if (sessionDate.getTime() === yesterday.getTime()) {
      groups['Yesterday'].push(session);
    } else if (sessionDate > lastWeek) {
      groups['Previous 7 Days'].push(session);
    } else {
      groups['Older'].push(session);
    }
  });

  return groups;
};

const ProfessionalPortal: React.FC<ProPortalProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('ai-diagnosis');
  const [selectedPatient, setSelectedPatient] = useState<number | null>(null);
  const [selectedModel, setSelectedModel] = useState<AIModelConfig>(AVAILABLE_MODELS[1]); // Default to Pro

  // Chat Sessions State
  const [sessions, setSessions] = useState<ChatSession[]>([
    {
      id: 'init-1',
      title: 'General Consultation  ',
      messages: [{
        id: 'init',
        role: 'model',
        text: `Hello, Dr. ${user.name.split(' ').pop()}. The Clinical Decision Support System is ready.`,
        timestamp: new Date()
      }],
      lastModified: new Date()
    },
    {
      id: 'hist-1',
      title: 'Hypertension Case Analysis',
      messages: [],
      lastModified: new Date(Date.now() - 86400000) // Yesterday
    },
    {
      id: 'hist-2',
      title: 'Pediatric Fever Protocol',
      messages: [],
      lastModified: new Date(Date.now() - 172800000) // 2 days ago
    }
  ]);
  const [activeSessionId, setActiveSessionId] = useState<string>('init-1');
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  // Derived Active Session
  const activeSession = sessions.find(s => s.id === activeSessionId) || sessions[0];

  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false); // Default collapsed as requested
  const [showModelSelector, setShowModelSelector] = useState(false);

  // New Toggles
  const [enableDeepThink, setEnableDeepThink] = useState(false);
  const [enableWebSearch, setEnableWebSearch] = useState(false);

  // Theme State
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme_professional');
    return saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  const chatRef = useRef<Chat | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- Effects ---

  // Use layout effect to prevent flash of wrong theme when switching portals
  useLayoutEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme_professional', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme_professional', 'light');
    }
  }, [isDarkMode]);

  useEffect(() => {
    // Initialize Professional Chat with selected model whenever session or model changes
    chatRef.current = createProfessionalChat(selectedModel.id);
  }, [activeSessionId, selectedModel]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeSession.messages]);

  // --- Handlers: Session Management ---

  const handleNewChat = () => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: 'New Clinical Case',
      messages: [{
        id: Date.now().toString(),
        role: 'model',
        text: `Hello, Dr. ${user.name.split(' ').pop()}. New session started using ${selectedModel.name}.`,
        timestamp: new Date()
      }],
      lastModified: new Date()
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
  };

  const handleDeleteSession = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    const newSessions = sessions.filter(s => s.id !== id);
    setSessions(newSessions);
    if (activeSessionId === id && newSessions.length > 0) {
      setActiveSessionId(newSessions[0].id);
    } else if (newSessions.length === 0) {
      handleNewChat();
    }
  };

  const startRenameSession = (e: React.MouseEvent, session: ChatSession) => {
    e.stopPropagation();
    setEditingSessionId(session.id);
    setEditTitle(session.title);
  };

  const saveRenameSession = () => {
    if (editingSessionId) {
      setSessions(prev => prev.map(s => s.id === editingSessionId ? { ...s, title: editTitle } : s));
      setEditingSessionId(null);
    }
  };

  const updateSessionMessages = (sessionId: string, newMessages: ChatMessage[]) => {
    setSessions(prev => prev.map(s => s.id === sessionId ? { ...s, messages: newMessages, lastModified: new Date() } : s));
  };

  const groupedSessions = groupSessionsByDate(sessions);

  // --- Handlers: Chat ---

  const handleSendMessage = async (text: string = inputValue) => {
    if (!text.trim() || !chatRef.current) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      text: text,
      timestamp: new Date()
    };

    const updatedMessages = [...activeSession.messages, userMsg];
    updateSessionMessages(activeSessionId, updatedMessages);

    // Auto-rename if it's the first user message
    if (activeSession.messages.length <= 1 && activeSession.title === 'New Clinical Case') {
       const newTitle = text.slice(0, 25) + (text.length > 25 ? '...' : '');
       setSessions(prev => prev.map(s => s.id === activeSessionId ? { ...s, title: newTitle } : s));
    }

    setInputValue('');
    setIsLoading(true);

    try {
      const config: any = {};
      if (enableDeepThink) config.thinkingConfig = { thinkingBudget: 1024 };
      if (enableWebSearch) config.tools = [{ googleSearch: {} }];

      const result = await chatRef.current.sendMessage({
        message: text,
        config: Object.keys(config).length > 0 ? config : undefined
      });

      const modelMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'model',
        text: result.text || "No response generated.",
        timestamp: new Date()
      };
      updateSessionMessages(activeSessionId, [...updatedMessages, modelMsg]);
    } catch (e) {
      updateSessionMessages(activeSessionId, [...updatedMessages, {
        id: Date.now().toString(),
        role: 'model',
        text: "System Error: Unable to connect to diagnostic engine.",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action: string) => {
    let prompt = "";
    switch(action) {
      case 'generate_case': prompt = "Help me structure a standard medical case record for a new patient."; break;
      case 'drug_check': prompt = "I need to check for drug interactions. Please list the medications."; break;
      case 'lit_search': prompt = "Search for recent literature regarding: "; break;
    }
    setInputValue(prompt);
  };

  const handleVoiceInput = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-US';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setInputValue(prev => prev + " (Listening...)");
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(prev => prev.replace(" (Listening...)", "") + " " + transcript);
      };

      recognition.onerror = () => {
        setInputValue(prev => prev.replace(" (Listening...)", ""));
      };

      recognition.start();
    } else {
      alert("Speech recognition not supported.");
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setInputValue(prev => prev + ` [Attached: ${e.target.files![0].name}] `);
    }
  };

  // --- Sub-Views for Navigation ---

  const PatientsView = () => (
    <div className="w-full h-full p-8 bg-gray-50 dark:bg-gray-900 overflow-y-auto animate-in fade-in slide-in-from-bottom-4 transition-colors">
      <div className="flex justify-between items-center mb-8">
        <div>
           <h2 className="text-2xl font-bold text-tcm-darkGreen dark:text-tcm-cream font-serif-sc">诊疗管理</h2>
           <p className="text-gray-500 dark:text-gray-400 text-sm">当前病例和患者历史</p>
        </div>
        <button className="bg-tcm-darkGreen dark:bg-tcm-lightGreen text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-green-900 transition-colors">
          <Icons.ShieldPlus size={18} /> 添加新病例 
        </button>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden transition-colors">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 dark:bg-gray-700/50 border-b border-gray-100 dark:border-gray-700 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              <th className="p-4">患者</th>
              <th className="p-4">年龄/性别</th>
              <th className="p-4">诊断</th>
              <th className="p-4">最后访问</th>
              <th className="p-4">状态</th>
              <th className="p-4">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
            {RECENT_PATIENTS.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors group cursor-pointer" onClick={() => { setSelectedPatient(p.id); setActiveTab('ai-diagnosis'); }}>
                <td className="p-4 flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full ${p.avatarColor} text-white flex items-center justify-center font-bold text-xs`}>{p.name.charAt(0)}</div>
                  <span className="font-bold text-gray-700 dark:text-gray-200">{p.name}</span>
                </td>
                <td className="p-4 text-sm text-gray-600 dark:text-gray-400">{p.age} / {p.gender}</td>
                <td className="p-4 text-sm text-tcm-darkGreen dark:text-tcm-lightGreen font-medium">{p.condition}</td>
                <td className="p-4 text-sm text-gray-500 dark:text-gray-400">{p.date}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-bold ${p.status === 'Critical' ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400' : p.status === 'Stable' ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400'}`}>
                    {p.status}
                  </span>
                </td>
                <td className="p-4 text-gray-400 group-hover:text-tcm-gold transition-colors">
                  <Icons.ChevronRight size={18} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const ReportAnalysisView = () => {
    const [reportText, setReportText] = useState('');
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [base64Data, setBase64Data] = useState<string | null>(null);
    const [mimeType, setMimeType] = useState<string | null>(null);
    const [analysisResult, setAnalysisResult] = useState<string | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    const handleReportUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        setPreviewUrl(URL.createObjectURL(file));
        setMimeType(file.type);
        const reader = new FileReader();
        reader.onload = (ev) => {
          if (ev.target?.result) {
            setBase64Data(ev.target.result as string);
          }
        };
        reader.readAsDataURL(file);
      }
    };

    const runAnalysis = async () => {
      setIsAnalyzing(true);
      setAnalysisResult(null);
      // Clean base64 string if present
      const cleanBase64 = base64Data ? base64Data.split(',')[1] : undefined;

      const result = await analyzeMedicalReport(reportText, cleanBase64, mimeType || undefined);
      setAnalysisResult(result);
      setIsAnalyzing(false);
    };

    return (
      <div className="w-full h-full p-6 bg-gray-50 dark:bg-gray-900 overflow-y-auto animate-in fade-in slide-in-from-bottom-4 flex flex-col md:flex-row gap-6 transition-colors">

        {/* Left Column: Input */}
        <div className="w-full md:w-1/3 flex flex-col gap-4">
          <h2 className="text-2xl font-bold text-tcm-darkGreen dark:text-tcm-cream font-serif-sc mb-2">报告上传</h2>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors">
             <div className="mb-4">
               <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">上传报告</label>
               <div className="relative border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                 <input type="file" onChange={handleReportUpload} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" accept="image/*" />
                 {previewUrl ? (
                   <img src={previewUrl} alt="Preview" className="max-h-48 mx-auto rounded shadow-sm" />
                 ) : (
                   <div className="text-gray-400 flex flex-col items-center">
                     <Icons.UploadCloud size={32} className="mb-2"/>
                     <span className="text-sm">点击上传报告</span>
                   </div>
                 )}
               </div>
             </div>

             <div className="mb-4">
               <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">临床笔记（可选）</label>
               <textarea
                 value={reportText}
                 onChange={(e) => setReportText(e.target.value)}
                 className="w-full p-3 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg text-sm focus:ring-2 focus:ring-tcm-lightGreen focus:border-transparent min-h-[100px]"
                 placeholder="Enter any additional context or copy-paste text report here..."
               />
             </div>

             <button
               onClick={runAnalysis}
               disabled={isAnalyzing || (!reportText && !base64Data)}
               className="w-full bg-tcm-darkGreen dark:bg-tcm-lightGreen text-white py-3 rounded-lg font-bold shadow-md hover:bg-green-900 dark:hover:bg-green-700 transition-all disabled:opacity-50 disabled:shadow-none flex items-center justify-center gap-2"
             >
               {isAnalyzing ? (
                 <>
                   <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                   Analyzing...
                 </>
               ) : (
                 <>
                   <Icons.Zap size={18} /> Run AI Analysis
                 </>
               )}
             </button>
          </div>
        </div>

        {/* Right Column: Results */}
        <div className="w-full md:w-2/3 flex flex-col">
          <h2 className="text-2xl font-bold text-tcm-darkGreen dark:text-tcm-cream font-serif-sc mb-6">分析结果</h2>

          <div className="flex-1 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-8 overflow-y-auto transition-colors">
             {analysisResult ? (
               <div className="prose prose-sm max-w-none dark:prose-invert prose-headings:text-tcm-darkGreen dark:prose-headings:text-tcm-lightGreen prose-p:text-gray-700 dark:prose-p:text-gray-300 prose-strong:text-tcm-darkGreen dark:prose-strong:text-tcm-gold">
                 {analysisResult.split('\n').map((line, i) => {
                   if (line.startsWith('**') || line.startsWith('#')) return <h3 key={i} className="text-lg font-bold mt-4 mb-2">{line.replace(/[#*]/g, '')}</h3>;
                   if (line.trim().startsWith('-')) return <li key={i} className="ml-4">{line.substring(1)}</li>;
                   return <p key={i} className="mb-2">{line}</p>;
                 })}
               </div>
             ) : (
               <div className="h-full flex flex-col items-center justify-center text-gray-300 dark:text-gray-600">
                 <Icons.FileText size={64} className="mb-4 opacity-50"/>
                 <p className="text-lg font-medium">No analysis generated yet.</p>
                 <p className="text-sm">Upload a report to begin.</p>
               </div>
             )}
          </div>
        </div>
      </div>
    );
  };

  const RecordsView = () => (
    <div className="w-full h-full p-8 bg-gray-50 dark:bg-gray-900 overflow-y-auto animate-in fade-in slide-in-from-bottom-4 transition-colors">
      <h2 className="text-2xl font-bold text-tcm-darkGreen dark:text-tcm-cream font-serif-sc mb-6">电子医疗记录</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1,2,3,4,5,6].map(i => (
          <div key={i} className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all cursor-pointer group hover:border-tcm-gold/50">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg group-hover:bg-tcm-gold group-hover:text-white transition-colors">
                <Icons.FileText size={24} />
              </div>
              <button className="text-gray-300 hover:text-gray-500 dark:hover:text-gray-200"><Icons.Menu size={16}/></button>
            </div>
            <h3 className="font-bold text-gray-800 dark:text-gray-200 mb-1">病例记录  #{202300 + i}</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">更新于 2 小时 前</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">2 小时 前更新</p>
            <div className="flex items-center gap-2 text-xs font-medium text-gray-400 group-hover:text-tcm-darkGreen dark:group-hover:text-tcm-lightGreen">
              <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">Cardiology </span>
              <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">Inpatient</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const ResearchView = () => (
    <div className="w-full h-full p-8 bg-gray-50 dark:bg-gray-900 overflow-y-auto animate-in fade-in slide-in-from-bottom-4 transition-colors">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold text-tcm-darkGreen dark:text-tcm-cream font-serif-sc mb-2">Medical Knowledge Graph</h2>
        <p className="text-gray-500 dark:text-gray-400 mb-8">Search global medical databases with AI synthesis.</p>

        <div className="relative mb-10">
          <input type="text" placeholder="Search for symptoms, drug interactions, or recent papers..." className="w-full p-4 pl-12 rounded-full border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen shadow-sm" />
          <Icons.Globe className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <button className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-tcm-darkGreen dark:bg-tcm-lightGreen text-white px-6 py-2 rounded-full hover:bg-green-900 transition-colors">Search</button>
        </div>

        <div className="space-y-6">
          <h3 className="font-bold text-gray-800 dark:text-gray-200 border-b dark:border-gray-700 pb-2">Latest relevant papers</h3>
          {[1, 2, 3].map(i => (
             <div key={i} className="bg-white dark:bg-gray-800 p-5 rounded-lg border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow">
               <span className="text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-2 py-0.5 rounded mb-2 inline-block">NEJM</span>
               <h4 className="font-bold text-lg text-gray-900 dark:text-gray-100 mb-2">Efficacy of Integrative Medicine in Chronic Hypertension Management</h4>
               <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed mb-3">
                 A randomized control trial demonstrating significant improvement in patient outcomes when combining standard protocols with...
               </p>
               <div className="flex gap-4 text-xs text-gray-400">
                 <span>Oct 24, 2023</span>
                 <span>Cited by 45</span>
                 <button className="text-tcm-lightGreen hover:underline ml-auto font-bold">Read Summary</button>
               </div>
             </div>
          ))}
        </div>
      </div>
    </div>
  );

  const SettingsView = () => (
    <div className="w-full h-full p-8 bg-gray-50 dark:bg-gray-900 overflow-y-auto animate-in fade-in slide-in-from-bottom-4 transition-colors">
       <div className="max-w-2xl">
         <h2 className="text-2xl font-bold text-tcm-darkGreen dark:text-tcm-cream font-serif-sc mb-8">System Settings</h2>

         <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden mb-6 transition-colors">
           <div className="p-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50 font-bold text-sm text-gray-500 dark:text-gray-400 uppercase">General</div>
           <div className="p-6 space-y-6">
             <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-gray-800 dark:text-gray-200">Dark Mode</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Reduce eye strain during night shifts</div>
                </div>
                <button
                  onClick={() => setIsDarkMode(!isDarkMode)}
                  className={`w-12 h-6 rounded-full relative transition-colors duration-300 ${isDarkMode ? 'bg-tcm-lightGreen' : 'bg-gray-200'}`}
                >
                  <div className={`w-4 h-4 bg-white rounded-full absolute top-1 shadow-sm transition-transform duration-300 ${isDarkMode ? 'left-7' : 'left-1'}`}></div>
                </button>
             </div>
             <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-gray-800 dark:text-gray-200">Compact View</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Show more data density in tables</div>
                </div>
                <div className="w-12 h-6 bg-tcm-lightGreen rounded-full relative cursor-pointer"><div className="w-4 h-4 bg-white rounded-full absolute top-1 right-1 shadow-sm"></div></div>
             </div>
           </div>
         </div>

         <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden transition-colors">
           <div className="p-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50 font-bold text-sm text-gray-500 dark:text-gray-400 uppercase">AI Configuration</div>
           <div className="p-6 space-y-6">
             <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-gray-800 dark:text-gray-200">Model Temperature</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Adjust creativity vs precision (0.0 - 1.0)</div>
                </div>
                <input type="range" className="w-32" />
             </div>
             <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-gray-800 dark:text-gray-200">Auto-Suggest Treatments</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Automatically append TCM protocols</div>
                </div>
                <div className="w-12 h-6 bg-tcm-lightGreen rounded-full relative cursor-pointer"><div className="w-4 h-4 bg-white rounded-full absolute top-1 right-1 shadow-sm"></div></div>
             </div>
           </div>
         </div>
       </div>
    </div>
  );

  return (
    <div className="w-full h-screen flex bg-gray-50 dark:bg-gray-900 font-sans overflow-hidden transition-colors duration-500">

      {/* 1. Navigation Sidebar (Left) */}
      <aside className="w-64 bg-tcm-darkGreen dark:bg-black/50 flex flex-col text-white flex-shrink-0 z-20 shadow-xl transition-all duration-300">
        {/* Branding */}
        <div className="h-16 flex items-center px-6 border-b border-white/10 bg-black/10">
           <BrandLogo size="md" variant="dark" />
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 py-6 px-3 space-y-2 overflow-y-auto">
          <NavItem
            icon={Icons.BrainCircuit}
            label="AI诊断"
            isActive={activeTab === 'ai-diagnosis'}
            onClick={() => setActiveTab('ai-diagnosis')}
          />
          <NavItem
            icon={Icons.User}
            label="患者管理"
            isActive={activeTab === 'patients'}
            onClick={() => setActiveTab('patients')}
          />
          <NavItem
             icon={Icons.FileText}
             label="报告分析"
             isActive={activeTab === 'report-analysis'}
             onClick={() => setActiveTab('report-analysis')}
          />
          <NavItem
            icon={Icons.MessageSquare}
            label="电子记录"
            isActive={activeTab === 'records'}
            onClick={() => setActiveTab('records')}
          />
          <NavItem
            icon={Icons.Globe}
            label="医学研究"
            isActive={activeTab === 'research'}
            onClick={() => setActiveTab('research')}
          />
          <NavItem
            icon={Icons.Settings}
            label="系统设置"
            isActive={activeTab === 'settings'}
            onClick={() => setActiveTab('settings')}
          />
        </nav>

        {/* User Profile (Bottom) */}
        <div className="p-4 bg-black/20 border-t border-white/10">
          <div className="flex items-center gap-3 mb-3">
            <img src={user.avatar} className="w-10 h-10 rounded-full border-2 border-tcm-gold object-cover" alt="Dr" />
            <div className="overflow-hidden">
              <p className="text-sm font-bold text-white truncate">{user.name}</p>
              <p className="text-xs text-tcm-gold/80 truncate">Attending Physician</p>
            </div>
          </div>
          <button onClick={onLogout} className="w-full flex items-center justify-center gap-2 py-2 text-xs text-red-300 hover:text-white hover:bg-white/10 rounded transition-colors">
            <Icons.LogOut size={14} /> Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area - Conditional Rendering */}
      {activeTab === 'ai-diagnosis' ? (
        <div className="flex-1 flex overflow-hidden relative">

          {/* 2. Collapsible History Sidebar */}
           <div className={`bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col transition-all duration-300 ease-in-out ${showHistory ? 'w-64 opacity-100' : 'w-0 opacity-0 overflow-hidden'}`}>
             <div className="p-4 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
                <span className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">Chat History</span>
                <button
                  onClick={() => setShowHistory(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"
                >
                  <Icons.PanelLeft size={18} />
                </button>
             </div>

             <div className="p-3 flex-1 flex flex-col overflow-hidden">
               <button
                 onClick={handleNewChat}
                 className="w-full flex items-center gap-2 px-3 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-200 hover:border-tcm-lightGreen hover:text-tcm-lightGreen transition-colors shadow-sm mb-4 whitespace-nowrap shrink-0"
               >
                 <Icons.MessageSquare size={16} /> New Chat
               </button>

               <div className="flex-1 overflow-y-auto custom-scrollbar space-y-4">
                 {Object.entries(groupedSessions).map(([group, groupSessions]) => (
                   groupSessions.length > 0 && (
                     <div key={group} className="animate-in fade-in">
                       <div className="px-2 py-1 text-[10px] font-bold text-gray-400 uppercase mt-2 mb-1">{group}</div>
                       {groupSessions.map(session => (
                          <div
                            key={session.id}
                            onClick={() => setActiveSessionId(session.id)}
                            className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                              activeSessionId === session.id 
                                ? 'bg-tcm-lightGreen/10 dark:bg-tcm-lightGreen/10 text-tcm-darkGreen dark:text-tcm-lightGreen font-medium' 
                                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                            }`}
                          >
                            <div className="flex-1 min-w-0">
                              {editingSessionId === session.id ? (
                                <input
                                  type="text"
                                  value={editTitle}
                                  onChange={(e) => setEditTitle(e.target.value)}
                                  onBlur={saveRenameSession}
                                  onKeyDown={(e) => e.key === 'Enter' && saveRenameSession()}
                                  autoFocus
                                  className="w-full bg-transparent border-b border-gray-400 focus:outline-none text-sm"
                                  onClick={(e) => e.stopPropagation()}
                                />
                              ) : (
                                <div className="text-sm truncate">
                                  {session.title}
                                </div>
                              )}
                            </div>

                            {/* Hover Actions */}
                            <div className={`flex items-center ${activeSessionId === session.id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'} transition-opacity`}>
                               <button onClick={(e) => startRenameSession(e, session)} className="p-1 hover:bg-black/10 dark:hover:bg-white/10 rounded">
                                 <Icons.Edit3 size={12} />
                               </button>
                               <button onClick={(e) => handleDeleteSession(e, session.id)} className="p-1 hover:bg-black/10 dark:hover:bg-white/10 rounded hover:text-red-500 ml-1">
                                 <Icons.Trash2 size={12} />
                               </button>
                            </div>
                          </div>
                       ))}
                     </div>
                   )
                 ))}
               </div>
             </div>
           </div>

          {/* 3. Main Workspace (Right) - Chat Interface */}
          <main className="flex-1 flex flex-col bg-white dark:bg-gray-800 min-w-0 relative transition-colors">
            {/* Header */}
            <header className="h-16 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between px-6 bg-white dark:bg-gray-800 z-10 transition-colors">
              <div className="flex items-center gap-3">
                 {!showHistory && (
                   <button
                     onClick={() => setShowHistory(true)}
                     className="p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                     title="Show History"
                   >
                     <Icons.PanelLeft size={20} />
                   </button>
                 )}

                 <div className="p-2 bg-tcm-darkGreen/5 dark:bg-white/10 rounded-lg text-tcm-darkGreen dark:text-tcm-lightGreen">
                   <Icons.BrainCircuit size={20} />
                 </div>
                 <div className="flex flex-col">
                   <div className="flex items-center gap-2">
                     <h1 className="text-sm font-bold text-gray-800 dark:text-gray-100">
                       AI Clinical Assistant
                     </h1>

                     {/* Custom Model Selector */}
                     <div className="relative">
                        <button
                          onClick={() => setShowModelSelector(!showModelSelector)}
                          className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold transition-colors border ${
                            showModelSelector 
                              ? 'bg-tcm-lightGreen/10 border-tcm-lightGreen text-tcm-darkGreen dark:text-tcm-lightGreen' 
                              : 'bg-blue-50 dark:bg-blue-900/20 border-blue-100 dark:border-blue-800 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/40'
                          }`}
                        >
                            <span>{selectedModel.name}</span>
                            <Icons.ChevronDown size={10} className={`transition-transform duration-300 ${showModelSelector ? 'rotate-180' : ''}`} />
                        </button>

                        {/* Custom Dropdown Menu */}
                        {showModelSelector && (
                          <>
                            <div className="fixed inset-0 z-40" onClick={() => setShowModelSelector(false)}></div>
                            <div className="absolute top-full left-0 mt-2 w-52 bg-white dark:bg-[#1e1e1e] border border-gray-200 dark:border-gray-700 rounded-xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 origin-top-left">
                              <div className="p-1.5 space-y-0.5">
                                <div className="px-2 py-1.5 text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Select Model</div>
                                {AVAILABLE_MODELS.map(model => (
                                  <button
                                    key={model.id}
                                    onClick={() => {
                                      setSelectedModel(model);
                                      setShowModelSelector(false);
                                    }}
                                    className={`w-full text-left p-2 rounded-lg flex items-start gap-2 transition-colors ${
                                      selectedModel.id === model.id 
                                        ? 'bg-tcm-lightGreen/10 border border-tcm-lightGreen/20' 
                                        : 'hover:bg-gray-50 dark:hover:bg-white/5 border border-transparent'
                                    }`}
                                  >
                                    <div className={`mt-0.5 p-1 rounded-md flex-shrink-0 ${
                                      selectedModel.id === model.id 
                                        ? 'bg-tcm-lightGreen text-white' 
                                        : 'bg-gray-100 dark:bg-white/10 text-gray-500 dark:text-gray-400'
                                    }`}>
                                      <Icons.Zap size={12} />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                      <div className={`text-xs font-bold truncate ${
                                        selectedModel.id === model.id 
                                          ? 'text-tcm-darkGreen dark:text-tcm-lightGreen' 
                                          : 'text-gray-700 dark:text-gray-200'
                                      }`}>
                                        {model.name}
                                      </div>
                                      <div className="text-[10px] text-gray-500 dark:text-gray-400 mt-0 truncate">
                                        {model.description}
                                      </div>
                                    </div>
                                    {selectedModel.id === model.id && (
                                      <Icons.Check size={14} className="text-tcm-lightGreen mt-1" />
                                    )}
                                  </button>
                                ))}
                              </div>
                            </div>
                          </>
                        )}
                     </div>
                   </div>
                   <p className="text-xs text-gray-400 dark:text-gray-500">Context: {selectedPatient ? `Patient #${selectedPatient}` : 'General Session'}</p>
                 </div>
              </div>

              {/* Quick Actions (Top Right) */}
              <div className="flex items-center gap-2">
                <QuickActionButton label="Generate Case" onClick={() => handleQuickAction('generate_case')} />
                <QuickActionButton label="Drug Check" onClick={() => handleQuickAction('drug_check')} />
                <QuickActionButton label="Lit Search" onClick={() => handleQuickAction('lit_search')} />
              </div>
            </header>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-6 bg-[#f8f9fa] dark:bg-[#121825] transition-colors">
              <div className="max-w-4xl mx-auto w-full space-y-6">
                {activeSession.messages.map((msg) => (
                  <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2`}>
                    {msg.role === 'model' && (
                      <div className="w-8 h-8 rounded-full bg-tcm-darkGreen flex items-center justify-center text-white mr-3 shadow-sm flex-shrink-0 mt-1">
                        <Icons.Bot size={16} />
                      </div>
                    )}

                    <div className={`max-w-[80%] p-2 text-sm leading-relaxed text-gray-800 dark:text-gray-100`}>
                       {msg.role === 'model' ? (
                         <div className="prose prose-sm max-w-none dark:prose-invert prose-p:my-1 prose-headings:text-tcm-darkGreen dark:prose-headings:text-tcm-lightGreen prose-strong:text-tcm-darkGreen dark:prose-strong:text-tcm-gold">
                           {/* Naive markdown-ish rendering for demo */}
                           {msg.text.split('\n').map((line, i) => <p key={i}>{line}</p>)}
                         </div>
                       ) : (
                         msg.text
                       )}
                    </div>

                    {msg.role === 'user' && (
                       <img src={user.avatar} className="w-8 h-8 rounded-full ml-3 border border-gray-200 flex-shrink-0 mt-1" alt="User" />
                    )}
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                     <div className="w-8 h-8 rounded-full bg-tcm-darkGreen flex items-center justify-center text-white mr-3 shadow-sm flex-shrink-0">
                        <Icons.Bot size={16} />
                     </div>
                     <div className="bg-white dark:bg-gray-700 px-4 py-3 rounded-2xl rounded-bl-none border border-gray-100 dark:border-gray-600 shadow-sm flex items-center gap-2">
                       <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
                       <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-75"></span>
                       <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-150"></span>
                     </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 shadow-[0_-5px_20px_rgba(0,0,0,0.02)] z-10 pb-6 transition-colors">
              <div className="max-w-4xl mx-auto w-full">

                 {/* Toolbar: Thinking & Search - Moved above input capsule */}
                 <div className="flex items-center gap-3 mb-2 px-1">
                    <button
                      onClick={() => setEnableDeepThink(!enableDeepThink)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${enableDeepThink ? 'bg-indigo-50 dark:bg-indigo-900/30 border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 shadow-sm' : 'bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600'}`}
                    >
                      <Icons.BrainCircuit size={14} className={enableDeepThink ? "animate-pulse" : ""} />
                      Deep Thinking {enableDeepThink && <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full ml-1"></span>}
                    </button>

                    <button
                      onClick={() => setEnableWebSearch(!enableWebSearch)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${enableWebSearch ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300 shadow-sm' : 'bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600'}`}
                    >
                      <Icons.Globe size={14} />
                      Web Search {enableWebSearch && <span className="w-1.5 h-1.5 bg-blue-500 rounded-full ml-1"></span>}
                    </button>
                 </div>

                 {/* Input Capsule */}
                 <div className="relative flex items-end gap-2 bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-3xl p-2 transition-shadow focus-within:ring-2 focus-within:ring-tcm-lightGreen/20 focus-within:border-tcm-lightGreen/50 focus-within:bg-white dark:focus-within:bg-gray-700 focus-within:shadow-md">
                   <input type="file" multiple ref={fileInputRef} className="hidden" onChange={handleFileUpload} />
                   <button
                      onClick={() => fileInputRef.current?.click()}
                      className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-full hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                      title="Upload Reports/Images"
                   >
                     <Icons.Paperclip size={20} />
                   </button>
                   <button
                      onClick={handleVoiceInput}
                      className="p-2 text-gray-400 hover:text-tcm-darkGreen dark:hover:text-tcm-lightGreen rounded-full hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                      title="Voice Dictation"
                   >
                     <Icons.Mic size={20} />
                   </button>
                   <textarea
                     value={inputValue}
                     onChange={(e) => setInputValue(e.target.value)}
                     onKeyDown={(e) => {
                       if (e.key === 'Enter' && !e.shiftKey) {
                         e.preventDefault();
                         handleSendMessage();
                       }
                     }}
                     placeholder="Enter clinical question, upload results, or request differential diagnosis..."
                     className="flex-1 bg-transparent border-none focus:ring-0 focus:outline-none text-sm text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 resize-none max-h-32 py-2"
                     rows={1}
                     style={{minHeight: '24px'}}
                   />
                   <button
                     onClick={() => handleSendMessage()}
                     disabled={!inputValue.trim() || isLoading}
                     className="p-2 bg-tcm-darkGreen text-white rounded-full hover:bg-green-900 dark:hover:bg-green-700 disabled:opacity-50 disabled:hover:bg-tcm-darkGreen transition-colors shadow-sm"
                   >
                     <Icons.Send size={18} className={isLoading ? "animate-pulse" : ""} />
                   </button>
                 </div>
              </div>
              <p className="text-center text-[10px] text-gray-400 dark:text-gray-500 mt-2">
                AI-generated insights must be verified by a qualified physician.
              </p>
            </div>
          </main>
        </div>
      ) : (
        // Other Views Container
        <div className="flex-1 bg-white dark:bg-gray-800 overflow-hidden flex flex-col transition-colors">
          <header className="h-16 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between px-6 bg-white dark:bg-gray-800 z-10 shrink-0 transition-colors">
             <h2 className="text-lg font-bold text-gray-800 dark:text-gray-100 font-serif-sc flex items-center gap-2 capitalize">
               {activeTab.replace('-', ' ')}
             </h2>
             <div className="text-xs text-gray-400">Professional Workspace</div>
          </header>
          {activeTab === 'patients' && <PatientsView />}
          {activeTab === 'report-analysis' && <ReportAnalysisView />}
          {activeTab === 'records' && <RecordsView />}
          {activeTab === 'research' && <ResearchView />}
          {activeTab === 'settings' && <SettingsView />}
        </div>
      )}

    </div>
  );
};

// Helper Components
const NavItem = ({ icon: Icon, label, isActive, onClick }: { icon: any, label: string, isActive: boolean, onClick: () => void }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all group ${
      isActive 
        ? 'bg-tcm-lightGreen text-white shadow-md' 
        : 'text-gray-400 hover:bg-white/5 hover:text-white'
    }`}
  >
    <Icon size={18} className={isActive ? 'text-white' : 'text-gray-400 group-hover:text-tcm-gold transition-colors'} />
    <span className="text-sm font-medium">{label}</span>
  </button>
);

const QuickActionButton = ({ label, onClick }: { label: string, onClick: () => void }) => (
  <button
    onClick={onClick}
    className="px-3 py-1.5 text-xs font-medium text-tcm-lightGreen dark:text-tcm-lightGreen bg-tcm-lightGreen/10 dark:bg-tcm-lightGreen/20 border border-tcm-lightGreen/20 dark:border-tcm-lightGreen/30 rounded-full hover:bg-tcm-lightGreen hover:text-white dark:hover:bg-tcm-lightGreen dark:hover:text-white transition-all"
  >
    {label}
  </button>
);

export default ProfessionalPortal;