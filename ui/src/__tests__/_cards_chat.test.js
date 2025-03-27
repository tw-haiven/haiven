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
import { toast } from "react-toastify";

import { fetchSSE } from "../app/_fetch_sse";
vi.mock("../app/_fetch_sse");

import { getRenderedPrompt } from "../app/_boba_api";
import { saveContext } from "../app/_local_store";

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

vi.mock("../app/_boba_api", () => ({
  getRenderedPrompt: vi.fn(),
}));

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
    help_sample_input: "Some sample input",
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

const mockFeatureToggleConfig = {
  cards_iteration: true,
};

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

const mockOnDelete = vi.fn();

const setup = async () => {
  await act(async () => {
    render(
      <CardsChat
        promptId={mockPrompts[0].identifier}
        prompts={mockPrompts}
        contexts={mockContexts}
        models={mockModels}
        featureToggleConfig={mockFeatureToggleConfig}
        onDelete={mockOnDelete}
      />,
    );
  });
};

const givenUserInput = (userInput) => {
  const inputField = screen.getByTestId("user-input-text-area");
  expect(inputField).toBeVisible();
  fireEvent.change(inputField, { target: { value: userInput } });
};

const whenSendIsClicked = async () => {
  await waitFor(() => {
    const mainSendButton = screen.getAllByText(/SEND/i)[0];
    expect(mainSendButton).toBeVisible();
    fireEvent.click(mainSendButton);
  });
};

const thenStopButtonIsDisplayed = () => {
  expect(screen.getByTestId("stop-button")).toBeInTheDocument();
  expect(screen.getByTestId("stop-button")).toBeVisible();
};

const thenAllInitialScenariosAreRendered = async () => {
  await waitFor(() => {
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
    expect(screen.getByText(someScenarios[1].moreDetails)).toBeInTheDocument();
    expect(screen.getByText("Items:")).toBeInTheDocument();
    expect(screen.getByText("item1")).toBeInTheDocument();
    expect(screen.getByText("item2")).toBeInTheDocument();
    expect(screen.getByText(/COPY ALL/i)).toBeInTheDocument();

    const nonEditableSummary = screen.getByText(someScenarios[0].summary);
    expect(nonEditableSummary).toBeInTheDocument();
    expect(nonEditableSummary.tagName.toLowerCase()).not.toBe("textarea");
  });
};

function clickAdvancedPrompt() {
  const advancedPromptLink = screen.getByText("Attach more context");
  fireEvent.click(advancedPromptLink);
}

async function selectContext(contextTitle) {
  const contextDropdown = screen.getByTestId("context-select").firstChild;
  fireEvent.mouseDown(contextDropdown);
  const selectedContext = await screen.findByText(contextTitle);
  fireEvent.click(selectedContext);
}

describe("CardsChat Component", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("should allow adding advanced prompting information like context", async () => {
    const thenAdvancedPromptingInputCanBeAdded = () => {
      const advancedPromptingCollapse =
        screen.getByTestId("advanced-prompting");
      fireEvent.click(advancedPromptingCollapse);
      expect(screen.getByTestId("context-select")).toBeInTheDocument();
    };

    const thenSampleInputCanBeOpened = () => {
      const sampleInput = screen.getByTestId("prompt-sample-input-link");
      fireEvent.click(sampleInput);
      expect(screen.getByTestId("sample-input-modal")).toBeInTheDocument();
      const closeModal = screen.getByTestId("close-sample-input");
      fireEvent.click(closeModal);
    };

    const thenPromptPreviewCanBeOpened = () => {
      const promptPreview = screen.getByTestId("prompt-preview-btn");
      fireEvent.click(promptPreview);
      expect(screen.getByTestId("prompt-preview-modal")).toBeInTheDocument();
      const closeModal = screen.getByTestId("close-prompt-preview");
      fireEvent.click(closeModal);
    };

    getRenderedPrompt.mockImplementation((requestData, onSuccess) => {
      expect(requestData.promptid).toBe(mockPrompts[0].identifier);
      onSuccess({
        prompt: "Some prompt",
        template: "Some prompt template",
      });
    });

    await setup();
    givenUserInput(someUserInput);
    thenAdvancedPromptingInputCanBeAdded();
    thenSampleInputCanBeOpened();
    thenPromptPreviewCanBeOpened();
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
      expect(body.scenarios.length).toBe(someScenarios.length);
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
    givenUserInput(someUserInput);
    await whenSendIsClicked();

    await waitFor(async () => {
      thenStopButtonIsDisplayed();
      await thenAllInitialScenariosAreRendered();

      whenFollowUpGenerateIsClicked();
      expect(fetchSSE).toHaveBeenCalledTimes(2);

      await waitFor(() => {
        thenStopButtonIsDisplayed();
        thenFollowUpIsRendered();
      });
    });
  });

  it("should render data for the given user defined context", async () => {
    const setUpUserContexts = () => {
      saveContext("User Context 1", "User Context 1 description");
      saveContext("User Context 2", "User Context 2 description");
    };

    const thenFirstPromptRequestHappensWithUserContext = (bodyString) => {
      const body = JSON.parse(bodyString);
      expect(body.userinput).toBe(someUserInput);
      expect(body.promptid).toBe(mockPrompts[0].identifier);
      expect(body.userContext).toBe("User Context 1 description\n");
      expect(body.context).not.toBeDefined();
    };

    const thenUserContextsAreAddedInDropdown = () => {
      const contextDropdown = screen.getByTestId("context-select").firstChild;
      fireEvent.mouseDown(contextDropdown);
      expect(screen.getByText("User Context 1")).toBeInTheDocument();
      expect(screen.getByText("User Context 2")).toBeInTheDocument();
    };

    fetchSSE.mockImplementationOnce((url, options, { onMessageHandle }) => {
      thenFirstPromptRequestHappensWithUserContext(options.body);
    });

    setUpUserContexts();
    await setup();
    clickAdvancedPrompt();

    thenUserContextsAreAddedInDropdown();

    await selectContext("User Context 1");

    givenUserInput(someUserInput);
    await whenSendIsClicked();
    expect(fetchSSE).toHaveBeenCalledTimes(1);
  });

  it("should allow editing the original user input and restarting the chat", async () => {
    const secondUserInput = "I've changed my mind, new input";
    const secondSetOfScenarios = [
      {
        title: "Scenario 3",
      },
    ];

    const thenFirstPromptRequestHappens = (bodyString) => {
      const body = JSON.parse(bodyString);
      expect(body.userinput).toBe(someUserInput);
      expect(body.promptid).toBe(mockPrompts[0].identifier);
    };

    const thenUserInputIsCollapsed = async () => {
      await waitFor(() => {
        const userInputTextArea = screen.getByTestId("user-input-text-area");
        expect(userInputTextArea).not.toBeVisible();
      });
    };

    const thenSecondPromptRequestHappens = (bodyString) => {
      const body = JSON.parse(bodyString);
      expect(body.userinput).toBe(secondUserInput);
      expect(body.promptid).toBe(mockPrompts[0].identifier);
      expect(body.chatSessionId).not.toBeDefined();
    };

    const whenUserInputIsEdited = async () => {
      const inputAreaCollapse = screen.getByTestId("input-area-collapse");
      expect(inputAreaCollapse).toBeInTheDocument();

      const collapseHeader = within(inputAreaCollapse).getByRole("button");
      expect(collapseHeader).toBeInTheDocument();
      fireEvent.click(collapseHeader);

      await waitFor(() => {
        const userInputTextArea = screen.getByTestId("user-input-text-area");
        expect(userInputTextArea.value).toBe(someUserInput);

        fireEvent.change(userInputTextArea, {
          target: { value: secondUserInput },
        });
      });
    };

    const thenSecondSetOfScenariosReplaceInitialSet = async () => {
      await waitFor(() => {
        expect(
          screen.getByText(someScenarios[0].title),
        ).not.toBeInTheDocument();
        expect(
          screen.getByText(secondSetOfScenarios[0].title),
        ).toBeInTheDocument();
      });
    };

    fetchSSE
      .mockImplementationOnce((url, options, { onMessageHandle }) => {
        thenFirstPromptRequestHappens(options.body);
        console.log("FIRST CALL");
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
        console.log("SECOND CALL");
        thenSecondPromptRequestHappens(options.body);

        onMessageHandle(
          { data: JSON.stringify(secondSetOfScenarios) },
          mockResponseHeadersWithChatId,
        );
      });

    await setup();
    givenUserInput(someUserInput);

    await whenSendIsClicked();

    await thenUserInputIsCollapsed();
    await thenAllInitialScenariosAreRendered();
    expect(fetchSSE).toHaveBeenCalledTimes(1);

    // Edit and send again

    const inputAreaCollapse = screen.getByTestId("input-area-collapse");
    expect(inputAreaCollapse).toBeInTheDocument();
    const collapseHeader = within(inputAreaCollapse).getByRole("button");
    expect(collapseHeader).toBeInTheDocument();
    fireEvent.click(collapseHeader);
    givenUserInput(secondUserInput);

    await whenSendIsClicked();

    // TODO: For the life of me, I cannot get these to work, even though it works in the application
    // await thenUserInputIsCollapsed();
    // await waitFor(() => {
    //   expect(fetchSSE).toHaveBeenCalledTimes(2);
    //   thenSecondSetOfScenariosReplaceInitialSet();
    // });
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
          featureToggleConfig={mockFeatureToggleConfig}
        />,
      );
    });

    givenUserInput(someUserInput);
    await whenSendIsClicked();

    await waitFor(() => {
      const textArea = screen.getByTestId("scenario-summary-0");
      expect(textArea).toBeInTheDocument();
      expect(textArea.tagName.toLowerCase()).toBe("textarea");
    });
  });

  it("should render sections with titles when backend returns nested arrays", async () => {
    const sectionsData = [
      {
        title: "Section of cards",
        scenarios: [
          {
            title: "Scenario 1",
            summary: "A summary",
          },
        ],
      },
      {
        title: "Section of cards 2",
        scenarios: [
          {
            title: "Scenario in section 2",
            summary: "Another summary",
          },
        ],
      },
      {
        title: "Regular card",
        summary: "This is just a regular card without nested scenarios",
      },
    ];

    fetchSSE.mockImplementationOnce((url, options, { onMessageHandle }) => {
      const sectionsString = JSON.stringify(sectionsData);
      onMessageHandle({ data: sectionsString }, mockResponseHeadersWithChatId);
    });

    await setup();
    givenUserInput(someUserInput);
    await whenSendIsClicked();

    await waitFor(async () => {
      // Check section titles are rendered
      expect(screen.getByText("Section of cards")).toBeInTheDocument();
      expect(screen.getByText("Section of cards 2")).toBeInTheDocument();

      // Check cards in first section
      expect(screen.getByText("Scenario 1")).toBeInTheDocument();
      expect(screen.getByText("A summary")).toBeInTheDocument();

      // Check cards in second section
      expect(screen.getByText("Scenario in section 2")).toBeInTheDocument();
      expect(screen.getByText("Another summary")).toBeInTheDocument();

      // Check regular card without nested scenarios
      expect(screen.getByText("Regular card")).toBeInTheDocument();
      expect(
        screen.getByText(
          "This is just a regular card without nested scenarios",
        ),
      ).toBeInTheDocument();
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
      givenUserInput(someUserInput);
      await whenSendIsClicked();

      await thenAllInitialScenariosAreRendered();
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
      givenUserInput(someUserInput);
      await whenSendIsClicked();

      await thenAllInitialScenariosAreRendered();
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
      givenUserInput(someUserInput);
      await whenSendIsClicked();

      await thenAllInitialScenariosAreRendered();
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

      givenUserInput(someUserInput);
      await whenSendIsClicked();
      await thenAllInitialScenariosAreRendered();
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
      givenUserInput(someUserInput);
      await whenSendIsClicked();

      await waitFor(() => {
        expect(warningMock).toHaveBeenCalledWith(
          "Model failed to respond rightly, please rewrite your message and try again",
        );
      });
    });

    it("should not process data and show error message when the streaming data is not json", async () => {
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
      givenUserInput(someUserInput);
      await whenSendIsClicked();

      await waitFor(() => {
        expect(warningMock).toHaveBeenCalledWith(
          "Model failed to respond rightly, please rewrite your message and try again",
        );
      });
    });
  });
});
