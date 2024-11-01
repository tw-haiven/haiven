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

describe("CardsChat Component", () => {
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

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("should render the default user input fields and options when no prompt is selected", async () => {
    await act(async () => {
      render(
        <CardsChat
          promptId="some-prompt-id"
          prompts={mockPrompts}
          contexts={mockContexts}
          models={mockModels}
        />,
      );
    });

    expect(
      screen.getAllByText(/User persona creation/i)[0],
    ).toBeInTheDocument();
    expect(screen.getByTestId("user-input")).toBeInTheDocument();
    expect(screen.getByTestId("context-select")).toBeInTheDocument();
    expect(screen.getByText(/Contexts/i)).toBeInTheDocument();
    const generateButtons = screen.getAllByText((content, element) => {
      return element.tagName.toLowerCase() === "span" && content === "GENERATE";
    });
    expect(generateButtons.length).toBe(1);
  });

  it.skip("should display follow-up options after generating scenarios", async () => {
    fetchSSE.mockImplementation((url, fetchOptions, options) => {
      console.log("fetchSSE mock called");
      const someScenario = JSON.stringify([
        { title: "Scenario 1", summary: "Summary 1" },
      ]);
      options.onMessageHandle({ data: someScenario.substring(0, 10) });
      options.onMessageHandle({ data: someScenario.substring(11) });
    });

    await act(async () => {
      render(
        <CardsChat
          promptId="1"
          prompts={mockPrompts}
          contexts={mockContexts}
          models={mockModels}
        />,
      );
    });

    const generateButton = screen.getAllByText(/GENERATE/i)[0];
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText(/Follow Up 1/i)).toBeInTheDocument();
    });
  });

  it("should show a scenario returned by the backend on a card and handle follow-up", async () => {
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

    function givenUserInput() {
      const inputField = screen.getByTestId("user-input");
      fireEvent.change(inputField, { target: { value: someUserInput } });

      // TODO: Cannot get the selection of a value in the dropdown to work
      // const contextSelect = screen.getByTestId("context-select").firstElementChild;
      // fireEvent.mouseDown(contextSelect);
      // expect(screen.getByText("Context 1")).toBeInTheDocument();
      // fireEvent.click(screen.getByText('Context 1'));
      //////////////////
    }

    function whenGenerateIsClicked() {
      const mainGenerateButton = screen.getAllByText(/GENERATE/i)[0];
      fireEvent.click(mainGenerateButton);
    }

    function thenFirstPromptRequestHappens(bodyString) {
      const body = JSON.parse(bodyString);
      expect(body.userinput).toBe(someUserInput);
      expect(body.promptid).toBe(mockPrompts[0].identifier);
      // TODO: Cannot get the selection of a value in the dropdown to work
      // expect(body.context).toBe(mockContexts[1].key);
    }

    function thenScenariosAreRendered() {
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
    }

    function thenFollowUpPromptRequestHappens(bodyString) {
      const body = JSON.parse(bodyString);
      expect(body.userinput).toBe(someUserInput);
      expect(body.promptid).toBe(mockPrompts[0].followUps[0].identifier);
      expect(body.scenarios[0].title).toBe(someScenarios[0].title);
      expect(body.previous_promptid).toBe(mockPrompts[0].identifier);
      // TODO: Cannot get the selection of a value in the dropdown to work
      // expect(body.context).toBe(mockContexts[1].key);
    }

    function whenFollowUpGenerateIsClicked() {
      const followUpCollapse = screen.getByTestId("follow-up-collapse");
      const firstFollowUp = within(followUpCollapse).getByText(/Follow Up 1/i);
      expect(firstFollowUp).toBeInTheDocument();
      fireEvent.click(firstFollowUp);
      const followUpGenerateButton =
        within(followUpCollapse).getAllByText(/GENERATE/i)[0];
      fireEvent.click(followUpGenerateButton);
    }

    fetchSSE
      .mockImplementationOnce((url, options, { onMessageHandle }) => {
        thenFirstPromptRequestHappens(options.body);

        // given the backend sends scenarios
        const scenarioString = JSON.stringify(someScenarios);
        onMessageHandle({ data: scenarioString.substring(0, 10) });
        onMessageHandle({ data: scenarioString.substring(10) });
      })
      .mockImplementationOnce((url, options, { onMessageHandle }) => {
        thenFollowUpPromptRequestHappens(options.body);

        // given the backend sends the follow-up response
        onMessageHandle(followUpResponse);
      });

    function thenFollowUpIsRendered() {
      expect(screen.getByText(followUpResponse)).toBeInTheDocument();
    }

    //////////////
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
});
