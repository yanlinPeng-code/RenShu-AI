import React, { useState, useEffect, useRef } from 'react';
import { User, ChatMessage, UserPersona, AVAILABLE_MODELS, AIModelConfig } from '../../types/types';
import { Icons } from '../../components/common/Icons';
import { createPublicChat, analyzeUserPersona, sendMessageWithConfig } from '../../services/geminiService';
import { Chat } from "@google/genai";

interface PublicPortalProps {
  user: User;
  onLogout: () => void;
}

interface Attachment {
  file: File;
  previewUrl: string;
  base64: string;
}

// Mock History
const MOCK_HISTORY = [
  { id: '1', title: '季节性过敏建议', date: '今天' },
  { id: '2', title: '睡眠周期分析', date: '昨天' },
  { id: '3', title: '饮食建议', date: '10月24日' },
];

const PublicPortal: React.FC<PublicPortalProps> = ({ user, onLogout }) => {
  // Chat & AI State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isPersonaAnalyzing, setIsPersonaAnalyzing] = useState(false);
  const [showHistory, setShowHistory] = useState(true);
  
  // Settings & Toggles
  const [selectedModel, setSelectedModel] = useState<AIModelConfig>(AVAILABLE_MODELS[0]);
  const [enableDeepThink, setEnableDeepThink] = useState(false);
  const [enableWebSearch, setEnableWebSearch] = useState(false);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  
  // User Profile State
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [persona, setPersona] = useState<UserPersona>(user.persona || {
    age: 'Unknown',
    gender: 'Unknown',
    chiefComplaint: 'Pending...',
    medicalHistory: 'None recorded',
    suspectedDiagnosis: 'Analysis pending',
    contraindications: 'None known',
    recommendedTreatment: 'Wellness advice'
  });
  const [editPersonaForm, setEditPersonaForm] = useState<UserPersona>(persona);

  // Animation State
  const [changedFields, setChangedFields] = useState<string[]>([]);
  const [healthScore, setHealthScore] = useState(user.healthScore || 85);
  
  const chatRef = useRef<Chat | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- Initialization ---
  useEffect(() => {
    // Reset chat when model changes
    chatRef.current = createPublicChat(selectedModel.id);
    setMessages([{
      id: 'init',
      role: 'model',
      text: `您好 ${user.name}。我正在使用 ${selectedModel.name}。您今天感觉如何？`,
      timestamp: new Date()
    }]);
  }, [user.name, selectedModel]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // --- Handlers ---

  const handleSendMessage = async () => {
    if ((!inputValue.trim() && attachments.length === 0) || !chatRef.current) return;

    // Prepare User Message
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

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    const currentAttachments = [...attachments];
    setAttachments([]); // Clear attachments immediately
    setIsLoading(true);
    setIsPersonaAnalyzing(true);

    try {
      // Prepare file parts for API
      const fileParts = currentAttachments.map(a => ({
        data: a.base64.split(',')[1], // Remove 'data:mime;base64,' prefix
        mimeType: a.file.type
      }));

      // Send to Chat with Config
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
        text: response.text || "No response text generated.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, modelMsg]);

      // Update Persona (Background)
      analyzeUserPersona(userMsg.text, persona).then(newPersona => {
        const changes: string[] = [];
        (Object.keys(newPersona) as Array<keyof UserPersona>).forEach(key => {
          if (newPersona[key] !== persona[key]) changes.push(key);
        });

        if (changes.length > 0) {
          setChangedFields(changes);
          setPersona(newPersona);
          setHealthScore(prev => Math.max(0, Math.min(100, prev + (Math.random() > 0.5 ? 1 : -1))));
          setTimeout(() => setChangedFields([]), 2500);
        }
        setIsPersonaAnalyzing(false);
      });

    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'model',
        text: "很抱歉，我目前在连接AI服务时遇到问题。",
        timestamp: new Date()
      }]);
      setIsPersonaAnalyzing(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceInput = () => {
    // Basic Web Speech API Implementation
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-US'; // Could make this dynamic
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setInputValue(prev => prev + " (正在聆听...)");
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(prev => prev.replace(" (正在聆听...)", "") + " " + transcript);
      };

      recognition.onerror = () => {
        setInputValue(prev => prev.replace(" (Listening...)", ""));
        alert("语音识别错误。");
      };

      recognition.start();
    } else {
      alert("此浏览器不支持语音识别。");
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (ev) => {
        if (ev.target?.result) {
          setAttachments(prev => [...prev, {
            file,
            previewUrl: URL.createObjectURL(file),
            base64: ev.target.result as string
          }]);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSaveProfile = () => {
    setPersona(editPersonaForm);
    setIsEditingProfile(false);
  };

  // --- Components ---

  const InfoItem = ({ fieldKey, label, value, icon: Icon, isAlert = false }: { fieldKey: string, label: string, value: string, icon?: any, isAlert?: boolean }) => {
    const isChanged = changedFields.includes(fieldKey);
    return (
      <div className={`mb-4 last:mb-0 transition-all duration-500 ${isChanged ? 'transform scale-105' : ''}`}>
        <div className="flex items-center gap-2 mb-1">
          {Icon && <Icon size={14} className={isAlert ? "text-red-500" : "text-tcm-lightGreen"} />}
          <span className="text-xs font-bold uppercase tracking-wider text-gray-400">{label}</span>
          {isChanged && <span className="ml-auto w-2 h-2 rounded-full bg-tcm-gold animate-ping"></span>}
        </div>
        <div className={`text-sm font-medium leading-snug rounded transition-colors duration-1000 ${isAlert ? "text-red-700 bg-red-50 border border-red-100 p-2" : "text-tcm-darkGreen"} ${isChanged && !isAlert ? "bg-tcm-gold/20 p-2 text-black" : ""}`}>
          {value || "—"}
        </div>
      </div>
    );
  };

  return (
    <div className="w-full h-full flex flex-col bg-tcm-cream overflow-hidden relative">
      
      {/* Edit Profile Modal */}
      {isEditingProfile && (
        <div className="absolute inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
            <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-tcm-cream">
              <h3 className="text-lg font-bold text-tcm-darkGreen font-serif-sc flex items-center gap-2">
                <Icons.Edit3 size={18} /> 编辑个人资料
              </h3>
              <button onClick={() => setIsEditingProfile(false)} className="text-gray-400 hover:text-gray-600"><Icons.X size={20}/></button>
            </div>
            <div className="p-6 space-y-4 overflow-y-auto custom-scrollbar">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-gray-500 mb-1">年龄</label>
                  <input value={editPersonaForm.age} onChange={e => setEditPersonaForm({...editPersonaForm, age: e.target.value})} className="w-full p-2 border rounded-lg focus:ring-tcm-gold" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 mb-1">性别</label>
                  <select value={editPersonaForm.gender} onChange={e => setEditPersonaForm({...editPersonaForm, gender: e.target.value})} className="w-full p-2 border rounded-lg focus:ring-tcm-gold bg-white">
                    <option value="Male">男</option>
                    <option value="Female">女</option>
                    <option value="Other">其他</option>
                    <option value="Unknown">未知</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1">主诉</label>
                <input value={editPersonaForm.chiefComplaint} onChange={e => setEditPersonaForm({...editPersonaForm, chiefComplaint: e.target.value})} className="w-full p-2 border rounded-lg focus:ring-tcm-gold" />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1">病史</label>
                <textarea value={editPersonaForm.medicalHistory} onChange={e => setEditPersonaForm({...editPersonaForm, medicalHistory: e.target.value})} className="w-full p-2 border rounded-lg focus:ring-tcm-gold h-20" />
              </div>
              <div>
                 <label className="block text-xs font-bold text-gray-500 mb-1">禁忌症</label>
                 <input value={editPersonaForm.contraindications} onChange={e => setEditPersonaForm({...editPersonaForm, contraindications: e.target.value})} className="w-full p-2 border rounded-lg focus:ring-tcm-gold" />
              </div>
            </div>
            <div className="p-4 border-t border-gray-100 bg-gray-50 flex justify-end gap-3 mt-auto">
               <button onClick={() => setIsEditingProfile(false)} className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-200 rounded-lg">取消</button>
               <button onClick={handleSaveProfile} className="px-6 py-2 text-sm bg-tcm-darkGreen text-white rounded-lg hover:bg-green-800">保存更改</button>
            </div>
          </div>
        </div>
      )}

      {/* Navbar */}
      <header className="h-16 bg-white/80 backdrop-blur-md border-b border-tcm-gold/20 flex items-center justify-between px-6 z-20 sticky top-0 shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-tcm-darkGreen flex items-center justify-center text-tcm-gold font-serif-sc font-bold">仁</div>
            <span className="text-xl font-bold text-tcm-darkGreen font-serif-sc hidden md:block">仁术公众版</span>
          </div>
          
          {/* Model Selector Dropdown */}
          <div className="relative group ml-4">
             <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">
               <Icons.BrainCircuit size={14} />
             </div>
             <select 
               className="bg-gray-100 hover:bg-white border border-transparent hover:border-gray-300 text-gray-700 text-sm rounded-full pl-9 pr-8 py-1.5 focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen/50 focus:bg-white transition-all appearance-none cursor-pointer font-medium"
               value={selectedModel.id}
               onChange={(e) => setSelectedModel(AVAILABLE_MODELS.find(m => m.id === e.target.value) || AVAILABLE_MODELS[0])}
             >
               {AVAILABLE_MODELS.map(model => (
                 <option key={model.id} value={model.id}>
                   {model.name}
                 </option>
               ))}
             </select>
             <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-gray-500">
               <Icons.ChevronRight size={14} className="rotate-90" />
             </div>
          </div>
        </div>
        
        {/* Right side is empty now, user settings moved to sidebar */}
        <div className="w-8"></div> 
      </header>

      <div className="flex-1 flex overflow-hidden relative">
        {/* 1. History Sidebar (Left) */}
        <div className={`bg-gray-50 border-r border-gray-200 flex flex-col transition-all duration-300 ease-in-out ${showHistory ? 'w-64 opacity-100' : 'w-0 opacity-0 overflow-hidden'}`}>
             <div className="p-4 border-b border-gray-100 flex items-center justify-between shrink-0">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider whitespace-nowrap">聊天历史</span>
                <button 
                   onClick={() => setShowHistory(false)}
                   className="text-gray-400 hover:text-gray-600"
                >
                   <Icons.PanelLeft size={20} />
                </button>
             </div>
             
             {/* History List - Grows to take available space */}
             <div className="p-3 flex-1 overflow-y-auto custom-scrollbar">
               <button 
                 onClick={() => { setMessages([]); setInputValue(''); }}
                 className="w-full flex items-center gap-2 px-3 py-2 bg-tcm-darkGreen text-white rounded-lg text-sm hover:bg-green-800 transition-colors shadow-sm mb-4 whitespace-nowrap"
               >
                 <Icons.MessageSquare size={16} /> 新建聊天
               </button>
               
               <div className="space-y-1">
                 {MOCK_HISTORY.map((item) => (
                   <button key={item.id} className="w-full text-left px-3 py-2 rounded-lg text-sm text-gray-600 hover:bg-white hover:shadow-sm transition-all truncate group">
                     <span className="block truncate">{item.title}</span>
                     <span className="text-[10px] text-gray-400">{item.date}</span>
                   </button>
                 ))}
               </div>
             </div>

             {/* User Profile - Fixed at bottom left */}
             <div className="p-4 border-t border-gray-200 bg-white shrink-0 relative">
               <button 
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center gap-3 w-full hover:bg-gray-50 p-2 rounded-lg transition-colors group"
                >
                  <img src={user.avatar} alt="User" className="w-9 h-9 rounded-full border border-gray-200 object-cover shrink-0" />
                  <div className="flex-1 min-w-0 text-left">
                    <span className="block text-sm font-bold text-gray-700 group-hover:text-tcm-darkGreen truncate">{user.name}</span>
                    <span className="block text-[10px] text-gray-400 font-medium uppercase tracking-wider">我的账户</span>
                  </div>
                  <Icons.ChevronRight size={14} className={`text-gray-400 transition-transform ${showUserMenu ? '-rotate-90' : ''}`} />
               </button>

               {/* Pop-up Menu (Above the profile) */}
               {showUserMenu && (
                  <div className="absolute bottom-full left-2 right-2 mb-2 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-50 animate-in fade-in slide-in-from-bottom-2">
                    <button 
                      onClick={() => {
                        setEditPersonaForm(persona);
                        setIsEditingProfile(true);
                        setShowUserMenu(false);
                      }}
                      className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3 border-b border-gray-50"
                    >
                      <Icons.Edit3 size={16} className="text-tcm-gold"/> 编辑个人资料
                    </button>
                    <button onClick={onLogout} className="w-full text-left px-4 py-3 text-sm text-red-600 hover:bg-red-50 flex items-center gap-3">
                      <Icons.LogOut size={16}/> 退出登录
                    </button>
                  </div>
               )}
             </div>
        </div>

        {/* 2. Main Chat Area (Middle) */}
        <main className="flex-1 flex flex-col relative bg-gray-50/50 min-w-0">
           {/* Sidebar Toggle Button (Floating) - Only visible when history is hidden */}
           {!showHistory && (
             <div className="absolute top-4 left-4 z-20">
                <button 
                   onClick={() => setShowHistory(true)}
                   className="p-2 bg-white/80 hover:bg-white text-gray-500 hover:text-tcm-darkGreen rounded-lg shadow-sm border border-gray-200 transition-all backdrop-blur-sm"
                   title="Show History"
                >
                   <Icons.PanelLeft size={20} />
                </button>
             </div>
           )}

          <div className="flex-1 overflow-y-auto p-4 md:p-8 pt-16 md:pt-8">
            <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                <div className={`max-w-[85%] md:max-w-[70%] p-5 rounded-2xl shadow-sm text-sm md:text-base leading-relaxed relative ${msg.role === 'user' ? 'bg-tcm-darkGreen text-white rounded-br-none shadow-md' : 'bg-white text-gray-800 border border-gray-100 rounded-bl-none shadow-sm'}`}>
                  {msg.role === 'model' && (
                    <div className="absolute -left-10 top-0 w-8 h-8 bg-tcm-cream rounded-full flex items-center justify-center border border-tcm-gold/30 hidden md:flex">
                      <span className="text-tcm-darkGreen font-serif-sc font-bold text-xs">仁</span>
                    </div>
                  )}
                  {msg.attachments && msg.attachments.length > 0 && (
                    <div className="flex gap-2 mb-3">
                      {msg.attachments.map((att, idx) => (
                         <div key={idx} className="relative group">
                            {att.type === 'image' ? (
                              <img src={att.url} alt="附件" className="w-24 h-24 object-cover rounded-lg border border-white/20" />
                            ) : (
                              <div className="w-24 h-24 bg-gray-100 rounded-lg flex flex-col items-center justify-center text-gray-500 text-xs p-2 text-center">
                                <Icons.FileText size={20} className="mb-1"/>
                                <span className="truncate w-full">{att.name}</span>
                              </div>
                            )}
                         </div>
                      ))}
                    </div>
                  )}
                  {msg.text}
                </div>
              </div>
            ))}
            {isLoading && (
               <div className="flex justify-start animate-in fade-in">
                 <div className="bg-white p-4 rounded-2xl rounded-bl-none border border-gray-100 flex items-center gap-2 shadow-sm">
                    <div className="w-2 h-2 bg-tcm-lightGreen rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-tcm-lightGreen rounded-full animate-bounce delay-75"></div>
                    <div className="w-2 h-2 bg-tcm-lightGreen rounded-full animate-bounce delay-150"></div>
                 </div>
               </div>
            )}
            <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area Wrapper */}
          <div className="bg-white border-t border-gray-100 shadow-[0_-5px_20px_rgba(0,0,0,0.02)] z-10 p-4 pb-6 md:px-8">
            <div className="max-w-4xl mx-auto w-full">
              
              {/* Toolbar: Thinking & Search - Aligned Top Left of Input Box */}
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

              {/* Attachment Preview */}
              {attachments.length > 0 && (
                <div className="flex gap-3 mb-3 px-1 overflow-x-auto">
                  {attachments.map((att, idx) => (
                    <div key={idx} className="relative group shrink-0">
                      <img src={att.previewUrl} className="w-16 h-16 object-cover rounded-lg border border-gray-200" alt="preview"/>
                      <button 
                        onClick={() => setAttachments(prev => prev.filter((_, i) => i !== idx))}
                        className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full p-0.5 shadow-md hover:bg-red-600"
                      >
                        <Icons.X size={12}/>
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Main Input Bar */}
              <div className="relative flex items-end gap-2 bg-gray-50 border border-gray-200 rounded-3xl p-2 transition-shadow focus-within:ring-2 focus-within:ring-tcm-lightGreen/50 focus-within:bg-white focus-within:shadow-md">
                
                {/* Left Actions (Upload & Voice) */}
                <div className="flex items-center gap-1 pb-2 pl-2">
                   <input type="file" multiple ref={fileInputRef} className="hidden" onChange={handleFileUpload} accept="image/*,.pdf,.txt" />
                   <button 
                      onClick={() => fileInputRef.current?.click()} 
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors" 
                      title="附加文件"
                   >
                      <Icons.Paperclip size={20} />
                   </button>
                   <button 
                      onClick={handleVoiceInput} 
                      className="p-2 text-gray-400 hover:text-tcm-darkGreen hover:bg-gray-100 rounded-full transition-colors" 
                      title="语音输入"
                   >
                      <Icons.Mic size={20} />
                   </button>
                </div>

                <textarea 
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  placeholder={`询问 ${selectedModel.name}... (Shift+Enter 换行)`}
                  className="flex-1 bg-transparent border-none text-gray-800 px-3 py-3 focus:ring-0 max-h-32 resize-none text-sm md:text-base placeholder-gray-400"
                  rows={1}
                  style={{minHeight: '44px'}}
                />
                
                <button 
                  onClick={handleSendMessage}
                  disabled={(!inputValue.trim() && attachments.length === 0) || isLoading}
                  className="mb-1 mr-1 bg-gradient-to-br from-tcm-gold to-yellow-600 text-white rounded-full p-3 shadow-lg hover:shadow-xl transition-all active:scale-95 disabled:opacity-50 disabled:scale-100 disabled:shadow-none flex items-center justify-center"
                >
                  {isLoading ? <Icons.Zap size={20} className="animate-pulse"/> : <Icons.Send size={20} />}
                </button>
              </div>
              
              <p className="text-center text-[10px] text-gray-400 mt-2 font-serif-sc uppercase tracking-widest opacity-60">
                仁术AI医疗系统 v2.0
              </p>
            </div>
          </div>
        </main>

        {/* 3. User Persona Sidebar (Right) */}
        <aside className="hidden md:flex flex-col w-[20%] min-w-[260px] bg-white border-l border-gray-200 overflow-y-auto custom-scrollbar z-10">
          <div className="flex-1 p-6">
            <div className="flex items-start gap-4 mb-6 pb-6 border-b border-gray-100 group relative">
              <div className="relative w-16 h-16 shrink-0">
                <img src={user.avatar} className="w-full h-full rounded-full object-cover border-2 border-tcm-cream shadow-sm" />
                <button 
                  onClick={() => { setEditPersonaForm(persona); setIsEditingProfile(true); }}
                  className="absolute -bottom-1 -right-1 bg-white border border-gray-200 rounded-full p-1.5 shadow-sm text-gray-500 hover:text-tcm-darkGreen hover:border-tcm-darkGreen transition-all"
                  title="编辑照片（模拟）"
                >
                  <Icons.Camera size={12} />
                </button>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                   <h3 className="text-lg font-bold text-tcm-darkGreen font-serif-sc truncate">{user.name}</h3>
                   <button 
                     onClick={() => { setEditPersonaForm(persona); setIsEditingProfile(true); }}
                     className="text-gray-400 hover:text-tcm-gold transition-colors"
                     title="编辑详情"
                   >
                     <Icons.Edit3 size={16} />
                   </button>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                  <span className={`bg-gray-100 px-2 py-0.5 rounded text-gray-600 font-medium transition-colors duration-500 ${changedFields.includes('gender') ? 'bg-tcm-gold/30 text-black' : ''}`}>{persona.gender}</span>
                  <span className={`bg-gray-100 px-2 py-0.5 rounded text-gray-600 font-medium transition-colors duration-500 ${changedFields.includes('age') ? 'bg-tcm-gold/30 text-black' : ''}`}>{persona.age !== 'Unknown' ? `${persona.age} 岁` : '年龄?'}</span>
                </div>
              </div>
            </div>

            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                 <span className="text-xs font-bold uppercase text-gray-400">健康活力</span>
                 <span className="text-sm font-bold text-tcm-gold">{healthScore}/100</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2">
                <div className="bg-gradient-to-r from-tcm-lightGreen to-tcm-darkGreen h-2 rounded-full transition-all duration-1000" style={{ width: `${healthScore}%` }}></div>
              </div>
            </div>

            {/* Profile Details */}
            <div className="space-y-1 relative">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-sm font-serif-sc font-bold text-tcm-darkGreen border-l-4 border-tcm-gold pl-2">患者档案</h4>
                {isPersonaAnalyzing && (
                  <div className="flex items-center gap-1 text-xs text-tcm-gold animate-pulse">
                    <Icons.BrainCircuit size={14} className="animate-spin" />
                    更新中...
                  </div>
                )}
              </div>
              <div className="bg-tcm-cream/30 p-4 rounded-xl border border-tcm-gold/10 space-y-4">
                 <InfoItem fieldKey="chiefComplaint" label="主诉" value={persona.chiefComplaint} icon={Icons.Activity} />
                 <InfoItem fieldKey="suspectedDiagnosis" label="疑似诊断" value={persona.suspectedDiagnosis} icon={Icons.Stethoscope} />
                 <InfoItem fieldKey="medicalHistory" label="病史" value={persona.medicalHistory} icon={Icons.FileText} />
                 <InfoItem fieldKey="contraindications" label="禁忌症" value={persona.contraindications} icon={Icons.ShieldPlus} isAlert={true} />
                 <div className={`pt-2 border-t border-tcm-gold/20 mt-2 transition-all duration-500 ${changedFields.includes('recommendedTreatment') ? 'scale-105' : ''}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <Icons.Leaf size={14} className="text-tcm-gold" />
                      <span className="text-xs font-bold uppercase tracking-wider text-gray-400">推荐护理</span>
                    </div>
                    <div className={`text-sm text-tcm-darkGreen bg-white p-3 rounded-lg border border-gray-100 shadow-sm leading-relaxed italic font-serif-sc transition-colors duration-1000 ${changedFields.includes('recommendedTreatment') ? 'bg-tcm-gold/10 border-tcm-gold/50' : ''}`}>
                      "{persona.recommendedTreatment}"
                    </div>
                 </div>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default PublicPortal;