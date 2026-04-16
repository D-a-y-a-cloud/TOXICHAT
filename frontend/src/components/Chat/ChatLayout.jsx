import React, { useState, useEffect, useRef, useCallback } from 'react';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import Dashboard from '../Dashboard/Dashboard';
import ToxicityAlert from './ToxicityAlert';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
const WS_URL = API_URL.replace('http', 'ws');

export default function ChatLayout({ user, onLogout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [contacts, setContacts] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [showDashboard, setShowDashboard] = useState(false);
  const [alert, setAlert] = useState(null);
  const [cooldownAlert, setCooldownAlert] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [receiverWarning, setReceiverWarning] = useState(null);
  
  const wsRef = useRef(null);

  // ── Dashboard Data Fetch ──────────────────────────────────
  useEffect(() => {
    if (!showDashboard) return;
    fetch(`${API_URL}/api/dashboard/stats`)
      .then(r => r.json())
      .then(setDashboardStats)
      .catch(console.error);
  }, [showDashboard, messages]); // Refresh stats if messages change

  // ── WebSocket Connection ──────────────────────────────────
  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}/ws/${user.access_token}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'users_list') {
        setContacts(data.users.filter(u => u.username !== user.username));
      } else if (data.type === 'message') {
        setMessages(prev => [...prev, data]);
      } else if (data.type === 'toxicity_alert') {
        setAlert(data);
      } else if (data.type === 'toxicity_warning') {
        setReceiverWarning(data);
        setTimeout(() => setReceiverWarning(null), 5000);
      } else if (data.type === 'cooldown_suggestion') {
        setCooldownAlert(data.message);
      } else if (data.type === 'system') {
        ws.send(JSON.stringify({ type: 'get_users' }));
      }
    };

    return () => ws.close();
  }, [user]);

  // ── Load Message History ──────────────────────────────────
  useEffect(() => {
    if (!activeChat) return;
    fetch(`${API_URL}/api/messages/${user.username}/${activeChat.username}`)
      .then(r => r.json())
      .then(data => setMessages(Array.isArray(data) ? data : []))
      .catch(() => setMessages([]));
  }, [activeChat, user.username]);

  // ── Send Message ──────────────────────────────────────────
  const sendMessage = useCallback((e) => {
    e.preventDefault();
    if (!input.trim() || !activeChat || !wsRef.current) return;
    wsRef.current.send(JSON.stringify({
      type: 'message',
      text: input.trim(),
      receiver: activeChat.username,
      is_group: false,
    }));
    setInput('');
  }, [input, activeChat]);

  // Filter messages
  const chatMessages = messages.filter(m =>
    (m.sender === user.username && m.receiver === activeChat?.username) ||
    (m.sender === activeChat?.username && m.receiver === user.username)
  );

  return (
    <>
      <ToxicityAlert alert={alert} onClose={() => setAlert(null)} />
      
      {/* Cooldown Popup Modal */}
      {cooldownAlert && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="glass-panel p-8 rounded-3xl max-w-md w-full border border-blue-500/30 text-center relative overflow-hidden animate-in fade-in zoom-in duration-300">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-400 to-indigo-500"></div>
            <div className="w-20 h-20 mx-auto bg-blue-500/10 rounded-full flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(59,130,246,0.3)]">
              <span className="text-4xl">🧘</span>
            </div>
            <h2 className="text-2xl font-bold mb-4 text-white">Time to Breathe</h2>
            <p className="text-gray-300 text-sm leading-relaxed mb-8">
              {cooldownAlert}
            </p>
            <button 
              onClick={() => setCooldownAlert(null)}
              className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold transition-all shadow-lg"
            >
              I Understand
            </button>
          </div>
        </div>
      )}

      {/* Top Floating Dashboard Toggle */}
      <div className="absolute top-6 right-8 z-50 flex gap-4">
        <button 
          onClick={() => setShowDashboard(!showDashboard)}
          className={`px-4 py-2 rounded-xl text-sm font-medium border backdrop-blur-md transition-all shadow-lg ${
            showDashboard 
              ? 'bg-emerald-500 text-white border-emerald-400 shadow-emerald-500/20' 
              : 'bg-white/5 border-white/10 text-gray-300 hover:bg-white/10 hover:text-white'
          }`}
        >
          {showDashboard ? 'Close Dashboard' : '📊 View Analytics'}
        </button>
      </div>

      <div className="relative h-screen w-full flex p-0 md:p-6 max-w-7xl mx-auto md:pt-20 pb-0 md:pb-10 overflow-hidden">
        {/* Sidebar wrapper */}
        <div className={`w-full md:w-1/3 h-full ${activeChat || showDashboard ? 'hidden md:block' : 'block'}`}>
          <Sidebar 
            user={user} 
            contacts={contacts} 
            activeChat={activeChat} 
            setActiveChat={(c) => { setActiveChat(c); setShowDashboard(false); }} 
            onLogout={onLogout} 
          />
        </div>
        
        {/* Main Content wrapper */}
        <div className={`w-full md:flex-1 h-full ${!activeChat && !showDashboard ? 'hidden md:flex' : 'flex'} flex-col`}>
          {showDashboard ? (
            <div className="flex-1 w-full relative">
              <button 
                onClick={() => setShowDashboard(false)}
                className="md:hidden absolute top-4 left-4 z-50 bg-black/50 p-2 rounded-xl text-white"
              >
                ← Back
              </button>
              <Dashboard stats={dashboardStats} />
            </div>
          ) : (
            <ChatWindow 
              user={user}
              activeChat={activeChat}
              setActiveChat={setActiveChat}
              messages={chatMessages}
              input={input}
              setInput={setInput}
              sendMessage={sendMessage}
              receiverWarning={receiverWarning}
            />
          )}
        </div>
      </div>
    </>
  );
}
