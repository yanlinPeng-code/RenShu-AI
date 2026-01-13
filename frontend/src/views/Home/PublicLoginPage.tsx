import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserRole } from '../../types/types';
import { Icons } from '../../components/common/Icons';

interface PublicLoginPageProps {
  onLogin: (role: UserRole) => void;
}

const PublicLoginPage: React.FC<PublicLoginPageProps> = ({ onLogin }) => {
  const navigate = useNavigate();
  const [username, setUsername] = React.useState('');
  const [password, setPassword] = React.useState('');

  const handleLogin = () => {
    // Perform login logic here
    onLogin(UserRole.PUBLIC);
  };

  return (
    <div className="w-full h-screen bg-[url('https://images.unsplash.com/photo-1524334228333-0f6db392f8a1?q=80&w=2560&auto=format&fit=crop')] bg-cover bg-center flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-tcm-darkGreen/60 backdrop-blur-sm"></div>
      
      <div className="relative z-10 w-full max-w-md bg-white/95 shadow-2xl rounded-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="h-16 flex items-center justify-center bg-tcm-cream border-b border-tcm-gold/30">
          <h1 className="text-xl font-bold text-tcm-darkGreen font-serif-sc"></h1>
        </div>

        <div className="p-8 flex flex-col gap-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-tcm-darkGreen font-serif-sc">
              欢迎回来
            </h2>
            <p className="text-gray-500 text-sm mt-2">
              请登录以访问健康助手。
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1 uppercase tracking-wider">用户名</label>
              <input 
                type="text" 
                className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen" 
                placeholder="输入用户名" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1 uppercase tracking-wider">密码</label>
              <input 
                type="password" 
                className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <button 
            onClick={handleLogin}
            className="w-full py-4 rounded-xl font-bold text-white shadow-lg transform transition active:scale-95 flex items-center justify-center gap-2 bg-tcm-darkGreen hover:bg-tcm-lightGreen"
          >
            登录 <Icons.ChevronRight size={20}/>
          </button>

          <button onClick={() => navigate('/')} className="text-center text-gray-400 text-sm hover:text-gray-600">
            返回首页
          </button>
        </div>
      </div>
    </div>
  );
};

export default PublicLoginPage;