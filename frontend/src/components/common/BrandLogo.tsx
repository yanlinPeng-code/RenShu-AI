import React from 'react';

interface BrandLogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  variant?: 'light' | 'dark' | 'auto';
  animate?: boolean;
}

export const BrandLogo: React.FC<BrandLogoProps> = ({ 
  className = "", 
  size = 'md', 
  showText = true,
  variant = 'auto',
  animate = false
}) => {
  const sizeClasses = {
    sm: "h-6",
    md: "h-8",
    lg: "h-12",
    xl: "h-20"
  };

  const textClasses = {
    sm: "text-lg",
    md: "text-xl",
    lg: "text-3xl",
    xl: "text-5xl"
  };

  const textColorClass = {
    light: "text-tcm-darkGreen",
    dark: "text-tcm-cream",
    auto: "text-tcm-darkGreen dark:text-tcm-cream"
  }[variant];

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className={`relative ${sizeClasses[size]} aspect-square flex items-center justify-center`}>
        <svg 
          viewBox="0 0 100 100" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
          className={`w-full h-full drop-shadow-sm ${animate ? 'animate-float' : ''}`}
        >
          <defs>
            <linearGradient id="leafGradient" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#1a3c34" />
              <stop offset="100%" stopColor="#4d8c7c" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="2" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>
          
          {/* Stylized Ginkgo Leaf - Organic Side */}
          <path 
            d="M50 85 C 50 85, 45 60, 25 50 C 10 40, 15 20, 35 15 C 45 12, 55 12, 65 15 C 85 20, 90 40, 75 50 C 55 60, 50 85, 50 85 Z" 
            fill="url(#leafGradient)" 
            className="opacity-90"
          />
          
          {/* Tech/AI Overlay - Circuit Lines */}
          <path 
            d="M50 85 C 50 85, 52 70, 60 60 M 60 60 L 75 50 M 60 60 L 65 35" 
            stroke="#d4af37" 
            strokeWidth="2" 
            strokeLinecap="round"
            className={animate ? "animate-pulse" : ""}
          />
          
          {/* Connection Nodes */}
          <circle cx="60" cy="60" r="3" fill="#fff" stroke="#d4af37" strokeWidth="1" />
          <circle cx="75" cy="50" r="2" fill="#fff" stroke="#d4af37" strokeWidth="1" />
          <circle cx="65" cy="35" r="2" fill="#fff" stroke="#d4af37" strokeWidth="1" />
        </svg>
      </div>

      {showText && (
        <div className="flex flex-col leading-none">
          <span className={`font-serif-sc font-bold tracking-wide ${textColorClass} ${textClasses[size]}`}>
            仁术 <span className="font-sans font-light opacity-60 text-[0.6em] tracking-widest ml-1">AI</span>
          </span>
        </div>
      )}
    </div>
  );
};