// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { Tooltip } from "antd";
import { GiToken } from "react-icons/gi";
import { formatTokens } from "./utils/tokenUtils";
import { FEATURES } from "../app/feature_toggle";

const LLMTokenUsage = ({ tokenUsage, featureToggleConfig = {} }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const [hasTokenUsage, setHasTokenUsage] = useState(false);

  useEffect(() => {
    setHasTokenUsage(
      (tokenUsage?.input_tokens || 0) > 0 ||
        (tokenUsage?.output_tokens || 0) > 0,
    );
  }, [tokenUsage?.input_tokens, tokenUsage?.output_tokens]);

  // Don't render if no token usage data
  if (
    !hasTokenUsage ||
    !(featureToggleConfig[FEATURES.LLM_TOKEN_USAGE] === true)
  ) {
    console.log("!hasTokenUsage", !hasTokenUsage);
    console.log("featureToggleConfig", featureToggleConfig);
    console.log("FEATURES.LLM_TOKEN_USAGE", FEATURES.LLM_TOKEN_USAGE);
    console.log(
      "featureToggleConfig[FEATURES.LLM_TOKEN_USAGE] === true",
      featureToggleConfig[FEATURES.LLM_TOKEN_USAGE] === true,
    );
    return null;
  }

  return (
    <Tooltip
      open={showTooltip}
      title={
        <div>
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
