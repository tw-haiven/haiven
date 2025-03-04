// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, fireEvent, waitFor } from "@testing-library/react";
import Pinboard from "../pages/pinboard";
import { describe, it, expect } from "vitest";

describe("Pinboard Component", () => {
  it("renders pinboardTitle content correctly", () => {
    const { getByText } = render(
      <Pinboard isModalVisible={true} onClose={() => {}} />,
    );

    expect(getByText("Pinboard")).toBeInTheDocument();
    expect(
      getByText("Access content you've pinned to reuse in your Haiven inputs."),
    ).toBeInTheDocument();
    expect(getByText("ADD SNIPPET")).toBeInTheDocument();
  });

  it("displays tooltip on hover over ADD SNIPPET button", async () => {
    const { getByText, findByText } = render(
      <Pinboard isModalVisible={true} onClose={() => {}} />,
    );

    fireEvent.mouseOver(getByText("ADD SNIPPET"));

    const tooltip = await findByText(
      "Add your own reusable text snippets to the pinboard",
    );
    expect(tooltip).toBeInTheDocument();
  });

  it("opens add snippet modal when ADD SNIPPET button is clicked", () => {
    const { getByText, getByPlaceholderText } = render(
      <Pinboard isModalVisible={true} onClose={() => {}} />,
    );

    fireEvent.click(getByText("ADD SNIPPET"));

    expect(getByText("Add new snippet")).toBeInTheDocument();
    expect(
      getByPlaceholderText(
        "Enter your reusable snippet here, e.g. a description of your domain or architecture that you frequently need",
      ),
    ).toBeInTheDocument();
  });
});
