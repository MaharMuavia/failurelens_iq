import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MicrosoftIQProofPanel } from "../components/MicrosoftIQProofPanel";

describe("MicrosoftIQProofPanel", () => {
  it("renders Microsoft IQ proof details and copy action", () => {
    render(
      <MicrosoftIQProofPanel
        iqStatus={{
          selected_iq_layer: "Foundry IQ",
          active_provider: "LocalIQProvider",
          proof_level: "local_demo_fallback",
          live_services: {
            azure_ai_search: false,
            azure_openai: false
          },
          compliance_status: "ready_for_demo",
          honest_limitation: "Demo mode uses local grounding; Azure AI Search is not live.",
          judge_explanation: "FailureLens IQ satisfies the Microsoft IQ requirement."
        }}
        readiness={{ checks: { azure_ai_search_configured: false, azure_openai_configured: false } }}
        demoReport={{
          grounding_summary: {
            source_types: ["local_demo_grounding"],
            citations_count: 3
          }
        }}
        onCopy={vi.fn()}
      />
    );

    expect(screen.getByText("Foundry IQ grounded retrieval proof")).toBeInTheDocument();
    expect(screen.getByText("Local Demo Fallback")).toBeInTheDocument();
    expect(screen.getByText("LocalIQProvider")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /copy iq compliance summary/i })).toBeInTheDocument();
  });
});
