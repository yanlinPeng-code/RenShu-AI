import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { UserRole } from '../types';
import { useAuth } from '../contexts/AuthContext';
import ProtectedRoute from './ProtectedRoute';
// 页面组件
import LandingPage from '../views/home/LandingPage';
import PublicPortal from '../views/public/PublicPortal';
import ProfessionalPortal from '../views/professional/ProfessionalPortal';
import PublicLoginPage from '../views/public/PublicLoginPage';
import ProfessionalLoginPage from '../views/professional/ProfessionalLoginPage';
import PublicRegisterPage from '../views/public/PublicRegisterPage';
import ProfessionalRegisterPage from '../views/professional/ProfessionalRegisterPage';
import AdminLoginPage from '../views/admin/AdminLoginPage';
import AdminRegisterPage from '../views/admin/AdminRegisterPage';
import AdminPortal from '../views/admin/AdminPortal';
import PublicModelManagementPage from '../views/public/PublicModelManagementPage';


const AppContent: React.FC = () => {
    // const { user, toast, login, logout } = useAuth();
    const { user, login, logout } = useAuth();
    const handleRegisterSuccess = () => {
        console.log('Registration successful');
    };

    return (
        <div className="h-screen w-full bg-tcm-cream text-tcm-charcoal overflow-hidden selection:bg-tcm-lightGreen selection:text-white relative">

            <Routes>
                {/* 公开路由 */}
                <Route path="/" element={<LandingPage />} />

                {/* 登录路由 */}
                <Route path="/login/public" element={<PublicLoginPage onLogin={login} />} />
                <Route path="/login/professional" element={<ProfessionalLoginPage onLogin={login} />} />
                <Route path="/login/admin" element={<AdminLoginPage onLogin={login} />} />
                <Route path="/login" element={<Navigate to="/login/public" />} />

                {/* 注册路由 */}
                <Route path="/register/public" element={<PublicRegisterPage onRegisterSuccess={handleRegisterSuccess} />} />
                <Route path="/register/professional" element={<ProfessionalRegisterPage onRegisterSuccess={handleRegisterSuccess} />} />
                <Route path="/register/admin" element={<AdminRegisterPage onRegister={handleRegisterSuccess} />} />

                {/* 受保护的路由 - Public */}
                <Route
                    path="/public"
                    element={
                        <ProtectedRoute allowedRoles={[UserRole.PUBLIC]} redirectTo="/">
                            <PublicPortal user={user!} onLogout={logout} />
                        </ProtectedRoute>
                    }
                />
                  {/* 新增模型管理路由 */}
                <Route
                    path="/public/models"
                    element={
                        <ProtectedRoute allowedRoles={[UserRole.PUBLIC]} redirectTo="/">
                            <PublicModelManagementPage />
                        </ProtectedRoute>
                    }
                />

                {/* 受保护的路由 - Professional */}
                <Route
                    path="/professional"
                    element={
                        <ProtectedRoute allowedRoles={[UserRole.PROFESSIONAL]} redirectTo="/">
                            <ProfessionalPortal user={user!} onLogout={logout} />
                        </ProtectedRoute>
                    }
                />

                {/* 受保护的路由 - Admin */}
                <Route
                    path="/admin"
                    element={
                        <ProtectedRoute allowedRoles={[UserRole.ADMIN]} redirectTo="/login/admin">
                            <AdminPortal user={user!} onLogout={logout} />
                        </ProtectedRoute>
                    }
                />
            </Routes>
        </div>
    );
};

export default AppContent;
