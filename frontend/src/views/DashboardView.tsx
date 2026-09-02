import React, { useEffect, useState } from 'react';
import type { DashboardSummary } from '../types';
import { fetchDashboard } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import {
  Activity,
  AlertTriangle,
  Clock,
  ShieldCheck,
  BarChart2,
  PieChart,
  ArrowUpRight,
  Filter,
} from 'lucide-react';

interface DashboardViewProps {
  onNavigateTab: (tab: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ onNavigateTab }) => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Analytics View State
  const [timeframe, setTimeframe] = useState<'24h' | '7d' | '30d'>('24h');
  const [tableFilter, setTableFilter] = useState<'all' | 'high' | 'pending'>('all');
  const [activeBarIndex, setActiveBarIndex] = useState<number | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchDashboard(timeframe)
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [timeframe]);

  if (loading) {
    return (
      <div className="glass-panel" style={{ textAlign: 'center', padding: '60px' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading live analytics engine...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="glass-panel" style={{ textAlign: 'center', padding: '40px' }}>
        <AlertTriangle size={32} color="var(--danger)" style={{ marginBottom: '12px' }} />
        <p style={{ color: 'var(--danger-text)' }}>Failed to load analytics dashboard: {error}</p>
      </div>
    );
  }

  const hourlyTrendData = data.hourly_trend;
  const maxVolume = Math.max(1, ...hourlyTrendData.map((d) => d.volume));
  const paymentBreakdown = data.payment_breakdown;
  const riskDistribution = data.risk_distribution;

  const statValues = new Map(data.stats.map((stat) => [stat.label, stat.value]));

  // KPI Stat Cards
  const statCards = [
    { label: 'Transactions', value: statValues.get('Transactions') || '0', icon: ArrowUpRight },
    { label: 'High Risk Flags', value: statValues.get('High Risk') || '0', icon: AlertTriangle },
    { label: 'Pending Reviews', value: statValues.get('Review Queue') || '0', icon: Clock },
    { label: 'Total Volume', value: statValues.get('Total Volume') || '₹0', icon: Activity },
    { label: 'Model Precision', value: statValues.get('Precision') || '', icon: ShieldCheck },
  ];

  // Filtered Transactions Feed
  const filteredTransactions = data.recent_transactions.filter((tx) => {
    if (tableFilter === 'high') return tx.risk_level === 'HIGH';
    if (tableFilter === 'pending') return tx.action.toLowerCase().includes('review') || tx.action.toLowerCase().includes('verification');
    return true;
  });

  return (
    <div>
      {/* Analytics Header Bar */}
      <section className="glass-panel">
        <div className="page-head">
          <div>
            <h2>Merchant Risk Analytics Dashboard</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '2px' }}>
              Real-time payment volume monitoring, fraud rate breakdown, and model evaluation metrics.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div className="tab-group">
              <button
                className={`filter-tab ${timeframe === '24h' ? 'active' : ''}`}
                onClick={() => setTimeframe('24h')}
              >
                24 Hours
              </button>
              <button
                className={`filter-tab ${timeframe === '7d' ? 'active' : ''}`}
                onClick={() => setTimeframe('7d')}
              >
                7 Days
              </button>
              <button
                className={`filter-tab ${timeframe === '30d' ? 'active' : ''}`}
                onClick={() => setTimeframe('30d')}
              >
                30 Days
              </button>
            </div>
          </div>
        </div>

        {/* Analytics KPI Stat Cards */}
        <div className="stat-grid">
          {statCards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <div key={idx} className="stat-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <strong>{card.value}</strong>
                  <Icon size={20} color="var(--primary)" />
                </div>
                <span>{card.label}</span>
              </div>
            );
          })}
        </div>
      </section>

      {/* Row 1: Interactive Charts */}
      <div className="analytics-grid-two">
        {/* Chart 1: Hourly Transaction Volume & Fraud Trend */}
        <section className="glass-panel">
          <div className="page-head" style={{ marginBottom: '16px' }}>
            <div>
              <h3>
                <BarChart2 size={18} color="var(--primary)" style={{ marginRight: '8px', verticalAlign: 'middle' }} />
                24-Hour Transaction Volume & Fraud Velocity
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '2px' }}>
                Comparing overall transaction count (bars) against high-risk flags. Hover over bars to inspect details.
              </p>
            </div>
          </div>

            <div style={{ position: 'relative', width: '100%', height: '220px', paddingTop: '10px' }}>
            {hourlyTrendData.length === 0 ? (
              <div style={{ height: '180px', display: 'grid', placeItems: 'center', color: 'var(--text-muted)' }}>
                No transactions recorded for the selected timeframe.
              </div>
            ) : (
            <svg width="100%" height="180" viewBox="0 0 600 180" preserveAspectRatio="none" style={{ overflow: 'visible' }}>
              {/* Background Grid Lines */}
              {[0, 45, 90, 135, 180].map((y, i) => (
                <line key={i} x1="0" y1={y} x2="600" y2={y} stroke="var(--panel-border)" strokeDasharray="3 3" />
              ))}

              {/* Bar Elements */}
              {hourlyTrendData.map((d, idx) => {
                const barWidth = 32;
                const gap = (600 - barWidth * hourlyTrendData.length) / (hourlyTrendData.length + 1);
                const x = gap + idx * (barWidth + gap);
                const barHeight = (d.volume / maxVolume) * 140;
                const y = 180 - barHeight;

                const fraudHeight = (d.fraud / maxVolume) * 140 * 15; // Scale fraud visually
                const fraudY = 180 - Math.min(fraudHeight, barHeight);

                const isHovered = activeBarIndex === idx;

                return (
                  <g
                    key={idx}
                    className="bar-group"
                    onMouseEnter={() => setActiveBarIndex(idx)}
                    onMouseLeave={() => setActiveBarIndex(null)}
                    style={{ cursor: 'pointer' }}
                  >
                    {/* Volume Bar */}
                    <rect
                      x={x}
                      y={y}
                      width={barWidth}
                      height={barHeight}
                      rx="4"
                      fill={isHovered ? 'var(--primary-hover)' : 'var(--primary)'}
                      opacity={isHovered ? 1 : 0.85}
                      className="bar-rect"
                    />

                    {/* Fraud Highlight Overlay */}
                    <rect
                      x={x}
                      y={fraudY}
                      width={barWidth}
                      height={Math.min(fraudHeight, barHeight)}
                      rx="2"
                      fill="var(--danger)"
                      opacity="0.9"
                    />

                    {/* X-Axis Labels */}
                    <text
                      x={x + barWidth / 2}
                      y="196"
                      textAnchor="middle"
                      fill="var(--text-muted)"
                      fontSize="10"
                      fontWeight="600"
                    >
                      {d.label}
                    </text>
                  </g>
                );
              })}
            </svg>
            )}

            {/* Hover Tooltip Box */}
            {activeBarIndex !== null && (
              <div
                style={{
                  position: 'absolute',
                  top: '10px',
                  right: '20px',
                  background: 'var(--card-bg)',
                  border: '1px solid var(--panel-border)',
                  padding: '8px 14px',
                  borderRadius: '8px',
                  boxShadow: 'var(--shadow-sm)',
                  fontSize: '0.8rem',
                  color: 'var(--text-main)',
                  pointerEvents: 'none',
                }}
              >
                <strong>Hour: {hourlyTrendData[activeBarIndex].label}</strong>
                <div>Volume: {hourlyTrendData[activeBarIndex].volume} txs</div>
                <div style={{ color: 'var(--danger-text)', fontWeight: '700' }}>
                  High Risk: {hourlyTrendData[activeBarIndex].fraud} flags
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Chart 2: Risk Classification Distribution */}
        <section className="glass-panel">
          <div className="page-head" style={{ marginBottom: '16px' }}>
            <h3>
              <PieChart size={18} color="var(--accent)" style={{ marginRight: '8px', verticalAlign: 'middle' }} />
              Risk Classification Share
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
            {/* SVG Donut Chart */}
            <div style={{ position: 'relative', width: '130px', height: '130px' }}>
              {riskDistribution.length === 0 ? (
                <div style={{ width: '130px', height: '130px', display: 'grid', placeItems: 'center', color: 'var(--text-muted)' }}>
                  No data
                </div>
              ) : (
              <svg width="130" height="130" viewBox="0 0 42 42" className="donut">
                <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="var(--panel-hover)" strokeWidth="5" />
                {riskDistribution.map((segment, idx) => (
                  <circle
                    key={segment.label}
                    cx="21"
                    cy="21"
                    r="15.915"
                    fill="transparent"
                    stroke={idx === 0 ? 'var(--accent)' : idx === 1 ? 'var(--warning)' : 'var(--danger)'}
                    strokeWidth="5"
                    strokeDasharray={`${segment.percent} ${100 - segment.percent}`}
                    strokeDashoffset={idx === 0 ? '25' : idx === 1 ? '-67' : '-73'}
                  />
                ))}
              </svg>
              )}
              <div
                style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  textAlign: 'center',
                }}
              >
                <strong style={{ fontSize: '1.2rem', color: 'var(--text-main)', display: 'block' }}>
                  {riskDistribution[0] ? `${riskDistribution[0].percent.toFixed(1)}%` : '0%'}
                </strong>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                  {riskDistribution[0] ? riskDistribution[0].label : 'Low Risk'}
                </span>
              </div>
            </div>

            {/* Legend Distribution List */}
            <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent)' }} /> Low Risk
                </span>
                <strong style={{ color: 'var(--text-main)' }}>{riskDistribution[0] ? `${riskDistribution[0].percent.toFixed(1)}% (${riskDistribution[0].count.toLocaleString()})` : '0%'}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--warning)' }} /> Medium Risk
                </span>
                <strong style={{ color: 'var(--text-main)' }}>{riskDistribution[1] ? `${riskDistribution[1].percent.toFixed(1)}% (${riskDistribution[1].count.toLocaleString()})` : '0%'}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--danger)' }} /> High Risk
                </span>
                <strong style={{ color: 'var(--danger-text)' }}>{riskDistribution[2] ? `${riskDistribution[2].percent.toFixed(1)}% (${riskDistribution[2].count.toLocaleString()})` : '0%'}</strong>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* Row 2: Risk Breakdown by Payment Method & Operational Gauge */}
      <section className="glass-panel">
        <div className="page-head" style={{ marginBottom: '16px' }}>
          <div>
            <h3>Risk & Volume Breakdown by Payment Type</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '2px' }}>
              PAYMENT fraud concentrated heavily in TRANSFER and CASH_OUT categories.
            </p>
          </div>
        </div>

        <div className="progress-list">
          {paymentBreakdown.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No payment data recorded yet.</p>
          ) : paymentBreakdown.map((item, idx) => (
            <div key={idx} className="progress-item">
              <div className="progress-label-row">
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontWeight: '700', width: '90px' }}>{item.type}</span>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Volume: {item.volume} ({item.share})</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ color: item.riskLevel === 'HIGH' ? 'var(--danger-text)' : 'var(--text-muted)', fontWeight: '700', fontSize: '0.8rem' }}>
                    Fraud Rate: {item.fraudRate}
                  </span>
                  <StatusBadge status={item.riskLevel} />
                </div>
              </div>

              <div className="progress-track">
                <div
                  className="progress-fill"
                  style={{
                    width: `${item.percent}%`,
                    backgroundColor: item.riskLevel === 'HIGH' ? '#ef4444' : item.riskLevel === 'MEDIUM' ? '#f59e0b' : '#10b981',
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Row 3: Scored Transactions Feed with Analytics Filter Tabs */}
      <section className="glass-panel">
        <div className="page-head">
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
            <h3>Recent Scored Transactions Feed</h3>

            {/* Filter Tabs */}
            <div className="tab-group">
              <button
                className={`filter-tab ${tableFilter === 'all' ? 'active' : ''}`}
                onClick={() => setTableFilter('all')}
              >
                All Transactions ({data.recent_transactions.length})
              </button>
              <button
                className={`filter-tab ${tableFilter === 'high' ? 'active' : ''}`}
                onClick={() => setTableFilter('high')}
              >
                <Filter size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                High Risk Only ({data.recent_transactions.filter((t) => t.risk_level === 'HIGH').length})
              </button>
              <button
                className={`filter-tab ${tableFilter === 'pending' ? 'active' : ''}`}
                onClick={() => setTableFilter('pending')}
              >
                Pending Review ({data.recent_transactions.filter((t) => t.action.toLowerCase().includes('review')).length})
              </button>
            </div>
          </div>

          <button className="btn btn-secondary" onClick={() => onNavigateTab('transactions')}>
            View Full Queue
          </button>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Amount</th>
                <th>Risk Level</th>
                <th>Risk Score</th>
                <th>Recommended Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredTransactions.map((tx) => (
                <tr key={tx.id}>
                  <td style={{ fontWeight: '600', color: 'var(--primary)' }}>{tx.id}</td>
                  <td style={{ fontWeight: '600' }}>{tx.amount}</td>
                  <td>
                    <StatusBadge status={tx.risk_level} />
                  </td>
                  <td style={{ fontWeight: '700', color: tx.risk_level === 'HIGH' ? 'var(--danger-text)' : 'var(--text-main)' }}>
                    {tx.risk_score}
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>{tx.action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};
