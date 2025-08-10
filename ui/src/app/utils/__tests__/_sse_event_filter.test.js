// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect } from "vitest";
import { filterSSEEvents } from "../_sse_event_filter";

describe("filterSSEEvents", () => {
  it("should return clean text and parsed events for a single SSE event", () => {
    const input =
      'Hello world!\nevent: token_usage\ndata: {"prompt_tokens": 10}\n\nGoodbye!';
    const { text, events } = filterSSEEvents(input);
    expect(text).toBe("Hello world!\nGoodbye!");
    expect(events).toEqual([
      { type: "token_usage", data: { prompt_tokens: 10 } },
    ]);
  });

  it("should handle multiple SSE events and interleaved text", () => {
    const input =
      'A\nevent: token_usage\ndata: {"prompt_tokens": 1}\n\nB\nevent: token_usage\ndata: {"prompt_tokens": 2}\n\nC';
    const { text, events } = filterSSEEvents(input);
    expect(text).toBe("A\nB\nC");
    expect(events).toEqual([
      { type: "token_usage", data: { prompt_tokens: 1 } },
      { type: "token_usage", data: { prompt_tokens: 2 } },
    ]);
  });

  it("should handle partial/incomplete SSE event chunks gracefully", () => {
    const input = 'Text before\nevent: token_usage\ndata: {"prompt_tokens": 3}'; // no trailing \n\n
    const { text, events } = filterSSEEvents(input);
    expect(text).toBe("Text before\n");
    expect(events).toEqual([
      { type: "token_usage", data: { prompt_tokens: 3 } },
    ]);
  });

  it("should ignore malformed SSE events", () => {
    const input = "event: token_usage\ndata: notjson\n\nText after";
    const { text, events } = filterSSEEvents(input);
    expect(text).toBe("Text after");
    expect(events).toEqual([]);
  });

  it("should return all text if there are no SSE events", () => {
    const input = "Just plain text.";
    const { text, events } = filterSSEEvents(input);
    expect(text).toBe("Just plain text.");
    expect(events).toEqual([]);
  });
});
