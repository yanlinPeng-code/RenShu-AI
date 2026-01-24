import React, { useEffect } from 'react';
import { Icons } from './Icons';

export interface ToastProps {
  message: string;
  type: 'success' | 'error';
  onClose: () => void;
  variant?: 'tcm' | 'admin';
}

export const Toast: React.FC<ToastProps> = ({ message, type, onClose, variant = 'tcm' }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const styles = {
    tcm: {
      success: 'bg-tcm-darkGreen/90 text-white border-tcm-lightGreen/30',
      error: 'bg-red-600/90 text-white border-red-400/30',
      icon: 'bg-tcm-lightGreen/20 text-tcm-gold'
    },
    admin: {
      success: 'bg-blue-600/90 text-white border-blue-400/30',
      error: 'bg-red-600/90 text-white border-red-400/30',
      icon: 'bg-white/10 text-white'
    }
  }[variant];

  return (
    <div className="fixed top-8 left-1/2 transform -translate-x-1/2 z-[100] animate-in fade-in slide-in-from-top-4 duration-500">
      <div className={`px-8 py-3.5 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.2)] flex items-center gap-4 border backdrop-blur-md ${type === 'success' ? styles.success : styles.error}`}>
        <div className={`p-1.5 rounded-full ${styles.icon}`}>
          {type === 'success' ? <Icons.Check size={20} /> : <Icons.X size={20} />}
        </div>
        <span className="text-sm font-bold tracking-widest font-serif-sc">{message}</span>
      </div>
    </div>
  );
};