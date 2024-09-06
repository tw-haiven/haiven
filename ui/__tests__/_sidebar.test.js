// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import Sidebar from "../src/pages/_sidebar";

vi.mock("next/router", () => ({
  useRouter: () => ({
    pathname: "/ideate",
  }),
}));

vi.mock("../src/app/_navigation_items", () => ({
  initialiseMenuCategoriesForSidebar: () => ({
    ideate: {
      key: "ideate",
      label: "Ideate",
      children: [],
    },
    analyse: {
      key: "analyse",
      label: "Analyse",
      children: [],
    },
    other: {
      key: "other",
      label: "Other",
      children: [],
    },
  }),
}));

describe("Sidebar Component", () => {
  const promptsMock = [
    {
      identifier: "prompt1",
      title: "Prompt 1",
      categories: ["ideate"],
    },
    {
      identifier: "prompt2",
      title: "Prompt 2",
      categories: ["analyse"],
    },
  ];

  it("should render menu items based on prompts", () => {
    render(<Sidebar prompts={promptsMock} />);

    // Verify that the menu items are rendered properly
    expect(screen.getByText("Prompt 1")).toBeInTheDocument();
    expect(screen.getByText("Prompt 2")).toBeInTheDocument();
  });
});
