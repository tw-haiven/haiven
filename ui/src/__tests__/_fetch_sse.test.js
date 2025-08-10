// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect, vi, beforeEach } from "vitest";
import { fetchSSE } from "../app/_fetch_sse";

// Mock fetch globally
global.fetch = vi.fn();

describe("fetchSSE", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should handle mixed JSON and SSE events in JSON mode", async () => {
    const mockOnMessageHandle = vi.fn();
    const mockOnTokenUsage = vi.fn();

    // Mock a response that contains both JSON data and SSE events
    const mockResponse = {
      ok: true,
      body: {
        getReader: () => ({
          read: vi.fn().mockResolvedValueOnce({
            value: new TextEncoder().encode(
              '{"metadata": {"citations": ["https://example.com"]}}\n\n' +
                "event: token_usage\n" +
                'data: {"event_type":"token_usage","prompt_tokens":100,"completion_tokens":200,"total_tokens":300,"model":"test"}\n\n' +
                '{"data": "Hello world"}\n\n',
            ),
            done: true,
          }),
        }),
      },
    };

    global.fetch.mockResolvedValue(mockResponse);

    await fetchSSE(
      "/test",
      {},
      {
        json: true,
        onMessageHandle: mockOnMessageHandle,
        onTokenUsage: mockOnTokenUsage,
      },
    );

    // Should have called onMessageHandle for metadata
    expect(mockOnMessageHandle).toHaveBeenCalledWith(
      { metadata: { citations: ["https://example.com"] } },
      mockResponse,
    );

    // Should have called onMessageHandle for token usage
    expect(mockOnMessageHandle).toHaveBeenCalledWith(
      {
        type: "token_usage",
        data: {
          event_type: "token_usage",
          prompt_tokens: 100,
          completion_tokens: 200,
          total_tokens: 300,
          model: "test",
        },
      },
      mockResponse,
    );

    // Should have called onMessageHandle for data
    expect(mockOnMessageHandle).toHaveBeenCalledWith(
      { data: "Hello world" },
      mockResponse,
    );
  });

  it("should handle mixed JSON and SSE events in text mode", async () => {
    const mockOnMessageHandle = vi.fn();
    const mockOnTokenUsage = vi.fn();

    // Mock a response that contains both text data and SSE events
    const mockResponse = {
      ok: true,
      body: {
        getReader: () => ({
          read: vi.fn().mockResolvedValueOnce({
            value: new TextEncoder().encode(
              '{"data": "Hello world"}\n\n' +
                "event: token_usage\n" +
                'data: {"event_type":"token_usage","prompt_tokens":100,"completion_tokens":200,"total_tokens":300,"model":"test"}\n\n',
            ),
            done: true,
          }),
        }),
      },
    };

    global.fetch.mockResolvedValue(mockResponse);

    await fetchSSE(
      "/test",
      {},
      {
        text: true,
        onMessageHandle: mockOnMessageHandle,
        onTokenUsage: mockOnTokenUsage,
      },
    );

    // Should have called onMessageHandle for text data
    expect(mockOnMessageHandle).toHaveBeenCalledWith(
      "Hello world",
      mockResponse,
    );

    // Should have called onTokenUsage for token usage
    expect(mockOnTokenUsage).toHaveBeenCalledWith({
      event_type: "token_usage",
      prompt_tokens: 100,
      completion_tokens: 200,
      total_tokens: 300,
      model: "test",
    });
  });

  it("should handle malformed JSON gracefully", async () => {
    const mockOnMessageHandle = vi.fn();
    const consoleSpy = vi.spyOn(console, "log").mockImplementation(() => {});

    // Mock a response with malformed JSON
    const mockResponse = {
      ok: true,
      body: {
        getReader: () => ({
          read: vi.fn().mockResolvedValueOnce({
            value: new TextEncoder().encode('{"invalid": json}\n\n'),
            done: true,
          }),
        }),
      },
    };

    global.fetch.mockResolvedValue(mockResponse);

    await fetchSSE(
      "/test",
      {},
      {
        json: true,
        onMessageHandle: mockOnMessageHandle,
      },
    );

    // Should log the parse error but not crash
    expect(consoleSpy).toHaveBeenCalledWith(
      "Failed to parse JSON chunk:",
      '{"invalid": json}',
      expect.any(SyntaxError),
    );

    consoleSpy.mockRestore();
  });

  it("should handle the exact error scenario from the user", async () => {
    const mockOnMessageHandle = vi.fn();
    const consoleSpy = vi.spyOn(console, "log").mockImplementation(() => {});

    // This is the exact format that causes the error
    const problematicChunk =
      '{"metadata": {"citations": ["https://blocksandfiles.com/2025/05/23/lenovo-boasts-near-record-revenues-despite-sequential-pc-slump/", "https://doc.irasia.com/listco/hk/lenovo/annual/2025/res.pdf", "https://investor.lenovo.com/en/financial/results/press_2425_q4.pdf", "https://news.lenovo.com/pressroom/press-releases/fy-2024-25/", "https://www.macrotrends.net/stocks/charts/LNVGY/lenovo-group/revenue"]}}\n\n' +
      "event: token_usage\n" +
      'data: {"event_type":"token_usage","prompt_tokens":861,"completion_tokens":1298,"total_tokens":2159,"model":"unknown"}\n\n';

    const mockResponse = {
      ok: true,
      body: {
        getReader: () => ({
          read: vi.fn().mockResolvedValueOnce({
            value: new TextEncoder().encode(problematicChunk),
            done: true,
          }),
        }),
      },
    };

    global.fetch.mockResolvedValue(mockResponse);

    await fetchSSE(
      "/test",
      {},
      {
        json: true,
        onMessageHandle: mockOnMessageHandle,
      },
    );

    // Should have called onMessageHandle for metadata
    expect(mockOnMessageHandle).toHaveBeenCalledWith(
      {
        metadata: {
          citations: [
            "https://blocksandfiles.com/2025/05/23/lenovo-boasts-near-record-revenues-despite-sequential-pc-slump/",
            "https://doc.irasia.com/listco/hk/lenovo/annual/2025/res.pdf",
            "https://investor.lenovo.com/en/financial/results/press_2425_q4.pdf",
            "https://news.lenovo.com/pressroom/press-releases/fy-2024-25/",
            "https://www.macrotrends.net/stocks/charts/LNVGY/lenovo-group/revenue",
          ],
        },
      },
      mockResponse,
    );

    // Should have called onMessageHandle for token usage
    expect(mockOnMessageHandle).toHaveBeenCalledWith(
      {
        type: "token_usage",
        data: {
          event_type: "token_usage",
          prompt_tokens: 861,
          completion_tokens: 1298,
          total_tokens: 2159,
          model: "unknown",
        },
      },
      mockResponse,
    );

    // Should not have logged any parse errors
    expect(consoleSpy).not.toHaveBeenCalledWith(
      "Failed to parse JSON chunk:",
      expect.any(String),
      expect.any(SyntaxError),
    );

    consoleSpy.mockRestore();
  });
});
