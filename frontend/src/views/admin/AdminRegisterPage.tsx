import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { RegisterRequest } from '../../types/api.types';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';

interface AdminRegisterPageProps {  
  onRegister: (data: RegisterRequest) => void;
}

const AdminRegisterPage: React.FC<AdminRegisterPageProps> = ({ onRegister }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });

  const handleSubmit = () => {
    onRegister({
      ...formData,
      role: 'admin'
    });
  };

  return (
    <div className="w-full h-screen bg-[#020617] flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'linear-gradient(#3b82f6 1px, transparent 1px), linear-gradient(90deg, #3b82f6 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

      <div className="relative z-10 w-full max-w-md bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 shadow-2xl rounded-2xl overflow-hidden">
        <div className="p-8 text-center border-b border-slate-800/50">
           <BrandLogo size="md" variant="dark" className="justify-center mb-4" />
           <h2 className="text-lg font-bold text-white uppercase tracking-[0.3em]">Identity Provisioning</h2>
           <p className="text-slate-500 text-[10px] mt-2 font-bold uppercase">System Operator Enrollment</p>
        </div>

        <div className="p-8 flex flex-col gap-4">
          <div className="space-y-4">
            <div>
              <label className="block text-[10px] font-bold text-slate-500 mb-1 uppercase tracking-widest">Admin Alias</label>
              <input
                value={formData.username}
                onChange={e => setFormData({...formData, username: e.target.value})}
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-all font-mono text-sm"
                placeholder="sys_admin_01"
              />
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-500 mb-1 uppercase tracking-widest">Internal Mail</label>
              <input
                value={formData.email}
                onChange={e => setFormData({...formData, email: e.target.value})}
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-all font-mono text-sm"
                placeholder="ops@renshu.ai"
              />
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-500 mb-1 uppercase tracking-widest">Secure Keyphrase</label>
              <input
                type="password"
                value={formData.password}
                onChange={e => setFormData({...formData, password: e.target.value})}
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-all font-mono text-sm"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            onClick={handleSubmit}
            className="w-full py-4 mt-4 bg-white text-slate-900 font-bold rounded-lg hover:bg-blue-400 transition-all flex items-center justify-center gap-2 uppercase text-[10px] tracking-widest"
          >
            Provision Account <Icons.ShieldPlus size={16}/>
          </button>

          <button onClick={() => navigate('/login/admin')} className="text-center text-slate-500 text-[10px] font-bold uppercase tracking-widest mt-4 hover:text-white transition-colors">
            Already in system? Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminRegisterPage;