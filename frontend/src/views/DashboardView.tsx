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
    fetchDashboard()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

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

  // Sample Time Series Data for 24-hour Trend Chart
  const hourlyTrendData = [
    { hour: '00:00', volume: 380, fraud: 4 },
    { hour: '02:00', volume: 290, fraud: 2 },
    { hour: '04:00', volume: 180, fraud: 1 },
    { hour: '06:00', volume: 420, fraud: 5 },
    { hour: '08:00', volume: 850, fraud: 12 },
    { hour: '10:00', volume: 1240, fraud: 18 },
    { hour: '12:00', volume: 1420, fraud: 24 },
    { hour: '14:00', volume: 1650, fraud: 31 },
    { hour: '16:00', volume: 1580, fraud: 28 },
    { hour: '18:00', volume: 1390, fraud: 22 },
    { hour: '20:00', volume: 1120, fraud: 16 },
    { hour: '22:00', volume: 740, fraud: 9 },
  ];

  const maxVolume = Math.max(...hourlyTrendData.map((d) => d.volume));

  // Payment Method Risk Breakdown
  const paymentBreakdown = [
    { type: 'TRANSFER', volume: '₹4.8M', share: '38%', fraudRate: '18.4%', riskLevel: 'HIGH', percent: 38, color: '#ef4444' },
    { type: 'CASH_OUT', volume: '₹3.6M', share: '29%', fraudRate: '14.1%', riskLevel: 'HIGH', percent: 29, color: '#f97316' },
    { type: 'PAYMENT', volume: '₹2.2M', share: '18%', fraudRate: '0.1%', riskLevel: 'LOW', percent: 18, color: '#3b82f6' },
    { type: 'CASH_IN', volume: '₹1.1M', share: '9%', fraudRate: '0.0%', riskLevel: 'LOW', percent: 9, color: '#10b981' },
    { type: 'DEBIT', volume: '₹700K', share: '6%', fraudRate: '0.0%', riskLevel: 'LOW', percent: 6, color: '#6366f1' },
  ];

  // KPI Stat Cards
  const statCards = [
    { label: 'Total Volume', value: '₹12.4M', icon: Activity },
    { label: 'Monitored Count', value: data.stats[0]?.value || '12,526', icon: ArrowUpRight },
    { label: 'High Risk Flags', value: data.stats[1]?.value || '193', icon: AlertTriangle },
    { label: 'Pending Reviews', value: data.stats[2]?.value || '76', icon: Clock },
    { label: 'Model Precision', value: data.stats[3]?.value || '91.2%', icon: ShieldCheck },
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
                      {d.hour}
                    </text>
                  </g>
                );
              })}
            </svg>

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
                <strong>Hour: {hourlyTrendData[activeBarIndex].hour}</strong>
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
              <svg width="130" height="130" viewBox="0 0 42 42" className="donut">
                <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="var(--panel-hover)" strokeWidth="5" />
                {/* Low Risk Segment (Green) - 92% */}
                <circle
                  cx="21"
                  cy="21"
                  r="15.915"
                  fill="transparent"
                  stroke="var(--accent)"
                  strokeWidth="5"
                  strokeDasharray="92 8"
                  strokeDashoffset="25"
                />
                {/* Medium Risk Segment (Yellow) - 6% */}
                <circle
                  cx="21"
                  cy="21"
                  r="15.915"
                  fill="transparent"
                  stroke="var(--warning)"
                  strokeWidth="5"
                  strokeDasharray="6 94"
                  strokeDashoffset="-67"
                />
                {/* High Risk Segment (Red) - 2% */}
                <circle
                  cx="21"
                  cy="21"
                  r="15.915"
                  fill="transparent"
                  stroke="var(--danger)"
                  strokeWidth="5"
                  strokeDasharray="2 98"
                  strokeDashoffset="-73"
                />
              </svg>
              <div
                style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  textAlign: 'center',
                }}
              >
                <strong style={{ fontSize: '1.2rem', color: 'var(--text-main)', display: 'block' }}>92.4%</strong>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Low Risk</span>
              </div>
            </div>

            {/* Legend Distribution List */}
            <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent)' }} /> Low Risk
                </span>
                <strong style={{ color: 'var(--text-main)' }}>92.4% (11,574)</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--warning)' }} /> Medium Risk
                </span>
                <strong style={{ color: 'var(--text-main)' }}>6.1% (759)</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--danger)' }} /> High Risk
                </span>
                <strong style={{ color: 'var(--danger-text)' }}>1.5% (193)</strong>
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
          {paymentBreakdown.map((item, idx) => (
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
                    backgroundColor: item.color,
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
