import React, { useState, useEffect } from 'react';
import {useLocation, useNavigate} from 'react-router-dom';
import { UserRole } from '../../types';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';
import { authApi } from '../../api';

interface PublicLoginPageProps {
  onLogin: (role: UserRole, userData?: any) => void;
}

const PublicLoginPage: React.FC<PublicLoginPageProps> = ({ onLogin }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: localStorage.getItem('remembered_public_email') || '',
    password: localStorage.getItem('remembered_public_password') || '',
  });
  const [rememberMe, setRememberMe] = useState(!!localStorage.getItem('remembered_public_email'));
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

  const handleRememberMeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRememberMe(e.target.checked);
  };

  const handleSubmit = async () => {
    if (!formData.email || !formData.password) {
      setError('请填写所有字段');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await authApi.login(formData);
      console.log(res);
      localStorage.setItem('user_access_token', res.data.access_token);
      localStorage.setItem('user_refresh_token', res.data.refresh_token);
      localStorage.setItem('user_user_id', res.data.user_id);
      
      // 保存记住的账号密码
      if (rememberMe) {
        localStorage.setItem('remembered_public_email', formData.email);
        localStorage.setItem('remembered_public_password', formData.password);
      } else {
        localStorage.removeItem('remembered_public_email');
        localStorage.removeItem('remembered_public_password');
      }
      
      // 显示成功提示
      setToast({ message: '登录成功！', type: 'success' });
      
      // 小延迟让用户看到提示后再导航
      setTimeout(() => {
        onLogin(UserRole.PUBLIC, res.data);
      }, 100);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.message || '登录失败');
      // 显示错误提示
      setToast({ message: err.response?.data?.message || '登录失败', type: 'error' });
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
           <h2 className="text-2xl font-bold text-tcm-darkGreen font-serif-sc">Public Portal</h2>
           <p className="text-gray-500 text-sm mt-2">
            欢迎使用你的全维健康助手
           </p>
        </div>

        <div className="p-8 pt-2 flex flex-col gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1 uppercase tracking-wider">邮箱</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen text-gray-800"
                placeholder="Enter your email"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1 uppercase tracking-wider">密码</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen text-gray-800"
                placeholder="••••••••"
              />
            </div>
          </div>

          {error && <p className="text-red-500 text-sm text-center">{error}</p>}

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                checked={rememberMe}
                onChange={handleRememberMeChange}
                className="w-4 h-4 text-tcm-darkGreen bg-transparent border-tcm-darkGreen/50 rounded focus:ring-tcm-darkGreen focus:ring-2"
              />
              <label htmlFor="remember-me" className="text-sm text-tcm-darkGreen">
                记住账号密码
              </label>
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full py-4 rounded-xl font-bold text-white shadow-lg transform transition active:scale-95 flex items-center justify-center gap-2 bg-tcm-darkGreen hover:bg-tcm-lightGreen disabled:opacity-50"
          >
            {loading ? '正在登录...' : <>进入 <Icons.ChevronRight size={20}/></>}
          </button>

          <div className="flex items-center justify-between text-sm mt-2">
             <button onClick={() => navigate('/')} className="text-gray-400 hover:text-gray-600 flex items-center gap-1">
               <Icons.ChevronRight className="rotate-180" size={14} /> 返回
             </button>
             <div className="flex gap-2">
                <button className="text-gray-500 hover:underline">忘记密码?</button>
                <span className="text-gray-300">|</span>
                <button onClick={() => navigate('/register/public')} className="text-tcm-lightGreen font-bold hover:underline">注册 </button>
             </div>
          </div>
        </div>

        <div className="h-1.5 w-full bg-gradient-to-r from-tcm-lightGreen to-tcm-freshGreen"></div>
      </div>
    </div>
  );
};

export default PublicLoginPage;
