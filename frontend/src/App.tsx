import React from 'react';
import { HashRouter } from 'react-router-dom';
import AppRoutes from './router';

const App: React.FC = () => {
  return (
    <HashRouter>
      <AppRoutes />
    </HashRouter>
  );
};

export default App;