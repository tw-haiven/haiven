// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
} from "@testing-library/react";
import { act } from "react";
import ThreatModelling from "../pages/threat-modelling";
import { describe, it, expect, vi, afterEach } from "vitest";
import { fetchSSE } from "../app/_fetch_sse";

vi.mock("../app/_fetch_sse");

const mockContexts = [
  { key: "base", label: "Base Context" },
  { key: "context1", label: "Context 1" },
];
const mockModels = [
  {
    chat: "Chat Model",
    vision: "Vision Model ",
    embeddings: "Embeddings Model",
  },
];

const someScenarios = [
  {
    title: "Scenario 1",
    summary: "Summary of scenario 1",
    additionalInfo: "Extra info 1",
  },
  {
    title: "Scenario 2",
    summary: "Summary of scenario 2",
    moreDetails: "Extra info 2",
    items: ["item1", "item2"],
  },
];
const someUserInput = "Here is my prompt input";

const setup = async () => {
  await act(async () => {
    render(<ThreatModelling contexts={mockContexts} models={mockModels} />);
  });
};

const givenUserInput = () => {
  const inputField = screen.getByTestId("user-input");
  fireEvent.change(inputField, { target: { value: someUserInput } });
};

const whenGenerateIsClicked = () => {
  const mainGenerateButton = screen.getByRole("button", { name: "GENERATE" });
  fireEvent.click(mainGenerateButton);
};

const thenScenariosAreRendered = () => {
  expect(screen.getByText(someScenarios[0].title)).toBeInTheDocument();
  expect(screen.getByText(someScenarios[0].summary)).toBeInTheDocument();
  expect(screen.getByText("Additional Info:")).toBeInTheDocument();
  expect(screen.getByText(someScenarios[0].additionalInfo)).toBeInTheDocument();
  expect(screen.getByText(someScenarios[1].title)).toBeInTheDocument();
  expect(screen.getByText(someScenarios[1].summary)).toBeInTheDocument();
  expect(screen.getByText("More Details:")).toBeInTheDocument();
  expect(screen.getByText(someScenarios[1].moreDetails)).toBeInTheDocument();
  expect(screen.getByText("Items:")).toBeInTheDocument();
  expect(screen.getByText("item1")).toBeInTheDocument();
  expect(screen.getByText("item2")).toBeInTheDocument();
};

const thenPromptRequestHappens = (bodyString) => {
  const body = JSON.parse(bodyString);
  expect(body.userinput).toBe(someUserInput);
  expect(body.promptid).toBe("guided-threat-modelling");
};

describe("ThreatModelling Page", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("should show scenarios returned by the backend", async () => {
    fetchSSE.mockImplementationOnce((url, options, { onMessageHandle }) => {
      thenPromptRequestHappens(options.body);
      const scenarioString = JSON.stringify(someScenarios);
      onMessageHandle({ data: scenarioString.substring(0, 10) });
      onMessageHandle({ data: scenarioString.substring(10) });
    });

    await setup();
    givenUserInput();
    whenGenerateIsClicked();

    await waitFor(() => {
      thenScenariosAreRendered();
    });
  });
});
