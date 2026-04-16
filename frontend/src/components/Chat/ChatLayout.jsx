import React, { useState, useEffect, useRef, useCallback } from 'react';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import Dashboard from '../Dashboard/Dashboard';
import ToxicityAlert from './ToxicityAlert';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = API_URL.replace('http', 'ws');

export default function ChatLayout({ user, onLogout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [contacts, setContacts] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [showDashboard, setShowDashboard] = useState(false);
  const [alert, setAlert] = useState(null);
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

      <div className="h-screen w-full flex p-6 max-w-7xl mx-auto pt-20 pb-10">
        <Sidebar 
          user={user} 
          contacts={contacts} 
          activeChat={activeChat} 
          setActiveChat={(c) => { setActiveChat(c); setShowDashboard(false); }} 
          onLogout={onLogout} 
        />
        
        {showDashboard ? (
          <Dashboard stats={dashboardStats} />
        ) : (
          <ChatWindow 
            user={user}
            activeChat={activeChat}
            messages={chatMessages}
            input={input}
            setInput={setInput}
            sendMessage={sendMessage}
            receiverWarning={receiverWarning}
          />
        )}
      </div>
    </>
  );
}
