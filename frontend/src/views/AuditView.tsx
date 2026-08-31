import React, { useEffect, useState } from 'react';
import type { AuditEntry } from '../types';
import { fetchAudit } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';

export const AuditView: React.FC = () => {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchAudit()
      .then((res) => {
        setEntries(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div>
      <section className="glass-panel">
        <div className="page-head">
          <div>
            <h2>Decision Audit Log</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
              Immutable audit log capturing model versions, decision thresholds, risk scores, and human reviewer decisions.
            </p>
          </div>
        </div>

        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading audit entries...</p>
        ) : entries.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No audit log entries recorded yet.</p>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Transaction ID</th>
                  <th>Model Version</th>
                  <th>Risk Score</th>
                  <th>Threshold</th>
                  <th>System Decision</th>
                  <th>Reviewer Outcome</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry, idx) => (
                  <tr key={idx}>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{entry.timestamp}</td>
                    <td style={{ fontWeight: '600', color: '#38bdf8' }}>{entry.transaction_id}</td>
                    <td>
                      <span className="pill">{entry.model_version}</span>
                    </td>
                    <td style={{ fontWeight: '700' }}>{entry.score}</td>
                    <td style={{ color: 'var(--text-muted)' }}>{entry.threshold}</td>
                    <td>
                      <StatusBadge status={entry.decision} />
                    </td>
                    <td>
                      <StatusBadge status={entry.reviewer_outcome} />
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
