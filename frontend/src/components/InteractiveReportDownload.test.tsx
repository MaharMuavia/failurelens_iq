import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InteractiveReportDownload } from "./InteractiveReportDownload";

describe("InteractiveReportDownload component", () => {
  it("renders disabled buttons initially when not enabled", () => {
    render(<InteractiveReportDownload downloadUrl={null} isEnabled={false} />);
    
    const downloadBtn = screen.getByRole("button", { name: /Download Interactive Report/i });
    const previewBtn = screen.getByRole("button", { name: /Preview Report/i });
    
    expect(downloadBtn).toBeDisabled();
    expect(previewBtn).toBeDisabled();
  });

  it("renders enabled buttons and responds to click events", () => {
    const openMock = vi.fn();
    vi.stubGlobal("open", openMock);
    
    render(<InteractiveReportDownload downloadUrl="/report/PROMPT-123/interactive" isEnabled={true} />);
    
    const previewBtn = screen.getByRole("button", { name: /Preview Report/i });
    expect(previewBtn).toBeEnabled();
    
    fireEvent.click(previewBtn);
    expect(openMock).toHaveBeenCalled();
  });
});
