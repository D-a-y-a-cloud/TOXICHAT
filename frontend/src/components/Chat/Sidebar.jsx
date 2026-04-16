import React from 'react';
import { motion } from 'framer-motion';
import { Users, Search } from 'lucide-react';

export default function Sidebar({ user, contacts, activeChat, setActiveChat, onLogout }) {
  return (
    <div className="w-full h-full border-r border-space-border bg-wa-bg md:rounded-l-3xl flex flex-col overflow-hidden relative z-10">
      
      {/* Header */}
      <div className="p-4 md:p-6 border-b border-white/5 bg-wa-panel relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-500 to-cyan-500"></div>
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-emerald-500/20 to-cyan-500/20 border border-emerald-500/30 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-cyan-400">
              {user.display_name?.[0]?.toUpperCase() || '?'}
            </span>
          </div>
          <div className="flex-1 overflow-hidden">
            <h2 className="text-white font-bold truncate">{user.display_name}</h2>
            <p className="text-xs text-emerald-400 flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,1)]"></span> Online</p>
          </div>
        </div>
      </div>

      {/* Contacts List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {contacts.length === 0 ? (
          <div className="text-center py-10 px-4">
            <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-4">
              <Users className="text-gray-500 w-8 h-8" />
            </div>
            <p className="text-gray-400 text-sm">No other users online right now.</p>
          </div>
        ) : (
          contacts.map((c, i) => {
            const isActive = activeChat?.username === c.username;
            return (
              <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                key={c.username}
                onClick={() => setActiveChat(c)}
                className={`p-3 rounded-xl md:rounded-2xl cursor-pointer flex items-center gap-4 transition-all duration-300 group ${
                  isActive 
                    ? 'bg-wa-panel shadow-lg' 
                    : 'hover:bg-wa-panel/50 border border-transparent'
                }`}
              >
                <div className="relative">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm transition-colors ${
                    isActive ? 'bg-emerald-500 text-white' : 'bg-gray-800 text-gray-300 group-hover:bg-gray-700'
                  }`}>
                    {c.display_name?.[0]?.toUpperCase() || '?'}
                  </div>
                  {c.is_online && (
                    <div className="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-emerald-500 border-2 border-space-bg rounded-full shadow-[0_0_5px_rgba(16,185,129,0.8)]"></div>
                  )}
                </div>
                
                <div className="flex-1 truncate">
                  <h3 className={`font-medium truncate ${isActive ? 'text-white' : 'text-gray-300 group-hover:text-white'}`}>
                    {c.display_name || c.username}
                  </h3>
                  <p className="text-xs text-gray-500 truncate mt-0.5">Click to chat</p>
                </div>
              </motion.div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-white/5">
        <button 
          onClick={onLogout}
          className="w-full py-2.5 rounded-xl bg-white/5 hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-colors text-sm font-medium flex items-center justify-center gap-2 border border-transparent hover:border-red-500/30"
        >
          Sign Out
        </button>
      </div>
    </div>
  );
}
