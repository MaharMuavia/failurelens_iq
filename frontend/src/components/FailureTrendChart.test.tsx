import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { experiments } from "../data/mockData";
import { FailureTrendChart } from "./FailureTrendChart";

describe("FailureTrendChart", () => {
  it("renders the trend comparison chart and shows legend entries for baseline and current performance", () => {
    render(<FailureTrendChart experiment={experiments[0]} />);

    expect(screen.getByText("Metric trend")).toBeInTheDocument();
    expect(screen.getByText("Current run vs baseline performance")).toBeInTheDocument();
    expect(screen.getByText("Baseline")).toBeInTheDocument();
    expect(screen.getByText("Current")).toBeInTheDocument();
  });
});
