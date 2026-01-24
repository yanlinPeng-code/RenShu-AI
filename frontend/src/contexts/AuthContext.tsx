import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { User, UserRole } from '../types';
import { authApi } from '../api';
import { adminAuthApi } from '../api/modules/auth';

// 认证上下文类型
interface AuthContextType {
    user: User | null;
    isAuthLoading: boolean;
    login: (role: UserRole, authData?: any) => Promise<void>;
    logout: () => Promise<void>;
}

// 创建上下文
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 根据路由判断当前角色
const getRoleFromPath = (pathname: string): UserRole | null => {
    if (pathname.startsWith('/admin') || pathname.startsWith('/login/admin') || pathname.startsWith('/register/admin')) {
        return UserRole.ADMIN;
    }
    if (pathname.startsWith('/public') || pathname.startsWith('/login/public') || pathname.startsWith('/register/public')) {
        return UserRole.PUBLIC;
    }
    if (pathname.startsWith('/professional') || pathname.startsWith('/login/professional') || pathname.startsWith('/register/professional')) {
        return UserRole.PROFESSIONAL;
    }
    return null;
};

// 根据角色获取 localStorage key 前缀
const getStoragePrefix = (role: UserRole): string => {
    if (role === UserRole.ADMIN) return 'admin_';
    if (role === UserRole.PROFESSIONAL) return 'professional_';
    return 'user_';
};

// 从 localStorage 同步读取初始用户状态（根据当前路由）
const getInitialUser = (pathname: string): User | null => {
    try {
        const role = getRoleFromPath(pathname);
        if (!role) return null;

        const prefix = getStoragePrefix(role);
        const token = localStorage.getItem(`${prefix}access_token`);
        const savedUser = localStorage.getItem(`${prefix}user`);

        if (token && savedUser) {
            return JSON.parse(savedUser);
        }
    } catch {
        // 解析失败，返回 null
    }
    return null;
};

// Provider 组件
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const location = useLocation();
    const navigate = useNavigate();

    // 乐观渲染：立即从 localStorage 同步初始化用户状态
    const [user, setUser] = useState<User | null>(() => getInitialUser(location.pathname));
    const [isAuthLoading, setIsAuthLoading] = useState(false);

    // 当路由变化时，更新用户状态
    useEffect(() => {
        const newUser = getInitialUser(location.pathname);
        setUser(newUser);
    }, [location.pathname]);

    // 后台静默验证 Token（不阻塞页面渲染）
    useEffect(() => {
        const verifyTokenSilently = async () => {
            const role = getRoleFromPath(location.pathname);
            if (!role) return;

            const prefix = getStoragePrefix(role);
            const token = localStorage.getItem(`${prefix}access_token`);
            const savedUser = localStorage.getItem(`${prefix}user`);

            if (token && savedUser) {
                try {
                    const userObj = JSON.parse(savedUser);

                    // 根据用户角色调用对应的API验证token
                    if (userObj.role === UserRole.ADMIN) {
                        await adminAuthApi.me();
                    } else {
                        await authApi.getMe();
                    }
                    // Token 有效，无需操作
                } catch (error: any) {
                    // 只有在明确的 401 错误时才清除认证数据
                    if (error?.response?.status === 401) {
                        console.log('Token已过期或无效，清除登录状态');
                        clearAuthData(role);
                        navigate(role === UserRole.ADMIN ? '/login/admin' : '/', { replace: true });
                    } else {
                        // 网络错误或其他错误，保持登录状态
                        console.log('Token验证请求失败，但保持登录状态', error);
                    }
                }
            }
        };

        // 只有当用户状态存在时才进行后台验证
        if (user) {
            verifyTokenSilently();
        }
    }, [location.pathname, user, navigate]);

    // 清除认证数据（只清除指定角色的数据）
    const clearAuthData = (role: UserRole) => {
        const prefix = getStoragePrefix(role);
        localStorage.removeItem(`${prefix}access_token`);
        localStorage.removeItem(`${prefix}refresh_token`);
        localStorage.removeItem(`${prefix}user_id`);
        localStorage.removeItem(`${prefix}user`);

        // 只有当前用户是该角色时才清除状态
        if (user?.role === role) {
            setUser(null);
        }
    };

    // 登录处理
    const login = useCallback(async (role: UserRole, authData?: any) => {
        try {
            // 根据角色获取用户详细信息
            let userData: any;
            if (role === UserRole.ADMIN) {
                const response = await adminAuthApi.me();
                userData = response.data;
            } else {
                const response = await authApi.getMe();
                userData = response.data;
            }

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
                    chiefComplaint: '发热，头疼',
                    medicalHistory: '无记录',
                    suspectedDiagnosis: '待分析...',
                    contraindications: '无禁忌',
                    recommendedTreatment: '一般 wellness 建议'
                } : undefined,
                specialty: role === UserRole.PROFESSIONAL ? 'Integrative Medicine' : undefined
            };

            setUser(loggedInUser);

            // 使用角色前缀存储用户信息
            const prefix = getStoragePrefix(role);
            localStorage.setItem(`${prefix}user`, JSON.stringify(loggedInUser));

            // 导航到相应页面
            const routeMap: Record<UserRole, string> = {
                [UserRole.PUBLIC]: '/public',
                [UserRole.PROFESSIONAL]: '/professional',
                [UserRole.ADMIN]: '/admin'
            };
            navigate(routeMap[role]);

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

            const prefix = getStoragePrefix(role);
            localStorage.setItem(`${prefix}user`, JSON.stringify(basicUser));

            const routeMap: Record<UserRole, string> = {
                [UserRole.PUBLIC]: '/public',
                [UserRole.PROFESSIONAL]: '/professional',
                [UserRole.ADMIN]: '/admin'
            };
            navigate(routeMap[role]);
        }
    }, [navigate]);

    // 登出处理
    const logout = useCallback(async () => {
        const isAdmin = user?.role === UserRole.ADMIN;

        try {
            if (isAdmin) {
                await adminAuthApi.logout();
            } else {
                await authApi.logout();
            }

        } catch {
            console.log('登出时出现问题，但仍已退出登录。');
        }

        if (user) {
            clearAuthData(user.role);
        }
        navigate(isAdmin ? '/login/admin' : '/', { replace: true });
    }, [user, navigate]);

    return (
        <AuthContext.Provider value={{ user, isAuthLoading,  login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

// 自定义 Hook
export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export default AuthContext;
