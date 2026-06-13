import React, { Component, type ErrorInfo, type ReactNode } from "react";
import { API_BASE } from "../api/client";
import { demoErrorMessage, VIDEO_DEMO_MODE } from "../config/demoMode";

const DEBUG_LOGS = import.meta.env.VITE_DEBUG_LOGS === "true";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    if (DEBUG_LOGS) {
      console.error("ErrorBoundary caught an error:", error, errorInfo);
    }
  }

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: "2rem",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "100vh",
          backgroundColor: "#f8fafc",
          color: "#334155",
          fontFamily: "Inter, system-ui, sans-serif"
        }}>
          <h1 style={{ color: "#dc2626" }}>Something went wrong in the demo dashboard.</h1>
          <p style={{ margin: "1rem 0" }}>
            An unexpected client-side error occurred. You can reload the page or check the backend health.
          </p>
          <div style={{ display: "flex", gap: "1rem" }}>
            <button
              onClick={this.handleReload}
              style={{
                padding: "0.5rem 1rem",
                backgroundColor: "#0078d4",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                fontWeight: "bold"
              }}
            >
              Reload
            </button>
            <a
              href={`${API_BASE}/health`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                padding: "0.5rem 1rem",
                backgroundColor: "#ffffff",
                color: "#0078d4",
                border: "1px solid #cbd5e1",
                borderRadius: "4px",
                textDecoration: "none",
                fontWeight: "bold"
              }}
            >
              Check Backend Health
            </a>
          </div>
          {import.meta.env.DEV && !VIDEO_DEMO_MODE && this.state.error && (
            <pre style={{
              marginTop: "2rem",
              padding: "1rem",
              backgroundColor: "#ffffff",
              border: "1px solid #e2e8f0",
              borderRadius: "4px",
              maxWidth: "80%",
              overflowX: "auto",
              color: "#dc2626"
            }}>
              {demoErrorMessage(this.state.error.toString())}
            </pre>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}
export default ErrorBoundary;
