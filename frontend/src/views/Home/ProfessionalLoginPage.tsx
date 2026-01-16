import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserRole } from '../../types';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';
import { authApi } from '../../api';

interface ProfessionalLoginPageProps {
  onLogin: (role: UserRole, userData?: any) => void;
}

const ProfessionalLoginPage: React.FC<ProfessionalLoginPageProps> = ({ onLogin }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: localStorage.getItem('remembered_email') || '',
    password: localStorage.getItem('remembered_password') || '',
  });
  const [rememberMe, setRememberMe] = useState(!!localStorage.getItem('remembered_email'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('refresh_token', res.data.refresh_token);
      localStorage.setItem('user_id', res.data.user_id);
      
      // 保存记住的账号密码
      if (rememberMe) {
        localStorage.setItem('remembered_email', formData.email);
        localStorage.setItem('remembered_password', formData.password);
      } else {
        localStorage.removeItem('remembered_email');
        localStorage.removeItem('remembered_password');
      }
      
      onLogin(UserRole.PROFESSIONAL, res.data);

    } catch (err: any) {
      setError(err.response?.data?.message || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full h-screen bg-[url('https://images.unsplash.com/photo-1666214280557-f1b5022eb634?q=80&w=2670&auto=format&fit=crop')] bg-cover bg-center flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-tcm-darkGreen/80 backdrop-blur-md"></div>

      <div className="relative z-10 w-full max-w-md bg-tcm-darkGreen border border-tcm-gold/20 shadow-2xl rounded-sm overflow-hidden flex flex-col">
        <div className="p-8 pb-4 text-center">
           <div className="flex justify-center mb-6">
             <BrandLogo size="lg" variant="dark" />
           </div>
           <div className="flex items-center justify-center gap-2 mb-2">
             <div className="h-px w-8 bg-tcm-gold/50"></div>
             <h2 className="text-xl font-bold text-tcm-gold font-serif-sc uppercase tracking-widest">Clinical Access </h2>
             <div className="h-px w-8 bg-tcm-gold/50"></div>
           </div>
           <p className="text-gray-400 text-xs">
             仅限授权医务人员使用
           </p>
        </div>

        <div className="p-8 pt-2 flex flex-col gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-tcm-gold/80 mb-1 uppercase tracking-wider">邮箱</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full p-3 bg-black/20 border border-tcm-gold/20 rounded-none focus:outline-none focus:border-tcm-gold text-white placeholder-gray-600 transition-colors"
                placeholder="email@hospital.org"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-tcm-gold/80 mb-1 uppercase tracking-wider">密码</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full p-3 bg-black/20 border border-tcm-gold/20 rounded-none focus:outline-none focus:border-tcm-gold text-white placeholder-gray-600 transition-colors"
                placeholder="••••••••"
              />
            </div>
          </div>

          {error && <p className="text-red-400 text-sm text-center">{error}</p>}

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                checked={rememberMe}
                onChange={handleRememberMeChange}
                className="w-4 h-4 text-tcm-gold bg-transparent border-tcm-gold/50 rounded focus:ring-tcm-gold focus:ring-2"
              />
              <label htmlFor="remember-me" className="text-sm text-tcm-gold/80">
                记住账号密码
              </label>
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full py-4 mt-2 font-bold text-tcm-darkGreen bg-tcm-gold hover:bg-white transition-colors flex items-center justify-center gap-2 rounded-none uppercase tracking-wide text-sm disabled:opacity-50"
          >
            {loading ? '认证中...' : <> 登录 <Icons.ShieldPlus size={18}/></>}
          </button>

          <div className="flex items-center justify-between text-sm mt-4">
             <button onClick={() => navigate('/')} className="text-gray-500 hover:text-gray-300 flex items-center gap-1 transition-colors">
               <Icons.ChevronRight className="rotate-180" size={14} /> 返回
             </button>
             <button onClick={() => navigate('/register/professional')} className="text-tcm-gold/70 hover:text-tcm-gold text-xs">
               新员工注册
             </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfessionalLoginPage;
