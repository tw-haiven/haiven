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
    expect(getByText("ADD NOTE")).toBeInTheDocument();
  });

  it("displays tooltip on hover over ADD NOTE button", async () => {
    const { getByText, findByText } = render(
      <Pinboard isModalVisible={true} onClose={() => {}} />,
    );

    fireEvent.mouseOver(getByText("ADD NOTE"));

    const tooltip = await findByText(
      "Add your own reusable text notes to the pinboard",
    );
    expect(tooltip).toBeInTheDocument();
  });

  it("opens add note modal when ADD NOTE button is clicked", () => {
    const { getByText, getByPlaceholderText } = render(
      <Pinboard isModalVisible={true} onClose={() => {}} />,
    );

    fireEvent.click(getByText("ADD NOTE"));

    expect(getByText("Add new note")).toBeInTheDocument();
    expect(
      getByPlaceholderText("Enter the title of your note"),
    ).toBeInTheDocument();
    expect(
      getByPlaceholderText(
        "Enter the description of your note, e.g. a description of your domain or architecture that you frequently need",
      ),
    ).toBeInTheDocument();
  });
});
