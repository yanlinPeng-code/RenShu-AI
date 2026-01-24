import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';
import { authApi } from '../../api';

interface PublicRegisterPageProps {
  onRegisterSuccess: () => void;
}

const PublicRegisterPage: React.FC<PublicRegisterPageProps> = ({ onRegisterSuccess }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Toast auto-hide
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async () => {
    if (!formData.username || !formData.email || !formData.password) {
      setError('请填写所有字段');
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('密码不匹配');
      return;
    }
    if (formData.password.length < 6) {
      setError('密码必须至少6个字符');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await authApi.register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        role: 'patient'
      });
      
      // 显示成功提示
      setToast({ message: '注册成功！', type: 'success' });
      
      // 小延迟让用户看到提示后再导航
      setTimeout(() => {
        onRegisterSuccess();
        navigate('/login/public');
      }, 150);
    } catch (err: any) {
      setError(err.response?.data?.message || '注册失败');
      // 显示错误提示
      setToast({ message: err.response?.data?.message || '注册失败', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full h-screen bg-[url('https://images.unsplash.com/photo-1544367563-12123d8965cd?q=80&w=2670&auto=format&fit=crop')] bg-cover bg-center flex items-center justify-center p-4 relative">
      {/* Toast Notification */}
      {toast && (
        <div className="fixed top-6 left-1/2 transform -translate-x-1/2 z-[100] animate-in fade-in slide-in-from-top-4 duration-300">
          <div className={`px-6 py-3 rounded-full shadow-2xl flex items-center gap-3 border ${
            toast.type === 'success' 
              ? 'bg-tcm-darkGreen text-white border-tcm-lightGreen/20' 
              : 'bg-red-600 text-white border-red-400'
          }`}>
            {toast.type === 'success' ? <Icons.Check size={18} className="text-tcm-gold" /> : <Icons.X size={18} />}
            <span className="text-sm font-bold tracking-wide">{toast.message}</span>
          </div>
        </div>
      )}
      
      <div className="absolute inset-0 bg-tcm-freshGreen/40 backdrop-blur-sm"></div>

      <div className="relative z-10 w-full max-w-md bg-white/95 shadow-2xl rounded-2xl overflow-hidden flex flex-col border border-white">
        <div className="p-8 pb-4 text-center">
           <div className="flex justify-center mb-4">
             <BrandLogo size="lg" />
           </div>
           <h2 className="text-2xl font-bold text-tcm-darkGreen font-serif-sc"></h2>
           <p className="text-gray-500 text-sm mt-2">
              记入我们的 wellness 社区。
           </p>
        </div>

        <div className="p-8 pt-2 flex flex-col gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1 uppercase tracking-wider">用户名</label>
            <input name="username" value={formData.username} onChange={handleChange} type="text" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen text-gray-800" placeholder="Choose a username" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1 uppercase tracking-wider">邮箱</label>
            <input name="email" value={formData.email} onChange={handleChange} type="email" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen text-gray-800" placeholder="your@email.com" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1 uppercase tracking-wider">密码</label>
            <input name="password" value={formData.password} onChange={handleChange} type="password" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen text-gray-800" placeholder="••••••••" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1 uppercase tracking-wider">确认密码</label>
            <input name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} type="password" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen text-gray-800" placeholder="••••••••" />
          </div>

          {error && <p className="text-red-500 text-sm text-center">{error}</p>}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full py-4 mt-2 rounded-xl font-bold text-white shadow-lg transform transition active:scale-95 flex items-center justify-center gap-2 bg-tcm-darkGreen hover:bg-tcm-lightGreen disabled:opacity-50"
          >
            {loading ? '创建账户...' : <>注册 <Icons.ChevronRight size={20}/></>}
          </button>

          <div className="flex items-center justify-center text-sm mt-2 gap-1">
             <span className="text-gray-500">已有账户?</span>
             <button onClick={() => navigate('/login/public')} className="text-tcm-lightGreen font-bold hover:underline">
               登录
             </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicRegisterPage;
