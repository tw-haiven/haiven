// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen } from "@testing-library/react";
import CardActions from "../app/_card_actions";
import { describe, it, expect, vi } from "vitest";

describe("CardActions", () => {
  const baseProps = {
    featureToggleConfig: {},
    scenario: {},
    onExploreHandler: vi.fn(),
    selfReview: null,
    progress: 42,
    isGenerating: false,
  };

  it("does not render progress bar when isGenerating is false", () => {
    render(<CardActions {...baseProps} />);
    expect(screen.queryByTestId("progress-bar")).not.toBeInTheDocument();
  });

  it("renders progress bar with correct percent when isGenerating is true", () => {
    render(<CardActions {...baseProps} isGenerating={true} />);
    const progress = screen.getByTestId("progress-bar");
    expect(progress).toBeInTheDocument();
    expect(progress).toHaveAttribute("aria-valuenow", "42");
  });
});
