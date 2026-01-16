import React, {useState, useEffect} from 'react';
import {Routes, Route, Navigate, useNavigate, useLocation} from 'react-router-dom';
import { Icons } from '../components/common/Icons';
import {User, UserRole, UserPersona} from '../types';
import LandingPage from '../views/Home/LandingPage';
import PublicPortal from '../views/Public/PublicPortal';
import ProfessionalPortal from '../views/Professional/ProfessionalPortal';
import PublicLoginPage from '../views/Home/PublicLoginPage';
import ProfessionalLoginPage from '../views/Home/ProfessionalLoginPage';
import PublicRegisterPage from '../views/Home/PublicRegisterPage';
import ProfessionalRegisterPage from '../views/Home/ProfessionalRegisterPage';
import AdminLoginPage from '../views/admin/AdminLoginPage';
import AdminRegisterPage from '../views/admin/AdminRegisterPage';
import AdminPortal from '../views/admin/AdminPortal';
import {authApi} from '../api';

const AppContent: React.FC = () => {
    const [user, setUser] = useState<User | null>(null);
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
    const navigate = useNavigate();
    const location = useLocation();

    // Toast auto-hide
    useEffect(() => {
        if (toast) {
            const timer = setTimeout(() => setToast(null), 3000);
            return () => clearTimeout(timer);
        }
    }, [toast]);

    // 初始化时检查本地存储的登录状态
    useEffect(() => {
        const token = localStorage.getItem('access_token');
        const savedUser = localStorage.getItem('user');
        if (token && savedUser) {
            setUser(JSON.parse(savedUser));
        }
    }, []);

    // 保护路由
    useEffect(() => {
        // 只有在页面加载或切换页面时，而不是在登出操作期间，才执行路由保护
        if (!user && location.pathname !== '/' && !location.pathname.startsWith('/login') && !location.pathname.startsWith('/register')) {
            navigate('/');
        }
    }, [user, location.pathname]);

    const handleLogin = async (role: UserRole, authData?: any) => {
        try {
            // 获取用户详细信息
            const userInfo = await authApi.getMe();
            const userData = userInfo.data;

            const loggedInUser: User = {
                id: authData?.user_id || userData.id,
                name: userData.username || userData.real_name || 'User',
                role: role,
                avatar: userData.avatar_url || (role === UserRole.PUBLIC
                    ? 'https://picsum.photos/id/64/200/200'
                    : 'https://picsum.photos/id/55/200/200'),
                healthScore: 85,
                persona: role === UserRole.PUBLIC ? {
                    age: '18',
                    gender: userData.gender || '男',
                    chiefComplaint: '发热，头疼 ',
                    medicalHistory: '无记录',
                    suspectedDiagnosis: '待分析...',
                    contraindications: '无禁忌',
                    recommendedTreatment: '一般 wellness 建议'
                } : undefined,
                specialty: role === UserRole.PROFESSIONAL ? 'Integrative Medicine' : undefined
            };

            setUser(loggedInUser);
            localStorage.setItem('user', JSON.stringify(loggedInUser));

            // 导航到相应页面
            if (role === UserRole.PUBLIC) {
                navigate('/public');
            } else if (role === UserRole.PROFESSIONAL) {
                navigate('/professional');
            } else if (role === UserRole.ADMIN) {
                navigate('/admin');
            }

        } catch {
            // 如果获取用户信息失败，使用基本信息
            const basicUser: User = {
                id: authData?.user_id || 'unknown',
                name: 'User',
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
            setUser(basicUser);
            localStorage.setItem('user', JSON.stringify(basicUser));

            // 导航到相应页面
            if (role === UserRole.PUBLIC) {
                navigate('/public');
            } else if (role === UserRole.PROFESSIONAL) {
                navigate('/professional');
            } else if (role === UserRole.ADMIN) {
                navigate('/admin');
            }

        }
    };

    const handleRegisterSuccess = () => {
        // 注册成功后的回调，可以显示提示信息
        console.log('Registration successful');
    };

    const handleLogout = async () => {
        try {
            await authApi.logout();
            // 显示登出成功提示
            setToast({ message: '登出成功！', type: 'success' });
        } catch {
            // 即使登出API失败，也清除本地状态
            setToast({ message: '登出时出现问题，但仍已退出登录。', type: 'error' });
        }
        
        // 立即清除本地状态
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user');
        
        // 立即更新用户状态并导航到根目录，防止页面闪烁
        setUser(null);
        
        // 直接导航到根目录，使用 replace 替换当前页面，防止回退到受保护的页面
        navigate('/', { replace: true });
    };



    return (
         <div className="h-screen w-full bg-tcm-cream text-tcm-charcoal overflow-hidden selection:bg-tcm-lightGreen selection:text-white relative">
          {/* Toast Notification */}
          {toast && (
            <div className="fixed top-6 left-1/2 transform -translate-x-1/2 z-[100] animate-in fade-in slide-in-from-top-4 duration-300">
              <div className={`px-6 py-3 rounded-full shadow-2xl flex items-center gap-3 border ${
                toast.type === 'success' 
                  ? 'bg-tcm-darkGreen text-white border-tcm-lightGreen/20' 
                  : 'bg-red-600 text-white border-red-400'
              }`}>
                {toast.type === 'success' ? <Icons.Check size={18} className="text-tcm-gold" /> : <Icons.X size={18} />}
                <span className="text-sm font-bold tracking-wide">{toast.message}</span>
              </div>
            </div>
          )}
            <Routes>
                <Route path="/" element={<LandingPage/>}/>

                {/* Login routes */}
                <Route path="/login/public" element={<PublicLoginPage onLogin={handleLogin}/>}/>
                <Route path="/login/professional" element={<ProfessionalLoginPage onLogin={handleLogin}/>}/>

                {/* Register routes */}
                <Route path="/register/public"
                       element={<PublicRegisterPage onRegisterSuccess={handleRegisterSuccess}/>}/>
                <Route path="/register/professional"
                       element={<ProfessionalRegisterPage onRegisterSuccess={handleRegisterSuccess}/>}/>

                {/* Admin routes */}
                <Route path="/login/admin" element={<AdminLoginPage onLogin={handleLogin} />} />
                <Route path="/register/admin" element={<AdminRegisterPage onRegister={handleRegisterSuccess} />} />
                <Route
                    path="/admin"
                    element={user?.role === UserRole.ADMIN ? <AdminPortal user={user} onLogout={handleLogout} /> :
                        <Navigate to="/" replace={true} />}
                />

                {/* Redirect old login route */}
                <Route path="/login" element={<Navigate to="/login/public"/>}/>

                <Route
                    path="/public"
                    element={user ? <PublicPortal user={user} onLogout={handleLogout} /> :
                        <Navigate to="/" replace={true} />}
                />
                <Route
                    path="/professional"
                    element={user ? <ProfessionalPortal user={user} onLogout={handleLogout} /> :
                        <Navigate to="/" replace={true} />}
                />
            </Routes>
        </div>
    );
};

export default AppContent;
