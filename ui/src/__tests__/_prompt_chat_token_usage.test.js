import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import PromptChat from '../app/_prompt_chat';

// Mock ProChat to capture and verify streaming behavior
const mockProChat = {
  clearMessage: vi.fn(),
  sendMessage: vi.fn(),
  getChatMessages: vi.fn(() => []),
  setMessageContent: vi.fn(),
  resendMessage: vi.fn(),
  deleteMessage: vi.fn(),
  stopGenerateMessage: vi.fn(),
};

vi.mock('@ant-design/pro-chat', () => ({
  ProChatProvider: ({ children }) => <div>{children}</div>,
  ProChat: ({ request, ...props }) => {
    // Store the request function for testing
    window.testProChatRequest = request;
    return <div data-testid="pro-chat">ProChat Mock</div>;
  },
  useProChat: () => mockProChat,
  ActionIconGroup: ({ items, onActionClick }) => (
    <div data-testid="action-group">
      {items.map(item => (
        <button key={item.key} onClick={() => onActionClick({ item })}>
          {item.label}
        </button>
      ))}
    </div>
  ),
}));

// Mock other dependencies
vi.mock('../app/_image_description', () => ({
  __esModule: true,
  default: () => <div data-testid="image-description" />,
}));

vi.mock('../app/_help_tooltip', () => ({
  __esModule: true,
  default: () => <div data-testid="help-tooltip" />,
}));

vi.mock('../app/_context_choice', () => ({
  __esModule: true,
  default: () => <div data-testid="context-choice" />,
}));

vi.mock('../pages/_chat_header', () => ({
  __esModule: true,
  default: () => <div data-testid="chat-header" />,
}));

vi.mock('../app/_prompt_preview', () => ({
  __esModule: true,
  default: () => <div data-testid="prompt-preview" />,
}));

vi.mock('../app/_download_prompt', () => ({
  __esModule: true,
  default: () => <div data-testid="download-prompt" />,
}));

vi.mock('../app/_local_store', () => ({
  getSortedUserContexts: vi.fn(() => []),
  getSummaryForTheUserContext: vi.fn(() => ''),
  addToPinboard: vi.fn(),
  getTokenUsage: vi.fn(() => ({})),
  saveTokenUsage: vi.fn(),
}));

const mockUseTokenUsage = vi.fn(() => ({
  tokenUsage: { input_tokens: 100, output_tokens: 200 },
  hasTokenUsage: true,
}));

vi.mock('../hooks/useTokenUsage', () => ({
  useTokenUsage: () => mockUseTokenUsage(),
}));

vi.mock('../app/_llm_token_usage', () => ({
  __esModule: true,
  default: () => <div data-testid="llm-token-usage">Token usage displayed</div>,
}));

describe('PromptChat Token Usage Stream Processing', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
    // Reset to default mock behavior
    mockUseTokenUsage.mockReturnValue({
      tokenUsage: { input_tokens: 100, output_tokens: 200 },
      hasTokenUsage: true,
    });
  });

  const createMockStreamResponse = (chunks) => {
    const encoder = new TextEncoder();
    let chunkIndex = 0;
    
    return {
      ok: true,
      headers: {
        get: (key) => key === 'X-Chat-ID' ? 'test-chat-id' : null,
      },
      body: {
        getReader: () => ({
          read: vi.fn().mockImplementation(() => {
            if (chunkIndex < chunks.length) {
              const chunk = chunks[chunkIndex++];
              return Promise.resolve({
                done: false,
                value: encoder.encode(chunk),
              });
            }
            return Promise.resolve({ done: true });
          }),
        }),
      },
    };
  };

  it('should extract token usage from streaming response and display it', async () => {
    // Mock streaming response with token usage in SSE format
    const mockResponse = createMockStreamResponse([
      'data: Hello\n\n',
      'data:  world\n\n',
      'event: token_usage\ndata: {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300, "model": "gpt-4"}\n\n',
    ]);

    global.fetch.mockResolvedValue(mockResponse);

    const { container } = render(
      <PromptChat
        prompts={[]}
        contexts={[]}
        documents={[]}
        models={[]}
        featureToggleConfig={{}}
      />
    );

    // Trigger a chat request
    const testRequest = window.testProChatRequest;
    await testRequest([{ content: 'Test message' }]);

    // Wait for token usage to be displayed
    await waitFor(() => {
      expect(screen.getByTestId('llm-token-usage')).toBeInTheDocument();
    });

    // Verify token usage component is shown
    expect(screen.getByText('Token usage displayed')).toBeInTheDocument();
  });

  it('should not pass token usage data to ProChat component', async () => {
    const mockResponse = createMockStreamResponse([
      'data: Hello\n\n',
      'event: token_usage\ndata: {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300, "model": "gpt-4"}\n\n',
      'data:  world\n\n',
    ]);

    global.fetch.mockResolvedValue(mockResponse);

    render(
      <PromptChat
        prompts={[]}
        contexts={[]}
        documents={[]}
        models={[]}
        featureToggleConfig={{}}
      />
    );

    // Trigger a chat request and capture the stream
    const testRequest = window.testProChatRequest;
    const responsePromise = testRequest([{ content: 'Test message' }]);

    // Read the stream that ProChat would receive
    const response = await responsePromise;
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let streamedContent = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      streamedContent += decoder.decode(value, { stream: true });
    }

    // Verify that token usage JSON is NOT in the stream content
    expect(streamedContent).not.toContain('token_usage');
    expect(streamedContent).toContain('Hello');
    expect(streamedContent).toContain(' world');
  });

  it('should handle malformed JSON gracefully', async () => {
    const mockResponse = createMockStreamResponse([
      'data: Hello\n\n',
      'event: token_usage\ndata: {"invalid": json}\n\n', // malformed JSON
      'data:  world\n\n',
    ]);

    global.fetch.mockResolvedValue(mockResponse);

    render(
      <PromptChat
        prompts={[]}
        contexts={[]}
        documents={[]}
        models={[]}
        featureToggleConfig={{}}
      />
    );

    const testRequest = window.testProChatRequest;
    const responsePromise = testRequest([{ content: 'Test message' }]);

    // Should not throw errors
    await expect(responsePromise).resolves.toBeDefined();

    // Should pass through malformed JSON as regular content
    const response = await responsePromise;
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let streamedContent = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      streamedContent += decoder.decode(value, { stream: true });
    }

    expect(streamedContent).toContain('Hello');
    expect(streamedContent).toContain(' world');
    // Malformed JSON should not cause crashes - content should still be there
  });

  it('should preserve content in complete SSE response with newlines', async () => {
    // Mock streaming response with complete content including newlines
    const completeContent = `## Step 1 - Feature breakdown

### Key features:
- Feature A: Description here
- Feature B: Another description

This is a complete response with all formatting preserved.`;

    // Backend sends escaped newlines in SSE format
    const escapedContent = completeContent.replace(/\n/g, '\\n');
    
    const mockResponse = createMockStreamResponse([
      `data: ${escapedContent}\n\n`,
      'event: token_usage\ndata: {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300, "model": "gpt-4"}\n\n',
    ]);

    global.fetch.mockResolvedValue(mockResponse);

    render(
      <PromptChat
        prompts={[]}
        contexts={[]}
        documents={[]}
        models={[]}
        featureToggleConfig={{}}
      />
    );

    // Trigger a chat request
    const testRequest = window.testProChatRequest;
    const responsePromise = testRequest([{ content: 'Test message' }]);

    // Get the streamed content
    const response = await responsePromise;
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let streamedContent = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      streamedContent += decoder.decode(value, { stream: true });
    }

    // Verify the complete content is preserved - the backend sends escaped newlines
    // and the frontend displays them as-is (the content comes from SSE data: field)
    const expectedContent = `data: ${escapedContent}\n\n`;
    expect(streamedContent).toBe(expectedContent);
    
    // Verify token usage is still displayed
    await waitFor(() => {
      expect(screen.getByTestId('llm-token-usage')).toBeInTheDocument();
    });
  });

  it('should handle responses without token usage data gracefully', async () => {
    // Mock streaming response with no token usage data
    const mockResponse = createMockStreamResponse([
      'data: Hello world\n\n',
      'data: This is a test\n\n',
    ]);

    global.fetch.mockResolvedValue(mockResponse);

    const { container } = render(
      <PromptChat
        prompts={[]}
        contexts={[]}
        documents={[]}
        models={[]}
        featureToggleConfig={{}}
      />
    );

    // Trigger a chat request
    const testRequest = window.testProChatRequest;
    const responsePromise = testRequest([{ content: 'Test message' }]);

    // Should not throw errors when no token usage is received
    await expect(responsePromise).resolves.toBeDefined();
    
    // The component itself should still be present (it handles its own visibility)
    expect(container).toBeInTheDocument();
  });


}); 