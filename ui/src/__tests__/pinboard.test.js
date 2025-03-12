// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, fireEvent, waitFor, within } from "@testing-library/react";
import Pinboard from "../pages/pinboard";
import { describe, it, expect } from "vitest";
import { FEATURES } from "../app/feature_toggle";

beforeAll(() => {
  vi.mock(import("../app/feature_toggle"), async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      isFeatureEnabled: (featureName) =>
        featureName === FEATURES.ADD_CONTEXT_FROM_UI ? true : false,
    };
  });

  const localStorageMock = (() => {
    let store = {};
    return {
      getItem: (key) => store[key] || null,
      setItem: (key, value) => {
        store[key] = value.toString();
      },
      clear: () => {
        store = {};
      },
    };
  })();

  Object.defineProperty(window, "localStorage", {
    value: localStorageMock,
  });

  Object.assign(navigator, {
    clipboard: {
      writeText: vi.fn(),
    },
  });
});

afterEach(() => {
  localStorage.clear();
  navigator.clipboard.writeText.mockClear();
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
    expect(getByText("ADD CONTEXT")).toBeInTheDocument();
  });

  function verifyCopy(tab, title, description) {
    const copyButton = within(tab).getByTestId("copy");
    fireEvent.click(copyButton);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      "# " + title + "\n\n" + description,
    );
  }

  function verifyDelete(tab, title, description) {
    const deleteButton = within(tab).getByTestId("delete");
    fireEvent.click(deleteButton);
    expect(within(tab).queryByText(title)).not.toBeInTheDocument();
    expect(within(tab).queryByText(description)).not.toBeInTheDocument();
  }

  describe("Add Note", () => {
    function submitNewNote(getByTestId, getByText) {
      const titleInput = getByTestId("add-content-title");
      const descriptionInput = getByTestId("add-content-description");
      const saveButton = getByText("Save");

      fireEvent.change(titleInput, { target: { value: "Test Note Title" } });
      fireEvent.change(descriptionInput, {
        target: { value: "Test Note Description" },
      });
      fireEvent.click(saveButton);
    }

    it("displays ADD NOTE button with tooltip", async () => {
      const { getByText, findByText } = render(
        <Pinboard isModalVisible={true} onClose={() => {}} />,
      );

      expect(getByText("ADD NOTE")).toBeInTheDocument();
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

    it("save note with title and description and display in Pinboard", async () => {
      const noteTitle = "Test Note Title";
      const noteDescription = "Test Note Description";
      const { getByText, getByTestId } = render(
        <Pinboard isModalVisible={true} onClose={() => {}} />,
      );
      const buttonElement = getByText("ADD NOTE");
      fireEvent.click(buttonElement);

      submitNewNote(getByTestId, getByText);
      fireEvent.click(getByText("Pins/Notes"));

      await waitFor(() => {
        const pinsAndNotesTab = getByTestId("pin-and-notes-tab");
        expect(
          within(pinsAndNotesTab).getByText(noteTitle),
        ).toBeInTheDocument();
        expect(
          within(pinsAndNotesTab).getByText(noteDescription),
        ).toBeInTheDocument();
        verifyCopy(pinsAndNotesTab, noteTitle, noteDescription);
        verifyDelete(pinsAndNotesTab, noteTitle, noteDescription);
      });
    });
  });

  describe("Add Context", () => {
    function submitNewContext(getByTestId, getByText) {
      const titleInput = getByTestId("add-content-title");
      const descriptionInput = getByTestId("add-content-description");
      const saveButton = getByText("Save");

      fireEvent.change(titleInput, { target: { value: "Test Context Title" } });
      fireEvent.change(descriptionInput, {
        target: { value: "Test Context Description" },
      });
      fireEvent.click(saveButton);
    }

    it("displays ADD CONTEXT button with tooltip", async () => {
      const { getByText, findByText } = render(
        <Pinboard isModalVisible={true} onClose={() => {}} />,
      );

      fireEvent.mouseOver(getByText("ADD CONTEXT"));

      const tooltip = await findByText(
        "Add your project context to be reused in your Haiven inputs. This will be included in the context dropdown.",
      );
      expect(tooltip).toBeInTheDocument();
    });

    it("opens add context modal when ADD CONTEXT button is clicked", () => {
      const { getByText } = render(
        <Pinboard isModalVisible={true} onClose={() => {}} />,
      );

      fireEvent.click(getByText("ADD CONTEXT"));

      expect(getByText("Add new Context")).toBeInTheDocument();
      expect(getByText("Title")).toBeInTheDocument();
      expect(getByText("Description")).toBeInTheDocument();
    });

    it("save context with title and description and display in Pinboard", async () => {
      const contextTitle = "Test Context Title";
      const contextDescription = "Test Context Description";
      const { getByText, getByTestId } = render(
        <Pinboard isModalVisible={true} onClose={() => {}} />,
      );
      const buttonElement = getByText("ADD CONTEXT");
      fireEvent.click(buttonElement);

      submitNewContext(getByTestId, getByText);
      fireEvent.click(getByText("Contexts"));

      await waitFor(() => {
        const contextsTab = getByTestId("contexts-tab");
        expect(within(contextsTab).getByText(contextTitle)).toBeInTheDocument();
        expect(
          within(contextsTab).getByText(contextDescription),
        ).toBeInTheDocument();
        verifyCopy(contextsTab, contextTitle, contextDescription);
        verifyDelete(contextsTab, contextTitle, contextDescription);
      });
    });
  });
});
