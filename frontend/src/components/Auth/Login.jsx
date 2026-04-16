import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, ArrowRight, UserPlus, LogIn } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    const endpoint = isRegister ? '/api/register' : '/api/login';
    const body = isRegister
      ? { username, password, display_name: displayName || username }
      : { username, password };

    try {
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Auth failed');
      onLogin(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const formVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative px-4">
      <motion.div 
        initial="hidden" 
        animate="visible" 
        variants={formVariants}
        className="glass-panel w-full max-w-md p-8 rounded-3xl"
      >
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center mb-4 shadow-lg shadow-emerald-500/30">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">ToxiChat</h1>
          <p className="text-gray-400 mt-2 text-sm text-center">AI-Powered Safe Messaging Interface</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <input 
              placeholder="Username" 
              value={username}
              onChange={e => setUsername(e.target.value)} 
              required 
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all"
            />
          </div>
          
          {isRegister && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
              <input 
                placeholder="Display Name (optional)" 
                value={displayName}
                onChange={e => setDisplayName(e.target.value)} 
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all"
              />
            </motion.div>
          )}

          <div>
            <input 
              placeholder="Password" 
              type="password" 
              value={password}
              onChange={e => setPassword(e.target.value)} 
              required 
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all"
            />
          </div>

          {error && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-xl text-sm">
              {error}
            </motion.div>
          )}

          <motion.button 
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit" 
            disabled={loading}
            className="w-full bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-medium py-3 rounded-xl flex items-center justify-center gap-2 hover:from-emerald-400 hover:to-cyan-400 transition-all shadow-lg shadow-emerald-500/25 disabled:opacity-50"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : isRegister ? (
              <><UserPlus className="w-5 h-5" /> Create Account</>
            ) : (
              <><LogIn className="w-5 h-5" /> Sign In</>
            )}
          </motion.button>
        </form>

        <div className="mt-6 text-center">
          <button 
            onClick={() => { setIsRegister(!isRegister); setError(''); }}
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            {isRegister ? 'Already have an account? Sign In' : "Don't have an account? Register"}
          </button>
        </div>
      </motion.div>
    </div>
  );
}
