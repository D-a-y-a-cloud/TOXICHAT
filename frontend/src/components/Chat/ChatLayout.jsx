import React, { useState, useEffect, useRef, useCallback } from 'react';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import Dashboard from '../Dashboard/Dashboard';
import ToxicityAlert from './ToxicityAlert';
import MutedModal from './MutedModal';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = API_URL.replace(/^http/, 'ws');

export default function ChatLayout({ user, onLogout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [contacts, setContacts] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [showDashboard, setShowDashboard] = useState(false);
  const [alert, setAlert] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [receiverWarning, setReceiverWarning] = useState(null);
  const [showMutedModal, setShowMutedModal] = useState(false);
  const [warningCount, setWarningCount] = useState(0);
  
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
    let ws = null;
    let reconnectTimer = null;

    const connectWS = () => {
      ws = new WebSocket(`${WS_URL}/ws/${user.access_token}`);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'users_list') {
          setContacts(data.users.filter(u => u.username !== user.username));
        } else if (data.type === 'message') {
          if (data.sender !== user.username) {
            ws.send(JSON.stringify({ type: 'message_delivered', message_id: data.id, sender: data.sender }));
          }
          setMessages(prev => [...prev, data]);
        } else if (data.type === 'user_presence') {
          setContacts(prev => prev.map(c => 
            c.username === data.username ? { ...c, is_online: data.is_online } : c
          ));
        } else if (data.type === 'message_status_update') {
          setMessages(prev => prev.map(m => 
            m.id === data.message_id ? { ...m, status: data.status } : m
          ));
        } else if (data.type === 'toxicity_alert') {
          setAlert(data);
          setWarningCount(prev => {
            const next = prev + 1;
            if (next === 3 || data.message.includes('RESTRICTED')) {
              setShowMutedModal(true);
            }
            return next;
          });
        } else if (data.type === 'toxicity_warning') {
          setReceiverWarning(data);
          setTimeout(() => setReceiverWarning(null), 5000);
        } else if (data.type === 'system') {
          ws.send(JSON.stringify({ type: 'get_users' }));
        }
      };

      ws.onclose = () => {
        reconnectTimer = setTimeout(connectWS, 2000);
      };
    };

    connectWS();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) {
        ws.onclose = null;
        ws.close();
      }
    };
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
      <MutedModal isOpen={showMutedModal} onClose={() => setShowMutedModal(false)} />
      
      {/* Top Floating Dashboard Toggle */}
      <div className="absolute top-4 right-4 md:top-6 md:right-8 z-50 flex gap-4">
        <button 
          onClick={() => setShowDashboard(!showDashboard)}
          className={`px-3 py-1.5 md:px-4 md:py-2 rounded-xl text-xs md:text-sm font-medium border backdrop-blur-md transition-all shadow-lg ${
            showDashboard 
              ? 'bg-emerald-500 text-white border-emerald-400 shadow-emerald-500/20' 
              : 'bg-white/5 border-white/10 text-gray-300 hover:bg-white/10 hover:text-white'
          }`}
        >
          {showDashboard ? 'Close Analytics' : '📊 View Analytics'}
        </button>
      </div>

      <div className="h-[100dvh] w-full flex md:p-6 p-0 max-w-7xl mx-auto md:pt-20 pt-16 md:pb-10 pb-0 overflow-hidden bg-space-bg">
        
        {/* Sidebar wrapper */}
        <div className={`w-full md:w-80 h-full flex-shrink-0 ${activeChat || showDashboard ? 'hidden md:flex' : 'flex'}`}>
          <Sidebar 
            user={user} 
            contacts={contacts} 
            activeChat={activeChat} 
            setActiveChat={(c) => { setActiveChat(c); setShowDashboard(false); }} 
            onLogout={onLogout} 
          />
        </div>
        
        {/* Main Content wrapper */}
        <div className={`w-full h-full flex-1 md:flex md:pl-4 transition-all duration-300 ease-in-out ${!activeChat && !showDashboard ? 'hidden md:flex opacity-0 md:opacity-100 pointer-events-none md:pointer-events-auto text-center' : 'flex opacity-100'}`}>
          {showDashboard ? (
            <div className="w-full h-full bg-space-bg md:bg-transparent overflow-y-auto">
              <Dashboard stats={dashboardStats} />
            </div>
          ) : activeChat ? (
            <ChatWindow 
              user={user}
              activeChat={activeChat}
              messages={chatMessages}
              input={input}
              setInput={setInput}
              sendMessage={sendMessage}
              receiverWarning={receiverWarning}
              onBack={() => setActiveChat(null)}
              ws={wsRef.current}
            />
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center relative z-10 glass-panel md:rounded-r-3xl border-l-0 bg-wa-bg w-full">
              <div className="text-center max-w-sm">
                <div className="w-24 h-24 mx-auto bg-emerald-500/10 rounded-full flex items-center justify-center mb-6 shadow-[0_0_50px_rgba(16,185,129,0.2)]">
                  <span className="text-5xl">🛡️</span>
                </div>
                <h2 className="text-2xl font-bold mb-2">ToxiChat Web</h2>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Select a contact from the sidebar to start a secure, ML-monitored conversation.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
