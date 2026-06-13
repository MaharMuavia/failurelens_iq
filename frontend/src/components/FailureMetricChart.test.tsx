import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { experiments } from "../data/mockData";
import { FailureMetricChart } from "./FailureMetricChart";

describe("FailureMetricChart", () => {
  it("renders the metric contradiction and callout", () => {
    render(<FailureMetricChart experiment={experiments[0]} />);

    expect(screen.getByText("High accuracy hid minority-class failure")).toBeInTheDocument();
    expect(screen.getByText("93% accuracy hides 14% minority F1.")).toBeInTheDocument();
    expect(screen.getByText("Why this experiment failed despite high accuracy")).toBeInTheDocument();
  });
});
