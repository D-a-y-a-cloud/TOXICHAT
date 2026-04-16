import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, X } from 'lucide-react';

export default function ToxicityAlert({ alert, onClose }) {
  return (
    <AnimatePresence>
      {alert && (
        <motion.div
          initial={{ opacity: 0, y: -50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.9 }}
          className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-full max-w-md"
        >
          <div className="bg-toxic-dark/90 backdrop-blur-xl border border-toxic-border shadow-2xl shadow-toxic-glow rounded-2xl overflow-hidden flex flex-row items-center p-4 gap-4">
            <div className="w-12 h-12 rounded-xl bg-red-500/20 flex flex-shrink-0 items-center justify-center border border-red-500/50">
              <AlertTriangle className="text-red-500 w-6 h-6 animate-pulse-fast" />
            </div>
            
            <div className="flex-1">
              <h3 className="text-red-400 font-bold text-lg mb-1">Toxicity Warning</h3>
              <p className="text-gray-300 text-sm leading-tight">{alert.message}</p>
              <div className="mt-2 inline-flex items-center gap-2 bg-red-500/10 px-2 py-1 rounded border border-red-500/20">
                <span className="text-xs text-red-300 uppercase tracking-wider font-semibold">Score: {(alert.score * 100).toFixed(1)}%</span>
              </div>
            </div>

            <button 
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-xl transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
