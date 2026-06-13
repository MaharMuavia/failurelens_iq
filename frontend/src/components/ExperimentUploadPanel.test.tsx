import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExperimentUploadPanel } from "./ExperimentUploadPanel";
import * as api from "../utils/api";

describe("ExperimentUploadPanel", () => {
  it("renders upload textarea and buttons", () => {
    render(<ExperimentUploadPanel />);
    expect(screen.getByText("Upload Experiment")).toBeInTheDocument();
    expect(screen.getByText("Upload JSON")).toBeInTheDocument();
    expect(screen.getByText("Load Sample Experiment")).toBeInTheDocument();
  });

  it("shows success message after upload", async () => {
    vi.spyOn(api, "uploadExperiment").mockResolvedValue({ success: true });
    render(<ExperimentUploadPanel />);
    fireEvent.click(screen.getByText("Upload JSON"));
    expect(await screen.findByText(/Stored successfully/i)).toBeInTheDocument();
  });
});
