import { render, screen, fireEvent } from "@testing-library/react";
import { act } from "react-dom/test-utils";
import ChatDashboard from "../pages/index";
import { describe, it, expect, vi } from "vitest";
import { getPrompts } from "../app/_boba_api";
import { staticFeaturesForDashboard } from "../app/_navigation_items";

vi.mock("../app/_boba_api", () => ({
    getPrompts: vi.fn(),
}));

vi.mock("../app/_navigation_items", () => ({
staticFeaturesForDashboard: vi.fn(),
}));

describe("ChatDashboard Component", () => {
const mockPrompts = [
    {
        identifier: "1",
        title: "User persona creation",
        categories: ["research"],
        help_prompt_description: "Description for user persona creation",
    },
    {
        identifier: "2",
        title: "Contract test generation",
        categories: ["testing"],
        help_prompt_description: "Description for contract test generation",
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

it("should correctly fetch and display prompts and static features on initial render", async () => {
    getPrompts.mockImplementation((onSuccess) => onSuccess(mockPrompts));
    staticFeaturesForDashboard.mockReturnValue(mockStaticFeatures);

    await act(async () => {
        render(<ChatDashboard />);
    });

    expect(screen.getByText("User persona creation")).toBeInTheDocument();
    expect(screen.getByText("Contract test generation")).toBeInTheDocument();
    expect(screen.getByText("Creative Matrix")).toBeInTheDocument();
    });

it("should filter prompts based on selected categories", async () => {
    getPrompts.mockImplementation((onSuccess) => onSuccess(mockPrompts));
    staticFeaturesForDashboard.mockReturnValue(mockStaticFeatures);

    await act(async () => {
        render(<ChatDashboard />);
    });

    const researchTags = screen.getAllByText("research");
    const testingTags = screen.getAllByText("testing");

    // Assuming you want to click the first "research" tag
    await act(async () => {
        fireEvent.click(researchTags[0]);
    });

    expect(screen.getByText("User persona creation")).toBeInTheDocument();
    expect(screen.queryByText(/Contract test generation/i)).not.toBeInTheDocument();
});

it("should handle the case where no prompts are returned from the API", async () => {
    getPrompts.mockImplementation((onSuccess) => onSuccess([]));
    staticFeaturesForDashboard.mockReturnValue([]);

    await act(async () => {
    render(<ChatDashboard />);
    });

    expect(screen.queryByText(/User persona creation/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Contract test generation/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Creative Matrix/i)).not.toBeInTheDocument();
    });
});