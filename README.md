# Goal
Demonstrate how to control deployments and feature availability using a tag + feature flag mechanism, with versioned rollback capability, driven by GitHub Actions pipelines.

## 1. Problem Introduction

- **Why feature flags and tags are critical for CI/CD**
- **Avoiding risky full deployments**
- **How rollback saves downtime in production**

## 2. Architecture & Tools Overview

- **Frontend:** React app reading feature flags from API or Git commit metadata
- **Backend API:** FastAPI service that:

  - Reads current tag/flag from config or Git
  - Exposes `/feature-flags` endpoint

- **Deployment Orchestration:**

  - GitHub Actions workflow triggers
  - Deploy to Kubernetes

- **Versioning & Rollback:**

  - Store configs in Git with version history
  - Use previous commit hash to rollback

## 3. Hands-On Implementation Steps

### Step 1 – Backend Feature Flag API

- FastAPI Express API:

  - Reads flags from `feature-flags.json`
  - Returns current active flags
  - Supports `POST /feature-flags` to update

### Step 2 – Frontend Integration

- React app:

  - Calls `/feature-flags` on load
  - Conditionally renders UI components

### Step 3 – GitHub Actions Workflow

- Workflow triggers on commit to `feature/*` branch
- Updates config file in repo
- Runs deployment pipeline

### Step 4 – Rollback Mechanism

- Pipeline input param for rollback commit hash
- Redeploys previous version from Git history

## 4. Testing & Demo

- Deploy a feature to staging using tag `feature-login-v1`
- Toggle a feature flag to hide/show a UI element
- Rollback to previous commit & verify UI change disappears

## 5. Step-by-Step Guide: FastAPI + React Feature Flags

### Step 1 – Backend: FastAPI Feature Flag API

- Implement a FastAPI router (`/feature-flags`) that reads/writes flags from `feature-flags.json`.
- Example endpoints:
  - `GET /feature-flags`: Returns current flags.
  - `POST /feature-flags`: Updates flags.
- Flags are stored in `feature-flags.json` (e.g. `{ "feature-login": true }`).

### Step 2 – Frontend: React Integration

- On app load, fetch `/feature-flags` from FastAPI backend.
- Store flags in React state/context.
- Conditionally render UI components based on flag values:
  ```jsx
  {flags["feature-login"] && <LoginComponent />}
  ```

### Step 3 – Deployment & GitHub Actions Workflow

- Workflow triggers on commit to `feature/*` branch.
- Updates `feature-flags.json` in repo.
- Runs deployment pipeline (e.g. to Kubernetes).
- Example workflow steps:
  - Checkout code
  - Update flags/config
  - Build & deploy backend/frontend

#### Example GitHub Actions Workflow

### Step 4 – Rollback Mechanism

- Workflow accepts a commit hash for rollback.
- Checks out previous commit, redeploys backend/frontend.
- Flags/configs revert to previous state.

### Step 5 – Testing & Demo

- Deploy a feature to staging using tag (e.g. `feature-login-v1`).
- Toggle a feature flag to show/hide a UI element in React.
- Rollback to previous commit; verify UI change disappears.

---

This guide demonstrates controlling deployments and feature availability using FastAPI, React, and GitHub Actions with feature flags and versioned rollback.