import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { AppProvider } from "./AppContext";

function mockFetch(options: { offlinePrompt?: boolean } = {}) {
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (options.offlinePrompt && url.includes("/prompt/analyze")) {
      throw new Error("backend offline");
    }
    if (url.includes("/health")) {
      return Response.json({ status: options.offlinePrompt ? "offline_mock_preview" : "ok", timestamp: new Date().toISOString() });
    }
    if (url.includes("/iq/status")) {
      return Response.json({
        status: "ready_for_demo",
        active_provider: "FoundryIQLocalAdapter",
        foundry_iq_mode: "local_foundry_iq_adapter",
        live_microsoft_iq: false,
        citations_supported: true,
      });
    }
    if (url.includes("/experiments")) {
      return Response.json({ items: [] });
    }
    if (url.includes("/proof/live-iq")) {
      return Response.json({
        selected_iq_layer: "Foundry IQ",
        proof_level: "configuration_only",
        live_microsoft_iq: false,
        is_live_backend: true,
        is_live_microsoft_iq: false,
        azure_ai_search_configured: false,
        azure_ai_search_used_this_run: false,
        foundry_model_configured: false,
        foundry_model_used_this_run: false,
        active_reasoning_provider: "local",
        active_grounding_provider: "local_iq",
        citations_count: 0,
        grounding_refs: [],
        source_types: [],
        run_id: "",
        trace_ids: [],
        warnings: ["Configuration status only."],
        warning: "Configuration status only.",
        honest_limitation: "Configuration status only.",
      });
    }
    return Response.json({});
  }));
}

function renderApp() {
  return render(
    <AppProvider>
      <App />
    </AppProvider>
  );
}

async function enterGuestChat(user = userEvent.setup()) {
  renderApp();
  await user.click(screen.getByRole("button", { name: /launch demo app/i }));
  await user.click(screen.getByRole("button", { name: /continue as guest reviewer/i }));
  expect(await screen.findByText(/what failed in your ml experiment/i)).toBeInTheDocument();
  return user;
}

describe("FailureLens IQ judge flow", () => {
  beforeEach(() => {
    mockFetch();
  });

  it("landing renders", async () => {
    renderApp();
    expect(await screen.findByText(/learning intelligence from/i)).toBeInTheDocument();
  });

  it("guest sign-in opens chat", async () => {
    await enterGuestChat();
  });

  it("chat sample prompt fills composer", async () => {
    const user = await enterGuestChat();
    await user.click(screen.getByRole("button", { name: /class imbalance bias/i }));
    const composer = screen.getByPlaceholderText(/describe the failed ml experiment/i) as HTMLInputElement;
    expect(composer.value).toContain("minority class F1");
  });

  it("offline warning appears only in offline mode", async () => {
    mockFetch({ offlinePrompt: true });
    const user = await enterGuestChat();
    await user.click(screen.getByRole("button", { name: /class imbalance bias/i }));
    await user.click(screen.getByRole("button", { name: /run analysis/i }));

    expect(await screen.findByText(/Offline Mock Preview — not live submission proof/i, {}, { timeout: 7000 })).toBeInTheDocument();
  }, 10000);

  it("IQ proof page renders proof JSON button", async () => {
    const user = await enterGuestChat();
    await user.click(screen.getByRole("button", { name: /microsoft iq proof/i }));
    expect(await screen.findByRole("button", { name: /copy judge proof json/i })).toBeInTheDocument();
  });
});
