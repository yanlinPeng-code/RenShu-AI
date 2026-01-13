import React from 'react';
import { useNavigate } from 'react-router-dom';
import { UserRole } from '../../types/types';
import { Icons } from '../../components/common/Icons';

interface LoginPageProps {
  onLogin: (role: UserRole) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const navigate = useNavigate();
  
  // Auto redirect to role-specific login pages
  React.useEffect(() => {
    // For backward compatibility, redirect to public login by default
    navigate('/login/public');
  }, [navigate]);
  
  return null; // This component will redirect before rendering anything

  return (
    <div className="w-full h-screen bg-[url('https://images.unsplash.com/photo-1524334228333-0f6db392f8a1?q=80&w=2560&auto=format&fit=crop')] bg-cover bg-center flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-tcm-darkGreen/60 backdrop-blur-sm"></div>
      
      <div className="relative z-10 w-full max-w-md bg-white/95 shadow-2xl rounded-2xl overflow-hidden flex flex-col">
        <div className="p-8 flex flex-col gap-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-tcm-darkGreen font-serif-sc">
              正在跳转到登录页面...
            </h2>
            <p className="text-gray-500 text-sm mt-2">
              请稍候...
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;