# Production Hardening

This document outlines the security, stability, and architectural enhancements applied to FailureLens IQ to transition it from a hackathon MVP to a hardened, enterprise-ready service.

## Hardening Achievements

### 1. API Security & Authentication
- **Optional API Key Authentication:** Mutation endpoints are protected by `X-API-Key` headers when `ENABLE_AUTH=true`. Exempts `/health` and `/agents` to keep local demo verification frictionless.
- **CORS Hardening:** Enabled dynamic CORS origin configuration via the `CORS_ORIGINS` environment variable. Added safety guards in `production` mode to fail startup if unsafe wildcard origins (`*`) are used with credentials enabled.
- **Security Response Headers:** Applied standard security headers (e.g., `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, default `Cache-Control: no-store`, and a safe `Content-Security-Policy`).

### 2. Stability & DoS Prevention
- **Request Size Limiting:** Custom `MaxBodySizeMiddleware` ASGI middleware caps incoming payload sizes to `MAX_UPLOAD_BYTES` (default 1MB).
- **Rate Limiting:** Lightweight in-memory rate limiting middleware keying by client IP and request path, exempting `/health` and `/agents`.
- **Pydantic Validation Caps:** Added `Field(max_length=...)` validation constraints on model fields in `ExperimentLog` to block memory-exhaustion exploits.

### 3. Storage & Caching
- **Persistent Local Uploads:** Created `ExperimentStore` to atomically persist uploaded experiments to `data/uploads/uploaded_experiments.json`.
- **TTL Demo Caching:** Implemented `DemoCache` to cache `/demo/run` outputs for `DEMO_CACHE_TTL_SECONDS` (default 300s) to limit downstream LLM/Agent costs. Supports overriding via `?force_refresh=true`.

### 4. Code & Build Hardening
- **Route Refactoring:** Moved all endpoints from `main.py` into decoupled routers inside `backend/api/routes/`.
- **Dependency Pinning:** Pinned all Python dependencies inside `requirements.txt` and React frontend dependencies inside `package.json`.
- **Container Healthchecks:** Added container healthchecks to `docker-compose.yml` for backend and frontend services.
- **Frontend Error Boundaries:** Wrapped React application with a custom `ErrorBoundary` component to capture client-side rendering crashes.

---

## Remaining Enterprise Production Requirements

For true production/enterprise deployments, the following components should be replaced with managed cloud services:

1. **Enterprise Identity Provider:**
   Replace the API Key header authentication with OAuth2/OIDC integrated with an identity provider (e.g., Microsoft Entra ID, Auth0, or Azure AD B2C) to support single sign-on (SSO).

2. **Distributed/Database-Backed Rate Limiting:**
   The current rate limiting middleware is in-memory and local to the FastAPI instance. In a load-balanced, multi-instance environment, replace it with a Redis-backed rate limiter (e.g., using `redis-py` or `limits`).

3. **Persistent Managed Storage:**
   Replace local JSON file uploads (`uploaded_experiments.json`) with Cosmos DB or SQL Database storage for horizontal scaling and durability.

4. **Role-Based Access Control (RBAC):**
   Add distinct role assignments (e.g., `Viewer`, `Engineer`, `Manager`, `Auditor`) with fine-grained endpoint authorization scopes.

5. **Audit Logging & SIEM Integration:**
   Route JSON-structured application logs directly to central log sinks (e.g., Azure Monitor Logs, Log Analytics, or Datadog) for anomaly detection and security audit compliance.

6. **Enterprise Deployment Topology:**
   Deploy container images to Azure Container Apps or Azure App Service with auto-scaling rules and private endpoints, isolating backend databases from the public internet.
