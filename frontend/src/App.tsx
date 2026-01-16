import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import AppContent from './router';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
};

export default App;