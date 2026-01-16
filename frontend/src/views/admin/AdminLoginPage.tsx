import React from 'react';
import { useNavigate } from 'react-router-dom';
import { UserRole } from '../../types';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';

interface AdminLoginPageProps {
  onLogin: (role: UserRole) => void;
}

const AdminLoginPage: React.FC<AdminLoginPageProps> = ({ onLogin }) => {
  const navigate = useNavigate();

  return (
    <div className="w-full h-screen bg-[#020617] flex items-center justify-center p-4 overflow-hidden relative">
      {/* 科技感背景装饰 */}
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
           <p className="text-slate-500 text-[10px] mt-2 uppercase tracking-widest font-bold">Secure Core Access Only</p>
        </div>

        <div className="p-8 flex flex-col gap-6">
          <div className="space-y-4">
            <div className="group">
              <label className="block text-[10px] font-bold text-slate-500 mb-2 uppercase tracking-widest group-focus-within:text-blue-400 transition-colors">Credential ID</label>
              <div className="relative">
                <Icons.ShieldPlus className="absolute left-3 top-3 text-slate-600 group-focus-within:text-blue-500 transition-colors" size={16} />
                <input type="text" className="w-full p-3 pl-10 bg-slate-950 border border-slate-800 rounded-lg focus:outline-none focus:border-blue-500 text-white placeholder-slate-700 transition-all font-mono text-sm" placeholder="root_admin" />
              </div>
            </div>
            <div className="group">
              <label className="block text-[10px] font-bold text-slate-500 mb-2 uppercase tracking-widest group-focus-within:text-blue-400 transition-colors">Access Key</label>
              <div className="relative">
                <Icons.Settings className="absolute left-3 top-3 text-slate-600 group-focus-within:text-blue-500 transition-colors" size={16} />
                <input type="password" className="w-full p-3 pl-10 bg-slate-950 border border-slate-800 rounded-lg focus:outline-none focus:border-blue-500 text-white placeholder-slate-700 transition-all font-mono text-sm" placeholder="••••••••" />
              </div>
            </div>
          </div>

          <button
            onClick={() => onLogin(UserRole.ADMIN)}
            className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg shadow-lg shadow-blue-900/20 transform transition active:scale-95 flex items-center justify-center gap-2 uppercase tracking-widest text-xs"
          >
            Initiate Auth <Icons.Zap size={16}/>
          </button>

          <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-slate-600">
             <button onClick={() => navigate('/')} className="hover:text-slate-300 transition-colors">← Root</button>
             <button onClick={() => navigate('/register/admin')} className="text-blue-500 hover:text-blue-400">Request New ID</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminLoginPage;