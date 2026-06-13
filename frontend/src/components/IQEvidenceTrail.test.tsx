import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IQEvidenceTrail } from "./IQEvidenceTrail";

describe("IQEvidenceTrail", () => {
  it("renders citation IDs, source types, agent usage, and permission scope", () => {
    render(
      <IQEvidenceTrail
        demoReport={{
          iq_grounding_story: {
            citations: [
              {
                id: "failure-taxonomy-001",
                source_type: "failure_taxonomy",
                excerpt: "High accuracy can hide minority-class weakness.",
                relevance_score: 0.91,
                permission_scope: "demo"
              }
            ]
          }
        }}
      />
    );

    expect(screen.getByText("failure-taxonomy-001")).toBeInTheDocument();
    expect(screen.getByText("Type: failure_taxonomy")).toBeInTheDocument();
    expect(screen.getByText("Classifier")).toBeInTheDocument();
    expect(screen.getByText("Scope: demo")).toBeInTheDocument();
  });
});
