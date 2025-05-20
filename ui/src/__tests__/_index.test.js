// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent } from "@testing-library/react";
import { act } from "react";
import ChatDashboard from "../pages/index";
import { describe, it, expect, vi } from "vitest";
import {
  getPrompts,
  getDisclaimerAndGuidelines,
  getInspirations,
} from "../app/_boba_api";
import { staticFeaturesForDashboard } from "../app/_navigation_items";

vi.mock("../app/_boba_api", () => ({
  getPrompts: vi.fn(),
  getDisclaimerAndGuidelines: vi.fn(),
  getInspirations: vi.fn(),
}));

vi.mock("../app/_navigation_items", () => ({
  staticFeaturesForDashboard: vi.fn(),
}));

describe("ChatDashboard Component", () => {
  const mockPrompts = [
    {
      identifier: "1",
      title: "User Persona Creation",
      categories: ["research"],
      help_prompt_description: "Description for user persona creation",
      show: true,
    },
    {
      identifier: "2",
      title: "Contract Test Generation",
      categories: ["testing"],
      help_prompt_description: "Description for Contract Test Generation",
      show: true,
    },
  ];

  const mockStaticFeatures = [
    {
      identifier: "boba-creative-matrix",
      title: "Creative Matrix",
      help_prompt_description: "Description for creative matrix",
      categories: ["ideate"],
      type: "static",
      link: "/creative-matrix",
    },
  ];

  const mockFeatureToggleConfig = {
    cards_iteration: true,
  };

  beforeEach(() => {
    // Setup default mocks before each test
    getPrompts.mockImplementation((onSuccess) => onSuccess(mockPrompts));
    staticFeaturesForDashboard.mockReturnValue(mockStaticFeatures);
    getDisclaimerAndGuidelines.mockImplementation((onSuccess) =>
      onSuccess({
        title: "Welcome",
        content: "Disclaimer message",
      }),
    );
    getInspirations.mockImplementation((onSuccess) => onSuccess([]));
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("should correctly fetch and display prompts and static features on initial render", async () => {
    await act(async () => {
      render(<ChatDashboard />);
    });

    expect(screen.getByText("User Persona Creation")).toBeInTheDocument();
    expect(screen.getByText("Contract Test Generation")).toBeInTheDocument();
    expect(screen.getByText("Creative Matrix")).toBeInTheDocument();
  });

  it("should filter prompts based on selected categories", async () => {
    await act(async () => {
      render(<ChatDashboard />);
    });

    const researchTag = screen.getAllByText("research")[0];

    await act(async () => {
      fireEvent.click(researchTag);
    });

    expect(screen.getByText("User Persona Creation")).toBeInTheDocument();
    expect(
      screen.queryByText("Contract Test Generation"),
    ).not.toBeInTheDocument();
  });

  it("should handle the case where no prompts are returned from the API", async () => {
    getPrompts.mockImplementation((onSuccess) => onSuccess([]));
    staticFeaturesForDashboard.mockReturnValue([]);

    await act(async () => {
      render(<ChatDashboard />);
    });

    expect(screen.queryByText("User Persona Creation")).not.toBeInTheDocument();
    expect(
      screen.queryByText("Contract Test Generation"),
    ).not.toBeInTheDocument();
    expect(screen.queryByText("Creative Matrix")).not.toBeInTheDocument();
  });
});
