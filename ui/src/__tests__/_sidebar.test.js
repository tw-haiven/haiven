// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen } from "@testing-library/react";
import { act } from "react";
import Sidebar from "../pages/_sidebar";
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { useRouter } from "next/router";

vi.mock("next/router", () => ({
  useRouter: vi.fn(),
}));

describe("Sidebar Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockPrompts = [
    {
      identifier: "1",
      title: "User person creation",
      categories: ["research"],
    },
    {
      identifier: "2",
      title: "Contract Test Generation",
      categories: ["testing"],
    },
    {
      identifier: "3",
      title: "Architecture Discussion",
      categories: ["coding"],
    },
  ];

  it("should render default menu items", async () => {
    useRouter.mockReturnValue({
      pathname: "/scenarios",
    });

    await act(async () => {
      render(<Sidebar prompts={[]} featureToggleConfig={{}} />);
    });

    expect(
      screen.getByRole("link", { name: /Dashboard/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /Chat with Haiven/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/Ideate/i)).toBeInTheDocument();
    expect(screen.queryByText(/Architecture/i)).not.toBeInTheDocument(); // No hard-coded entry, so it shouldn't show up
  });

  it("should render menu items with prompts", async () => {
    useRouter.mockReturnValue({
      pathname: "/scenarios",
    });

    await act(async () => {
      render(<Sidebar prompts={mockPrompts} featureToggleConfig={{}} />);
    });

    expect(screen.getByText(/Research/i)).toBeInTheDocument();
    expect(screen.getByText(/Testing/i)).toBeInTheDocument();
    expect(screen.getByText(/Coding/i)).toBeInTheDocument();

    await act(async () => {
      screen.getByText(/Research/i).click();
    });
    expect(screen.getByText(/User person creation/i)).toBeInTheDocument();
  });

  it("should show sub menu items if clicked menu item", async () => {
    useRouter.mockReturnValue({
      pathname: "/scenarios",
    });

    await act(async () => {
      render(<Sidebar prompts={mockPrompts} featureToggleConfig={{}} />);
    });

    await act(async () => {
      screen.getByText(/Research/i).click();
    });

    expect(screen.getByText(/User person creation/i)).toBeInTheDocument();
  });

  describe("Sidebar Component - Delivery Management Feature Toggle via Env", () => {
    const mockPromptsForDeliveryManagement = [
      {
        identifier: "ahm-process",
        title: "AHM Process",
        categories: ["deliveryManagement"],
        type: "chat",
        show: true,
      },
    ];

    const mockPromptsForOtherCategory = [
      {
        identifier: "creative-matrix",
        title: "Creative Matrix",
        categories: ["something-else"],
        type: "static",
        show: true,
      },
    ];

    it("should render Delivery Management category and its prompt when feature flag is true", async () => {
      const Sidebar = (await import("../pages/_sidebar")).default;

      useRouter.mockReturnValue({
        pathname: "/delivery-management",
      });

      await act(async () => {
        render(
          <Sidebar
            prompts={mockPromptsForDeliveryManagement}
            featureToggleConfig={{ FEATURE_DELIVERY_MANAGEMENT: true }}
          />,
        );
      });

      expect(screen.getByText(/Delivery Management/i)).toBeInTheDocument();
      const deliveryManagement = screen.getByText(/Delivery Management/i);
      await act(async () => {
        deliveryManagement.click();
      });
      expect(screen.getByText(/AHM Process/i)).toBeInTheDocument();
    });

    it("should NOT render Delivery Management category when feature flag is false", async () => {
      const Sidebar = (await import("../pages/_sidebar")).default;

      useRouter.mockReturnValue({
        pathname: "/",
      });

      await act(async () => {
        render(
          <Sidebar
            prompts={mockPromptsForDeliveryManagement}
            featureToggleConfig={{ FEATURE_DELIVERY_MANAGEMENT: false }}
          />,
        );
      });

      expect(
        screen.queryByText(/Delivery Management/i),
      ).not.toBeInTheDocument();
      expect(screen.queryByText(/AHM Process/i)).not.toBeInTheDocument();
    });

    it("should NOT render Delivery Management category when feature flag is not set", async () => {
      const Sidebar = (await import("../pages/_sidebar")).default;

      useRouter.mockReturnValue({
        pathname: "/",
      });

      await act(async () => {
        render(
          <Sidebar
            prompts={mockPromptsForDeliveryManagement}
            featureToggleConfig={{}}
          />,
        );
      });

      expect(
        screen.queryByText(/Delivery Management/i),
      ).not.toBeInTheDocument();
      expect(screen.queryByText(/AHM Process/i)).not.toBeInTheDocument();
    });

    it("should always render items under others regardless of the feature flag", async () => {
      const Sidebar = (await import("../pages/_sidebar")).default;

      useRouter.mockReturnValue({
        pathname: "/creative-matrix",
      });

      await act(async () => {
        render(
          <Sidebar
            prompts={mockPromptsForOtherCategory}
            featureToggleConfig={{ FEATURE_DELIVERY_MANAGEMENT: false }}
          />,
        );
      });

      expect(screen.getByText(/Ideate/i)).toBeInTheDocument();
      const ideate = screen.getByText(/Ideate/i);
      await act(async () => {
        ideate.click();
      });
      expect(screen.getByText(/Creative Matrix/i)).toBeInTheDocument();
    });
  });

  describe("Grounded Research Icon", () => {
    const mockPromptsWithGroundedAttribute = [
      {
        identifier: "grounded-research-1",
        title: "Company Research Analysis",
        categories: ["research"],
        type: "chat",
        show: true,
        grounded: true,
      },
      {
        identifier: "regular-prompt",
        title: "Regular Prompt",
        categories: ["research"],
        type: "chat",
        show: true,
        grounded: false,
      },
    ];

    it("should render RiGlobalLine icon for grounded research items", async () => {
      useRouter.mockReturnValue({
        pathname: "/scenarios",
      });

      await act(async () => {
        render(
          <Sidebar
            prompts={mockPromptsWithGroundedAttribute}
            featureToggleConfig={{}}
          />,
        );
      });

      const researchCategory = screen.getByText(/Research/i);
      await act(async () => {
        researchCategory.click();
      });

      // Check if the icon is present for company research item
      const companyResearchItem = screen.getByText(
        /Company Research Analysis/i,
      );
      expect(companyResearchItem.closest("a")).toContainHTML("svg");

      // Check if the icon is not present for regular item
      const regularItem = screen.getByText(/Regular Prompt/i);
      expect(regularItem.closest("a")).not.toContainHTML("svg");
    });

    it("should maintain correct sorting with icons", async () => {
      useRouter.mockReturnValue({
        pathname: "/scenarios",
      });

      await act(async () => {
        render(
          <Sidebar
            prompts={mockPromptsWithGroundedAttribute}
            featureToggleConfig={{}}
          />,
        );
      });

      const researchCategory = screen.getByText(/Research/i);
      await act(async () => {
        researchCategory.click();
      });

      const items = screen.getAllByRole("link");
      const itemTexts = items.map((item) => item.textContent.trim());

      // Verify that items are sorted alphabetically regardless of icon presence
      expect(itemTexts).toEqual([
        "Dashboard",
        "Chat with Haiven",
        "Company Research Analysis",
        "Regular Prompt",
      ]);
    });
  });
});
