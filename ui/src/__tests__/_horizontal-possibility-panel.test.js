// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import HorizontalPossibilityPanel from "../pages/_horizontal-possibility-panel";

describe("HorizontalPossibilityPanel", () => {
  const mockQueries = [
    {
      name: "What is the weather today?",
      description: "What is the weather today?",
    },
    {
      name: "Show me vacation ideas.",
      description: "Show me vacation ideas.",
    },
    {
      name: "Plan a weekend getaway.",
      description: "Plan a weekend getaway.",
    },
  ];

  it("renders the suggestions", () => {
    const mockOnClick = vi.fn();

    render(
      <HorizontalPossibilityPanel
        scenarioQueries={mockQueries}
        onClick={mockOnClick}
      />,
    );

    expect(screen.getByText("Suggestions:")).toBeInTheDocument();

    mockQueries.forEach((query) => {
      expect(screen.getByText(query.description)).toBeInTheDocument();
    });
  });

  it("handles suggestion button clicks", () => {
    const mockOnClick = vi.fn();
    render(
      <HorizontalPossibilityPanel
        scenarioQueries={mockQueries}
        onClick={mockOnClick}
      />,
    );
    const firstButton = screen.getByText(mockQueries[0].description);

    fireEvent.click(firstButton);

    expect(mockOnClick).toHaveBeenCalledOnce();
    expect(mockOnClick).toHaveBeenCalledWith(mockQueries[0].description);
  });
});
