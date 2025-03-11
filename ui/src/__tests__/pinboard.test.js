// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, fireEvent, waitFor } from "@testing-library/react";
import Pinboard from "../pages/pinboard";
import { describe, it, expect } from "vitest";
import { FEATURES } from "../app/feature_toggle";

beforeEach(() => {
  vi.mock(import("../app/_local_store"), async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      getFeatureToggleConfiguration: () => ({
        [FEATURES.ADD_CONTEXT_FROM_UI]: "true",
      }),
    };
  });
});

afterEach(() => {
  vi.resetAllMocks();
});

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
    const { getByText } = render(
      <Pinboard isModalVisible={true} onClose={() => {}} />,
    );

    fireEvent.click(getByText("ADD NOTE"));

    expect(getByText("Add new Note")).toBeInTheDocument();
    expect(getByText("Title")).toBeInTheDocument();
    expect(getByText("Description")).toBeInTheDocument();
  });
});
