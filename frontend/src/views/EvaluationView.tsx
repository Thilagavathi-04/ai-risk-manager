import React, { useEffect, useState } from 'react';
import type { EvaluationData } from '../types';
import { fetchEvaluation } from '../services/api';
import { GitCompare } from 'lucide-react';

export const EvaluationView: React.FC = () => {
  const [data, setData] = useState<EvaluationData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchEvaluation()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return (
      <div className="glass-panel" style={{ textAlign: 'center', padding: '60px' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading model evaluation diagnostics...</p>
      </div>
    );
  }

  return (
    <div>
      <section className="glass-panel">
        <div className="page-head">
          <div>
            <h2>Model Performance Metrics</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
              Held-out test set metrics for the current production model sweep.
            </p>
          </div>
        </div>

        <div className="stat-grid">
          {data.metrics.map((m, idx) => (
            <div key={idx} className="stat-card">
              <strong>{m.value}</strong>
              <span>{m.label}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="glass-panel">
        <div className="page-head">
          <h3>
            <GitCompare size={20} color="var(--primary)" style={{ marginRight: '8px', verticalAlign: 'middle' }} />
            Model Comparison Matrix
          </h3>
        </div>
        <p style={{ color: 'var(--text-muted)', marginBottom: '16px', fontSize: '0.9rem' }}>
          Comparing all tracked candidate models on the same temporal test split.
        </p>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Model Architecture</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1 Score</th>
                <th>PR-AUC</th>
                <th>Expected Cost</th>
              </tr>
            </thead>
            <tbody>
              {data.model_comparison.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ color: 'var(--text-muted)', textAlign: 'center' }}>
                    No model comparison data available yet.
                  </td>
                </tr>
              ) : (
                data.model_comparison.map((row, idx) => (
                  <tr key={idx} style={{ background: row.is_selected ? 'rgba(2, 132, 199, 0.08)' : 'transparent' }}>
                    <td style={{ fontWeight: '700', color: row.is_selected ? 'var(--primary)' : 'var(--text-main)' }}>
                      {row.model_name} {row.is_selected && '(Active)'}
                    </td>
                    <td style={{ fontWeight: '600' }}>{row.precision}</td>
                    <td style={{ fontWeight: '600' }}>{row.recall}</td>
                    <td style={{ fontWeight: '600' }}>{row.f1}</td>
                    <td style={{ fontWeight: '600' }}>{row.pr_auc}</td>
                    <td style={{ fontWeight: '700', color: 'var(--accent)' }}>{row.expected_cost}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* Removed Threshold and Confusion Matrix sections per UI request */}
    </div>
  );
};
