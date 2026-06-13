import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MicrosoftIQProofPanel } from "../components/MicrosoftIQProofPanel";

describe("MicrosoftIQProofPanel", () => {
  it("renders Microsoft IQ proof details and copy action", () => {
    render(
      <MicrosoftIQProofPanel
        iqStatus={{
          selected_iq_layer: "Foundry IQ",
          active_provider: "FoundryIQLocalAdapter",
          foundry_iq_label: "Foundry IQ Local Adapter Mode",
          proof_level: "local_demo_fallback",
          live_services: {
            azure_ai_search: false,
            azure_openai: false
          },
          compliance_status: "ready_for_demo",
          honest_limitation: "Azure quota is 0, so this demo uses local Foundry IQ adapter mode.",
          judge_explanation: "This project mirrors Foundry IQ architecture locally."
        }}
        readiness={{ checks: { azure_ai_search_configured: false, azure_openai_configured: false } }}
        demoReport={{
          grounding_summary: {
            source_types: ["local_foundry_iq_adapter"],
            citations_count: 3
          }
        }}
        onCopy={vi.fn()}
      />
    );

    expect(screen.getByText("Local adapter mode with citations and permission-aware metadata")).toBeInTheDocument();
    expect(screen.getByText("Foundry IQ Local Adapter")).toBeInTheDocument();
    expect(screen.getByText("Foundry IQ")).toBeInTheDocument();
    expect(screen.getByText("Local Knowledge Index")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /copy iq/i })).toBeInTheDocument();
  });
});
