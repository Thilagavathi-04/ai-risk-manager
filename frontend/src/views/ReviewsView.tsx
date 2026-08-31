import React, { useEffect, useState } from 'react';
import type { ReviewItem } from '../types';
import { fetchReviews, submitReview } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react';

export const ReviewsView: React.FC = () => {
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const loadData = () => {
    setLoading(true);
    fetchReviews()
      .then((res) => {
        setReviews(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAction = async (id: string, outcome: string) => {
    setUpdatingId(id);
    try {
      await submitReview(id, outcome);
      loadData();
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div>
      <section className="glass-panel">
        <div className="page-head">
          <div>
            <h2>Human Review Queue</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
              Verification queue for flagged transactions requiring risk analyst confirmation.
            </p>
          </div>
          <button className="btn btn-secondary" onClick={loadData}>
            <RefreshCw size={16} /> Refresh Queue
          </button>
        </div>

        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading review queue items...</p>
        ) : reviews.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            <CheckCircle size={32} color="#10b981" style={{ marginBottom: '12px' }} />
            <p>Review queue is clear! All flagged items have been resolved.</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Transaction ID</th>
                  <th>Amount</th>
                  <th>Risk Score</th>
                  <th>Recommendation</th>
                  <th>Current Status</th>
                  <th>Analyst Decision Actions</th>
                </tr>
              </thead>
              <tbody>
                {reviews.map((item) => (
                  <tr key={item.transaction_id}>
                    <td style={{ fontWeight: '600', color: '#38bdf8' }}>{item.transaction_id}</td>
                    <td style={{ fontWeight: '600' }}>{item.amount}</td>
                    <td style={{ fontWeight: '700', color: '#fca5a5' }}>{item.score}</td>
                    <td style={{ color: 'var(--text-muted)' }}>{item.recommendation}</td>
                    <td>
                      <StatusBadge status={item.status} />
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          className="btn btn-success"
                          style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                          disabled={updatingId === item.transaction_id}
                          onClick={() => handleAction(item.transaction_id, 'APPROVED')}
                        >
                          <CheckCircle size={14} /> Approve
                        </button>
                        <button
                          className="btn btn-danger"
                          style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                          disabled={updatingId === item.transaction_id}
                          onClick={() => handleAction(item.transaction_id, 'DECLINED')}
                        >
                          <XCircle size={14} /> Decline
                        </button>
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '6px 12px', fontSize: '0.8rem', background: '#f59e0b', color: '#0f172a' }}
                          disabled={updatingId === item.transaction_id}
                          onClick={() => handleAction(item.transaction_id, 'ESCALATED')}
                        >
                          <AlertTriangle size={14} /> Escalate
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};
