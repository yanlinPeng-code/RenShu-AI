
import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icons } from '../../components/common/Icons';
import { ProviderConfig, CustomModel } from '../../types';
import { DeleteConfirmToast } from '../../components/common/DeleteConfirmToast';
import { providerApi, modelApi } from '../../api/modules/model';
import { ModelProviderCreate, ModelProviderUpdate, ModelConfigDelete, ModelProviderDelete, ModelConfigCreate, ModelConfigUpdate } from '../../api/types';

// Supported Model Types for the Add Provider Modal
const SUPPORTED_MODEL_TYPES = [
  { id: 'llm', label: 'LLM' },
  { id: 'multimodal', label: '多模态' },
  { id: 'embedding', label: '嵌入' },
  { id: 'rerank', label: '重排序' },
  { id: 'image', label: '图像' },
  { id: 'audio', label: '音频' },
  { id: 'video', label: '视频' },
  { id: 'code', label: '代码' },
];

const MODEL_CONFIG_TYPES = [
    'LLM (大语言模型)',
    'Multimodal (多模态)',
    'Embedding (文本嵌入)',
    'Image (图像生成)',
    'Code (代码大模型)'
];

const MODEL_FEATURES = [
    { id: 'structured', label: '结构化输出' },
    { id: 'tools', label: '工具调用' },
    { id: 'thinking', label: '思维链' },
    { id: 'reasoning', label: '推理' },
    { id: 'streaming', label: '流式输出' },
    { id: 'vision', label: '视觉识别' }
];

const PublicModelManagementPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedProviderId, setSelectedProviderId] = useState<string>('');
  const [searchProvider, setSearchProvider] = useState('');
  const [searchModel, setSearchModel] = useState('');
  const [apiProviders, setApiProviders] = useState<any[]>([]);
  
  // --- Persistence States ---

  // Provider Configurations (API Key, Base URL)
  const [providerConfigs, setProviderConfigs] = useState<Record<string, ProviderConfig>>(() => {
    const saved = localStorage.getItem('user_provider_configs');
    return saved ? JSON.parse(saved) : {};
  });

  // Enabled Models List (IDs of models user wants to see)
  const [enabledModels, setEnabledModels] = useState<string[]>(() => {
    const saved = localStorage.getItem('user_enabled_models');
    // Default: enable all built-in models initially if not set
    return saved ? JSON.parse(saved) : [];
  });

  // Custom Models
  const [customModels, setCustomModels] = useState<CustomModel[]>(() => {
    const saved = localStorage.getItem('user_custom_models');
    return saved ? JSON.parse(saved) : [];
  });

  // Custom Providers
  const [customProviders, setCustomProviders] = useState<any[]>(() => {
    const saved = localStorage.getItem('user_custom_providers');
    return saved ? JSON.parse(saved) : [];
  });

  // UI States
  const [showKey, setShowKey] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [checkStatus, setCheckStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [checkModelId, setCheckModelId] = useState<string>('');

  // Delete Confirmation State
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ type: 'provider' | 'model', id: string } | null>(null);

  // Add Provider Modal State
  const [showAddProviderModal, setShowAddProviderModal] = useState(false);
  const [newProviderForm, setNewProviderForm] = useState({
    nameId: '',
    description: '',
    defaultBaseUrl: '',
    supportedTypes: [] as string[],
    isEnabled: true
  });

  // Add Model Modal State (Detailed)
  const [showAddModelModal, setShowAddModelModal] = useState(false);
  const [editingModelId, setEditingModelId] = useState<string | null>(null); // Track if we're editing an existing model
  const [modelForm, setModelForm] = useState({
    id: '', // Model Name (API)
    type: 'LLM (大语言模型)',
    description: '',
    features: [] as string[],
    contextWindow: 4096,
    maxTokens: 4096,
    temperature: 0.7,
    topP: 1.0,
    enabled: true
  });

  // --- Effects ---

  useEffect(() => {
    localStorage.setItem('user_provider_configs', JSON.stringify(providerConfigs));
  }, [providerConfigs]);

  useEffect(() => {
    localStorage.setItem('user_enabled_models', JSON.stringify(enabledModels));
  }, [enabledModels]);

  useEffect(() => {
    localStorage.setItem('user_custom_models', JSON.stringify(customModels));
  }, [customModels]);

  useEffect(() => {
    localStorage.setItem('user_custom_providers', JSON.stringify(customProviders));
  }, [customProviders]);

  useEffect(() => {
    const fetchBuiltinProviders = async () => {
      try {
        const res = await providerApi.get_builtin_providers_with_models();
        if (res.success === true && Array.isArray(res.data)) {
          console.log('Builtin providers with models:', res.data);
          setApiProviders(res.data);
          if (!localStorage.getItem('user_enabled_models')) {
            const enabledFromApi = res.data.flatMap((p: any) =>
              (p.models || []).filter((m: any) => m.is_enabled !== false).map((m: any) => m.model_name)
            );
            if (enabledFromApi.length > 0) {
              setEnabledModels(enabledFromApi);
            }
          }
          if (res.data.length > 0 && !selectedProviderId) {
            // 优先选择第一个内置provider作为默认选项
            setSelectedProviderId(res.data[0].name);
          } else if (res.data.length > 0 && !res.data.some((p: any) => p.name === selectedProviderId)) {
            // 如果当前选中的provider不存在于API返回的数据中，则选择第一个
            setSelectedProviderId(res.data[0].name);
          }
        }
      } catch (error) {
        console.error('Failed to fetch builtin providers:', error);
        setApiProviders([]);
        // 如果获取内置provider失败，尝试使用本地数据
        // if (!selectedProviderId && PROVIDERS.length > 0) {
        //   setSelectedProviderId(PROVIDERS[0].id);
        // }
      }
    };
    fetchBuiltinProviders();
  }, [selectedProviderId]);

  // Reset check status when provider changes
  useEffect(() => {
    setCheckStatus('idle');
    setShowKey(false);
  }, [selectedProviderId]);

  // --- Helpers ---

  // Merge built-in and custom providers
  const allProviders = useMemo(() => {
    if (apiProviders.length > 0) {
      return apiProviders.map((p: any) => ({
        id: p.name,
        name: p.label || p.name,
        icon: p.icon || '🤖',
        description: p.description,
        defaultBaseUrl: p.default_base_url || p.base_url || '',
        supportedTypes: p.supported_model_types || [],
        helpUrl: p.help_url,
        providerId: p.id,
        isCustom: p.is_builtin === false,
        isEnabled: p.is_enabled !== false
      }));
    }
    // 如果apiProviders为空且没有导入PROVIDERS，则返回空数组
    return [];
  }, [apiProviders]);

  const currentProvider = allProviders.find(p => p.id === selectedProviderId);
  const currentProviderMeta = apiProviders.find((p: any) => p.name === selectedProviderId);
  const isCustomProvider = (currentProvider as any)?.isCustom || customProviders.some(p => p.id === selectedProviderId);
  const currentConfig = providerConfigs[selectedProviderId] || { apiKey: '', baseUrl: '', enabled: false };

  const rawModelsForProvider = useMemo(() => {
    if (currentProviderMeta?.models?.length) {
      return currentProviderMeta.models.map((m: any) => ({
        id: m.model_name,
        name: m.label || m.model_name,
        description: m.description || '',
        provider: currentProviderMeta.name,
        supportsThinking: m.features?.includes('thinking') || m.features?.includes('agent_thought'),
        supportsVision: m.features?.includes('image_input') || m.features?.includes('vision'),
        contextWindow: m.context_window ? `${Math.round(m.context_window / 1000)}K` : undefined,
        isCustom: customModels.some(cm => cm.id === m.model_name),
        modelConfigId: m.id,
        isEnabled: m.is_enabled !== false,
        rawFeatures: m.features || []
      }));
    }
    return [
      ...customModels.filter(m => m.provider === selectedProviderId)
    ];
  }, [currentProviderMeta, selectedProviderId, customModels]);

  const displayModels = useMemo(() => {
    return rawModelsForProvider.filter(m => m.name.toLowerCase().includes(searchModel.toLowerCase()) || m.id.toLowerCase().includes(searchModel.toLowerCase()));
  }, [rawModelsForProvider, searchModel]);

  const modelMetaMap = useMemo(() => {
    return new Map<string, any>(rawModelsForProvider.map((m: any) => [m.id, m]));
  }, [rawModelsForProvider]);

  const fetchProvidersWithModels = async (nextSelectedProviderId?: string) => {
    try {
      const res = await providerApi.get_providers_with_models();
      if (res.success === true && Array.isArray(res.data)) {
        setApiProviders(res.data);
        const target = nextSelectedProviderId || selectedProviderId;
        if (res.data.length > 0 && !res.data.some((p: any) => p.name === target)) {
          setSelectedProviderId(res.data[0].name);
        } else if (nextSelectedProviderId) {
          setSelectedProviderId(nextSelectedProviderId);
        }
      }
    } catch (error) {
      setApiProviders([]);
    }
  };

  const mapModelType = (value: string) => {
    const lower = value.toLowerCase();
    if (lower.includes('multimodal')) return 'multimodal';
    if (lower.includes('embedding')) return 'embedding';
    if (lower.includes('image')) return 'image';
    if (lower.includes('code')) return 'code';
    return 'llm';
  };

  const mapModelFeatures = (features: string[]) => {
    return features.map(f => {
      if (f === 'structured') return 'structured_output';
      if (f === 'tools') return 'tool_call';
      if (f === 'reasoning') return 'agent_thought';
      if (f === 'vision') return 'image_input';
      return f;
    });
  };

  // Update checkModelId when provider changes or models change
  useEffect(() => {
    if (rawModelsForProvider.length > 0) {
        setCheckModelId(prev => {
            const exists = rawModelsForProvider.find(m => m.id === prev);
            return exists ? prev : rawModelsForProvider[0].id;
        });
    } else {
        setCheckModelId('');
    }
  }, [rawModelsForProvider]);

  const toggleProviderEnabled = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    const newEnabled = !currentConfig.enabled;
    setProviderConfigs(prev => ({
      ...prev,
      [selectedProviderId]: { ...currentConfig, enabled: newEnabled }
    }));
    if (currentProviderMeta?.id) {
      const updateData: ModelProviderUpdate = {
        provider_id: currentProviderMeta.id,
        is_enabled: newEnabled
      };
      providerApi.update(updateData);
    }
  };

  const updateConfig = async (field: keyof ProviderConfig, value: string) => {
    const nextConfig = { ...currentConfig, [field]: value, enabled: true };
    setProviderConfigs(prev => ({
      ...prev,
      [selectedProviderId]: nextConfig
    }));
    if (currentProviderMeta?.id) {
      const updateData: ModelProviderUpdate = {
        provider_id: currentProviderMeta.id,
        api_key: nextConfig.apiKey,
        base_url: nextConfig.baseUrl,
        is_enabled: true
      };
      try {
        const res = await providerApi.update(updateData);
        if (res.success !== true) {
          throw new Error(res.message || '更新供应商配置失败');
        }
      } catch (error: any) {
        console.error('Error updating provider config:', error);
        alert('更新供应商配置失败：' + (error.message || '网络错误'));
        // 恢复之前的配置
        setProviderConfigs(prev => ({
          ...prev,
          [selectedProviderId]: currentConfig
        }));
      }
    }
  };

  const toggleModelEnabled = async (modelId: string) => {
    const newEnabled = !enabledModels.includes(modelId);
    setEnabledModels(prev => {
      if (prev.includes(modelId)) return prev.filter(id => id !== modelId);
      return [...prev, modelId];
    });
    const modelMeta = modelMetaMap.get(modelId);
    if (modelMeta?.modelConfigId) {
      const updateData: ModelConfigUpdate = {
        model_config_id: modelMeta.modelConfigId,
        is_enabled: newEnabled
      };
      try {
        const res = await modelApi.update(updateData);
        if (res.success !== true) {
          throw new Error(res.message || '更新模型配置失败');
        }
      } catch (error: any) {
        console.error('Error updating model config:', error);
        alert('更新模型配置失败：' + (error.message || '网络错误'));
        // 恢复之前的启用状态
        setEnabledModels(prev => {
          if (newEnabled) return prev.filter(id => id !== modelId);
          return [...prev, modelId];
        });
      }
    }
  };

  const handleCheckConnectivity = async () => {
    if (!currentConfig.apiKey) return;
    setIsChecking(true);
    setCheckStatus('idle');
    // Simulate check
    setTimeout(() => {
      setIsChecking(false);
      setCheckStatus('success'); // In a real app, actually fetch models
    }, 1500);
  };

  const handleCreateCustomModel = async () => {
    if (!modelForm.id) {
      alert('请填写模型名称');
      return;
    }
    
    if (!currentProviderMeta?.id) {
      alert('无法获取当前供应商信息，请刷新页面重试');
      return;
    }
    
    // Validate model name format
    const modelNameRegex = /^[a-zA-Z0-9][a-zA-Z0-9._-]*$/;
    if (!modelNameRegex.test(modelForm.id)) {
      alert('模型名称只能包含字母、数字、点号、下划线和横线，且必须以字母或数字开头');
      return;
    }
    
    const newModel: CustomModel = {
      id: modelForm.id,
      name: modelForm.id,
      description: modelForm.description || 'Custom Model Configuration',
      provider: selectedProviderId as any,
      supportsThinking: modelForm.features.includes('thinking') || modelForm.features.includes('reasoning'),
      supportsVision: modelForm.features.includes('vision') || modelForm.type.includes('Multimodal'),
      contextWindow: modelForm.contextWindow.toString() + (modelForm.contextWindow > 1000 ? 'K' : ''),
      isCustom: true
    };
    
    try {
      const createData: ModelConfigCreate = {
        provider_id: currentProviderMeta.id,
        model_name: modelForm.id,
        description: modelForm.description,
        model_type: mapModelType(modelForm.type),
        features: mapModelFeatures(modelForm.features),
        context_window: modelForm.contextWindow,
        default_max_tokens: modelForm.maxTokens,
        default_temperature: modelForm.temperature,
        default_top_p: modelForm.topP,
      };
      const res = await modelApi.create(createData);
      if (res.success === true) {
        setCustomModels(prev => prev.some(m => m.id === newModel.id) ? prev : [...prev, newModel]);
        if (modelForm.enabled) {
          setEnabledModels(prev => prev.includes(newModel.id) ? prev : [...prev, newModel.id]);
        }
        setShowAddModelModal(false);
        setModelForm({
          id: '',
          type: 'LLM (大语言模型)',
          description: '',
          features: [],
          contextWindow: 4096,
          maxTokens: 4096,
          temperature: 0.7,
          topP: 1.0,
          enabled: true
        });
        fetchProvidersWithModels(selectedProviderId);
      } else {
        throw new Error(res.message || '创建模型失败');
      }
    } catch (error: any) {
      console.error('Error creating custom model:', error);
      alert('创建模型时发生错误：' + (error.message || '网络错误'));
      setCustomModels(prev => prev);
    }
  };

  // Delete Request Handlers
  const requestDeleteCustomModel = (id: string) => {
    setDeleteTarget({ type: 'model', id });
    setShowDeleteConfirm(true);
  };

  const requestDeleteCustomProvider = (id: string) => {
    setDeleteTarget({ type: 'provider', id });
    setShowDeleteConfirm(true);
  };

  // Confirm Delete Logic
  const handleConfirmDelete = async () => {
    if (!deleteTarget) return;

    if (deleteTarget.type === 'model') {
      const modelMeta = modelMetaMap.get(deleteTarget.id);
      if (modelMeta?.modelConfigId) {
        const deleteData: ModelConfigDelete = { model_config_id: modelMeta.modelConfigId };
        try {
          const res = await modelApi.delete(deleteData);
          if (res.success !== true) {
            throw new Error(res.message || '删除模型失败');
          }
          fetchProvidersWithModels(selectedProviderId);
        } catch (error: any) {
          console.error('Error deleting model:', error);
          alert('删除模型失败：' + (error.message || '网络错误'));
        }
      }
      setCustomModels(prev => prev.filter(m => m.id !== deleteTarget.id));
      setEnabledModels(prev => prev.filter(mid => mid !== deleteTarget.id));
    } else if (deleteTarget.type === 'provider') {
      const providerMeta = apiProviders.find((p: any) => p.name === deleteTarget.id);
      if (providerMeta?.id) {
        const deleteData: ModelProviderDelete = { provider_id: providerMeta.id };
        try {
          const res = await providerApi.delete(deleteData);
          if (res.success !== true) {
            throw new Error(res.message || '删除供应商失败');
          }
          fetchProvidersWithModels(apiProviders.length > 0 ? apiProviders[0].name : '');
        } catch (error: any) {
          console.error('Error deleting provider:', error);
          alert('删除供应商失败：' + (error.message || '网络错误'));
        }
      }
      setCustomProviders(prev => prev.filter(p => p.id !== deleteTarget.id));
      setProviderConfigs(prev => {
        const next = { ...prev };
        delete next[deleteTarget.id];
        return next;
      });
      const modelsToDelete = customModels.filter(m => m.provider === deleteTarget.id).map(m => m.id);
      setCustomModels(prev => prev.filter(m => m.provider !== deleteTarget.id));
      setEnabledModels(prev => prev.filter(mid => !modelsToDelete.includes(mid)));
      if (selectedProviderId === deleteTarget.id) {
        setSelectedProviderId(apiProviders.length > 0 ? apiProviders[0].name : '');
      }
    }

    setShowDeleteConfirm(false);
    setDeleteTarget(null);
  };

  // Add Provider Logic
  const handleAddProvider = async () => {
    if (!newProviderForm.nameId) {
      alert('请填写供应商名称');
      return;
    }
    
    // Validate provider ID format
    const providerIdRegex = /^[a-zA-Z][a-zA-Z0-9_-]*$/;
    if (!providerIdRegex.test(newProviderForm.nameId)) {
      alert('供应商名称只能包含字母、数字、下划线和横线，且必须以字母开头');
      return;
    }
    
    // Check ID conflict
    if (allProviders.some(p => p.id === newProviderForm.nameId)) {
        alert("供应商ID已存在！");
        return;
    }

    const newProvider = {
        id: newProviderForm.nameId,
        name: newProviderForm.nameId.charAt(0).toUpperCase() + newProviderForm.nameId.slice(1), // Simple capitalization
        icon: '📦', // Default icon for custom providers
        description: newProviderForm.description,
        defaultBaseUrl: newProviderForm.defaultBaseUrl,
        supportedTypes: newProviderForm.supportedTypes,
        isCustom: true
    };
    try {
      const createData: ModelProviderCreate = {
        name: newProviderForm.nameId,
        description: newProviderForm.description,
        base_url: newProviderForm.defaultBaseUrl,
        supported_model_types: newProviderForm.supportedTypes,
        position: allProviders.length + 1
      };
      const res = await providerApi.create(createData);
      if (res.success === true) {
        if (!newProviderForm.isEnabled && res.data?.id) {
          const updateData: ModelProviderUpdate = { provider_id: res.data.id, is_enabled: false };
          await providerApi.update(updateData);
        }
        setCustomProviders(prev => prev.some(p => p.id === newProvider.id) ? prev : [...prev, newProvider]);
        if (newProviderForm.isEnabled) {
          setProviderConfigs(prev => ({
            ...prev,
            [newProvider.id]: {
              apiKey: '',
              baseUrl: newProvider.defaultBaseUrl,
              enabled: true
            }
          }));
        }
        setShowAddProviderModal(false);
        setSelectedProviderId(newProvider.id);
        setNewProviderForm({ nameId: '', description: '', defaultBaseUrl: '', supportedTypes: [], isEnabled: true });
        fetchProvidersWithModels(newProvider.id);
      } else {
        throw new Error(res.message || '创建供应商失败');
      }
    } catch (error: any) {
      console.error('Error adding provider:', error);
      alert('添加供应商时发生错误：' + (error.message || '网络错误')); 
      setCustomProviders(prev => prev);
    }
  };

  const toggleSupportedType = (typeId: string) => {
      setNewProviderForm(prev => {
          const types = prev.supportedTypes.includes(typeId) 
            ? prev.supportedTypes.filter(t => t !== typeId)
            : [...prev.supportedTypes, typeId];
          return { ...prev, supportedTypes: types };
      });
  };

  const toggleModelFeature = (featureId: string) => {
      setModelForm(prev => {
          const features = prev.features.includes(featureId)
            ? prev.features.filter(f => f !== featureId)
            : [...prev.features, featureId];
          return { ...prev, features };
      });
  };

  // Edit existing model
  const handleEditModel = (model: any) => {
    setEditingModelId(model.id);
    setModelForm({
      id: model.id,
      type: MODEL_CONFIG_TYPES.find(t => mapModelType(t) === model.model_type) || 'LLM (大语言模型)',
      description: model.description || '',
      features: model.rawFeatures || model.features || [],
      contextWindow: model.contextWindow ? parseInt(model.contextWindow.replace('K', '000')) : 4096,
      maxTokens: model.default_max_tokens || 4096,
      temperature: model.default_temperature || 0.7,
      topP: model.default_top_p || 1.0,
      enabled: model.isEnabled !== false
    });
    setShowAddModelModal(true);
  };

  // Handle update existing model
  const handleUpdateCustomModel = async () => {
    if (!modelForm.id || !currentProviderMeta?.id || !editingModelId) return;
    
    // Validate model name format
    const modelNameRegex = /^[a-zA-Z0-9][a-zA-Z0-9._-]*$/;
    if (!modelNameRegex.test(modelForm.id)) {
      alert('模型名称只能包含字母、数字、点号、下划线和横线，且必须以字母或数字开头');
      return;
    }
    
    try {
      const updateData: ModelConfigUpdate = {
        model_config_id: editingModelId, // This should be the actual model config ID
        label: modelForm.id, // Update the display name
        description: modelForm.description,
        model_type: mapModelType(modelForm.type),
        features: mapModelFeatures(modelForm.features),
        context_window: modelForm.contextWindow,
        default_max_tokens: modelForm.maxTokens,
        default_temperature: modelForm.temperature,
        default_top_p: modelForm.topP,
        is_enabled: modelForm.enabled
      };
      
      // Find the actual model config ID from the meta map
      const modelMeta = rawModelsForProvider.find((m: any) => m.id === editingModelId);
      if (modelMeta?.modelConfigId) {
        updateData.model_config_id = modelMeta.modelConfigId;
      }
      
      const res = await modelApi.update(updateData);
      if (res.success === true) {
        // Update the custom models state
        setCustomModels(prev => 
          prev.map(m => 
            m.id === editingModelId 
              ? { 
                  ...m, 
                  id: modelForm.id,
                  name: modelForm.id,
                  description: modelForm.description,
                  supportsThinking: modelForm.features.includes('thinking') || modelForm.features.includes('reasoning'),
                  supportsVision: modelForm.features.includes('vision') || modelForm.type.includes('Multimodal'),
                  contextWindow: modelForm.contextWindow.toString() + (modelForm.contextWindow > 1000 ? 'K' : ''),
                } 
              : m
          )
        );
        
        // Update enabled models if needed
        if (modelForm.enabled && !enabledModels.includes(editingModelId)) {
          setEnabledModels(prev => [...prev, editingModelId]);
        } else if (!modelForm.enabled && enabledModels.includes(editingModelId)) {
          setEnabledModels(prev => prev.filter(id => id !== editingModelId));
        }
        
        setShowAddModelModal(false);
        setEditingModelId(null);
        setModelForm({
          id: '',
          type: 'LLM (大语言模型)',
          description: '',
          features: [],
          contextWindow: 4096,
          maxTokens: 4096,
          temperature: 0.7,
          topP: 1.0,
          enabled: true
        });
        fetchProvidersWithModels(selectedProviderId);
      } else {
        throw new Error(res.message || '更新模型失败');
      }
    } catch (error: any) {
      console.error('Error updating custom model:', error);
      alert('更新模型时发生错误：' + (error.message || '网络错误'));
    }
  };

  return (
    <div className="flex h-screen bg-rice-paper text-tcm-charcoal transition-colors duration-500 overflow-hidden font-sans">
      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && deleteTarget && (
        <DeleteConfirmToast
          message={deleteTarget.type === 'provider' 
            ? '确定要删除该提供商及其全部模型吗？' 
            : '确定要删除该模型吗？'}
          onConfirm={handleConfirmDelete}
          onCancel={() => { setShowDeleteConfirm(false); setDeleteTarget(null); }}
          onClose={() => { setShowDeleteConfirm(false); setDeleteTarget(null); }}
          variant="tcm"
        />
      )}

      {/* 1. Sidebar - Provider List */}
      <aside className="w-72 bg-[#f9fafb] dark:bg-[#181818] border-r border-gray-200 dark:border-gray-800 flex flex-col flex-shrink-0 z-20">
        <div className="p-4 pt-6">
          <div className="flex items-center gap-2 mb-6 cursor-pointer" onClick={() => navigate('/public')}>
            <button className="p-1.5 hover:bg-gray-200 dark:hover:bg-white/10 rounded-lg transition-colors text-gray-500">
              <Icons.ChevronRight className="rotate-180" size={20} />
            </button>
            <h1 className="text-lg font-bold font-serif-sc text-tcm-darkGreen dark:text-tcm-cream">设置</h1>
          </div>
          
          <div className="flex gap-2 mb-4">
            <div className="relative flex-1">
                <Icons.Activity className="absolute left-3 top-2.5 text-gray-400" size={16} />
                <input 
                type="text" 
                placeholder="搜索服务商..." 
                value={searchProvider}
                onChange={(e) => setSearchProvider(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-white dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-tcm-lightGreen/50 outline-none transition-all"
                />
            </div>
            <button 
                onClick={() => setShowAddProviderModal(true)}
                className="p-2 bg-white dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-500 hover:text-tcm-darkGreen hover:border-tcm-darkGreen transition-all group relative"
                title="添加自定义服务"
            >
                <Icons.Plus size={20} />
                <div className="absolute left-1/2 -translate-x-1/2 -top-8 px-2 py-1 bg-black text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">添加自定义服务</div>
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-3 space-y-1 custom-scrollbar pb-4">
          <div className="px-3 py-2 text-xs font-bold text-gray-400 uppercase tracking-wider">全部</div>
          {allProviders.filter(p => p.name.toLowerCase().includes(searchProvider.toLowerCase())).map(provider => {
            const config = providerConfigs[provider.id];
            const isEnabled = config?.enabled && !!config?.apiKey;
            const isActive = selectedProviderId === provider.id;

            return (
              <button
                key={provider.id}
                onClick={() => setSelectedProviderId(provider.id)}
                className={`w-full flex items-center justify-between p-3 rounded-xl transition-all group ${
                  isActive 
                    ? 'bg-white dark:bg-[#252525] shadow-sm border border-gray-100 dark:border-gray-700' 
                    : 'hover:bg-gray-100 dark:hover:bg-white/5 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl bg-gray-100 dark:bg-white/10 w-8 h-8 flex items-center justify-center rounded-lg">{provider.icon}</span>
                  <span className={`text-sm font-medium ${isActive ? 'text-tcm-darkGreen dark:text-tcm-lightGreen font-bold' : 'text-gray-700 dark:text-gray-300'}`}>
                    {provider.name}
                  </span>
                </div>
                {isEnabled && <div className="w-1.5 h-1.5 rounded-full bg-tcm-lightGreen shadow-[0_0_8px_rgba(77,140,124,0.6)]"></div>}
              </button>
            );
          })}
        </div>
      </aside>

      {/* 2. Main Content - Settings & Model List */}
      <main className="flex-1 overflow-y-auto bg-rice-paper p-4 md:p-8 scroll-smooth">
        <div className="max-w-4xl mx-auto space-y-6">
          
          {/* Header */}
          <div className="flex items-center gap-3 mb-6">
             <div className="text-3xl">{currentProvider?.icon}</div>
             <h2 className="text-2xl font-bold font-serif-sc text-tcm-darkGreen dark:text-tcm-cream">{currentProvider?.name}</h2>
             {/* Show badge if custom */}
             {isCustomProvider && (
                 <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-tcm-gold/10 text-tcm-gold border border-tcm-gold/20">CUSTOM</span>
             )}
             
             {/* Provider Master Controls (Right Aligned) */}
             <div className="ml-auto flex items-center gap-3">
                {/* Provider Master Toggle */}
                <button 
                    onClick={toggleProviderEnabled}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    currentConfig.enabled ? 'bg-tcm-lightGreen' : 'bg-gray-200 dark:bg-gray-700'
                    }`}
                >
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${currentConfig.enabled ? 'translate-x-6' : 'translate-x-1'}`} />
                </button>

                {/* Delete Provider Button (Only for Custom Providers) */}
                {isCustomProvider && (
                    <button 
                        onClick={() => requestDeleteCustomProvider(selectedProviderId)}
                        className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all"
                        title="删除该提供商"
                    >
                        <Icons.Trash2 size={18} />
                    </button>
                )}
             </div>
          </div>

          {/* Card 1: Provider Configuration */}
          <div className="bg-white dark:bg-[#1e1e1e] rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
             <div className="grid gap-6">
                
                {/* API Key */}
                <div className="space-y-2">
                   <div className="flex justify-between">
                      <label className="text-sm font-bold text-gray-700 dark:text-gray-200">API Key</label>
                      <a href="#" className="text-xs text-tcm-lightGreen hover:underline">获取 API Key</a>
                   </div>
                   <div className="relative group">
                      <input 
                        type={showKey ? "text" : "password"}
                        value={currentConfig.apiKey || ''}
                        onChange={(e) => updateConfig('apiKey', e.target.value)}
                        placeholder={`输入 ${currentProvider?.name} API Key`}
                        className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-tcm-lightGreen/50 focus:border-tcm-lightGreen transition-all text-sm font-mono"
                      />
                      <button 
                        onClick={() => setShowKey(!showKey)}
                        className="absolute right-3 top-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                      >
                        {showKey ? <Icons.Image size={16} /> : <Icons.Zap size={16} />} {/* Assuming icons for eye */}
                      </button>
                   </div>
                </div>

                {/* Base URL */}
                <div className="space-y-2">
                   <label className="text-sm font-bold text-gray-700 dark:text-gray-200">API 代理地址</label>
                   <input 
                      type="text"
                      value={currentConfig.baseUrl || ''}
                      onChange={(e) => updateConfig('baseUrl', e.target.value)}
                      placeholder={ (currentProvider as any)?.defaultBaseUrl || "https://api.openai.com/v1" }
                      className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-tcm-lightGreen/50 focus:border-tcm-lightGreen transition-all text-sm font-mono"
                   />
                   <p className="text-xs text-gray-400">默认使用官方地址，如需使用代理请输入完整地址。</p>
                </div>

                {/* Check Connectivity */}
                <div className="pt-2 flex items-center justify-between bg-gray-50 dark:bg-black/10 p-3 rounded-xl border border-dashed border-gray-200 dark:border-gray-700">
                   <div className="flex flex-col">
                      <span className="text-sm font-bold text-gray-700 dark:text-gray-200">连通性检查</span>
                      <span className="text-xs text-gray-400">测试 API Key 与代理地址是否正确填写</span>
                   </div>
                   
                   <div className="flex items-center gap-2">
                       <div className="relative">
                            <select 
                                value={checkModelId}
                                onChange={(e) => setCheckModelId(e.target.value)}
                                className="bg-white dark:bg-[#1e1e1e] border border-gray-200 dark:border-gray-700 rounded-lg text-xs py-2 pl-3 pr-8 appearance-none outline-none focus:ring-1 focus:ring-tcm-lightGreen cursor-pointer min-w-[160px] font-mono text-gray-700 dark:text-gray-300"
                            >
                                {rawModelsForProvider.length === 0 ? <option>无可用模型</option> : rawModelsForProvider.map(m => (
                                    <option key={m.id} value={m.id}>{m.id}</option>
                                ))}
                            </select>
                            <Icons.ChevronDown className="absolute right-2.5 top-2.5 text-gray-400 pointer-events-none" size={14} />
                       </div>
                       
                       <button 
                         onClick={handleCheckConnectivity}
                         disabled={isChecking || !currentConfig.apiKey}
                         className="px-4 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-xs font-bold hover:bg-gray-50 dark:hover:bg-gray-600 transition-all flex items-center gap-2"
                       >
                         {isChecking ? '检查中...' : checkStatus === 'success' ? <span className="text-green-500 flex items-center gap-1"><Icons.Check size={14}/> 通行</span> : '检查'}
                       </button>
                   </div>
                </div>

             </div>
          </div>

          {/* Card 2: Model List */}
          <div className="bg-white dark:bg-[#1e1e1e] rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col min-h-[400px]">
             
             {/* Toolbar */}
             <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex flex-wrap gap-4 items-center justify-between bg-gray-50/50 dark:bg-black/10 rounded-t-2xl">
                <div className="flex items-center gap-2">
                   <span className="font-bold text-gray-700 dark:text-gray-200 text-sm">模型列表</span>
                   <span className="bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400 px-2 py-0.5 rounded-full text-xs font-mono">{displayModels.length}</span>
                </div>
                
                <div className="flex items-center gap-2 flex-1 justify-end">
                   <div className="relative max-w-[200px] w-full">
                      <Icons.Activity className="absolute left-2.5 top-2 text-gray-400" size={14} />
                      <input 
                        type="text" 
                        placeholder="搜索模型..." 
                        value={searchModel}
                        onChange={e => setSearchModel(e.target.value)}
                        className="w-full pl-8 pr-3 py-1.5 bg-white dark:bg-black/20 border border-gray-200 dark:border-gray-600 rounded-lg text-xs outline-none focus:ring-1 focus:ring-tcm-lightGreen"
                      />
                   </div>
                   <button 
                     onClick={() => {
                       setEditingModelId(null);
                       setModelForm({
                         id: '',
                         type: 'LLM (大语言模型)',
                         description: '',
                         features: [],
                         contextWindow: 4096,
                         maxTokens: 4096,
                         temperature: 0.7,
                         topP: 1.0,
                         enabled: true
                       });
                       setShowAddModelModal(true);
                     }}
                     className="p-1.5 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-tcm-lightGreen hover:text-tcm-lightGreen transition-colors text-gray-500"
                     title="Add Custom Model"
                   >
                     <Icons.Plus size={16} />
                   </button>
                </div>
             </div>

             {/* List */}
             <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {displayModels.map(model => (
                   <div key={model.id} className="p-4 flex items-center gap-4 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors group">
                      <div className="w-10 h-10 rounded-xl bg-gray-100 dark:bg-white/10 flex items-center justify-center text-xl flex-shrink-0 text-gray-600 dark:text-gray-300">
                         {selectedProviderId === 'google' ? <Icons.Zap size={20}/> : 
                          selectedProviderId === 'openai' ? <Icons.BrainCircuit size={20}/> : 
                          selectedProviderId === 'anthropic' ? <Icons.Leaf size={20}/> : <Icons.Bot size={20}/>}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                         <div className="flex items-center gap-2 mb-0.5">
                            <span className="font-bold text-sm text-gray-800 dark:text-gray-200 truncate">{model.name}</span>
                            <span className="bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 px-1.5 py-0.5 rounded text-[10px] font-mono">{model.id}</span>
                            {(model as CustomModel).isCustom && <span className="text-[9px] text-tcm-gold border border-tcm-gold/30 px-1 rounded">Custom</span>}
                         </div>
                         <div className="flex items-center gap-3 text-xs text-gray-400">
                            <span>{model.description}</span>
                         </div>
                      </div>

                      {/* Features Badges */}
                      <div className="hidden md:flex gap-2">
                         {model.supportsVision && <span className="p-1 rounded bg-blue-50 dark:bg-blue-900/20 text-blue-500" title="Vision"><Icons.Image size={14}/></span>}
                         {model.supportsThinking && <span className="p-1 rounded bg-indigo-50 dark:bg-indigo-900/20 text-indigo-500" title="Reasoning"><Icons.BrainCircuit size={14}/></span>}
                         {model.contextWindow && <span className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-500 text-[10px] font-mono">{model.contextWindow}</span>}
                      </div>

                      {/* Toggle & Delete */}
                      <div className="flex items-center gap-3">
                         <button 
                            onClick={() => toggleModelEnabled(model.id)}
                            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                              enabledModels.includes(model.id) ? 'bg-tcm-lightGreen' : 'bg-gray-200 dark:bg-gray-700'
                            }`}
                         >
                            <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${enabledModels.includes(model.id) ? 'translate-x-4.5' : 'translate-x-0.5'}`} />
                         </button>

                         {/* Delete Model Button (Right side of toggle, only for custom models) */}
                         {(model as CustomModel).isCustom && (
                            <>
                              <button onClick={() => handleEditModel(model)} className="p-1.5 text-gray-300 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-all" title="编辑模型">
                                 <Icons.Settings size={16} />
                              </button>
                              <button onClick={() => requestDeleteCustomModel(model.id)} className="p-1.5 text-gray-300 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-all" title="删除模型">
                                 <Icons.Trash2 size={16} />
                              </button>
                            </>
                         )}
                      </div>
                   </div>
                ))}
             </div>
          </div>

        </div>
      </main>

      {/* ADD PROVIDER MODAL */}
      {showAddProviderModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-white dark:bg-[#1e1e1e] rounded-2xl border border-gray-200 dark:border-gray-700 shadow-2xl w-full max-w-lg overflow-hidden animate-in zoom-in-95">
                <div className="p-6 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
                    <h3 className="text-base font-bold text-tcm-darkGreen dark:text-tcm-cream uppercase tracking-widest font-serif-sc">添加供应商</h3>
                    <button onClick={() => setShowAddProviderModal(false)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors">
                        <Icons.X size={20} />
                    </button>
                </div>
                <div className="p-6 space-y-5">
                    
                    {/* ID */}
                    <div className="space-y-1.5">
                        <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest block">名称标识 (英文)</label>
                        <input 
                            type="text" 
                            placeholder="如: openai, anthropic"
                            value={newProviderForm.nameId}
                            onChange={(e) => setNewProviderForm({...newProviderForm, nameId: e.target.value.toLowerCase().replace(/\s+/g, '-')})}
                            className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white text-xs focus:outline-none focus:border-tcm-lightGreen font-mono"
                        />
                    </div>

                    {/* Description */}
                    <div className="space-y-1.5">
                        <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest block">描述</label>
                        <input 
                            type="text" 
                            placeholder="供应商描述..."
                            value={newProviderForm.description}
                            onChange={(e) => setNewProviderForm({...newProviderForm, description: e.target.value})}
                            className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white text-xs focus:outline-none focus:border-tcm-lightGreen"
                        />
                    </div>

                    {/* Default Base URL */}
                    <div className="space-y-1.5">
                        <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest block">默认BASE URL</label>
                        <input 
                            type="text" 
                            placeholder="https://api.example.com/v1"
                            value={newProviderForm.defaultBaseUrl}
                            onChange={(e) => setNewProviderForm({...newProviderForm, defaultBaseUrl: e.target.value})}
                            className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white text-xs focus:outline-none focus:border-tcm-lightGreen font-mono"
                        />
                    </div>

                    {/* Model Types */}
                    <div className="space-y-2">
                        <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest block">支持的模型类型</label>
                        <div className="flex flex-wrap gap-2">
                            {SUPPORTED_MODEL_TYPES.map(type => (
                                <button
                                    key={type.id}
                                    onClick={() => toggleSupportedType(type.id)}
                                    className={`px-3 py-1.5 rounded-lg text-[10px] font-bold transition-all ${
                                        newProviderForm.supportedTypes.includes(type.id)
                                            ? 'bg-tcm-darkGreen text-white shadow-lg'
                                            : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                                    }`}
                                >
                                    {type.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Enabled Toggle */}
                    <div className="pt-2 flex items-center justify-between">
                        <span className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest">启用状态</span>
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => setNewProviderForm({...newProviderForm, isEnabled: !newProviderForm.isEnabled})}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                                    newProviderForm.isEnabled ? 'bg-tcm-lightGreen' : 'bg-gray-200 dark:bg-gray-700'
                                }`}
                            >
                                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${newProviderForm.isEnabled ? 'translate-x-6' : 'translate-x-1'}`} />
                            </button>
                            <span className="text-xs text-gray-600 dark:text-gray-300">{newProviderForm.isEnabled ? '已启用' : '已禁用'}</span>
                        </div>
                    </div>

                </div>
                <div className="p-6 bg-gray-50/50 dark:bg-black/10 border-t border-gray-100 dark:border-gray-700 flex gap-3">
                    <button 
                        onClick={() => setShowAddProviderModal(false)}
                        className="flex-1 py-3 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-200 text-xs font-bold rounded-lg transition-colors"
                    >
                        取消
                    </button>
                    <button 
                        onClick={handleAddProvider}
                        className="flex-1 py-3 bg-tcm-darkGreen hover:bg-tcm-lightGreen text-white text-xs font-bold rounded-lg transition-colors shadow-lg"
                    >
                        创建
                    </button>
                </div>
            </div>
        </div>
      )}

      {/* ADD MODEL MODAL (DETAILED) */}
      {showAddModelModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-white dark:bg-[#1e1e1e] rounded-2xl border border-gray-200 dark:border-gray-700 shadow-2xl w-full max-w-2xl overflow-hidden animate-in zoom-in-95 flex flex-col max-h-[90vh]">
                <div className="p-6 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center shrink-0">
                    <h3 className="text-base font-bold text-tcm-darkGreen dark:text-tcm-cream uppercase tracking-widest font-serif-sc">添加模型配置</h3>
                    <button onClick={() => setShowAddModelModal(false)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors">
                        <Icons.X size={20} />
                    </button>
                </div>
                <div className="p-6 space-y-5 overflow-y-auto custom-scrollbar">
                    
                    <div className="grid grid-cols-2 gap-4">
                        {/* Model Name */}
                        <div className="space-y-1.5">
                            <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest block">模型名称 (API调用用)</label>
                            <input 
                                type="text" 
                                placeholder="如: gpt-4o, claude-3-opus"
                                value={modelForm.id}
                                onChange={(e) => setModelForm({...modelForm, id: e.target.value})}
                                className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white text-xs focus:outline-none focus:border-tcm-lightGreen font-mono"
                            />
                        </div>
                        {/* Model Type */}
                        <div className="space-y-1.5">
                            <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest block">模型类型</label>
                            <select 
                                value={modelForm.type}
                                onChange={(e) => setModelForm({...modelForm, type: e.target.value})}
                                className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white text-xs focus:outline-none focus:border-tcm-lightGreen appearance-none cursor-pointer"
                            >
                                {MODEL_CONFIG_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                            </select>
                        </div>
                    </div>

                    {/* Description */}
                    <div className="space-y-1.5">
                        <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest block">描述</label>
                        <textarea 
                            placeholder="模型描述..."
                            value={modelForm.description}
                            onChange={(e) => setModelForm({...modelForm, description: e.target.value})}
                            className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white text-xs focus:outline-none focus:border-tcm-lightGreen min-h-[80px] resize-none"
                        />
                    </div>

                    {/* Features */}
                    <div className="space-y-2">
                        <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest block">模型特性</label>
                        <div className="flex flex-wrap gap-2">
                            {MODEL_FEATURES.map(feature => (
                                <button
                                    key={feature.id}
                                    onClick={() => toggleModelFeature(feature.id)}
                                    className={`px-3 py-1.5 rounded-lg text-[10px] font-bold transition-all ${
                                        modelForm.features.includes(feature.id)
                                            ? 'bg-tcm-darkGreen text-white shadow-lg'
                                            : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                                    }`}
                                >
                                    {feature.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        {/* Context Window */}
                        <div className="space-y-1.5">
                            <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest block">上下文窗口</label>
                            <input 
                                type="number" 
                                placeholder="4096"
                                value={modelForm.contextWindow}
                                onChange={(e) => setModelForm({...modelForm, contextWindow: parseInt(e.target.value) || 0})}
                                className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white text-xs focus:outline-none focus:border-tcm-lightGreen font-mono"
                            />
                        </div>
                        {/* Max Tokens */}
                        <div className="space-y-1.5">
                            <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest block">最大输出TOKEN</label>
                            <input 
                                type="number" 
                                placeholder="4096"
                                value={modelForm.maxTokens}
                                onChange={(e) => setModelForm({...modelForm, maxTokens: parseInt(e.target.value) || 0})}
                                className="w-full p-3 bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white text-xs focus:outline-none focus:border-tcm-lightGreen font-mono"
                            />
                        </div>
                    </div>

                    {/* Temperature */}
                    <div className="space-y-3">
                        <div className="flex justify-between items-center">
                            <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest">Temperature (温度)</label>
                            <span className="text-xs font-mono font-bold text-tcm-lightGreen">{modelForm.temperature.toFixed(2)}</span>
                        </div>
                        <input 
                            type="range" 
                            min="0" max="2" step="0.1"
                            value={modelForm.temperature}
                            onChange={(e) => setModelForm({...modelForm, temperature: parseFloat(e.target.value)})}
                            className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-tcm-lightGreen"
                        />
                        <div className="flex justify-between text-[10px] text-gray-400 font-bold uppercase">
                            <span>精确 0</span>
                            <span>平衡 1</span>
                            <span>创意 2</span>
                        </div>
                    </div>

                    {/* Top P */}
                    <div className="space-y-3">
                        <div className="flex justify-between items-center">
                            <label className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest">TOP P (核采样)</label>
                            <span className="text-xs font-mono font-bold text-tcm-lightGreen">{modelForm.topP.toFixed(2)}</span>
                        </div>
                        <input 
                            type="range" 
                            min="0" max="1" step="0.05"
                            value={modelForm.topP}
                            onChange={(e) => setModelForm({...modelForm, topP: parseFloat(e.target.value)})}
                            className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-tcm-lightGreen"
                        />
                        <div className="flex justify-between text-[10px] text-gray-400 font-bold uppercase">
                            <span>聚焦 0</span>
                            <span>0.5</span>
                            <span>全部 1</span>
                        </div>
                    </div>

                    {/* Enabled Toggle */}
                    <div className="pt-2 flex items-center justify-between">
                        <span className="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest">启用状态</span>
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => setModelForm({...modelForm, enabled: !modelForm.enabled})}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                                    modelForm.enabled ? 'bg-tcm-lightGreen' : 'bg-gray-200 dark:bg-gray-700'
                                }`}
                            >
                                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${modelForm.enabled ? 'translate-x-6' : 'translate-x-1'}`} />
                            </button>
                            <span className="text-xs text-gray-600 dark:text-gray-300">{modelForm.enabled ? '已启用' : '已禁用'}</span>
                        </div>
                    </div>

                </div>
                <div className="p-6 bg-gray-50/50 dark:bg-black/10 border-t border-gray-100 dark:border-gray-700 flex gap-3 shrink-0">
                    <button 
                        onClick={() => {
                          setShowAddModelModal(false);
                          setEditingModelId(null);
                          setModelForm({
                            id: '',
                            type: 'LLM (大语言模型)',
                            description: '',
                            features: [],
                            contextWindow: 4096,
                            maxTokens: 4096,
                            temperature: 0.7,
                            topP: 1.0,
                            enabled: true
                          });
                        }}
                        className="flex-1 py-3 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-200 text-xs font-bold rounded-lg transition-colors"
                    >
                        取消
                    </button>
                    <button 
                        onClick={editingModelId ? handleUpdateCustomModel : handleCreateCustomModel}
                        className="flex-1 py-3 bg-tcm-darkGreen hover:bg-tcm-lightGreen text-white text-xs font-bold rounded-lg transition-colors shadow-lg"
                    >
                        {editingModelId ? '更新' : '创建'}
                    </button>
                </div>
            </div>
        </div>
      )}

    </div>
  );
};

export default PublicModelManagementPage;
