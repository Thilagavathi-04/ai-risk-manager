import type {
  AuditEntry,
  CsvUploadSummary,
  DashboardSummary,
  EvaluationData,
  ModelTestResult,
  ReviewItem,
  SettingsData,
  TransactionDetail,
  TransactionListItem,
} from '../types';

const API_BASE = 'http://localhost:8000/api/v1';

export const fetchHealth = async (): Promise<boolean> => {
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    return data.status === 'ok';
  } catch {
    return false;
  }
};

export const fetchDashboard = async (timeframe: '24h' | '7d' | '30d' = '24h'): Promise<DashboardSummary> => {
  const res = await fetch(`${API_BASE}/dashboard?timeframe=${encodeURIComponent(timeframe)}`);
  if (!res.ok) throw new Error('Failed to fetch dashboard data');
  return res.json();
};

export const fetchTransactions = async (): Promise<TransactionListItem[]> => {
  const res = await fetch(`${API_BASE}/transactions`);
  if (!res.ok) throw new Error('Failed to fetch transactions');
  return res.json();
};

export const fetchTransactionDetail = async (id: string): Promise<TransactionDetail> => {
  const res = await fetch(`${API_BASE}/transactions/${id}`);
  if (!res.ok) throw new Error('Failed to fetch transaction detail');
  return res.json();
};

export const fetchReviews = async (): Promise<ReviewItem[]> => {
  const res = await fetch(`${API_BASE}/reviews`);
  if (!res.ok) throw new Error('Failed to fetch reviews');
  return res.json();
};

export const submitReview = async (id: string, outcome: string): Promise<TransactionDetail> => {
  const res = await fetch(`${API_BASE}/reviews/${id}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reviewer_outcome: outcome }),
  });
  if (!res.ok) throw new Error('Failed to submit review outcome');
  return res.json();
};

export const fetchEvaluation = async (): Promise<EvaluationData> => {
  const res = await fetch(`${API_BASE}/evaluation`);
  if (!res.ok) throw new Error('Failed to fetch evaluation metrics');
  return res.json();
};

export const fetchAudit = async (): Promise<AuditEntry[]> => {
  const res = await fetch(`${API_BASE}/audit`);
  if (!res.ok) throw new Error('Failed to fetch audit log');
  return res.json();
};

export const fetchSettings = async (): Promise<SettingsData> => {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
};

export const uploadCsvTestData = async (file: File): Promise<CsvUploadSummary> => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/settings/test-data`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'CSV upload failed');
  }
  return res.json();
};

export const testModelInput = async (payload: {
  step: number;
  type: string;
  amount: number;
  oldbalanceOrg: number;
  newbalanceOrig: number;
  oldbalanceDest: number;
  newbalanceDest: number;
}): Promise<ModelTestResult> => {
  const res = await fetch(`${API_BASE}/settings/test-model`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Model test failed');
  }
  return res.json();
};
