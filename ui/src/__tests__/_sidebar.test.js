import { render, screen } from "@testing-library/react";
import { act } from "react";
import Sidebar from "../pages/_sidebar";
import { describe, it, expect } from "vitest";
import { useRouter } from "next/router";

vi.mock("next/router", () => ({
  useRouter: vi.fn(),
}));

describe("Sidebar Component", () => {
  const mockPrompts = [
    {
      identifier: "1",
      title: "User person creation",
      categories: ["research"],
    },
    {
      identifier: "2",
      title: "Contract test generation",
      categories: ["testing"],
    },
    {
      identifier: "3",
      title: "Architecture discussion",
      categories: ["coding"],
    },
  ];

  it("should render default menu items", async () => {
    (useRouter).mockReturnValue({
      pathname: "/scenarios",
    });

    await act(async () => {
      render(<Sidebar prompts={[]} />);
    });

    expect(screen.getByRole("link", { name: /Dashboard/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Chat with Haiven/i })).toBeInTheDocument();
    expect(screen.getByText(/Ideate/i)).toBeInTheDocument();
    expect(screen.getByText(/Analyse/i)).toBeInTheDocument();
    expect(screen.getByText(/Architecture/i)).toBeInTheDocument();
  });

  it("should render menu items with prompts", async () => {
    (useRouter).mockReturnValue({
      pathname: "/scenarios",
    });

    await act(async () => {
      render(<Sidebar prompts={mockPrompts} />);
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
    (useRouter).mockReturnValue({
      pathname: "/scenarios",
    });

    await act(async () => {
      render(<Sidebar prompts={mockPrompts} />);
    });

    await act(async () => {
      screen.getByText(/Research/i).click();
    });

    expect(screen.getByText(/User person creation/i)).toBeInTheDocument();
  });
});
