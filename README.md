# AI Risk Manager

**AI Risk Manager** is an enterprise-grade, defensive payment risk detection engine and merchant workflow system. It evaluates mobile money transactions in real time, surfaces human-interpretable risk signals, supports analyst review workflows, and tracks decision audit logs.

---

## 🌟 Key Features & Capabilities

- **Interactive Merchant Analytics Dashboard**:
  - Real-time KPI stat cards for total volume, high-risk flags, review queue depth, and model precision.
  - Interactive **24-Hour Transaction Volume & Fraud Velocity** SVG chart with bar hover tooltips.
  - **Risk Classification Share**: Donut chart detailing Low Risk (`92.4%`), Medium Risk (`6.1%`), and High Risk (`1.5%`).
  - **Payment Method Breakdown**: Progress distribution analyzing `TRANSFER`, `CASH_OUT`, `PAYMENT`, `CASH_IN`, and `DEBIT` volume and fraud rates.
  - **Recent Transactions Feed**: Filterable by `All`, `High Risk Only`, and `Pending Review`.

- **Modern Left Sidebar React SPA**:
  - Built with **React 18**, **Vite**, **TypeScript**, **Lucide Icons**, and **Plus Jakarta Sans** typography.
  - Left sidebar navigation with active pill indicators and system theme switcher (**Light & Dark Modes**).

- **Human-in-the-Loop Analyst Review Queue**:
  - Flagged transactions are routed directly to analysts for decision verification (`Approve`, `Decline`, `Escalate`).

- **Immutable Decision Audit Log**:
  - Captures timestamps, model versions, thresholds, risk scores, and analyst outcomes into SQLite persistence.

- **Model Configuration & Test Sandbox (`Model & Test Data`)**:
  - Runtime specs read directly from active MLflow experiment runs and artifact bundles.
  - **Chunked CSV Stream Validator**: Ingests test datasets without memory spikes.
  - **Interactive Model Sandbox**: Allows instant real-time scoring of custom transaction inputs with extracted risk signals.

---

## 🏗️ Architecture Stack

The project combines three decoupled layers:

1. **Frontend SPA Layer**: React 18, Vite, TypeScript, Lucide Icons, Plus Jakarta Sans font, CSS variables for Light & Dark mode themes.
2. **REST API & Backend Layer**: Python 3.12, FastAPI, CORS Middleware, JSON REST API endpoints (`/api/v1/*`).
3. **Machine Learning & Persistence Layer**: `scikit-learn` (HistGradientBoostingClassifier), `MLflow` experiment tracking, `joblib` artifact serialization, SQLite (`ai-risk-manager.db`) repository layer.

---

## 📂 Repository Layout

- [`main.py`](main.py): FastAPI app factory, CORS middleware, REST routers, and static SPA mounting.
- [`routes/v1/api.py`](routes/v1/api.py): REST API endpoints for `/dashboard`, `/transactions`, `/reviews`, `/evaluation`, `/audit`, `/settings/test-data`, and `/settings/test-model`.
- [`frontend/`](frontend): React 18 + Vite + TypeScript application source code.
  - `src/components/Sidebar.tsx`: Left sidebar navigation layout.
  - `src/views/DashboardView.tsx`: Analytics dashboard with interactive SVG charts.
  - `src/views/TransactionsView.tsx`: Searchable transaction queue & inspection drawer modal.
  - `src/views/ReviewsView.tsx`: Analyst review queue.
  - `src/views/EvaluationView.tsx`: Model metrics, cost curve, & comparison matrix.
  - `src/views/AuditView.tsx`: Immutable decision audit log.
  - `src/views/SettingsView.tsx`: Model metadata, CSV validator, & interactive sandbox.
  - `src/services/api.ts`: API client connecting to FastAPI REST endpoints.
- [`db/repositories/app_repository.py`](db/repositories/app_repository.py): SQLite repository layer managing `ai-risk-manager.db`.
- [`ml_pipeline`](ml_pipeline): Pipeline for training, feature extraction, evaluation, and inference.
- [`MODEL_DETAILS.md`](MODEL_DETAILS.md): Comprehensive model specifications and held-out test evaluation metrics.
- [`tests`](tests): Comprehensive Pytest suite covering all API endpoints and repository logic.

---

## 🚀 How to Run the Application

### Prerequisites
- Python 3.12+
- `uv` package manager (`pip install uv`)
- Node.js 18+ & `npm`

---

### Option A: Concurrent Development (React Dev Server + FastAPI)

1. **Start the FastAPI Backend**:
   ```bash
   uv sync --python 3.12
   uv run ai-risk-manager
   # Server runs at http://localhost:8000
   ```

2. **Start the React Frontend** (in a separate terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   # React app runs at http://localhost:5173
   ```

---

### Option B: Unified Production Server (FastAPI serving compiled React SPA)

1. **Build the React Production Bundle**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Launch the FastAPI Server**:
   ```bash
   uv run ai-risk-manager
   ```

3. **Open in Browser**:
   - React SPA: **[http://localhost:8000/app](http://localhost:8000/app)**
   - Interactive Swagger API Docs: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 🤖 Model Performance & Rationale

The active production model is selected from a **ten-model MLflow sweep** over XGBoost, LightGBM, CatBoost, HistGradientBoosting, Random Forest, Extra Trees, Balanced Random Forest, Logistic Regression, MLP Neural Network, and Isolation Forest. Each model is trained on the same temporal split, tracked in MLflow, and compared on validation/test metrics before promotion to production.

The selected model for the current run is **LightGBM**.

For a more detailed breakdown of the sweep and runtime metadata, see [`MODEL_DETAILS.md`](MODEL_DETAILS.md) and the Settings screen in the app.

The MLflow UI reads from the repo-root `mlruns/` store. If you start it from the frontend folder, use `uv run mlflow ui --backend-store-uri ../mlruns`.

---

## 🧪 Automated Testing

Run the full validation test suite (16 unit & integration tests):

```bash
uv run pytest
```
