import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { UserRole } from '../../types/types';
import { Icons } from '../../components/common/Icons';

interface LoginPageProps {
  onLogin: (role: UserRole) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const location = useLocation();
  const navigate = useNavigate();
  // Determine default tab based on where they came from
  const initialRole = location.state?.role === 'professional' ? UserRole.PROFESSIONAL : UserRole.PUBLIC;
  const [role, setRole] = React.useState<UserRole>(initialRole);

  return (
    <div className="w-full h-screen bg-[url('https://images.unsplash.com/photo-1524334228333-0f6db392f8a1?q=80&w=2560&auto=format&fit=crop')] bg-cover bg-center flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-tcm-darkGreen/60 backdrop-blur-sm"></div>

      <div className="relative z-10 w-full max-w-md bg-white/95 shadow-2xl rounded-2xl overflow-hidden flex flex-col">
        {/* Header Tabs */}
        <div className="flex h-16">
          <button
            onClick={() => setRole(UserRole.PUBLIC)}
            className={`flex-1 flex items-center justify-center font-serif-sc text-lg transition-colors ${role === UserRole.PUBLIC ? 'bg-tcm-cream text-tcm-darkGreen font-bold border-b-4 border-tcm-darkGreen' : 'bg-gray-100 text-gray-500'}`}
          >
            Public Access
          </button>
          <button
            onClick={() => setRole(UserRole.PROFESSIONAL)}
            className={`flex-1 flex items-center justify-center font-serif-sc text-lg transition-colors ${role === UserRole.PROFESSIONAL ? 'bg-tcm-cream text-tcm-darkGreen font-bold border-b-4 border-tcm-gold' : 'bg-gray-100 text-gray-500'}`}
          >
            Medical Staff
          </button>
        </div>

        <div className="p-8 flex flex-col gap-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-tcm-darkGreen font-serif-sc">
              {role === UserRole.PUBLIC ? 'Welcome Back' : 'Doctor Login'}
            </h2>
            <p className="text-gray-500 text-sm mt-2">
              Please sign in to access the {role === UserRole.PUBLIC ? 'health assistant' : 'clinical system'}.
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1 uppercase tracking-wider">Username</label>
              <input type="text" className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen" placeholder="Enter username" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1 uppercase tracking-wider">Password</label>
              <input type="password" className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-tcm-lightGreen" placeholder="••••••••" />
            </div>
          </div>

          <button
            onClick={() => onLogin(role)}
            className={`w-full py-4 rounded-xl font-bold text-white shadow-lg transform transition active:scale-95 flex items-center justify-center gap-2
              ${role === UserRole.PUBLIC ? 'bg-tcm-darkGreen hover:bg-tcm-lightGreen' : 'bg-tcm-gold hover:bg-yellow-500 text-black'}
            `}
          >
            Sign In <Icons.ChevronRight size={20}/>
          </button>

          <button onClick={() => navigate('/')} className="text-center text-gray-400 text-sm hover:text-gray-600">
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;