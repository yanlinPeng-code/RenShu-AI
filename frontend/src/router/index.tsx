import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { HashRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { User, UserRole } from '../types/types';
import LandingPage from '../views/Home/LandingPage';
import PublicPortal from '../views/Public/PublicPortal';
import ProfessionalPortal from '../views/Professional/ProfessionalPortal';
import LoginPage from '../views/Home/LoginPage';

const AppRoutes: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Protect routes
  useEffect(() => {
    if (!user && location.pathname !== '/' && location.pathname !== '/login') {
      navigate('/login');
    }
  }, [user, location.pathname, navigate]);

  const handleLogin = (role: UserRole) => {
    // Mock login logic
    const mockUser: User = {
      id: '123',
      name: role === UserRole.PUBLIC ? 'Wang Xiaoming' : 'Dr. Li Shizhen',
      role: role,
      avatar: role === UserRole.PUBLIC 
        ? 'https://picsum.photos/id/64/200/200' 
        : 'https://picsum.photos/id/55/200/200',
      healthScore: 85,
      persona: role === UserRole.PUBLIC ? {
        age: 'Unknown',
        gender: 'Unknown',
        chiefComplaint: 'None yet',
        medicalHistory: 'None recorded',
        suspectedDiagnosis: 'Pending analysis...',
        contraindications: 'None known',
        recommendedTreatment: 'General wellness'
      } : undefined,
      specialty: role === UserRole.PROFESSIONAL ? 'Integrative Medicine' : undefined
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
