import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FoundryIQLayerDiagram } from "./FoundryIQLayerDiagram";

describe("FoundryIQLayerDiagram", () => {
  it("renders the local adapter architecture steps and status badges", () => {
    render(<FoundryIQLayerDiagram />);

    const list = screen.getByRole("list");
    expect(list).toBeInTheDocument();
    expect(within(list).getByText("Knowledge Sources")).toBeInTheDocument();
    expect(within(list).getByText("Local Knowledge Base")).toBeInTheDocument();
    expect(within(list).getByText("Citation Retrieval")).toBeInTheDocument();
    expect(within(list).getByText("Reasoning Agents")).toBeInTheDocument();
    expect(within(list).getByText("Manager Report")).toBeInTheDocument();

    expect(screen.getByText("Foundry IQ Local Adapter")).toBeInTheDocument();
    expect(screen.getByText("Adapter Ready")).toBeInTheDocument();
    expect(screen.getByText("Azure Quota Blocked")).toBeInTheDocument();
    expect(screen.getByText("Live Azure Not Active")).toBeInTheDocument();
  });
});
