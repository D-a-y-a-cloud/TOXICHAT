import React, { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Mic, Phone, Video, ArrowLeft } from 'lucide-react';
import MessageBubble from './MessageBubble';

export default function ChatWindow({ user, activeChat, messages, input, setInput, sendMessage, receiverWarning, onBack, ws }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  useEffect(scrollToBottom, [messages]);

  const [isDictating, setIsDictating] = useState(false);
  const [callStatus, setCallStatus] = useState(null);

  // Send message_read when viewing an unread message from the active contact
  useEffect(() => {
    if (!ws) return;
    const unread = messages.filter(m => m.receiver === user.username && m.status !== 'read');
    if (unread.length > 0) {
      unread.forEach(m => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'message_read', message_id: m.id, sender: m.sender }));
        }
      });
    }
  }, [messages, ws, user.username]);

  const handleDictation = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support Speech Recognition.");
      return;
    }
    
    if (isDictating) return;
    
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsDictating(true);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(prev => prev + (prev ? ' ' : '') + transcript);
    };
    recognition.onerror = (event) => {
      console.error("Speech recognition error", event.error);
      setIsDictating(false);
    };
    recognition.onend = () => setIsDictating(false);

    recognition.start();
  };

  const handleCall = (type) => {
    setCallStatus(`Initiating ${type} call...`);
    setTimeout(() => {
      setCallStatus(null);
      alert(`${type} call ended (Mockup Demo).`);
    }, 4000);
  };

  if (!activeChat) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center relative z-10 glass-panel ml-4 rounded-r-3xl border-l-0">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center max-w-sm"
        >
          <div className="w-24 h-24 mx-auto bg-emerald-500/10 rounded-full flex items-center justify-center mb-6 shadow-[0_0_50px_rgba(16,185,129,0.2)]">
            <span className="text-5xl">🛡️</span>
          </div>
          <h2 className="text-2xl font-bold mb-2">ToxiChat Protected</h2>
          <p className="text-gray-400 text-sm leading-relaxed">
            Select a contact from the sidebar to start a secure, ML-monitored conversation.
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col relative z-10 bg-wa-bg md:rounded-r-3xl overflow-hidden shadow-2xl w-full h-full">
      
      {/* Header */}
      <div className="p-3 md:p-4 border-b border-wa-panel bg-wa-panel flex items-center gap-2 md:gap-4 relative z-20">
        
        {/* Mobile Back Button */}
        <button onClick={onBack} className="md:hidden p-1.5 -ml-1 text-gray-300 hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>

        <div className="w-10 h-10 flex-shrink-0 rounded-xl bg-gray-600 text-gray-200 flex items-center justify-center font-bold">
          {activeChat.display_name?.[0]?.toUpperCase() || '?'}
        </div>
        <div className="flex-1">
          <h2 className="text-white font-semibold flex items-center gap-2">
            {activeChat.display_name}
            {activeChat.is_online && <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-emerald-500/20 text-emerald-400">Online</span>}
          </h2>
          <p className="text-xs text-gray-400">Secure AES-256 / DL Monitored</p>
        </div>
        
        {/* Call options */}
        <div className="flex gap-2 relative z-20">
          <button onClick={() => handleCall('Audio')} className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white transition-colors" title="Voice Call">
            <Phone className="w-5 h-5" />
          </button>
          <button onClick={() => handleCall('Video')} className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white transition-colors" title="Video Call">
            <Video className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Receiver Warning Banner */}
      {receiverWarning && (
        <motion.div 
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="bg-red-500/10 border-b border-red-500/20 py-2 px-6 flex items-center gap-3 relative z-20"
        >
          <span className="text-red-500 animate-pulse">⚠️</span>
          <span className="text-red-200 text-sm">
            {receiverWarning.message} (from {receiverWarning.from}, score: {(receiverWarning.score * 100).toFixed(0)}%)
          </span>
        </motion.div>
      )}

      {/* Call Status Banner */}
      {callStatus && (
        <motion.div 
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="bg-blue-500/10 border-b border-blue-500/20 py-2 px-6 flex items-center justify-center gap-3 relative z-20"
        >
          <span className="text-blue-400 animate-pulse">📞</span>
          <span className="text-blue-200 text-sm font-semibold">{callStatus}</span>
        </motion.div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 md:space-y-6 flex flex-col relative z-10">
        {messages.map((m, i) => (
          <MessageBubble key={m.id || i} message={m} isOwn={m.sender === user.username} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-3 md:p-4 border-t border-wa-panel bg-wa-bg relative z-20">
        <form onSubmit={sendMessage} className="flex gap-2">
          
          <motion.button 
            type="button"
            onClick={handleDictation}
            whileTap={{ scale: 0.95 }}
            title="Voice to Text"
            className={`h-12 px-4 flex-shrink-0 rounded-xl flex items-center justify-center gap-2 transition-all font-semibold ${
              isDictating 
                ? 'bg-red-500 text-white animate-pulse shadow-lg shadow-red-500/30' 
                : 'bg-indigo-500/20 hover:bg-indigo-500/40 border border-indigo-500/30 text-indigo-300 hover:text-white'
            }`}
          >
            <Mic className="w-5 h-5" />
            <span className="text-sm">{isDictating ? 'Listening...' : 'Voice Message'}</span>
          </motion.button>

          <input 
            value={input} 
            onChange={e => setInput(e.target.value)}
            placeholder="Type or dictate a message..." 
            autoFocus 
            className="flex-1 bg-wa-panel border border-transparent rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500/50 transition-all font-medium"
          />
          <motion.button 
            whileTap={{ scale: 0.95 }}
            type="submit" 
            disabled={!input.trim()}
            className="bg-emerald-500 hover:bg-emerald-400 text-white w-12 h-12 rounded-xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg shadow-emerald-500/20"
          >
            <Send className="w-5 h-5 -ml-1 mt-1" />
          </motion.button>
        </form>
      </div>
    </div>
  );
}
