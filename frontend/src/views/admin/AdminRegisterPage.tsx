import React, {useEffect, useState} from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminRegisterRequest } from '../../types';
import { Toast } from '../../components/common/Toast';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';
import {adminAuthApi} from "@/src/api/modules/auth.ts";
interface AdminRegisterPageProps {  
  onRegister: () => void;
}

const AdminRegisterPage: React.FC<AdminRegisterPageProps> = ({ onRegister }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  // const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
const [toastMsg, setToastMsg] = useState<string | null>(null);
  // Toast auto-hide
  useEffect(() => {
    if (toastMsg) {
      const timer = setTimeout(() => setToastMsg(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [toastMsg]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };



  const handleSubmit = async () => {
      if (!formData.username || !formData.password) {
          setError('请填写所有的字段');
          return;
      }
      if (formData.password.length<6){
          setError('密码必须至少6个字符');
          return;
      }
      setLoading(true)
      setError('')
      try {
          await adminAuthApi.register({
              username: formData.username,
              password: formData.password

          });
          //显示注册成功
          setToastMsg('注册成功！');

          //添加小的时延
          setTimeout(() => {
              onRegister();
              navigate('/login/admin');
          }, 150);
      }catch(err:any){
          setError(err.response?.data?.message || '注册失败');
          // 显示错误提示
          setToastMsg(err.response?.data?.message || '注册失败');
    } finally {
          setLoading(false);
    }
  };

  return (
     <div className="w-full h-screen bg-[#020617] flex items-center justify-center p-4 relative overflow-hidden">
      {toastMsg && <Toast message={toastMsg} type="success" onClose={() => setToastMsg(null)} variant="admin" />}
      <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'linear-gradient(#3b82f6 1px, transparent 1px), linear-gradient(90deg, #3b82f6 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

      <div className="relative z-10 w-full max-w-md bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 shadow-2xl rounded-2xl overflow-hidden">
        <div className="p-8 text-center border-b border-slate-800/50">
           <BrandLogo size="md" variant="dark" className="justify-center mb-4" />
           <h2 className="text-lg font-bold text-white uppercase tracking-[0.3em]">Identity Provisioning </h2>
           <p className="text-slate-500 text-[10px] mt-2 font-bold uppercase">系统管理员注册</p>
        </div>

        <div className="p-8 flex flex-col gap-4">
          <div className="space-y-4">
            <div>
              <label className="block text-[10px] font-bold text-slate-500 mb-1 uppercase tracking-widest">用户名</label>
              <input
                name="username"
                value={formData.username}
                onChange={handleChange}
                type="text"
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-all font-mono text-sm"
                placeholder="admin username"
              />
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-500 mb-1 uppercase tracking-widest">密码</label>
              <input
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-all font-mono text-sm"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full py-4 mt-4 bg-white text-slate-900 font-bold rounded-lg hover:bg-blue-400 transition-all flex items-center justify-center gap-2 uppercase text-[10px] tracking-widest"
          >
            {loading ? '注册中...' : <>注册<Icons.ShieldPlus size={16}/></>}
          </button>

          <button onClick={() => navigate('/login/admin')} className="text-center text-slate-500 text-[10px] font-bold uppercase tracking-widest mt-4 hover:text-white transition-colors">
            已有账户? 登录
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminRegisterPage;