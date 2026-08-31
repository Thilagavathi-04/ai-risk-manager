export interface DashboardStat {
  label: string;
  value: string;
}

export interface TransactionCard {
  id: string;
  amount: string;
  risk_level: string;
  risk_score: string;
  action: string;
}

export interface DashboardSummary {
  page_title: string;
  stats: DashboardStat[];
  recent_transactions: TransactionCard[];
}

export interface TransactionListItem {
  id: string;
  timestamp: string;
  amount: string;
  merchant: string;
  category: string;
  risk_score: string;
  risk_level: string;
  recommended_action: string;
  review_status: string;
}

export interface TransactionDetail extends TransactionListItem {
  signals: string[];
  historical_context: [string, string][];
}

export interface ReviewItem {
  transaction_id: string;
  score: string;
  amount: string;
  recommendation: string;
  status: string;
}

export interface EvaluationMetric {
  label: string;
  value: string;
}

export interface ThresholdCostPoint {
  threshold: string;
  cost: string;
}

export interface ModelComparisonRow {
  model_name: string;
  precision: string;
  recall: string;
  f1: string;
  pr_auc: string;
  expected_cost: string;
}

export interface EvaluationData {
  metrics: EvaluationMetric[];
  threshold_cost_points: ThresholdCostPoint[];
  model_comparison: ModelComparisonRow[];
  confusion_matrix: Record<string, Record<string, string>>;
  selected_threshold: string;
}

export interface AuditEntry {
  timestamp: string;
  transaction_id: string;
  model_version: string;
  score: string;
  threshold: string;
  decision: string;
  reviewer_outcome: string;
}

export interface SettingsItem {
  label: string;
  value: string;
}

export interface SettingsSection {
  title: string;
  items: SettingsItem[];
}

export interface ModelContext {
  model_version: string;
  model_name: string;
  run_name: string;
  run_id: string;
  experiment: string;
  sklearn_version: string;
  artifact_uri: string;
  status: string;
  user: string;
  training_summary: string;
}

export interface SettingsData {
  sections: SettingsSection[];
  model_context: ModelContext;
}

export interface CsvUploadSummary {
  rows: string;
  columns: string[];
  fraud_rate: string;
  target: string;
}

export interface ModelTestResult {
  transaction_id?: string;
  risk_score: number;
  risk_level: string;
  recommended_action: string;
  threshold: number;
  decision: string;
  reasons: string[];
}
