import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserRole } from '../types';

interface ProtectedRouteProps {
    children: React.ReactNode;
    allowedRoles?: UserRole[];  // 允许访问的角色列表
    redirectTo?: string;        // 未授权时跳转的路径
}

// 加载状态组件
// const LoadingScreen: React.FC = () => (
//     <div className="h-screen w-full bg-tcm-cream flex items-center justify-center">
//         <div className="flex flex-col items-center gap-4">
//             <div className="w-8 h-8 border-4 border-tcm-lightGreen border-t-transparent rounded-full animate-spin"></div>
//             <span className="text-tcm-charcoal text-sm">验证登录状态...</span>
//         </div>
//     </div>
// );

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    children,
    allowedRoles,
    redirectTo = '/'
}) => {
    const { user, isAuthLoading } = useAuth();

    // 认证加载中（正常情况下不会触发，因为使用了同步初始化）
    if (isAuthLoading) {
        return null;
    }

    // 未登录，跳转到指定页面
    if (!user) {
        return <Navigate to={redirectTo} replace />;
    }

    // 如果指定了允许的角色，检查用户角色是否匹配
    if (allowedRoles && !allowedRoles.includes(user.role)) {
        return <Navigate to={redirectTo} replace />;
    }

    // 验证通过，渲染子组件
    return <>{children}</>;
};

export default ProtectedRoute;
