import React, { useState, useEffect, useRef } from 'react';
import { User, ChatMessage, AVAILABLE_MODELS, AIModelConfig } from '../../types/types';
import { Icons } from '../../components/common/Icons';
import { createProfessionalChat, analyzeMedicalReport } from '../../services/geminiService';
import { Chat } from "@google/genai";

interface ProPortalProps {
  user: User;
  onLogout: () => void;
}

// Mock Data for Patients (Used in Patients Tab)
const RECENT_PATIENTS = [
  { id: 1, name: '张伟', age: 45, gender: '男', condition: '高血压 Stage II', date: '2023-10-24', status: '稳定', avatarColor: 'bg-tcm-lightGreen ' },
  { id: 2, name: '李秀英', age: 62, gender: '女', condition: '2型糖尿病', date: '2023-10-25', status: '监测中', avatarColor: 'bg-tcm-gold' },
  { id: 3, name: '王强', age: 28, gender: '男', condition: '急性上呼吸道感染', date: '2023-10-26', status: '恢复中', avatarColor: 'bg-blue-500' },
  { id: 4, name: '陈慧', age: 35, gender: '女', condition: '偏头痛', date: '2023-10-27', status: '稳定', avatarColor: 'bg-purple-500' },
  { id: 5, name: '刘洋', age: 50, gender: '男', condition: '胃炎', date: '2023-10-28', status: '危急', avatarColor: 'bg-red-500' },
  { id: 6, name: '赵敏', age: 41, gender: '女', condition: '失眠', date: '2023-10-29', status: '稳定', avatarColor: 'bg-indigo-500' },
  { id: 7, name: '孙雷', age: 55, gender: '男', condition: '关节炎', date: '2023-10-30', status: '监测中', avatarColor: 'bg-orange-500' },
];

const MOCK_HISTORY = [
  { id: '1', title: '高血压病例分析', date: '今天' },
  { id: '2', title: '2型糖尿病复习', date: '昨天' },
  { id: '3', title: '儿科发热协议', date: '10月24日' },
  { id: '4', title: '药物相互作用检查', date: '10月22日' },
];

const ProfessionalPortal: React.FC<ProPortalProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('ai-diagnosis');
  const [selectedPatient, setSelectedPatient] = useState<number | null>(null);
  const [selectedModel, setSelectedModel] = useState<AIModelConfig>(AVAILABLE_MODELS[1]); // Default to Pro
  
  // Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(true);

  // New Toggles
  const [enableDeepThink, setEnableDeepThink] = useState(false);
  const [enableWebSearch, setEnableWebSearch] = useState(false);
  
  const chatRef = useRef<Chat | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Initialize Professional Chat with selected model
    chatRef.current = createProfessionalChat(selectedModel.id);
    setMessages([{
      id: 'init',
      role: 'model',
      text: `您好，${user.name}医生。临床决策支持系统已准备就绪，使用的是 ${selectedModel.name}。请提供病例详情或提出临床问题。`,
      timestamp: new Date()
    }]);
  }, [user.name, selectedModel]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (text: string = inputValue) => {
    if (!text.trim() || !chatRef.current) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      text: text,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
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
      setMessages(prev => [...prev, modelMsg]);
    } catch (e) {
      setMessages(prev => [...prev, {
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
    <div className="w-full h-full p-8 bg-gray-50 overflow-y-auto animate-in fade-in slide-in-from-bottom-4">
      <div className="flex justify-between items-center mb-8">
        <div>
           <h2 className="text-2xl font-bold text-tcm-darkGreen font-serif-sc">患者管理</h2>
           <p className="text-gray-500 text-sm">活跃病例和患者历史</p>
        </div>
        <button className="bg-tcm-darkGreen text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-green-900 transition-colors">
          <Icons.ShieldPlus size={18} /> 添加新患者
        </button>
      </div>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-100 text-xs font-bold text-gray-500 uppercase tracking-wider">
              <th className="p-4">患者</th>
              <th className="p-4">年龄/性别</th>
              <th className="p-4">诊断</th>
              <th className="p-4">最后就诊</th>
              <th className="p-4">状态</th>
              <th className="p-4">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {RECENT_PATIENTS.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50 transition-colors group cursor-pointer" onClick={() => { setSelectedPatient(p.id); setActiveTab('ai-diagnosis'); }}>
                <td className="p-4 flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full ${p.avatarColor} text-white flex items-center justify-center font-bold text-xs`}>{p.name.charAt(0)}</div>
                  <span className="font-bold text-gray-700">{p.name}</span>
                </td>
                <td className="p-4 text-sm text-gray-600">{p.age} / {p.gender}</td>
                <td className="p-4 text-sm text-tcm-darkGreen font-medium">{p.condition}</td>
                <td className="p-4 text-sm text-gray-500">{p.date}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-bold ${p.status === 'Critical' ? 'bg-red-100 text-red-600' : p.status === 'Stable' ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'}`}>
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
      <div className="w-full h-full p-6 bg-gray-50 overflow-y-auto animate-in fade-in slide-in-from-bottom-4 flex flex-col md:flex-row gap-6">
        
        {/* Left Column: Input */}
        <div className="w-full md:w-1/3 flex flex-col gap-4">
          <h2 className="text-2xl font-bold text-tcm-darkGreen font-serif-sc mb-2">报告上传</h2>
          
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
             <div className="mb-4">
               <label className="block text-sm font-bold text-gray-700 mb-2">扫描或图像</label>
               <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:bg-gray-50 transition-colors">
                 <input type="file" onChange={handleReportUpload} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" accept="image/*" />
                 {previewUrl ? (
                   <img src={previewUrl} alt="Preview" className="max-h-48 mx-auto rounded shadow-sm" />
                 ) : (
                   <div className="text-gray-400 flex flex-col items-center">
                     <Icons.UploadCloud size={32} className="mb-2"/>
                     <span className="text-sm">点击上传图像</span>
                   </div>
                 )}
               </div>
             </div>

             <div className="mb-4">
               <label className="block text-sm font-bold text-gray-700 mb-2">临床记录（可选）</label>
               <textarea 
                 value={reportText}
                 onChange={(e) => setReportText(e.target.value)}
                 className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-tcm-lightGreen focus:border-transparent min-h-[100px]"
                 placeholder="在此输入任何附加信息或复制粘贴文本报告..."
               />
             </div>

             <button 
               onClick={runAnalysis}
               disabled={isAnalyzing || (!reportText && !base64Data)}
               className="w-full bg-tcm-darkGreen text-white py-3 rounded-lg font-bold shadow-md hover:bg-green-900 transition-all disabled:opacity-50 disabled:shadow-none flex items-center justify-center gap-2"
             >
               {isAnalyzing ? (
                 <>
                   <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                   分析中...
                 </>
               ) : (
                 <>
                   <Icons.Zap size={18} /> 运行AI分析
                 </>
               )}
             </button>
          </div>
        </div>

        {/* Right Column: Results */}
        <div className="w-full md:w-2/3 flex flex-col">
          <h2 className="text-2xl font-bold text-tcm-darkGreen font-serif-sc mb-6">解读结果</h2>
          
          <div className="flex-1 bg-white rounded-xl border border-gray-200 shadow-sm p-8 overflow-y-auto">
             {analysisResult ? (
               <div className="prose prose-sm max-w-none prose-headings:text-tcm-darkGreen prose-p:text-gray-700 prose-strong:text-tcm-darkGreen">
                 {analysisResult.split('\n').map((line, i) => {
                   if (line.startsWith('**') || line.startsWith('#')) return <h3 key={i} className="text-lg font-bold mt-4 mb-2">{line.replace(/[#*]/g, '')}</h3>;
                   if (line.trim().startsWith('-')) return <li key={i} className="ml-4">{line.substring(1)}</li>;
                   return <p key={i} className="mb-2">{line}</p>;
                 })}
               </div>
             ) : (
               <div className="h-full flex flex-col items-center justify-center text-gray-300">
                 <Icons.FileText size={64} className="mb-4 opacity-50"/>
                 <p className="text-lg font-medium">尚未生成分析。</p>
                 <p className="text-sm">上传报告以开始。</p>
               </div>
             )}
          </div>
        </div>
      </div>
    );
  };

  const RecordsView = () => (
    <div className="w-full h-full p-8 bg-gray-50 overflow-y-auto animate-in fade-in slide-in-from-bottom-4">
      <h2 className="text-2xl font-bold text-tcm-darkGreen font-serif-sc mb-6">电子病历</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1,2,3,4,5,6].map(i => (
          <div key={i} className="bg-white p-6 rounded-xl border border-gray-200 hover:shadow-lg transition-all cursor-pointer group hover:border-tcm-gold/50">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-blue-50 text-blue-600 rounded-lg group-hover:bg-tcm-gold group-hover:text-white transition-colors">
                <Icons.FileText size={24} />
              </div>
              <button className="text-gray-300 hover:text-gray-500"><Icons.Menu size={16}/></button>
            </div>
            <h3 className="font-bold text-gray-800 mb-1">病例记录 #{202300 + i}</h3>
            <p className="text-xs text-gray-500 mb-4">2小时前更新</p>
            <div className="flex items-center gap-2 text-xs font-medium text-gray-400 group-hover:text-tcm-darkGreen">
              <span className="bg-gray-100 px-2 py-1 rounded">心脏病学</span>
              <span className="bg-gray-100 px-2 py-1 rounded">住院患者</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const ResearchView = () => (
    <div className="w-full h-full p-8 bg-gray-50 overflow-y-auto animate-in fade-in slide-in-from-bottom-4">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold text-tcm-darkGreen font-serif-sc mb-2">医学知识图谱</h2>
        <p className="text-gray-500 mb-8">使用AI综合搜索全球医学数据库。</p>
        
        <div className="relative mb-10">
          <input type="text" placeholder="搜索症状、药物相互作用或最新论文..." className="w-full p-4 pl-12 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen shadow-sm" />
          <Icons.Globe className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <button className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-tcm-darkGreen text-white px-6 py-2 rounded-full hover:bg-green-900 transition-colors">搜索</button>
        </div>

        <div className="space-y-6">
          <h3 className="font-bold text-gray-800 border-b pb-2">最新相关论文</h3>
          {[1, 2, 3].map(i => (
             <div key={i} className="bg-white p-5 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
               <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded mb-2 inline-block">新英格兰医学杂志</span>
               <h4 className="font-bold text-lg text-gray-900 mb-2">综合医学在慢性高血压管理中的疗效</h4>
               <p className="text-sm text-gray-600 leading-relaxed mb-3">
                 一项随机对照试验，展示了将标准方案与...结合时患者结果的显著改善
               </p>
               <div className="flex gap-4 text-xs text-gray-400">
                 <span>2023年10月24日</span>
                 <span>被引用45次</span>
                 <button className="text-tcm-lightGreen hover:underline ml-auto font-bold">阅读摘要</button>
               </div>
             </div>
          ))}
        </div>
      </div>
    </div>
  );
  
  const SettingsView = () => (
    <div className="w-full h-full p-8 bg-gray-50 overflow-y-auto animate-in fade-in slide-in-from-bottom-4">
       <div className="max-w-2xl">
         <h2 className="text-2xl font-bold text-tcm-darkGreen font-serif-sc mb-8">系统设置</h2>
         
         <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-6">
           <div className="p-4 border-b border-gray-100 bg-gray-50 font-bold text-sm text-gray-500 uppercase">通用</div>
           <div className="p-6 space-y-6">
             <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-gray-800">深色模式</div>
                  <div className="text-xs text-gray-500">减少夜班时的眼部疲劳</div>
                </div>
                <div className="w-12 h-6 bg-gray-200 rounded-full relative cursor-pointer"><div className="w-4 h-4 bg-white rounded-full absolute top-1 left-1 shadow-sm"></div></div>
             </div>
             <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-gray-800">紧凑视图</div>
                  <div className="text-xs text-gray-500">在表格中显示更多数据密度</div>
                </div>
                <div className="w-12 h-6 bg-tcm-lightGreen rounded-full relative cursor-pointer"><div className="w-4 h-4 bg-white rounded-full absolute top-1 right-1 shadow-sm"></div></div>
             </div>
           </div>
         </div>

         <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
           <div className="p-4 border-b border-gray-100 bg-gray-50 font-bold text-sm text-gray-500 uppercase">AI配置</div>
           <div className="p-6 space-y-6">
             <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-gray-800">模型温度</div>
                  <div className="text-xs text-gray-500">调整创造力与精确度 (0.0 - 1.0)</div>
                </div>
                <input type="range" className="w-32" />
             </div>
             <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-gray-800">自动建议治疗方案</div>
                  <div className="text-xs text-gray-500">自动追加中医协议</div>
                </div>
                <div className="w-12 h-6 bg-tcm-lightGreen rounded-full relative cursor-pointer"><div className="w-4 h-4 bg-white rounded-full absolute top-1 right-1 shadow-sm"></div></div>
             </div>
           </div>
         </div>
       </div>
    </div>
  );

  return (
    <div className="w-full h-screen flex bg-gray-50 font-sans overflow-hidden">
      
      {/* 1. Navigation Sidebar (Left) */}
      <aside className="w-64 bg-tcm-darkGreen flex flex-col text-white flex-shrink-0 z-20 shadow-xl transition-all duration-300">
        {/* Branding */}
        <div className="h-16 flex items-center px-6 border-b border-white/10 bg-black/10">
           <div className="w-8 h-8 bg-tcm-gold rounded flex items-center justify-center text-tcm-darkGreen font-bold font-serif-sc mr-3">
             医
           </div>
           <span className="font-serif-sc font-bold text-lg tracking-wider">仁术专业版</span>
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
            label="电子病历" 
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
              <p className="text-xs text-tcm-gold/80 truncate">主治医师</p>
            </div>
          </div>
          <button onClick={onLogout} className="w-full flex items-center justify-center gap-2 py-2 text-xs text-red-300 hover:text-white hover:bg-white/10 rounded transition-colors">
            <Icons.LogOut size={14} /> 退出登录
          </button>
        </div>
      </aside>

      {/* Main Content Area - Conditional Rendering */}
      {activeTab === 'ai-diagnosis' ? (
        <div className="flex-1 flex overflow-hidden relative">
          
          {/* 2. Collapsible History Sidebar */}
           <div className={`bg-gray-50 border-r border-gray-200 flex flex-col transition-all duration-300 ease-in-out ${showHistory ? 'w-64 opacity-100' : 'w-0 opacity-0 overflow-hidden'}`}>
             <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider whitespace-nowrap">聊天历史</span>
                <button 
                  onClick={() => setShowHistory(false)}
                  className="text-gray-400 hover:text-gray-600 p-1 hover:bg-gray-100 rounded transition-colors"
                >
                  <Icons.PanelLeft size={18} />
                </button>
             </div>
             
             <div className="p-3">
               <button 
                 onClick={() => { setMessages([]); setInputValue(''); }}
                 className="w-full flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-700 hover:border-tcm-lightGreen hover:text-tcm-lightGreen transition-colors shadow-sm mb-4 whitespace-nowrap"
               >
                 <Icons.MessageSquare size={16} /> 新建聊天
               </button>
               
               <div className="space-y-1 overflow-y-auto custom-scrollbar" style={{maxHeight: 'calc(100vh - 180px)'}}>
                 <div className="px-2 py-1 text-[10px] font-bold text-gray-400 uppercase mt-2 mb-1">最近</div>
                 {MOCK_HISTORY.map((item) => (
                   <button key={item.id} className="w-full text-left px-3 py-2 rounded-lg text-sm text-gray-600 hover:bg-white hover:shadow-sm transition-all truncate group">
                     <span className="block truncate">{item.title}</span>
                     <span className="text-[10px] text-gray-400">{item.date}</span>
                   </button>
                 ))}
               </div>
             </div>
           </div>

          {/* 3. Main Workspace (Right) - Chat Interface */}
          <main className="flex-1 flex flex-col bg-white min-w-0 relative">
            {/* Header */}
            <header className="h-16 border-b border-gray-100 flex items-center justify-between px-6 bg-white z-10">
              <div className="flex items-center gap-3">
                 {!showHistory && (
                   <button 
                     onClick={() => setShowHistory(true)}
                     className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
                     title="显示历史"
                   >
                     <Icons.PanelLeft size={20} />
                   </button>
                 )}
                 
                 <div className="p-2 bg-tcm-darkGreen/5 rounded-lg text-tcm-darkGreen">
                   <Icons.BrainCircuit size={20} />
                 </div>
                 <div>
                   <h1 className="text-sm font-bold text-gray-800 flex items-center gap-2">
                     AI临床助手 
                                    
                     {/* Model Selector Dropdown */}
                     <div className="relative inline-block ml-1">
                       <select 
                          value={selectedModel.id}
                          onChange={(e) => setSelectedModel(AVAILABLE_MODELS.find(m => m.id === e.target.value) || AVAILABLE_MODELS[1])}
                          className="appearance-none pl-2 pr-6 py-0.5 bg-blue-50 text-blue-700 text-[10px] rounded-full border border-blue-100 font-medium focus:outline-none focus:ring-1 focus:ring-blue-300 cursor-pointer"
                       >
                          {AVAILABLE_MODELS.map(m => (
                            <option key={m.id} value={m.id}>{m.name}</option>
                          ))}
                       </select>
                       <Icons.ChevronRight size={10} className="absolute right-1.5 top-1/2 transform -translate-y-1/2 rotate-90 text-blue-500 pointer-events-none"/>
                     </div>
                   </h1>
                   <p className="text-xs text-gray-400">上下文: {selectedPatient ? `患者 #${selectedPatient}` : '常规会话'}</p>
                 </div>
              </div>
              
              {/* Quick Actions (Top Right) */}
              <div className="flex items-center gap-2">
                <QuickActionButton label="生成病例" onClick={() => handleQuickAction('generate_case')} />
                <QuickActionButton label="药物检查" onClick={() => handleQuickAction('drug_check')} />
                <QuickActionButton label="文献检索" onClick={() => handleQuickAction('lit_search')} />
              </div>
            </header>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-6 bg-[#f8f9fa] space-y-6">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2`}>
                  {msg.role === 'model' && (
                    <div className="w-8 h-8 rounded-full bg-tcm-darkGreen flex items-center justify-center text-white mr-3 shadow-sm flex-shrink-0 mt-1">
                      <Icons.Bot size={16} />
                    </div>
                  )}
                  
                  <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm text-sm leading-relaxed ${
                    msg.role === 'user' 
                      ? 'bg-tcm-darkGreen text-white rounded-br-none' 
                      : 'bg-white text-gray-700 border border-gray-100 rounded-bl-none'
                  }`}>
                     {msg.role === 'model' ? (
                       <div className="prose prose-sm max-w-none prose-p:my-1 prose-headings:text-tcm-darkGreen prose-strong:text-tcm-darkGreen">
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
                   <div className="bg-white px-4 py-3 rounded-2xl rounded-bl-none border border-gray-100 shadow-sm flex items-center gap-2">
                     <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
                     <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-75"></span>
                     <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-150"></span>
                   </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-gray-100 shadow-[0_-5px_20px_rgba(0,0,0,0.02)] z-10 pb-6">
              <div className="max-w-4xl mx-auto w-full">
                 
                 {/* Toolbar: Thinking & Search - Moved above input capsule */}
                 <div className="flex items-center gap-3 mb-2 px-1">
                    <button 
                      onClick={() => setEnableDeepThink(!enableDeepThink)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${enableDeepThink ? 'bg-indigo-50 border-indigo-200 text-indigo-700 shadow-sm' : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50'}`}
                    >
                      <Icons.BrainCircuit size={14} className={enableDeepThink ? "animate-pulse" : ""} />
                      深度思考 {enableDeepThink && <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full ml-1"></span>}
                    </button>
                    
                    <button 
                      onClick={() => setEnableWebSearch(!enableWebSearch)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${enableWebSearch ? 'bg-blue-50 border-blue-200 text-blue-700 shadow-sm' : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50'}`}
                    >
                      <Icons.Globe size={14} />
                      网络搜索 {enableWebSearch && <span className="w-1.5 h-1.5 bg-blue-500 rounded-full ml-1"></span>}
                    </button>
                 </div>

                 {/* Input Capsule */}
                 <div className="relative flex items-end gap-2 bg-gray-50 border border-gray-200 rounded-3xl p-2 transition-shadow focus-within:ring-2 focus-within:ring-tcm-lightGreen/20 focus-within:border-tcm-lightGreen/50 focus-within:bg-white focus-within:shadow-md">
                   <input type="file" multiple ref={fileInputRef} className="hidden" onChange={handleFileUpload} />
                   <button 
                      onClick={() => fileInputRef.current?.click()}
                      className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                      title="上传报告/图像"
                   >
                     <Icons.Paperclip size={20} />
                   </button>
                   <button 
                      onClick={handleVoiceInput}
                      className="p-2 text-gray-400 hover:text-tcm-darkGreen rounded-full hover:bg-gray-100 transition-colors"
                      title="语音听写"
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
                     placeholder="输入临床问题、上传结果或请求鉴别诊断..."
                     className="flex-1 bg-transparent border-none focus:ring-0 text-sm text-gray-800 resize-none max-h-32 py-2"
                     rows={1}
                     style={{minHeight: '24px'}}
                   />
                   <button 
                     onClick={() => handleSendMessage()}
                     disabled={!inputValue.trim() || isLoading}
                     className="p-2 bg-tcm-darkGreen text-white rounded-full hover:bg-green-900 disabled:opacity-50 disabled:hover:bg-tcm-darkGreen transition-colors shadow-sm"
                   >
                     <Icons.Send size={18} className={isLoading ? "animate-pulse" : ""} />
                   </button>
                 </div>
              </div>
              <p className="text-center text-[10px] text-gray-400 mt-2">
                AI生成的见解必须由合格的医师验证。
              </p>
            </div>
          </main>
        </div>
      ) : (
        // Other Views Container
        <div className="flex-1 bg-white overflow-hidden flex flex-col">
          <header className="h-16 border-b border-gray-100 flex items-center justify-between px-6 bg-white z-10 shrink-0">
             <h2 className="text-lg font-bold text-gray-800 font-serif-sc flex items-center gap-2 capitalize">
               {activeTab.replace('-', ' ')}
             </h2>
             <div className="text-xs text-gray-400">专业工作区</div>
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
    className="px-3 py-1.5 text-xs font-medium text-tcm-lightGreen bg-tcm-lightGreen/10 border border-tcm-lightGreen/20 rounded-full hover:bg-tcm-lightGreen hover:text-white transition-all"
  >
    {label}
  </button>
);

export default ProfessionalPortal;