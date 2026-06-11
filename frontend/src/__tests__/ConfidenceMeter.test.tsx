import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ConfidenceMeter } from "../components/ConfidenceMeter";

describe("ConfidenceMeter", () => {
  it("renders with 0 score and requires review", () => {
    render(<ConfidenceMeter score={0} requiresReview={true} />);
    expect(screen.getByText("0%")).toBeInTheDocument();
    expect(screen.getByText("Human review")).toBeInTheDocument();
  });

  it("renders with 1 score and passes gate", () => {
    render(<ConfidenceMeter score={1} requiresReview={false} />);
    expect(screen.getByText("100%")).toBeInTheDocument();
    expect(screen.getByText("Gate passed")).toBeInTheDocument();
  });
});
