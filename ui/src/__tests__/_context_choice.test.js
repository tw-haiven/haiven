// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent, within } from "@testing-library/react";
import "@testing-library/jest-dom";
import { vi } from "vitest";
import ContextChoice from "../app/_context_choice";

describe("ContextChoice Component", () => {
  const mockContexts = [
    { value: "base", label: "base" },
    { value: "context1", label: "Context 1" },
    { value: "context2", label: "Context 2" },
  ];

  const verifyTooltip = async (testId, tooltipText) => {
    const tooltipElement = screen.getByTestId(testId);
    expect(tooltipElement).toBeInTheDocument();
    fireEvent.mouseOver(tooltipElement.firstChild);
    expect(await screen.findByText(tooltipText)).toBeInTheDocument();
  };

  function verifyAddContextLink() {
    const addContextLink = screen.getByText("Add Context");
    expect(addContextLink).toBeInTheDocument();
    fireEvent.click(addContextLink);

    expect(screen.getByText("Add new Context")).toBeInTheDocument();
    expect(screen.getByText("Title")).toBeInTheDocument();
    expect(screen.getByText("Description")).toBeInTheDocument();
  }

  it("should render context dropdown", async () => {
    render(<ContextChoice contexts={mockContexts} />);
    expect(screen.getByText("Select your context")).toBeInTheDocument();
    expect(screen.getByTestId("context-select")).toBeInTheDocument();
    await verifyTooltip(
      "context-selection-tooltip",
      "Choose a context from your knowledge pack that is relevant to the domain, architecture, or team you are working on.",
    );

    const select = screen.getByTestId("context-select").firstChild;
    fireEvent.mouseDown(select);

    expect(screen.getByText("Context 1")).toBeInTheDocument();
    expect(screen.getByText("Context 2")).toBeInTheDocument();
    verifyAddContextLink();

    const option = await screen.findByText("Context 1");
    fireEvent.click(option);

    expect(within(select).getByText("Context 1")).toBeInTheDocument();
  });
});
