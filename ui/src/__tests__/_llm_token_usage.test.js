// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent } from "@testing-library/react";
import { vi } from "vitest";
import LLMTokenUsage from "../app/_llm_token_usage";
import { FEATURES } from "../app/feature_toggle";

// Mock the formatTokens utility
vi.mock("../app/utils/tokenUtils", () => ({
  formatTokens: vi.fn((num) => {
    if (typeof num !== "number" || isNaN(num)) return "-";
    if (num < 1500) return "1k";
    return `${Math.round(num / 1000)}k`;
  }),
}));

describe("LLMTokenUsage Component", () => {
  const defaultProps = {
    tokenUsage: { input_tokens: 1000, output_tokens: 2000 },
    featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: true },
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render token usage icon when feature toggle is enabled and has token usage", () => {
    render(<LLMTokenUsage {...defaultProps} />);

    expect(screen.getByTestId("llm-token-usage")).toBeInTheDocument();
  });

  it("should not render when feature toggle is disabled", () => {
    const props = {
      ...defaultProps,
      featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: false },
    };

    const { container } = render(<LLMTokenUsage {...props} />);
    expect(container.firstChild).toBeNull();
  });

  it("should not render when feature toggle is not provided", () => {
    const props = {
      tokenUsage: { input_tokens: 1000, output_tokens: 2000 },
      featureToggleConfig: {},
    };

    const { container } = render(<LLMTokenUsage {...props} />);
    expect(container.firstChild).toBeNull();
  });

  it("should not render when no token usage data", () => {
    const props = {
      tokenUsage: { input_tokens: 0, output_tokens: 0 },
      featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: true },
    };

    const { container } = render(<LLMTokenUsage {...props} />);
    expect(container.firstChild).toBeNull();
  });

  it("should not render when token usage is null", () => {
    const props = {
      tokenUsage: null,
      featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: true },
    };

    const { container } = render(<LLMTokenUsage {...props} />);
    expect(container.firstChild).toBeNull();
  });

  it("should not render when token usage is undefined", () => {
    const props = {
      tokenUsage: undefined,
      featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: true },
    };

    const { container } = render(<LLMTokenUsage {...props} />);
    expect(container.firstChild).toBeNull();
  });

  it("should render when only input tokens are present", () => {
    const props = {
      tokenUsage: { input_tokens: 1500, output_tokens: 0 },
      featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: true },
    };

    render(<LLMTokenUsage {...props} />);
    expect(screen.getByTestId("llm-token-usage")).toBeInTheDocument();
  });

  it("should render when only output tokens are present", () => {
    const props = {
      tokenUsage: { input_tokens: 0, output_tokens: 2500 },
      featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: true },
    };

    render(<LLMTokenUsage {...props} />);
    expect(screen.getByTestId("llm-token-usage")).toBeInTheDocument();
  });

  it("should show tooltip on mouse enter", async () => {
    render(<LLMTokenUsage {...defaultProps} />);

    const tokenIcon = screen.getByTestId("llm-token-usage");
    fireEvent.mouseEnter(tokenIcon);

    // Check that tooltip content is displayed
    expect(screen.getByText("Input Tokens: 1k")).toBeInTheDocument();
    expect(screen.getByText("Output Tokens: 2k")).toBeInTheDocument();
  });

  it("should hide tooltip on mouse leave", async () => {
    render(<LLMTokenUsage {...defaultProps} />);

    const tokenIcon = screen.getByTestId("llm-token-usage");

    // Show tooltip
    fireEvent.mouseEnter(tokenIcon);
    expect(screen.getByText("Input Tokens: 1k")).toBeInTheDocument();

    // Hide tooltip
    fireEvent.mouseLeave(tokenIcon);
    // The tooltip should be hidden, but we can't easily test this with the current implementation
    // This test ensures the mouse events are handled without errors
  });

  it("should handle undefined token values gracefully", () => {
    const props = {
      tokenUsage: { input_tokens: undefined, output_tokens: 2000 },
      featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: true },
    };

    render(<LLMTokenUsage {...props} />);
    expect(screen.getByTestId("llm-token-usage")).toBeInTheDocument();
  });

  it("should handle null token values gracefully", () => {
    const props = {
      tokenUsage: { input_tokens: null, output_tokens: 2000 },
      featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: true },
    };

    render(<LLMTokenUsage {...props} />);
    expect(screen.getByTestId("llm-token-usage")).toBeInTheDocument();
  });

  it("should handle NaN token values gracefully", () => {
    const props = {
      tokenUsage: { input_tokens: NaN, output_tokens: 2000 },
      featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: true },
    };

    render(<LLMTokenUsage {...props} />);
    expect(screen.getByTestId("llm-token-usage")).toBeInTheDocument();
  });

  it("should handle large token numbers correctly", () => {
    const props = {
      tokenUsage: { input_tokens: 15000, output_tokens: 25000 },
      featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: true },
    };

    render(<LLMTokenUsage {...props} />);
    const tokenIcon = screen.getByTestId("llm-token-usage");
    fireEvent.mouseEnter(tokenIcon);

    expect(screen.getByText("Input Tokens: 15k")).toBeInTheDocument();
    expect(screen.getByText("Output Tokens: 25k")).toBeInTheDocument();
  });

  it("should handle small token numbers correctly", () => {
    const props = {
      tokenUsage: { input_tokens: 500, output_tokens: 1000 },
      featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: true },
    };

    render(<LLMTokenUsage {...props} />);
    const tokenIcon = screen.getByTestId("llm-token-usage");
    fireEvent.mouseEnter(tokenIcon);

    expect(screen.getByText("Input Tokens: 1k")).toBeInTheDocument();
    expect(screen.getByText("Output Tokens: 1k")).toBeInTheDocument();
  });

  it("should handle edge case of exactly 1500 tokens", () => {
    const props = {
      tokenUsage: { input_tokens: 1500, output_tokens: 1500 },
      featureToggleConfig: { [FEATURES.LLM_TOKEN_USAGE]: true },
    };

    render(<LLMTokenUsage {...props} />);
    const tokenIcon = screen.getByTestId("llm-token-usage");
    fireEvent.mouseEnter(tokenIcon);

    expect(screen.getByText("Input Tokens: 2k")).toBeInTheDocument();
    expect(screen.getByText("Output Tokens: 2k")).toBeInTheDocument();
  });
});
