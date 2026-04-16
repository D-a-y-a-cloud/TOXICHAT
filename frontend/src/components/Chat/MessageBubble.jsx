import React from 'react';
import { motion } from 'framer-motion';
import { Check, CheckCheck } from 'lucide-react';

export default function MessageBubble({ message, isOwn }) {
  const isFlagged = message.is_flagged;
  const isToxic = message.toxicity_label === 'toxic';
  const timeString = new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className={`flex w-full ${isOwn ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`relative max-w-[85%] sm:max-w-[70%] flex flex-col ${isOwn ? 'items-end' : 'items-start'}`}>
        
        {/* Flagged Warning Header */}
        {isFlagged && !isOwn && (
          <div className="flex items-center gap-1 mb-1 px-2">
            <span className="text-red-500 text-xs">⚠️</span>
            <span className="text-red-400 text-[10px] uppercase font-bold tracking-wider">Potentially harmful</span>
          </div>
        )}

        {/* Bubble */}
        <div className={`px-2.5 pt-1.5 pb-1 text-[15px] rounded-lg relative min-w-[90px] shadow-sm ${
          isOwn 
            ? 'bg-wa-sender text-[#E9EDEF] rounded-tr-none' 
            : isFlagged 
              ? 'bg-red-900/50 text-[#E9EDEF] rounded-tl-none border border-red-500/50' 
              : 'bg-wa-panel text-[#E9EDEF] rounded-tl-none'
        }`}>
          <p className="leading-snug whitespace-pre-wrap break-words pr-2">{message.text}</p>
          
          {/* Timestamp and Status Container */}
          <div className="flex items-center justify-end gap-1 mt-0.5 float-right -mr-0.5">
            {message.toxicity_score > 0 && (
              <span className={`text-[9px] font-bold px-1 rounded uppercase ${
                isToxic ? 'text-red-400' : 'text-emerald-400'
              }`}>
                {isToxic ? '🔴' : '🟢'} {(message.toxicity_score * 100).toFixed(0)}%
              </span>
            )}
            <span className="text-[10px] text-white/50 font-medium whitespace-nowrap tracking-wide leading-none select-none">
              {timeString}
            </span>
            {isOwn && (
              <div className="flex flex-shrink-0 items-center -mb-[1px]">
                {message.status === 'sent' && <Check className="w-[14px] h-[14px] text-white/50" strokeWidth={2.5} />}
                {message.status === 'delivered' && <CheckCheck className="w-[14px] h-[14px] text-white/50" strokeWidth={2.5} />}
                {message.status === 'read' && <CheckCheck className="w-[14px] h-[14px] text-[#53bdeb]" strokeWidth={2.5} />}
                {!['sent', 'delivered', 'read'].includes(message.status) && <Check className="w-[14px] h-[14px] text-white/50" strokeWidth={2.5} />}
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
