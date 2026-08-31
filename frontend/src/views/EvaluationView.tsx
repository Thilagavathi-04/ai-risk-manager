import React, { useEffect, useState } from 'react';
import type { EvaluationData } from '../types';
import { fetchEvaluation } from '../services/api';
import { TrendingUp, Layers, GitCompare } from 'lucide-react';

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
              Held-out test set metrics for the active HistGradientBoostingClassifier.
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
          Comparing the active Boosted Tree against the Logistic Regression baseline.
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
              {data.model_comparison.map((row, idx) => (
                <tr key={idx} style={{ background: row.model_name.includes('Boosted') ? 'rgba(2, 132, 199, 0.08)' : 'transparent' }}>
                  <td style={{ fontWeight: '700', color: row.model_name.includes('Boosted') ? 'var(--primary)' : 'var(--text-main)' }}>
                    {row.model_name} {row.model_name.includes('Boosted') && '(Active)'}
                  </td>
                  <td style={{ fontWeight: '600' }}>{row.precision}</td>
                  <td style={{ fontWeight: '600' }}>{row.recall}</td>
                  <td style={{ fontWeight: '600' }}>{row.f1}</td>
                  <td style={{ fontWeight: '600' }}>{row.pr_auc}</td>
                  <td style={{ fontWeight: '700', color: 'var(--accent)' }}>{row.expected_cost}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <section className="glass-panel">
          <div className="page-head">
            <h3>
              <TrendingUp size={18} color="var(--accent)" style={{ marginRight: '8px', verticalAlign: 'middle' }} />
              Threshold vs Expected Cost Curve
            </h3>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Decision Threshold</th>
                  <th>Expected Operational Cost</th>
                </tr>
              </thead>
              <tbody>
                {data.threshold_cost_points.map((pt, idx) => (
                  <tr key={idx} style={{ background: pt.threshold === data.selected_threshold ? 'rgba(16, 185, 129, 0.1)' : 'transparent' }}>
                    <td style={{ fontWeight: '700' }}>
                      {pt.threshold} {pt.threshold === data.selected_threshold && '(Selected Optimal)'}
                    </td>
                    <td style={{ fontWeight: '700', color: 'var(--accent)' }}>{pt.cost}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="glass-panel">
          <div className="page-head">
            <h3>
              <Layers size={18} color="var(--primary)" style={{ marginRight: '8px', verticalAlign: 'middle' }} />
              Test Confusion Matrix
            </h3>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Prediction</th>
                  <th>Actual Legit</th>
                  <th>Actual Fraud</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ fontWeight: '700', color: 'var(--text-muted)' }}>Predicted Legit</td>
                  <td style={{ fontWeight: '700', color: 'var(--accent)' }}>{data.confusion_matrix.pred_legit.actual_legit}</td>
                  <td style={{ fontWeight: '700', color: 'var(--danger)' }}>{data.confusion_matrix.pred_legit.actual_fraud}</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: '700', color: 'var(--text-muted)' }}>Predicted Risk</td>
                  <td style={{ fontWeight: '700', color: 'var(--warning)' }}>{data.confusion_matrix.pred_risk.actual_legit}</td>
                  <td style={{ fontWeight: '700', color: 'var(--primary)' }}>{data.confusion_matrix.pred_risk.actual_fraud}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
};
