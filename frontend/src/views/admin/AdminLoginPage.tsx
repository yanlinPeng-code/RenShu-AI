import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ApiResponse, AuthResponse, UserRole } from '../../types';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';
import { adminAuthApi } from '@/src/api/modules/auth';
import { Toast } from '../../components/common/Toast';
interface AdminLoginPageProps {
  onLogin: (role: UserRole, userData: any) => void;
}

const AdminLoginPage: React.FC<AdminLoginPageProps> = ({ onLogin }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: localStorage.getItem('remembered_admin_username') || '',
    password: localStorage.getItem('remembered_admin_password') || ''
  });
  const [rememberMe, setRememberMe] = useState(!!localStorage.getItem('remembered_admin_username'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  // const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | '' } | null>(null);
  

  // toast 自动隐藏
  useEffect(()=>{
    if(toastMsg){
      const timer = setTimeout(() => setToastMsg(null), 3000);
      return () => clearTimeout(timer);
    }



  }, [toastMsg])
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };
  
  const handleRememberMeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRememberMe(e.target.checked);
  };


  const handleSubmit = async () => {
    if (!formData.username || !formData.password){
      setError('请输入用户名和密码')
      return;
    }
    setLoading(true);
    setError('');


    try{
        const res: ApiResponse<AuthResponse> = await adminAuthApi.login({
          username: formData.username,
          password: formData.password
        });
        localStorage.setItem('admin_access_token', res.data.access_token);
        localStorage.setItem('admin_refresh_token', res.data.refresh_token);
        localStorage.setItem('admin_user_id', res.data.user_id);
        localStorage.setItem('admin_expires_in', String(res.data.expires_in));
        //如果记住我
        if (rememberMe) {
          localStorage.setItem('remembered_admin_username', formData.username);
          localStorage.setItem('remembered_admin_password', formData.password);
        } else {
          localStorage.removeItem('remembered_admin_username');
          localStorage.removeItem('remembered_admin_password');
        }
        //toast显示登录成功
        setToastMsg('登录成功！');
        //添加小的延迟让用户看到提示后再导航
        setTimeout(() => {
          onLogin(UserRole.ADMIN, res.data);
        }, 100);
    } catch (error) {
      console.error('登录失败:', error);
      setError('登录失败，请检查用户名和密码');
      setToastMsg('登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);









    }


  };








  return (
    <div className="w-full h-screen bg-[#020617] flex items-center justify-center p-4 overflow-hidden relative">
      {toastMsg && <Toast message={toastMsg} type="success" onClose={() => setToastMsg(null)} variant="admin" />}
      <div className="absolute inset-0 opacity-20" style={{ 
        backgroundImage: 'radial-gradient(#3b82f6 1px, transparent 1px)', 
        backgroundSize: '30px 30px' 
      }}></div>



      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/10 rounded-full blur-[120px]"></div>

      <div className="relative z-10 w-full max-w-md bg-slate-900/40 backdrop-blur-2xl border border-slate-700/50 shadow-[0_0_50px_rgba(0,0,0,0.5)] rounded-2xl overflow-hidden flex flex-col">
        <div className="p-8 text-center border-b border-slate-800/50">
           <div className="flex justify-center mb-6">
             <BrandLogo size="lg" variant="dark" />
           </div>
            <h2 className="text-xl font-bold text-white tracking-[0.2em] uppercase font-sans">System Administration</h2>
           <p className="text-slate-500 text-[10px] mt-2 uppercase tracking-widest font-bold">仅限安全核心访问</p>
        </div>

        <div className="p-8 flex flex-col gap-6">
          <div className="space-y-4">
            <div className="group">
              <label className="block text-[10px] font-bold text-slate-500 mb-2 uppercase tracking-widest group-focus-within:text-blue-400 transition-colors">认证ID</label>
              <div className="relative">
                <Icons.ShieldPlus className="absolute left-3 top-3 text-slate-600 group-focus-within:text-blue-500 transition-colors" size={16} />
                <input 
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full p-3 pl-10 bg-slate-950 border border-slate-800 rounded-lg focus:outline-none focus:border-blue-500 text-white placeholder-slate-700 transition-all font-mono text-sm" placeholder="root_admin" />
              </div>
            </div>
            <div className="group">
              <label className="block text-[10px] font-bold text-slate-500 mb-2 uppercase tracking-widest group-focus-within:text-blue-400 transition-colors">访问密钥</label>
              <div className="relative">
                <Icons.Settings className="absolute left-3 top-3 text-slate-600 group-focus-within:text-blue-500 transition-colors" size={16} />
                <input 
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  type="password" 
                  className="w-full p-3 pl-10 bg-slate-950 border border-slate-800 rounded-lg focus:outline-none focus:border-blue-500 text-white placeholder-slate-700 transition-all font-mono text-sm" placeholder="••••••••" />
              </div>
            </div>
          </div>
          {error && <p className="text-red-500 text-[10px] uppercase tracking-widest font-bold">{error}</p>}
          <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <input
                  id="rememberMe"
                  name="rememberMe"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={handleRememberMeChange}
                  className="w-5 h-5 bg-slate-950 border border-slate-800 rounded focus:outline-none focus:border-blue-500"
                />
                <label htmlFor="rememberMe" className="text-[10px] font-bold uppercase tracking-widest text-slate-600">记住我</label>
              </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg shadow-lg shadow-blue-900/20 transform transition active:scale-95 flex items-center justify-center gap-2 uppercase tracking-widest text-xs"
          >
            {loading ? '正在登录...' : '登录'}
            <Icons.Zap size={16}/>
          </button>

          <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-slate-600">
             <button  className="hover:text-slate-300 transition-colors">
              <Icons.ChevronRight className="mr-2" size={16} />← 返回</button>
            <div className='flex  gap-2'>
                <button className='text-blue-500 hover:text-blue-400'>忘记密码</button>
                <span className='text-blue-500 hover:text-blue-400'>|</span> 
                <button onClick={()=>navigate('/register/admin')} className='text-blue-500 hover:text-blue-400'>注册</button>
            </div>
          </div>
             
    
        </div>
      </div>
    </div>
  );
};

export default AdminLoginPage;