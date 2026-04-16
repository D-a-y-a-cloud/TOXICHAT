import React, { useState } from 'react';
import './App.css';
import Background3D from './components/3D/Background3D';
import Login from './components/Auth/Login';
import ChatLayout from './components/Chat/ChatLayout';

function App() {
  const [user, setUser] = useState(() => {
    const saved = sessionStorage.getItem('toxichat_user');
    return saved ? JSON.parse(saved) : null;
  });

  const handleLogin = (userData) => {
    setUser(userData);
    sessionStorage.setItem('toxichat_user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    sessionStorage.removeItem('toxichat_user');
  };

  return (
    <div className="relative min-h-screen text-white font-sans overflow-hidden">
      {/* 3D R3F Background lives at the absolute back, global to entire app */}
      <Background3D />
      
      {/* Foreground UI Layer */}
      <div className="relative z-10 w-full h-full flex flex-col items-center justify-center">
        {user ? (
          <ChatLayout user={user} onLogout={handleLogout} />
        ) : (
          <Login onLogin={handleLogin} />
        )}
      </div>
    </div>
  );
}

export default App;
