import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertOctagon } from 'lucide-react';

export default function MutedModal({ isOpen, onClose }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/60 backdrop-blur-md"
          />
          
          {/* Modal Content */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative w-full max-w-sm bg-wa-panel border border-red-500/50 rounded-3xl p-6 shadow-2xl shadow-red-500/20 overflow-hidden"
          >
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-red-500/20 flex items-center justify-center mb-4 border border-red-500/30">
                <AlertOctagon className="w-8 h-8 text-red-500 animate-pulse" />
              </div>
              
              <h2 className="text-2xl font-bold text-white mb-2 tracking-tight">Account Muted</h2>
              
              <p className="text-gray-300 text-sm leading-relaxed mb-6">
                You have received 3 toxicity warnings. Your messaging privileges have been temporarily suspended to maintain community safety.
              </p>
              
              <button 
                onClick={onClose}
                className="w-full py-3 rounded-xl bg-red-500 hover:bg-red-600 text-white font-semibold transition-colors shadow-lg shadow-red-500/30"
              >
                I Understand
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
