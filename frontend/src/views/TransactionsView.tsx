import React, { useEffect, useState } from 'react';
import type { TransactionDetail, TransactionListItem } from '../types';
import { fetchTransactionDetail, fetchTransactions } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { Search, Eye, X, AlertCircle, ShieldAlert } from 'lucide-react';

export const TransactionsView: React.FC = () => {
  const [transactions, setTransactions] = useState<TransactionListItem[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedTxId, setSelectedTxId] = useState<string | null>(null);
  const [detail, setDetail] = useState<TransactionDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchTransactions()
      .then((res) => {
        setTransactions(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleOpenDetail = (id: string) => {
    setSelectedTxId(id);
    fetchTransactionDetail(id).then((res) => setDetail(res));
  };

  const filtered = transactions.filter(
    (tx) =>
      tx.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tx.merchant.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tx.risk_level.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <section className="glass-panel">
        <div className="page-head">
          <h2>Transaction Queue</h2>
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '10px' }} />
            <input
              type="text"
              placeholder="Search ID, merchant, risk..."
              className="search-input"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                paddingLeft: '36px',
              }}
            />
          </div>
        </div>

        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading transaction queue...</p>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Timestamp</th>
                  <th>Amount</th>
                  <th>Merchant</th>
                  <th>Category</th>
                  <th>Risk Score</th>
                  <th>Risk Level</th>
                  <th>Action</th>
                  <th>Inspect</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((tx) => (
                  <tr key={tx.id}>
                    <td style={{ fontWeight: '600', color: 'var(--primary)' }}>{tx.id}</td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{tx.timestamp}</td>
                    <td style={{ fontWeight: '600' }}>{tx.amount}</td>
                    <td>{tx.merchant}</td>
                    <td style={{ textTransform: 'capitalize' }}>{tx.category}</td>
                    <td style={{ fontWeight: '700' }}>{tx.risk_score}</td>
                    <td>
                      <StatusBadge status={tx.risk_level} />
                    </td>
                    <td style={{ color: 'var(--text-muted)' }}>{tx.recommended_action}</td>
                    <td>
                      <button className="btn btn-secondary" style={{ padding: '6px 12px' }} onClick={() => handleOpenDetail(tx.id)}>
                        <Eye size={14} /> Detail
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Transaction Detail Modal Drawer */}
      {selectedTxId && detail && (
        <div className="modal-overlay" onClick={() => setSelectedTxId(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <ShieldAlert size={24} color="var(--primary)" />
                <h3 style={{ margin: 0, fontFamily: 'Outfit, sans-serif', fontSize: '1.4rem' }}>
                  Transaction {detail.id}
                </h3>
              </div>
              <button className="btn btn-secondary" style={{ padding: '6px' }} onClick={() => setSelectedTxId(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="stat-grid" style={{ marginBottom: '24px' }}>
              <div className="stat-card">
                <strong>{detail.amount}</strong>
                <span>Amount</span>
              </div>
              <div className="stat-card">
                <StatusBadge status={detail.risk_level} />
                <span style={{ display: 'block', marginTop: '6px' }}>Risk Score: {detail.risk_score}</span>
              </div>
              <div className="stat-card">
                <strong>{detail.recommended_action}</strong>
                <span>Action</span>
              </div>
            </div>

            <div style={{ marginBottom: '24px' }}>
              <h4 style={{ color: 'var(--text-muted)', marginBottom: '12px', fontSize: '0.85rem', textTransform: 'uppercase' }}>
                Extracted Model Risk Signals
              </h4>
              <ul style={{ paddingLeft: '20px', color: 'var(--danger)' }}>
                {detail.signals.map((sig, i) => (
                  <li key={i} style={{ marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AlertCircle size={14} color="var(--danger)" /> {sig}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 style={{ color: 'var(--text-muted)', marginBottom: '12px', fontSize: '0.85rem', textTransform: 'uppercase' }}>
                Historical Customer Velocity
              </h4>
              <div className="field-grid">
                {detail.historical_context.map(([key, val], idx) => (
                  <div key={idx} className="field-box">
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>{key}</span>
                    <strong style={{ fontSize: '1.1rem', color: 'var(--text-main)' }}>{val}</strong>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
