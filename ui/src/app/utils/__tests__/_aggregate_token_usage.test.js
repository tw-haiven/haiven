// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect } from "vitest";
import { aggregateTokenUsage } from "../_aggregate_token_usage";

describe("aggregateTokenUsage", () => {
  it("sums input and output tokens", () => {
    const prev = { input_tokens: 1000, output_tokens: 500 };
    const next = { input_tokens: 2000, output_tokens: 800 };
    expect(aggregateTokenUsage(prev, next)).toEqual({
      input_tokens: 3000,
      output_tokens: 1300,
    });
  });

  it("treats missing values as zero", () => {
    const prev = { input_tokens: 1000 };
    const next = { output_tokens: 800 };
    expect(aggregateTokenUsage(prev, next)).toEqual({
      input_tokens: 1000,
      output_tokens: 800,
    });
  });

  it("treats invalid values as zero", () => {
    const prev = { input_tokens: NaN, output_tokens: undefined };
    const next = { input_tokens: 2000, output_tokens: null };
    expect(aggregateTokenUsage(prev, next)).toEqual({
      input_tokens: 2000,
      output_tokens: 0,
    });
  });

  it("handles both objects missing fields", () => {
    expect(aggregateTokenUsage({}, {})).toEqual({
      input_tokens: 0,
      output_tokens: 0,
    });
  });
});
