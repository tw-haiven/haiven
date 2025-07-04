// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState } from "react";
import { Tooltip } from "antd";
import { GiToken } from "react-icons/gi";
import { useTokenUsage } from "../hooks/useTokenUsage";
import { formatTokens } from "./utils/tokenUtils";

const LLMTokenUsage = () => {
  const [showTooltip, setShowTooltip] = useState(false);
  const { tokenUsage, hasTokenUsage } = useTokenUsage();

  // Don't render if no token usage data
  if (!hasTokenUsage) {
    return null;
  }

  return (
    <Tooltip
      open={showTooltip}
      title={
        <div>
          <p>Input Tokens: {formatTokens(tokenUsage.input_tokens)}</p>
          <p>Output Tokens: {formatTokens(tokenUsage.output_tokens)}</p>
        </div>
      }
    >
      <span 
        className="token-usage-icon"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <GiToken fontSize="large" />
      </span>
    </Tooltip>
  );
};

export default LLMTokenUsage; 