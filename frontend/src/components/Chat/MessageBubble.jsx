import React from 'react';
import { motion } from 'framer-motion';

export default function MessageBubble({ message, isOwn }) {
  const isFlagged = message.is_flagged;
  const isToxic = message.toxicity_label === 'toxic';
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className={`flex w-full ${isOwn ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`relative max-w-[70%] sm:max-w-[60%] flex flex-col ${isOwn ? 'items-end' : 'items-start'}`}>
        
        {/* Flagged Warning Header */}
        {isFlagged && !isOwn && (
          <div className="flex items-center gap-1 mb-1 px-2">
            <span className="text-red-500 text-xs">⚠️</span>
            <span className="text-red-400 text-[10px] uppercase font-bold tracking-wider">Potentially harmful</span>
          </div>
        )}

        {/* Bubble */}
        <div className={`px-5 py-3 rounded-2xl shadow-lg relative overflow-hidden backdrop-blur-md ${
          isOwn 
            ? 'bg-gradient-to-br from-emerald-500 to-teal-600 text-white rounded-br-sm border border-emerald-400/30' 
            : isFlagged 
              ? 'bg-red-500/10 text-red-100 rounded-bl-sm border border-red-500/50 shadow-red-500/20' 
              : 'bg-white/10 text-gray-100 rounded-bl-sm border border-white/5 shadow-black/50'
        }`}>
          {isOwn && <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />}
          <p className="relative z-10 leading-relaxed text-[15px]">{message.text}</p>
        </div>

        {/* Meta / Timestamp */}
        <div className={`flex items-center gap-2 mt-1.5 px-1 ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}>
          <span className="text-[10px] text-gray-500 font-medium">
            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
          
          {message.toxicity_score > 0 && (
            <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
              isToxic 
                ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
            }`}>
              {isToxic ? '🔴' : '🟢'} {(message.toxicity_score * 100).toFixed(0)}%
            </span>
          )}
        </div>

      </div>
    </motion.div>
  );
}
