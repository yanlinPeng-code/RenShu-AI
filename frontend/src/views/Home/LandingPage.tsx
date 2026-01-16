import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icons } from '../../components/common/Icons';
import { BrandLogo } from '../../components/common/BrandLogo';


const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [hoveredSide, setHoveredSide] = useState<'left' | 'right' | null>(null);

  const handleEnter = (role: 'public' | 'professional') => {
    // Navigate to the specific login page based on role
    navigate(`/login/${role}`);
  };

  return (
    <div className="relative w-full h-full flex flex-col md:flex-row overflow-hidden font-serif-sc bg-rice-paper">
      
      {/* Decorative Background Elements */}
      <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
        {/* Abstract Green Ink Flow */}
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] bg-tcm-lightGreen/10 rounded-full blur-[100px] animate-pulse-slow"></div>
        <div className="absolute top-[40%] -right-[10%] w-[40%] h-[40%] bg-tcm-gold/10 rounded-full blur-[80px] animate-pulse-slow delay-1000"></div>
        
        {/* Floating Particles/Leaves */}
        <div className="absolute top-1/4 left-1/4 animate-float opacity-20"><Icons.Leaf className="text-tcm-lightGreen rotate-45" size={24} /></div>
        <div className="absolute bottom-1/3 right-1/3 animate-float opacity-20" style={{animationDelay: '1s'}}><Icons.Leaf className="text-tcm-darkGreen -rotate-12" size={32} /></div>
        <div className="absolute top-1/2 right-10 animate-float opacity-10" style={{animationDelay: '2s'}}><Icons.BrainCircuit className="text-tcm-gold" size={48} /></div>
      </div>

      {/* Central Branding Overlay - Absolute Center with Glass Effect */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-30 pointer-events-none text-center w-full max-w-md">
        <div className="glass-panel p-12 rounded-full shadow-2xl animate-ink-spread border border-white/40 flex flex-col items-center justify-center relative overflow-hidden group">
           
           {/* Subtle Shine Effect */}
           <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/30 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
           
           <BrandLogo size="xl" animate={true} className="mb-4 scale-125" />
           
           <div className="mt-4 space-y-2">
             <div className="text-sm uppercase tracking-[0.5em] text-tcm-darkGreen font-sans font-medium opacity-70">
               Intelligent Diagnosis
             </div>
             <div className="h-px w-16 bg-tcm-gold mx-auto"></div>
             <div className="font-calligraphy text-2xl text-tcm-darkGreen opacity-80">
               传承 · 创新 · 仁心
             </div>
           </div>
        </div>
      </div>

      {/* Left Side: Public / Patient */}
      <div 
        className={`relative flex-1 h-1/2 md:h-full transition-all duration-700 ease-in-out cursor-pointer group overflow-hidden border-b md:border-b-0 md:border-r border-tcm-lightGreen/20
          ${hoveredSide === 'right' ? 'flex-[0.6] blur-[2px] opacity-80' : 'flex-1'}
          ${hoveredSide === 'left' ? 'flex-[1.4]' : ''}
        `}
        onMouseEnter={() => setHoveredSide('left')}
        onMouseLeave={() => setHoveredSide(null)}
        onClick={() => handleEnter('public')}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-tcm-freshGreen/50 to-white/80 z-0"></div>
        {/* Subtle Background Image */}
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1544367563-12123d8965cd?q=80&w=2670&auto=format&fit=crop')] bg-cover bg-center opacity-10 mix-blend-multiply transition-transform duration-1000 group-hover:scale-105"></div>
        
        <div className="absolute inset-0 flex flex-col justify-center items-center p-12 text-tcm-darkGreen z-10 transition-transform duration-700 group-hover:translate-y-[-10px]">
          <div className="p-4 rounded-full bg-white/50 backdrop-blur-sm mb-6 group-hover:bg-tcm-lightGreen group-hover:text-white transition-colors shadow-lg">
            <Icons.UserCircle2 className="w-12 h-12" />
          </div>
          <h2 className="text-3xl md:text-5xl font-bold mb-2 tracking-wide font-serif-sc">Public Portal</h2>
          <span className="text-sm uppercase tracking-widest text-tcm-lightGreen font-semibold mb-4">面向患者与健康养生</span>
          
          <p className="text-lg opacity-0 group-hover:opacity-100 transform translate-y-4 group-hover:translate-y-0 transition-all duration-500 max-w-xs text-center font-sans text-gray-600">
            体验基于传统智慧的AI驱动整体健康分析。
          </p>
          
          <button className="mt-8 px-8 py-2 border border-tcm-darkGreen text-tcm-darkGreen rounded-full opacity-0 group-hover:opacity-100 transition-all duration-700 hover:bg-tcm-darkGreen hover:text-white flex items-center gap-2">
            Enter <Icons.ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Right Side: Professional / Doctor */}
      <div 
        className={`relative flex-1 h-1/2 md:h-full transition-all duration-700 ease-in-out cursor-pointer group overflow-hidden
          ${hoveredSide === 'left' ? 'flex-[0.6] blur-[2px] opacity-80' : 'flex-1'}
          ${hoveredSide === 'right' ? 'flex-[1.4]' : ''}
          bg-tcm-darkGreen text-tcm-cream
        `}
        onMouseEnter={() => setHoveredSide('right')}
        onMouseLeave={() => setHoveredSide(null)}
        onClick={() => handleEnter('professional')}
      >
        <div className="absolute inset-0 bg-gradient-to-bl from-tcm-darkGreen to-[#0d211c] z-0"></div>
         <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1666214280557-f1b5022eb634?q=80&w=2670&auto=format&fit=crop')] bg-cover bg-center opacity-10 mix-blend-overlay transition-transform duration-1000 group-hover:scale-105"></div>

        <div className="absolute inset-0 flex flex-col justify-center items-center p-12 z-10 transition-transform duration-700 group-hover:translate-y-[-10px]">
          <div className="p-4 rounded-full bg-white/10 backdrop-blur-sm mb-6 group-hover:bg-tcm-gold group-hover:text-tcm-darkGreen transition-colors shadow-lg border border-white/10">
            <Icons.Stethoscope className="w-12 h-12" />
          </div>
          <h2 className="text-3xl md:text-5xl font-bold mb-2 tracking-wide font-serif-sc">Professional</h2>
          <span className="text-sm uppercase tracking-widest text-tcm-gold font-semibold mb-4">面向医生与研究人员</span>
          
          <p className="text-lg opacity-0 group-hover:opacity-100 transform translate-y-4 group-hover:translate-y-0 transition-all duration-500 max-w-xs text-center font-sans text-gray-300">
            
            高级临床决策支持，医学报告分析，和文献综合。
          </p>

          <button className="mt-8 px-8 py-2 border border-tcm-gold text-tcm-gold rounded-full opacity-0 group-hover:opacity-100 transition-all duration-700 hover:bg-tcm-gold hover:text-tcm-darkGreen flex items-center gap-2">
            Access System <Icons.ChevronRight size={16} />
          </button>
        </div>
      </div>

    </div>
  );
};

export default LandingPage;