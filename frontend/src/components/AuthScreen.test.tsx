import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AuthScreen } from "./AuthScreen";

describe("AuthScreen", () => {
  it("renders sign in view and guest button", () => {
    render(<AuthScreen />);
    expect(screen.getByText("FailureLens IQ")).toBeInTheDocument();
    expect(screen.getByText("Sign In")).toBeInTheDocument();
    expect(screen.getByText("Continue as Guest")).toBeInTheDocument();
  });

  it("switches to sign up view and back", () => {
    render(<AuthScreen />);
    fireEvent.click(screen.getByText("Create account"));
    expect(screen.getByText("Create Account")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Already have an account?"));
    expect(screen.getByText("Sign In")).toBeInTheDocument();
  });
});
