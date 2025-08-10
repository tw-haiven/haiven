// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { Tooltip } from "antd";
import { GiToken } from "react-icons/gi";
import { formatTokens } from "./utils/tokenUtils";

const LLMTokenUsage = ({ tokenUsage }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  // Determine if either value is missing/invalid
  const inputTokensValid =
    typeof tokenUsage?.input_tokens === "number" &&
    !isNaN(tokenUsage.input_tokens);
  const outputTokensValid =
    typeof tokenUsage?.output_tokens === "number" &&
    !isNaN(tokenUsage.output_tokens);

  // Log error if either value is missing/invalid
  useEffect(() => {
    if (!inputTokensValid || !outputTokensValid) {
      console.error(
        "Token usage calculation failed: input_tokens or output_tokens missing or invalid",
        tokenUsage,
      );
    }
  }, [inputTokensValid, outputTokensValid, tokenUsage]);

  return (
    <Tooltip
      open={showTooltip}
      title={
        <div>
          <p>
            <b>Aggregated Token Usage (this page):</b>
          </p>
          <p>Input Tokens: {formatTokens(tokenUsage?.input_tokens)}</p>
          <p>Output Tokens: {formatTokens(tokenUsage?.output_tokens)}</p>
        </div>
      }
    >
      <span
        className="token-usage-icon"
        data-testid="llm-token-usage"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <GiToken fontSize="large" />
      </span>
    </Tooltip>
  );
};

export default LLMTokenUsage;
