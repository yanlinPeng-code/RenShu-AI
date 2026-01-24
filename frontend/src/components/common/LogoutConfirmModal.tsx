import React from 'react';
import { Icons } from './Icons';

interface LogoutConfirmModalProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  variant?: 'public' | 'professional' | 'admin';
}

export const LogoutConfirmModal: React.FC<LogoutConfirmModalProps> = ({ 
  isOpen, 
  onConfirm, 
  onCancel, 
  variant = 'public' 
}) => {
  if (!isOpen) return null;

  // 根据不同变体定义视觉样式
  const themes = {
    public: {
      overlay: 'bg-black/20 backdrop-blur-[2px]',
      container: 'bg-[#fcfbf7] rounded-[32px] border border-white shadow-2xl',
      title: 'text-tcm-darkGreen font-serif-sc',
      description: 'text-gray-500 font-sans',
      iconBg: 'bg-orange-50 text-orange-500',
      cancelBtn: 'bg-gray-100 text-gray-500 hover:bg-gray-200',
      confirmBtn: 'bg-[#ff4d4f] text-white hover:bg-[#ff7875] shadow-[0_4px_15px_rgba(255,77,79,0.3)]',
      decoration: 'bg-tcm-lightGreen/20'
    },
    professional: {
      overlay: 'bg-slate-900/40 backdrop-blur-sm',
      container: 'bg-white rounded-2xl border border-slate-100 shadow-2xl',
      title: 'text-tcm-darkGreen font-serif-sc',
      description: 'text-slate-500 font-sans',
      iconBg: 'bg-tcm-gold/10 text-tcm-gold',
      cancelBtn: 'bg-slate-50 text-slate-400 border border-slate-100 hover:bg-slate-100',
      confirmBtn: 'bg-tcm-darkGreen text-white hover:bg-tcm-lightGreen shadow-lg',
      decoration: 'bg-tcm-gold/30'
    },
    admin: {
      overlay: 'bg-black/70 backdrop-blur-md',
      container: 'bg-slate-900 rounded-2xl border border-slate-700 shadow-[0_0_50px_rgba(0,0,0,0.5)]',
      title: 'text-white font-sans uppercase tracking-widest',
      description: 'text-slate-400 font-sans',
      iconBg: 'bg-red-500/10 text-red-500',
      cancelBtn: 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700',
      confirmBtn: 'bg-red-600 text-white hover:bg-red-500 shadow-[0_0_20px_rgba(220,38,38,0.2)]',
      decoration: 'bg-red-600/50'
    }
  }[variant];

  return (
    <div className="fixed inset-0 z-[999] flex items-center justify-center p-4 animate-in fade-in duration-300">
      {/* 蒙层 */}
      <div 
        className={`absolute inset-0 ${themes.overlay}`} 
        onClick={onCancel}
      ></div>

      {/* 弹窗主体 */}
      <div className={`relative w-full max-w-[420px] overflow-hidden animate-in zoom-in-95 duration-200 ${themes.container}`}>
        <div className="p-8 md:p-10">
          <div className="flex items-start gap-5">
            {/* 图标 */}
            <div className={`p-4 rounded-full shrink-0 ${themes.iconBg}`}>
              <Icons.Zap size={32} strokeWidth={2.5} />
            </div>
            
            {/* 文字内容 */}
            <div className="space-y-3">
              <h3 className={`text-2xl font-bold leading-tight ${themes.title}`}>
                确认退出登录？
              </h3>
              <p className={`text-sm leading-relaxed ${themes.description}`}>
                退出登录不会丢失任何数据，你仍可以登录此账号。
              </p>
            </div>
          </div>

          {/* 按钮区域 */}
          <div className="mt-10 flex items-center justify-end gap-3">
            <button 
              onClick={onCancel}
              className={`px-8 py-3 text-sm font-bold rounded-xl transition-all active:scale-95 ${themes.cancelBtn}`}
            >
              取消
            </button>
            <button 
              onClick={onConfirm}
              className={`px-8 py-3 text-sm font-bold rounded-xl transition-all active:scale-95 ${themes.confirmBtn}`}
            >
              退出登录
            </button>
          </div>
        </div>
        
        {/* 顶部或底部的视觉点缀 */}
        <div className={`h-1.5 w-full opacity-50 ${themes.decoration}`}></div>
      </div>
    </div>
  );
};