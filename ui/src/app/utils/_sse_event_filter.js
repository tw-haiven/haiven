// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
// Splits out SSE events (e.g., 'event: token_usage\ndata: {...}') from a string.
// Returns { text: string, events: Array<{ type: string, data: any }> }
export function filterSSEEvents(input) {
  let textParts = [];
  let events = [];

  // Regex to match SSE event blocks: event: <type>\ndata: <json>\n\n or at end of string
  const sseEventRegex = /event: (\w+)\ndata: ([^\n]+)(?:\n\n|$)/g;
  let lastIndex = 0;
  let match;

  while ((match = sseEventRegex.exec(input)) !== null) {
    // Text before this event (preserve all whitespace)
    if (match.index > lastIndex) {
      textParts.push(input.slice(lastIndex, match.index));
    }
    // Parse the event
    const type = match[1];
    const dataStr = match[2];
    try {
      const data = JSON.parse(dataStr);
      events.push({ type, data });
    } catch {
      // Ignore malformed events
    }
    lastIndex = sseEventRegex.lastIndex;
  }
  // Remaining text after last event
  if (lastIndex < input.length) {
    textParts.push(input.slice(lastIndex));
  }
  // Join text parts, do NOT trim or collapse newlines
  const text = textParts.join("");
  return { text, events };
}
