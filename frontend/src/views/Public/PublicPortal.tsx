

import React, { useState, useEffect, useLayoutEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, ChatMessage, UserPersona, AIModelConfig, ProviderConfig, CustomModel } from '../../types';
import { AVAILABLE_MODELS, PROVIDERS } from '../../constants';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';
import { createPublicChat, analyzeUserPersona, sendMessageWithConfig } from '../../services/geminiService';
import { LogoutConfirmModal } from '../../components/common/LogoutConfirmModal';
import { Chat } from "@google/genai";
import { providerApi } from '../../api/modules/model';

interface PublicPortalProps {
  user: User;
  onLogout: () => void;
}

interface Attachment {
  file: File;
  previewUrl: string;
  base64: string;
}

interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  lastModified: Date;
}

// Helper to group sessions by date
const groupSessionsByDate = (sessions: ChatSession[]) => {
  const groups: { [key: string]: ChatSession[] } = {
    '今天': [],
    '昨天': [],
    '最近7天': [],
    '更早': []
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
      groups['今天'].push(session);
    } else if (sessionDate.getTime() === yesterday.getTime()) {
      groups['昨天'].push(session);
    } else if (sessionDate > lastWeek) {
      groups['最近7天'].push(session);
    } else {
      groups['更早'].push(session);
    }
  });

  return groups;
};

const PublicPortal: React.FC<PublicPortalProps> = ({ user, onLogout }) => {
  const navigate = useNavigate();
  
  // --- State ---

  // Sessions Management
  const [sessions, setSessions] = useState<ChatSession[]>([
    {
      id: 'init-1',
      title: '新的会话',
      messages: [{
        id: 'welcome',
        role: 'model',
        text: `你好 ${user.name}. 我是仁术AI健康助手,我可以为你提供健康咨询和建议。`,
        timestamp: new Date()
      }],
      lastModified: new Date()
    }
  ]);
  const [activeSessionId, setActiveSessionId] = useState<string>('init-1');
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchActive, setIsSearchActive] = useState(false);
  
  // UI Toggles
  const [showLeftSidebar, setShowLeftSidebar] = useState(true);
  const [showRightSidebar, setShowRightSidebar] = useState(true);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [showModelSelector, setShowModelSelector] = useState(false);
  const [showProviderSelector, setShowProviderSelector] = useState(false);
  const [isQuickConfigOpen, setIsQuickConfigOpen] = useState(false);

  // Persistence: Provider Configs & Custom Models
  const [providerConfigs, setProviderConfigs] = useState<Record<string, ProviderConfig>>(() => {
    const saved = localStorage.getItem('user_provider_configs');
    return saved ? JSON.parse(saved) : {};
  });

  const [customModels, setCustomModels] = useState<CustomModel[]>(() => {
    const saved = localStorage.getItem('user_custom_models');
    return saved ? JSON.parse(saved) : [];
  });

  const [enabledModelIds, setEnabledModelIds] = useState<string[]>(() => {
    const saved = localStorage.getItem('user_enabled_models');
    // If null, default to all available builtin
    return saved ? JSON.parse(saved) : AVAILABLE_MODELS.map(m => m.id);
  });

  // Model & Provider State
  const [selectedProviderId, setSelectedProviderId] = useState<string>('google');
  const [apiData, setApiData] = useState<any[]>([]);

  // Fetch Providers and Models from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await providerApi.get_providers_with_models();
        if (response.success && response.data) {
          setApiData(response.data);
          // If current selected provider is not in the list (and list is not empty), select the first one
          if (response.data.length > 0) {
             const currentExists = response.data.some((p: any) => p.name === selectedProviderId);
             if (!currentExists) {
                // Try to find google or just take the first one
                const defaultProvider = response.data.find((p: any) => p.name === 'google') || response.data[0];
                setSelectedProviderId(defaultProvider.name);
             }
          }
        }
      } catch (error) {
        console.error("Failed to fetch models config:", error);
      }
    };
    fetchData();
  }, []);

  // Computed Available Models (Filtered by Provider AND Enabled status)
  const allModels = useMemo(() => {
    if (apiData.length > 0) {
        // Map API data to AIModelConfig structure
        const models: AIModelConfig[] = [];
        apiData.forEach((p: any) => {
            if (p.models) {
                p.models.forEach((m: any) => {
                    models.push({
                        id: m.model_name, // Use model_name as ID for the chat service
                        name: m.label || m.model_name,
                        description: m.description || '',
                        supportsThinking: m.features?.includes('thinking') || false,
                        supportsVision: m.features?.includes('vision') || false,
                        provider: p.name as any,
                        contextWindow: m.context_window ? `${Math.round(m.context_window/1000)}K` : undefined
                    });
                });
            }
        });
        // Merge with custom models if any (local storage ones)
        return [...models, ...customModels];
    }
    // Fallback to constants if API fails or empty
    return [...AVAILABLE_MODELS, ...customModels];
  }, [apiData, customModels]);

  const currentProviders = useMemo(() => {
      if (apiData.length > 0) {
          return apiData.map((p: any) => ({
              id: p.name, // Use name as ID to match model provider field
              name: p.label || p.name,
              icon: p.icon || '🤖'
          }));
      }
      return PROVIDERS;
  }, [apiData]);

  const filteredModels = useMemo(() => 
    allModels.filter(m => m.provider === selectedProviderId && enabledModelIds.includes(m.id)), 
  [selectedProviderId, allModels, enabledModelIds]);
  
  const [selectedModel, setSelectedModel] = useState<AIModelConfig>(filteredModels[0] || AVAILABLE_MODELS[0]);

  // Sync when data changes externally (e.g. from management page)
  useEffect(() => {
    const handleStorageChange = () => {
        const savedProviderConfigs = localStorage.getItem('user_provider_configs');
        if (savedProviderConfigs) setProviderConfigs(JSON.parse(savedProviderConfigs));
        
        const savedCustomModels = localStorage.getItem('user_custom_models');
        if (savedCustomModels) setCustomModels(JSON.parse(savedCustomModels));

        const savedEnabledModels = localStorage.getItem('user_enabled_models');
        if (savedEnabledModels) setEnabledModelIds(JSON.parse(savedEnabledModels));
    };
    
    window.addEventListener('storage', handleStorageChange);
    handleStorageChange(); // Init
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  useEffect(() => {
    if (filteredModels.length > 0 && !filteredModels.find(m => m.id === selectedModel.id)) {
        setSelectedModel(filteredModels[0]);
    }
  }, [filteredModels, selectedModel]);

  // Chat State
  const activeSession = sessions.find(s => s.id === activeSessionId) || sessions[0];
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Settings
  const [enableDeepThink, setEnableDeepThink] = useState(false);
  const [enableWebSearch, setEnableWebSearch] = useState(false);
  const [attachments, setAttachments] = useState<Attachment[]>([]);

  // Theme & Persona
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme_public');
    return saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });
  const [persona, setPersona] = useState<UserPersona>(user.persona || {
    age: '18',
    gender: '男',
    chiefComplaint: '待分析...',
    medicalHistory: '无记录',
    suspectedDiagnosis: '分析待定',
    contraindications: '无禁忌',
    recommendedTreatment: ' wellness 建议'
  });
  const [editPersonaForm, setEditPersonaForm] = useState<UserPersona>(persona);
  const [changedFields, setChangedFields] = useState<string[]>([]);
  const [isPersonaAnalyzing, setIsPersonaAnalyzing] = useState(false);
  const [healthScore, setHealthScore] = useState(user.healthScore || 85);

  const chatRef = useRef<Chat | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // --- Effects ---

  useLayoutEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme_public', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme_public', 'light');
    }
  }, [isDarkMode]);

  useEffect(() => {
    chatRef.current = createPublicChat(selectedModel.id);
  }, [activeSessionId, selectedModel]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeSession.messages]);

  // --- Handlers ---

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files: File[] = Array.from(e.target.files);
      const newAttachments: Attachment[] = await Promise.all(
        files.map(async (file: File) => {
          const base64 = await new Promise<string>((resolve) => {
            const reader = new FileReader();
            reader.onload = (ev) => resolve(ev.target?.result as string);
            reader.readAsDataURL(file);
          });
          return { file, previewUrl: URL.createObjectURL(file), base64 };
        })
      );
      setAttachments(prev => [...prev, ...newAttachments]);
    }
  };

  // 语音识别逻辑 (来自 a.ts)
  const handleVoiceInput = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.lang = 'zh-CN';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;
      recognition.onstart = () => setInputValue(prev => prev + " (正在倾听...)");
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(prev => prev.replace(" (正在倾听...)", "") + transcript);
      };
      recognition.onerror = () => setInputValue(prev => prev.replace(" (正在倾听...)", ""));
      recognition.start();
    } else {
      alert("您的浏览器不支持语音识别功能。");
    }
  };

  const handleNewChat = () => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: '新的对话',
      messages: [{
        id: Date.now().toString(),
        role: 'model',
        text: `你好 ${user.name}. 我目前切换到了 ${selectedModel.name}. 请问有什么可以帮您？`,
        timestamp: new Date()
      }],
      lastModified: new Date()
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
    if (window.innerWidth < 768) setShowLeftSidebar(false);
  };

  const handleSendMessage = async () => {
    if ((!inputValue.trim() && attachments.length === 0) || !chatRef.current) return;

    // Check configuration
    // Look at Provider Level Config first
    const providerConfig = providerConfigs[selectedModel.provider];
    const isGoogle = selectedModel.provider === 'google';
    
    // Logic: If not google (built-in assumed), check if provider API key exists
    if (!isGoogle && !providerConfig?.apiKey) {
      setIsQuickConfigOpen(true);
      return;
    }

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      text: inputValue,
      timestamp: new Date(),
      attachments: attachments.map(a => ({
        type: a.file.type.startsWith('image') ? 'image' : 'file',
        url: a.previewUrl,
        name: a.file.name
      }))
    };

    const updatedMessages = [...activeSession.messages, userMsg];
    updateSessionMessages(activeSessionId, updatedMessages);

    if (activeSession.messages.length <= 1 && activeSession.title === '新的对话') {
       const newTitle = inputValue.slice(0, 20) + (inputValue.length > 20 ? '...' : '');
       setSessions(prev => prev.map(s => s.id === activeSessionId ? { ...s, title: newTitle } : s));
    }

    setInputValue('');
    const currentAttachments = [...attachments];
    setAttachments([]);
    setIsLoading(true);
    setIsPersonaAnalyzing(true);

    try {
      const fileParts = currentAttachments.map(a => ({
        data: a.base64.split(',')[1],
        mimeType: a.file.type
      }));

      // NOTE: In a real implementation, we would pass the providerConfig.apiKey to a new client instance here.
      // createPublicChat currently uses process.env.API_KEY. 
      // For this demo, we assume the service handles key swapping based on the selected model/provider context if implemented fully backend.
      // Or we would re-instantiate GoogleGenAI with the new key.
      
      const response = await sendMessageWithConfig(
        chatRef.current,
        userMsg.text || (currentAttachments.length > 0 ? "Analyzed attachment" : ""),
        fileParts,
        {
          enableThinking: enableDeepThink,
          enableSearch: enableWebSearch
        }
      );

      const modelMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'model',
        text: response.text || "No response generated.",
        timestamp: new Date()
      };

      updateSessionMessages(activeSessionId, [...updatedMessages, modelMsg]);

      const newPersona = await analyzeUserPersona(userMsg.text, persona);
      const changes: string[] = [];
      (Object.keys(newPersona) as Array<keyof UserPersona>).forEach(key => {
        if (newPersona[key] !== persona[key]) changes.push(key);
      });
      if (changes.length > 0) {
        setPersona(newPersona);
        setEditPersonaForm(newPersona);
        setChangedFields(changes);
        setTimeout(() => setChangedFields([]), 3000);
      }

    } catch (e) {
      console.error(e);
      updateSessionMessages(activeSessionId, [...updatedMessages, {
        id: Date.now().toString(),
        role: 'model',
        text: "抱歉，连接到该模型时出现问题。请确保您的 API Key 配置正确且有效。",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
      setIsPersonaAnalyzing(false);
    }
  };

  const updateSessionMessages = (sessionId: string, newMessages: ChatMessage[]) => {
    setSessions(prev => prev.map(s => s.id === sessionId ? { ...s, messages: newMessages, lastModified: new Date() } : s));
  };

  // Only used for Quick Config Modal - Saves to Provider Config now
  const saveQuickConfig = (apiKey: string) => {
    setProviderConfigs(prev => ({
        ...prev,
        [selectedProviderId]: {
            ...prev[selectedProviderId],
            apiKey: apiKey,
            enabled: true
        }
    }));
    // Persist to local storage immediately for sync
    const current = JSON.parse(localStorage.getItem('user_provider_configs') || '{}');
    current[selectedProviderId] = { ...current[selectedProviderId], apiKey, enabled: true };
    localStorage.setItem('user_provider_configs', JSON.stringify(current));
  };

  const groupSessions = groupSessionsByDate(sessions.filter(s => s.title.toLowerCase().includes(searchQuery.toLowerCase())));

  const toggleTheme = () => {
      setIsDarkMode(!isDarkMode);
  };

  return (
    <div className="h-screen w-full flex bg-rice-paper overflow-hidden transition-colors duration-500">
      <LogoutConfirmModal 
        isOpen={showLogoutModal} 
        onConfirm={() => { setShowLogoutModal(false); onLogout(); }} 
        onCancel={() => setShowLogoutModal(false)} 
        variant="public"
      />
      
      {/* 快速配置小窗 (仅在对话拦截时显示) */}
      {isQuickConfigOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white dark:bg-tcm-charcoal w-full max-w-sm rounded-3xl shadow-2xl p-6 border border-tcm-gold/30 scale-in-center">
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="p-4 bg-tcm-gold/10 rounded-full text-tcm-gold">
                <Icons.Zap size={32} />
              </div>
              <h3 className="text-lg font-bold text-tcm-darkGreen dark:text-tcm-cream font-serif-sc">需配置服务商</h3>
              <p className="text-sm text-gray-500">您选中的模型属于 <b>{currentProviders.find(p => p.id === selectedProviderId)?.name}</b>，需要配置 API Key 才能使用。</p>
              
              <div className="w-full space-y-3 pt-2">
                <input 
                  type="password" 
                  placeholder="输入 Provider API Key" 
                  autoFocus
                  className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-tcm-lightGreen transition-all text-sm"
                  onChange={(e) => saveQuickConfig(e.target.value)}
                />
                <button 
                  onClick={() => setIsQuickConfigOpen(false)}
                  className="w-full py-3 bg-tcm-darkGreen text-white rounded-xl font-bold hover:bg-tcm-lightGreen transition-all"
                >
                  保存并继续
                </button>
                <button 
                  onClick={() => setIsQuickConfigOpen(false)}
                  className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  稍后再说
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 1. LEFT SIDEBAR */}
      <aside
        className={`${showLeftSidebar ? 'w-[280px]' : 'w-0'} flex-shrink-0 bg-[#f0f4f9]/80 dark:bg-[#1e1e1e]/80 backdrop-blur-md border-r border-tcm-lightGreen/10 flex flex-col transition-all duration-300 overflow-hidden relative z-30`}
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between p-4 pb-2">
            <button
               onClick={() => setShowLeftSidebar(false)}
               className="p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-white/10 rounded-full transition-colors"
            >
              <Icons.Menu size={20} />
            </button>

            <button
               onClick={() => setIsSearchActive(!isSearchActive)}
               className={`p-2 rounded-full transition-colors ${isSearchActive ? 'bg-gray-200 dark:bg-white/10 text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-white/10'}`}
            >
              <Icons.Stethoscope className="rotate-90" size={20} />
            </button>
          </div>

          <div className="px-4 py-2">
            {isSearchActive ? (
              <div className="relative animate-in fade-in slide-in-from-top-1">
                 <input
                   ref={searchInputRef}
                   type="text"
                   placeholder="搜索历史会话..."
                   value={searchQuery}
                   onChange={(e) => setSearchQuery(e.target.value)}
                   className="w-full bg-white dark:bg-black/20 border border-transparent dark:border-white/10 rounded-full py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-gray-200 dark:focus:ring-gray-700 shadow-sm"
                 />
                 <div className="absolute left-3 top-2.5 text-gray-500">
                   <Icons.Activity size={16} />
                 </div>
              </div>
            ) : (
              <button
                onClick={handleNewChat}
                className="flex items-center gap-3 px-4 py-3 bg-[#dde3ea] dark:bg-[#2a2a2a] text-gray-700 dark:text-gray-200 rounded-2xl hover:bg-[#d0d7de] dark:hover:bg-[#333] transition-colors w-full shadow-sm"
              >
                <Icons.Edit3 size={18} />
                <span className="text-sm font-medium">开启新诊疗</span>
              </button>
            )}
          </div>

          <div className="flex-1 overflow-y-auto px-2 py-2 custom-scrollbar space-y-4">
             {Object.entries(groupSessions).map(([group, groupSessions]) => (
               groupSessions.length > 0 && (
                 <div key={group} className="animate-in fade-in">
                   <div className="px-4 py-2 text-xs font-bold text-gray-500 dark:text-gray-400">{group}</div>
                   {groupSessions.map(session => (
                      <div
                        key={session.id}
                        onClick={() => setActiveSessionId(session.id)}
                        className={`group flex items-center gap-3 px-4 py-2 mx-2 rounded-full cursor-pointer transition-colors ${
                          activeSessionId === session.id 
                            ? 'bg-tcm-lightGreen/20 dark:bg-tcm-lightGreen/10 text-tcm-darkGreen dark:text-tcm-freshGreen font-medium' 
                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-white/5'
                        }`}
                      >
                        <Icons.MessageSquare size={16} className="flex-shrink-0 opacity-70" />
                        <div className="flex-1 min-w-0 text-sm truncate">{session.title}</div>
                      </div>
                   ))}
                 </div>
               )
             ))}
          </div>
          {/* Bottom: Settings / User */}
          <div className="p-2 border-t border-gray-200 dark:border-white/5 relative bg-white/50 dark:bg-black/20">
             {showUserMenu && (
                <div className="absolute bottom-full left-2 right-2 mb-2 bg-[#f0f4f9] dark:bg-[#1e1e1e] rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden animate-in slide-in-from-bottom-2 z-40">
                  <button onClick={() => { setIsEditingProfile(true); setShowUserMenu(false); }} className="w-full text-left px-4 py-3 hover:bg-gray-200 dark:hover:bg-white/10 flex items-center gap-3 text-sm text-gray-700 dark:text-gray-200 transition-colors">
                    <Icons.Edit3 size={16} className="text-tcm-lightGreen"/> 个人资料设置
                  </button>
                  {/* 跳转到新的模型管理页面 */}
                  <button onClick={() => { navigate('/public/models'); setShowUserMenu(false); }} className="w-full text-left px-4 py-3 hover:bg-gray-200 dark:hover:bg-white/10 flex items-center gap-3 text-sm text-gray-700 dark:text-gray-200 transition-colors">
                    <Icons.Settings size={16} className="text-tcm-gold"/> 模型管理配置
                  </button>
                  <button onClick={toggleTheme} className="w-full text-left px-4 py-3 hover:bg-gray-200 dark:hover:bg-white/10 flex items-center gap-3 text-sm text-gray-700 dark:text-gray-200 transition-colors">
                    {isDarkMode ? <Icons.Sun size={16} className="text-yellow-500" /> : <Icons.Moon size={16} className="text-indigo-400" />}
                    {isDarkMode ? '切换到浅色模式' : '切换到深色模式'}
                  </button>
                  <button onClick={() => { setShowLogoutModal(true); setShowUserMenu(false); }}  className="w-full text-left px-4 py-3 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center gap-3 text-sm text-red-600 dark:text-red-400 border-t border-gray-200 dark:border-gray-700 transition-colors">
                    <Icons.LogOut size={16}/> 退出账号
                  </button>
                </div>
             )}

             <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className={`flex items-center gap-3 w-full p-3 rounded-full hover:bg-gray-200 dark:hover:bg-white/5 transition-colors ${showUserMenu ? 'bg-gray-200 dark:bg-white/5' : ''}`}
             >
                <div className="w-8 h-8 rounded-full bg-tcm-darkGreen text-white flex items-center justify-center text-xs font-bold shadow-inner">
                   {user.name.charAt(0)}
                </div>
                <div className="flex-1 text-left text-sm font-medium text-gray-700 dark:text-gray-200 truncate">
                  {user.name}
                </div>
                <Icons.Settings size={18} className="text-gray-500" />
             </button>
          </div>
        </div>
      </aside>

      {/* 2. MIDDLE AREA */}
      <main className="flex-1 flex flex-col relative z-10 transition-colors duration-500 min-w-0 bg-transparent">
        <header className="h-16 flex items-center justify-between px-6 z-10 transition-colors bg-white/80 dark:bg-[#131314]/80 backdrop-blur-sm border-b border-tcm-lightGreen/5">
          <div className="flex items-center gap-3">
             {!showLeftSidebar && (
               <button
                 onClick={() => setShowLeftSidebar(true)}
                 className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-white/5 rounded-full transition-colors"
               >
                 <Icons.Menu size={20} />
               </button>
             )}

             {/* 仁术 Logo Dropdown 实现供应商切换 */}
             <div className="relative">
               <div 
                  onClick={() => setShowProviderSelector(!showProviderSelector)}
                  className="flex items-center gap-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-white/5 px-3 py-1.5 rounded-lg transition-colors group"
                >
                  <BrandLogo size="sm" showText={true} />
                  <Icons.ChevronDown size={14} className={`text-gray-400 transition-transform duration-300 ${showProviderSelector ? 'rotate-180' : ''}`} />
               </div>

               {showProviderSelector && (
                 <>
                   <div className="fixed inset-0 z-40" onClick={() => setShowProviderSelector(false)}></div>
                   <div className="absolute top-full left-0 mt-2 w-56 bg-white dark:bg-[#1e1e1e] border border-gray-200 dark:border-gray-700 rounded-xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 origin-top-left">
                     <div className="p-1.5 space-y-0.5">
                        <div className="px-2 py-1.5 text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">选择模型提供商</div>
                        {currentProviders.map((p: any) => (
                          <button
                            key={p.id}
                            onClick={() => {
                              setSelectedProviderId(p.id);
                              setShowProviderSelector(false);
                            }}
                           className={`w-full text-left p-2 rounded-lg flex items-center gap-3 transition-colors ${
                             selectedProviderId === p.id 
                               ? 'bg-tcm-lightGreen/10 border border-tcm-lightGreen/20 text-tcm-darkGreen dark:text-tcm-lightGreen' 
                               : 'hover:bg-gray-50 dark:hover:bg-white/5 text-gray-700 dark:text-gray-200'
                           }`}
                         >
                           <span className="text-lg">{p.icon}</span>
                           <span className="text-xs font-bold">{p.name}</span>
                           {selectedProviderId === p.id && <Icons.Check size={14} className="ml-auto" />}
                         </button>
                       ))}
                     </div>
                   </div>
                 </>
               )}
             </div>
          </div>

          <div className="flex items-center gap-2">
             <div className="relative">
                <button
                  onClick={() => setShowModelSelector(!showModelSelector)}
                  className={`flex items-center justify-between gap-2 w-52 bg-white dark:bg-white/5 border px-3 py-1.5 rounded-lg text-xs font-bold text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-white/10 transition-colors shadow-sm ${showModelSelector ? 'border-tcm-lightGreen ring-2 ring-tcm-lightGreen/20' : 'border-gray-200 dark:border-white/10'}`}
                >
                    <div className="flex items-center gap-2 truncate">
                      <Icons.Zap size={14} className="text-tcm-gold flex-shrink-0" />
                      <span className="truncate">{selectedModel.name}</span>
                    </div>
                    <Icons.ChevronDown size={12} className={`text-gray-400 flex-shrink-0 transition-transform duration-300 ${showModelSelector ? 'rotate-180' : ''}`} />
                </button>

                {showModelSelector && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setShowModelSelector(false)}></div>
                    <div className="absolute top-full right-0 mt-2 w-full bg-white dark:bg-[#1e1e1e] border border-gray-200 dark:border-gray-700 rounded-xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 origin-top-right">
                      <div className="p-1.5 space-y-0.5">
                        <div className="px-2 py-1.5 text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">选择已适配模型</div>
                        {filteredModels.length === 0 ? (
                            <div className="p-4 text-center text-xs text-gray-400">
                                暂无已启用模型。<br/>请前往 <span className="text-tcm-lightGreen cursor-pointer" onClick={() => navigate('/public/models')}>模型管理</span> 启用。
                            </div>
                        ) : filteredModels.map(model => (
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
                              }`}>{model.name}</div>
                              <div className="text-[10px] text-gray-500 dark:text-gray-400 mt-0 truncate">{model.description}</div>
                            </div>
                            {(model as CustomModel).isCustom && <span className="text-[9px] text-tcm-gold border border-tcm-gold/30 px-1 rounded">Custom</span>}
                          </button>
                        ))}
                      </div>
                    </div>
                  </>
                )}
             </div>

             <button
               onClick={() => setShowRightSidebar(!showRightSidebar)}
               className={`p-2 rounded-full transition-colors ${showRightSidebar ? 'bg-tcm-lightGreen/10 text-tcm-lightGreen' : 'text-gray-400 hover:bg-gray-100 dark:hover:bg-white/5'}`}
             >
               <Icons.Activity size={20} />
             </button>
          </div>
        </header>

        {/* Chat Stream */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 scroll-smooth">
          <div className="max-w-4xl mx-auto w-full space-y-8">
            {activeSession.messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up group w-full`}>
                  {msg.role === 'model' && (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-tcm-lightGreen to-tcm-darkGreen text-white flex items-center justify-center shadow-lg mr-4 flex-shrink-0 mt-1">
                      <Icons.Zap size={14} />
                    </div>
                  )}
                  <div className={`space-y-2 max-w-[85%]`}>
                    {msg.role === 'user' ? (
                       <div className="px-5 py-3 text-gray-800 dark:text-white leading-relaxed whitespace-pre-wrap">
                          {msg.attachments?.map((att, idx) => (
                            <img key={idx} src={att.url} alt="att" className="h-32 rounded-lg border mb-2" />
                          ))}
                          {msg.text}
                       </div>
                    ) : (
                       <div className="text-gray-800 dark:text-gray-200 leading-relaxed">
                          <div className="prose prose-lg max-w-none dark:prose-invert prose-p:my-2">
                            {msg.text.split('\n').map((line, i) => <p key={i}>{line}</p>)}
                          </div>
                       </div>
                    )}
                  </div>
                  {msg.role === 'user' && (
                    <img src={user.avatar} className="w-8 h-8 rounded-full border border-gray-200 dark:border-gray-600 ml-3 shadow-sm object-cover flex-shrink-0 mt-1" alt="Me" />
                  )}
                </div>
            ))}
            {isLoading && (
               <div className="flex justify-start w-full">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-tcm-lightGreen to-tcm-darkGreen text-white flex items-center justify-center shadow-lg mr-4 flex-shrink-0">
                    <Icons.Zap size={14} />
                  </div>
                  <div className="flex items-center gap-1 mt-2">
                     <div className="w-2 h-2 bg-tcm-lightGreen rounded-full animate-bounce"></div>
                     <div className="w-2 h-2 bg-tcm-gold rounded-full animate-bounce delay-75"></div>
                     <div className="w-2 h-2 bg-tcm-darkGreen rounded-full animate-bounce delay-150"></div>
                  </div>
               </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="p-2 z-20">
          <div className="max-w-4xl mx-auto">
             {attachments.length > 0 && (
                <div className="flex gap-3 px-4 py-2 overflow-x-auto custom-scrollbar">
                  {attachments.map((att, idx) => (
                      <div key={idx} className="relative group flex-shrink-0">
                        <img src={att.previewUrl} alt="preview" className="h-12 w-12 rounded-lg object-cover border border-gray-200 dark:border-gray-600 shadow-sm" />
                        <button
                          onClick={() => setAttachments(attachments.filter((_, i) => i !== idx))}
                          className="absolute -top-1 -right-1 bg-gray-800 text-white rounded-full p-0.5 shadow-md opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <Icons.X size={10} />
                        </button>
                      </div>
                  ))}
                </div>
             )}

             <div className="bg-[#f0f4f9] dark:bg-[#1e1e1e] rounded-full p-3 flex items-center gap-2 transition-all duration-300 shadow-sm border border-gray-200 dark:border-gray-700 ring-1 ring-transparent focus-within:ring-tcm-lightGreen/30 focus-within:bg-white dark:focus-within:bg-[#252525]">
                <button
                    onClick={() => fileInputRef.current?.click()}
                    className="p-1.5 text-gray-400 hover:text-tcm-darkGreen dark:text-gray-500 dark:hover:text-tcm-lightGreen transition-colors rounded-full hover:bg-gray-200/50 dark:hover:bg-white/10"
                    title="Upload"
                >
                  <input type="file" multiple ref={fileInputRef} className="hidden" onChange={handleFileUpload} />
                  <Icons.Paperclip size={20} />
                </button>

                <button
                    onClick={handleVoiceInput}
                    className="p-1.5 text-gray-400 hover:text-tcm-darkGreen dark:text-gray-500 dark:hover:text-tcm-lightGreen transition-colors rounded-full hover:bg-gray-200/50 dark:hover:bg-white/10"
                    title="语音输入"
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
                  placeholder="输入健康咨询问题..."
                  className="flex-1 bg-transparent border-none focus:ring-0 focus:outline-none text-gray-800 dark:text-gray-100 placeholder-gray-400 resize-none py-1.5 text-sm max-h-32"
                  rows={1}
                  style={{ minHeight: '32px' }}
                />

                <div className="flex items-center gap-1 border-l border-gray-300 dark:border-gray-700 pl-2">
                    <button
                      onClick={() => setEnableDeepThink(!enableDeepThink)}
                      className={`p-1.5 rounded-full transition-all ${
                        enableDeepThink 
                          ? 'text-tcm-darkGreen bg-tcm-lightGreen/20 dark:text-tcm-lightGreen' 
                          : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
                      }`}
                      title="Deep Thinking"
                    >
                       <Icons.BrainCircuit size={18} />
                    </button>
                    <button
                      onClick={() => setEnableWebSearch(!enableWebSearch)}
                      className={`p-1.5 rounded-full transition-all ${
                        enableWebSearch
                          ? 'text-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:text-blue-400' 
                          : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
                      }`}
                      title="Web Search"
                    >
                       <Icons.Globe size={18} />
                    </button>
                </div>
                
                <button
                    onClick={() => handleSendMessage()}
                    disabled={!inputValue.trim() && attachments.length === 0}
                    className={`p-1.5 rounded-full transition-all duration-300 ${
                      inputValue.trim() || attachments.length > 0
                        ? 'bg-tcm-darkGreen text-white shadow-md hover:bg-tcm-lightGreen transform hover:scale-105'
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                    }`}
                >
                    <Icons.Send size={18} className={isLoading ? "animate-pulse" : ""} />
                </button>
             </div>
          </div>
        </div>
      </main>

      {/* 3. RIGHT SIDEBAR */}
      <aside className={`${showRightSidebar ? 'w-80' : 'w-0'} flex-shrink-0 flex flex-col ${isDarkMode ? 'glass-panel-dark' : 'glass-panel'} border-l border-white/50 dark:border-white/10 z-20 shadow-xl transition-all duration-500 overflow-hidden`}>
        <div className="h-16 flex-shrink-0 flex items-center px-6 border-b border-gray-200/50 dark:border-white/10 bg-white/30 dark:bg-black/10">
           <Icons.Leaf className="text-tcm-lightGreen mr-3" size={24} />
           <h1 className="text-lg font-bold text-tcm-darkGreen dark:text-tcm-cream font-serif-sc tracking-wide whitespace-nowrap">智能健康画像</h1>
        </div>

        <div className="flex-1 overflow-y-auto p-6 relative w-80">
           <div className="space-y-4 relative z-10">
              <div className="bg-white/60 dark:bg-white/5 p-4 rounded-xl border border-white dark:border-white/10 shadow-sm backdrop-blur-sm">
                <div className="flex justify-between items-end mb-2">
                  <span className="text-sm font-bold text-gray-600 dark:text-gray-300">体质健康分</span>
                  <span className="text-3xl font-serif-sc font-bold text-tcm-darkGreen dark:text-tcm-lightGreen">{healthScore}</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 h-2 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-tcm-lightGreen to-tcm-gold transition-all duration-1000" style={{width: `${healthScore}%`}}></div>
                </div>
              </div>

              {(Object.keys(persona) as Array<keyof UserPersona>).map((key) => (
                <div
                  key={key}
                  className={`p-3 rounded-lg border transition-all duration-700 ${
                    changedFields.includes(key) 
                      ? 'bg-tcm-gold/20 border-tcm-gold transform scale-105' 
                      : 'bg-white/40 dark:bg-white/5 border-transparent hover:border-tcm-lightGreen/30'
                  }`}
                >
                  <div className="text-[10px] text-gray-500 dark:text-gray-400 uppercase mb-1 flex items-center gap-1">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                    {changedFields.includes(key) && <span className="w-2 h-2 bg-tcm-accent rounded-full animate-ping"></span>}
                  </div>
                  <div className="font-serif-sc text-tcm-darkGreen dark:text-tcm-cream text-sm font-medium leading-relaxed">
                    {persona[key] || "未录入"}
                  </div>
                </div>
              ))}
           </div>
        </div>
      </aside>

      {/* Edit Profile Modal */}
      {isEditingProfile && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
           <div className="bg-white dark:bg-tcm-charcoal rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-fade-in-up border border-tcm-lightGreen/20">
              <div className="p-6 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
                 <h2 className="text-xl font-bold text-tcm-darkGreen dark:text-tcm-cream font-serif-sc">修改健康档案</h2>
                 <button onClick={() => setIsEditingProfile(false)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"><Icons.X /></button>
              </div>
              <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
                 <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1">年龄</label>
                      <input type="text" value={editPersonaForm.age} onChange={e => setEditPersonaForm({...editPersonaForm, age: e.target.value})} className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg dark:text-white focus:ring-1 focus:ring-tcm-lightGreen outline-none" />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1">性别</label>
                      <input type="text" value={editPersonaForm.gender} onChange={e => setEditPersonaForm({...editPersonaForm, gender: e.target.value})} className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg dark:text-white focus:ring-1 focus:ring-tcm-lightGreen outline-none" />
                    </div>
                 </div>
                 <div>
                    <label className="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1">既往病史</label>
                    <textarea value={editPersonaForm.medicalHistory} onChange={e => setEditPersonaForm({...editPersonaForm, medicalHistory: e.target.value})} className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg h-24 dark:text-white focus:ring-1 focus:ring-tcm-lightGreen outline-none" />
                 </div>
              </div>
              <div className="p-6 bg-gray-50 dark:bg-black/10 flex justify-end gap-3">
                 <button onClick={() => setIsEditingProfile(false)} className="px-6 py-2 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-white/5 rounded-lg">取消</button>
                 <button onClick={() => { setPersona(editPersonaForm); setIsEditingProfile(false); }} className="px-6 py-2 bg-tcm-darkGreen text-white rounded-lg hover:bg-tcm-lightGreen shadow-lg">保存更改</button>
              </div>
           </div>
        </div>
      )}
    </div>
  );
};

const toggleTheme = () => {}; // 占位逻辑，已在组件内部实现

export default PublicPortal;
