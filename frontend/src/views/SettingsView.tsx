import React, { useEffect, useState } from 'react';
import type { CsvUploadSummary, ModelTestResult, SettingsData } from '../types';
import { fetchSettings, testModelInput, uploadCsvTestData } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { Upload, Play, CheckCircle2, AlertTriangle } from 'lucide-react';

interface SettingsViewProps {
  initialSandbox?: boolean;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ initialSandbox = false }) => {
  const [data, setData] = useState<SettingsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // CSV Upload State
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [csvUploading, setCsvUploading] = useState<boolean>(false);
  const [csvSummary, setCsvSummary] = useState<CsvUploadSummary | null>(null);
  const [csvError, setCsvError] = useState<string | null>(null);

  // Model Sandbox Form State
  const [formData, setFormData] = useState({
    step: 6,
    type: 'TRANSFER',
    amount: 9100,
    oldbalanceOrg: 6000,
    newbalanceOrig: 1200,
    oldbalanceDest: 400,
    newbalanceDest: 9500,
  });
  const [testResult, setTestResult] = useState<ModelTestResult | null>(null);
  const [testingModel, setTestingModel] = useState<boolean>(false);
  const [testError, setTestError] = useState<string | null>(null);

  useEffect(() => {
    fetchSettings()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    if (initialSandbox) {
      const el = document.getElementById('sandbox-section');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  }, [initialSandbox]);

  const handleCsvUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!csvFile) return;
    setCsvUploading(true);
    setCsvError(null);
    setCsvSummary(null);

    try {
      const res = await uploadCsvTestData(csvFile);
      setCsvSummary(res);
    } catch (err: any) {
      setCsvError(err.message || 'CSV upload failed');
    } finally {
      setCsvUploading(false);
    }
  };

  const handleModelTest = async (e: React.FormEvent) => {
    e.preventDefault();
    setTestingModel(true);
    setTestError(null);
    setTestResult(null);

    try {
      const res = await testModelInput(formData);
      setTestResult(res);
    } catch (err: any) {
      setTestError(err.message || 'Model test failed');
    } finally {
      setTestingModel(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="glass-panel" style={{ textAlign: 'center', padding: '60px' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading model metadata & settings...</p>
      </div>
    );
  }

  const { model_context } = data;

  return (
    <div>
      {/* Active Model Specs Header */}
      <section className="glass-panel">
        <div className="page-head">
          <div>
            <h2>Model Configuration & Metadata</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '2px' }}>
              Runtime specifications read directly from active MLflow experiment runs.
            </p>
          </div>
        </div>

        <div className="stat-grid">
          <div className="stat-card">
            <strong>{model_context.model_version}</strong>
            <span>Model Version</span>
          </div>
          <div className="stat-card">
            <strong>{model_context.run_name}</strong>
            <span>MLflow Run</span>
          </div>
          <div className="stat-card">
            <strong>{model_context.experiment}</strong>
            <span>Experiment</span>
          </div>
          <div className="stat-card">
            <strong>{model_context.sklearn_version}</strong>
            <span>Scikit-Learn</span>
          </div>
        </div>

        <div className="info-callout">
          <p style={{ color: 'var(--text-main)', fontSize: '0.88rem' }}>
            <strong>Model Selection Rationale:</strong> Boosted Tree Classifier selected for superior PR-AUC performance and lower expected verification cost compared to the baseline model.
          </p>
        </div>
      </section>

      {/* CSV Dataset Upload Tool */}
      <section className="glass-panel">
        <div className="page-head">
          <div>
            <h3>Upload CSV Test Dataset</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '2px' }}>
              Upload PaySim formatted CSV files to stream, validate, and score transactions in bulk.
            </p>
          </div>
        </div>

        <form onSubmit={handleCsvUpload} style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            type="file"
            accept=".csv,text/csv"
            className="file-input"
            onChange={(e) => setCsvFile(e.target.files ? e.target.files[0] : null)}
          />
          <button className="btn btn-primary" type="submit" disabled={csvUploading || !csvFile}>
            <Upload size={16} /> {csvUploading ? 'Validating & Streaming...' : 'Upload CSV'}
          </button>
        </form>

        {csvError && (
          <div className="alert-box-danger">
            <AlertTriangle size={16} style={{ marginRight: '6px', verticalAlign: 'middle' }} /> {csvError}
          </div>
        )}

        {csvSummary && (
          <div style={{ marginTop: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent)', marginBottom: '12px', fontWeight: '600' }}>
              <CheckCircle2 size={18} /> CSV Dataset Successfully Validated & Processed!
            </div>
            <div className="stat-grid">
              <div className="stat-card">
                <strong>{csvSummary.rows}</strong>
                <span>Total Transactions</span>
              </div>
              <div className="stat-card">
                <strong>{csvSummary.fraud_rate}</strong>
                <span>Dataset Fraud Rate</span>
              </div>
              <div className="stat-card">
                <strong>{csvSummary.columns.length}</strong>
                <span>Validated Columns</span>
              </div>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '10px' }}>
              High-risk transactions extracted from the dataset have been sent directly to your Dashboard and Review Queue.
            </p>
          </div>
        )}
      </section>

      {/* Real-Time Interactive Model Sandbox */}
      <section className="glass-panel" id="sandbox-section">
        <div className="page-head">
          <div>
            <h3>Test Model with Custom User Input Data</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '2px' }}>
              Simulate individual payment transactions to test model predictions and risk reasons in real time.
            </p>
          </div>
        </div>

        <form onSubmit={handleModelTest}>
          {/* Section 1: Transaction Basics */}
          <div style={{ marginBottom: '16px' }}>
            <h4 style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '10px' }}>
              Transaction Parameters
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div className="field-box">
                <label>Step (1 Step = 1 Hour)</label>
                <input
                  type="number"
                  value={formData.step}
                  onChange={(e) => setFormData({ ...formData, step: parseInt(e.target.value) || 1 })}
                  required
                />
              </div>
              <div className="field-box">
                <label>Transaction Type</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                >
                  <option value="TRANSFER">TRANSFER</option>
                  <option value="CASH_OUT">CASH_OUT</option>
                  <option value="PAYMENT">PAYMENT</option>
                  <option value="DEBIT">DEBIT</option>
                  <option value="CASH_IN">CASH_IN</option>
                </select>
              </div>
              <div className="field-box">
                <label>Amount (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                  required
                />
              </div>
            </div>
          </div>

          {/* Section 2: Account Balances */}
          <div>
            <h4 style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '10px' }}>
              Origin & Destination Balances
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div className="field-box">
                <label>Old Balance (Origin)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.oldbalanceOrg}
                  onChange={(e) => setFormData({ ...formData, oldbalanceOrg: parseFloat(e.target.value) || 0 })}
                  required
                />
              </div>
              <div className="field-box">
                <label>New Balance (Origin)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.newbalanceOrig}
                  onChange={(e) => setFormData({ ...formData, newbalanceOrig: parseFloat(e.target.value) || 0 })}
                  required
                />
              </div>
              <div className="field-box">
                <label>Old Balance (Destination)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.oldbalanceDest}
                  onChange={(e) => setFormData({ ...formData, oldbalanceDest: parseFloat(e.target.value) || 0 })}
                  required
                />
              </div>
              <div className="field-box">
                <label>New Balance (Destination)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.newbalanceDest}
                  onChange={(e) => setFormData({ ...formData, newbalanceDest: parseFloat(e.target.value) || 0 })}
                  required
                />
              </div>
            </div>
          </div>

          <button className="btn btn-primary" type="submit" disabled={testingModel} style={{ marginTop: '20px' }}>
            <Play size={16} /> {testingModel ? 'Running Inference...' : 'Test Model'}
          </button>
        </form>

        {testError && (
          <div className="alert-box-danger">
            {testError}
          </div>
        )}

        {testResult && (
          <div className="info-callout" style={{ marginTop: '24px' }}>
            <h4 style={{ color: 'var(--text-main)', marginBottom: '16px', fontSize: '1.1rem' }}>
              Model Prediction Results {testResult.transaction_id && `(Saved as ${testResult.transaction_id})`}
            </h4>

            <div className="stat-grid">
              <div className="stat-card">
                <strong>{(testResult.risk_score * 100).toFixed(1)}%</strong>
                <span>Calculated Risk Score</span>
              </div>
              <div className="stat-card">
                <StatusBadge status={testResult.risk_level} />
                <span style={{ display: 'block', marginTop: '6px' }}>Calculated Risk Level</span>
              </div>
              <div className="stat-card">
                <strong>{testResult.threshold}</strong>
                <span>Decision Threshold</span>
              </div>
              <div className="stat-card">
                <strong>{testResult.recommended_action}</strong>
                <span>Recommended Action</span>
              </div>
            </div>

            <div style={{ marginTop: '16px' }}>
              <p style={{ color: 'var(--text-main)', marginBottom: '8px' }}>
                Final System Policy Decision: <strong>{testResult.decision}</strong>
              </p>
              <h5 style={{ color: 'var(--text-muted)', marginBottom: '8px', fontSize: '0.8rem', textTransform: 'uppercase' }}>
                Extracted Model Risk Signals:
              </h5>
              <ul style={{ paddingLeft: '20px', color: 'var(--danger)' }}>
                {testResult.reasons.map((reason, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>
                    {reason}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </section>
    </div>
  );
};
