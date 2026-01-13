import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icons } from '../../components/common/Icons';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [hoveredSide, setHoveredSide] = useState<'left' | 'right' | null>(null);

  const handleEnter = (role: 'public' | 'professional') => {
    // Navigate to separate login pages based on role
    if (role === 'public') {
      navigate('/login/public');
    } else {
      navigate('/login/professional');
    }
  };

  return (
    <div className="relative w-full h-full flex flex-col md:flex-row overflow-hidden font-serif-sc">
      
      {/* Central Branding Overlay - Absolute Center */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-20 pointer-events-none text-center">
        <div className="bg-white/10 backdrop-blur-md border border-white/20 p-8 rounded-full shadow-2xl animate-fade-in-up">
           <div className="text-5xl md:text-7xl font-bold text-tcm-gold drop-shadow-lg tracking-widest mb-2">
            仁术
           </div>
           <div className="text-xl md:text-2xl text-white font-light tracking-[0.5em]">
             RENSHU AI
           </div>
        </div>
      </div>

      {/* Left Side: Public */}
      <div 
        className={`relative flex-1 h-1/2 md:h-full transition-all duration-700 ease-in-out cursor-pointer group
          ${hoveredSide === 'right' ? 'flex-[0.8] brightness-50' : 'flex-1'}
          ${hoveredSide === 'left' ? 'flex-[1.5]' : ''}
          bg-tcm-cream border-b md:border-b-0 md:border-r border-tcm-gold/30
        `}
        onMouseEnter={() => setHoveredSide('left')}
        onMouseLeave={() => setHoveredSide(null)}
        onClick={() => handleEnter('public')}
      >
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1514782831304-632d84503f6f?q=80&w=2535&auto=format&fit=crop')] bg-cover bg-center opacity-10 mix-blend-multiply transition-transform duration-1000 group-hover:scale-110"></div>
        <div className="absolute inset-0 flex flex-col justify-center items-center p-12 text-tcm-darkGreen z-10">
          <Icons.Leaf className="w-16 h-16 mb-6 text-tcm-lightGreen group-hover:scale-110 transition-transform" />
          <h2 className="text-3xl md:text-5xl font-bold mb-4 tracking-wide">公众健康</h2>
          <p className="text-lg md:text-xl opacity-80 mb-8 max-w-md text-center">
            个性化整体护理。<br/> 古老智慧与现代AI相结合。
          </p>
          <button className="px-8 py-3 border-2 border-tcm-darkGreen text-tcm-darkGreen rounded-full hover:bg-tcm-darkGreen hover:text-white transition-all font-sans font-semibold">
            进入公众门户
          </button>
        </div>
      </div>

      {/* Right Side: Professional */}
      <div 
        className={`relative flex-1 h-1/2 md:h-full transition-all duration-700 ease-in-out cursor-pointer group
          ${hoveredSide === 'left' ? 'flex-[0.8] brightness-50' : 'flex-1'}
          ${hoveredSide === 'right' ? 'flex-[1.5]' : ''}
          bg-tcm-darkGreen text-tcm-cream
        `}
        onMouseEnter={() => setHoveredSide('right')}
        onMouseLeave={() => setHoveredSide(null)}
        onClick={() => handleEnter('professional')}
      >
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?q=80&w=2670&auto=format&fit=crop')] bg-cover bg-center opacity-20 mix-blend-overlay transition-transform duration-1000 group-hover:scale-110"></div>
        <div className="absolute inset-0 flex flex-col justify-center items-center p-12 z-10">
          <Icons.Stethoscope className="w-16 h-16 mb-6 text-tcm-gold group-hover:scale-110 transition-transform" />
          <h2 className="text-3xl md:text-5xl font-bold mb-4 tracking-wide">专业人员</h2>
          <p className="text-lg md:text-xl opacity-80 mb-8 max-w-md text-center">
            临床决策支持。<br/> 高级诊断与分析。
          </p>
          <button className="px-8 py-3 border-2 border-tcm-gold text-tcm-gold rounded-full hover:bg-tcm-gold hover:text-tcm-darkGreen transition-all font-sans font-semibold">
            进入工作区
          </button>
        </div>
      </div>

    </div>
  );
};

export default LandingPage;