import sqlite3
from pathlib import Path

from db.repositories.dashboard_repository import InMemoryDashboardRepository
from ml_pipeline.artifacts import load_active_model_context
from models.audit import AuditEntry
from models.evaluation import EvaluationMetric, ModelComparisonRow, ThresholdCostPoint
from models.review import ReviewItem
from models.settings import SettingsItem, SettingsSection
from models.transaction import TransactionDetail, TransactionListItem
from paths import BASE_DIR


class SQLiteAppRepository:
    def __init__(self, database_path: str | Path | None = None) -> None:
        self.dashboard = InMemoryDashboardRepository()
        self.database_path = Path(database_path) if database_path is not None else BASE_DIR / "ai-risk-manager.db"
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    merchant TEXT NOT NULL,
                    category TEXT NOT NULL,
                    risk_score TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    recommended_action TEXT NOT NULL,
                    review_status TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS review_outcomes (
                    transaction_id TEXT PRIMARY KEY,
                    reviewer_outcome TEXT NOT NULL
                )
                """
            )

            existing = connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
            if existing == 0:
                connection.executemany(
                    """
                    INSERT INTO transactions (
                        id, timestamp, amount, merchant, category, risk_score, risk_level,
                        recommended_action, review_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            "TX1001",
                            "2026-08-29 14:31:28",
                            "₹8,200",
                            "M103",
                            "electronics",
                            "87%",
                            "HIGH",
                            "Manual Review",
                            "Pending",
                        ),
                        (
                            "TX1002",
                            "2026-08-29 14:29:11",
                            "₹1,200",
                            "M204",
                            "grocery",
                            "21%",
                            "LOW",
                            "Approve",
                            "Closed",
                        ),
                        (
                            "TX1003",
                            "2026-08-29 14:28:04",
                            "₹5,600",
                            "M317",
                            "travel",
                            "61%",
                            "MEDIUM",
                            "Verification",
                            "Pending",
                        ),
                    ],
                )
                connection.executemany(
                    "INSERT OR IGNORE INTO review_outcomes (transaction_id, reviewer_outcome) VALUES (?, ?)",
                    [
                        ("TX1001", "Pending"),
                        ("TX1003", "Pending"),
                    ],
                )

    def list_transactions(self) -> list[TransactionListItem]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM transactions ORDER BY timestamp DESC"
            ).fetchall()

        return [
            TransactionListItem(
                id=row["id"],
                timestamp=row["timestamp"],
                amount=row["amount"],
                merchant=row["merchant"],
                category=row["category"],
                risk_score=row["risk_score"],
                risk_level=row["risk_level"],
                recommended_action=row["recommended_action"],
                review_status=row["review_status"],
            )
            for row in rows
        ]

    def get_transaction(self, transaction_id: str) -> TransactionDetail:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM transactions WHERE id = ?",
                (transaction_id,),
            ).fetchone()

        if row is None:
            fallback = self.list_transactions()[0]
            row = {
                "id": fallback.id,
                "timestamp": fallback.timestamp,
                "amount": fallback.amount,
                "merchant": fallback.merchant,
                "category": fallback.category,
                "risk_score": fallback.risk_score,
                "risk_level": fallback.risk_level,
                "recommended_action": fallback.recommended_action,
                "review_status": fallback.review_status,
            }

        return TransactionDetail(
            id=row["id"],
            timestamp=row["timestamp"],
            amount=row["amount"],
            merchant=row["merchant"],
            category=row["category"],
            risk_score=row["risk_score"],
            risk_level=row["risk_level"],
            recommended_action=row["recommended_action"],
            review_status=row["review_status"],
            signals=[
                "Transaction amount is unusually high",
                "Recent transaction velocity is elevated",
                "Behavior differs from historical pattern",
            ],
            historical_context=[
                ("Transactions", "42"),
                ("Average amount", "₹1,850"),
                ("Last 24h", "7 transactions"),
                ("Typical velocity", "1-2/day"),
            ],
        )

    def list_reviews(self) -> list[ReviewItem]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM transactions
                WHERE review_status != 'Closed'
                ORDER BY timestamp DESC
                """
            ).fetchall()

        return [
            ReviewItem(
                transaction_id=row["id"],
                score=row["risk_score"],
                amount=row["amount"],
                recommendation=row["recommended_action"],
                status=row["review_status"],
            )
            for row in rows
        ]

    def record_review(self, transaction_id: str, outcome: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE transactions SET review_status = ? WHERE id = ?",
                (outcome, transaction_id),
            )
            connection.execute(
                "INSERT INTO review_outcomes (transaction_id, reviewer_outcome) VALUES (?, ?) "
                "ON CONFLICT(transaction_id) DO UPDATE SET reviewer_outcome = excluded.reviewer_outcome",
                (transaction_id, outcome),
            )

    def evaluation_metrics(self) -> list[EvaluationMetric]:
        return [
            EvaluationMetric(label="Precision", value="91.2%"),
            EvaluationMetric(label="Recall", value="78.6%"),
            EvaluationMetric(label="F1", value="84.4%"),
            EvaluationMetric(label="PR-AUC", value="89.1%"),
            EvaluationMetric(label="ROC-AUC", value="96.2%"),
        ]

    def threshold_cost_points(self) -> list[ThresholdCostPoint]:
        return [
            ThresholdCostPoint(threshold="0.20", cost="₹7,540"),
            ThresholdCostPoint(threshold="0.40", cost="₹5,120"),
            ThresholdCostPoint(threshold="0.60", cost="₹3,180"),
            ThresholdCostPoint(threshold="0.72", cost="₹2,940"),
            ThresholdCostPoint(threshold="0.85", cost="₹3,610"),
        ]

    def model_comparison(self) -> list[ModelComparisonRow]:
        return [
            ModelComparisonRow(
                model_name="Logistic Regression",
                precision="86.4%",
                recall="72.1%",
                f1="78.7%",
                pr_auc="83.0%",
                expected_cost="₹3,840",
            ),
            ModelComparisonRow(
                model_name="Boosted Tree",
                precision="91.2%",
                recall="78.6%",
                f1="84.4%",
                pr_auc="89.1%",
                expected_cost="₹2,940",
            ),
        ]

    def confusion_matrix(self) -> dict[str, dict[str, str]]:
        return {
            "pred_legit": {"actual_legit": "TN 1,240", "actual_fraud": "FN 83"},
            "pred_risk": {"actual_legit": "FP 56", "actual_fraud": "TP 301"},
        }

    def audit_entries(self) -> list[AuditEntry]:
        return [
            AuditEntry(
                timestamp="2026-08-29 14:31:30",
                transaction_id="TX1001",
                model_version="ai-risk-manager-v1",
                score="0.87",
                threshold="0.72",
                decision="REVIEW",
                reviewer_outcome="Pending",
            ),
            AuditEntry(
                timestamp="2026-08-29 14:28:05",
                transaction_id="TX1003",
                model_version="ai-risk-manager-v1",
                score="0.61",
                threshold="0.72",
                decision="VERIFY",
                reviewer_outcome="Pending",
            ),
        ]

    def settings(self) -> list[SettingsSection]:
        model_context = load_active_model_context()
        return [
            SettingsSection(
                title="Model",
                items=[
                    SettingsItem(label="Version", value=model_context["model_version"]),
                    SettingsItem(label="Active model", value=model_context["model_name"]),
                    SettingsItem(label="MLflow run", value=model_context["run_name"]),
                    SettingsItem(label="Run ID", value=model_context["run_id"]),
                    SettingsItem(label="Scikit-learn", value=model_context["sklearn_version"]),
                ],
            ),
            SettingsSection(
                title="Decision Policy",
                items=[
                    SettingsItem(label="Review threshold", value="0.72"),
                    SettingsItem(label="Why this model", value=model_context["training_summary"]),
                ],
            ),
            SettingsSection(
                title="Cost Assumptions",
                items=[
                    SettingsItem(label="False positive", value="₹20"),
                    SettingsItem(label="False negative", value="₹500"),
                    SettingsItem(label="Manual review", value="₹10"),
                ],
            ),
        ]


class InMemoryAppRepository(SQLiteAppRepository):
    def __init__(self) -> None:
        super().__init__(database_path=str(BASE_DIR / ".inmemory_compat.db"))


app_repository = SQLiteAppRepository()
