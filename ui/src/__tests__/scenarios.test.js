import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Home from "../pages/scenarios";
import {afterEach, vi} from "vitest";
import { fetchSSE } from "../app/_fetch_sse";

// Mock window.matchMedia for Ant Design components
window.matchMedia =
  window.matchMedia ||
  function () {
    return {
      matches: false,
      addListener: function () {},
      removeListener: function () {},
    };
  };

vi.mock("../app/_fetch_sse", () => ({
  fetchSSE: vi.fn(),
}));

vi.mock("../app/_dynamic_data_renderer", () => ({
  scenarioToText: vi.fn(() => "Scenario text"),
}));

vi.mock("../hooks/useLoader", () => ({
  __esModule: true,
  default: () => ({
    loading: false,
    abortLoad: vi.fn(),
    startLoad: vi.fn(),
    StopLoad: vi.fn(() => <div>StopLoad</div>),
  }),
}));

vi.mock("../pages/_chat_header", () => ({
  __esModule: true,
  default: ({ titleComponent }) => (
    <div>
      ChatHeader
      {titleComponent}
    </div>
  ),
}));
vi.mock("../pages/_chat_exploration", () => ({
  __esModule: true,
  default: () => <div>ChatExploration</div>,
}));
vi.mock("../app/_cards-list", () => ({
  __esModule: true,
  default: ({ scenarios, onExplore }) => (
    <div>
      CardsList
      {scenarios.map((s, i) => (
        <div key={i} data-testid="scenario-card" onClick={() => onExplore(s)}>
          {s.title}
        </div>
      ))}
    </div>
  ),
}));
vi.mock("../app/_help_tooltip", () => ({
  __esModule: true,
  default: () => <span>HelpTooltip</span>,
}));



describe("Scenarios Page", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the title and input area", () => {
    render(<Home models={[]} />);
    expect(screen.getByText(/Scenario Design/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Enter your strategic prompt here/i)).toBeInTheDocument();
  });

  it("shows advanced prompt options", () => {
    render(<Home models={[]} />);
    expect(screen.getByText(/Specify scenario parameters/i)).toBeInTheDocument();
    expect(screen.getByText(/Optimistic/i)).toBeInTheDocument();
    expect(screen.getByText(/Sci-fi Future/i)).toBeInTheDocument();
    expect(screen.getByText(/Add details/i)).toBeInTheDocument();
  });

  it("submits a prompt and disables input", async () => {
    const mockedFetchSSE = vi.mocked(fetchSSE);
    mockedFetchSSE.mockImplementation((_uri, _opts, { onMessageHandle, onFinish }) => {
      onMessageHandle({ data: '[{"id":1,"title":"Test Scenario"}]' });
      onFinish();
    });
    render(<Home models={[]} />);
    const textarea = screen.getByPlaceholderText(/Enter your strategic prompt here/i);
    fireEvent.change(textarea, { target: { value: "Test prompt" } });
    fireEvent.keyDown(textarea, { key: "Enter", code: "Enter", shiftKey: false });
    await waitFor(() => expect(screen.getByText("Test Scenario")).toBeInTheDocument());
  });

  it("opens the exploration drawer when a scenario is clicked", async () => {
    const mockedFetchSSE = vi.mocked(fetchSSE);
    mockedFetchSSE.mockImplementation((_uri, _opts, { onMessageHandle, onFinish }) => {
      onMessageHandle({ data: '[{"id":2,"title":"Explore Me"}]' });
      onFinish();
    });
    render(<Home models={[]} />);
    const textarea = screen.getByPlaceholderText(/Enter your strategic prompt here/i);
    fireEvent.change(textarea, { target: { value: "Prompt" } });
    fireEvent.keyDown(textarea, { key: "Enter", code: "Enter", shiftKey: false });
    await waitFor(() => expect(screen.getByText("Explore Me")).toBeInTheDocument());
    fireEvent.click(screen.getByText("Explore Me"));
    expect(screen.getByText("ChatExploration")).toBeInTheDocument();
  });
});
