import React from 'react';

export default function Dashboard({ stats }) {
  if (!stats) return <div className="flex-1 glass-panel ml-4 rounded-r-3xl flex items-center justify-center text-gray-400">Loading dashboard...</div>;

  const toxRate = (stats.toxicity_rate * 100).toFixed(1);

  return (
    <div className="flex-1 flex flex-col relative z-10 glass-panel ml-4 rounded-r-3xl overflow-y-auto shadow-2xl p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-cyan-400 inline-block mb-2">Toxicity Dashboard</h2>
        <p className="text-gray-400 text-sm">Real-time statistics of machine learning moderation.</p>
      </div>

      {/* Grid Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 flex flex-col">
          <span className="text-3xl font-bold text-white tracking-tight">{stats.total_messages}</span>
          <span className="text-sm font-medium text-gray-400 mt-1 uppercase tracking-wider">Total Messages</span>
        </div>
        <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-5 flex flex-col shadow-[0_0_30px_rgba(239,68,68,0.1)]">
          <span className="text-3xl font-bold text-red-500 tracking-tight">{stats.toxic_count}</span>
          <span className="text-sm font-medium text-red-400 mt-1 uppercase tracking-wider">Toxic Flags</span>
        </div>
        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-5 flex flex-col">
          <span className="text-3xl font-bold text-emerald-400 tracking-tight">{stats.non_toxic_count}</span>
          <span className="text-sm font-medium text-emerald-500/70 mt-1 uppercase tracking-wider">Safe Messages</span>
        </div>
        <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-2xl p-5 flex flex-col">
          <span className="text-3xl font-bold text-cyan-400 tracking-tight">{toxRate}%</span>
          <span className="text-sm font-medium text-cyan-500/70 mt-1 uppercase tracking-wider">Toxicity Rate</span>
        </div>
      </div>

      {/* Flagged Users List */}
      {stats.most_toxic_users.length > 0 && (
        <div className="mb-10">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
            Most Flagged Users
          </h3>
          <div className="bg-black/20 border border-white/5 rounded-2xl overflow-hidden shadow-inner">
            {stats.most_toxic_users.map((u, i) => (
              <div key={i} className="flex items-center justify-between p-4 border-b border-white/5 last:border-b-0 hover:bg-white/5 transition-colors">
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-500 w-4 font-mono">{i + 1}.</span>
                  <span className="text-white font-medium">{u.username}</span>
                </div>
                <div className="bg-red-500/20 text-red-400 text-xs font-bold px-2 py-1 rounded inline-flex items-center gap-1 border border-red-500/30">
                  {u.toxic_count} flags
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
