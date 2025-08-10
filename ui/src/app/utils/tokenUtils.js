// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

const MIN_TOKENS_FOR_K_FORMAT = 1500;

/**
 * Formats token count as human-readable string with 'k' suffix for large numbers
 * @param {number} num - Token count
 * @returns {string} Formatted token count (e.g., "1k", "5k")
 */
export function formatTokens(num) {
  if (typeof num !== "number" || isNaN(num) || num <= 0) return "N/A";
  if (num < MIN_TOKENS_FOR_K_FORMAT) return "1k";
  return `${Math.round(num / 1000)}k`;
}

export function formattedUsage(tokenUsage) {
  return {
    input_tokens: tokenUsage.prompt_tokens || 0,
    output_tokens: tokenUsage.completion_tokens || 0,
    total_tokens: tokenUsage.total_tokens || 0,
    model: tokenUsage.model || "",
  };
}
