// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
} from "@testing-library/react";
import { act } from "react";
import CardsChat from "../pages/_cards-chat";
import { describe, it, expect, vi, afterEach } from "vitest";
import { fetchSSE } from "../app/_fetch_sse";

vi.mock("../app/_fetch_sse");

const mockPrompts = [
  {
    identifier: "some-prompt-id",
    value: "some-prompt-id",
    title: "User persona creation",
    label: "User persona creation",
    help_prompt_description: "Help description",
    help_user_input: "Help input",
    followUps: [
      {
        identifier: "followUp1",
        title: "Follow Up 1",
        help_prompt_description: "Follow Up 1 Description",
      },
    ],
  },
  { identifier: "2", title: "Contract Test Generation", followUps: [] },
];
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
    tags: ["tag1", "tag2"],
  },
  {
    title: "Scenario 2",
    summary: "Summary of scenario 2",
    moreDetails: "Extra info 2",
    items: ["item1", "item2"],
  },
];
const someUserInput = "Here is my prompt input";
const followUpResponse = "Follow-up response";

const setup = async () => {
  await act(async () => {
    render(
      <CardsChat
        promptId={mockPrompts[0].identifier}
        prompts={mockPrompts}
        contexts={mockContexts}
        models={mockModels}
      />,
    );
  });
};

const givenUserInput = () => {
  const inputField = screen.getByTestId("user-input");
  fireEvent.change(inputField, { target: { value: someUserInput } });
};

const whenGenerateIsClicked = () => {
  const mainGenerateButton = screen.getAllByText(/GENERATE/i)[0];
  fireEvent.click(mainGenerateButton);
};

describe("CardsChat Component", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("should show a scenario returned by the backend on a card and handle follow-up", async () => {
    const thenFirstPromptRequestHappens = (bodyString) => {
      const body = JSON.parse(bodyString);
      expect(body.userinput).toBe(someUserInput);
      expect(body.promptid).toBe(mockPrompts[0].identifier);
    };

    const thenScenariosAreRendered = () => {
      expect(screen.getByText(someScenarios[0].title)).toBeInTheDocument();
      expect(screen.getByText(someScenarios[0].summary)).toBeInTheDocument();
      expect(screen.getByText("Additional Info:")).toBeInTheDocument();
      expect(
        screen.getByText(someScenarios[0].additionalInfo),
      ).toBeInTheDocument();
      expect(screen.getByText("Tags:")).toBeInTheDocument();
      expect(screen.getByText("tag1")).toBeInTheDocument();
      expect(screen.getByText("tag2")).toBeInTheDocument();
      expect(screen.getByText(someScenarios[1].title)).toBeInTheDocument();
      expect(screen.getByText(someScenarios[1].summary)).toBeInTheDocument();
      expect(screen.getByText("More Details:")).toBeInTheDocument();
      expect(
        screen.getByText(someScenarios[1].moreDetails),
      ).toBeInTheDocument();
      expect(screen.getByText("Items:")).toBeInTheDocument();
      expect(screen.getByText("item1")).toBeInTheDocument();
      expect(screen.getByText("item2")).toBeInTheDocument();
      expect(screen.getByText(/COPY ALL/i)).toBeInTheDocument();

      const nonEditableSummary = screen.getByText(someScenarios[0].summary);
      expect(nonEditableSummary).toBeInTheDocument();
      expect(nonEditableSummary.tagName.toLowerCase()).not.toBe("textarea");
    };

    const thenFollowUpPromptRequestHappens = (bodyString) => {
      const body = JSON.parse(bodyString);
      expect(body.userinput).toBe(someUserInput);
      expect(body.promptid).toBe(mockPrompts[0].followUps[0].identifier);
      expect(body.scenarios[0].title).toBe(someScenarios[0].title);
      expect(body.previous_promptid).toBe(mockPrompts[0].identifier);
    };

    const whenFollowUpGenerateIsClicked = () => {
      const followUpCollapse = screen.getByTestId("follow-up-collapse");
      const firstFollowUp = within(followUpCollapse).getByText(/Follow Up 1/i);
      expect(firstFollowUp).toBeInTheDocument();
      fireEvent.click(firstFollowUp);
      const followUpGenerateButton =
        within(followUpCollapse).getAllByText(/GENERATE/i)[0];
      fireEvent.click(followUpGenerateButton);
    };

    const thenFollowUpIsRendered = () => {
      expect(screen.getByText(followUpResponse)).toBeInTheDocument();
    };

    fetchSSE
      .mockImplementationOnce((url, options, { onMessageHandle }) => {
        thenFirstPromptRequestHappens(options.body);

        const scenarioString = JSON.stringify(someScenarios);
        onMessageHandle({ data: scenarioString.substring(0, 10) });
        onMessageHandle({ data: scenarioString.substring(10) });
      })
      .mockImplementationOnce((url, options, { onMessageHandle }) => {
        thenFollowUpPromptRequestHappens(options.body);

        onMessageHandle(followUpResponse);
      });

    await setup();
    givenUserInput();
    whenGenerateIsClicked();

    await waitFor(async () => {
      thenScenariosAreRendered();
      whenFollowUpGenerateIsClicked();
      await waitFor(() => {
        thenFollowUpIsRendered();
      });
    });
  });

  it("should allow editing the summary if the prompt configuration is editable", async () => {
    const editablePrompt = {
      ...mockPrompts[0],
      editable: true,
    };

    fetchSSE.mockImplementationOnce((url, options, { onMessageHandle }) => {
      const scenarioString = JSON.stringify(someScenarios);
      onMessageHandle({ data: scenarioString.substring(0, 10) });
      onMessageHandle({ data: scenarioString.substring(10) });
    });

    await act(async () => {
      render(
        <CardsChat
          promptId={editablePrompt.identifier}
          prompts={[editablePrompt]}
          contexts={mockContexts}
          models={mockModels}
        />,
      );
    });

    givenUserInput();
    whenGenerateIsClicked();

    await waitFor(() => {
      const textArea = screen.getByTestId("scenario-summary-0");
      expect(textArea).toBeInTheDocument();
      expect(textArea.tagName.toLowerCase()).toBe("textarea");
    });
  });
});
