# Product Requirements Document (PRD)

## 1. Product overview

AI Risk Manager is a defensive merchant-risk workflow for payment transactions. It helps identify suspicious transactions, explain the sources of risk, and route borderline cases into a review workflow for human verification.

The product provides a merchant-facing dashboard that presents:

- transaction risk scores
- supporting risk reasons
- model evaluation metrics
- threshold and cost trade-offs
- audit history and reviewer outcomes

## 2. Problem statement

Merchant risk teams need to catch fraud before it creates losses, while avoiding unnecessary friction for legitimate customers. The solution must balance detection quality against operational cost.

The system should therefore:

- identify risky transactions early
- explain why a decision was reached
- support verification rather than blanket blocking
- expose the business cost of false positives and false negatives
- provide transparent model metrics and artifact provenance

## 3. Goals

### Primary goals

- build a working payment-risk detector
- score a transaction with a probability-based risk signal
- compare a baseline model against a stronger model
- track and explain decision reasons
- support manual review and audit
- surface the selected model and the reason it was chosen

### Secondary goals

- provide a browser-based dashboard
- keep the system understandable and explainable
- make the app runnable in a local development environment
- integrate artifact and MLflow metadata into the product UI

## 4. Non-goals

The project does not aim to:

- provide misuse guidance
- evade payment controls
- infer unsafe bypass techniques
- automate irreversible customer blocking
- claim production fraud performance from synthetic demo data

## 5. Target users

### Primary

- merchant risk analyst
- operations/compliance reviewer

### Secondary

- support or verification staff
- technical stakeholders reviewing model behavior

## 6. Key user stories

- As a risk analyst, I want to see risky transactions prioritized.
- As a reviewer, I want to understand why a score is high.
- As an operator, I want to know the effect of threshold changes.
- As a stakeholder, I want to see the active model and its metadata.
- As an engineer, I want the app to use saved model artifacts and MLflow metadata.

## 7. Functional requirements

### Core app flow

1. Load transaction data.
2. Score the transaction with the trained model.
3. Return a risk score and recommendation.
4. Show supporting risk reasons.
5. Save reviewer decisions and audit trail entries.

### Dashboard requirements

- transaction list
- review queue
- high-risk summary stats
- model metrics overview
- threshold/cost diagnostics
- settings page with model metadata and validation tools

### Model transparency requirements

- display the active model and model version
- read metadata from the saved artifact bundle and MLflow run metadata
- explain why the chosen model is preferred over the baseline

## 8. Data strategy

The demo uses the public PaySim1 synthetic dataset and stores model logs and artifacts locally with MLflow. The app is designed to demonstrate the workflow rather than represent production-scale real payment fraud data.

## 9. Acceptance criteria

The project is considered successful when:

- the app runs locally with FastAPI and the configured environment
- the dashboard and review flow operate without in-memory-only state loss
- the model artifact bundle loads successfully at runtime
- the settings page shows active model metadata
- a user can test a transaction by inputting data in the UI
- the documentation clearly explains the chosen model and the trade-offs
- the validation suite passes end to end
