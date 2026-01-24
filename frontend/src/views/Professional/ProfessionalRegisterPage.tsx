import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';
import { authApi } from '../../api';

interface ProfessionalRegisterPageProps {
  onRegisterSuccess: () => void;
}

const ProfessionalRegisterPage: React.FC<ProfessionalRegisterPageProps> = ({ onRegisterSuccess }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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
        role: 'doctor'
      });
      onRegisterSuccess();
      navigate('/login/professional');
    } catch (err: any) {
      setError(err.response?.data?.message || '注册失败');
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
             <h2 className="text-xl font-bold text-tcm-gold font-serif-sc uppercase tracking-widest">Physician Registration</h2>
             <div className="h-px w-8 bg-tcm-gold/50"></div>
           </div>
           <p className="text-gray-400 text-xs">
             系统访问凭证申请。
           </p>
        </div>

        <div className="p-8 pt-2 flex flex-col gap-4">
          <div>
            <label className="block text-xs font-semibold text-tcm-gold/80 mb-1 uppercase tracking-wider">全名 / ID</label>
            <input name="username" value={formData.username} onChange={handleChange} type="text" className="w-full p-3 bg-black/20 border border-tcm-gold/20 rounded-none focus:outline-none focus:border-tcm-gold text-white placeholder-gray-600 transition-colors" placeholder="Dr. Name or ID" />
          </div>
           <div>
            <label className="block text-xs font-semibold text-tcm-gold/80 mb-1 uppercase tracking-wider">机构邮箱</label>
            <input name="email" value={formData.email} onChange={handleChange} type="email" className="w-full p-3 bg-black/20 border border-tcm-gold/20 rounded-none focus:outline-none focus:border-tcm-gold text-white placeholder-gray-600 transition-colors" placeholder="email@hospital.org" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-tcm-gold/80 mb-1 uppercase tracking-wider">密码</label>
            <input name="password" value={formData.password} onChange={handleChange} type="password" className="w-full p-3 bg-black/20 border border-tcm-gold/20 rounded-none focus:outline-none focus:border-tcm-gold text-white placeholder-gray-600 transition-colors" placeholder="••••••••" />
          </div>
           <div>
            <label className="block text-xs font-semibold text-tcm-gold/80 mb-1 uppercase tracking-wider">确认密码</label>
            <input name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} type="password" className="w-full p-3 bg-black/20 border border-tcm-gold/20 rounded-none focus:outline-none focus:border-tcm-gold text-white placeholder-gray-600 transition-colors" placeholder="••••••••" />
          </div>

          {error && <p className="text-red-400 text-sm text-center">{error}</p>}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full py-4 mt-2 font-bold text-tcm-darkGreen bg-tcm-gold hover:bg-white transition-colors flex items-center justify-center gap-2 rounded-none uppercase tracking-wide text-sm disabled:opacity-50"
          >
            {loading ? '提交中...' : <>提交申请 <Icons.ShieldPlus size={18}/></>}
          </button>

          <div className="flex items-center justify-between text-sm mt-4">
             <button onClick={() => navigate('/')} className="text-gray-500 hover:text-gray-300 flex items-center gap-1 transition-colors">
               <Icons.ChevronRight className="rotate-180" size={14} /> 返回
             </button>
             <button onClick={() => navigate('/login/professional')} className="text-tcm-gold/70 hover:text-tcm-gold text-xs">
               既有用户? 登录
             </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfessionalRegisterPage;
