
import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { HashRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { User, UserRole } from '../types/types';
import LandingPage from '../views/Home/LandingPage';
import PublicPortal from '../views/Public/PublicPortal';
import ProfessionalPortal from '../views/Professional/ProfessionalPortal';
import LoginPage from '../views/Home/LoginPage';
import PublicLoginPage from '../views/Home/PublicLoginPage';
import ProfessionalLoginPage from '../views/Home/ProfessionalLoginPage';

const AppRoutes: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Protect routes
  useEffect(() => {
    if (!user && location.pathname !== '/' && !location.pathname.startsWith('/login')) {
      // Redirect to general login page which will redirect to public login
      navigate('/login');
    }
  }, [user, location.pathname, navigate]);

  const handleLogin = (role: UserRole) => {
    // Mock login logic
    const mockUser: User = {
      id: '123',
      name: role === UserRole.PUBLIC ? '王小明' : '李时珍医生',
      role: role,
      avatar: role === UserRole.PUBLIC 
        ? 'https://picsum.photos/id/64/200/200' 
        : 'https://picsum.photos/id/55/200/200',
      healthScore: 85,
      persona: role === UserRole.PUBLIC ? {
        age: '未知',
        gender: '未知',
        chiefComplaint: '暂无',
        medicalHistory: '无记录',
        suspectedDiagnosis: '待分析...',
        contraindications: '无已知',
        recommendedTreatment: '一般保健'
      } : undefined,
      specialty: role === UserRole.PROFESSIONAL ? '整合医学' : undefined
    };
    setUser(mockUser);
    navigate(role === UserRole.PUBLIC ? '/public' : '/professional');
  };

  const handleLogout = () => {
    setUser(null);
    navigate('/');
  };

  return (
    <div className="h-screen w-full bg-tcm-cream text-tcm-charcoal overflow-hidden selection:bg-tcm-lightGreen selection:text-white">
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
        <Route path="/login/public" element={<PublicLoginPage onLogin={handleLogin} />} />
        <Route path="/login/professional" element={<ProfessionalLoginPage onLogin={handleLogin} />} />
        <Route 
          path="/public" 
          element={user ? <PublicPortal user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/professional" 
          element={user ? <ProfessionalPortal user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
        />
      </Routes>
    </div>
  );
};

export default AppRoutes;
