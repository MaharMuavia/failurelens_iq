import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MicrosoftIQProofPanel } from "./MicrosoftIQProofPanel";

describe("MicrosoftIQProofPanel component", () => {
  it("renders honest local fallback status", () => {
    render(
      <MicrosoftIQProofPanel
        iqStatus={{
          selected_iq_layer: "Foundry IQ",
          proof_level: "local_demo_fallback",
          compliance_status: "ready_for_demo",
          live_microsoft_iq: false,
          honest_limitation: "Demo mode uses local grounding; Azure AI Search is not live."
        }}
        demoReport={{ grounding_summary: { source_types: ["local_demo_grounding"], citations_count: 3 } }}
        onCopy={vi.fn()}
      />
    );

    expect(screen.getByText("Foundry IQ Local Adapter")).toBeInTheDocument();
    expect(screen.getByText("Local Knowledge Index")).toBeInTheDocument();
    expect(screen.queryByText("satisfies live Microsoft IQ")).not.toBeInTheDocument();
  });
});
