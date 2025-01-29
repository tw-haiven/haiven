// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
  act,
} from "@testing-library/react";
import CardsChat from "../pages/_cards-chat";
import { describe, it, expect, vi, afterEach } from "vitest";
import { fetchSSE } from "../app/_fetch_sse";
import { toast } from "react-toastify";

vi.mock("../app/_fetch_sse");

window.matchMedia =
  window.matchMedia ||
  function () {
    return {
      matches: false,
      addListener: function () {},
      removeListener: function () {},
    };
  };

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

const mockResponseHeadersWithChatId = {
  headers: { get: () => "some-chat-id" },
};

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
  const mainGenerateButton = screen.getAllByText(/SEND/i)[0];
  fireEvent.click(mainGenerateButton);
};

const whenScenarioIsDeselected = () => {
  const includeCheckBoxes = screen.getAllByTestId("scenario-include-checkbox");
  expect(includeCheckBoxes.length).toBe(someScenarios.length);
  includeCheckBoxes.forEach((checkbox) => {
    checkbox.checked = true;
  });

  fireEvent.click(includeCheckBoxes[includeCheckBoxes.length - 1]);
};

const thenStopButtonIsDisplayed = () => {
  expect(screen.getByTestId("stop-button")).toBeInTheDocument();
  expect(screen.getByTestId("stop-button")).toBeVisible();
};

const thenScenariosAreRendered = () => {
  expect(screen.getByText(someScenarios[0].title)).toBeInTheDocument();
  expect(screen.getByText(someScenarios[0].summary)).toBeInTheDocument();
  expect(screen.getByText("Additional Info:")).toBeInTheDocument();
  expect(screen.getByText(someScenarios[0].additionalInfo)).toBeInTheDocument();
  expect(screen.getByText("Tags:")).toBeInTheDocument();
  expect(screen.getByText("tag1")).toBeInTheDocument();
  expect(screen.getByText("tag2")).toBeInTheDocument();
  expect(screen.getByText(someScenarios[1].title)).toBeInTheDocument();
  expect(screen.getByText(someScenarios[1].summary)).toBeInTheDocument();
  expect(screen.getByText("More Details:")).toBeInTheDocument();
  expect(screen.getByText(someScenarios[1].moreDetails)).toBeInTheDocument();
  expect(screen.getByText("Items:")).toBeInTheDocument();
  expect(screen.getByText("item1")).toBeInTheDocument();
  expect(screen.getByText("item2")).toBeInTheDocument();
  expect(screen.getByText(/COPY ALL/i)).toBeInTheDocument();

  const nonEditableSummary = screen.getByText(someScenarios[0].summary);
  expect(nonEditableSummary).toBeInTheDocument();
  expect(nonEditableSummary.tagName.toLowerCase()).not.toBe("textarea");
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

    const thenFollowUpPromptRequestHappens = (bodyString) => {
      const body = JSON.parse(bodyString);
      expect(body.userinput).toBe(someUserInput);
      expect(body.promptid).toBe(mockPrompts[0].followUps[0].identifier);
      expect(body.scenarios.length).toBe(someScenarios.length - 1); // one scenario is deselected
      expect(body.scenarios[0].title).toBe(someScenarios[0].title);
      expect(body.previous_promptid).toBe(mockPrompts[0].identifier);
    };

    const whenFollowUpGenerateIsClicked = () => {
      const followUpCollapse = screen.getByTestId("follow-up-collapse");
      const firstFollowUpArea = within(followUpCollapse).getByText(
        mockPrompts[0].followUps[0].title,
      );
      expect(firstFollowUpArea).toBeInTheDocument();
      fireEvent.click(firstFollowUpArea);

      const followUpGenerateButtons =
        within(followUpCollapse).getAllByText(/GENERATE/i);
      expect(followUpGenerateButtons.length).toBe(1);
      fireEvent.click(followUpGenerateButtons[0]);
    };

    const thenFollowUpIsRendered = () => {
      expect(screen.getByText(followUpResponse)).toBeInTheDocument();
    };

    fetchSSE
      .mockImplementationOnce((url, options, { onMessageHandle }) => {
        thenFirstPromptRequestHappens(options.body);

        const scenarioString = JSON.stringify(someScenarios);
        onMessageHandle(
          { data: scenarioString.substring(0, 10) },
          mockResponseHeadersWithChatId,
        );
        onMessageHandle(
          { data: scenarioString.substring(10) },
          mockResponseHeadersWithChatId,
        );
      })
      .mockImplementationOnce((url, options, { onMessageHandle }) => {
        thenFollowUpPromptRequestHappens(options.body);

        onMessageHandle(followUpResponse, mockResponseHeadersWithChatId);
      });

    await setup();
    givenUserInput();
    whenGenerateIsClicked();

    await waitFor(async () => {
      thenStopButtonIsDisplayed();
      thenScenariosAreRendered();

      whenScenarioIsDeselected();
      whenFollowUpGenerateIsClicked();
      expect(fetchSSE).toHaveBeenCalledTimes(2);

      await waitFor(() => {
        thenStopButtonIsDisplayed();
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
      onMessageHandle(
        { data: scenarioString.substring(0, 10) },
        mockResponseHeadersWithChatId,
      );
      onMessageHandle(
        { data: scenarioString.substring(10) },
        mockResponseHeadersWithChatId,
      );
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

  describe("Process Streaming data", () => {
    afterEach(() => {
      vi.clearAllMocks();
    });

    it("should process streaming data if it is a valid json array", async () => {
      fetchSSE.mockImplementationOnce(
        (url, options, { onMessageHandle, onFinish }) => {
          const scenariosArrayString = JSON.stringify(someScenarios);
          onMessageHandle(
            { data: scenariosArrayString },
            mockResponseHeadersWithChatId,
          );
          onFinish();
        },
      );

      await setup();
      givenUserInput();
      whenGenerateIsClicked();

      await waitFor(async () => {
        thenScenariosAreRendered();
      });
    });

    it("should process streaming data if it is a valid json data with a prefix string", async () => {
      fetchSSE.mockImplementationOnce(
        (url, options, { onMessageHandle, onFinish }) => {
          const scenariosArrayString = JSON.stringify(someScenarios);
          onMessageHandle(
            {
              data: "```Here is your json:" + scenariosArrayString,
            },
            mockResponseHeadersWithChatId,
          );
          onFinish();
        },
      );

      await setup();
      givenUserInput();
      whenGenerateIsClicked();

      await waitFor(async () => {
        thenScenariosAreRendered();
      });
    });

    it("should process streaming data if it is a valid array json data with a suffix string", async () => {
      fetchSSE.mockImplementationOnce(
        (url, options, { onMessageHandle, onFinish }) => {
          const scenariosString = JSON.stringify(someScenarios);
          onMessageHandle(
            { data: scenariosString + "```Here is your json:" },
            mockResponseHeadersWithChatId,
          );
          onFinish();
        },
      );

      await setup();
      givenUserInput();
      whenGenerateIsClicked();

      await waitFor(async () => {
        thenScenariosAreRendered();
      });
    });

    it("should process streaming data if array of scenarios is encapsulated inside a json key value pair", async () => {
      vi.spyOn(toast, "warning");
      fetchSSE.mockImplementationOnce(
        (url, options, { onMessageHandle, onFinish }) => {
          const streamingData = { response: someScenarios };
          const streamingDataAsString = JSON.stringify(streamingData);
          onMessageHandle(
            { data: streamingDataAsString },
            mockResponseHeadersWithChatId,
          );
          onFinish();
        },
      );

      await setup();

      givenUserInput();
      whenGenerateIsClicked();
      await waitFor(async () => {
        thenScenariosAreRendered();
      });
    });

    it("should not process data and show error message when the streaming data is a JSON object but not an array object", async () => {
      const warningMock = vi.spyOn(toast, "warning");
      fetchSSE.mockImplementationOnce(
        (url, options, { onMessageHandle, onFinish }) => {
          onMessageHandle(
            { data: '{"title": "some title"}' },
            mockResponseHeadersWithChatId,
          );
          onFinish();
        },
      );

      await setup();
      givenUserInput();
      whenGenerateIsClicked();

      await waitFor(() => {
        expect(warningMock).toHaveBeenCalledWith(
          "Model failed to respond rightly, please rewrite your message and try again",
        );
      });
    });

    it("should not process data and show error message when the streaming data is not an json object", async () => {
      const warningMock = vi.spyOn(toast, "warning");
      fetchSSE.mockImplementationOnce(
        (url, options, { onMessageHandle, onFinish }) => {
          // Simulate receiving non-JSON data
          onMessageHandle(
            { data: "not a json object" },
            mockResponseHeadersWithChatId,
          );
          onFinish();
        },
      );

      await setup();
      givenUserInput();
      whenGenerateIsClicked();

      await waitFor(() => {
        expect(warningMock).toHaveBeenCalledWith(
          "Model failed to respond rightly, please rewrite your message and try again",
        );
      });
    });
  });
});
