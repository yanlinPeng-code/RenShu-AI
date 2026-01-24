import React, { useState, useEffect } from 'react';
import { User } from '../../types';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';
import { LogoutConfirmModal } from '../../components/common/LogoutConfirmModal';
import { DeleteConfirmToast } from '../../components/common/DeleteConfirmToast';
import { Toast } from '../../components/common/Toast';
import { providerApi, modelApi } from '../../api/modules/model';
import { ModelProviderCreate, ModelProviderUpdate, ModelConfigCreate, ModelConfigUpdate } from '../../api/types';



interface AdminPortalProps {
  user: User;
  onLogout: () => void;
}



type AdminView = 'dashboard' | 'models' | 'stats' | 'knowledge';

const AdminPortal: React.FC<AdminPortalProps> = ({ user, onLogout }) => {
  const [activeView, setActiveView] = useState<AdminView>('dashboard');
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  // 供应商和模型配置状态
  const [providers, setProviders] = useState<any[]>([]);
  const [selectedProviderId, setSelectedProviderId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // 模态框状态
  const [showProviderModal, setShowProviderModal] = useState(false);
  const [showModelModal, setShowModelModal] = useState(false);
  const [editingProvider, setEditingProvider] = useState<any | null>(null);
  const [editingModel, setEditingModel] = useState<any | null>(null);
  // 删除确认相关状态
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);
  const [deleteTarget, setDeleteTarget] = useState<{type: 'provider' | 'model', id: string} | null>(null);
  // Toast 提示状态
  const [toast, setToast] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  // 表单数据
  const [providerForm, setProviderForm] = useState<ModelProviderCreate & {is_enabled?: boolean}>({
    name: '', label: '', description: '', icon: '', base_url: '', supported_model_types: [], is_enabled: true
  });
  const [modelForm, setModelForm] = useState<ModelConfigCreate & {is_enabled?: boolean}>({
    model_name: '', label: '', description: '', model_type: 'llm', features: [],
    context_window: undefined, default_max_tokens: undefined,
    default_temperature: 0.7, default_top_p: 1.0, is_enabled: true
  });

  // 获取供应商和模型数据（管理员模板）
  const fetchProvidersWithModels = async (deletedProviderId?: string) => {
    setLoading(true);
    try {
      // 修改：使用 get_providers_with_models() 获取管理员模板
      // 后端会自动识别管理员角色，返回管理员模板（user_id=None）
      const res = await providerApi.get_providers_with_models();
      if (res.success === true) {
        // 如果有供应商数据
        if (res.data.length > 0) {
          // 如果传入了被删除的供应商ID，或者当前选中的供应商不在新数据中
          const shouldReselect = deletedProviderId === selectedProviderId ||
            !res.data.some((p: any) => p.id === selectedProviderId);
          if (!selectedProviderId || shouldReselect) {
            // 先更新选中状态，再更新列表
            setSelectedProviderId(res.data[0].id);
          }
          setProviders(res.data);
        } else {
          console.log('获取供应商列表成功:else', res.data)
          setProviders([]);
          // 如果没有供应商了，先清空选中状态，再清空列表
          setSelectedProviderId(null);
          
        }
      }
    } catch (error) {
      console.error('获取供应商列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeView === 'models') {
      fetchProvidersWithModels();
    }
  }, [activeView]);

  // 获取当前选中供应商
  const selectedProvider = providers.find(p => p.id === selectedProviderId);

 

  // 供应商操作
  const handleCreateProvider = async () => {
    try {
      const createData: ModelProviderCreate = {
        ...providerForm,
        position: providers.length + 1
      };
      const res = await providerApi.create(createData);
      console.log('创建供应商成功:', res);
      if (res.success === true) {
        setShowProviderModal(false);
        setProviderForm({ name: '', label: '', description: '', icon: '', base_url: '', supported_model_types: [], is_enabled: true });
        setTimeout(() => fetchProvidersWithModels(), 100);
      }
    } catch (error) {
      console.error('创建供应商失败:', error);
    }
  };

  const handleUpdateProvider = async () => {
    if (!editingProvider) return;
    try {
      const updateData: ModelProviderUpdate = {
        provider_id: editingProvider.id,
        label: providerForm.label, // Include label in update
        description: providerForm.description,
        icon: providerForm.icon,
        base_url: providerForm.base_url,
        supported_model_types: providerForm.supported_model_types,
        is_enabled: providerForm.is_enabled
      };
      const res = await providerApi.update(updateData);
      if (res.success === true) {
        setShowProviderModal(false);
        setEditingProvider(null);
        setProviderForm({ name: '', label: '', description: '', icon: '', base_url: '', supported_model_types: [], is_enabled: true });
        setTimeout(() => fetchProvidersWithModels(), 100);
      }
    } catch (error) {
      console.error('更新供应商失败:', error);
    }
  };

  const handleDeleteProvider = async (providerId: string) => {
    // 显示删除确认Toast
    setDeleteTarget({ type: 'provider', id: providerId });
    setShowDeleteConfirm(true);
  };

  const confirmDeleteProvider = async (providerId: string) => {
    try {
      const res = await providerApi.delete({ provider_id: providerId, role: 'admin' } as any);
      if (res.success === true) {
        setToast({ message: '供应商删除成功', type: 'success' });
        // 传入被删除的供应商ID，让fetchProvidersWithModels正确处理选中状态
        console.log('传入的被删除的供应商ID:', providerId);
        fetchProvidersWithModels(providerId);
      } else {
        setToast({ message: '删除供应商失败', type: 'error' });
      }
    } catch (error) {
      console.error('删除供应商失败:', error);
      setToast({ message: '删除供应商失败', type: 'error' });
    }
    setShowDeleteConfirm(false);
    setDeleteTarget(null);
  };

  const openEditProviderModal = (provider: any) => {
    setEditingProvider(provider);
    setProviderForm({
      name: provider.name,
      label: provider.label || '',
      description: provider.description || '',
      icon: provider.icon || '',
      base_url: provider.base_url || '',
      supported_model_types: provider.supported_model_types || [],
      is_enabled: provider.is_enabled !== false
    });
    setShowProviderModal(true);
  };

  // 模型配置操作
  const handleCreateModel = async () => {
    if (!selectedProviderId || !selectedProvider) return;
    try {
      const currentModelsCount = selectedProvider.models?.length || 0;
      const createData: ModelConfigCreate = {
        ...modelForm,
        provider_id: selectedProviderId,
        position: currentModelsCount + 1,
        label: modelForm.label || modelForm.model_name // Ensure label is passed, fallback to model_name if empty
      };
      const res = await modelApi.create(createData);
      if (res.success === true) {
        setShowModelModal(false);
        setModelForm({
          model_name: '', label: '', description: '', model_type: 'llm', features: [],
          context_window: 4096, default_max_tokens: 4096, default_temperature: 0.7, default_top_p: 1.0, is_enabled: true
        });
        setTimeout(() => fetchProvidersWithModels(), 100);
      }
    } catch (error) {
      console.error('创建模型配置失败:', error);
    }
  };

  const handleUpdateModel = async () => {
    if (!editingModel) return;
    try {
      const updateData: any = {
        model_config_id: editingModel.id,
        role: 'admin',
        description: modelForm.description,
        model_type: modelForm.model_type,
        label: modelForm.label, // Include label in update
        features: modelForm.features, // Ensure features are included in the update payload
        context_window: modelForm.context_window,
        default_max_tokens: modelForm.default_max_tokens,
        default_temperature: modelForm.default_temperature,
        default_top_p: modelForm.default_top_p,
        is_enabled: modelForm.is_enabled
      };
      const res = await modelApi.update(updateData);
      if (res.success === true) {
        setShowModelModal(false);
        setEditingModel(null);
        setModelForm({
          model_name: '', label: '', description: '', model_type: 'llm', features: [],
          context_window: 4096, default_max_tokens: 4096, default_temperature: 0.7, default_top_p: 1.0
        });
        setTimeout(() => fetchProvidersWithModels(), 100);
      }
    } catch (error) {
      console.error('更新模型配置失败:', error);
    }
  };

  const handleDeleteModel = async (modelId: string) => {
    // 显示删除确认Toast
    setDeleteTarget({ type: 'model', id: modelId });
    setShowDeleteConfirm(true);
  };

  const confirmDeleteModel = async (modelId: string) => {
    try {
      const res = await modelApi.delete({ model_config_id: modelId, role: 'admin' } as any);
      if (res.success === true) {
        setToast({ message: '模型配置删除成功', type: 'success' });
        fetchProvidersWithModels();
      } else {
        setToast({ message: '删除模型配置失败', type: 'error' });
      }
    } catch (error) {
      console.error('删除模型配置失败:', error);
      setToast({ message: '删除模型配置失败', type: 'error' });
    }
    setShowDeleteConfirm(false);
    setDeleteTarget(null);
  };

  const openEditModelModal = (model: any) => {
    setEditingModel(model);
    setModelForm({
      model_name: model.model_name,
      label: model.label || '',
      description: model.description || '',
      model_type: model.model_type || 'llm',
      features: model.features || [],
      context_window: model.context_window,
      default_temperature: model.default_temperature ?? 0.7,
      default_top_p: model.default_top_p ?? 1.0,
      default_max_tokens: model.default_max_tokens,
      is_enabled: model.is_enabled !== false
    });
    setShowModelModal(true);
  };

  // --- 子模块组件 ---

  const DashboardHome = () => (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard label="总请求量" value="284,102" trend="+12.5%" icon={Icons.Zap} color="text-blue-500" />
        <StatCard label="平均延迟" value="1.24s" trend="-5%" icon={Icons.Activity} color="text-emerald-500" />
        <StatCard label="令牌摄入量" value="1.4M" trend="+8%" icon={Icons.BrainCircuit} color="text-indigo-500" />
        <StatCard label="系统健康度" value="99.98%" trend="最优" icon={Icons.Check} color="text-tcm-gold" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            实时流量监控
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
           <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-6">关键系统日志</h3>
           <div className="space-y-3 font-mono">
              <LogLine time="14:20:01" type="信息" msg="模型 'gemini-3-pro' 更新到版本0925" />
              <LogLine time="14:15:22" type="警告" msg="检测到亚洲地区延迟峰值" />
              <LogLine time="14:02:45" type="认证" msg="管理员 'Root' 修改知识库: TCM_Core" />
              <LogLine time="13:55:10" type="成功" msg="计划的向量重新索引已完成" />
              <LogLine time="13:40:02" type="信息" msg="系统心跳脉冲: 62ms" />
           </div>
        </div>
      </div>
    </div>
  );

  const ModelConfig = () => (
    <div className="flex gap-6 h-full animate-in fade-in duration-500">
      {/* 左侧：供应商列表 */}
      <div className="w-72 flex-shrink-0 bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden flex flex-col">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center">
          <h3 className="text-xs font-bold text-white uppercase tracking-widest">模型供应商</h3>
          <button
            onClick={() => { setEditingProvider(null); setProviderForm({ name: '', label: '', description: '', icon: '', base_url: '', supported_model_types: [], is_enabled: true }); setShowProviderModal(true); }}
            className="p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
          >
            <Icons.Plus size={14} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : providers.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-xs">暂无供应商</div>
          ) : (
            providers.map((provider) => (
              <div
                key={provider.id}
                className={`p-3 rounded-xl cursor-pointer transition-all group ${
                  selectedProviderId === provider.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-950 hover:bg-slate-800 text-slate-300'
                }`}
                onClick={() => setSelectedProviderId(provider.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-lg ${
                      selectedProviderId === provider.id ? 'bg-white/20' : 'bg-slate-800'
                    }`}>
                      {provider.icon || '🤖'}
                    </div>
                    <div>
                      <div className="text-xs font-bold">{provider.label || provider.name}</div>
                      <div className={`text-[10px] ${selectedProviderId === provider.id ? 'text-blue-200' : 'text-slate-500'}`}>
                        {provider.models?.length || 0} 个模型
                      </div>
                    </div>
                  </div>
                  <div className={`flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity ${selectedProviderId === provider.id ? 'opacity-100' : ''}`}>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        const updateData: any = {
                          provider_id: provider.id,
                          role: 'admin',
                          is_enabled: !provider.is_enabled
                        };
                        providerApi.update(updateData).then(() => fetchProvidersWithModels());
                      }}
                      className={`relative inline-flex h-4 w-7 items-center rounded-full transition-colors ${
                        provider.is_enabled !== false ? 'bg-emerald-500' : 'bg-slate-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                          provider.is_enabled !== false ? 'translate-x-3.5' : 'translate-x-0.5'
                        }`}
                      />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); openEditProviderModal(provider); }}
                      className="p-1.5 hover:bg-white/20 rounded transition-colors"
                    >
                      <Icons.Edit3 size={12} />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeleteProvider(provider.id); }}
                      className="p-1.5 hover:bg-red-500/50 rounded transition-colors"
                    >
                      <Icons.Trash2 size={12} />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 右侧：模型配置列表 */}
      <div className="flex-1 bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden flex flex-col">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center">
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-widest">
              {selectedProvider ? `${selectedProvider.label || selectedProvider.name} 的模型配置` : '请选择供应商'}
            </h3>
            {selectedProvider?.description && (
              <p className="text-[10px] text-slate-500 mt-1">{selectedProvider.description}</p>
            )}
          </div>
          {selectedProviderId && (
            <button
              onClick={() => { setShowModelModal(false); setEditingModel(null); setModelForm({ model_name: '', label: '', description: '', model_type: 'llm', features: [], context_window: 4096, default_max_tokens: 4096, default_temperature: 0.7, default_top_p: 1.0, is_enabled: true }); setShowModelModal(true); }}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-[10px] font-bold rounded-lg uppercase tracking-widest flex items-center gap-2 transition-colors"
            >
              <Icons.Plus size={14} /> 添加模型
            </button>
          )}
        </div>
        <div className="flex-1 overflow-y-auto">
          {!selectedProviderId ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <Icons.BrainCircuit size={48} className="mb-4 opacity-30" />
              <p className="text-xs">请先选择一个供应商</p>
            </div>
          ) : !selectedProvider?.models || selectedProvider.models.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <Icons.Package size={48} className="mb-4 opacity-30" />
              <p className="text-xs">该供应商下暂无模型配置</p>
              <p className="text-[10px] mt-1">点击上方"添加模型"按钮创建</p>
            </div>
          ) : (
            <table className="w-full text-left text-xs text-slate-400">
              <thead className="bg-slate-950 text-slate-500 font-bold uppercase tracking-widest sticky top-0">
                <tr>
                  <th className="p-4">模型名称</th>
                  <th className="p-4">类型</th>
                  <th className="p-4">特性</th>
                  <th className="p-4">上下文窗口</th>
                  <th className="p-4">最大Token</th>
                  <th className="p-4">温度</th>
                  <th className="p-4">Top P</th>
                  <th className="p-4">状态</th>
                  <th className="p-4">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {selectedProvider.models.map((model: any) => (
                  <tr key={model.id} className="hover:bg-blue-500/5 transition-colors group">
                    <td className="p-4">
                      <div className="font-bold text-white group-hover:text-blue-400 transition-colors">{model.model_name}</div>
                      {model.description && (
                        <div className="text-[10px] text-slate-600 mt-0.5 truncate max-w-[200px]">{model.description}</div>
                      )}
                    </td>
                    <td className="p-4">
                      <span className="px-2 py-0.5 bg-slate-800 rounded text-[9px] uppercase font-bold">
                        {model.model_type || 'llm'}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex flex-wrap gap-1 max-w-[150px]">
                        {model.features && model.features.length > 0 ? (
                          model.features.slice(0, 3).map((feature: string, idx: number) => (
                            <span key={idx} className="px-1.5 py-0.5 bg-blue-500/10 text-blue-400 rounded text-[8px] font-bold uppercase">
                              {feature}
                            </span>
                          ))
                        ) : (
                          <span className="text-slate-600 text-[10px]">-</span>
                        )}
                        {model.features && model.features.length > 3 && (
                          <span className="text-slate-500 text-[8px]">+{model.features.length - 3}</span>
                        )}
                      </div>
                    </td>
                    <td className="p-4 font-mono">{model.context_window?.toLocaleString() || '-'}</td>
                    <td className="p-4 font-mono">{model.default_max_tokens?.toLocaleString() || '-'}</td>
                    <td className="p-4 font-mono">{model.default_temperature ?? '-'}</td>
                    <td className="p-4 font-mono">{model.default_top_p ?? '-'}</td>
                    <td className="p-4">
                      <button
                        type="button"
                        onClick={() => {
                          const updateData: any = {
                            model_config_id: model.id,
                            role: 'admin',
                            is_enabled: !model.is_enabled
                          };
                          modelApi.update(updateData).then(() => fetchProvidersWithModels());
                        }}
                        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                          model.is_enabled !== false ? 'bg-emerald-500' : 'bg-slate-600'
                        }`}
                      >
                        <span
                          className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
                            model.is_enabled !== false ? 'translate-x-4.5' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </td>
                    <td className="p-4">
                      <div className="flex gap-2">
                        <button
                          onClick={() => openEditModelModal(model)}
                          className="p-1.5 text-slate-500 hover:text-white hover:bg-slate-800 rounded transition-colors"
                        >
                          <Icons.Edit3 size={14} />
                        </button>
                        <button
                          onClick={() => handleDeleteModel(model.id)}
                          className="p-1.5 text-slate-500 hover:text-red-500 hover:bg-red-500/10 rounded transition-colors"
                        >
                          <Icons.Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );

  const UsageStats = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-500">
      <div className="lg:col-span-2 bg-slate-900/50 border border-slate-800 p-8 rounded-2xl">
        <div className="flex justify-between items-center mb-10">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">计算资源使用统计</h3>
          <select className="bg-slate-950 border border-slate-800 text-[10px] text-white px-3 py-1 rounded focus:outline-none">
            <option>最近7天</option>
            <option>最近30天</option>
          </select>
        </div>
        <div className="space-y-8">
           <UsageBar label="Gemini 3.0 Pro" percent={85} color="bg-blue-500" val="2.4M 令牌" />
           <UsageBar label="Gemini 3.0 Flash" percent={60} color="bg-emerald-500" val="1.8M 令牌" />
           <UsageBar label="Gemini 2.5 Flash" percent={30} color="bg-indigo-500" val="0.5M 令牌" />
           <UsageBar label="旧版引擎" percent={10} color="bg-slate-600" val="0.1M 令牌" />
        </div>
      </div>

      <div className="bg-slate-900/50 border border-slate-800 p-8 rounded-2xl flex flex-col">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-10">成本分布</h3>
        <div className="flex-1 flex flex-col justify-center items-center">
           <div className="relative w-40 h-40">
             <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#1e293b" strokeWidth="15" />
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#3b82f6" strokeWidth="15" strokeDasharray="251" strokeDashoffset="60" />
             </svg>
             <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="text-[10px] font-bold text-slate-500 uppercase">预估总额</span>
                <span className="text-xl font-bold text-white">$4,120</span>
             </div>
           </div>
           <div className="mt-8 grid grid-cols-2 gap-4 w-full text-[10px] font-bold uppercase">
              <div className="flex items-center gap-2"><div className="w-2 h-2 bg-blue-500"></div> API费用 (75%)</div>
              <div className="flex items-center gap-2"><div className="w-2 h-2 bg-slate-700"></div> 基础设施 (25%)</div>
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
              知识检索存储
            </h2>
            <p className="text-[10px] text-slate-500 font-bold uppercase mt-1">管理的向量数据库索引</p>
          </div>
          <button className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2 rounded-lg text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 transition-all">
            <Icons.UploadCloud size={14} /> 新建语料库
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
      <LogoutConfirmModal
        isOpen={showLogoutModal}
        onConfirm={() => { setShowLogoutModal(false); onLogout(); }}
        onCancel={() => setShowLogoutModal(false)}
        variant="admin"
      />

      {/* 供应商模态框 */}
      {showProviderModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-6">
              {editingProvider ? '编辑供应商' : '添加供应商'}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">名称标识 (英文)</label>
                <input
                  type="text"
                  value={providerForm.name || ''}
                  onChange={(e) => setProviderForm(prev => ({ ...prev, name: e.target.value }))}
                  disabled={!!editingProvider}
                  className="w-full mt-2 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500 disabled:opacity-50"
                  placeholder="如: openai, anthropic"
                />
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">供应商展示名称</label>
                <input
                  type="text"
                  value={providerForm.label || ''}
                  onChange={(e) => setProviderForm(prev => ({ ...prev, label: e.target.value }))}
                  className="w-full mt-2 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500"
                  placeholder="如: OpenAI, Anthropic AI"
                />
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">描述</label>
                <textarea
                  value={providerForm.description || ''}
                  onChange={(e) => setProviderForm(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full mt-2 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500 resize-none"
                  rows={2}
                  placeholder="供应商描述..."
                />
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">默认Base URL</label>
                <input
                  type="text"
                  value={providerForm.base_url || ''}
                  onChange={(e) => setProviderForm(prev => ({ ...prev, base_url: e.target.value }))}
                  className="w-full mt-2 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500"
                  placeholder="https://api.example.com/v1"
                />
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">支持的模型类型</label>
                <div className="flex flex-wrap gap-2">
                  {[
                    { key: 'llm', label: 'LLM' },
                    { key: 'multimodal', label: '多模态' },
                    { key: 'embedding', label: '嵌入' },
                    { key: 'rerank', label: '重排序' },
                    { key: 'image', label: '图像' },
                    { key: 'audio', label: '音频' },
                    { key: 'video', label: '视频' },
                    { key: 'code', label: '代码' }
                  ].map(type => (
                    <button
                      key={type.key}
                      type="button"
                      onClick={() => {
                        const currentTypes = providerForm.supported_model_types || [];
                        const newTypes = currentTypes.includes(type.key)
                          ? currentTypes.filter(t => t !== type.key)
                          : [...currentTypes, type.key];
                        setProviderForm(prev => ({ ...prev, supported_model_types: newTypes }));
                      }}
                      className={`px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all ${
                        (providerForm.supported_model_types || []).includes(type.key)
                          ? 'bg-blue-600 text-white shadow-[0_0_10px_rgba(59,130,246,0.3)]'
                          : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
                      }`}
                    >
                      {type.label}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 block">启用状态</label>
                <button
                  type="button"
                  onClick={() => setProviderForm(prev => ({ ...prev, is_enabled: !prev.is_enabled }))}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    providerForm.is_enabled ? 'bg-blue-600' : 'bg-slate-700'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      providerForm.is_enabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
                <span className="ml-3 text-xs text-slate-400">
                  {providerForm.is_enabled ? '已启用' : '已禁用'}
                </span>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => { setShowProviderModal(false); setEditingProvider(null); setProviderForm({ name: '', label: '', description: '', icon: '', base_url: '', supported_model_types: [], is_enabled: true }); }}
                className="flex-1 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white text-[10px] font-bold rounded-lg uppercase tracking-widest transition-colors"
              >
                取消
              </button>
              <button
                onClick={editingProvider ? handleUpdateProvider : handleCreateProvider}
                className="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-[10px] font-bold rounded-lg uppercase tracking-widest transition-colors"
              >
                {editingProvider ? '更新' : '创建'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 模型配置模态框 */}
      {showModelModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-2xl shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-6">
              {editingModel ? '编辑模型配置' : '添加模型配置'}
            </h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">模型名称 (API调用用)</label>
                  <input
                    type="text"
                    value={modelForm.model_name || ''}
                    onChange={(e) => setModelForm(prev => ({ ...prev, model_name: e.target.value }))}
                    disabled={!!editingModel}
                    className="w-full mt-2 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500 disabled:opacity-50"
                    placeholder="如: gpt-4o, claude-3-opus"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">模型展示名称</label>
                  <input
                    type="text"
                    value={modelForm.label || ''}
                    onChange={(e) => setModelForm(prev => ({ ...prev, label: e.target.value }))}
                    className="w-full mt-2 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500"
                    placeholder="如: GPT-4o, Claude 3 Opus"
                  />
                </div>
              </div>

              <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">模型类型</label>
                  <select
                    value={modelForm.model_type || 'llm'}
                    onChange={(e) => setModelForm(prev => ({ ...prev, model_type: e.target.value, features: [] }))}
                    className="w-full mt-2 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500"
                  >
                    <option value="llm">LLM (大语言模型)</option>
                    <option value="multimodal">Multimodal (多模态)</option>
                    <option value="embedding">Embedding (文本嵌入)</option>
                    <option value="rerank">Rerank (重排序)</option>
                    <option value="image">Image (图像生成)</option>
                    <option value="audio">Audio (音频)</option>
                    <option value="video">Video (视频)</option>
                    <option value="code">Code (代码)</option>
                  </select>
              </div>

              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">描述</label>
                <textarea
                  value={modelForm.description || ''}
                  onChange={(e) => setModelForm(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full mt-2 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500 resize-none"
                  rows={2}
                  placeholder="模型描述..."
                />
              </div>

              {/* 特性选择 - 根据模型类型显示不同选项 */}
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">模型特性</label>
                <div className="flex flex-wrap gap-2">
                  {(() => {
                    const featuresByType: Record<string, {key: string, label: string}[]> = {
                      llm: [
                        { key: 'structured_output', label: '结构化输出' },
                        { key: 'tool_call', label: '工具调用' },
                        { key: 'thinking', label: '思维链' },
                        { key: 'reasoning', label: '推理' },
                        { key: 'streaming', label: '流式输出' },
                      ],
                      multimodal: [
                        { key: 'image_input', label: '图像输入' },
                        { key: 'image_generate', label: '图像生成' },
                        { key: 'tts', label: '文字转语音' },
                        { key: 'speech2text', label: '语音转文字' },
                        { key: 'thinking', label: '思维链' },
                        { key: 'reasoning', label: '推理' },
                        { key: 'tool_call', label: '工具调用' },
                        { key: 'structured_output', label: '结构化输出' },
                      ],
                      embedding: [
                        { key: 'batch', label: '批量处理' },
                        { key: 'sparse', label: '稀疏向量' },
                        { key: 'dense', label: '稠密向量' },
                      ],
                      rerank: [
                        { key: 'batch', label: '批量处理' },
                        { key: 'multilingual', label: '多语言' },
                      ],
                      image: [
                        { key: 'text2img', label: '文生图' },
                        { key: 'img2img', label: '图生图' },
                        { key: 'inpainting', label: '图像修复' },
                        { key: 'upscale', label: '超分辨率' },
                      ],
                      audio: [
                        { key: 'tts', label: '文字转语音' },
                        { key: 'speech2text', label: '语音转文字' },
                        { key: 'voice_clone', label: '声音克隆' },
                        { key: 'music_gen', label: '音乐生成' },
                      ],
                      video: [
                        { key: 'text2video', label: '文生视频' },
                        { key: 'img2video', label: '图生视频' },
                        { key: 'video_edit', label: '视频编辑' },
                      ],
                      code: [
                        { key: 'completion', label: '代码补全' },
                        { key: 'generation', label: '代码生成' },
                        { key: 'explanation', label: '代码解释' },
                        { key: 'refactor', label: '代码重构' },
                        { key: 'debug', label: '调试' },
                      ],
                    };
                    const currentFeatures = featuresByType[modelForm.model_type || 'llm'] || [];
                    const selectedFeatures = modelForm.features || [];

                    return currentFeatures.map(feature => (
                      <button
                        key={feature.key}
                        type="button"
                        onClick={() => {
                          const newFeatures = selectedFeatures.includes(feature.key)
                            ? selectedFeatures.filter(f => f !== feature.key)
                            : [...selectedFeatures, feature.key];
                          setModelForm(prev => ({ ...prev, features: newFeatures }));
                        }}
                        className={`px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all ${
                          selectedFeatures.includes(feature.key)
                            ? 'bg-blue-600 text-white shadow-[0_0_10px_rgba(59,130,246,0.3)]'
                            : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
                        }`}
                      >
                        {feature.label}
                      </button>
                    ));
                  })()}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">上下文窗口</label>
                  <input
                    type="text"
                    inputMode="numeric"
                    value={modelForm.context_window !== undefined ? modelForm.context_window : ''}
                    onChange={(e) => {
                      const val = e.target.value;
                      if (val === '' || /^\d+$/.test(val)) {
                        setModelForm(prev => ({ ...prev, context_window: val === '' ? undefined : parseInt(val) }));
                      }
                    }}
                    placeholder="128000"
                    className="w-full mt-2 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">最大输出Token</label>
                  <input
                    type="text"
                    inputMode="numeric"
                    value={modelForm.default_max_tokens !== undefined ? modelForm.default_max_tokens : ''}
                    onChange={(e) => {
                      const val = e.target.value;
                      if (val === '' || /^\d+$/.test(val)) {
                        setModelForm(prev => ({ ...prev, default_max_tokens: val === '' ? undefined : parseInt(val) }));
                      }
                    }}
                    placeholder="4096"
                    className="w-full mt-2 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Temperature 滑块 */}
              <div>
                <div className="flex justify-between items-center">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Temperature (温度)</label>
                  <span className="text-xs font-mono text-blue-400">{(modelForm.default_temperature ?? 0.7).toFixed(2)}</span>
                </div>
                <div className="mt-3 px-1">
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.01"
                    value={modelForm.default_temperature ?? 0.7}
                    onChange={(e) => setModelForm(prev => ({ ...prev, default_temperature: parseFloat(e.target.value) }))}
                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer
                      [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                      [&::-webkit-slider-thumb]:bg-blue-500 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-pointer
                      [&::-webkit-slider-thumb]:shadow-[0_0_10px_rgba(59,130,246,0.5)]
                      [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:bg-blue-500
                      [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:cursor-pointer [&::-moz-range-thumb]:border-0"
                  />
                  <div className="flex justify-between text-[9px] text-slate-600 mt-1">
                    <span>精确 0</span>
                    <span>平衡 1</span>
                    <span>创意 2</span>
                  </div>
                </div>
              </div>

              {/* Top P 滑块 */}
              <div>
                <div className="flex justify-between items-center">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Top P (核采样)</label>
                  <span className="text-xs font-mono text-emerald-400">{(modelForm.default_top_p ?? 1.0).toFixed(2)}</span>
                </div>
                <div className="mt-3 px-1">
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={modelForm.default_top_p ?? 1.0}
                    onChange={(e) => setModelForm(prev => ({ ...prev, default_top_p: parseFloat(e.target.value) }))}
                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer
                      [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                      [&::-webkit-slider-thumb]:bg-emerald-500 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-pointer
                      [&::-webkit-slider-thumb]:shadow-[0_0_10px_rgba(16,185,129,0.5)]
                      [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:bg-emerald-500
                      [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:cursor-pointer [&::-moz-range-thumb]:border-0"
                  />
                  <div className="flex justify-between text-[9px] text-slate-600 mt-1">
                    <span>聚焦 0</span>
                    <span>0.5</span>
                    <span>全部 1</span>
                  </div>
                </div>
              </div>

              {/* 启用状态 */}
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 block">启用状态</label>
                <button
                  type="button"
                  onClick={() => setModelForm(prev => ({ ...prev, is_enabled: !prev.is_enabled }))}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    modelForm.is_enabled ? 'bg-blue-600' : 'bg-slate-700'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      modelForm.is_enabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
                <span className="ml-3 text-xs text-slate-400">
                  {modelForm.is_enabled ? '已启用' : '已禁用'}
                </span>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => { setShowModelModal(false); setEditingModel(null); setModelForm({ model_name: '', label: '', description: '', model_type: 'llm', features: [], context_window: undefined, default_max_tokens: undefined, default_temperature: 0.7, default_top_p: 1.0, is_enabled: true }); }}
                className="flex-1 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white text-[10px] font-bold rounded-lg uppercase tracking-widest transition-colors"
              >
                取消
              </button>
              <button
                onClick={editingModel ? handleUpdateModel : handleCreateModel}
                className="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-[10px] font-bold rounded-lg uppercase tracking-widest transition-colors"
              >
                {editingModel ? '更新' : '创建'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 侧边栏 */}
      <aside className={`${isSidebarOpen ? 'w-64' : 'w-20'} flex-shrink-0 bg-slate-900/50 border-r border-slate-800 transition-all duration-300 flex flex-col z-50`}>
        <div className="h-20 flex items-center px-6 border-b border-slate-800 shrink-0">
          <BrandLogo size="md" variant="dark" showText={isSidebarOpen} />
        </div>

        <nav className="flex-1 py-8 px-4 space-y-4">
          <AdminNavItem icon={Icons.Bot} label="仪表板" active={activeView === 'dashboard'} onClick={() => setActiveView('dashboard')} minimized={!isSidebarOpen} />
          <AdminNavItem icon={Icons.Settings} label="模型编排" active={activeView === 'models'} onClick={() => setActiveView('models')} minimized={!isSidebarOpen} />
          <AdminNavItem icon={Icons.Activity} label="性能分析" active={activeView === 'stats'} onClick={() => setActiveView('stats')} minimized={!isSidebarOpen} />
          <AdminNavItem icon={Icons.ShieldPlus} label="向量知识" active={activeView === 'knowledge'} onClick={() => setActiveView('knowledge')} minimized={!isSidebarOpen} />
        </nav>

        <div className="p-4 border-t border-slate-800">
          <button onClick={() => setShowLogoutModal(true)} className="w-full flex items-center justify-center gap-2 py-3 text-[10px] font-bold text-red-400 hover:bg-red-500/10 rounded-xl transition-all uppercase tracking-[0.2em]">
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
                {activeView === 'dashboard' ? '控制面板' : activeView === 'models' ? '模型编排' : activeView === 'stats' ? '性能分析' : '向量知识'}
              </h2>
           </div>

           <div className="flex items-center gap-8">
              <div className="hidden md:flex items-center gap-3 bg-slate-900 border border-slate-800 px-4 py-2 rounded-full">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_#10b981]"></div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">核心引擎: 稳定</span>
              </div>

              <div className="flex items-center gap-4">
                 <div className="text-right">
                    <div className="text-xs font-bold text-white uppercase tracking-wider">{user.name}</div>
                    <div className="text-[10px] text-blue-500 font-bold uppercase tracking-tighter">超级用户权限</div>
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
      
      {/* 删除确认Toast */}
      {showDeleteConfirm && deleteTarget && (
        <DeleteConfirmToast
          message={deleteTarget.type === 'provider'
            ? '确定要删除此供应商吗？这将同时删除该供应商下的所有模型配置。'
            : '确定要删除此模型配置吗？'}
          onConfirm={() => {
            if (deleteTarget.type === 'provider') {
              confirmDeleteProvider(deleteTarget.id);
            } else {
              confirmDeleteModel(deleteTarget.id);
            }
          }}
          onCancel={() => {
            setShowDeleteConfirm(false);
            setDeleteTarget(null);
          }}
          onClose={() => {
            setShowDeleteConfirm(false);
            setDeleteTarget(null);
          }}
          variant="admin"
        />
      )}

      {/* Toast 提示 */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
          variant="admin"
        />
      )}
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